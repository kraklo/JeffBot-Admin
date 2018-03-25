#!/usr/local/bin/python3.6

"""
MIT License

Copyright (c) 2018 Evan Liapakis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from discord.ext import commands
import discord
import ext

client = commands.Bot('v.')

tok = open('token')
token = tok.read().strip()
tok.close()


@client.event
async def on_ready():
    print("Bot online.")
    print("Username: {}".format(client.user.name))
    print("ID: {}".format(client.user.id))
    await client.change_presence(game=discord.Game(name="v.vote"))


@client.command(pass_context=True)
async def vote(ctx, player):
    """Vote for a player for Tribal Council"""
    if ext.isvotetime() and ext.exists(str(ctx.message.author)):
        user = str(ctx.message.author)
        if ext.voted(user):
            if ext.same(user, player):
                await client.say("Vote is already {}.".format(player))
            else:
                ext.write("players.csv", [user, ext.get("players.csv", 1, user), player])
                await client.say("Vote changed to {}.".format(player))
        else:
            if ext.exists(player):
                ext.write("players.csv", [user, ext.get("players.csv", 1, user), player])
                await client.say("Voted for {}.".format(player))
            else:
                await client.say("That is not a player you can vote for.")
    elif not ext.isvotetime():
        await client.say("You cannot vote at this time.")
    else:
        await client.say("You are not a player.")


client.run(token)