import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64

def generate_encryption_key():
    """
    Genera una nueva clave de encriptación utilizando Fernet.
    """
    return Fernet.generate_key().decode()

def encrypt_message(message, key, algorithm='SHA256'):
    """
    Encripta un mensaje utilizando la clave proporcionada y el algoritmo especificado.
    """
    f = Fernet(key.encode())
    return f.encrypt(message.encode()).decode()

def decrypt_message(encrypted_message, key, algorithm='SHA256'):
    """
    Desencripta un mensaje utilizando la clave proporcionada y el algoritmo especificado.
    """
    f = Fernet(key.encode())
    return f.decrypt(encrypted_message.encode()).decode()

def generate_unique_id():
    """
    Genera un identificador único para los mensajes.
    """
    return secrets.token_urlsafe(16)

def derive_key(password: str, salt: bytes, algorithm='SHA256') -> bytes:
    """
    Deriva una clave a partir de una contraseña y un salt utilizando el algoritmo especificado.
    """
    if algorithm == 'SHA256':
        hash_algorithm = hashes.SHA256()
    elif algorithm == 'SHA384':
        hash_algorithm = hashes.SHA384()
    elif algorithm == 'SHA512':
        hash_algorithm = hashes.SHA512()
    else:
        raise ValueError("Algoritmo no soportado")

    kdf = PBKDF2HMAC(
        algorithm=hash_algorithm,
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))
