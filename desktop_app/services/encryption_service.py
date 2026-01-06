"""
Encryption Service - Handles secure encryption of face data.
Uses Fernet symmetric encryption for sensitive face encodings.
"""
import os
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet

from config import ENCRYPTION_KEY_FILE, FACES_DIR, init_directories


class EncryptionService:
    """Handles encryption and decryption of sensitive data."""
    
    def __init__(self):
        """Initialize encryption service with key management."""
        init_directories()
        self.fernet = self._get_or_create_fernet()
    
    def _get_or_create_fernet(self) -> Fernet:
        """Get existing key or create new one."""
        if ENCRYPTION_KEY_FILE.exists():
            with open(ENCRYPTION_KEY_FILE, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            # Ensure parent directory exists
            ENCRYPTION_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(ENCRYPTION_KEY_FILE, 'wb') as f:
                f.write(key)
            # Set restrictive permissions
            os.chmod(ENCRYPTION_KEY_FILE, 0o600)
        
        return Fernet(key)
    
    def encrypt(self, data: bytes) -> bytes:
        """Encrypt binary data."""
        return self.fernet.encrypt(data)
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Decrypt binary data."""
        return self.fernet.decrypt(encrypted_data)
    
    def encrypt_to_file(self, data: bytes, filename: str) -> Path:
        """Encrypt data and save to file in faces directory."""
        encrypted = self.encrypt(data)
        filepath = FACES_DIR / f"{filename}.enc"
        with open(filepath, 'wb') as f:
            f.write(encrypted)
        return filepath
    
    def decrypt_from_file(self, filepath: Path) -> Optional[bytes]:
        """Read and decrypt data from file."""
        if not filepath.exists():
            return None
        with open(filepath, 'rb') as f:
            encrypted = f.read()
        return self.decrypt(encrypted)
    
    def delete_face_file(self, filepath: Path) -> bool:
        """Securely delete a face file."""
        if filepath.exists():
            filepath.unlink()
            return True
        return False


# Global encryption service instance
encryption_service = EncryptionService()
