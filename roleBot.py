import discord
from discord.ext import commands
from discord.utils import get
import re
import os
import csv
import asyncio
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.environ['DISCORD_BOT_TOKEN']

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    if member.bot:
        return

    embed = discord.Embed(
        title="Welcome to Nobel 👋",
        description=(
            f"Hi {member.name}, welcome to **{member.guild.name}**.\n\n"
            "You've joined a learning community built on **growth, collaboration, and leadership**. "
            "Before you explore the full space, there's one quick step to complete."
        ),
        color=discord.Color.light_gray()
    )

    embed.add_field(
        name="One Step to Get Full Access",
        value=(
            "Please submit your **Discord username** so we can connect you to the right learning channels.\n\n"
            "**Your Discord username is:**"
        ),
        inline=False
    )

    embed.add_field(
        name="Your Username (copy this exactly)",
        value=f"```{member.name}```",
        inline=False
    )

    embed.add_field(
        name="What to Do Next",
        value=(
            "1. **Copy** the username above\n"
            "2. **Open the discord collection form** using the link below\n"
            "3. **Paste your username exactly as shown**\n"
            "4. **Submit the form** — that's it!"
        ),
        inline=False
    )

    embed.add_field(
        name="Discord collection form",
        value="[Click Here to fill it out](https://docs.google.com/forms/d/e/1FAIpQLSdyOfgOof9qZ8ouI4psTb0hnaudfQIVx9feG-SaTxoCWiT_Yw/viewform)",
        inline=False
    )

    embed.add_field(
        name="Correct Format",
        value=f"`{member.name}`",
        inline=True
    )

    embed.add_field(
        name="Please Don't Use",
        value=f"`{member.display_name}` or `{member.id}`",
        inline=True
    )

    embed.add_field(
        name="Need Help?",
        value="Reach out to **@rofhiwa_** or the **@auto team** — we're here to support you.",
        inline=False
    )

    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text="• Learn • Lead • Succeed")

    try:
        await member.send(embed=embed)
        print(f"Sent welcome DM to {member.name} ({member.id})")
    except discord.Forbidden:
        print(f"Could not DM {member.name} - DMs are disabled")

@bot.command()
async def help(ctx):
    if ctx.author.guild_permissions.manage_guild:
        embed = discord.Embed(
            title="Bot Command Guide",
            description="All available commands for the Nobel Discord Bot",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="User Commands",
            value=(
                "`!getmyusername` - Get your Discord username for forms\n"
                "`!getmyid` - Quick username lookup\n"
                "`!help` - Show this help message"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Validation Commands (Admin)",
            value=(
                "`!validateuser <username>` - Check if username exists\n"
                "`!bulkvalidate <user1> <user2>...` - Validate multiple users\n"
                "`!checkform <email> <username>` - Validate form submission\n"
                "`!finduser <search>` - Search for users by name"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Mass Communication (Admin)",
            value=(
                "`!recentjoins [days]` - Show recent joiners (default: 7)\n"
                "`!dmverify [days]` - DM recent joiners with username\n"
                "`!dmall` - DM ALL members (use carefully!)"
            ),
            inline=False
        )
        
        embed.add_field(
            name="OPs Command",
            value=(
                "`!addrole <role> <@user1> <@user2>...` - Add role to users\n"
                "`!removerole <role> <@user1> <@user2>...` - Remove role from users\n"
                "`!exportusers` - Export members to CSV\n"
                "`!createchannels` - Interactive channel creator wizard"
            ),
            inline=False
        )
        
        embed.set_footer(text="Use !help to see this message anytime")
    else:
        embed = discord.Embed(
            title="Available Commands : ",
            description="Commands you can use",
            color=discord.Color.blue() 
        )
        
        embed.add_field(
            name="Your Commands",
            value=(
                "`!getmyusername` - Get your Discord username for registration\n"
                "`!getmyid` - Quick username lookup\n"
                "`!help` - Show this help message"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Need to Register?",
            value="Use `!getmyusername` to get your username, then submit it in the discord collection form.",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, role: discord.Role, *user_mentions: str):
    if not role:
        await ctx.send("Please specify a valid role.")
        return
    success_count = 0
    invalid_users = []
    for user_mention in user_mentions:
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
                await ctx.send(f"I don't have permission to add roles to {user.mention}.")
            except discord.HTTPException:
                await ctx.send(f"Failed to assign role to {user.mention} due to an error.")
    if invalid_users:
        await ctx.send(f"Invalid users: {', '.join(invalid_users)}")
    
    embed = discord.Embed(
        title="Role Assignment Complete",
        color=discord.Color.green()
    )
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
                await ctx.send(f"I don't have permission to remove roles from {user.mention}.")
            except discord.HTTPException:
                await ctx.send(f"Failed to remove role from {user.mention} due to an error.")
    if invalid_users:
        await ctx.send(f"Invalid users: {', '.join(invalid_users)}")
    
    embed = discord.Embed(
        title="Role Removal Complete",
        color=discord.Color.green()
    )
    embed.add_field(name="Role", value=role.name, inline=True)
    embed.add_field(name="Users Removed", value=str(success_count), inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def getmyusername(ctx):
    embed = discord.Embed(
        title=" Your Discord Registration Info",
        description="Use this information to fill out discord collection forms",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Your Discord Username",
        value=f"```{ctx.author.name}```",
        inline=False
    )
    
    embed.add_field(
        name="What to Submit",
        value=f"`{ctx.author.name}`",
        inline=True
    )
    
    embed.add_field(
        name="Do NOT Submit",
        value=f"`{ctx.author.display_name}`",
        inline=True
    )
    
    embed.add_field(
        name="How to Copy Your Username",
        value=(
            "**Method 1: Use this bot**\n"
            "Copy the username above from the box and fill out the form\n\n"
            "**Method 2: Check your profile**\n"
            "1. Click your profile picture in Discord\n"
            "2. Copy the text under 'Username' and fill out the same form"
        ),
        inline=False
    )
    
    embed.add_field(
        name="IMPORTANT",
        value=(
            "**When filling forms:**\n"
            "✅ : `" + ctx.author.name + "`\n"
            "❌ : `" + ctx.author.display_name + "`\n"
            "❌ : `" + str(ctx.author.id) + "`\n"
            "❌ : `@" + ctx.author.name + "`"
        ),
        inline=False
    )
    
    embed.add_field(
        name="Discord collection form",
        value="[Click Here to fill it out](https://docs.google.com/forms/d/e/1FAIpQLSdyOfgOof9qZ8ouI4psTb0hnaudfQIVx9feG-SaTxoCWiT_Yw/viewform)",
        inline=False
    )
    
    embed.add_field(
        name="What's the difference?",
        value=(
            "**Username**: `{0}` - Your unique account name\n"
            "**Display Name**: `{1}` - Can be changed anytime".format(
                ctx.author.name, 
                ctx.author.display_name,
            )
        ),
        inline=False
    )
    
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    embed.set_footer(text="Submit your USERNAME, not display name!")
    
    try:
        await ctx.author.send(embed=embed)
        await ctx.send(f"{ctx.author.mention} Check your DMs for your username info!", delete_after=20)
        await ctx.message.delete() 
    except discord.Forbidden:
        await ctx.send(embed=embed, delete_after=30)
        await ctx.send(f"{ctx.author.mention} Please enable DMs! Your info will be deleted in 30 seconds for privacy.", delete_after=30)
        await ctx.message.delete() 

@bot.command()
async def getmyid(ctx):
    await ctx.invoke(bot.get_command('getmyusername'))

@bot.command()
@commands.has_permissions(manage_guild=True)
async def validateuser(ctx, *, username: str):
    username_clean = username.strip().lower()
    
    if not username_clean:
        await ctx.send("Please provide a username to validate.")
        return
    
    matching_members = []
    for member in ctx.guild.members:
        if not member.bot:
            if member.name.lower() == username_clean:
                matching_members.append(member)
    
    if not matching_members:
        for member in ctx.guild.members:
            if not member.bot:
                if member.display_name.lower() == username_clean:
                    matching_members.append(member)
    
    if matching_members:
        for member in matching_members:
            embed = discord.Embed(
                title="USER FOUND in Server",
                color=discord.Color.green()
            )
            embed.add_field(name="Submitted Username", value=f"`{username}`", inline=False)
            embed.add_field(name="Actual Username", value=f"`{member.name}`", inline=True)
            embed.add_field(name="Display Name", value=f"`{member.display_name}`", inline=True)
            embed.add_field(name="Discord ID", value=f"`{member.id}`", inline=False)
            embed.add_field(
                name="In Server Since",
                value=member.joined_at.strftime('%Y-%m-%d') if member.joined_at else 'N/A',
                inline=True
            )
            embed.add_field(name="✅ Status", value="Ready to add to channels/roles", inline=False)
            embed.set_thumbnail(url=member.display_avatar.url)
            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="USER NOT FOUND in Server",
            description="No member found with that username. Common issues:",
            color=discord.Color.red()
        )
        embed.add_field(name="Submitted", value=f"`{username}`", inline=False)
        embed.add_field(
            name="Possible Issues",
            value=(
                "1. User submitted their display name instead of username\n"
                "2. User hasn't joined the server yet\n"
                "3. Typo in the username\n"
                "4. User changed their username after submitting"
            ),
            inline=False
        )
        embed.add_field(
            name="💡 What to Do",
            value=(
                "1. Ask the user to use `!getmyusername` to check their username\n"
                "2. Check if they've joined the Discord server\n"
                "3. Ask them to resubmit with correct username"
            ),
            inline=False
        )
        await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_guild=True)
async def bulkvalidate(ctx, *usernames):
    if not usernames:
        await ctx.send("Please provide at least one username.\nUsage: `!bulkvalidate username1 username2 username3`")
        await ctx.message.delete() 
        return
    
    if len(usernames) > 20:
        await ctx.send("Maximum 20 usernames at once. Processing first 20...")
        usernames = usernames[:20]
        await ctx.message.delete() 
    
    found_users = []
    not_found = []
    
    progress_msg = await ctx.send(f"Validating {len(usernames)} usernames...")
    
    for username in usernames:
        username_clean = username.strip().lower()
        found = False
        
        for member in ctx.guild.members:
            if not member.bot:
                if member.name.lower() == username_clean or member.display_name.lower() == username_clean:
                    found_users.append(f"`{username}` → `{member.name}` (Display: {member.display_name})")
                    found = True
                    break
        
        if not found:
            not_found.append(username)
    
    embed = discord.Embed(
        title="Bulk Validation Results",
        description=f"Checked {len(usernames)} submissions",
        color=discord.Color.blue()
    )
    
    if found_users:
        embed.add_field(
            name=f"Found in Server ({len(found_users)})",
            value="\n".join(found_users[:10]) + (f"\n... and {len(found_users) - 10} more" if len(found_users) > 10 else ""),
            inline=False
        )
    
    if not_found:
        embed.add_field(
            name=f"NOT Found ({len(not_found)})",
            value=", ".join([f"`{u}`" for u in not_found[:15]]) + (f"\n... and {len(not_found) - 15} more" if len(not_found) > 15 else ""),
            inline=False
        )
    
    if not_found:
        embed.add_field(
            name="Troubleshooting",
            value="For NOT FOUND users:\n1. Ask them to use `!getmyusername`\n2. Check if they've joined the server\n3. Look for typos in submission",
            inline=False
        )
    
    embed.set_footer(text="Use !validateuser <username> for detailed info on a specific user")
    
    await progress_msg.delete()
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_guild=True)
async def exportusers(ctx):
    await ctx.send("Generating member list with usernames...")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"discord_users_{ctx.guild.name.replace(' ', '_')}_{timestamp}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'Username',
            'Display Name',
            'Discord ID',
            'Account Created',
            'Joined Server',
            'Status'
        ])
        
        members = sorted(
            [m for m in ctx.guild.members if not m.bot],
            key=lambda x: x.name.lower()
        )
        
        for member in members:
            writer.writerow([
                member.name,
                member.display_name,
                member.id,
                member.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                member.joined_at.strftime('%Y-%m-%d %H:%M:%S') if member.joined_at else 'N/A',
                'Active'
            ])
    
    embed = discord.Embed(
        title="Member Export Complete",
        description=f"Exported **{len(members)}** members",
        color=discord.Color.green()
    )
    embed.add_field(
        name="Use This For",
        value=(
            "- VLOOKUP validation in Google Sheets\n"
            "- Cross-referencing form submissions\n"
            "- Finding Discord IDs from submitted usernames"
        ),
        inline=False
    )
    
    await ctx.send(embed=embed, file=discord.File(filename))
    os.remove(filename)

@bot.command()
@commands.has_permissions(manage_guild=True)
async def checkform(ctx, *, form_data: str):
    parts = form_data.split()
    
    if len(parts) < 2:
        await ctx.send("Usage: `!checkform email@school.edu username123`")
        return
    
    email = parts[0]
    username = parts[1]
    
    email_valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)
    
    username_clean = username.strip().lower()
    member_found = None
    
    for member in ctx.guild.members:
        if not member.bot:
            if member.name.lower() == username_clean:
                member_found = member
                break
            elif member.display_name.lower() == username_clean:
                member_found = member
                break
    
    embed = discord.Embed(
        title="Form Submission Check",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Email",
        value=f"{'VALID' if email_valid else 'INVALID'} `{email}`",
        inline=False
    )
    
    if member_found:
        if member_found.name.lower() == username_clean:
            status = "VALID (Exact username match)"
        else:
            status = "FOUND (Display name match - user submitted wrong info)"
        
        embed.add_field(
            name="Discord User",
            value=f"{status}\n`{username}` → `{member_found.name}` (Display: {member_found.display_name})",
            inline=False
        )
    else:
        embed.add_field(
            name="Discord User",
            value=f"NOT FOUND `{username}`\nUser may have:\n1. Not joined server yet\n2. Submitted display name\n3. Made a typo",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_guild=True)
async def recentjoins(ctx, days: int = 7):
    now = datetime.now(timezone.utc)
    recent_members = [
        m for m in ctx.guild.members 
        if not m.bot 
        and m.joined_at 
        and (now - m.joined_at).days <= days
    ]
    
    if not recent_members:
        await ctx.send(f"No members joined in the last {days} days.")
        return
    
    recent_members.sort(key=lambda x: x.joined_at, reverse=True)
    
    embed = discord.Embed(
        title=f"Recent Joins (Last {days} Days)",
        description=f"Found **{len(recent_members)}** members",
        color=discord.Color.blue()
    )
    
    display_count = min(25, len(recent_members))
    member_list = []
    
    for member in recent_members[:display_count]:
        days_ago = (now - member.joined_at).days
        member_list.append(
            f"`{member.name}` ({member.display_name}) - {days_ago} day{'s' if days_ago != 1 else ''} ago"
        )
    
    embed.add_field(
        name=f"Members (showing {display_count}/{len(recent_members)})",
        value="\n".join(member_list),
        inline=False
    )
    
    if len(recent_members) > 25:
        embed.set_footer(text=f"Showing first 25 of {len(recent_members)} members")
    
    embed.add_field(
        name="Next Step",
        value=f"Use `!dmverify {days}` to remind these members to submit their username",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_guild=True)
async def dmverify(ctx, days: int = 7):
    FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSdyOfgOof9qZ8ouI4psTb0hnaudfQIVx9feG-SaTxoCWiT_Yw/viewform"
    DELAY_BETWEEN_DMS = 1.5
    
    now = datetime.now(timezone.utc)
    recent_members = [
        m for m in ctx.guild.members 
        if not m.bot 
        and m.joined_at 
        and (now - m.joined_at).days <= days
    ]
    
    if not recent_members:
        await ctx.send(f"ℹNo members found who joined in the last {days} days.")
        return
    
    confirm_msg = await ctx.send(
        f"Found **{len(recent_members)}** members who joined in the last {days} days.\n"
        f"Estimated time: ~{int(len(recent_members) * DELAY_BETWEEN_DMS / 60)} minutes.\n"
        f"React with ✅ to proceed or ❌ to cancel."
    )
    await confirm_msg.add_reaction("✅")
    await confirm_msg.add_reaction("❌")
    
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == confirm_msg.id
    
    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
        
        if str(reaction.emoji) == "❌":
            await ctx.send("❌ DM verification cancelled.")
            return
            
    except asyncio.TimeoutError:
        await ctx.send("⏰ Confirmation timed out. DM verification cancelled.")
        return
    
    sent = 0
    failed = 0
    progress_msg = await ctx.send(f"📤 Sending DMs... 0/{len(recent_members)}")
    
    for i, member in enumerate(recent_members, 1):
        try:
            dm_embed = discord.Embed(
                title="Complete Your Registration",
                description=f"Hi **{member.display_name}**! Please complete your registration.",
                color=discord.Color.blue()
            )
            
            dm_embed.add_field(
                name=" Your Discord Username",
                value=f"```{member.name}```",
                inline=False
            )
            
            dm_embed.add_field(
                name="What to Do",
                value=(
                    f"1. **Copy your username above**\n"
                    f"2. **Fill out this form**: {FORM_LINK}\n"
                    f"3. **Paste your exact username** in the form\n"
                    f"4. **Submit the form**"
                ),
                inline=False
            )
            
            dm_embed.add_field(
                name="⚠️ Important Notes",
                value=(
                    "✅ Submit: `{0}`\n"
                    "❌ Don't submit: `{1}` (display name)\n"
                    "❌ Don't submit: `@{0}`\n"
                    "❌ Don't submit: numbers or IDs".format(
                        member.name,
                        member.display_name
                    )
                ),
                inline=False
            )
            
            dm_embed.set_footer(text="Submit your USERNAME, not display name!")
            
            await member.send(embed=dm_embed)
            sent += 1
            print(f"Sent DM to {member.name} ({i}/{len(recent_members)})")
        except discord.Forbidden:
            failed += 1
            print(f"Could not DM {member.name} - DMs disabled")
        except discord.HTTPException as e:
            failed += 1
            print(f"Failed to DM {member.name}: {e}")
        
        if i % 5 == 0 or i == len(recent_members):
            await progress_msg.edit(content=f"📤 Sending DMs... {i}/{len(recent_members)}")
        
        if i < len(recent_members):
            await asyncio.sleep(DELAY_BETWEEN_DMS)
    
    embed = discord.Embed(
        title="✅ DM Verification Complete",
        color=discord.Color.green()
    )
    embed.add_field(name="✅ Successfully Sent", value=str(sent), inline=True)
    embed.add_field(name="❌ Failed (DMs Disabled)", value=str(failed), inline=True)
    embed.add_field(name="📊 Total Attempted", value=str(len(recent_members)), inline=True)
    embed.add_field(
        name="📅 Time Period",
        value=f"Members who joined in the last {days} days",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_guild=True)
async def dmall(ctx):
    FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSdyOfgOof9qZ8ouI4psTb0hnaudfQIVx9feG-SaTxoCWiT_Yw/viewform"
    DELAY_BETWEEN_DMS = 1.5
    
    all_members = [m for m in ctx.guild.members if not m.bot]
    
    if not all_members:
        await ctx.send("ℹ️ No members found.")
        return
    
    confirm_msg = await ctx.send(
        f"⚠️ WARNING: This will DM **{len(all_members)}** members.\n"
        f"⏱️ Estimated time: ~{int(len(all_members) * DELAY_BETWEEN_DMS / 60)} minutes.\n"
        f"React with ✅ to proceed or ❌ to cancel."
    )
    await confirm_msg.add_reaction("✅")
    await confirm_msg.add_reaction("❌")
    
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == confirm_msg.id
    
    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
        
        if str(reaction.emoji) == "❌":
            await ctx.send("❌ DM verification cancelled.")
            return
            
    except asyncio.TimeoutError:
        await ctx.send("Confirmation timed out. DM verification cancelled.")
        return
    
    sent = 0
    failed = 0
    progress_msg = await ctx.send(f"Sending DMs... 0/{len(all_members)}")
    
    for i, member in enumerate(all_members, 1):
        try:
            dm_embed = discord.Embed(
                title="Registration Reminder",
                description=f"Hi **{member.display_name}**! This is a reminder to complete your registration.",
                color=discord.Color.blue()
            )
            
            dm_embed.add_field(
                name="Your Discord Username",
                value=f"```{member.name}```",
                inline=False
            )
            
            dm_embed.add_field(
                name="discord collection form",
                value=f"Please fill out: {FORM_LINK}",
                inline=False
            )
            
            dm_embed.add_field(
                name="Important",
                value=(
                    "**Submit your username:** `{0}`\n"
                    "**Not your display name:** `{1}`".format(
                        member.name,
                        member.display_name
                    )
                ),
                inline=False
            )
            
            dm_embed.set_footer(text="Submit your USERNAME, not display name!")
            
            await member.send(embed=dm_embed)
            sent += 1
        except discord.Forbidden:
            failed += 1
        except discord.HTTPException as e:
            failed += 1
            print(f"Failed to DM {member.name}: {e}")
        
        if i % 10 == 0 or i == len(all_members):
            await progress_msg.edit(content=f"📤 Sending DMs... {i}/{len(all_members)}")
        
        if i < len(all_members):
            await asyncio.sleep(DELAY_BETWEEN_DMS)
    
    embed = discord.Embed(
        title=" DM Verification Complete",
        color=discord.Color.green()
    )
    embed.add_field(name="Successfully Sent", value=str(sent), inline=True)
    embed.add_field(name="Failed (DMs Disabled)", value=str(failed), inline=True)
    embed.add_field(name="Total Attempted", value=str(len(all_members)), inline=True)
    
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_guild=True)
async def finduser(ctx, *, search_term: str):
    search_term = search_term.strip().lower()
    
    if len(search_term) < 2:
        await ctx.send("❌ Please enter at least 2 characters to search.")
        return
    
    matching_members = []
    
    for member in ctx.guild.members:
        if not member.bot:
            if (search_term in member.name.lower() or 
                search_term in member.display_name.lower()):
                matching_members.append(member)
    
    if not matching_members:
        await ctx.send(f"No members found matching `{search_term}`")
        return
    
    matching_members.sort(key=lambda x: x.name.lower())
    
    embed = discord.Embed(
        title=f"Search Results for '{search_term}'",
        description=f"Found {len(matching_members)} members",
        color=discord.Color.blue()
    )
    
    display_count = min(20, len(matching_members))
    result_list = []
    
    for member in matching_members[:display_count]:
        result_list.append(f"👤 `{member.name}` ({member.display_name}) - ID: `{member.id}`")
    
    embed.add_field(
        name=f"Members (showing {display_count}/{len(matching_members)})",
        value="\n".join(result_list),
        inline=False
    )
    
    if len(matching_members) > 20:
        embed.set_footer(text=f"Showing first 20 of {len(matching_members)} matches")
    
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def createchannels(ctx):
    await ctx.send("**Channel Creator Wizard Started!**\nLet's create some channels together.")
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    
    try:
        await ctx.send("**Step 1:** What category do you want to create channels in? (Type the category name)")
        category_msg = await bot.wait_for('message', check=check, timeout=120.0)
        category_name = category_msg.content.strip()
        
        category = discord.utils.get(ctx.guild.categories, name=category_name)
        
        if not category:
            await ctx.send(f"Category `{category_name}` not found. Creating it now...")
            category = await ctx.guild.create_category(category_name)
            await ctx.send(f"Category `{category_name}` created!")
        else:
            await ctx.send(f"Using existing category: `{category_name}`")
        
        await ctx.send("**Step 2:** How many channels do you want to create under this category?")
        count_msg = await bot.wait_for('message', check=check, timeout=60.0)
        
        try:
            channel_count = int(count_msg.content.strip())
            if channel_count < 1 or channel_count > 20:
                await ctx.send("Please enter a number between 1 and 20.")
                return
        except ValueError:
            await ctx.send("Please enter a valid number.")
            return
        
        await ctx.send(f" Great! We'll create **{channel_count}** channel(s).")
        
        for i in range(channel_count):
            await ctx.send(f"\n**Channel {i+1}/{channel_count}**")
            
            await ctx.send(f"**Channel {i+1} Name:** What should this channel be called?")
            name_msg = await bot.wait_for('message', check=check, timeout=60.0)
            channel_name = name_msg.content.strip().lower().replace(" ", "-")
            
            await ctx.send(f"👥 **Channel {i+1} Users:** Please provide usernames to add to this channel (space-separated)\nExample: `user1 user2 user3`\nType `skip` to create channel without specific users.")
            users_msg = await bot.wait_for('message', check=check, timeout=120.0)
            
            if users_msg.content.strip().lower() == 'skip':
                usernames = []
            else:
                usernames = users_msg.content.strip().split()
            
            valid_members = []
            invalid_usernames = []
            
            if usernames:
                validation_msg = await ctx.send(f"Validating {len(usernames)} username(s)...")
                
                for username in usernames:
                    username_clean = username.strip().lower()
                    found = False
                    
                    for member in ctx.guild.members:
                        if not member.bot:
                            if member.name.lower() == username_clean:
                                valid_members.append(member)
                                found = True
                                break
                    
                    if not found:
                        invalid_usernames.append(username)
                
                await validation_msg.delete()
                
                embed = discord.Embed(
                    title=f"Validation Results for Channel: {channel_name}",
                    color=discord.Color.blue()
                )
                
                if valid_members:
                    embed.add_field(
                        name=f"Valid Users ({len(valid_members)})",
                        value="\n".join([f"👤 `{m.name}`" for m in valid_members]),
                        inline=False
                    )
                
                if invalid_usernames:
                    embed.add_field(
                        name=f"Invalid/Not Found ({len(invalid_usernames)})",
                        value=", ".join([f"`{u}`" for u in invalid_usernames]),
                        inline=False
                    )
                    embed.add_field(
                        name="Note",
                        value="Invalid users will NOT be added. Channel will still be created for valid users.",
                        inline=False
                    )
                
                await ctx.send(embed=embed)
            
            creating_msg = await ctx.send(f"⚙️ Creating channel `#{channel_name}`...")
            
            try:
                new_channel = await ctx.guild.create_text_channel(
                    name=channel_name,
                    category=category
                )
                
                await new_channel.set_permissions(ctx.guild.default_role, read_messages=False)
                
                added_count = 0
                for member in valid_members:
                    try:
                        await new_channel.set_permissions(member, read_messages=True, send_messages=True)
                        added_count += 1
                    except Exception as e:
                        print(f"Error adding {member.name} to {channel_name}: {e}")
                
                result_embed = discord.Embed(
                    title=f"Channel Created: #{channel_name}",
                    color=discord.Color.green()
                )
                result_embed.add_field(name="Category", value=category.name, inline=True)
                result_embed.add_field(name="Users Added", value=str(added_count), inline=True)
                result_embed.add_field(name="Channel", value=new_channel.mention, inline=False)
                
                if invalid_usernames:
                    result_embed.add_field(
                        name=" Could Not Add",
                        value=f"{len(invalid_usernames)} user(s): " + ", ".join([f"`{u}`" for u in invalid_usernames[:5]]),
                        inline=False
                    )
                    result_embed.add_field(
                        name="💡 Action Required",
                        value="Please double-check these usernames and manually add them if needed.",
                        inline=False
                    )
                
                await creating_msg.delete()
                await ctx.send(embed=result_embed)
                
            except discord.Forbidden:
                await ctx.send(f"❌ I don't have permission to create channels in `{category.name}`")
            except discord.HTTPException as e:
                await ctx.send(f"❌ Failed to create channel: {e}")
        
        final_embed = discord.Embed(
            title="Channel Creation Complete!",
            description=f"Successfully processed {channel_count} channel(s) in category `{category.name}`",
            color=discord.Color.gold()
        )
        final_embed.set_footer(text="Use !help to see all available commands")
        
        await ctx.send(embed=final_embed)
        
    except asyncio.TimeoutError:
        await ctx.send("⏰ Channel creation timed out. Please run `!createchannels` again to start over.")

if __name__ == "__main__":
    bot.run(TOKEN)