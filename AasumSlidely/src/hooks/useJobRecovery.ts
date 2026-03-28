import { useEffect, useRef } from "react";
import { fetchJobState } from "../lib/api";
import { useJobStore } from "../stores/job-store";

const DECK_ID_KEY = "slidely_deck_id";

/**
 * On mount, checks sessionStorage for an active deck ID and
 * hydrates the store from the server if one is found.
 *
 * This handles page refresh recovery for all states:
 * - PROCESSING: shows persisted messages + in-progress slides, re-subscribes to Pusher
 * - WAITING_FOR_INPUT: reconstructs HITL form from persisted hitl_request
 * - COMPLETED: shows all messages + final slides
 * - FAILED: shows messages + error
 */
export function useJobRecovery() {
  const hydrateFromServer = useJobStore((s) => s.hydrateFromServer);
  const phase = useJobStore((s) => s.phase);
  const recoveredRef = useRef(false);

  useEffect(() => {
    if (recoveredRef.current || phase !== "idle") return;
    recoveredRef.current = true;

    const deckId = sessionStorage.getItem(DECK_ID_KEY);
    if (!deckId) return;

    fetchJobState(deckId)
      .then((serverState) => {
        hydrateFromServer(serverState);
      })
      .catch(() => {
        sessionStorage.removeItem(DECK_ID_KEY);
      });
  }, [hydrateFromServer, phase]);
}

/** Persist deck ID to sessionStorage for refresh recovery. */
export function saveDeckId(deckId: string) {
  sessionStorage.setItem(DECK_ID_KEY, deckId);
}

/** Clear persisted deck ID. */
export function clearDeckId() {
  sessionStorage.removeItem(DECK_ID_KEY);
}
