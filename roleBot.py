import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Button
import re
import os
import csv
import asyncio
import json
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.environ['DISCORD_BOT_TOKEN']

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.dm_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Store pending and completed verifications
pending_verifications = {}
completed_verifications = {}

# Load verifications from file
def load_verifications():
    global completed_verifications
    try:
        with open('verifications.json', 'r') as f:
            content = f.read().strip()
            completed_verifications = json.loads(content) if content else {}
    except FileNotFoundError:
        completed_verifications = {}
    except json.JSONDecodeError:
        print("Warning: verifications.json is corrupted. Starting fresh.")
        completed_verifications = {}

def save_verifications():
    with open('verifications.json', 'w') as f:
        json.dump(completed_verifications, f, indent=2)


# ── Verification Form Modal ───────────────────────────────────────────────────

class VerificationForm(Modal, title="Member Verification"):
    name = TextInput(
        label="Full Name",
        placeholder="Enter your full name...",
        required=True,
        min_length=2,
        max_length=100
    )

    email = TextInput(
        label="Email Address",
        placeholder="example@email.com",
        required=True,
        min_length=5,
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', self.email.value):
            await interaction.response.send_message(
                "❌ Invalid email format. Please try again.",
                ephemeral=True
            )
            return

        user_id = str(interaction.user.id)
        completed_verifications[user_id] = {
            'name': self.name.value,
            'email': self.email.value,
            'username': interaction.user.name,
            'discord_id': interaction.user.id,
            'verified_at': datetime.now(timezone.utc).isoformat()
        }
        save_verifications()

        start_here_channel = discord.utils.get(interaction.guild.channels, name="start-here")

        success_embed = discord.Embed(
            title="✅ Verification Complete",
            description="Your information has been submitted successfully!",
            color=discord.Color.green()
        )
        success_embed.add_field(name="Name", value=self.name.value, inline=True)
        success_embed.add_field(name="Email", value=self.email.value, inline=True)
        success_embed.add_field(name="Username", value=interaction.user.name, inline=True)

        if start_here_channel:
            success_embed.add_field(
                name="📍 Next Step",
                value=f"Head over to {start_here_channel.mention} to get started!",
                inline=False
            )
        else:
            success_embed.add_field(
                name="📍 Next Step",
                value="Check out the #start-here channel to get started!",
                inline=False
            )

        success_embed.set_footer(text="Welcome to the community!")
        await interaction.response.send_message(embed=success_embed, ephemeral=True)
        print(f"Verification: {self.name.value} - {interaction.user.name} ({self.email.value})")


# ── Message Sender Modal ──────────────────────────────────────────────────────

class MessageSenderForm(Modal, title="Send Message"):
    channel_id = TextInput(
        label="Channel ID",
        placeholder="123456789012345678",
        required=True,
        min_length=17,
        max_length=20
    )

    message = TextInput(
        label="Message",
        placeholder="Type your message here...",
        required=True,
        max_length=2000,
        style=discord.TextStyle.paragraph
    )

    async def on_submit(self, interaction: discord.Interaction):
        if not self.channel_id.value.strip().isdigit():
            await interaction.response.send_message(
                "❌ Invalid Channel ID. Must be numbers only.",
                ephemeral=True
            )
            return

        channel = interaction.guild.get_channel(int(self.channel_id.value.strip()))

        if not channel:
            await interaction.response.send_message(
                f"❌ Channel not found for ID: `{self.channel_id.value.strip()}`\n"
                "Make sure the ID is correct and the bot has access to that channel.",
                ephemeral=True
            )
            return

        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message(
                "❌ That channel is not a text channel.",
                ephemeral=True
            )
            return

        try:
            await channel.send(self.message.value)

            confirm_embed = discord.Embed(
                title="✅ Message Sent",
                color=discord.Color.green()
            )
            confirm_embed.add_field(name="Channel", value=channel.mention, inline=True)
            confirm_embed.add_field(name="Sent By", value=interaction.user.mention, inline=True)
            confirm_embed.add_field(name="Message", value=self.message.value, inline=False)

            await interaction.response.send_message(embed=confirm_embed, ephemeral=True)

        except discord.Forbidden:
            await interaction.response.send_message(
                f"❌ I don't have permission to send messages in {channel.mention}.",
                ephemeral=True
            )
        except discord.HTTPException as e:
            await interaction.response.send_message(
                f"❌ Failed to send message: {e}",
                ephemeral=True
            )


# ── Verify Button & View ──────────────────────────────────────────────────────

class VerifyButton(Button):
    def __init__(self):
        super().__init__(
            label="Click to Verify",
            style=discord.ButtonStyle.green,
            emoji="✅",
            custom_id="verify_button_persistent"
        )

    async def callback(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)

        if user_id in completed_verifications:
            existing = completed_verifications[user_id]
            embed = discord.Embed(
                title="Already Verified",
                description="You've already completed verification.",
                color=discord.Color.blue()
            )
            embed.add_field(name="Name", value=existing['name'], inline=True)
            embed.add_field(name="Email", value=existing['email'], inline=True)
            embed.set_footer(text="Contact an admin to update your info")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.send_modal(VerificationForm())


class VerifyView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(VerifyButton())


# ── Channel Creation Modal ────────────────────────────────────────────────────

class ChannelCreationForm(Modal, title="Create Channel"):
    channel_name = TextInput(
        label="Channel Name",
        placeholder="my-new-channel",
        required=True,
        max_length=100
    )

    category_name = TextInput(
        label="Category Name",
        placeholder="Leave empty for no category",
        required=False,
        max_length=100
    )

    usernames = TextInput(
        label="Usernames to Add (space-separated)",
        placeholder="user1 user2 user3 or leave empty",
        required=False,
        style=discord.TextStyle.paragraph,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        clean_name = self.channel_name.value.strip().lower().replace(" ", "-")

        category = None
        if self.category_name.value:
            category = discord.utils.get(interaction.guild.categories, name=self.category_name.value)
            if not category:
                try:
                    category = await interaction.guild.create_category(self.category_name.value)
                except discord.Forbidden:
                    await interaction.followup.send("❌ No permission to create categories.", ephemeral=True)
                    return

        valid_members = []
        invalid_usernames = []

        if self.usernames.value:
            usernames_list = self.usernames.value.strip().split()
            for username in usernames_list:
                username_clean = username.strip().lower()
                member = discord.utils.get(interaction.guild.members, name=username_clean)
                if member and not member.bot:
                    valid_members.append(member)
                else:
                    invalid_usernames.append(username)

        try:
            new_channel = await interaction.guild.create_text_channel(
                name=clean_name,
                category=category
            )

            await new_channel.set_permissions(interaction.guild.default_role, read_messages=False)

            added_count = 0
            for member in valid_members:
                try:
                    await new_channel.set_permissions(member, read_messages=True, send_messages=True)
                    added_count += 1
                except Exception as e:
                    print(f"Error adding {member.name}: {e}")

            result_embed = discord.Embed(
                title=f"Channel Created: #{clean_name}",
                color=discord.Color.green()
            )
            result_embed.add_field(name="Channel", value=new_channel.mention, inline=False)
            result_embed.add_field(name="Category", value=category.name if category else "None", inline=True)
            result_embed.add_field(name="Users Added", value=str(added_count), inline=True)

            if invalid_usernames:
                result_embed.add_field(
                    name="Invalid Usernames",
                    value=", ".join(invalid_usernames),
                    inline=False
                )

            await interaction.followup.send(embed=result_embed, ephemeral=True)

        except discord.Forbidden:
            await interaction.followup.send("❌ Missing permissions to create channels.", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)


# ── Update Discord ID Modal ───────────────────────────────────────────────────

class UpdateDiscordIDForm(Modal, title="Update Discord ID"):
    old_id = TextInput(
        label="Old Discord ID",
        placeholder="123456789012345678",
        required=True,
        max_length=20
    )

    new_id = TextInput(
        label="New Discord ID",
        placeholder="987654321098765432",
        required=True,
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):
        old_id_str = self.old_id.value.strip()
        new_id_str = self.new_id.value.strip()

        if old_id_str not in completed_verifications:
            await interaction.response.send_message(
                f"❌ No verification found for Discord ID: {old_id_str}",
                ephemeral=True
            )
            return

        old_data = completed_verifications[old_id_str]

        completed_verifications[new_id_str] = old_data.copy()
        completed_verifications[new_id_str]['discord_id'] = int(new_id_str)
        completed_verifications[new_id_str]['updated_at'] = datetime.now(timezone.utc).isoformat()

        del completed_verifications[old_id_str]
        save_verifications()

        success_embed = discord.Embed(title="Discord ID Updated", color=discord.Color.green())
        success_embed.add_field(name="Old ID", value=old_id_str, inline=True)
        success_embed.add_field(name="New ID", value=new_id_str, inline=True)
        success_embed.add_field(name="Name", value=old_data['name'], inline=False)

        await interaction.response.send_message(embed=success_embed, ephemeral=True)


# ── Events ────────────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    load_verifications()
    bot.add_view(VerifyView())
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"Error syncing commands: {e}")


@bot.event
async def on_member_join(member):
    VERIFICATION_CHANNEL_ID = 1458986052097151157
    verification_channel = member.guild.get_channel(VERIFICATION_CHANNEL_ID)

    if verification_channel:
        try:
            welcome_embed = discord.Embed(
                title="👋 Welcome!",
                description=f"Hello {member.mention}, welcome to {member.guild.name}!",
                color=discord.Color.brand_green()
            )
            welcome_embed.add_field(
                name="🔐 Get Verified to Access All Channels",
                value=(
                    "Click the button below to complete your verification.\n"
                    "You'll get access once your courses start!"
                ),
                inline=False
            )
            welcome_embed.add_field(
                name="📝 After Verification",
                value="Once verified, head to the **#start-here** channel to get oriented!",
                inline=False
            )
            welcome_embed.set_thumbnail(url=member.display_avatar.url)
            welcome_embed.set_footer(text="Click the green button below to start verification")

            await verification_channel.send(
                content=f"{member.mention}",
                embed=welcome_embed,
                view=VerifyView()
            )

        except discord.Forbidden:
            print("Cannot send message to verification channel")
        except Exception as e:
            print(f"Error sending welcome message: {e}")
    else:
        print("Verification channel not found. Please set the correct channel ID.")


# ── Slash Commands ────────────────────────────────────────────────────────────

@bot.tree.command(name="verify", description="Complete your verification (form only visible to you)")
async def verify(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id in completed_verifications:
        existing = completed_verifications[user_id]
        embed = discord.Embed(
            title="Already Verified",
            description="You've already completed verification.",
            color=discord.Color.blue()
        )
        embed.add_field(name="Name", value=existing['name'], inline=True)
        embed.add_field(name="Email", value=existing['email'], inline=True)
        embed.set_footer(text="Contact an admin to update your info")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    await interaction.response.send_modal(VerificationForm())


@bot.tree.command(name="myinfo", description="View your verification info")
async def myinfo(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id not in completed_verifications:
        await interaction.response.send_message(
            "❌ You haven't verified yet. Use **/verify** to get started.",
            ephemeral=True
        )
        return
    data = completed_verifications[user_id]
    embed = discord.Embed(title="Your Verification Info", color=discord.Color.blue())
    embed.add_field(name="Name", value=data['name'], inline=True)
    embed.add_field(name="Email", value=data['email'], inline=True)
    embed.add_field(name="Username", value=interaction.user.name, inline=True)
    embed.add_field(name="Discord ID", value=str(interaction.user.id), inline=True)
    embed.add_field(name="Verified", value=data['verified_at'][:10], inline=True)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="checkverification", description="Check if a user is verified (Admin only)")
@app_commands.checks.has_permissions(manage_guild=True)
async def checkverification(interaction: discord.Interaction, username: str):
    username_clean = username.strip().lower()
    found = None
    for user_id, data in completed_verifications.items():
        if data['username'].lower() == username_clean:
            found = (user_id, data)
            break

    if found:
        user_id, data = found
        member = interaction.guild.get_member(int(user_id))
        embed = discord.Embed(title="Verification Found", color=discord.Color.green())
        embed.add_field(name="Name", value=data['name'], inline=True)
        embed.add_field(name="Username", value=data['username'], inline=True)
        embed.add_field(name="Email", value=data['email'], inline=True)
        embed.add_field(name="Discord ID", value=user_id, inline=False)
        embed.add_field(name="Verified", value=data['verified_at'][:10], inline=True)
        embed.add_field(name="Status", value="In Server" if member else "Left Server", inline=True)
        if member:
            embed.set_thumbnail(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message(
            f"❌ No verification found for: {username}",
            ephemeral=True
        )


@bot.tree.command(name="listverifications", description="View all verified users (Admin only)")
@app_commands.checks.has_permissions(manage_guild=True)
async def listverifications(interaction: discord.Interaction):
    if not completed_verifications:
        await interaction.response.send_message("No verifications found.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    verified_list = []
    for user_id, data in list(completed_verifications.items())[:25]:
        member = interaction.guild.get_member(int(user_id))
        status = "Active" if member else "Left"
        verified_list.append(f"{status} - {data['name']} ({data['username']})")

    embed = discord.Embed(
        title="Verified Members",
        description="\n".join(verified_list),
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Total: {len(completed_verifications)} | Showing first 25")
    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(name="exportverifications", description="Export all verifications to CSV (Admin only)")
@app_commands.checks.has_permissions(manage_guild=True)
async def exportverifications(interaction: discord.Interaction):
    if not completed_verifications:
        await interaction.response.send_message("No verifications to export.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"verifications_{timestamp}.csv"

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Discord ID', 'Name', 'Username', 'Email', 'Verified At', 'In Server'])
        for user_id, data in completed_verifications.items():
            member = interaction.guild.get_member(int(user_id))
            writer.writerow([
                user_id,
                data['name'],
                data['username'],
                data['email'],
                data['verified_at'],
                'Yes' if member else 'No'
            ])

    await interaction.followup.send(
        f"Exported {len(completed_verifications)} verifications",
        file=discord.File(filename),
        ephemeral=True
    )
    os.remove(filename)


@bot.tree.command(name="syncusernames", description="Sync usernames in verification records (Admin only)")
@app_commands.checks.has_permissions(manage_guild=True)
async def syncusernames(interaction: discord.Interaction):
    if not completed_verifications:
        await interaction.response.send_message("No verifications to sync.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    updated = []
    unchanged = 0
    left_server = []

    for user_id, data in completed_verifications.items():
        member = interaction.guild.get_member(int(user_id))
        if not member:
            left_server.append(data['username'])
            continue
        old_username = data['username']
        current_username = member.name
        if old_username != current_username:
            completed_verifications[user_id]['username'] = current_username
            updated.append(f"{old_username} → {current_username}")
        else:
            unchanged += 1

    if updated:
        save_verifications()

    embed = discord.Embed(title="Username Sync Complete", color=discord.Color.green())
    embed.add_field(name="Updated", value=str(len(updated)), inline=True)
    embed.add_field(name="Unchanged", value=str(unchanged), inline=True)
    embed.add_field(name="Left Server", value=str(len(left_server)), inline=True)

    if updated:
        embed.add_field(
            name="Changes",
            value="\n".join(updated[:10]) + (f"\n...and {len(updated)-10} more" if len(updated) > 10 else ""),
            inline=False
        )

    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(name="createchannel", description="Create a new channel with users (Admin only)")
@app_commands.checks.has_permissions(manage_channels=True)
async def createchannel(interaction: discord.Interaction):
    await interaction.response.send_modal(ChannelCreationForm())


@bot.tree.command(name="updatediscordid", description="Update a Discord ID in verifications (Admin only)")
@app_commands.checks.has_permissions(manage_guild=True)
async def updatediscordid(interaction: discord.Interaction):
    await interaction.response.send_modal(UpdateDiscordIDForm())


@bot.tree.command(name="sendmessage", description="Send a message to a channel (Admin only)")
@app_commands.checks.has_permissions(manage_guild=True)
async def sendmessage(interaction: discord.Interaction):
    await interaction.response.send_modal(MessageSenderForm())


# ── Prefix Commands ───────────────────────────────────────────────────────────

@bot.command()
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, role: discord.Role, *user_mentions: str):
    if not role:
        await ctx.send("Please specify a valid role.")
        return
    success_count = 0
    invalid_users = []
    for user_mention in user_mentions:
        member = discord.utils.get(ctx.guild.members, mention=user_mention)
        if not member:
            invalid_users.append(user_mention)
            continue
        if role in member.roles:
            await ctx.send(f"{member.mention} already has the role {role.name}.")
        else:
            try:
                await member.add_roles(role)
                success_count += 1
            except discord.Forbidden:
                await ctx.send(f"I don't have permission to add roles to {member.mention}.")
            except discord.HTTPException:
                await ctx.send(f"Failed to assign role to {member.mention} due to an error.")
    if invalid_users:
        await ctx.send(f"Invalid users: {', '.join(invalid_users)}")
    embed = discord.Embed(title="Role Assignment Complete", color=discord.Color.green())
    embed.add_field(name="Role", value=role.name, inline=True)
    embed.add_field(name="Users Added", value=str(success_count), inline=True)
    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, role: discord.Role, *user_mentions: str):
    if not role:
        await ctx.send("Please specify a valid role.")
        return
    success_count = 0
    invalid_users = []
    for user_mention in user_mentions:
        member = discord.utils.get(ctx.guild.members, mention=user_mention)
        if not member:
            invalid_users.append(user_mention)
            continue
        if role not in member.roles:
            await ctx.send(f"{member.mention} doesn't have the role {role.name}.")
        else:
            try:
                await member.remove_roles(role)
                success_count += 1
            except discord.Forbidden:
                await ctx.send(f"I don't have permission to remove roles from {member.mention}.")
            except discord.HTTPException:
                await ctx.send(f"Failed to remove role from {member.mention} due to an error.")
    if invalid_users:
        await ctx.send(f"Invalid users: {', '.join(invalid_users)}")
    embed = discord.Embed(title="Role Removal Complete", color=discord.Color.green())
    embed.add_field(name="Role", value=role.name, inline=True)
    embed.add_field(name="Users Removed", value=str(success_count), inline=True)
    await ctx.send(embed=embed)


# ── Help Command ──────────────────────────────────────────────────────────────

@bot.tree.command(name="help", description="Show all available commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Bot Commands",
        description="Here are all the commands you can use:",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="User Commands",
        value=(
            "**/verify** - Complete your verification (private form)\n"
            "**/myinfo** - View your verification info\n"
            "**/help** - Show this help message"
        ),
        inline=False
    )

    if interaction.user.guild_permissions.manage_guild:
        embed.add_field(
            name="Verification Management (Admin)",
            value=(
                "**/checkverification** `username` - Check if user is verified\n"
                "**/listverifications** - View all verified users\n"
                "**/exportverifications** - Export verifications to CSV\n"
                "**/syncusernames** - Update usernames in records\n"
                "**/updatediscordid** - Update Discord ID in records\n"
                "**/sendmessage** - Send a message to any channel (form)"
            ),
            inline=False
        )

    if interaction.user.guild_permissions.manage_roles:
        embed.add_field(
            name="Role Management (Admin)",
            value=(
                "**!addrole** `@role` `@user1 @user2 ...` - Add role to multiple users\n"
                "**!removerole** `@role` `@user1 @user2 ...` - Remove role from multiple users\n"
                "Example: !addrole @Member @user1 @user2 @user3"
            ),
            inline=False
        )

    if interaction.user.guild_permissions.manage_channels:
        embed.add_field(
            name="Channel Management (Admin)",
            value="**/createchannel** - Create a new channel with specific users (form)",
            inline=False
        )

    if interaction.user.guild_permissions.manage_messages:
        embed.add_field(
            name="Channel Cleanup (Admin)",
            value="**/cleanwelcome** `amount` - Delete bot welcome messages",
            inline=False
        )

    embed.add_field(
        name="Tips",
        value=(
            "• All forms are private - only you can see them\n"
            "• Type / to see all available commands with autocomplete\n"
            "• Admin commands require appropriate permissions"
        ),
        inline=False
    )

    embed.set_footer(text="All commands use Discord's slash command system")
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ── Clean Welcome ─────────────────────────────────────────────────────────────

@bot.tree.command(name="cleanwelcome", description="Delete bot welcome messages (Admin only)")
@app_commands.checks.has_permissions(manage_messages=True)
@app_commands.describe(amount="Number of messages to check (default: 50, max: 100)")
async def cleanwelcome(interaction: discord.Interaction, amount: int = 50):
    if amount < 1 or amount > 100:
        await interaction.response.send_message(
            "Please provide a number between 1 and 100.",
            ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)
    deleted_count = 0

    try:
        async for message in interaction.channel.history(limit=amount):
            if message.author == bot.user and message.embeds:
                for embed in message.embeds:
                    if embed.title and "Welcome" in embed.title:
                        try:
                            await message.delete()
                            deleted_count += 1
                            await asyncio.sleep(0.5)
                        except discord.NotFound:
                            pass
                        except discord.Forbidden:
                            await interaction.followup.send(
                                "Missing permissions to delete messages.",
                                ephemeral=True
                            )
                            return
                        break

        embed = discord.Embed(
            title="Channel Cleanup Complete",
            description=f"Deleted {deleted_count} welcome message(s)",
            color=discord.Color.green()
        )
        embed.add_field(name="Messages Checked", value=str(amount), inline=True)
        embed.add_field(name="Messages Deleted", value=str(deleted_count), inline=True)
        await interaction.followup.send(embed=embed, ephemeral=True)

    except discord.Forbidden:
        await interaction.followup.send(
            "Missing permissions to read message history or delete messages.",
            ephemeral=True
        )
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {str(e)}", ephemeral=True)


if __name__ == "__main__":
    bot.run(TOKEN)
