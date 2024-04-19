import ast
import functools
import operator as op
import os
import random
import traceback

import discord
from discord.ext import commands
from dotenv import load_dotenv
from pyurbandict import UrbanDict

load_dotenv()

token: str = os.getenv(key="TOKEN")
devchannel = int(os.getenv(key="DEVCHANNEL"))
operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.BitXor: op.xor,
    ast.USub: op.neg,
}


bot = commands.Bot(command_prefix=">", self_bot=True)
bot.remove_command("help")


def is_me(m) -> bool:
    return m.author == bot.user


async def eval_(node):
    match node:
        case ast.Constant(value) if isinstance(value, int):
            return value  # integer
        case ast.BinOp(left, op, right):
            return operators[type(op)](eval_(node=left), eval_(node=right))
        case ast.UnaryOp(op, operand):  # e.g., -1
            return operators[type(op)](eval_(node=operand))
        case _:
            return None


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
    login: str = f"| Logged in as {bot.user} (ID: {bot.user.id}) |"
    decorator: str = "-" * len(login)
    print(decorator + "\n" + login + "\n" + decorator + "\n" * 6)


@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.message.delete()
        print(
            f"Command not found {ctx.command}: {''.join(traceback.format_tb(error.__traceback__))}"
        )
    else:
        print(f"Command: {ctx.command}\nError: {error}")


@bot.event
async def on_message(message: discord.Message) -> None:
    if isinstance(message.channel, discord.DMChannel):
        log: str = (
            f"LOG -- {message.author}: {message.clean_content.strip()} (DM with {message.channel.recipient.name})"
        )
        print(log)
    else:
        log: str = (
            f"LOG -- {message.author}: {message.clean_content.strip()} ({message.guild.name}, #{message.channel.name})"
        )
        print(log)
    with open(file="log.txt", mode="a") as f:
        f.write(log + "\n")
    if message.author.id == bot.user.id:
        await bot.process_commands(message)

        if message.content.startswith("f/"):
            components: list[str] = message.content.split(sep="/")
            if 3 <= len(components) < 5:
                before: str = components[1]
                after: str = components[2]
                if after == "":
                    return
                channel = await bot.fetch_channel(message.channel.id)
                msgs = [message async for message in channel.history(limit=100)]
                count = 0
                old: str = message.content
                await message.delete()
                for msg in msgs:
                    if msg.author.id == bot.user.id:
                        if before in msg.content.lower():
                            count += 1
                            print(
                                f"Replacing {count} message{'s' if count > 1 else ''}. ({msg.content} -> {msg.content.replace(before, after)}",
                                end="\r",
                            )
                            await msg.edit(content=msg.content.replace(before, after))
                            if old.endswith("/g"):
                                continue
                            else:
                                break
                print(f"Replaced {count} message{'s' if count > 1 else ''}.")
            elif len(components) >= 5:
                pass  # TODO possible thing that needs to be replaced has a / in it, need to fix this
    else:
        pass


@bot.command()
@cmd()
async def calculate(ctx, *expression: str) -> None:
    if expression == ():
        return
    expression = " ".join(expression)
    expr = eval_(node=ast.parse(expression, mode="eval").body)
    if expr is not None:
        await ctx.send(str(object=expression))


@bot.command()
@cmd()
async def choose(ctx, *choices: str) -> None:
    await ctx.send(random.choice(seq=choices))


@bot.command()
@cmd()
async def spam(ctx, times: int, *content) -> None:
    print(content)
    if content == ():
        content = "Repeating.."
    for _ in range(times):
        await ctx.send(
            " ".join(list(content)) if isinstance(content, tuple) else content
        )


@bot.command()
@cmd()
async def slang(ctx, *words):
    if words == ():
        return
    words = " ".join(words)
    word = UrbanDict(words)
    results = word.search()

    await ctx.send(results[0].definition + "\n\n" + results[0].example)


@bot.command()
@cmd()
async def purge(ctx, amount: int = 10, channel: int = None) -> None:
    if channel is None:
        channel = ctx.channel
    else:
        channel = await bot.fetch_channel(channel)

    count = 0
    if isinstance(channel, discord.TextChannel):
        await channel.purge(limit=amount, check=is_me)
    elif isinstance(channel, discord.DMChannel):
        msgs = [message async for message in channel.history(limit=amount * 2)]
        for msg in msgs:  # 2x the amount because 2 people in dms?
            if msg.author.id == bot.user.id:
                count += 1
                await msg.delete()
                if count == amount:
                    return
    else:
        return


@bot.command()
@cmd()
async def find(ctx, word: str, channel: int = None) -> None:
    if channel is None:
        channel = ctx.channel
    else:
        channel = await bot.fetch_channel(channel)
    msgs = [message async for message in channel.history(limit=100)]
    results = ""
    for msg in msgs:
        msg: discord.Message
        if word.lower() in msg.content.lower():
            results += f"{msg.author}: {msg.content} @{msg.created_at.strftime('%Y/%m/%d %H:%M:%S')}\n"
    if results == "":
        await ctx.send("...")
        return
    for i in range(0, len(results), 4000):
        await ctx.send(results[i : i + 4000])


# @bot.command()
# async def joined(member: discord.Member) -> None:
#     channel = bot.fetch_channel(devchannel)
#     await channel.send(f"{member.name} joined in {member.joined_at}")


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
