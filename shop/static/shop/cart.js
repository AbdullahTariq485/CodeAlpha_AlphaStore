function getCSRFToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 10) === 'csrftoken=') {
                cookieValue = decodeURIComponent(cookie.substring(10));
                break;
            }
        }
    }
    return cookieValue;
}

window.showToast = function(message, type = 'success') {
    const container = document.getElementById('toast-matrix-container');
    if (!container) return;

    const existingToast = [...container.children].find(toast => toast.dataset.message === message);
    if (existingToast) return;
    while (container.children.length >= 3) container.firstElementChild.remove();

    const toast = document.createElement('div');
    toast.className = 'store-toast';
    toast.dataset.message = message;
    toast.style.setProperty('--toast-accent', type === 'error' ? '#e11d48' : '#4f46e5');
    toast.setAttribute('role', type === 'error' ? 'alert' : 'status');

    const icon = document.createElement('span');
    icon.className = 'store-toast-icon';
    icon.textContent = type === 'error' ? '!' : '✓';
    const copy = document.createElement('span');
    copy.textContent = message;
    const close = document.createElement('button');
    close.className = 'store-toast-close';
    close.type = 'button';
    close.setAttribute('aria-label', 'Dismiss notification');
    close.textContent = '×';
    toast.append(icon, copy, close);

    container.appendChild(toast);
    close.addEventListener('click', () => dismissToast(toast));

    setTimeout(() => {
        toast.classList.add('is-visible');
    }, 10);

    setTimeout(() => dismissToast(toast), 4200);
};

function dismissToast(toast) {
    if (!toast || toast.classList.contains('is-leaving')) return;
    toast.classList.add('is-leaving');
    setTimeout(() => toast.remove(), 260);
}

window.modifyCart = function(action, productId) {
    const url = `/cart/${action}/${productId}/`;
    
    fetch(url, {
        method: 'GET',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => {
        document.querySelectorAll('.grand-total-val').forEach(el => {
            el.innerText = data.total_price;
        });

        if (action === 'remove' || data.removed === true) {
            const row = document.getElementById(`row-${productId}`);
            if (row) {
                row.classList.add('is-removing');
                setTimeout(() => row.remove(), 300);
            }
            
            window.showToast("Item completely removed from basket", "error");
            
            if (data.items_count === 0) {
                const itemsBody = document.getElementById('cart-items-body');
                if (itemsBody) {
                    itemsBody.innerHTML = `
                        <tr id="empty-row-msg">
                            <td colspan="3" style="text-align: center; color: #64748b; padding: 3rem 0;">Your basket is completely empty. <a href="/" style="color: #111111; font-weight: 600; text-decoration: underline;">Go shop items</a></td>
                        </tr>
                    `;
                }
                const checkoutBtn = document.getElementById('checkout-btn-wrapper');
                if (checkoutBtn) checkoutBtn.innerHTML = '';
            }
        } else {
            const itemData = data.items[productId];
            if (itemData) {
                const qtyEl = document.getElementById(`qty-${productId}`);
                const subEl = document.getElementById(`subtotal-${productId}`);
                if (qtyEl) {
                    qtyEl.innerText = itemData.quantity;
                    qtyEl.classList.remove('value-updated');
                    void qtyEl.offsetWidth;
                    qtyEl.classList.add('value-updated');
                }
                if (subEl) {
                    subEl.innerText = itemData.subtotal;
                    subEl.classList.remove('value-updated');
                    void subEl.offsetWidth;
                    subEl.classList.add('value-updated');
                }
                
                window.showToast("Basket quantity updated smoothly!");
            }
        }
    })
    .catch(error => {
        console.error('Error updating cart values:', error);
        window.location.reload();
    });
};

window.asyncToggleStock = function(productId) {
    const url = `/alpha-staff/stock/${productId}/`;
    
    fetch(url, {
        method: 'GET',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(res => {
        if (!res.ok) throw new Error('Network error');
        return res.json();
    })
    .then(data => {
        if (data.success) {
            const container = document.getElementById(`stock-badge-${productId}`);
            if (!container) return;
            
            if (data.in_stock) {
                container.innerHTML = `<span style="color: #059669; font-weight: 700; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.02em;">● In Stock</span>`;
                window.showToast("Stock allocation activated smoothly.");
            } else {
                container.innerHTML = `<span style="color: #e11d48; font-weight: 700; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.02em;">○ Out of Stock</span>`;
                window.showToast("Stock item marked Out of Stock.", "error");
            }
        }
    })
    .catch(err => console.error("Stock level operational update failure:", err));
};

window.asyncEditProduct = function(productId) {
    const url = `/alpha-staff/edit-product/${productId}/`;
    const name = document.getElementById(`edit-name-in-${productId}`).value;
    const price = document.getElementById(`edit-price-in-${productId}`).value;
    const desc = document.getElementById(`edit-desc-in-${productId}`).value;
    const imageInput = document.getElementById(`edit-image-in-${productId}`);
    
    let formData = new FormData();
    formData.append('edit_name', name);
    formData.append('edit_price', price);
    formData.append('edit_desc', desc);
    
    if (imageInput && imageInput.files && imageInput.files[0]) {
        formData.append('edit_image', imageInput.files[0]);
    }

    fetch(url, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCSRFToken()
        },
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            window.location.reload();
        } else {
            window.showToast(data.error || "Failed to update item specifications.", "error");
        }
    })
    .catch(err => console.error("Product property edit operation failed:", err));
};


window.asyncUpdateOrder = function(orderId) {
    const url = `/alpha-staff/order/${orderId}/`;
    const selector = document.getElementById(`select-status-${orderId}`);
    if (!selector) return;
    
    const selectedStatus = selector.value;
    const formData = new FormData();
    formData.append('status_update', selectedStatus);

    fetch(url, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCSRFToken()
        },
        body: formData
    })
    .then(res => {
        if (!res.ok) throw new Error('Fulfillment log sync broken');
        return res.json();
    })
    .then(data => {
        if (data.success) {
            if (data.new_status === 'Delivered') {
                const row = document.getElementById('order-row-' + orderId);
                if (row) {
                    row.style.opacity = '0';
                    row.style.transform = 'scale(0.95)';
                    setTimeout(() => {
                        row.remove();
                        const counter = document.getElementById('active-queue-count');
                        if (counter) counter.innerText = Math.max(0, parseInt(counter.innerText) - 1);
                        
                        const body = document.getElementById('admin-orders-tbody');
                        if (body && body.children.length === 0) {
                            body.innerHTML = `<tr id="no-orders-msg"><td colspan="5" style="text-align: center; color: var(--bc-text-muted); padding: 3rem 0;">No active consumer orders logged in database pipelines yet.</td></tr>`;
                        }
                    }, 300);
                }
                window.showToast(`Order #ALPHA-00${orderId} finalized & archived to history logs.`);
            } else {
                const badge = document.getElementById('status-badge-' + orderId);
                if (badge) badge.innerText = data.new_status;
                window.showToast(`Tracking status updated to: ${data.new_status}`);
            }
        }
    })
    .catch(err => console.error("Fulfillment dispatch queue transmission failure:", err));
};

window.toggleEditRow = function(productId) {
    const row = document.getElementById('edit-form-row-' + productId);
    if (row) row.style.display = row.style.display === 'none' ? 'table-row' : 'none';
};

document.addEventListener("DOMContentLoaded", function () {
    const filterBar = document.getElementById('catalog-filters');
    const cards = [...document.querySelectorAll('[data-product-card]')];
    const emptyState = document.getElementById('catalog-empty');
    const count = document.getElementById('catalog-count');

    if (filterBar && cards.length) {
        const applyFilter = (filter) => {
            let visibleCount = 0;
            cards.forEach(card => {
                const visible = filter === 'all' || card.dataset.category === filter;
                card.classList.toggle('is-hidden', !visible);
                if (visible) {
                    card.style.setProperty('--card-index', visibleCount);
                    visibleCount += 1;
                }
            });
            filterBar.querySelectorAll('[data-filter]').forEach(button => {
                const active = button.dataset.filter === filter;
                button.classList.toggle('active', active);
                button.setAttribute('aria-pressed', active ? 'true' : 'false');
            });
            if (emptyState) emptyState.hidden = visibleCount !== 0;
            if (count) count.textContent = `${visibleCount} ${visibleCount === 1 ? 'item' : 'items'} in the catalog`;
            if (window.history.replaceState) window.history.replaceState(null, '', filter === 'all' ? window.location.pathname : `#${filter}`);
        };

        document.querySelectorAll('[data-filter]').forEach(control => {
            control.addEventListener('click', () => {
                applyFilter(control.dataset.filter);
                document.getElementById('catalog')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
        });

        const initialFilter = window.location.hash.slice(1);
        applyFilter(filterBar.querySelector(`[data-filter="${initialFilter}"]`) ? initialFilter : 'all');
    }

    const container = document.getElementById('toast-matrix-container');
    if (!container) return;

    const rawData = container.getAttribute('data-messages');
    if (!rawData || rawData.trim() === "") return;

    const messageRows = rawData.split(';').filter(row => row.trim() !== "");
    
    messageRows.forEach(row => {
        const parts = row.split('|');
        if (parts.length === 2) {
            window.showToast(parts[0], parts[1]);
        }
    });
});

