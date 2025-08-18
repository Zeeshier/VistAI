// Navbar scroll effect
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 20) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// File upload functionality (only on index page)
if (document.getElementById('drop-zone')) {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const preview = document.getElementById('preview');
    const browse = document.querySelector('.browse');
    const uploadBtn = document.getElementById('upload-btn');

    // Browse file click
    browse.addEventListener('click', () => {
        fileInput.click();
    });

    // File input change
    fileInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            
            reader.onload = function(e) {
                preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
                dropZone.style.borderStyle = 'solid';
            }
            
            reader.readAsDataURL(this.files[0]);
        }
    });

    // Drag and drop functionality
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropZone.style.borderColor = '#4a4a4a';
        dropZone.style.backgroundColor = '#111111';
    }

    function unhighlight() {
        dropZone.style.borderColor = '#222222';
        dropZone.style.backgroundColor = '#0e0e0e';
    }

    // Handle file drop
    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length) {
            fileInput.files = files;
            const changeEvent = new Event('change');
            fileInput.dispatchEvent(changeEvent);
        }
    }

    // Upload button click
    uploadBtn.addEventListener('click', () => {
        if (fileInput.files.length === 0) {
            alert('Please select a T-shirt image first');
            return;
        }
        
        // Simulate loading
        uploadBtn.textContent = 'Processing...';
        uploadBtn.disabled = true;

        // Create FormData to send the image to Flask API
        const formData = new FormData();
        formData.append('image', fileInput.files[0]);

        // Send image to Flask API
        fetch('/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json()) // Get the JSON response
        .then(data => {
            // Store the data in sessionStorage
            sessionStorage.setItem('resultsData', JSON.stringify(data));
            window.location.href = '/results.html';
        })
        .catch(error => {
            console.error('Error uploading image:', error);
            alert('Error processing image. Please try again.');
            uploadBtn.textContent = 'Upload';
            uploadBtn.disabled = false;
        });
    });
}

// Results page initialization
if (document.getElementById('product-gallery')) {
    const gallery = document.getElementById('product-gallery');
    const uploadedImageContainer = document.getElementById('uploaded-image');

    // Fetch results from sessionStorage (set by Flask)
    const resultsData = sessionStorage.getItem('resultsData');
    
    if (resultsData) {
        // Parse the JSON data
        const data = JSON.parse(resultsData);
        const results = data.results;
        const recommendation = data.recommendation;
        const uploadedImage = data.uploaded_image;
        const uploadedImageUrl = data.uploaded_image_url || `/static/uploads/${uploadedImage}`;
        const uploadedImageUrlCacheBusted = `${uploadedImageUrl}${uploadedImageUrl.includes('?') ? '&' : '?'}v=${Date.now()}`;
        


        // Display uploaded image
        uploadedImageContainer.innerHTML = `
            <h3>Uploaded T-Shirt</h3>
            <img src="${uploadedImageUrlCacheBusted}" alt="Uploaded T-Shirt" style="max-width: 300px; max-height: 400px; object-fit: contain;">
        `;

        // Render similar products (visual search results)
        results.forEach((product, index) => {
            const card = document.createElement('div');
            card.className = `card fade-in`;
            card.innerHTML = `
                <img src="${product.image_path}" alt="${product.product_id}">
                <div class="overlay">
                    <h4>${product.product_id}</h4>
                    <p>Category: ${product.category}</p>
                    <p>Color: ${product.color}</p>
                </div>
            `;
            gallery.appendChild(card);
            card.style.animationDelay = `${index * 0.1}s`;
        });

        // Render RL-recommended product
        const recommendationCard = document.createElement('div');
        recommendationCard.className = 'card fade-in rl-recommended';
        recommendationCard.innerHTML = `
            <img src="${recommendation.image_path}" alt="${recommendation.product_id}">
            <div class="overlay">
                <h4>${recommendation.product_id} (Recommended)</h4>
                <p>Category: ${recommendation.category}</p>
                <p>Color: ${recommendation.color}</p>
            </div>
        `;
        gallery.appendChild(recommendationCard);
        recommendationCard.style.animationDelay = `${results.length * 0.1}s`;

        // Add fade-in effect to section title
        document.querySelector('.section-title').classList.add('fade-in');
    } else {
        console.error('No results data found in sessionStorage');
        gallery.innerHTML = '<p>Error loading results. Please try again.</p>';
    }
}