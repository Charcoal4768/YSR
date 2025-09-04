const productList = document.getElementById('product-list');

let currentPage = 1;
let isLoading = false;
let hasMore = true;

const loadingIndicator = document.getElementById('loading');

const fetchProducts = async (page) => {
    if (isLoading || !hasMore) return;
    isLoading = true;
    loadingIndicator.style.display = 'block';

    try {
        const response = await fetch(`/api/products_all?page=${page}`);
        const data = await response.json();

        data.products.forEach(product => {
            const productCard = document.createElement('div');
            productCard.className = 'productCard animate up';
            productCard.dataset.productId = product.id;
            productCard.innerHTML = `
                <div class="admin-controls" style="position: absolute; top: 10px; right: 10px; display: flex; gap: 5px;">
                    <button type="button" class="smallButton edit-btn">Edit</button>
                    <button type="button" class="smallButton delete-btn">Delete</button>
                    <button type="button" class="smallButton save-btn" style="display: none;">Save</button>
                    <button type="button" class="smallButton cancel-btn" style="display: none;">Cancel</button>
                </div>
                <div class="mobileTitle">
                    <h2 class="product-name" contenteditable="false">${product.name}</h2>
                </div>
                <div class="productLogo">
                    <div class="publishedLogo">
                        <img src="${product.image_url}" alt="${product.name}" class="product-image">
                        <input type="file" class="edit-product-image" accept="image/*" hidden>
                    </div>
                </div>
                <div class="productBody">
                    <h2 class="product-name" contenteditable="false">${product.name}</h2>
                    <div class="spacer"></div>
                    <p class="product-description" contenteditable="false">${product.description}</p>
                    <div class="tags">
                        ${product.tags.map(tag => `<span class="tag" contenteditable="false">${tag}</span>`).join('')}
                        <button type="button" class="smallButton add-tags-btn" style="display: none;">+</button>
                    </div>
                </div>
            `;
            productList.appendChild(productCard);
        });

        currentPage++;
        hasMore = data.has_next;
        window.observeAnimateElements();

    } catch (error) {
        console.error('Error fetching products:', error);
    } finally {
        isLoading = false;
        loadingIndicator.style.display = 'none';
    }
};

let throttleTimeout = null;
window.addEventListener('scroll', () => {
    if (throttleTimeout) return;
    throttleTimeout = setTimeout(() => {
        throttleTimeout = null;
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 800) {
            console.log('Fetching more products...');
            fetchProducts(currentPage);
        }
    }, 200);
});

fetchProducts(1);