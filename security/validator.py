import os
import re

class SecurityValidator:
    ALLOWED_EXTENSIONS = {'.zip', '.py', '.js', '.json', '.php', '.txt', '.env'}
    
    @classmethod
    def is_extension_allowed(cls, filename: str) -> bool:
        """Validates file extension against whitelist."""
        _, ext = os.path.splitext(filename)
        return ext.lower() in cls.ALLOWED_EXTENSIONS

    @classmethod
    def sanitize_command(cls, command: str) -> bool:
        """Command injection protection. Ensures commands only contain allowed characters."""
        pattern = re.compile(r'^[a-zA-Z0-9_\-\.\s\/]+$')
        return bool(pattern.match(command))
    
    @classmethod
    def malware_scan_placeholder(cls, file_path: str) -> bool:
        """
        Placeholder interface for malware scanning. 
        In production, integrate with ClamAV or VirusTotal API here.
        Returns True if clean, False if infected.
        """
        if not os.path.exists(file_path):
            return False
        
        # Simulated scan passing
        return True