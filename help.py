"""
REUserBot Help Module
Complete guide for using the userbot from A to Z
"""

HELP_TEXT = """
# 📚 REUserBot Complete Guide

## 🚀 Getting Started

### First Launch
On first launch, the userbot will:
1. Detect and save your user ID (only you can control the bot)
2. Create a private Log chat for error logs
3. Send startup information to the log chat
4. Display a welcome message

### Configuration
Edit `config.py` to customize:
- `owner_id`: Your Telegram user ID (auto-set on first run)
- `security_enabled`: Enable/disable security features
- `system_module_visible`: Show/hide system modules in .module list
- `commands_to_cli`: Allow commands from console
- `session_name`: Session file name

---

## 📦 Module Commands

### `.module import {type} [args]`
Import modules from various sources.

**Types:**
- `link <url> <module_name>` - Import from URL
- `local <file_path> <module_name>` - Import from local file
- `tg` - Reply to a .py file to import it
- `channel <module_name>` - Import from @pitupiarbitrash channel

**Examples:**
```
.module import link https://example.com/module.py mymodule
.module import local /home/user/mymodule.py mymodule
.module import tg (reply to a .py file)
.module import channel coolmodule
```

### `.module list`
Show all installed modules.
- System modules shown only if `system_module_visible = True` in config

### `.module del <module_name>`
Delete a module completely.

### `.module perm <module_name>`
Show permissions/requirements needed by a module.

### `.module config <module_name> <key> <value>`
Change a module's configuration value.

**Example:**
```
.module config weather api_key ABC123
```

### `.module info <module_name>`
Show detailed information about a module:
- Path
- System/Custom status
- Enabled status
- Description
- Available commands

### `.module root <module_name>`
⚠️ **DANGEROUS** - Grant full system access to a module.
- Requires confirmation with an 8-character code
- Disables all security checks for that module
- Use with extreme caution!

### `.module block <module_name>`
Restrict a module to Custom folder only.
- Cannot access system folders
- Cannot use dangerous functions
- Maximum security restriction

### `.module error <module_name>`
Show errors in a module and possible fixes:
- Missing dependencies
- Syntax errors
- Common issues

### `.module line <module_name> {show|replace} <line_number> [new_content]`
Edit module code without leaving Telegram.

**Examples:**
```
.module line mymodule show 10
.module line mymodule replace 10 new_code_here
```

### `.module restart <module_name> [debug]`
Restart/reload a module.
- Add `debug` flag to see reload output

---

## 🔒 Security Commands

### `.security`
Show security command help.

### `.security whitelist`
Show whitelisted modules (monitors https://t.me/pitupiarbitrash/2).

### `.security on`
Enable security features.

### `.security off`
⚠️ Disable security features.
- Requires confirmation with an 8-character code
- Allows modules to perform dangerous operations

**Security Features:**
- Blocks dangerous code patterns (os.remove, eval, exec, etc.)
- Protects sessions folder from module access
- Validates module code before loading
- Supports whitelist and blacklist

---

## ⚙️ System Commands

### `.reboot`
Restart the entire userbot.

### `.off`
Stop the userbot completely.

### `.welcome`
Show welcome message from:
https://raw.githubusercontent.com/dpnnsktch/REUserBot/refs/heads/main/welcome.txt

### `.update`
Check for updates manually.
- Monitors: https://github.com/dpnnsktch/REUserBot/releases
- Auto-downloads new versions
- Prompts to restart with `.reboot` after update

---

## 🛡️ Security System

The security module protects against:
- Malicious code execution
- Unauthorized file deletion (os.remove, shutil.rmtree)
- Sessions folder access
- Dangerous functions (eval, exec, subprocess)
- System command execution

**Security Levels:**
1. **Normal** - Standard protection
2. **Blocked** - Module restricted to Custom folder
3. **Root** - Full access (requires confirmation)

---

## 📁 Project Structure

```
REUserBot/
├── modules/           # All modules
│   └── Custom/        # User modules
├── core/              # Core functionality
│   ├── system.py      # System utilities
│   ├── security.py    # Security manager
│   ├── module_manager.py  # Module management
│   ├── module_importer.py # Module importing
│   └── commands.py    # Command handlers
├── logs/              # Log files
├── sessions/          # Session files (protected)
├── config.py          # Configuration
├── main.py            # Main entry point
└── help.py            # This help file
```

---

## 🔧 Module Development

### Basic Module Template

```
# My Custom Module
# Description of what it does

from pyrogram import Client, filters

# Module metadata
__doc__ = "My custom module"
commands = ["mycmd"]
permissions = []
requirements = []

@Client.on_message(filters.command("mycmd", prefixes=".") & filters.me)
async def my_command(client, message):
    await message.edit("Hello from my module!")
```

### Module Best Practices
1. Always include `__doc__`, `commands`, `permissions`, `requirements`
2. Use Pyrogram for Telegram interactions
3. Avoid dangerous operations unless you have root access
4. Test modules before deploying
5. Document your code

---

## 🆘 Troubleshooting

### Module won't load
- Check `.module error <name>` for issues
- Install missing dependencies
- Verify Python syntax

### Commands not working
- Ensure you're the owner (check config.py)
- Check if security is blocking the module
- Try `.module restart <name> debug`

### Security blocking legitimate code
- Use `.module root <name>` for trusted modules
- Add to whitelist if appropriate
- Contact module developer

---

## 📞 Support

- GitHub: https://github.com/dpnnsktch/REUserBot
- Channel: @pitupiarbitrash
- Whitelist Source: https://t.me/pitupiarbitrash/2

---

**Version:** 1.0.0
**Branch:** Official
"""


def get_help_text() -> str:
    """Get the complete help text"""
    return HELP_TEXT


def get_command_help(command: str) -> str:
    """Get help for a specific command"""
    # Simple command lookup (can be expanded)
    command_help = {
        "module": "Manage modules: import, list, delete, configure, etc.",
        "security": "Manage security settings: whitelist, enable/disable",
        "reboot": "Restart the userbot",
        "off": "Stop the userbot",
        "welcome": "Show welcome message",
        "update": "Check for and install updates",
    }
    
    return command_help.get(command, f"No help available for command: {command}")
