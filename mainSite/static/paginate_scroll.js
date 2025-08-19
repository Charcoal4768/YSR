// infinite_scroll.js

// Get the product list container and read the data attributes
const productList = document.getElementById('product-list');

// Initialize state from the data attributes
let currentPage = parseInt(productList.dataset.page) + 1;
let isLoading = false;
let hasMore = productList.dataset.hasNext === 'True';

const loadingIndicator = document.getElementById('loading');

// Function to fetch products from the API
const fetchProducts = async (page) => {
    if (isLoading || !hasMore) return;

    isLoading = true;
    loadingIndicator.style.display = 'block';

    try {
        const response = await fetch(`/api/products?page=${page}`);
        const data = await response.json();

        // Loop through the received categories and products and append them to the page
        for (const category in data.categories) {
            if (data.categories.hasOwnProperty(category)) {
                const categoryProducts = data.categories[category];

                // Create a new section for the category
                const categorySection = document.createElement('div');
                categorySection.className = 'category-section';

                const categoryHeading = document.createElement('div');
                categoryHeading.className = 'layer left category-heading animate up';
                categoryHeading.innerHTML = `<h2>${category}</h2>`;
                categorySection.appendChild(categoryHeading);

                const productContainer = document.createElement('div');
                productContainer.className = 'layer right';

                categoryProducts.forEach(product => {
                    const productCard = document.createElement('div');
                    productCard.className = 'productCard animate up';
                    productCard.innerHTML = `
                        <div class="mobileTitle">
                            <h2>${product.name}</h2>
                        </div>
                        <div class="productLogo">
                            <div class="publishedLogo">
                                <img src="${product.image_url}" alt="${product.name}">
                            </div>
                        </div>
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
            }
        }

        // Update the state for the next fetch
        currentPage += 1;
        hasMore = data.has_next;

    } catch (error) {
        console.error('Error fetching products:', error);
    } finally {
        isLoading = false;
        loadingIndicator.style.display = 'none';
    }
};

// Event listener for infinite scrolling
window.addEventListener('scroll', () => {
    // Check if the user has scrolled to the bottom of the page
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 500) {
        fetchProducts(currentPage);
    }
});