// Admin dashboard & PayHere Webhook Simulator
document.addEventListener('DOMContentLoaded', () => {
  loadMetrics();
  loadOrders();

  // Tab switching
  const tabs = document.querySelectorAll('.tab-btn');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

      tab.classList.add('active');
      const targetId = tab.getAttribute('data-target');
      const targetPane = document.getElementById(targetId);
      if (targetPane) targetPane.classList.add('active');
    });
  });

  // Simulator Form
  const simForm = document.getElementById('simulatorForm');
  if (simForm) {
    simForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const consoleEl = document.getElementById('simulatorConsole');
      const orderNumber = document.getElementById('simOrderNumber').value;
      const statusCode = parseInt(document.getElementById('simStatusCode').value);
      const method = document.getElementById('simMethod').value;
      const customMsg = document.getElementById('simStatusMessage').value;

      if (!orderNumber) {
        showToast('Please select or enter an order number', 'error');
        return;
      }

      consoleEl.textContent = `[INFO] Preparing simulated PayHere callback for ${orderNumber}...\n`;
      consoleEl.textContent += `[INFO] Calculating MD5 signature: MD5(merchant_id + order_id + amount + currency + status_code + MD5(secret))...\n`;

      try {
        const res = await fetch('/api/v1/payments/simulate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            order_number: orderNumber,
            status_code: statusCode,
            method: method,
            status_message: customMsg || 'PayHere simulated webhook'
          })
        });

        const data = await res.json();
        consoleEl.textContent += `[HTTP RESPONSE] Status ${res.status}:\n`;
        consoleEl.textContent += JSON.stringify(data, null, 2);

        if (res.ok) {
          showToast(`PayHere Webhook executed: ${data.message}`, 'success');
          loadMetrics();
          loadOrders();
        } else {
          showToast(`Simulation error: ${data.detail}`, 'error');
        }
      } catch (err) {
        consoleEl.textContent += `[ERROR] ${err.message}\n`;
        showToast('Simulation failed to connect', 'error');
      }
    });
  }
});

async function loadMetrics() {
  try {
    const res = await fetch('/api/v1/admin/metrics');
    if (!res.ok) return;
    const m = await res.json();

    document.getElementById('metricRevenue').textContent = `LKR ${m.total_revenue.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
    document.getElementById('metricOrders').textContent = m.total_orders;
    document.getElementById('metricPaid').textContent = m.paid_orders;
    document.getElementById('metricConversion').textContent = `${m.conversion_rate}%`;
  } catch (e) {
    console.error('Failed to load metrics', e);
  }
}

async function loadOrders() {
  try {
    const res = await fetch('/api/v1/orders?limit=50');
    if (!res.ok) return;
    const orders = await res.json();

    const tbody = document.getElementById('ordersTableBody');
    const simSelect = document.getElementById('simOrderNumber');

    if (simSelect) {
      const currentVal = simSelect.value;
      simSelect.innerHTML = '<option value="">-- Choose an Order --</option>' +
        orders.map(o => `
          <option value="${o.order_number}" ${o.order_number === currentVal ? 'selected' : ''}>
            ${o.order_number} (${o.first_name} ${o.last_name} - LKR ${o.total_amount.toFixed(2)} - [${o.status}])
          </option>
        `).join('');
    }

    if (tbody) {
      if (orders.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 2rem; color:var(--text-muted);">No orders created yet.</td></tr>`;
        return;
      }

      tbody.innerHTML = orders.map(o => `
        <tr>
          <td>
            <a href="/orders/track/${o.order_number}" style="color:var(--accent-blue); font-weight:700;">
              ${o.order_number}
            </a>
          </td>
          <td>${o.first_name} ${o.last_name}<br><small style="color:var(--text-muted);">${o.email}</small></td>
          <td style="font-weight:700;">LKR ${o.total_amount.toFixed(2)}</td>
          <td>
            <span class="status-pill status-${o.status}">${o.status}</span>
          </td>
          <td>${o.payments && o.payments.length > 0 ? o.payments[0].method || 'PayHere' : 'None'}</td>
          <td style="font-size:0.8rem; color:var(--text-muted);">${new Date(o.created_at).toLocaleString()}</td>
          <td>
            <div style="display:flex; gap:6px;">
              <a href="/orders/track/${o.order_number}" class="btn btn-secondary" style="padding:4px 8px; font-size:0.75rem;">Inspect</a>
              <button onclick="quickSimulate('${o.order_number}', 2)" class="btn btn-simulate" style="padding:4px 8px; font-size:0.75rem;">Simulate Pay</button>
            </div>
          </td>
        </tr>
      `).join('');
    }
  } catch (e) {
    console.error('Failed to load orders', e);
  }
}

async function quickSimulate(orderNumber, statusCode) {
  try {
    showToast(`Simulating status ${statusCode} for ${orderNumber}...`, 'info');
    const res = await fetch('/api/v1/payments/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        order_number: orderNumber,
        status_code: statusCode,
        method: 'VISA',
        status_message: 'Quick simulated webhook trigger'
      })
    });

    const data = await res.json();
    if (res.ok) {
      showToast(`Order updated to ${data.order_status}`, 'success');
      loadMetrics();
      loadOrders();
    } else {
      showToast(data.detail || 'Simulation error', 'error');
    }
  } catch (e) {
    showToast(e.message, 'error');
  }
}
