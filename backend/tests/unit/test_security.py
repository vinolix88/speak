import pytest
from app.core.security import hash_password, verify_password, create_access_token
from jose import jwt
from app.core.config import settings
from datetime import timedelta


# ===========================================================================
# hash_password / verify_password
# ===========================================================================

def test_hash_password():
    """Базовый кейс: хэш отличается от оригинала и верифицируется"""
    password = "Test123!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("WrongPass", hashed)


def test_hash_password_is_unique():
    """Два хэша одного пароля должны быть разными (bcrypt использует соль)"""
    password = "SamePassword1!"
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    assert hash1 != hash2
    # Оба должны верифицироваться
    assert verify_password(password, hash1)
    assert verify_password(password, hash2)


def test_verify_password_wrong():
    """Неверный пароль не проходит верификацию"""
    hashed = hash_password("CorrectPassword1!")
    assert not verify_password("WrongPassword!", hashed)


def test_verify_password_empty_string():
    """Пустая строка не верифицируется против реального пароля"""
    hashed = hash_password("RealPassword1!")
    assert not verify_password("", hashed)


def test_verify_password_case_sensitive():
    """Верификация чувствительна к регистру"""
    password = "CaseSensitive1!"
    hashed = hash_password(password)
    assert not verify_password("casesensitive1!", hashed)
    assert not verify_password("CASESENSITIVE1!", hashed)


def test_hash_password_special_characters():
    """Пароль со спецсимволами хэшируется и верифицируется корректно"""
    password = "P@$$w0rd!#%^&*()"
    hashed = hash_password(password)
    assert verify_password(password, hashed)


def test_hash_password_unicode():
    """Юникодный пароль хэшируется и верифицируется корректно"""
    password = "Пароль123!"
    hashed = hash_password(password)
    assert verify_password(password, hashed)
    assert not verify_password("WrongPassword", hashed)


# ===========================================================================
# create_access_token
# ===========================================================================

def test_create_access_token():
    """Базовый кейс: токен декодируется, содержит sub, exp, type"""
    data = {"sub": "test-user-id"}
    token = create_access_token(data)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "test-user-id"
    assert "exp" in payload
    assert payload["type"] == "access"


def test_create_access_token_custom_expiry():
    """
    create_access_token не принимает expires_delta — время жизни берётся из settings.
    Тест проверяет, что exp присутствует и токен валиден.
    """
    data = {"sub": "user-42"}
    token = create_access_token(data)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "user-42"
    assert "exp" in payload
    # exp должен быть в будущем
    from datetime import datetime, timezone
    exp_dt = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    assert exp_dt > datetime.now(tz=timezone.utc)


def test_create_access_token_wrong_secret():
    """Токен не декодируется с неверным секретом"""
    from jose import JWTError
    data = {"sub": "user-1"}
    token = create_access_token(data)
    with pytest.raises(JWTError):
        jwt.decode(token, "wrong-secret", algorithms=[settings.ALGORITHM])


def test_create_access_token_different_users():
    """Токены для разных пользователей отличаются"""
    token1 = create_access_token({"sub": "user-1"})
    token2 = create_access_token({"sub": "user-2"})
    assert token1 != token2


def test_create_access_token_preserves_extra_claims():
    """Дополнительные поля в payload сохраняются в токене"""
    data = {"sub": "user-1", "role": "admin"}
    token = create_access_token(data)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload.get("role") == "admin"
