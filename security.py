from passlib.context import CryptContext
import hashlib

# Use bcrypt for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _prehash_password(password: str) -> str:
    """
    Pre-hash a password using SHA-256 to support passwords > 72 bytes.
    bcrypt will hash this hash.
    """
    # Encode the password to bytes, hash it, and return the hex digest
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a hashed password."""
    # Pre-hash the plain password *before* verifying
    prehashed_plain = _prehash_password(plain_password)
    return pwd_context.verify(prehashed_plain, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes a plain-text password."""
    # Pre-hash the password *before* storing
    prehashed_pass = _prehash_password(password)
    return pwd_context.hash(prehashed_pass)