from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from gyver.crypto import RSACryptoProvider, RSACryptoConfig


def test_rsa_oaep_crypto_provider():
    # Generate a private/public key pair
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048
    )
    public_key = private_key.public_key()

    # Serialize the private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # Serialize the public key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    # Create a config object with the keys
    config = RSACryptoConfig(
        private_key=private_pem.decode(), public_key=public_pem.decode()
    )

    # Create the provider
    provider = RSACryptoProvider(config=config)

    # Test encryption
    plaintext = "Test plaintext"
    ciphertext = provider.encrypt(plaintext)
    assert plaintext != ciphertext

    # Test decryption
    decrypted_plaintext = provider.decrypt(ciphertext)
    assert plaintext == decrypted_plaintext
