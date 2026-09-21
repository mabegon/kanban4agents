// Configuration loader for frontend - loads from .env file via backend endpoint
let API_BASE_URL = 'http://192.168.1.181:8000';

// Load configuration from environment variables (for development)
// In production, this will be loaded from the server
async function loadFrontendConfig() {
    try {
        // Attempt to load config from backend endpoint that serves env vars
        const response = await fetch(`${API_BASE_URL}/config`);
        if (response.ok) {
            const config = await response.json();
            if (config.backend_url) {
                API_BASE_URL = config.backend_url;
            }
        }
    } catch (error) {
        // If we can't get the config from backend, keep default
        console.warn('Could not load frontend config from backend');
    }
}

// Load configuration when page loads
document.addEventListener('DOMContentLoaded', () => {
    loadFrontendConfig();
});
