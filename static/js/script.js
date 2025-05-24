/**
 * E-Commerce Platform Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Product Image Carousel Thumbnails
    const thumbnails = document.querySelectorAll('.img-thumbnail');
    if (thumbnails.length > 0) {
        thumbnails.forEach(thumbnail => {
            thumbnail.addEventListener('click', function() {
                const target = this.getAttribute('data-bs-target');
                const slideTo = this.getAttribute('data-bs-slide-to');
                const carousel = document.querySelector(target);
                
                if (carousel) {
                    const carouselInstance = bootstrap.Carousel.getInstance(carousel);
                    if (carouselInstance) {
                        carouselInstance.to(slideTo);
                    }
                }
            });
        });
    }

    // Product quantity increments
    const quantityInputs = document.querySelectorAll('.quantity-input');
    if (quantityInputs.length > 0) {
        quantityInputs.forEach(input => {
            const incrementBtn = input.parentElement.querySelector('.increment-qty');
            const decrementBtn = input.parentElement.querySelector('.decrement-qty');
            
            if (incrementBtn) {
                incrementBtn.addEventListener('click', function() {
                    let value = parseInt(input.value);
                    let max = parseInt(input.getAttribute('max')) || 99;
                    
                    if (value < max) {
                        input.value = value + 1;
                        input.dispatchEvent(new Event('change'));
                    }
                });
            }
            
            if (decrementBtn) {
                decrementBtn.addEventListener('click', function() {
                    let value = parseInt(input.value);
                    
                    if (value > 1) {
                        input.value = value - 1;
                        input.dispatchEvent(new Event('change'));
                    }
                });
            }
        });
    }
    
    // Handle image uploads for product forms
    const fileInput = document.getElementById('product-images');
    const imagePreviewContainer = document.getElementById('image-preview-container');
    const uploadedImagesInput = document.getElementById('uploaded-images');
    
    if (fileInput && imagePreviewContainer) {
        fileInput.addEventListener('change', function() {
            const files = this.files;
            
            if (files.length > 0) {
                for (let i = 0; i < files.length; i++) {
                    const file = files[i];
                    const reader = new FileReader();
                    
                    reader.onload = function(e) {
                        // Create a preview element
                        const preview = document.createElement('div');
                        preview.className = 'image-preview';
                        preview.innerHTML = `
                            <img src="${e.target.result}" alt="Preview">
                            <span class="remove-image" data-index="${i}"><i class="fas fa-times"></i></span>
                        `;
                        
                        imagePreviewContainer.appendChild(preview);
                        
                        // Upload the image to the server
                        uploadImage(file);
                    }
                    
                    reader.readAsDataURL(file);
                }
            }
        });
        
        // Handle removing images
        imagePreviewContainer.addEventListener('click', function(e) {
            if (e.target.closest('.remove-image')) {
                const preview = e.target.closest('.image-preview');
                const images = JSON.parse(uploadedImagesInput.value || '[]');
                const index = Array.from(imagePreviewContainer.children).indexOf(preview);
                
                // Remove the image URL from the array
                if (index >= 0 && index < images.length) {
                    images.splice(index, 1);
                    uploadedImagesInput.value = JSON.stringify(images);
                }
                
                // Remove the preview element
                preview.remove();
            }
        });
        
        // Function to upload an image
        function uploadImage(file) {
            const formData = new FormData();
            formData.append('file', file);
            
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.url) {
                    // Add the uploaded image URL to the hidden input
                    const images = JSON.parse(uploadedImagesInput.value || '[]');
                    images.push(data.url);
                    uploadedImagesInput.value = JSON.stringify(images);
                }
            })
            .catch(error => {
                console.error('Error uploading image:', error);
            });
        }
    }
    
    // Order status updates
    const orderStatusSelect = document.getElementById('order-status-select');
    const orderStatusForm = document.getElementById('order-status-form');
    
    if (orderStatusSelect && orderStatusForm) {
        orderStatusSelect.addEventListener('change', function() {
            if (confirm('Are you sure you want to update the order status?')) {
                orderStatusForm.submit();
            } else {
                // Reset to previous value
                this.value = this.getAttribute('data-current-status');
            }
        });
    }
    
    // Store customization (theme color)
    const themeColorInput = document.getElementById('theme-color');
    const themeColorPreview = document.getElementById('theme-color-preview');
    
    if (themeColorInput && themeColorPreview) {
        themeColorInput.addEventListener('input', function() {
            themeColorPreview.style.backgroundColor = this.value;
        });
    }
    
    // Product search autocomplete
    const searchInput = document.querySelector('input[name="search"]');
    const autocompleteResults = document.getElementById('autocomplete-results');
    
    if (searchInput && autocompleteResults) {
        let debounceTimer;
        
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            
            clearTimeout(debounceTimer);
            
            if (query.length < 2) {
                autocompleteResults.innerHTML = '';
                autocompleteResults.style.display = 'none';
                return;
            }
            
            debounceTimer = setTimeout(() => {
                // Send request to search API
                fetch(`/api/search?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        autocompleteResults.innerHTML = '';
                        
                        if (data.length > 0) {
                            data.forEach(item => {
                                const resultItem = document.createElement('div');
                                resultItem.className = 'autocomplete-item';
                                resultItem.innerHTML = `
                                    <a href="/product/${item.id}" class="d-flex align-items-center p-2">
                                        <img src="${item.image || '/static/img/no-image.png'}" alt="${item.name}" class="me-2" style="width: 40px; height: 40px; object-fit: cover;">
                                        <div>
                                            <div>${item.name}</div>
                                            <small class="text-muted">${item.price}</small>
                                        </div>
                                    </a>
                                `;
                                autocompleteResults.appendChild(resultItem);
                            });
                            
                            autocompleteResults.style.display = 'block';
                        } else {
                            autocompleteResults.style.display = 'none';
                        }
                    })
                    .catch(error => {
                        console.error('Search error:', error);
                    });
            }, 300);
        });
        
        // Hide autocomplete on click outside
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !autocompleteResults.contains(e.target)) {
                autocompleteResults.style.display = 'none';
            }
        });
    }
    
    // Category filter in market page
    const categoryFilters = document.querySelectorAll('.category-filter');
    if (categoryFilters.length > 0) {
        categoryFilters.forEach(filter => {
            filter.addEventListener('change', function() {
                const form = this.closest('form');
                if (form) {
                    form.submit();
                }
            });
        });
    }
});
