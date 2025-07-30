import os
import shutil
import pytest
import numpy as np

from .interface import (
    generate_keys, encrypt, decrypt,
    operate_add, operate_multi,
    DEFAULT_KEY_DIR, DEFAULT_CIPHER_DIR
)

@pytest.fixture(scope="function")
def clean_test_dirs():
    if os.path.exists(DEFAULT_KEY_DIR):
        shutil.rmtree(DEFAULT_KEY_DIR)
    if os.path.exists(DEFAULT_CIPHER_DIR):
        shutil.rmtree(DEFAULT_CIPHER_DIR)
    os.makedirs(DEFAULT_KEY_DIR, exist_ok=True)
    os.makedirs(DEFAULT_CIPHER_DIR, exist_ok=True)
    yield
    shutil.rmtree(DEFAULT_KEY_DIR)
    shutil.rmtree(DEFAULT_CIPHER_DIR)

def test_encrypt_decrypt(clean_test_dirs):
    N, p, lam, omega, delta, psi = 2, 67, 2, 1, 1, 1
    message = 42
    sk_name, k_name, evk_name = "sk", "kvec", "evk"
    cipher_name = "cipher"

    assert generate_keys(N, p, lam, omega, delta, sk_name, k_name, evk_name) == True

    ciphertext = encrypt(message, cipher_name, N, p, lam, psi, sk_name, k_name)
    assert isinstance(ciphertext, list)
    assert all(isinstance(mat, np.ndarray) for mat in ciphertext)

    decrypted_message = decrypt(cipher_name, sk_name, k_name, p)
    assert decrypted_message == message


def test_add(clean_test_dirs):
    N, p, lam, omega, delta, psi = 2, 67, 2, 1, 1, 1
    m1, m2 = 10, 20
    sk, kvec, evk = "sk", "kvec", "evk"
    c1_name, c2_name = "c1", "c2"
    csum_name = "csum"

    generate_keys(N, p, lam, omega, delta, sk, kvec, evk)
    encrypt(m1, c1_name, N, p, lam, psi, sk, kvec)
    encrypt(m2, c2_name, N, p, lam, psi, sk, kvec)

    operate_add(c1_name, c2_name, p, csum_name)
    decrypted_sum = decrypt(csum_name, sk, kvec, p)

    expected_sum = (m1 + m2) % p
    assert decrypted_sum == expected_sum


def test_multi(clean_test_dirs):
    N, p, lam, omega, delta, psi = 2, 67, 2, 1, 1, 1
    m1, m2 = 3, 4
    sk, kvec, evk = "sk", "kvec", "evk"
    c1_name, c2_name = "c1", "c2"
    cmul_name = "cmul"

    generate_keys(N, p, lam, omega, delta, sk, kvec, evk)
    encrypt(m1, c1_name, N, p, lam, psi, sk, kvec)
    encrypt(m2, c2_name, N, p, lam, psi, sk, kvec)

    operate_multi(c1_name, c2_name, p, evk, cmul_name)
    decrypted_product = decrypt(cmul_name, sk, kvec, p)

    expected_product = (m1 * m2) % p
    assert decrypted_product == expected_product
