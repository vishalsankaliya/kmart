
// Page Loader
window.addEventListener('load', function () {
    const loader = document.getElementById('page-loader');
    if (loader) {
        setTimeout(function () {
            loader.classList.add('fade-out');
        }, 500); // 0.5s delay for smooth effect
    }
});

// Example: Add to Cart functionality simulation
function addToCart(productName) {
    alert(productName + " added to cart!");
}

// Search Functionality
document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const searchSuggestions = document.getElementById('searchSuggestions');

    if (searchInput && searchSuggestions) {
        // Listen for input
        searchInput.addEventListener('input', function () {
            const query = this.value.toLowerCase().trim();
            searchSuggestions.innerHTML = '';

            if (query.length > 0 && typeof products !== 'undefined') {
                const filteredProducts = products.filter(product =>
                    product.name.toLowerCase().includes(query) ||
                    product.category.toLowerCase().includes(query)
                );

                if (filteredProducts.length > 0) {
                    searchSuggestions.classList.remove('hidden');
                    filteredProducts.forEach(product => {
                        const div = document.createElement('div');
                        div.className = 'p-3 hover:bg-gray-100 cursor-pointer flex items-center gap-3 border-b border-gray-100 last:border-0 transition duration-200';
                        div.innerHTML = `
                            <img src="${product.image}" class="w-10 h-10 object-contain rounded bg-white border border-gray-200">
                            <div>
                                <div class="text-sm font-medium text-gray-800">${product.name}</div>
                                <div class="text-xs text-gray-500">${product.category}</div>
                            </div>
                        `;
                        div.addEventListener('click', function () {
                            searchInput.value = product.name;
                            window.location.href = `search.html?query=${encodeURIComponent(product.name)}`;
                        });
                        searchSuggestions.appendChild(div);
                    });
                } else {
                    searchSuggestions.classList.remove('hidden');
                    searchSuggestions.innerHTML = '<div class="p-3 text-sm text-gray-500 italic">No results found</div>';
                }
            } else {
                searchSuggestions.classList.add('hidden');
            }
        });

        // Hide suggestions when clicking outside
        document.addEventListener('click', function (e) {
            if (!searchInput.contains(e.target) && !searchSuggestions.contains(e.target)) {
                searchSuggestions.classList.add('hidden');
            }
        });
    }

    // Search Button Click
    if (searchBtn && searchInput) {
        searchBtn.addEventListener('click', function () {
            const query = searchInput.value.trim();
            if (query) {
                window.location.href = `search.html?query=${encodeURIComponent(query)}`;
            }
        });

        // Enter key support
        searchInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                const query = searchInput.value.trim();
                // If suggestions are visible and user presses Enter, go to first suggestion or search term
                if (query) {
                    window.location.href = `search.html?query=${encodeURIComponent(query)}`;
                }
            }
        });
    }
});
