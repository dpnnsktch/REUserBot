"""
REUserBot Security Module
Provides protection against malicious modules and unauthorized access
"""

import os
import re
from pathlib import Path
from typing import List, Set

class SecurityManager:
    """Manages security for the userbot"""
    
    def __init__(self):
        self.enabled = True
        self.whitelist: List[str] = []
        self.blocked_modules: Set[str] = set()
        self.root_modules: Set[str] = set()  # Modules with full access
        self.sessions_path = Path(__file__).parent.parent / "sessions"
        
        # Dangerous patterns to block
        self.dangerous_patterns = [
            r'os\.remove',
            r'os\.rmdir',
            r'os\.unlink',
            r'shutil\.rmtree',
            r'__import__\s*\(\s*["\']os["\']\s*\)',
            r'subprocess\.',
            r'eval\s*\(',
            r'exec\s*\(',
        ]
        
    def enable(self):
        """Enable security"""
        self.enabled = True
        
    def disable(self):
        """Disable security (requires confirmation)"""
        self.enabled = False
        
    def is_enabled(self) -> bool:
        """Check if security is enabled"""
        return self.enabled
    
    def add_to_whitelist(self, module_name: str):
        """Add module to whitelist"""
        if module_name not in self.whitelist:
            self.whitelist.append(module_name)
    
    def remove_from_whitelist(self, module_name: str):
        """Remove module from whitelist"""
        if module_name in self.whitelist:
            self.whitelist.remove(module_name)
    
    def get_whitelist(self) -> List[str]:
        """Get whitelist of modules"""
        return self.whitelist.copy()
    
    def block_module(self, module_name: str):
        """Block a module (restrict to Custom folder only)"""
        self.blocked_modules.add(module_name)
    
    def unblock_module(self, module_name: str):
        """Unblock a module"""
        if module_name in self.blocked_modules:
            self.blocked_modules.remove(module_name)
    
    def is_blocked(self, module_name: str) -> bool:
        """Check if module is blocked"""
        return module_name in self.blocked_modules
    
    def grant_root_access(self, module_name: str):
        """Grant root access to a module (full permissions)"""
        self.root_modules.add(module_name)
    
    def revoke_root_access(self, module_name: str):
        """Revoke root access from a module"""
        if module_name in self.root_modules:
            self.root_modules.remove(module_name)
    
    def has_root_access(self, module_name: str) -> bool:
        """Check if module has root access"""
        return module_name in self.root_modules
    
    def check_dangerous_code(self, code: str, module_name: str) -> bool:
        """
        Check if code contains dangerous patterns
        Returns True if dangerous code is detected
        """
        if not self.enabled:
            return False
        
        # Root modules bypass security checks
        if self.has_root_access(module_name):
            return False
        
        # Blocked modules are heavily restricted
        if self.is_blocked(module_name):
            # Check for any system imports or file operations
            if re.search(r'import\s+(os|sys|subprocess|shutil)', code):
                return True
            if re.search(r'open\s*\(', code):
                return True
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, code):
                return True
        
        # Check for attempts to access sessions folder
        if 'sessions' in code.lower():
            return True
        
        return False
    
    def can_access_path(self, module_name: str, path: Path) -> bool:
        """
        Check if module can access a specific path
        Returns True if access is allowed
        """
        if not self.enabled:
            return True
        
        # Root modules have full access
        if self.has_root_access(module_name):
            return True
        
        # Blocked modules can only access Custom folder
        if self.is_blocked(module_name):
            custom_path = Path(__file__).parent.parent / "modules" / "Custom"
            try:
                path.relative_to(custom_path)
                return True
            except ValueError:
                return False
        
        # Sessions folder is always protected
        try:
            path.relative_to(self.sessions_path)
            return False  # No module can access sessions folder
        except ValueError:
            pass
        
        return True
    
    def generate_confirmation_key(self) -> str:
        """Generate a confirmation key for sensitive operations"""
        import random
        import string
        chars = string.ascii_lowercase + string.digits
        return ''.join(random.choice(chars) for _ in range(8))
    
    def validate_confirmation_key(self, key: str, expected_key: str) -> bool:
        """Validate a confirmation key"""
        return key == expected_key


# Global security manager instance
security_manager = SecurityManager()

def get_security_manager() -> SecurityManager:
    """Get the global security manager instance"""
    return security_manager
