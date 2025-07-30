const API_BASE_URL = 'http://localhost:8000';
const resultsDiv = document.getElementById('results');
const loadingDiv = document.getElementById('loading');
const searchInput = document.getElementById('searchInput');
const numImagesSelect = document.getElementById('numImages');

// Show/hide loading spinner
function toggleLoading(show) {
    loadingDiv.classList.toggle('hidden', !show);
}

// Display error message
function showError(message) {
    resultsDiv.innerHTML = `<div class="error">${message}</div>`;
}

// Toast notification
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;
    
    setTimeout(() => {
        toast.className = 'toast';
    }, 3000);
}

// Download image
async function downloadImage(url, filename) {
    try {
        toggleLoading(true);
        const response = await fetch(`${API_BASE_URL}/api/download/?url=${encodeURIComponent(url)}`);
        if (!response.ok) throw new Error('Download failed');
        
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = filename || url.split('/').pop();
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(downloadUrl);
        
        showToast('Image downloaded successfully!');
    } catch (error) {
        showToast('Download failed: ' + error.message, 'error');
    } finally {
        toggleLoading(false);
    }
}

// Create image card HTML
function createImageCard(image) {
    const filename = image.url.split('/').pop();
    return `
        <div class="image-card">
            <img src="${image.url}" alt="${image.title || 'Pinterest Image'}" loading="lazy">
            <div class="image-info">
                <h3>${image.title || 'Untitled'}</h3>
                <p>${image.description || 'No description available'}</p>
                <div class="image-actions">
                    <button class="download-btn" onclick="downloadImage('${image.url}', '${filename}')">
                        <i class="fas fa-download"></i> Download
                    </button>
                    <span class="image-size">${image.width}x${image.height}</span>
                </div>
            </div>
        </div>
    `;
}

// Handle search
async function search() {
    const query = searchInput.value.trim();
    if (!query) {
        showError('Please enter a search term');
        return;
    }

    const numImages = numImagesSelect.value;
    toggleLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/search/?query=${encodeURIComponent(query)}&num=${numImages}`);
        if (!response.ok) {
            throw new Error('Search failed');
        }
        
        const data = await response.json();
        if (data.results.length === 0) {
            showError('No images found');
            return;
        }

        resultsDiv.innerHTML = data.results.map(createImageCard).join('');
    } catch (error) {
        showError('Error: ' + error.message);
    } finally {
        toggleLoading(false);
    }
}

// Handle random image
async function getRandom() {
    const query = searchInput.value.trim();
    if (!query) {
        showError('Please enter a search term');
        return;
    }

    toggleLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/random/?query=${encodeURIComponent(query)}`);
        if (!response.ok) {
            throw new Error('Failed to get random image');
        }
        
        const image = await response.json();
        resultsDiv.innerHTML = createImageCard(image);
    } catch (error) {
        showError('Error: ' + error.message);
    } finally {
        toggleLoading(false);
    }
}

// Handle enter key in search input
searchInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        search();
    }
});

// Initial focus on search input
searchInput.focus();
