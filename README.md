# Discord User Management & Channel Creator Bot

A comprehensive Discord bot built with `discord.py` that streamlines user registration, validation, role management, and automated channel creation for Discord servers.

---

## Overview

This bot helps server administrators manage Discord username collection through Google Forms, validate user submissions, send mass DMs for registration reminders, and create organized channels with specific user permissions. It bridges the gap between external forms and Discord server management.

---

## Key Features

### User Registration System
- Automatic welcome DMs with registration instructions for new members
- User-friendly commands for members to retrieve their Discord username
- Clear guidance on username vs display name differences
- Integration with Google Forms for data collection

### Username Validation
- Single and bulk username validation against server members
- Form submission verification (email + username)
- Search functionality to find users by partial name matches
- Export all server usernames to CSV for external processing

### Mass Communication
- Send registration reminders to recent joiners (customizable time period)
- DM all server members with registration information
- Progress tracking and detailed success/failure reports
- Built-in rate limiting to prevent Discord API blocks

### Role Management
- Add roles to multiple users simultaneously
- Remove roles from multiple users at once
- Permission checks and error handling
- Success tracking and invalid user reporting

### Automated Channel Creation
- Interactive wizard-style channel creation process
- Create multiple channels in specified categories
- Automatic username validation before channel creation
- Set channel permissions for specific users
- Detailed reporting on successful and failed user additions

---

## Commands

### User Commands (Available to Everyone)

**`!getmyusername`**
Retrieves your Discord username with instructions on how to use it for registration forms. Sent via DM for privacy.

**`!getmyid`**
Quick alias for `!getmyusername`.

**`!help`**
Displays all available commands based on your permission level.

---

### Admin Commands (Require Manage Guild Permission)

#### Validation Commands

**`!validateuser <username>`**
Checks if a specific Discord username exists in the server.
```
Example: !validateuser john_doe
```

**`!bulkvalidate <username1> <username2> ...`**
Validates multiple usernames at once (maximum 20).
```
Example: !bulkvalidate alice bob charlie
```

**`!checkform <email> <username>`**
Validates a complete form submission with both email and username.
```
Example: !checkform student@university.edu alice
```

**`!finduser <search_term>`**
Searches for users by username or display name (minimum 2 characters).
```
Example: !finduser john
```

**`!exportusers`**
Exports all server member usernames to a CSV file for use with spreadsheets.

#### Communication Commands

**`!recentjoins [days]`**
Shows members who joined within the specified number of days (default: 7).
```
Example: !recentjoins 14
```

**`!dmverify [days]`**
Sends registration reminder DMs to members who joined recently (default: 7 days).
```
Example: !dmverify 30
```

**`!dmall`**
Sends registration reminders to ALL server members. Use with caution - requires confirmation.

---

### Role Management Commands (Require Manage Roles Permission)

**`!addrole <role> <@user1> <@user2> ...`**
Adds the specified role to multiple mentioned users.
```
Example: !addrole @Member @User1 @User2 @User3
```

**`!removerole <role> <@user1> <@user2> ...`**
Removes the specified role from multiple mentioned users.
```
Example: !removerole @Student @User1 @User2
```

---

### Channel Management Commands (Require Manage Channels Permission)

**`!createchannels`**
Starts an interactive channel creation wizard that guides you through:
1. Selecting or creating a category
2. Specifying number of channels to create
3. For each channel:
   - Setting the channel name
   - Providing usernames to add (space-separated)
   - Validating usernames
   - Creating the channel with proper permissions
4. Reporting results with successful and failed additions

```
Example workflow:
!createchannels
> Category name: Study Groups
> Number of channels: 2
> Channel 1 name: group-alpha
> Usernames: alice bob charlie
> Channel 2 name: group-beta
> Usernames: david emma frank
```

---

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Discord bot token
- Discord server with appropriate permissions

### Installation

1. Clone or download the bot code

2. Install required dependencies:
```bash
pip install discord.py python-dotenv
```

3. Create a `.env` file in the project directory:
```
DISCORD_BOT_TOKEN=your_bot_token_here
```

4. Update the Google Forms URL in the code (search for `FORM_LINK` variable)

5. Run the bot:
```bash
python bot.py
```

### Required Bot Permissions

For full functionality, the bot needs these Discord permissions:
- Read Messages/View Channels
- Send Messages
- Embed Links
- Attach Files
- Manage Roles
- Manage Channels
- Manage Messages (to delete command messages)
- Read Message History

Alternatively, you can grant the **Administrator** permission for simplicity.

### Important: Role Hierarchy

Ensure the bot's role is positioned above the roles of users it needs to manage. Discord role hierarchy determines what the bot can control.

---

## Workflow Examples

### New Member Registration Workflow

1. New member joins server
2. Bot automatically sends welcome DM with username and registration form link
3. Member fills out Google Form with their exact username
4. Admin uses `!validateuser` or `!bulkvalidate` to verify submissions
5. Admin adds validated users to appropriate channels/roles

### Bulk Channel Creation Workflow

1. Admin runs `!createchannels`
2. Specifies category (e.g., "Study Groups")
3. Specifies number of channels (e.g., 5)
4. For each channel, provides name and list of usernames
5. Bot validates all usernames
6. Bot creates channels and adds valid users
7. Bot reports which users couldn't be added for manual review

### Registration Reminder Workflow

1. Admin checks recent joiners with `!recentjoins 7`
2. Admin sends reminders with `!dmverify 7`
3. Bot DMs all members who joined in last 7 days
4. Progress tracking shows success/failure rates
5. Members receive their username and form link

---

## Configuration

### Customizable Settings

**Registration Form URL**: Update the `FORM_LINK` variable to point to your Google Form

**DM Rate Limiting**: Adjust `DELAY_BETWEEN_DMS` to control sending speed (default: 1.5 seconds)

**Command Prefix**: Change the bot prefix by modifying `command_prefix="!"` in the bot initialization

**Welcome Message**: Customize the embed in the `on_member_join` event handler

---

## Error Handling

The bot includes comprehensive error handling for:
- Users with DMs disabled
- Missing permissions
- Invalid usernames
- Network timeouts
- Discord API rate limits
- Invalid command arguments

All errors are reported with helpful messages explaining the issue and potential solutions.

---

## Best Practices

1. **Username Collection**: Always instruct users to use `!getmyusername` before filling forms
2. **Validation**: Validate usernames before adding to channels to avoid errors
3. **Bulk Operations**: Use `!bulkvalidate` for large form responses
4. **Rate Limits**: Be mindful of Discord's rate limits when using `!dmall`
5. **Permissions**: Regularly audit bot permissions and role hierarchy
6. **Backup**: Export user lists regularly with `!exportusers`

---

## Troubleshooting

**"Missing Access" Error**
- Ensure bot has Manage Channels and Manage Roles permissions
- Check that bot's role is above target users' roles in hierarchy

**Users Not Found**
- Verify user submitted username, not display name
- Check if user has actually joined the Discord server
- Look for typos in submission

**DMs Failing**
- Some users have DMs disabled - this is expected
- Bot will report how many DMs succeeded vs failed

**Channel Creation Fails**
- Verify bot has Manage Channels permission in the category
- Ensure category exists or bot can create categories

---

## Support

For issues or questions:
- Check the `!help` command for command syntax
- Review error messages for specific guidance
- Verify bot permissions and role hierarchy
- Contact server administrators: @rofhiwa_ or @auto team

---

## License

This bot is provided as-is for educational and community management purposes.
