import functools
import os
import random

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token: str = os.getenv(key="TOKEN")
devchannel = int(os.getenv(key="DEVCHANNEL"))
bot = commands.Bot(command_prefix=">", self_bot=True)
bot.remove_command("help")


def cmd():
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(*args):
            if args[0].author.id == bot.user.id:
                await args[0].message.delete()
                return await func(*args)
            else:
                return None

        return wrapped

    return wrapper


@bot.event
async def on_ready() -> None:
    login = f"| Logged in as {bot.user} (ID: {bot.user.id}) |"
    decorator = "-" * len(login)
    print(decorator + "\n" + login + "\n" + decorator + "\n" * 6)


@bot.command()
async def add(ctx, left: int, right: int) -> None:
    await ctx.send(left + right)


@bot.command()
async def choose(ctx, *choices: str) -> None:
    await ctx.send(random.choice(seq=choices))


@bot.command()
@cmd()
async def repeat(ctx, times: int, content="repeating...") -> None:
    for _ in range(times):
        await ctx.send(content)


@bot.command()
async def joined(member: discord.Member) -> None:
    channel = bot.fetch_channel(devchannel)
    await channel.send(f"{member.name} joined in {member.joined_at}")


# @bot.group()
# async def cool(ctx) -> None:
#     """Says if a user is cool.

#     In reality this just checks if a subcommand is being invoked.
#     """
#     if ctx.invoked_subcommand is None:
#         await ctx.send(f"No, {ctx.subcommand_passed} is not cool")


# @cool.command(name="bot")
# async def _bot(ctx) -> None:
#     """Is the bot cool?"""
#     await ctx.send("Yes, the bot is cool.")


bot.run(token=token)
