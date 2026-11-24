(() => {
  "use strict";

  const PRODUCTS = [
    { id: "basic", name: "Basic", description: "Everyday essentials", price: 100, stock: 10, eligible: true, icon: "B" },
    { id: "premium", name: "Premium", description: "A considered upgrade", price: 250, stock: 3, eligible: true, icon: "P" },
    { id: "gift", name: "Gift item", description: "Limited seasonal item", price: 25, stock: 0, eligible: false, icon: "G" },
  ];
  const SHIPPING_FEE = 20;
  const cart = new Map();
  let promoApplied = false;
  let orderCreated = false;
  let orderCount = 0;

  const byId = (id) => document.getElementById(id);
  const money = (value) => `CU ${value.toFixed(2)}`;
  const grid = byId("product-grid");
  const cartItems = byId("cart-items");
  const form = byId("checkout-form");
  const delivery = byId("fulfilment");
  const address = byId("address");

  function renderProducts() {
    grid.innerHTML = PRODUCTS.map((product) => {
      const quantity = cart.get(product.id) || 0;
      const unavailable = product.stock === 0;
      const atLimit = quantity >= product.stock;
      return `
        <article class="product-card" data-product-id="${product.id}">
          <div class="product-art" aria-hidden="true">${product.icon}</div>
          <h3>${product.name}</h3>
          <p class="product-description">${product.description}</p>
          <div class="product-bottom">
            <div><span class="product-price">${money(product.price)}</span><span class="stock ${unavailable ? "out" : ""}">${unavailable ? "Out of stock" : `${product.stock - quantity} available`}</span></div>
            <button class="button button-secondary" type="button" data-action="add" data-product="${product.id}" ${unavailable || atLimit ? "disabled" : ""}>${unavailable ? "Unavailable" : "Add " + product.name}</button>
          </div>
        </article>`;
    }).join("");
  }

  function totals() {
    let subtotal = 0;
    let eligibleSubtotal = 0;
    for (const [id, quantity] of cart) {
      const product = PRODUCTS.find((item) => item.id === id);
      const line = product.price * quantity;
      subtotal += line;
      if (product.eligible) eligibleSubtotal += line;
    }
    const discount = promoApplied ? Math.round(eligibleSubtotal * 0.10 * 100) / 100 : 0;
    const shipping = cart.size > 0 && delivery.value === "delivery" ? SHIPPING_FEE : 0;
    return { subtotal, discount, shipping, total: subtotal - discount + shipping };
  }

  function renderCart() {
    if (cart.size === 0) {
      cartItems.innerHTML = '<p class="empty-state">Your cart is empty. Add a product to begin.</p>';
    } else {
      cartItems.innerHTML = [...cart.entries()].map(([id, quantity]) => {
        const product = PRODUCTS.find((item) => item.id === id);
        return `
          <div class="cart-row" data-testid="cart-item" data-product-id="${id}">
            <div><div class="cart-product-name">${product.name}</div><div class="cart-meta">${money(product.price)} each · ${money(product.price * quantity)} line total</div></div>
            <div class="cart-actions">
              <div class="quantity-control" aria-label="Quantity for ${product.name}">
                <button type="button" data-action="decrease" data-product="${id}" aria-label="Decrease quantity for ${product.name}">−</button>
                <span class="quantity-value" data-testid="quantity-${id}">${quantity}</span>
                <button type="button" data-action="increase" data-product="${id}" aria-label="Increase quantity for ${product.name}" ${quantity >= product.stock ? "disabled" : ""}>+</button>
              </div>
              <button class="remove-item" type="button" data-action="remove" data-product="${id}" aria-label="Remove ${product.name}">Remove</button>
            </div>
          </div>`;
      }).join("");
    }

    const count = [...cart.values()].reduce((sum, value) => sum + value, 0);
    byId("cart-count").textContent = `${count} ${count === 1 ? "item" : "items"}`;
    const summary = totals();
    byId("subtotal").textContent = money(summary.subtotal);
    byId("discount").textContent = `− ${money(summary.discount)}`;
    byId("shipping").textContent = money(summary.shipping);
    byId("total").textContent = money(summary.total);
    byId("place-order").textContent = `Place order · ${money(summary.total)}`;
    byId("place-order").disabled = cart.size === 0 || orderCreated;
    renderProducts();
  }

  function updateAddressRequirement() {
    const isDelivery = delivery.value === "delivery";
    address.required = isDelivery;
    byId("address-hint").textContent = isDelivery ? "(required)" : "(not required for pickup)";
    address.placeholder = isDelivery ? "Street and building number" : "Optional for pickup";
  }

  grid.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-action='add']");
    if (!button || button.disabled) return;
    const id = button.dataset.product;
    const product = PRODUCTS.find((item) => item.id === id);
    const current = cart.get(id) || 0;
    if (current < product.stock) cart.set(id, current + 1);
    renderCart();
  });

  cartItems.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-action]");
    if (!button) return;
    const { action, product: id } = button.dataset;
    const current = cart.get(id) || 0;
    const product = PRODUCTS.find((item) => item.id === id);
    if (action === "increase" && current < product.stock) cart.set(id, current + 1);
    if (action === "decrease" && current > 1) cart.set(id, current - 1);
    if (action === "remove" || (action === "decrease" && current === 1)) cart.delete(id);
    renderCart();
  });

  byId("apply-promo").addEventListener("click", () => {
    const code = byId("promo-code").value.trim().toUpperCase();
    const feedback = byId("promo-feedback");
    feedback.classList.remove("error");
    if (code === "SAVE10" && promoApplied) {
      feedback.textContent = "SAVE10 is already applied. The discount has not been duplicated.";
      return;
    }
    if (code === "SAVE10") {
      promoApplied = true;
      feedback.textContent = "SAVE10 applied: 10% off eligible products.";
    } else {
      promoApplied = false;
      feedback.classList.add("error");
      feedback.textContent = code === "EXPIRED" ? "This promo code has expired." : "Promo code not recognised.";
    }
    renderCart();
  });

  delivery.addEventListener("change", () => {
    updateAddressRequirement();
    renderCart();
  });

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const feedback = byId("form-feedback");
    feedback.textContent = "";
    feedback.classList.remove("error");
    if (orderCreated || cart.size === 0) return;
    if (!form.reportValidity()) return;
    orderCreated = true;
    byId("place-order").disabled = true;
    byId("place-order").textContent = "Submitting order…";
    window.setTimeout(() => {
      orderCount += 1;
      byId("orders-created").textContent = String(orderCount);
      const orderReference = `NS-${String(orderCount).padStart(5, "0")}`;
      byId("order-reference").textContent = orderReference;
      byId("order-confirmation").hidden = false;
      form.hidden = true;
    }, 120);
  });

  updateAddressRequirement();
  renderCart();
})();
