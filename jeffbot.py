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

client = commands.Bot('j.')

tok = open('token')
token = tok.read().strip()
tok.close()


@client.event
async def on_ready():
    print("Bot online.")
    print("Username: {}".format(client.user.name))
    print("ID: {}".format(client.user.id))
    await client.change_presence(game=discord.Game(name="j.help"))


@client.command(pass_context=True)
async def addplayer(ctx, userid, name):
    """Adds a player to the player list"""
    if ext.exists(userid):
        await client.say('Player already exists.')
    else:
        ext.write("players.csv", [userid, name])
        user = discord.utils.get(ctx.message.server.members, name=userid[:-5])
        role = discord.utils.get(ctx.message.server.roles, name="Castaway")
        await client.say("Added user *{}* as *{}*".format(userid, name))
        try:
            await client.change_nickname(user, name)
        except:
            await client.say("Unable to change nickname. Please manually change {}'s nickname to {}.".format(userid, name))
        try:
            await client.add_roles(user, role)
        except:
            await client.say("Unable to add role *Castaway*. Please manually add role to player {}.".format(userid))


@client.command(pass_context=True)
async def removeplayer(ctx, userid):
    """Removes a player from the player list"""
    if ext.exists(userid):
        ext.write("players.csv", [userid], True)
        await client.say("Removed {} from player list.".format(userid))
        role = discord.utils.get(ctx.message.server.roles, name="Castaway")
        user = discord.utils.get(ctx.message.server.members, name=userid[:-5])
        try:
            await client.remove_roles(user, role)
        except:
            await client.say("Unable to remove role *Castaway*. Please manually remove role from player {}.".format(userid))
    else:
        await client.say("{} was already not a player.".format(userid))


@client.command()
async def listplayers():
    """Lists all players in the player list"""
    ids = ext.get("players.csv", 1)
    nicks = ext.get("players.csv", 2)
    for item in ids:
        await client.say("{}: {}".format(nicks(item.index()), item))


@client.command()
async def votetime():
    """Manually toggle if players can vote or not"""
    ext.toggle("votetime")
    if ext.isvotetime():
        await client.say("Players can now no longer vote.")
    else:
        await client.say("Players can now vote.")


client.run(token)