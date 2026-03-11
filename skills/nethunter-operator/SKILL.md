# Kali NetHunter Operator Skill

## Description
A comprehensive skill for managing Kali NetHunter on Android via Termux, with full system permissions to install, configure, update, and operate security testing tools.

## Capabilities
- **Installation**: Full setup of Termux + Kali NetHunter environment
- **Package Management**: Install, update, remove Kali packages via apt
- **Tool Configuration**: Metasploit, nmap, sqlmap, etc.
- **System Operations**: Service management, SSH setup, persistence
- **Network Operations**: Scanning, monitoring, packet capture
- **Persistence**: Auto-start services, backup/restore
- **Cleanup**: Complete uninstall and system reset

## Usage

### Install NetHunter
```bash
/skill nethunter install
```
Options:
- `--f-droid` - Use F-Droid Termux (recommended)
- `--no-root` - Install in proot (default)
- `--full` - Install all tools and dependencies

### Start NetHunter Session
```bash
/skill nethunter start
```
- Launches the Kali environment
- Runs auto-configuration scripts
- Starts essential services (SSH, postgresql)

### Package Operations
```bash
/skill nethunter install-package nmap metasploit
/skill nethunter update-package metasploit
/skill nethunter remove-package sqlmap
```

### Service Management
```bash
/skill nethunter service start ssh
/skill nethunter service status postgresql
/skill nethunter service stop apache2
```

### Tool Configuration
```bash
/skill nethunter configure metasploit --db postgresql
/skill nethunter configure ssh --port 2222 --permit-root no
```

### System Backup/Restore
```bash
/skill nethunter backup --to /sdcard/backup/
/skill nethunter restore --from /sdcard/backup/
```

### Update NetHunter
```bash
/skill nethunter update --all
```

### Uninstall
```bash
/skill nethunter uninstall --full
```
WARNING: This removes all Kali NetHunter data and configurations.

## Permissions
This skill operates with full permissions within the Termux environment. All file operations, package installs, and system commands are executed with user-level privileges (no root required).

## Environment Requirements
- Android device (Termux app)
- Minimum 2GB storage
- Internet connection
- Optional: USB OTG for external adapters

## Notes
- All operations are logged for audit
- Services run in Termux's proot environment
- No actual Android root required
- WiFi monitor mode limited without root

## Troubleshooting
If a command fails, check Termux logs at:
`~/termux.log` or output from the skill will include error details.

## Security
- Change default Kali passwords after install
- Use SSH keys for remote access
- Keep Termux updated
- Never run unknown scripts