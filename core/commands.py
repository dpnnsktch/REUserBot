"""
REUserBot Command Handler
Handles all userbot commands (.module, .security, .reboot, etc.)
"""

import os
import sys
import asyncio
import re
from pathlib import Path
from typing import Optional, Dict, Any

from pyrogram import Client, filters
from pyrogram.types import Message

from core.security import get_security_manager
from core.module_manager import get_module_manager
from core.module_importer import get_module_importer
from core.system import log_info, log_error, VERSION, BRANCH


class CommandHandler:
    """Handles all userbot commands"""
    
    def __init__(self, client: Client):
        self.client = client
        self.security_manager = get_security_manager()
        self.module_manager = get_module_manager()
        self.module_importer = get_module_importer()
        
        # Pending confirmations (for sensitive operations)
        self.pending_confirmations: Dict[str, str] = {}  # key -> expected_value
        
        self.register_commands()
    
    def register_commands(self):
        """Register all command handlers"""
        
        # ===== MODULE COMMANDS =====
        
        @self.client.on_message(filters.command("module", prefixes=".") & filters.me)
        async def module_command(client: Client, message: Message):
            await self.handle_module_command(message)
        
        # ===== SECURITY COMMANDS =====
        
        @self.client.on_message(filters.command("security", prefixes=".") & filters.me)
        async def security_command(client: Client, message: Message):
            await self.handle_security_command(message)
        
        # ===== SYSTEM COMMANDS =====
        
        @self.client.on_message(filters.command("reboot", prefixes=".") & filters.me)
        async def reboot_command(client: Client, message: Message):
            await message.edit("🔄 Restarting userbot...")
            os.execv(sys.executable, [sys.executable] + sys.argv)
        
        @self.client.on_message(filters.command("off", prefixes=".") & filters.me)
        async def off_command(client: Client, message: Message):
            await message.edit("⏹️ Userbot stopped")
            sys.exit(0)
        
        @self.client.on_message(filters.command("welcome", prefixes=".") & filters.me)
        async def welcome_command(client: Client, message: Message):
            await self.handle_welcome_command(message)
        
        @self.client.on_message(filters.command("update", prefixes=".") & filters.me)
        async def update_command(client: Client, message: Message):
            await self.handle_update_command(message)
        
        # ===== CONFIRMATION HANDLER =====
        
        @self.client.on_message(filters.regex(r'^[a-z0-9]{8}$') & filters.me)
        async def confirmation_handler(client: Client, message: Message):
            await self.handle_confirmation(message)
    
    async def handle_module_command(self, message: Message):
        """Handle .module command and its subcommands"""
        args = message.text.split()
        
        if len(args) < 2:
            await message.edit("❌ Usage: .module <subcommand> [args]\n\nSubcommands:\n• import {link|local|tg|channel} [args]\n• list\n• del <name>\n• perm <name>\n• config <name> <key> <value>\n• info <name>\n• root <name>\n• block <name>\n• error <name>\n• line <name> {replace|show} [line] [new_content]\n• restart <name> [debug]")
            return
        
        subcommand = args[1].lower()
        
        try:
            if subcommand == "import":
                await self.module_import(message, args[2:])
            elif subcommand == "list":
                await self.module_list(message)
            elif subcommand == "del":
                await self.module_delete(message, args[2:])
            elif subcommand == "perm":
                await self.module_permissions(message, args[2:])
            elif subcommand == "config":
                await self.module_config(message, args[2:])
            elif subcommand == "info":
                await self.module_info(message, args[2:])
            elif subcommand == "root":
                await self.module_root(message, args[2:])
            elif subcommand == "block":
                await self.module_block(message, args[2:])
            elif subcommand == "error":
                await self.module_error(message, args[2:])
            elif subcommand == "line":
                await self.module_line(message, args[2:])
            elif subcommand == "restart":
                await self.module_restart(message, args[2:])
            else:
                await message.edit(f"❌ Unknown subcommand: {subcommand}")
        except Exception as e:
            log_error(f"Module command error: {e}")
            await message.edit(f"❌ Error: {str(e)}")
    
    async def module_import(self, message: Message, args):
        """Handle .module import command"""
        if len(args) < 1:
            await message.edit("❌ Usage: .module import {link|local|tg|channel} [args]")
            return
        
        import_type = args[0].lower()
        
        if import_type == "link":
            if len(args) < 3:
                await message.edit("❌ Usage: .module import link <url> <module_name>")
                return
            url = args[1]
            module_name = args[2]
            success, msg = await self.module_importer.import_from_link(url, module_name)
            
        elif import_type == "local":
            if len(args) < 3:
                await message.edit("❌ Usage: .module import local <file_path> <module_name>")
                return
            file_path = args[1]
            module_name = args[2]
            success, msg = await self.module_importer.import_from_local(file_path, module_name)
            
        elif import_type == "tg":
            if not message.reply_to_message:
                await message.edit("❌ Reply to a .py file to import it")
                return
            success, msg = await self.module_importer.import_from_telegram_reply(message.reply_to_message)
            
        elif import_type == "channel":
            if len(args) < 2:
                await message.edit("❌ Usage: .module import channel <module_name>\nChannel: @pitupiarbitrash")
                return
            module_name = args[1]
            channel = "@pitupiarbitrash"
            success, msg = await self.module_importer.import_from_channel(channel, module_name, self.client)
            
        else:
            await message.edit(f"❌ Unknown import type: {import_type}")
            return
        
        if success:
            # Load the module
            module_path = Path(__file__).parent.parent / "modules" / "Custom" / f"{module_name}.py"
            if self.module_manager.load_module(module_name, module_path, is_system=False):
                msg += "\n✅ Module loaded successfully"
            else:
                msg += "\n⚠️ Module saved but failed to load"
        
        await message.edit(msg)
    
    async def module_list(self, message: Message):
        """Handle .module list command"""
        from config import system_module_visible
        
        modules = self.module_manager.get_module_list(show_system=system_module_visible)
        
        if not modules:
            await message.edit("📭 No modules found")
            return
        
        module_list = "\n".join(f"• {m}" for m in sorted(modules))
        await message.edit(f"📦 Installed Modules:\n\n{module_list}")
    
    async def module_delete(self, message: Message, args):
        """Handle .module del command"""
        if len(args) < 1:
            await message.edit("❌ Usage: .module del <module_name>")
            return
        
        module_name = args[0]
        
        if module_name not in self.module_manager.modules:
            await message.edit(f"❌ Module {module_name} not found")
            return
        
        # Unload module
        self.module_manager.unload_module(module_name)
        
        # Delete file
        module_path = Path(__file__).parent.parent / "modules" / "Custom" / f"{module_name}.py"
        if module_path.exists():
            os.remove(module_path)
        
        await message.edit(f"✅ Module {module_name} deleted")
    
    async def module_permissions(self, message: Message, args):
        """Handle .module perm command"""
        if len(args) < 1:
            await message.edit("❌ Usage: .module perm <module_name>")
            return
        
        module_name = args[0]
        permissions = self.module_manager.get_module_permissions(module_name)
        
        if not permissions:
            await message.edit(f"ℹ️ Module {module_name} has no special permissions/requirements")
        else:
            perm_list = "\n".join(f"• {p}" for p in permissions)
            await message.edit(f"🔐 Permissions for {module_name}:\n\n{perm_list}")
    
    async def module_config(self, message: Message, args):
        """Handle .module config command"""
        if len(args) < 3:
            await message.edit("❌ Usage: .module config <module_name> <key> <value>")
            return
        
        module_name = args[0]
        key = args[1]
        value = ' '.join(args[2:])
        
        if self.module_manager.set_module_config(module_name, key, value):
            await message.edit(f"✅ Config updated: {module_name}.{key} = {value}")
        else:
            await message.edit(f"❌ Failed to set config for {module_name}")
    
    async def module_info(self, message: Message, args):
        """Handle .module info command"""
        if len(args) < 1:
            await message.edit("❌ Usage: .module info <module_name>")
            return
        
        module_name = args[0]
        info = self.module_manager.get_module_info(module_name)
        
        if not info:
            await message.edit(f"❌ Module {module_name} not found")
            return
        
        info_text = f"""📋 Module Info: {info['name']}

Path: {info['path']}
System: {'Yes' if info['is_system'] else 'No'}
Enabled: {'Yes' if info['enabled'] else 'No'}
Description: {info['description']}
Commands: {', '.join(info['commands']) if info['commands'] else 'None'}
"""
        await message.edit(info_text)
    
    async def module_root(self, message: Message, args):
        """Handle .module root command - grants full access to module"""
        if len(args) < 1:
            await message.edit("❌ Usage: .module root <module_name>")
            return
        
        module_name = args[0]
        
        if module_name not in self.module_manager.modules:
            await message.edit(f"❌ Module {module_name} not found")
            return
        
        # Generate confirmation key
        confirmation_key = self.security_manager.generate_confirmation_key()
        self.pending_confirmations[f"root:{module_name}"] = confirmation_key
        
        await message.edit(f"""⚠️ WARNING: Granting ROOT access to {module_name}

This will give the module FULL system access and disable all security checks for it.

To confirm, send the following code:
`{confirmation_key}`

Or cancel by sending: cancel""")
    
    async def module_block(self, message: Message, args):
        """Handle .module block command - restricts module to Custom folder"""
        if len(args) < 1:
            await message.edit("❌ Usage: .module block <module_name>")
            return
        
        module_name = args[0]
        
        if module_name not in self.module_manager.modules:
            await message.edit(f"❌ Module {module_name} not found")
            return
        
        self.security_manager.block_module(module_name)
        await message.edit(f"🔒 Module {module_name} is now BLOCKED (restricted to Custom folder only)")
    
    async def module_error(self, message: Message, args):
        """Handle .module error command - shows errors and fixes"""
        if len(args) < 1:
            await message.edit("❌ Usage: .module error <module_name>")
            return
        
        module_name = args[0]
        errors = self.module_manager.get_module_errors(module_name)
        
        if not errors:
            await message.edit(f"✅ No errors detected in {module_name}")
        else:
            error_text = "\n\n".join(errors)
            await message.edit(f"⚠️ Errors in {module_name}:\n\n{error_text}")
    
    async def module_line(self, message: Message, args):
        """Handle .module line command - edit/show specific lines"""
        if len(args) < 3:
            await message.edit("❌ Usage: .module line <module_name> {replace|show} <line_number> [new_content]")
            return
        
        module_name = args[0]
        action = args[1].lower()
        
        try:
            line_number = int(args[2])
        except ValueError:
            await message.edit("❌ Line number must be an integer")
            return
        
        if action == "show":
            line = self.module_manager.get_module_line(module_name, line_number)
            if line:
                await message.edit(f"📄 Line {line_number} in {module_name}:\n\n`{line}`")
            else:
                await message.edit(f"❌ Could not read line {line_number} from {module_name}")
        
        elif action == "replace":
            if len(args) < 4:
                await message.edit("❌ Usage: .module line <name> replace <line> <new_content>")
                return
            
            new_content = ' '.join(args[3:])
            
            if self.module_manager.edit_module_line(module_name, line_number, new_content):
                # Reload the module
                self.module_manager.reload_module(module_name)
                await message.edit(f"✅ Line {line_number} in {module_name} updated and module reloaded")
            else:
                await message.edit(f"❌ Failed to update line {line_number}")
        
        else:
            await message.edit(f"❌ Unknown action: {action}. Use 'show' or 'replace'")
    
    async def module_restart(self, message: Message, args):
        """Handle .module restart command"""
        if len(args) < 1:
            await message.edit("❌ Usage: .module restart <module_name> [debug]")
            return
        
        module_name = args[0]
        debug = len(args) > 1 and args[1].lower() == "debug"
        
        result = self.module_manager.reload_module(module_name, debug=debug)
        
        if result:
            await message.edit(result)
        else:
            if module_name in self.module_manager.modules:
                await message.edit(f"✅ Module {module_name} restarted")
            else:
                await message.edit(f"❌ Module {module_name} not found")
    
    async def handle_security_command(self, message: Message):
        """Handle .security command and its subcommands"""
        args = message.text.split()
        
        if len(args) < 2:
            await message.edit("❌ Usage: .security <subcommand>\n\nSubcommands:\n• whitelist - Show whitelisted modules\n• on/off - Enable/disable security")
            return
        
        subcommand = args[1].lower()
        
        if subcommand == "whitelist":
            whitelist = self.security_manager.get_whitelist()
            if not whitelist:
                await message.edit("📭 No modules in whitelist")
            else:
                wl_text = "\n".join(f"• {m}" for m in whitelist)
                await message.edit(f"✅ Whitelisted Modules:\n\n{wl_text}\n\nSource: https://t.me/pitupiarbitrash/2")
        
        elif subcommand == "on":
            self.security_manager.enable()
            await message.edit("✅ Security ENABLED")
        
        elif subcommand == "off":
            # Require confirmation
            confirmation_key = self.security_manager.generate_confirmation_key()
            self.pending_confirmations["security_off"] = confirmation_key
            
            await message.edit(f"""⚠️ WARNING: Disabling security

This will allow modules to perform dangerous operations.

To confirm, send: `{confirmation_key}`""")
        
        else:
            await message.edit(f"❌ Unknown subcommand: {subcommand}")
    
    async def handle_confirmation(self, message: Message):
        """Handle confirmation codes for sensitive operations"""
        code = message.text.strip().lower()
        
        # Check for security off confirmation
        if "security_off" in self.pending_confirmations:
            if code == self.pending_confirmations["security_off"]:
                self.security_manager.disable()
                del self.pending_confirmations["security_off"]
                await message.edit("⚠️ Security DISABLED")
                return
            elif code == "cancel":
                del self.pending_confirmations["security_off"]
                await message.edit("❌ Operation cancelled")
                return
        
        # Check for root access confirmations
        for key, expected_code in list(self.pending_confirmations.items()):
            if key.startswith("root:"):
                module_name = key.split(":")[1]
                if code == expected_code:
                    self.security_manager.grant_root_access(module_name)
                    del self.pending_confirmations[key]
                    await message.edit(f"✅ ROOT access granted to {module_name}")
                    return
                elif code == "cancel":
                    del self.pending_confirmations[key]
                    await message.edit(f"❌ Root access request for {module_name} cancelled")
                    return
    
    async def handle_welcome_command(self, message: Message):
        """Handle .welcome command"""
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://raw.githubusercontent.com/dpnnsktch/REUserBot/refs/heads/main/welcome.txt") as response:
                    if response.status == 200:
                        welcome_text = await response.text()
                        await message.edit(f"👋 Welcome!\n\n{welcome_text}")
                    else:
                        await message.edit("👋 Welcome! Click to start using: https://raw.githubusercontent.com/dpnnsktch/REUserBot/refs/heads/main/welcome.txt")
        except Exception as e:
            await message.edit(f"👋 Welcome! Error loading welcome message: {e}")
    
    async def handle_update_command(self, message: Message):
        """Handle .update command - manual update trigger"""
        await message.edit("🔄 Checking for updates...")
        # Update logic would be implemented in the main bot loop
        await message.edit("✅ Update check complete. See logs for details.")


def get_command_handler(client: Client) -> CommandHandler:
    """Get command handler instance"""
    return CommandHandler(client)
