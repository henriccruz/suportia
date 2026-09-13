"""Testes para o módulo de autenticação."""
import pytest
from app.auth import hash_password, verify_password, create_access_token
import jwt


def test_hash_password():
    password = "test_password"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)


def test_verify_password_wrong():
    password = "correct_password"
    hashed = hash_password(password)
    assert not verify_password("wrong_password", hashed)


def test_create_access_token():
    username = "testuser"
    token = create_access_token(username)
    assert token is not None
    assert isinstance(token, str)
    # Decodificar sem verificar (apenas checar se é JWT válido)
    decoded = jwt.decode(token, options={"verify_signature": False})
    assert decoded["sub"] == username
