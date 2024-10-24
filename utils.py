import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def generate_encryption_key():
    """
    Genera una nueva clave de encriptación utilizando Fernet.
    """
    return Fernet.generate_key().decode()

def encrypt_message(data, key, algorithm='SHA256'):
    """
    Encripta datos (texto o binarios) utilizando la clave proporcionada y el algoritmo especificado.
    """
    try:
        f = Fernet(key.encode())
        # Si los datos son una cadena, convertirlos a bytes
        if isinstance(data, str):
            data = data.encode()
        
        logger.debug(f"Encrypting data of type: {type(data)}")
        encrypted_data = f.encrypt(data)
        logger.debug(f"Data encrypted successfully, size: {len(encrypted_data)} bytes")
        return encrypted_data
    except Exception as e:
        logger.error(f"Error during encryption: {str(e)}")
        raise

def decrypt_message(encrypted_data, key, algorithm='SHA256', is_file=False):
    """
    Desencripta datos (texto o binarios) utilizando la clave proporcionada y el algoritmo especificado.
    
    Args:
        encrypted_data: Datos encriptados (bytes o str)
        key: Clave de encriptación
        algorithm: Algoritmo de encriptación
        is_file: True si los datos son un archivo binario
    
    Returns:
        bytes si is_file es True, str en caso contrario
    """
    try:
        f = Fernet(key.encode())
        
        # Asegurar que encrypted_data sea bytes
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()
        
        logger.debug(f"Decrypting data of type: {type(encrypted_data)}, size: {len(encrypted_data)} bytes")
        decrypted_data = f.decrypt(encrypted_data)
        logger.debug(f"Data decrypted successfully, size: {len(decrypted_data)} bytes")
        
        # Para archivos, devolver bytes directamente
        if is_file:
            return decrypted_data
        
        # Para mensajes de texto, intentar decodificar
        try:
            return decrypted_data.decode()
        except UnicodeDecodeError:
            logger.warning("Could not decode data as text, returning raw bytes")
            return decrypted_data
    except Exception as e:
        logger.error(f"Error during decryption: {str(e)}")
        raise

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
