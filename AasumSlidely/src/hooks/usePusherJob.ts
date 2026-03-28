import { useEffect, useRef, useCallback } from "react";
import { pusher, subscribeToJob, unsubscribeFromJob } from "../lib/pusher";
import { fetchJobState } from "../lib/api";
import { useJobStore } from "../stores/job-store";
import type {
  AgentStatusEvent,
  HitlRequestEvent,
  SlidesUpdatedEvent,
} from "../types";

const THINKING_FLUSH_INTERVAL = 50; // ms

/**
 * Subscribes to Pusher events for the active job and dispatches
 * them to the Zustand store.
 *
 * Includes a ref-based thinking text buffer that flushes at 50ms
 * intervals to prevent re-render storms during LLM streaming.
 *
 * Monitors Pusher connection state for reconnection — on reconnect,
 * fetches the latest server state to catch up on missed events.
 */
export function usePusherJob(deckId: string | null) {
  const store = useJobStore;
  const bufferRef = useRef<string[]>([]);
  const connectionRef = useRef<"connected" | "disconnected">("connected");

  // Flush thinking text buffer into store on interval
  useEffect(() => {
    const intervalId = setInterval(() => {
      if (bufferRef.current.length > 0) {
        const flushed = bufferRef.current[bufferRef.current.length - 1];
        bufferRef.current = [];
        store.getState().handleAgentStatus({ stage: "processing", message: flushed });
      }
    }, THINKING_FLUSH_INTERVAL);
    return () => clearInterval(intervalId);
  }, []);

  // Catch up after reconnection
  const catchUp = useCallback(async () => {
    const currentDeckId = store.getState().deckId;
    if (!currentDeckId) return;
    try {
      const serverState = await fetchJobState(currentDeckId);
      store.getState().hydrateFromServer(serverState);
    } catch {
      // Silently fail — next Pusher event or user action will sync
    }
  }, []);

  // Monitor Pusher connection state
  useEffect(() => {
    const handleStateChange = (states: { current: string; previous: string }) => {
      if (
        states.current === "connected" &&
        connectionRef.current === "disconnected"
      ) {
        connectionRef.current = "connected";
        catchUp();
      } else if (states.current !== "connected") {
        connectionRef.current = "disconnected";
      }
    };

    pusher.connection.bind("state_change", handleStateChange);
    return () => {
      pusher.connection.unbind("state_change", handleStateChange);
    };
  }, [catchUp]);

  // Subscribe to job channel and bind events
  useEffect(() => {
    if (!deckId) return;

    const channel = subscribeToJob(deckId);

    channel.bind("agent_status", (data: AgentStatusEvent) => {
      bufferRef.current.push(data.message);
    });

    channel.bind("slides_updated", (data: SlidesUpdatedEvent) => {
      store.getState().handleSlidesUpdated(data);
      // Fetch updated HTML from server
      fetchJobState(deckId).then((serverState) => {
        store.getState().setSlidesHtml(serverState.slides_html);
      }).catch(() => {});
    });

    channel.bind(
      "job_waiting_for_input",
      (data: HitlRequestEvent) => {
        bufferRef.current = [];
        store.getState().handleHitlRequest(data);
      },
    );

    channel.bind("job_completed", () => {
      bufferRef.current = [];
      store.getState().handleJobCompleted();
      // Fetch final state with AI message and slides
      fetchJobState(deckId).then((serverState) => {
        store.getState().hydrateFromServer(serverState);
      }).catch(() => {});
    });

    channel.bind("job_failed", (data: { error: string }) => {
      bufferRef.current = [];
      store.getState().handleJobFailed(data.error);
    });

    return () => {
      unsubscribeFromJob(deckId);
    };
  }, [deckId]);
}
