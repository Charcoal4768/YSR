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

    moreTags.addEventListener("click", () => {
        const newTag = document.createElement("span");
        newTag.classList.add("tag");
        newTag.contentEditable = "true";
        newTag.textContent = "New Category";

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
        publishProductButton.disabled = true;
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
                    console.log(formData);
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
                                productName.textContent = "";
                                productDescription.textContent = "";
                                file = null;
                                document.querySelector(".customFileupload").style.backgroundImage = "";
                                document.querySelector(".tags")
                                    .querySelectorAll(".tag").forEach(tag => {
                                        tag.remove();
                                    });
                                publishProductButton.disabled = false;
                            } else {
                                if (data.errordata.error.includes('duplicate key value violates unique constraint "product_tags_pkey"')) {
                                    console.error("Error publishing product:", data.error);
                                    const uniqueTags = new Set();
                                    productData.tags = productData.tags.filter(tagId => {
                                        const combination = `${productData.id}-${tagId}`;
                                        if (uniqueTags.has(combination)) {
                                            return false;
                                        } else {
                                            uniqueTags.add(combination);
                                            return true;
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

    const productsSection = document.querySelector(".productsSection");
    let originalCardState = {};

    const setEditable = (card, isEditable) => {
        card.querySelectorAll('.product-name, .product-description, .tags .tag').forEach(el => {
            el.contentEditable = isEditable;
        });
        card.querySelector('.edit-btn').style.display = isEditable ? 'none' : 'block';
        card.querySelector('.delete-btn').style.display = isEditable ? 'none' : 'block';
        card.querySelector('.save-btn').style.display = isEditable ? 'block' : 'none';
        card.querySelector('.cancel-btn').style.display = isEditable ? 'block' : 'none';
        card.querySelector('.add-tags-btn').style.display = isEditable ? 'inline-block' : 'none';
        card.classList.toggle('is-editing', isEditable);
        if (isEditable) {
            card.querySelector('.productLogo').style.cursor = 'pointer';
        } else {
            card.querySelector('.productLogo').style.cursor = 'default';
        }
    };

    const getPublishToken = async () => {
        const response = await fetch('/api/request_new_token', {
            method: 'GET',
            credentials: 'include'
        });
        if (!response.ok) return null;
        const data = await response.json();
        return data.publish_token;
    };

    if (productsSection) {
        productsSection.addEventListener("click", async (event) => {
            const target = event.target;
            const card = target.closest('.productCard');
            if (!card) return;

            const productId = card.dataset.productId;

            if (target.classList.contains('edit-btn')) {
                originalCardState[productId] = card.innerHTML;
                setEditable(card, true);
            }

            if ((target.classList.contains('product-image') || target.closest('.productLogo')) && card.classList.contains('is-editing')) {
                card.querySelector('.edit-product-image').click();
            }

            if (target.classList.contains('cancel-btn')) {
                if (originalCardState[productId]) {
                    card.innerHTML = originalCardState[productId];
                    delete originalCardState[productId];
                }
            }

            if (target.classList.contains('add-tags-btn')) {
                const newTag = document.createElement("span");
                newTag.className = "tag";
                newTag.contentEditable = "true";
                newTag.textContent = "New Tag";
                target.before(newTag);
                newTag.focus();
            }

            if (target.classList.contains('delete-btn')) {
                if (confirm('Are you sure you want to delete this product?')) {
                    const token = await getPublishToken();
                    if (!token) return alert("Error: Could not get authorization.");
                    const response = await fetch(`/api/delete_product/${productId}`, {
                        method: 'DELETE',
                        credentials: 'include',
                        headers: {
                            'Publish-Token': token
                        }
                    });
                    const data = await response.json();
                    if (data.success) card.remove();
                    else alert(`Error: ${data.error}`);
                }
            }

            if (target.classList.contains('save-btn')) {
                target.disabled = true;
                const token = await getPublishToken();
                if (!token) {
                    alert("Error: Could not get authorization.");
                    return target.disabled = false;
                }

                const formData = new FormData();
                formData.append('name', card.querySelector('.productBody .product-name').textContent.trim());
                formData.append('description', card.querySelector('.product-description').textContent.trim());
                formData.append('tags', JSON.stringify(Array.from(card.querySelectorAll('.tags .tag')).map(t => t.textContent.trim())));
                const imageFile = card.querySelector('.edit-product-image').files[0];
                if (imageFile) formData.append('image', imageFile);

                const response = await fetch(`/api/edit_product/${productId}`, {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Publish-Token': token
                    },
                    body: formData
                });
                const data = await response.json();

                if (data.success) {
                    card.querySelector('.product-image').src = data.product.image_url;
                    setEditable(card, false);
                } else {
                    alert(`Error: ${data.error}`);
                }
                target.disabled = false;
            }
        });

        productsSection.addEventListener('change', (event) => {
            if (event.target.classList.contains('edit-product-image')) {
                const card = event.target.closest('.productCard');
                const file = event.target.files[0];
                if (file && card) {
                    const reader = new FileReader();
                    reader.onload = (e) => card.querySelector('.product-image').src = e.target.result;
                    reader.readAsDataURL(file);
                }
            }
        });

        productsSection.addEventListener('blur', (event) => {
            if (event.target.classList.contains('tag') && event.target.isContentEditable && event.target.textContent.trim() === "") {
                event.target.remove();
            }
        }, true);
    }
});