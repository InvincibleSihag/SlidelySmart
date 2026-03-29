import { useEffect, useRef } from "react";
import { useParams } from "react-router-dom";
import { fetchJobState } from "../lib/api";
import { useJobStore } from "../stores/job-store";

/**
 * On mount, checks the URL for a job ID and
 * hydrates the store from the server if one is found.
 *
 * This handles page refresh recovery for all states:
 * - PROCESSING: shows persisted messages + in-progress slides, re-subscribes to Pusher
 * - WAITING_FOR_INPUT: reconstructs HITL form from persisted hitl_request
 * - COMPLETED: shows all messages + final slides
 * - FAILED: shows messages + error
 */
export function useJobRecovery() {
  const { jobId } = useParams<{ jobId: string }>();
  const hydrateFromServer = useJobStore((s) => s.hydrateFromServer);
  const phase = useJobStore((s) => s.phase);
  const recoveredRef = useRef(false);

  useEffect(() => {
    if (recoveredRef.current || phase !== "idle") return;
    recoveredRef.current = true;

    if (!jobId) return;

    fetchJobState(jobId)
      .then((serverState) => {
        hydrateFromServer(serverState);
      })
      .catch(() => {
        // Leave store idle — URL may point to an invalid/expired job
      });
  }, [jobId, hydrateFromServer, phase]);
}
