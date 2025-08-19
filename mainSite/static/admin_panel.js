document.addEventListener("DOMContentLoaded", () => {
    const addProductButton = document.getElementById("add-product-menu-button");
    const publishProductButton = document.getElementById("add-product-button");
    const uploadFileButton = document.getElementById("upload-file-button");
    const productFieldsContainer = document.getElementById("product-fields-container");
    const fileInput = document.getElementById("new-product-image");
    const productName = document.getElementById("new-product-name");
    const productDescription = document.getElementById("new-product-description");
    const mobileProductName = document.getElementById("new-product-mobile-name");
    const moreTags = document.getElementById("add-tags");
    let file = null;

    function getLocalData() {
        const tags = Array.from(document.querySelectorAll("#product-fields-container .tags .tag")).map(tag => tag.textContent.trim()).filter(text => text !== "");
        return {
            name: productName.textContent.trim(),
            description: productDescription.textContent.trim(),
            image: file,
            tags: tags
        };
    }

    addProductButton.addEventListener("click", () => {
        productFieldsContainer.classList.toggle("visible");
    });

    uploadFileButton.addEventListener("click", () => {
        fileInput.click();
    });

    fileInput.addEventListener("change", (event) => {
        file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                document.querySelector(".customFileupload").style.backgroundImage = `url(${e.target.result})`;
            };
            reader.readAsDataURL(file);
        }
    });

    productName.addEventListener("input", () => {
        mobileProductName.textContent = productName.textContent;
    });

    mobileProductName.addEventListener("input", () => {
        productName.textContent = mobileProductName.textContent;
    });

// admin_panel.js (Updated)

    moreTags.addEventListener("click", () => {
        const newTag = document.createElement("span");
        newTag.classList.add("tag");
        newTag.contentEditable = "true";
        newTag.textContent = "New Category";
        
        // Use a more specific selector here as well
        const tagsContainer = document.querySelector("#product-fields-container .tags");
        tagsContainer.insertBefore(newTag, moreTags);
    });

    document.querySelector("#product-fields-container .tags").addEventListener("input", (event) => {
        if (event.target.classList.contains("tag") && event.target.textContent.trim() === "") {
            event.target.remove();
        }
    });

    publishProductButton.addEventListener("click", () => {
        const productData = getLocalData();
        
        fetch('/api/request_new_token', {
            method: 'GET',
            credentials: 'include'
        })
        .then(response => response.json())
        .then(tokenData => {
            if (tokenData.publish_token) {
                const formData = new FormData();
                formData.append('name', productData.name);
                formData.append('description', productData.description);
                formData.append('image', productData.image);
                formData.append('tags', JSON.stringify(productData.tags));
                console.log(formData)
                // Now, use the received token to publish the product
                fetch('/api/publish_product', {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Publish-Token': tokenData.publish_token
                    },
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        console.log("Product published successfully:", data.product);
                        // clear all data and refresh page
                        productName.textContent = "";
                        productDescription.textContent = "";
                        file = null;
                        document.querySelector(".customFileupload").style.backgroundImage = "none";
                        document.querySelector(".tags").innerHTML = "";
                        location.reload();
                    } else {
                        if (data.errordata.error.includes('duplicate key value violates unique constraint "product_tags_pkey"')) {
                            console.error("Error publishing product:", data.error);
                            const uniqueTags = new Set();
                            productData.tags = productData.tags.filter(tagId => {
                            const combination = `${productData.id}-${tagId}`;
                            if (uniqueTags.has(combination)) {
                                return false; // Remove duplicate
                            } else {
                                uniqueTags.add(combination);
                                return true; // Keep unique
                                }
                            });
                        }
                        console.error("Failed to publish product:", data.error);
                    }
                })
                .catch(error => {
                    console.error("Error publishing product:", error);
                });
            } else {
                console.error("Failed to retrieve publish token");
            }
        })
        .catch(error => {
            console.error("Error fetching publish token:", error);
        });
    });
});