/**
 * 🚀 Alpha Store Core Client-Side Interactivity Engine
 * Handles Flash-Free AJAX Shopping Updates and Dynamic Toast Alerts
 */

// Global function to spawn premium toast notifications dynamically
function showToast(message, type = 'success') {
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
}

// Global function to process dynamic quantity and removal updates without page refreshes
function modifyCart(action, productId) {
    const url = `/cart/${action}/${productId}/`;
    
    fetch(url, {
        method: 'GET',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => {
        // 1. Update overall grand totals instantly
        document.querySelectorAll('.grand-total-val').forEach(el => {
            el.innerText = data.total_price;
        });

        // 2. Handle visual row elimination
        if (action === 'remove' || data.removed === true) {
            const row = document.getElementById(`row-${productId}`);
            if (row) row.remove();
            
            showToast("Item completely removed from basket", "error");
            
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
            // 3. Update active item details on layout rows
            const itemData = data.items[productId];
            if (itemData) {
                const qtyEl = document.getElementById(`qty-${productId}`);
                const subEl = document.getElementById(`subtotal-${productId}`);
                if (qtyEl) qtyEl.innerText = itemData.quantity;
                if (subEl) subEl.innerText = itemData.subtotal;
                
                showToast("Basket quantity updated smoothly!");
            }
        }
    })
    .catch(error => console.error('Error updating cart values:', error));
}
// 🚀 Add this clean event block to the absolute bottom of your static/shop/cart.js file:
document.addEventListener("DOMContentLoaded", function () {
    const container = document.getElementById('toast-matrix-container');
    if (!container) return;

    const rawData = container.getAttribute('data-messages');
    if (!rawData || rawData.trim() === "") return;

    // Parse the pipeline separated messages strings safely
    const messageRows = rawData.split(';').filter(row => row.trim() !== "");
    
    messageRows.forEach(row => {
        const parts = row.split('|');
        if (parts.length === 2) {
            const msgText = parts[0];
            const msgType = parts[1];
            showToast(msgText, msgType);
        }
    });
});
