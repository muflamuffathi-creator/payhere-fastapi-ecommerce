// LankaCart Storefront & Cart Management
const Cart = {
  KEY: 'lankacart_items',

  getItems() {
    try {
      return JSON.parse(localStorage.getItem(this.KEY) || '[]');
    } catch {
      return [];
    }
  },

  saveItems(items) {
    localStorage.setItem(this.KEY, JSON.stringify(items));
    this.updateUI();
  },

  addItem(product) {
    let items = this.getItems();
    const existing = items.find(i => i.id === product.id);
    if (existing) {
      existing.quantity += 1;
    } else {
      items.push({
        id: product.id,
        name: product.name,
        price: product.price,
        image_url: product.image_url,
        quantity: 1
      });
    }
    this.saveItems(items);
    showToast(`Added "${product.name}" to cart!`, 'success');
  },

  removeItem(productId) {
    let items = this.getItems().filter(i => i.id !== productId);
    this.saveItems(items);
  },

  updateQuantity(productId, delta) {
    let items = this.getItems();
    const item = items.find(i => i.id === productId);
    if (!item) return;

    item.quantity += delta;
    if (item.quantity <= 0) {
      items = items.filter(i => i.id !== productId);
    }
    this.saveItems(items);
  },

  clear() {
    localStorage.removeItem(this.KEY);
    this.updateUI();
  },

  getTotal() {
    return this.getItems().reduce((sum, item) => sum + (item.price * item.quantity), 0);
  },

  getCount() {
    return this.getItems().reduce((sum, item) => sum + item.quantity, 0);
  },

  updateUI() {
    const count = this.getCount();
    const total = this.getTotal();
    const countBadges = document.querySelectorAll('.cart-count');
    countBadges.forEach(el => el.textContent = count);

    const drawerList = document.getElementById('drawerCartItems');
    const drawerSubtotal = document.getElementById('drawerSubtotal');

    if (drawerSubtotal) {
      drawerSubtotal.textContent = `LKR ${total.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
    }

    if (drawerList) {
      const items = this.getItems();
      if (items.length === 0) {
        drawerList.innerHTML = `
          <div style="text-align: center; padding: 3rem 1rem; color: var(--text-muted);">
            <svg width="48" height="48" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="margin-bottom: 1rem; opacity: 0.5;">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/>
            </svg>
            <p>Your shopping cart is empty.</p>
          </div>
        `;
      } else {
        drawerList.innerHTML = items.map(item => `
          <div class="cart-item">
            <img src="${item.image_url || 'https://via.placeholder.com/60'}" class="cart-item-img" alt="${item.name}">
            <div class="cart-item-info">
              <div class="cart-item-title">${item.name}</div>
              <div class="cart-item-price">LKR ${(item.price * item.quantity).toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
              <div class="qty-controls">
                <button class="qty-btn" onclick="Cart.updateQuantity(${item.id}, -1)">-</button>
                <span style="font-size: 0.85rem; font-weight: 700; padding: 0 4px;">${item.quantity}</span>
                <button class="qty-btn" onclick="Cart.updateQuantity(${item.id}, 1)">+</button>
                <button onclick="Cart.removeItem(${item.id})" style="background:none; border:none; color:var(--text-muted); cursor:pointer; margin-left:auto; font-size:0.75rem;">Remove</button>
              </div>
            </div>
          </div>
        `).join('');
      }
    }
  }
};

// Toast Notifications
function showToast(message, type = 'info') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Drawer Toggle
function toggleCart(open = null) {
  const backdrop = document.getElementById('cartBackdrop');
  if (!backdrop) return;
  if (open === null) {
    backdrop.classList.toggle('open');
  } else if (open) {
    backdrop.classList.add('open');
  } else {
    backdrop.classList.remove('open');
  }
}

// Product Filtering
document.addEventListener('DOMContentLoaded', () => {
  Cart.updateUI();

  // Search input filter
  const searchInput = document.getElementById('searchInput');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase().trim();
      const cards = document.querySelectorAll('.product-card');
      cards.forEach(card => {
        const title = card.getAttribute('data-name')?.toLowerCase() || '';
        const category = card.getAttribute('data-category')?.toLowerCase() || '';
        if (title.includes(query) || category.includes(query)) {
          card.style.display = 'flex';
        } else {
          card.style.display = 'none';
        }
      });
    });
  }

  // Category pills filter
  const pills = document.querySelectorAll('.cat-pill');
  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      pills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');

      const selectedCat = pill.getAttribute('data-cat');
      const cards = document.querySelectorAll('.product-card');

      cards.forEach(card => {
        const cardCat = card.getAttribute('data-category');
        if (!selectedCat || selectedCat === 'all' || cardCat === selectedCat) {
          card.style.display = 'flex';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });
});
