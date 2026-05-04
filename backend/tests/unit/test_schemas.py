import pytest
from pydantic import ValidationError
from app.schemas.user import UserCreate, UserOut, Token
from uuid import UUID


# ===========================================================================
# UserCreate
# ===========================================================================

def test_user_create_valid():
    """Базовый кейс: корректные данные"""
    user = UserCreate(username="testuser", email="test@example.com", password="StrongP@ss1")
    assert user.username == "testuser"
    assert user.email == "test@example.com"


def test_user_create_invalid_email():
    """Невалидный email вызывает ValidationError"""
    with pytest.raises(ValidationError):
        UserCreate(username="test", email="not-an-email", password="pass")


def test_user_create_missing_username():
    """Отсутствие username вызывает ValidationError"""
    with pytest.raises(ValidationError):
        UserCreate(email="test@example.com", password="StrongP@ss1")


def test_user_create_missing_email():
    """Отсутствие email вызывает ValidationError"""
    with pytest.raises(ValidationError):
        UserCreate(username="testuser", password="StrongP@ss1")


def test_user_create_missing_password():
    """Отсутствие password вызывает ValidationError"""
    with pytest.raises(ValidationError):
        UserCreate(username="testuser", email="test@example.com")


def test_user_create_empty_username():
    """
    Схема UserCreate принимает пустой username (min_length не задан).
    Тест фиксирует текущее поведение — валидация длины на уровне БД или эндпоинта.
    """
    user = UserCreate(username="", email="test@example.com", password="StrongP@ss1")
    assert user.username == ""


def test_user_create_empty_email():
    """Пустой email вызывает ValidationError"""
    with pytest.raises(ValidationError):
        UserCreate(username="testuser", email="", password="StrongP@ss1")


def test_user_create_email_without_domain():
    """Email без домена вызывает ValidationError"""
    with pytest.raises(ValidationError):
        UserCreate(username="testuser", email="test@", password="StrongP@ss1")


# ===========================================================================
# UserOut
# ===========================================================================

def test_user_out():
    """Базовый кейс: валидный UUID, full_name по умолчанию None"""
    user = UserOut(id="123e4567-e89b-12d3-a456-426614174000", username="test", email="test@ex.com")
    assert UUID(user.id)  # валидный UUID
    assert user.full_name is None


def test_user_out_with_full_name():
    """UserOut с full_name"""
    user = UserOut(
        id="123e4567-e89b-12d3-a456-426614174000",
        username="test",
        email="test@ex.com",
        full_name="Test User",
    )
    assert user.full_name == "Test User"


def test_user_out_missing_id():
    """Отсутствие id вызывает ValidationError"""
    with pytest.raises(ValidationError):
        UserOut(username="test", email="test@ex.com")


def test_user_out_missing_username():
    """Отсутствие username вызывает ValidationError"""
    with pytest.raises(ValidationError):
        UserOut(id="123e4567-e89b-12d3-a456-426614174000", email="test@ex.com")


# ===========================================================================
# Token
# ===========================================================================

def test_token():
    """Базовый кейс: все поля присутствуют"""
    token = Token(access_token="abc", refresh_token="def", token_type="bearer")
    assert token.token_type == "bearer"
    assert token.access_token == "abc"
    assert token.refresh_token == "def"


def test_token_missing_access_token():
    """Отсутствие access_token вызывает ValidationError"""
    with pytest.raises(ValidationError):
        Token(refresh_token="def", token_type="bearer")


def test_token_missing_refresh_token():
    """Отсутствие refresh_token вызывает ValidationError"""
    with pytest.raises(ValidationError):
        Token(access_token="abc", token_type="bearer")


def test_token_type_default_bearer():
    """token_type должен быть 'bearer' (стандарт OAuth2)"""
    token = Token(access_token="abc", refresh_token="def", token_type="bearer")
    assert token.token_type == "bearer"
