/**
 * Placeholder hook: combines orval-generated useGetJob query with
 * Pusher real-time notifications for efficient job status polling.
 *
 * Strategy:
 * 1. On mount, subscribe to Pusher channel `job-{jobId}`
 * 2. On Pusher "status_changed" event, invalidate the TanStack Query
 * 3. As fallback, poll with refetchInterval when status is PROCESSING
 * 4. Stop polling when status is COMPLETED or FAILED
 */
export function useJobPolling(_jobId: string) {
  // TODO: implement after orval generates the API hooks
}
