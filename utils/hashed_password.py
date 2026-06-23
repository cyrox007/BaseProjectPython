from typing import Optional

import bcrypt

from core.logger import setup_logger

logger = setup_logger(__name__)

# Константы
MAX_PASSWORD_LENGTH = 72  # Ограничение bcrypt
MIN_PASSWORD_LENGTH = 8
BCRYPT_ROUNDS = 12

def hash_password(password: str) -> Optional[str]:
    if not password:
        return None
    
    # Ограничение длины (bcrypt игнорирует символы после 72)
    password = password[:MAX_PASSWORD_LENGTH]

    try:
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    except Exception as e:
        logger.error(f"hash_password: {e}")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    
    # Ограничение длины для консистентности
    plain_password = plain_password[:MAX_PASSWORD_LENGTH]

    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        logger.error(f"verify_password: {e}")
        return False