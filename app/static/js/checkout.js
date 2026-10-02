// Checkout logic and PayHere payment integration
document.addEventListener('DOMContentLoaded', () => {
  const items = Cart.getItems();
  const checkoutItemsContainer = document.getElementById('checkoutItemsList');
  const subtotalEl = document.getElementById('checkoutSubtotal');
  const totalEl = document.getElementById('checkoutTotal');
  const emptyCartWarning = document.getElementById('emptyCartNotice');
  const checkoutForm = document.getElementById('checkoutForm');

  if (items.length === 0) {
    if (emptyCartWarning) emptyCartWarning.style.display = 'block';
    if (checkoutForm) {
      checkoutForm.querySelectorAll('button, input').forEach(el => el.disabled = true);
    }
    return;
  }

  const subtotal = Cart.getTotal();
  if (subtotalEl) subtotalEl.textContent = `LKR ${subtotal.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
  if (totalEl) totalEl.textContent = `LKR ${subtotal.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;

  if (checkoutItemsContainer) {
    checkoutItemsContainer.innerHTML = items.map(item => `
      <div style="display:flex; justify-content:space-between; align-items:center; padding: 10px 0; border-bottom: 1px solid var(--border-color);">
        <div style="display:flex; gap:12px; align-items:center;">
          <img src="${item.image_url || 'https://via.placeholder.com/50'}" style="width:44px; height:44px; border-radius:6px; object-fit:cover;">
          <div>
            <div style="font-weight:600; font-size:0.9rem;">${item.name}</div>
            <div style="font-size:0.8rem; color:var(--text-muted);">Qty: ${item.quantity} × LKR ${item.price.toFixed(2)}</div>
          </div>
        </div>
        <div style="font-weight:700; color:var(--accent-gold);">
          LKR ${(item.price * item.quantity).toFixed(2)}
        </div>
      </div>
    `).join('');
  }

  // Handle Form Submission
  if (checkoutForm) {
    checkoutForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const submitBtn = document.getElementById('btnSubmitPayHere');
      const simBtn = document.getElementById('btnSubmitSimulator');
      const actionType = e.submitter ? e.submitter.value : 'payhere';

      if (submitBtn) submitBtn.disabled = true;
      if (simBtn) simBtn.disabled = true;

      const orderPayload = {
        first_name: document.getElementById('first_name').value.trim(),
        last_name: document.getElementById('last_name').value.trim(),
        email: document.getElementById('email').value.trim(),
        phone: document.getElementById('phone').value.trim(),
        address: document.getElementById('address').value.trim(),
        city: document.getElementById('city').value.trim(),
        country: document.getElementById('country').value.trim() || 'Sri Lanka',
        postal_code: document.getElementById('postal_code').value.trim() || null,
        notes: document.getElementById('notes')?.value.trim() || null,
        items: items.map(i => ({ product_id: i.id, quantity: i.quantity }))
      };

      try {
        showToast('Creating your order in database...', 'info');

        // Step 1: Create Order
        const orderRes = await fetch('/api/v1/orders', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(orderPayload)
        });

        if (!orderRes.ok) {
          const err = await orderRes.json();
          throw new Error(err.detail || 'Failed to place order');
        }

        const order = await orderRes.json();
        showToast(`Order ${order.order_number} created!`, 'success');

        // Step 2: Fetch PayHere Checkout Hash & Params
        const paramsRes = await fetch(`/api/v1/orders/${order.order_number}/checkout-params`);
        if (!paramsRes.ok) throw new Error('Failed to retrieve PayHere checkout hash');
        const payhereParams = await paramsRes.json();

        // Clear local cart now that order is saved
        Cart.clear();

        if (actionType === 'simulate') {
          // Direct Simulation route (fast local test without gateway redirect)
          showToast('Simulating PayHere Sandbox approval...', 'info');
          const simRes = await fetch('/api/v1/payments/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              order_number: order.order_number,
              status_code: 2,
              method: 'VISA',
              status_message: 'Simulated approval in sandbox'
            })
          });

          if (!simRes.ok) throw new Error('Simulation failed');
          window.location.href = `/checkout/success?order_number=${order.order_number}`;
        } else {
          // Real PayHere Sandbox Gateway Form submission
          showToast('Redirecting to PayHere Sandbox Gateway...', 'info');
          submitPayHereForm(payhereParams);
        }
      } catch (err) {
        showToast(`Error: ${err.message}`, 'error');
        if (submitBtn) submitBtn.disabled = false;
        if (simBtn) simBtn.disabled = false;
      }
    });
  }
});

function submitPayHereForm(params) {
  // Create hidden form and submit directly to PayHere Sandbox
  const form = document.createElement('form');
  form.method = 'POST';
  form.action = params.checkout_url;

  // Add all PayHere fields
  for (const [key, value] of Object.entries(params)) {
    if (key === 'checkout_url') continue;
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = key;
    input.value = value;
    form.appendChild(input);
  }

  document.body.appendChild(form);
  form.submit();
}
