/**
 * 🚀 Alpha Store Core Client-Side Interactivity Engine
 */

// Helper function to read secure CSRF token cookies
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

// Global function to spawn premium toast notifications dynamically
window.showToast = function(message, type = 'success') {
    const container = document.getElementById('toast-matrix-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.style.pointerEvents = 'auto';
    toast.style.minWidth = '300px';
    toast.style.background = '#ffffff';
    toast.style.color = '#111111';
    toast.style.borderLeft = type === 'error' ? '4px solid #f43f5e' : '4px solid #059669';
    toast.style.padding = '1rem 1.25rem';
    toast.style.boxShadow = '0 10px 25px -5px rgba(0,0,0,0.08), 0 8px 10px -6px rgba(0,0,0,0.03)';
    toast.style.display = 'flex';
    toast.style.justifyContent = 'space-between';
    toast.style.alignItems = 'center';
    toast.style.fontFamily = "'Inter', sans-serif";
    toast.style.fontSize = '0.9rem';
    toast.style.fontWeight = '600';
    toast.style.transform = 'translateX(120%)';
    toast.style.opacity = '0';
    toast.style.transition = 'transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.4s ease';

    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <span>${type === 'error' ? '⚠️' : '✨'}</span>
            <span>${message}</span>
        </div>
        <button onclick="this.parentElement.remove()" style="background: none; border: none; font-size: 1.1rem; cursor: pointer; color: #888888; padding-left: 1rem;">&times;</button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
        toast.style.opacity = '1';
    }, 10);

    setTimeout(() => {
        toast.style.transform = 'translateX(120%)';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 400);
    }, 3500);
};

// Global function to process dynamic basket increments/decrements/removals
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
            if (row) row.remove();
            
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
                if (qtyEl) qtyEl.innerText = itemData.quantity;
                if (subEl) subEl.innerText = itemData.subtotal;
                
                window.showToast("Basket quantity updated smoothly!");
            }
        }
    })
    .catch(error => {
        console.error('Error updating cart values:', error);
        window.location.reload();
    });
};

// Stock Toggle Controller Bound Globally to Window Scope
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

// Shipment Update Controller Bound Globally to Window Scope
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
                const row = document.getElementById(`order-row-${orderId}`);
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
                const badge = document.getElementById(`status-badge-${orderId}`);
                if (badge) badge.innerText = data.new_status;
                window.showToast(`Tracking status updated to: ${data.new_status}`);
            }
        }
    })
    .catch(err => console.error("Fulfillment dispatch queue transmission failure:", err));
};

// Clean DOM initialiser processing dataset variables safely
document.addEventListener("DOMContentLoaded", function () {
    const container = document.getElementById('toast-matrix-container');
    if (!container) return;

    const rawData = container.getAttribute('data-messages');
    if (!rawData || rawData.trim() === "") return;

    const messageRows = rawData.split(';').filter(row => row.trim() !== "");
    
    messageRows.forEach(row => {
        const parts = row.split('|');
        if (parts.length === 2) {
            window.showToast(parts, parts);
        }
    });
});

// 🚀 BULLETPROOF REAL-TIME CROSS-BROWSER INTERFACE SYNC LISTENER
// Every time a user clicks back onto or focuses a customer tab, it reads straight from the upgraded database records instantly
document.addEventListener("visibilitychange", function() {
    if (!document.hidden) {
        window.location.reload();
    }
});
// 🚀 Global handler to submit inline product spec alterations
window.asyncEditProduct = function(productId) {
    const url = `/alpha-staff/edit-product/${productId}/`;
    const name = document.getElementById(`edit-name-in-${productId}`).value;
    const price = document.getElementById(`edit-price-in-${productId}`).value;
    const desc = document.getElementById(`edit-desc-in-${productId}`).value;
    
    let formData = new FormData();
    formData.append('edit_name', name);
    formData.append('edit_price', price);
    formData.append('edit_desc', desc);

    fetch(url, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCSRFToken() // Uses your existing CSRF cookie token helper
        },
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            // Update the baseline read-only text fields on the dashboard
            document.getElementById(`display-name-${productId}`).innerText = data.name;
            document.getElementById(`display-price-${productId}`).innerText = `$${data.price}`;
            
            // Toggle the visibility mode box back down softly
            document.getElementById(`edit-form-row-${productId}`).style.display = 'none';
            showToast("Hardware specifications committed successfully!");
        } else {
            showToast(data.error || "Failed to update item.", "error");
        }
    })
    .catch(err => console.error("Product property edit operation failed:", err));
};

// Simple visual toggle helper method
window.toggleEditRow = function(productId) {
    const row = document.getElementById(`edit-form-row-${productId}`);
    row.style.display = row.style.display === 'none' ? 'table-row' : 'none';
};
