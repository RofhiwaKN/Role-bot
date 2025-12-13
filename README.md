# Discord Role Management Bot

A simple Discord bot built with `discord.py` that allows users with **Manage Roles** permission to add or remove roles for multiple users at once using commands.

---

## Features

- Add a role to multiple users with one command
- Remove a role from multiple users with one command
- Permission checks to ensure only authorized users can use the commands
- Handles invalid users and permission errors gracefully

---

## Commands

### `!addrole <role> <user_mentions...>`

Adds the specified role to the mentioned users.

Example:
!addrole @Member @User1 @User2

### `!removerole <role> <user_mentions...>`

Removes the specified role from the mentioned users.

Example:
!removerole @Member @User1 @User2


