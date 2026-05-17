"""
REUserBot - Main Entry Point
Telegram UserBot with Pyrogram and Telethon support
"""

import os
import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import core modules
from core.system import log_startup, log_info, log_error, get_system_info, VERSION, BRANCH
from core.security import get_security_manager
from core.module_manager import get_module_manager
from core.commands import get_command_handler
from config import (
    owner_id, 
    security_enabled, 
    system_module_visible,
    session_name,
    log_chat_id,
    welcome_url,
    github_releases_url
)

# Try to import pyrogram (main library)
try:
    from pyrogram import Client, filters
    from pyrogram.types import Message
    PYROGRAM_AVAILABLE = True
except ImportError:
    print("Pyrogram not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyrogram', 'tgcrypto'])
    from pyrogram import Client, filters
    from pyrogram.types import Message
    PYROGRAM_AVAILABLE = True


class REUserBot:
    """Main UserBot class"""
    
    def __init__(self):
        self.client = None
        self.security_manager = get_security_manager()
        self.module_manager = get_module_manager()
        self.command_handler = None
        self.log_chat_id = log_chat_id
        self.owner_id = owner_id
        self.is_first_run = owner_id is None
        
        # Session file path
        self.session_path = Path(__file__).parent / "sessions" / session_name
        
    async def initialize(self):
        """Initialize the userbot"""
        log_startup()
        
        # Create Pyrogram client
        self.client = Client(
            name=session_name,
            workdir=str(Path(__file__).parent),
            in_memory=False
        )
        
        # Setup security
        if security_enabled:
            self.security_manager.enable()
            log_info("Security enabled")
        else:
            self.security_manager.disable()
            log_info("Security disabled")
        
        # Initialize command handler
        self.command_handler = get_command_handler(self.client)
        
        log_info("UserBot initialized")
    
    async def start(self):
        """Start the userbot"""
        await self.initialize()
        
        # Start the client
        await self.client.start()
        
        # Get current user info on first run
        if self.is_first_run:
            me = await self.client.get_me()
            self.owner_id = me.id
            
            # Save owner_id to config
            self._save_owner_id(me.id)
            
            # Create log chat
            await self._create_log_chat()
            
            # Send welcome message
            await self._send_welcome()
        
        # Load existing modules
        await self._load_modules()
        
        # Start update checker
        asyncio.create_task(self._check_updates())
        
        log_info(f"UserBot started as @{(await self.client.get_me()).username}")
        
        # Keep running
        await self.run_forever()
    
    async def run_forever(self):
        """Keep the bot running"""
        try:
            # Idle until disconnected
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            log_info("UserBot stopped by user")
        except Exception as e:
            log_error(f"Error in main loop: {e}")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the userbot"""
        if self.client:
            await self.client.stop()
        log_info("UserBot stopped")
    
    def _save_owner_id(self, user_id: int):
        """Save owner ID to config file"""
        config_path = Path(__file__).parent / "config.py"
        
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Replace owner_id value
        import re
        content = re.sub(r'owner_id\s*=\s*.*', f'owner_id = {user_id}', content)
        
        with open(config_path, 'w') as f:
            f.write(content)
        
        log_info(f"Owner ID saved: {user_id}")
    
    async def _create_log_chat(self):
        """Create a private log chat"""
        try:
            # Create a private channel/supergroup for logs
            chat = await self.client.create_channel(
                title="REUserBot Logs",
                description="Private log chat for REUserBot errors and events"
            )
            
            self.log_chat_id = chat.id
            
            # Save to config
            self._save_log_chat_id(chat.id)
            
            # Send startup message
            await self._send_to_log(f"""REUserBot Started
Branch: {BRANCH}
Version: {VERSION}
""")
            
            log_info(f"Log chat created: {chat.id}")
        except Exception as e:
            log_error(f"Failed to create log chat: {e}")
    
    def _save_log_chat_id(self, chat_id: int):
        """Save log chat ID to config file"""
        config_path = Path(__file__).parent / "config.py"
        
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Replace log_chat_id value
        import re
        content = re.sub(r'log_chat_id\s*=\s*.*', f'log_chat_id = {chat_id}', content)
        
        with open(config_path, 'w') as f:
            f.write(content)
    
    async def _send_to_log(self, message: str):
        """Send a message to the log chat"""
        if self.log_chat_id and self.client:
            try:
                await self.client.send_message(self.log_chat_id, message)
            except Exception as e:
                log_error(f"Failed to send to log chat: {e}")
    
    async def _send_welcome(self):
        """Send welcome message to owner"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(welcome_url) as response:
                    if response.status == 200:
                        welcome_text = await response.text()
                        await self.client.send_message(
                            self.owner_id,
                            f"👋 Welcome to REUserBot!\n\n{welcome_text}\n\nClick to start using: {welcome_url}"
                        )
        except Exception as e:
            log_error(f"Failed to send welcome: {e}")
    
    async def _load_modules(self):
        """Load all existing modules"""
        modules_dir = Path(__file__).parent / "modules"
        custom_dir = modules_dir / "Custom"
        
        # Load custom modules
        if custom_dir.exists():
            for module_file in custom_dir.glob("*.py"):
                if not module_file.name.startswith('_'):
                    module_name = module_file.stem
                    self.module_manager.load_module(module_name, module_file, is_system=False)
                    log_info(f"Loaded module: {module_name}")
        
        # Load system modules (if any in modules folder)
        for module_file in modules_dir.glob("*.py"):
            if not module_file.name.startswith('_') and module_file.parent == modules_dir:
                module_name = module_file.stem
                self.module_manager.load_module(module_name, module_file, is_system=True)
                log_info(f"Loaded system module: {module_name}")
    
    async def _check_updates(self):
        """Check for updates periodically"""
        import aiohttp
        import json
        
        while True:
            try:
                await asyncio.sleep(3600)  # Check every hour
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(github_releases_url) as response:
                        if response.status == 200:
                            # Parse releases (simplified)
                            # In production, you'd parse the actual GitHub API response
                            pass
                            
            except Exception as e:
                log_error(f"Update check failed: {e}")
    
    def check_owner(self, user_id: int) -> bool:
        """Check if user is the owner"""
        return user_id == self.owner_id


# Global bot instance
bot = REUserBot()


async def main():
    """Main entry point"""
    try:
        await bot.start()
    except Exception as e:
        log_error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())
