/**
 * Shared formatting & status utility functions
 */

export function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString()
}

export function formatDateTime(d) {
  if (!d) return '—'
  return new Date(d).toLocaleString()
}

export function driveStatusLabel(drive) {
  if (!drive.is_active) return 'Closed'
  if (drive.deadline_passed) return 'Deadline Passed'
  if (drive.already_applied) return 'Applied'
  return 'Open'
}

export function driveStatusClass(drive) {
  if (!drive.is_active) return 'status-closed'
  if (drive.deadline_passed) return 'status-deadline'
  if (drive.already_applied) return 'status-applied'
  return 'status-open'
}

export function getStatusActions(status) {
  const actions = {
    Applied: [
      { label: 'Shortlist', status: 'Shortlisted', type: 'approve' },
      { label: 'Reject', status: 'Rejected', type: 'reject' }
    ],
    Shortlisted: [
      { label: 'Move to Interview', status: 'Interview', type: 'approve' },
      { label: 'Reject', status: 'Rejected', type: 'reject' }
    ],
    Interview: [
      { label: 'Send Offer', status: 'Offer', type: 'approve' },
      { label: 'Reject', status: 'Rejected', type: 'reject' }
    ],
    Offer: [{ label: 'Mark Placed', status: 'Placed', type: 'approve' }]
  }
  return actions[status] || []
}
