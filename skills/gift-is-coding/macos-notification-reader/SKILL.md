# macOS Notification Reader

Reads the macOS notification center database and exports recent notifications to markdown files. Useful for reviewing missed notifications, logging daily activity, or debugging notification issues.

## Features

- 📱 **Multi-app support**: WeChat, Teams, Outlook, Mail, iMessage, Calendar, Reminders, and more
- ⏰ **Time filtering**: Fetch notifications from the last N minutes or hours
- 📅 **Date-organized output**: Exports to `memory/YYYY-MM-DD/computer_io/notification/` 
- 🤖 **Cron scheduling**: Designed for automated periodic exports
- 🔒 **Privacy-friendly**: Reads from local database only, no cloud upload

## Quick Start

### 1. Grant Full Disk Access (Required)

This skill requires Full Disk Access to read the macOS notification database.

```bash
# Verify permission
python3 -c "import os; print('OK' if os.access(os.path.expanduser('~/Library/Group Containers/group.com.apple.usernoted/db2/db'), os.R_OK) else 'FAIL')"
```

If it returns `FAIL`, follow these steps:

1. Open **System Settings** → **Privacy & Security** → **Full Disk Access**
2. Click the 🔒 lock and enter your password
3. Click **+**, press `Cmd+Shift+G`, enter `/usr/bin/python3`, click **Open**
4. Ensure the toggle is **ON**

> **Note**: If using a virtual environment, add the Python binary from that venv instead.

### 2. Test the Script

```bash
# Navigate to the skill directory
cd /path/to/macos-notification-reader

# Read notifications from the last 35 minutes
python3 scripts/read_notifications.py --minutes 35

# Read notifications from the last 24 hours
python3 scripts/read_notifications.py --hours 24

# Limit the number of results
python3 scripts/read_notifications.py --hours 1 --limit 50
```

### 3. Set Up Cron Job (Recommended)

To automatically export notifications every 30 minutes, add a cron job:

```bash
# Edit crontab
crontab -e

# Add this line (adjust paths as needed):
*/30 * * * * /path/to/macos-notification-reader/scripts/export-notification.sh
```

Or use OpenClaw's built-in cron (if available):

```bash
openclaw cron add --schedule "*/30 * * *" --command "bash /path/to/macos-notification-reader/scripts/export-notification.sh"
```

## Output Format

The script exports to markdown table format:

```markdown
# macOS Notifications Export
- Date: 2026-03-05
- Timestamp: 20260305-112000
- Total: 15 items

## Notifications

| Time | App | Content |
|------|-----|---------|
| 2026-03-05 11:15:32 | WeChat | Contact Name: Hello message |
| 2026-03-05 10:30:00 | Teams | Meeting reminder: Weekly Standup |
```

## Configuration

### Output Directory

By default, exports go to:
```
~/.openclaw/workspace/memory/YYYY-MM-DD/computer_io/notification/
```

To customize, edit `export-notification.sh` and change the `OUTPUT_DIR` variable.

### Supported Apps

The script recognizes these apps by default:

| Bundle ID | Display Name |
|-----------|--------------|
| com.tencent.xinWeChat | WeChat |
| com.microsoft.teams2 | Teams |
| com.microsoft.Outlook | Outlook |
| com.apple.mail | Mail |
| com.apple.mobilesms | iMessage |
| com.apple.ical | Calendar |
| com.apple.reminders | Reminders |

To add more apps, edit the `simplify_app_name()` function in `read_notifications.py`.

## Limitations

- ⚠️ **macOS only**: This skill only works on macOS
- ⚠️ **Full Disk Access required**: Must be granted manually (see above)
- ⚠️ **Limited retention**: macOS automatically deletes notifications after ~3-7 days. This skill can only access notifications that still exist in the database
- ⚠️ **Notification state**: Cannot read notifications that have been explicitly dismissed by the user

## File Structure

```
macos-notification-reader/
├── SKILL.md                  # This file
├── _meta.json                # Skill metadata
├── scripts/
│   ├── read_notifications.py # Core script (file output)
│   └── export-notification.sh # Wrapper for cron usage
└── references/
    └── permission-setup.md   # Detailed permission guide
```

## Use Cases

- 📊 **Review missed notifications**: Quickly see what you missed while away
- 🔍 **Debug notification issues**: Check if a specific app sent a notification
- 📝 **Daily logging**: Automatically archive notifications for later review
- 🤖 **Automation**: Integrate with other tools via the markdown output

## Troubleshooting

### "Permission denied" error

You haven't granted Full Disk Access. See [references/permission-setup.md](references/permission-setup.md).

### "Cannot find notification database"

- Make sure you're on macOS 15.0 or later
- Check if the database path exists:
  ```bash
  ls -la ~/Library/Group\ Containers/group.com.apple.usernoted/db2/
  ```

### Notifications are empty

- macOS may have already deleted old notifications
- Try reducing the time window (e.g., `--minutes 10` instead of `--hours 24`)

---

**Author**: OpenClaw Community  
**Version**: 1.0.0  
**Platform**: macOS 15.0+  
**License**: MIT
