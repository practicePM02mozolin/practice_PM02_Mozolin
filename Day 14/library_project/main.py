# main.py
from services.library_service import LibraryService
from repositories.in_memory import (
    InMemoryBookRepository,
    InMemoryReaderRepository,
    InMemoryLoanRepository
)


def main():
    """Пример использования библиотеки"""
    
    # Создание репозиториев
    book_repo = InMemoryBookRepository()
    reader_repo = InMemoryReaderRepository()
    loan_repo = InMemoryLoanRepository()
    
    # Создание сервиса с внедрением зависимостей
    library = LibraryService(book_repo, reader_repo, loan_repo)
    
    print("=" * 50)
    print("БИБЛИОТЕКА - ДЕМОНСТРАЦИЯ РАБОТЫ")
    print("=" * 50)
    
    # 1. Добавление книг
    print("\n1. Добавление книг:")
    book1 = library.add_book(
        title="Война и мир",
        author="Л.Н. Толстой",
        isbn="978-5-17-123456-7",
        year=1869,
        genre="Роман",
        copies=3,
        electronic_link="https://example.com/war_and_peace.pdf"
    )
    print(f"   ✓ Добавлена книга: {book1['title']} (ID: {book1['id']})")
    
    book2 = library.add_book(
        title="Преступление и наказание",
        author="Ф.М. Достоевский",
        isbn="978-5-17-123456-8",
        year=1866,
        genre="Роман",
        copies=2
    )
    print(f"   ✓ Добавлена книга: {book2['title']} (ID: {book2['id']})")
    
    # 2. Регистрация читателей
    print("\n2. Регистрация читателей:")
    reader1 = library.register_reader(
        name="Иван Петров",
        email="ivan@mail.ru",
        phone="+79111234567"
    )
    print(f"   ✓ Зарегистрирован читатель: {reader1['name']} (ID: {reader1['id']})")
    
    reader2 = library.register_reader(
        name="Мария Иванова",
        email="maria@mail.ru",
        phone="+79117654321"
    )
    print(f"   ✓ Зарегистрирован читатель: {reader2['name']} (ID: {reader2['id']})")
    
    # 3. Выдача книг
    print("\n3. Выдача книг:")
    try:
        loan1 = library.lend_book(book_id=book1['id'], reader_id=reader1['id'])
        print(f"   ✓ Книга выдана: ID выдачи {loan1['id']}")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    try:
        loan2 = library.lend_book(book_id=book2['id'], reader_id=reader1['id'])
        print(f"   ✓ Книга выдана: ID выдачи {loan2['id']}")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    # 4. Поиск книг
    print("\n4. Поиск книг по запросу 'война':")
    results = library.search_books("война")
    for book in results:
        print(f"   - {book['title']} ({book['author']})")
    
    # 5. Рекомендации
    print("\n5. Рекомендации для читателя Ивана Петрова:")
    recommendations = library.get_recommendations(reader_id=reader1['id'], limit=3)
    for book in recommendations:
        rating = book.get('rating', 0)
        print(f"   - {book['title']} (рейтинг: {rating:.1f})")
    
    # 6. Возврат книги
    print("\n6. Возврат книги:")
    try:
        returned = library.return_book(book_id=book1['id'], reader_id=reader1['id'])
        print(f"   ✓ Книга возвращена, штраф: {returned.get('fine', 0)} руб.")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    # 7. Просроченные выдачи
    print("\n7. Просроченные выдачи:")
    overdue = library.get_overdue_loans()
    if overdue:
        for loan in overdue:
            print(f"   - {loan['book_title']} (должник: {loan['reader_name']}, дней: {loan['days_overdue']})")
    else:
        print("   Нет просроченных выдач")
    
    print("\n" + "=" * 50)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 50)


if __name__ == "__main__":
    main()