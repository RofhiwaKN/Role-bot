import discord
from discord.ext import commands
from discord.utils import get
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Bot Setup
TOKEN = os.environ['DISCORD_BOT_TOKEN']

intents = discord.Intents.default()
intents.members = True  # Enable member intents
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
@bot.command()
@commands.has_permissions(manage_roles=True)  # Only users with 'Manage Roles' permission can use
async def addrole(ctx, role: discord.Role, *user_mentions: str):
    """Adds a role to multiple users"""
    if not role:
        await ctx.send("Please specify a valid role.")
        return
    success_count = 0
    invalid_users = []
    for user_mention in user_mentions:
        # Try to find the user by their mention
        user = get(ctx.guild.members, mention=user_mention)
        if not user:
            invalid_users.append(user_mention)
            continue
        if role in user.roles:
            await ctx.send(f"{user.mention} already has the role {role.name}.")
        else:
            try:
                await user.add_roles(role)
                success_count += 1
            except discord.Forbidden:
                await ctx.send(f"❌ I don't have permission to add roles to {user.mention}.")
            except discord.HTTPException:
                await ctx.send(f"⚠️ Failed to assign role to {user.mention} due to an error.")
    if invalid_users:
        await ctx.send(f"❌ Invalid users: {', '.join(invalid_users)}")
    await ctx.send(f"✅ Successfully added {role.name} to {success_count} users.")
@bot.command()
@commands.has_permissions(manage_roles=True)  # Only users with 'Manage Roles' permission can use
async def removerole(ctx, role: discord.Role, *user_mentions: str):
    """Removes a role from multiple users"""
    if not role:
        await ctx.send("Please specify a valid role.")
        return
    success_count = 0
    invalid_users = []
    for user_mention in user_mentions:
        # Try to find the user by their mention
        user = get(ctx.guild.members, mention=user_mention)
        if not user:
            invalid_users.append(user_mention)
            continue
        if role not in user.roles:
            await ctx.send(f"{user.mention} doesn't have the role {role.name}.")
        else:
            try:
                await user.remove_roles(role)
                success_count += 1
            except discord.Forbidden:
                await ctx.send(f"❌ I don't have permission to remove roles from {user.mention}.")
            except discord.HTTPException:
                await ctx.send(f"⚠️ Failed to remove role from {user.mention} due to an error.")
    if invalid_users:
        await ctx.send(f"❌ Invalid users: {', '.join(invalid_users)}")
    await ctx.send(f"✅ Successfully removed {role.name} from {success_count} users.")
# Run the bot
bot.run(TOKEN)

