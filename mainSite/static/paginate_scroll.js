const productList = document.getElementById('product-list');

let currentPage = 1;
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
                const description = product.description;
                const maxLength = 55;
                let productDescriptionHTML;

                // Conditionally apply 'Read More' logic based on screen size
                if (description.length > maxLength && window.matchMedia('(max-width: 768px)').matches) {
                    const truncated = description.substring(0, maxLength);
                    const fullText = description.substring(maxLength);
                    productDescriptionHTML = `
                        <p class="product-description" data-original-text="${description}">
                            <span class="truncated-text">${truncated}</span>
                            <span class="more-text hidden">${fullText}</span>
                            <a href="javascript:void(0);" class="read-more-btn">...Read More</a>
                        </p>
                    `;
                } else {
                    productDescriptionHTML = `<p class="product-description">${description}</p>`;
                }
                const productCard = document.createElement('div');
                productCard.className = 'productCard animate up';
                productCard.innerHTML = `
                    <div class="mobileTitle">
                        <h2>${product.name}</h2>
                    </div>
                    <div class="productLogo">
                        <div class="publishedLogo">
                            <img src="${product.image_url}" alt="${product.name}" loading="lazy">
                        </div>
                    </div>
                    <div class="productBody">
                        <h2>${product.name}</h2>
                        <div class="spacer"></div>
                        ${productDescriptionHTML}
                        <div class="tags">
                            ${product.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                        </div>
                    </div>
                `;

                productContainer.appendChild(productCard);

                // Add the event listener for the new card
                if (description.length > maxLength && window.matchMedia('(max-width: 768px)').matches) {
                    const readMoreBtn = productCard.querySelector('.read-more-btn');
                    readMoreBtn.addEventListener('click', function() {
                        const descriptionContainer = this.parentElement;
                        const truncatedSpan = descriptionContainer.querySelector('.truncated-text');
                        const moreSpan = descriptionContainer.querySelector('.more-text');
                        
                        if (moreSpan.classList.contains('hidden')) {
                            moreSpan.classList.remove('hidden');
                            this.textContent = 'Read Less';
                        } else {
                            moreSpan.classList.add('hidden');
                            this.textContent = '...Read More';
                        }
                    });
                }
            });

            categorySection.appendChild(productContainer);
            productList.appendChild(categorySection);
            window.observeAnimateElements();
            window.addSideBarLinks();
        });

        currentPage++;
        hasMore = data.has_next;

    } catch (error) {
        console.error('Error fetching products:');
    } finally {
        isLoading = false;
        loadingIndicator.style.display = 'none';
    }
};

let throttleTimeout = null;

window.addEventListener('scroll', () => {
    if (throttleTimeout) return; // exit if we're waiting

    throttleTimeout = setTimeout(() => {
        throttleTimeout = null; // reset throttle

        if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 800) {
            console.log('Fetching more products...');
            fetchProducts(currentPage);
        }
    }, 200); // throttle interval in ms (adjust as needed)
});
fetchProducts(1)