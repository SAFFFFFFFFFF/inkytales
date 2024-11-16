from app import db, Book  # Импортируем из вашего основного приложения

# Подключение к базе данных и проверка содержимого таблицы
def check_books():
    books = Book.query.all()  # Получаем все книги
    for book in books:
        print(f"ID: {book.id}, Title: {book.title}, Category: {book.category}")

if __name__ == "__main__":
    check_books()
