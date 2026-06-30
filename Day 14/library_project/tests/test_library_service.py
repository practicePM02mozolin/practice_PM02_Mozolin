# tests/test_library_service.py
import pytest
from unittest.mock import Mock
from datetime import date, timedelta
from services.library_service import (
    LibraryService, 
    BookNotFoundError, 
    ReaderNotFoundError,
    NoAvailableCopiesError,
    ReaderBlockedError,
    TooManyLoansError,
    DuplicateIsbnError,
    ValidationError,
    LoanNotFoundError
)


@pytest.fixture
def mock_repos():
    """Создание моков репозиториев"""
    book_repo = Mock()
    reader_repo = Mock()
    loan_repo = Mock()
    return book_repo, reader_repo, loan_repo


@pytest.fixture
def library_service(mock_repos):
    """Создание сервиса с моками"""
    book_repo, reader_repo, loan_repo = mock_repos
    return LibraryService(book_repo, reader_repo, loan_repo)


class TestAddBook:
    """Тесты для метода add_book"""
    
    def test_add_book_success(self, library_service, mock_repos):
        """Тест успешного добавления книги"""
        book_repo, _, _ = mock_repos
        book_repo.find_by_isbn.return_value = None
        book_repo.save.return_value = {'id': 1, 'title': 'Test Book'}

        result = library_service.add_book(
            title='Test Book',
            author='Test Author',
            isbn='978-5-17-123456-7',
            year=2020,
            genre='Fiction',
            copies=5
        )

        assert result['id'] == 1
        book_repo.save.assert_called_once()
    
    def test_add_book_duplicate_isbn(self, library_service, mock_repos):
        """Тест попытки добавить книгу с дублирующимся ISBN"""
        book_repo, _, _ = mock_repos
        book_repo.find_by_isbn.return_value = {'id': 1, 'isbn': '978-5-17-123456-7'}

        with pytest.raises(DuplicateIsbnError):
            library_service.add_book(
                title='Test Book',
                author='Test Author',
                isbn='978-5-17-123456-7',
                year=2020,
                genre='Fiction',
                copies=5
            )
    
    def test_add_book_invalid_copies(self, library_service, mock_repos):
        """Тест попытки добавить книгу с отрицательным количеством экземпляров"""
        book_repo, _, _ = mock_repos
        book_repo.find_by_isbn.return_value = None

        with pytest.raises(ValidationError, match="Количество экземпляров не может быть отрицательным"):
            library_service.add_book(
                title='Test Book',
                author='Test Author',
                isbn='978-5-17-123456-7',
                year=2020,
                genre='Fiction',
                copies=-1
            )
    
    def test_add_book_empty_title(self, library_service, mock_repos):
        """Тест попытки добавить книгу с пустым названием"""
        book_repo, _, _ = mock_repos
        book_repo.find_by_isbn.return_value = None

        with pytest.raises(ValidationError, match="Название книги не может быть пустым"):
            library_service.add_book(
                title='',
                author='Test Author',
                isbn='978-5-17-123456-7',
                year=2020,
                genre='Fiction',
                copies=5
            )


class TestRegisterReader:
    """Тесты для метода register_reader"""
    
    def test_register_reader_success(self, library_service, mock_repos):
        """Тест успешной регистрации читателя"""
        _, reader_repo, _ = mock_repos
        reader_repo.find_by_email.return_value = None
        reader_repo.save.return_value = {'id': 1, 'name': 'Test Reader'}

        result = library_service.register_reader(
            name='Test Reader',
            email='test@mail.ru',
            phone='+79111234567'
        )

        assert result['id'] == 1
        reader_repo.save.assert_called_once()
    
    def test_register_reader_duplicate_email(self, library_service, mock_repos):
        """Тест попытки регистрации с дублирующимся email"""
        _, reader_repo, _ = mock_repos
        reader_repo.find_by_email.return_value = {'id': 1, 'email': 'test@mail.ru'}

        with pytest.raises(ValidationError, match="Читатель с email test@mail.ru уже зарегистрирован"):
            library_service.register_reader(
                name='Test Reader',
                email='test@mail.ru',
                phone='+79111234567'
            )
    
    def test_register_reader_invalid_email(self, library_service, mock_repos):
        """Тест попытки регистрации с некорректным email"""
        _, reader_repo, _ = mock_repos
        reader_repo.find_by_email.return_value = None

        with pytest.raises(ValidationError, match="Некорректный email"):
            library_service.register_reader(
                name='Test Reader',
                email='invalid-email',
                phone='+79111234567'
            )


class TestLendBook:
    """Тесты для метода lend_book"""
    
    def test_lend_book_success(self, library_service, mock_repos):
        """Тест успешной выдачи книги"""
        book_repo, reader_repo, loan_repo = mock_repos
        book_repo.find_by_id.return_value = {'id': 1, 'title': 'Test Book', 'copies': 3}
        reader_repo.find_by_id.return_value = {'id': 1, 'name': 'Test Reader'}
        reader_repo.is_blocked.return_value = False
        loan_repo.find_active_by_reader.return_value = []
        loan_repo.find_active_loan.return_value = None
        book_repo.decrement_copies.return_value = True
        loan_repo.save.return_value = {'id': 1, 'book_id': 1, 'reader_id': 1}

        result = library_service.lend_book(book_id=1, reader_id=1)

        assert result['id'] == 1
        book_repo.decrement_copies.assert_called_once_with(1)
        loan_repo.save.assert_called_once()
    
    def test_lend_book_not_found(self, library_service, mock_repos):
        """Тест попытки выдать несуществующую книгу"""
        book_repo, _, _ = mock_repos
        book_repo.find_by_id.return_value = None

        with pytest.raises(BookNotFoundError):
            library_service.lend_book(book_id=999, reader_id=1)
    
    def test_lend_book_reader_not_found(self, library_service, mock_repos):
        """Тест попытки выдать книгу несуществующему читателю"""
        book_repo, reader_repo, _ = mock_repos
        book_repo.find_by_id.return_value = {'id': 1, 'copies': 3}
        reader_repo.find_by_id.return_value = None

        with pytest.raises(ReaderNotFoundError):
            library_service.lend_book(book_id=1, reader_id=999)
    
    def test_lend_book_no_copies(self, library_service, mock_repos):
        """Тест попытки выдать книгу с нулевым количеством экземпляров"""
        book_repo, reader_repo, loan_repo = mock_repos
        book_repo.find_by_id.return_value = {'id': 1, 'title': 'Test Book', 'copies': 0}
        reader_repo.find_by_id.return_value = {'id': 1, 'name': 'Test Reader'}
        reader_repo.is_blocked.return_value = False
        loan_repo.find_active_by_reader.return_value = []
        loan_repo.find_active_loan.return_value = None
        book_repo.decrement_copies.return_value = False

        with pytest.raises(NoAvailableCopiesError):
            library_service.lend_book(book_id=1, reader_id=1)
    
    def test_lend_book_too_many_loans(self, library_service, mock_repos):
        """Тест попытки выдать книгу читателю, у которого уже 5 книг"""
        book_repo, reader_repo, loan_repo = mock_repos
        book_repo.find_by_id.return_value = {'id': 1, 'title': 'Test Book', 'copies': 3}
        reader_repo.find_by_id.return_value = {'id': 1, 'name': 'Test Reader'}
        reader_repo.is_blocked.return_value = False
        loan_repo.find_active_by_reader.return_value = [
            {'id': 1}, {'id': 2}, {'id': 3}, {'id': 4}, {'id': 5}
        ]
        loan_repo.find_active_loan.return_value = None

        with pytest.raises(TooManyLoansError):
            library_service.lend_book(book_id=1, reader_id=1)
    
    def test_lend_book_blocked_reader(self, library_service, mock_repos):
        """Тест попытки выдать книгу заблокированному читателю"""
        book_repo, reader_repo, _ = mock_repos
        book_repo.find_by_id.return_value = {'id': 1, 'copies': 3}
        reader_repo.find_by_id.return_value = {'id': 1, 'name': 'Test Reader'}
        reader_repo.is_blocked.return_value = True

        with pytest.raises(ReaderBlockedError):
            library_service.lend_book(book_id=1, reader_id=1)


class TestReturnBook:
    """Тесты для метода return_book"""
    
    def test_return_book_success(self, library_service, mock_repos):
        """Тест успешного возврата книги"""
        book_repo, reader_repo, loan_repo = mock_repos
        book_repo.find_by_id.return_value = {'id': 1, 'title': 'Test Book'}
        reader_repo.find_by_id.return_value = {'id': 1, 'name': 'Test Reader'}
        loan_repo.find_active_loan.return_value = {
            'id': 1,
            'book_id': 1,
            'reader_id': 1,
            'due_date': (date.today() - timedelta(days=10)).isoformat()
        }
        book_repo.increment_copies.return_value = True
        loan_repo.update.return_value = {'id': 1, 'status': 'returned', 'fine': 0.0}

        result = library_service.return_book(book_id=1, reader_id=1)

        assert result['status'] == 'returned'
        book_repo.increment_copies.assert_called_once_with(1)
    
    def test_return_book_not_found(self, library_service, mock_repos):
        """Тест попытки вернуть несуществующую книгу"""
        book_repo, _, _ = mock_repos
        book_repo.find_by_id.return_value = None

        with pytest.raises(BookNotFoundError):
            library_service.return_book(book_id=999, reader_id=1)
    
    def test_return_book_loan_not_found(self, library_service, mock_repos):
        """Тест попытки вернуть книгу, которая не была выдана"""
        book_repo, reader_repo, loan_repo = mock_repos
        book_repo.find_by_id.return_value = {'id': 1, 'title': 'Test Book'}
        reader_repo.find_by_id.return_value = {'id': 1, 'name': 'Test Reader'}
        loan_repo.find_active_loan.return_value = None

        with pytest.raises(LoanNotFoundError):
            library_service.return_book(book_id=1, reader_id=1)
    
    def test_return_book_with_fine(self, library_service, mock_repos):
        """Тест возврата книги с просрочкой и расчетом штрафа"""
        book_repo, reader_repo, loan_repo = mock_repos
        book_repo.find_by_id.return_value = {'id': 1, 'title': 'Test Book'}
        reader_repo.find_by_id.return_value = {'id': 1, 'name': 'Test Reader'}
        due_date = (date.today() - timedelta(days=20)).isoformat()
        loan_repo.find_active_loan.return_value = {
            'id': 1,
            'book_id': 1,
            'reader_id': 1,
            'due_date': due_date
        }
        book_repo.increment_copies.return_value = True
        loan_repo.update.return_value = {'id': 1, 'status': 'returned', 'fine': 60.0}

        result = library_service.return_book(book_id=1, reader_id=1)

        assert result['fine'] == 60.0


class TestSearchBooks:
    """Тесты для метода search_books"""
    
    def test_search_books_success(self, library_service, mock_repos):
        """Тест успешного поиска книг"""
        book_repo, _, _ = mock_repos
        expected_books = [
            {'id': 1, 'title': 'War and Peace', 'author': 'Tolstoy'},
            {'id': 2, 'title': 'Peace', 'author': 'Unknown'}
        ]
        book_repo.search.return_value = expected_books

        result = library_service.search_books('Peace')

        assert len(result) == 2
        book_repo.search.assert_called_once_with('Peace')
    
    def test_search_books_short_query(self, library_service, mock_repos):
        """Тест поиска с коротким запросом"""
        with pytest.raises(ValidationError, match="Поисковый запрос должен содержать минимум 2 символа"):
            library_service.search_books('a')


class TestGetRecommendations:
    """Тесты для метода get_recommendations"""
    
    def test_get_recommendations_with_history(self, library_service, mock_repos):
        """Тест получения рекомендаций на основе истории"""
        book_repo, reader_repo, loan_repo = mock_repos
        reader_repo.find_by_id.return_value = {'id': 1, 'name': 'Test Reader'}
        loan_repo.get_history_by_reader.return_value = [
            {'book_id': 1, 'reader_id': 1}
        ]
        book_repo.find_by_id.return_value = {
            'id': 1, 
            'title': 'Book 1', 
            'genre': 'Fiction', 
            'author': 'Author 1'
        }
        book_repo.search.return_value = [
            {'id': 3, 'title': 'Book 3', 'genre': 'Fiction', 'author': 'Author 1'}
        ]
        book_repo.find_all.return_value = []

        result = library_service.get_recommendations(reader_id=1, limit=1)

        assert len(result) > 0
    
    def test_get_recommendations_no_history(self, library_service, mock_repos):
        """Тест получения рекомендаций без истории"""
        book_repo, reader_repo, loan_repo = mock_repos
        reader_repo.find_by_id.return_value = {'id': 1, 'name': 'Test Reader'}
        loan_repo.get_history_by_reader.return_value = []
        book_repo.find_all.return_value = [
            {'id': 1, 'title': 'Book 1', 'rating': 4.5},
            {'id': 2, 'title': 'Book 2', 'rating': 4.0}
        ]

        result = library_service.get_recommendations(reader_id=1, limit=1)

        assert len(result) > 0
        book_repo.find_all.assert_called_once()
    
    def test_get_recommendations_reader_not_found(self, library_service, mock_repos):
        """Тест получения рекомендаций для несуществующего читателя"""
        _, reader_repo, _ = mock_repos
        reader_repo.find_by_id.return_value = None

        with pytest.raises(ReaderNotFoundError):
            library_service.get_recommendations(reader_id=999)


class TestGetOverdueLoans:
    """Тесты для метода get_overdue_loans"""
    
    def test_get_overdue_loans_success(self, library_service, mock_repos):
        """Тест получения просроченных выдач"""
        book_repo, reader_repo, loan_repo = mock_repos
        loan_repo.find_overdue.return_value = [
            {
                'id': 1, 
                'book_id': 1, 
                'reader_id': 1, 
                'due_date': (date.today() - timedelta(days=20)).isoformat()
            }
        ]
        book_repo.find_by_id.return_value = {'id': 1, 'title': 'Test Book'}
        reader_repo.find_by_id.return_value = {'id': 1, 'name': 'Test Reader'}

        result = library_service.get_overdue_loans()

        assert len(result) == 1
        assert 'book_title' in result[0]
        assert 'reader_name' in result[0]
        assert 'days_overdue' in result[0]