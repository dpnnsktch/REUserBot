"""
REUserBot Module Importer
Handles importing modules from various sources (link, local file, Telegram, channel)
"""

import os
import re
import asyncio
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse
import aiohttp


class ModuleImporter:
    """Handles module imports from different sources"""
    
    def __init__(self):
        self.modules_path = Path(__file__).parent.parent / "modules" / "Custom"
        self.modules_path.mkdir(parents=True, exist_ok=True)
        
    async def import_from_link(self, url: str, module_name: str) -> Tuple[bool, str]:
        """
        Import module from a URL link
        Returns (success, message)
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        code = await response.text()
                        
                        # Validate it's Python code
                        if not self._is_valid_python_code(code):
                            return False, "Invalid Python code"
                        
                        # Save to file
                        file_path = self.modules_path / f"{module_name}.py"
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(code)
                        
                        # Check for dependencies in code and install them
                        await self._install_dependencies(code)
                        
                        return True, f"Module {module_name} imported successfully from {url}"
                    else:
                        return False, f"Failed to download from URL: {response.status}"
        except Exception as e:
            return False, f"Error importing from link: {str(e)}"
    
    async def import_from_local(self, file_path: str, module_name: str) -> Tuple[bool, str]:
        """
        Import module from a local file path
        Returns (success, message)
        """
        try:
            source_path = Path(file_path)
            
            if not source_path.exists():
                return False, f"File not found: {file_path}"
            
            if not source_path.suffix == '.py':
                return False, "File must be a Python file (.py)"
            
            # Read the source file
            with open(source_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Validate it's Python code
            if not self._is_valid_python_code(code):
                return False, "Invalid Python code"
            
            # Save to Custom folder
            dest_path = self.modules_path / f"{module_name}.py"
            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Check for dependencies in code and install them
            await self._install_dependencies(code)
            
            return True, f"Module {module_name} imported successfully from local file"
        except Exception as e:
            return False, f"Error importing from local file: {str(e)}"
    
    async def import_from_telegram_reply(self, message) -> Tuple[bool, str]:
        """
        Import module from a Telegram message reply (document)
        Returns (success, message)
        """
        try:
            # Check if message has a document
            if not message.document or not message.document.file_name.endswith('.py'):
                return False, "Please reply to a Python file (.py)"
            
            # Download the file
            file_name = message.document.file_name
            module_name = file_name[:-3]  # Remove .py extension
            
            file_path = await message.download(file_name=self.modules_path / file_name)
            
            # Read and validate
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            if not self._is_valid_python_code(code):
                os.remove(file_path)
                return False, "Invalid Python code"
            
            # Check for dependencies and install them
            await self._install_dependencies(code)
            
            return True, f"Module {module_name} imported successfully from Telegram"
        except Exception as e:
            return False, f"Error importing from Telegram: {str(e)}"
    
    async def import_from_channel(self, channel: str, module_name: str, client) -> Tuple[bool, str]:
        """
        Import module from a Telegram channel
        Returns (success, message)
        """
        try:
            # Get messages from channel
            messages = await client.get_chat_history(channel, limit=100)
            
            found = False
            async for message in messages:
                if message.document and message.document.file_name == f"{module_name}.py":
                    # Download the file
                    file_path = await message.download(file_name=self.modules_path / f"{module_name}.py")
                    
                    # Read and validate
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                    
                    if not self._is_valid_python_code(code):
                        os.remove(file_path)
                        return False, "Invalid Python code in channel"
                    
                    # Check for dependencies and install them
                    await self._install_dependencies(code)
                    
                    found = True
                    break
            
            if not found:
                return False, f"Module {module_name} not found in channel {channel}"
            
            return True, f"Module {module_name} imported successfully from channel {channel}"
        except Exception as e:
            return False, f"Error importing from channel: {str(e)}"
    
    def _is_valid_python_code(self, code: str) -> bool:
        """Check if code is valid Python"""
        import ast
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False
    
    async def _install_dependencies(self, code: str):
        """
        Parse code for imports and install missing dependencies
        Supports both pyrogram and telethon
        """
        import re
        import subprocess
        
        # Find all import statements
        import_patterns = [
            r'^import\s+(\w+)',
            r'^from\s+(\w+)\s+import'
        ]
        
        installed_packages = set()
        
        for pattern in import_patterns:
            matches = re.findall(pattern, code, re.MULTILINE)
            for match in matches:
                package = match.lower()
                
                # Map common import names to pip package names
                package_mapping = {
                    'telethon': 'telethon',
                    'pyrogram': 'pyrogram',
                    'aiohttp': 'aiohttp',
                    'requests': 'requests',
                }
                
                pip_package = package_mapping.get(package, package)
                
                # Skip standard library modules
                stdlib_modules = {'os', 'sys', 're', 'json', 'asyncio', 'time', 'datetime', 
                                  'pathlib', 'typing', 'logging', 'hashlib', 'base64'}
                
                if pip_package in stdlib_modules:
                    continue
                
                if pip_package not in installed_packages:
                    try:
                        # Try to import first
                        __import__(pip_package)
                    except ImportError:
                        # Install if not found
                        print(f"Installing dependency: {pip_package}")
                        subprocess.check_call(['pip', 'install', pip_package])
                        installed_packages.add(pip_package)


# Global importer instance
module_importer = ModuleImporter()

def get_module_importer() -> ModuleImporter:
    """Get the global module importer instance"""
    return module_importer
