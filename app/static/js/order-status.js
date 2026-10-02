// Real-time order tracking and sandbox status triggers
document.addEventListener('DOMContentLoaded', () => {
  const orderNumber = document.getElementById('trackingOrderNumber')?.value;
  if (!orderNumber) return;

  let pollInterval = null;

  async function checkStatus() {
    try {
      const res = await fetch(`/api/v1/orders/${orderNumber}`);
      if (!res.ok) return;
      const order = await res.json();

      updateStatusDisplay(order);

      // If finished, stop polling
      if (['PAID', 'FAILED', 'CANCELLED'].includes(order.status)) {
        if (pollInterval) clearInterval(pollInterval);
      }
    } catch (e) {
      console.error('Polling error', e);
    }
  }

  function updateStatusDisplay(order) {
    const badge = document.getElementById('orderStatusBadge');
    if (badge) {
      badge.textContent = order.status;
      badge.className = `status-pill status-${order.status}`;
    }

    if (order.status === 'PAID') {
      const pendingBox = document.getElementById('pendingNoticeBox');
      const paidBox = document.getElementById('paidSuccessBox');
      if (pendingBox) pendingBox.style.display = 'none';
      if (paidBox) paidBox.style.display = 'block';
    }
  }

  // Poll every 3 seconds if pending
  const currentStatus = document.getElementById('currentStatusValue')?.value;
  if (currentStatus === 'PENDING' || currentStatus === 'PROCESSING') {
    pollInterval = setInterval(checkStatus, 3000);
  }
});

// Quick simulator triggers from order tracking page
async function triggerOrderSimulation(statusCode, statusDesc) {
  const orderNumber = document.getElementById('trackingOrderNumber')?.value;
  if (!orderNumber) return;

  try {
    showToast(`Sending PayHere signed callback (Status ${statusCode})...`, 'info');
    const res = await fetch('/api/v1/payments/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        order_number: orderNumber,
        status_code: statusCode,
        method: 'VISA',
        status_message: statusDesc
      })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Simulation failed');
    }

    const data = await res.json();
    showToast(`Success: ${data.message}`, 'success');
    setTimeout(() => window.location.reload(), 1200);
  } catch (e) {
    showToast(`Error: ${e.message}`, 'error');
  }
}
