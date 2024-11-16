// Function to toggle sidebar visibility
function toggleMenu() {
    const sidebar = document.getElementById("sidebar");
    sidebar.classList.toggle("open");
}

// Функция для обработки ввода в поисковую строку
function searchBooks() {
    const query = document.getElementById('search-bar').value.trim().toLowerCase();
    const suggestionsContainer = document.getElementById('search-suggestions');

    if (query.length > 0) {
        // Отправляем запрос на сервер для получения предложений
        fetch(`/search_suggestions?query=${encodeURIComponent(query)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                suggestionsContainer.innerHTML = ''; // Очищаем предыдущие предложения

                if (data.length === 0) {
                    const noResults = document.createElement('li');
                    noResults.textContent = 'No results found';
                    suggestionsContainer.appendChild(noResults);
                } else {
                    data.forEach(book => {
                        const suggestion = document.createElement('li');
                        suggestion.textContent = book.title;
                        suggestion.onclick = () => {
                            window.location.href = `/book/${book.id}`;
                        };
                        suggestionsContainer.appendChild(suggestion);
                    });
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);
            });
    } else {
        // Если запрос пустой, очищаем контейнер с предложениями
        suggestionsContainer.innerHTML = '';
    }
}
