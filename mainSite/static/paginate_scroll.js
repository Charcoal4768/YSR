const productList = document.getElementById('product-list');

let currentPage = 2; // first page (2 categories) loaded server-side
let isLoading = false;
let hasMore = true;
const loadedCategories = new Set(); // 🔑 track categories already rendered

const loadingIndicator = document.getElementById('loading');

const fetchProducts = async (page) => {
    if (isLoading || !hasMore) return;
    isLoading = true;
    loadingIndicator.style.display = 'block';

    try {
        const response = await fetch(`/api/products?page=${page}`);
        const data = await response.json();

        data.categories.forEach(category => {
            if (loadedCategories.has(category.name)) {
                return; // skip duplicate category
            }
            loadedCategories.add(category.name);

            const categorySection = document.createElement('div');
            categorySection.className = 'category-section';

            const categoryHeading = document.createElement('div');
            categoryHeading.className = 'layer left category-heading animate left';
            categoryHeading.innerHTML = `<h2 id="cat-${category.name}">${category.name}</h2>`;
            categorySection.appendChild(categoryHeading);

            const productContainer = document.createElement('div');
            productContainer.className = 'layer right';

            category.products.forEach(product => {
                const productCard = document.createElement('div');
                productCard.className = 'productCard animate up';
                productCard.innerHTML = `
                    <div class="mobileTitle"><h2>${product.name}</h2></div>
                    <div class="productLogo"><div class="publishedLogo">
                        <img src="${product.image_url}" alt="${product.name}">
                    </div></div>
                    <div class="productBody">
                        <h2>${product.name}</h2>
                        <div class="spacer"></div>
                        <p>${product.description}</p>
                        <div class="tags">
                            ${product.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                        </div>
                    </div>
                `;
                productContainer.appendChild(productCard);
            });

            categorySection.appendChild(productContainer);
            productList.appendChild(categorySection);
            window.observeAnimateElements();
            window.addSideBarLinks();
        });

        currentPage++;
        hasMore = data.has_next;

    } catch (error) {
        console.error('Error fetching products:', error);
    } finally {
        isLoading = false;
        loadingIndicator.style.display = 'none';
    }
};

window.addEventListener('scroll', () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 500) {
        console.log('Fetching more products...');
        fetchProducts(currentPage);
    }
});
