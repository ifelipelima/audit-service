import hashlib

from app.core.security import generate_api_key, hash_api_key

def test_generate_api_key_format():
    api_key = generate_api_key()

    assert api_key.startswith("aud_")
    assert len(api_key) == 47

def test_generate_unique_api_keys():
    api_keys = {generate_api_key() for _ in range(100)}
    assert len(api_keys) == 100

def test_hash_api_key():
    api_key = generate_api_key()
    result = hash_api_key(api_key)
    assert result == hashlib.sha256(api_key.encode("utf-8")).hexdigest()
    assert len(result) == 64

def test_hash_api_key_is_deterministic():
    api_key = generate_api_key()
    assert hash_api_key(api_key) == hash_api_key(api_key)

def test_different_api_keys_have_different_hashes():
    first_api_key = generate_api_key()
    second_api_key = generate_api_key()
    assert hash_api_key(first_api_key) != hash_api_key(second_api_key)