"""
REUserBot Module Manager
Handles loading, unloading, and managing userbot modules
"""

import os
import sys
import importlib.util
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
import re

from core.security import get_security_manager, SecurityManager


class ModuleManager:
    """Manages all userbot modules"""
    
    def __init__(self):
        self.modules: Dict[str, Any] = {}
        self.modules_path = Path(__file__).parent.parent / "modules"
        self.custom_path = self.modules_path / "Custom"
        self.system_path = self.modules_path  # System modules are in modules folder
        self.security_manager = get_security_manager()
        
        # Ensure directories exist
        self.custom_path.mkdir(parents=True, exist_ok=True)
        
    def load_module(self, module_name: str, module_path: Path, is_system: bool = False) -> bool:
        """
        Load a module from file
        Returns True if successful
        """
        try:
            # Security check
            if not is_system and self.security_manager.is_enabled():
                with open(module_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                if self.security_manager.check_dangerous_code(code, module_name):
                    raise SecurityError(f"Module {module_name} contains dangerous code")
            
            # Load the module
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec is None or spec.loader is None:
                return False
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            self.modules[module_name] = {
                'module': module,
                'path': module_path,
                'is_system': is_system,
                'enabled': True,
                'config': {}
            }
            
            return True
        except Exception as e:
            print(f"Error loading module {module_name}: {e}")
            return False
    
    def unload_module(self, module_name: str) -> bool:
        """Unload a module"""
        if module_name not in self.modules:
            return False
        
        try:
            del sys.modules[module_name]
            del self.modules[module_name]
            return True
        except Exception as e:
            print(f"Error unloading module {module_name}: {e}")
            return False
    
    def reload_module(self, module_name: str, debug: bool = False) -> Optional[str]:
        """
        Reload a module
        If debug is True, returns the output
        """
        if module_name not in self.modules:
            return None
        
        module_info = self.modules[module_name]
        module_path = module_info['path']
        is_system = module_info['is_system']
        
        # Unload first
        self.unload_module(module_name)
        
        # Load again
        success = self.load_module(module_name, module_path, is_system)
        
        if debug:
            if success:
                return f"Module {module_name} reloaded successfully"
            else:
                return f"Failed to reload module {module_name}"
        
        return None
    
    def get_module_list(self, show_system: bool = True) -> List[str]:
        """Get list of all modules"""
        modules = []
        for name, info in self.modules.items():
            if not show_system and info['is_system']:
                continue
            modules.append(name)
        return modules
    
    def get_module_info(self, module_name: str) -> Optional[Dict]:
        """Get information about a module"""
        if module_name not in self.modules:
            return None
        
        module_info = self.modules[module_name]
        module = module_info['module']
        
        info = {
            'name': module_name,
            'path': str(module_info['path']),
            'is_system': module_info['is_system'],
            'enabled': module_info['enabled'],
            'description': getattr(module, '__doc__', 'No description'),
            'commands': getattr(module, 'commands', []),
            'config': module_info['config']
        }
        
        return info
    
    def get_module_config(self, module_name: str) -> Optional[Dict]:
        """Get module configuration"""
        if module_name not in self.modules:
            return None
        return self.modules[module_name]['config'].copy()
    
    def set_module_config(self, module_name: str, key: str, value: Any) -> bool:
        """Set a configuration value for a module"""
        if module_name not in self.modules:
            return False
        self.modules[module_name]['config'][key] = value
        return True
    
    def get_module_permissions(self, module_name: str) -> List[str]:
        """Get permissions/requirements for a module"""
        if module_name not in self.modules:
            return []
        
        module = self.modules[module_name]['module']
        permissions = getattr(module, 'permissions', [])
        requirements = getattr(module, 'requirements', [])
        
        return permissions + requirements
    
    def edit_module_line(self, module_name: str, line_number: int, new_content: str) -> bool:
        """Edit a specific line in a module"""
        if module_name not in self.modules:
            return False
        
        module_path = self.modules[module_name]['path']
        
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if line_number < 1 or line_number > len(lines):
                return False
            
            lines[line_number - 1] = new_content + '\n'
            
            with open(module_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            return True
        except Exception as e:
            print(f"Error editing module line: {e}")
            return False
    
    def get_module_line(self, module_name: str, line_number: int) -> Optional[str]:
        """Get a specific line from a module"""
        if module_name not in self.modules:
            return None
        
        module_path = self.modules[module_name]['path']
        
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if line_number < 1 or line_number > len(lines):
                return None
            
            return lines[line_number - 1].strip()
        except Exception as e:
            print(f"Error reading module line: {e}")
            return None
    
    def get_module_errors(self, module_name: str) -> List[str]:
        """Get errors and possible fixes for a module"""
        errors = []
        
        if module_name not in self.modules:
            errors.append("Module not found")
            return errors
        
        module_path = self.modules[module_name]['path']
        
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Check for common issues
            if 'import' in code and 'telethon' in code.lower():
                try:
                    importlib.import_module('telethon')
                except ImportError:
                    errors.append("Missing dependency: telethon. Install with: pip install telethon")
            
            if 'pyrogram' in code.lower():
                try:
                    importlib.import_module('pyrogram')
                except ImportError:
                    errors.append("Missing dependency: pyrogram. Install with: pip install pyrogram")
            
            # Check syntax
            try:
                compile(code, str(module_path), 'exec')
            except SyntaxError as e:
                errors.append(f"Syntax error at line {e.lineno}: {e.msg}")
                errors.append(f"Fix: Check line {e.lineno} for syntax issues")
            
        except Exception as e:
            errors.append(f"Error reading module: {e}")
        
        return errors
    
    def install_dependency(self, package_name: str) -> bool:
        """Install a Python package dependency"""
        import subprocess
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name])
            return True
        except Exception as e:
            print(f"Error installing {package_name}: {e}")
            return False


class SecurityError(Exception):
    """Raised when security check fails"""
    pass


# Global module manager instance
module_manager = ModuleManager()

def get_module_manager() -> ModuleManager:
    """Get the global module manager instance"""
    return module_manager
