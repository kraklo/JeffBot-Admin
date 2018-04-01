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
import random
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
async def add_player(ctx, user_id, name):
    """Adds a player to the player list (discord_id, nickname)"""
    if "Host" in [role.name for role in ctx.message.author.roles]:
        if ext.exists("players.csv", user_id):
            await client.say('Player already exists.')
        else:
            # Write to players.csv with the player data
            ext.write("players.csv", [user_id, name, 'no', 'nobody'])
            # Change nickname and role
            user = discord.utils.get(ctx.message.server.members, name=user_id[:-5])
            role = discord.utils.get(ctx.message.server.roles, name="Castaway")
            await client.say("Added user *{}* as *{}*".format(user_id, name))
            try:
                await client.change_nickname(user, name)
            except discord.errors.Forbidden:
                await client.say("Unable to change nickname. Please manually change {}'s nickname to {}.".format(user_id, name))
            except AttributeError:
                await client.say("Unable to change nickname. Please manually change {}'s nickname to {}.".format(user_id, name))
            try:
                await client.add_roles(user, role)
            except discord.errors.Forbidden:
                await client.say("Unable to add role *Castaway*. Please manually add role to player {}.".format(user_id))
            except AttributeError:
                await client.say("Unable to add role *Castaway*. Please manually add role to player {}.".format(user_id, name))
    else:
        await client.say("You are not a host.")


@client.command(pass_context=True)
async def remove_player(ctx, user_id):
    """Removes a player from the player list (discord_id or nickname)"""
    if "Host" in [role.name for role in ctx.message.author.roles]:
        if ext.exists("players.csv", user_id):
            id = ext.get("players.csv", 1, user_id)[:-5]
            # Delete player from players.csv
            ext.write("players.csv", [user_id], True)
            await client.say("Removed {} from player list.".format(user_id))
            # Replace Castaway role with Spectator
            user = discord.utils.get(ctx.message.server.members, name=id)
            spec = discord.utils.get(ctx.message.server.roles, name="Spectator")
            try:
                await client.replace_roles(user, spec)
            except discord.errors.Forbidden:
                await client.say("Unable to replace role *Castaway*. Please manually remove role from player {}.".format(user_id))
            except AttributeError:
                await client.say("Unable to replace role *Castaway*. Please manually remove role from player {}.".format(user_id))
        else:
            await client.say("{} was already not a player.".format(user_id))
    else:
        await client.say("You are not a host.")


@client.command(pass_context=True)
async def show(ctx, what):
    """Lists either the players in the player list, the players who have voted, or the players who haven't voted"""
    if "Host" in [role.name for role in ctx.message.author.roles]:
        if what == "players":
            # Store player ids and then print data
            ids = ext.get("players.csv", 1)
            nicks = ext.get("players.csv", 2)
            for item in ids:
                await client.say("{}: {}, {} tribe".format(item, nicks[ids.index(item)], ext.get("players.csv", 3, item)))
        elif what == "voted":
            # Get players who have voted
            ids = ext.get("players.csv", 1)
            voted = [ext.get("players.csv", 2, player) for player in ids if ext.voted(player)]
            if not voted:
                await client.say("Nobody has voted.")
            elif len(ids) == len(voted):
                await client.say("Everybody has voted.")
            else:
                for player in voted:
                    await client.say(player)
        elif what == "not_voted":
            # Get players who haven't voted
            ids = ext.get("players.csv", 1)
            not_voted = [ext.get("players.csv", 2, player) for player in ids if not ext.voted(player)]
            if not not_voted:
                await client.say("Everybody has voted.")
            elif len(ids) == len(not_voted):
                await client.say("Nobody has voted.")
            else:
                for player in not_voted:
                    await client.say(player)
        else:
            await client.say("Please enter a valid argument (players, voted, not_voted).")
    else:
        await client.say("You are not a host.")


@client.command(pass_context=True)
async def vote_time(ctx, tribe=''):
    """Manually toggle if players can vote or not"""
    if "Host" in [role.name for role in ctx.message.author.roles]:
        if not ext.is_vote_time() and tribe and ext.exists("tribes.csv", tribe):
            # Toggle vote time and set tribal to tribe
            ext.toggle("vote_time")
            ext.set_tribal(tribe)
            await client.say("Players can now vote.")
        elif not tribe and not ext.is_vote_time():
            await client.say("Specify a tribe to allow players to vote.")
        elif not ext.is_vote_time() and not ext.exists("tribes.csv", tribe):
            await client.say("Tribe {} does not exist.".format(tribe))
        else:
            ext.toggle("vote_time")
            ext.set_tribal('none')
            await client.say("Players can now no longer vote.")
    else:
        await client.say("You are not a host.")


@client.command(pass_context=True)
async def read_votes(ctx):
    """Manually read the votes"""
    if "Host" in [role.name for role in ctx.message.author.roles]:
        # Toggle vote time if players can still vote
        if ext.is_vote_time():
            ext.toggle("vote_time")
        # Store a tally of players and the number of votes they have
        tally = {}
        votes = []
        ids = ext.get("players.csv", 1)
        for id in ids:
            if ext.voted(id):
                votes.append(ext.get("players.csv", 4, id))
            elif ext.get("players.csv", 3, id) == ext.get_tribal():
                votes.append(ext.get("players.csv", 2, id))
        for item in votes:
            if item in tally:
                tally[item] += 1
            else:
                tally[item] = 1

        # Print the data in tally
        await client.say("The votes are as follows.")
        for item in tally:
            if tally[item] == 1:
                await client.say("{} has 1 vote.".format(item))
            else:
                await client.say("{} has {} votes.".format(item, tally[item]))

        # Calculate who has the most votes
        highest = max(tally.values())
        most = [a for a, b in tally.items() if b == highest]

        if len(most) != 1:
            # Print tie if thre are more than two people with the highest count
            await client.say("We have a tie!")
        else:
            await client.say("{}, the tribe has spoken.".format(most[0]))
            player_id = ext.get("players.csv", 1, most[0])
            # Replace role to either Spectator or Juror
            user = discord.utils.get(ctx.message.server.members, name=player_id[:-5])
            spec = discord.utils.get(ctx.message.server.roles, name="Spectator")
            if len(ext.get("players.csv", 1)) <= 10:
                spec = discord.utils.get(ctx.message.server.roles, name="Juror")
            try:
                await client.replace_roles(user, spec)
            except discord.errors.Forbidden:
                await client.say("Unable to replace role.")
            except AttributeError:
                await client.say("Unable to replace role.")
            # Delete player from player list
            ext.write("players.csv", [player_id], True)

        # Set everyone's vote to nobody
        ids = ext.get("players.csv", 1)
        for item in ids:
            ext.write("players.csv", [item, ext.get("players.csv", 2, item), ext.get_tribal(), 'nobody'])
        # Reset tribal
        ext.set_tribal('none')
    else:
        await client.say("You are not a host.")


@client.command(pass_context=True)
async def vote(ctx, player):
    """Vote for a player for Tribal Council (player's nickname)"""
    exists = ext.exists("players.csv", str(ctx.message.author))
    if ext.is_vote_time() and exists:
        user = str(ctx.message.author)
        tribe = ext.get_tribal()
        if "#" in player:
            await client.say("Please use a player's nickname, not their id.")
        elif tribe != ext.get("players.csv", 3, user):
            await client.say("You are not in {} tribe.".format(tribe))
        elif tribe != ext.get("players.csv", 3, player):
            await client.say("{} is not in your tribe.".format(player))
        elif ext.voted(user):
            if ext.same(user, player):
                await client.say("Vote is already {}.".format(player))
            else:
                ext.write(
                    "players.csv",
                    [
                        user,
                        ext.get("players.csv", 2, user),
                        ext.get_tribal(),
                        player
                    ]
                )
                await client.say("Vote changed to {}.".format(player))
        else:
            if ext.exists("players.csv", player):
                ext.write(
                    "players.csv",
                    [
                        user,
                        ext.get("players.csv", 2, user), ext.get_tribal(),
                        player
                    ]
                )
                await client.say("Voted for {}.".format(player))
            else:
                await client.say("That is not a player you can vote for.")
    elif not ext.is_vote_time():
        await client.say("You cannot vote at this time.")
    else:
        await client.say("You are not a player.")


@client.command(pass_context=True)
async def sort_tribes(ctx, tribe1, tribe2):
    """Sorts players into tribes. (tribe1, tribe2)"""
    if "Host" in [role.name for role in ctx.message.author.roles]:
        # Store all player data in a dict
        player_data = {}
        tribes = [tribe1, tribe2]
        counter = {tribe1: 0, tribe2: 0}
        players = ext.get("players.csv", 1)
        for player in players:
            # Choose a random tribe
            while True:
                choice = random.choice(tribes)
                if counter[choice] < len(players) / 2:
                    counter[choice] += 1
                    break
            # Assign tribe to player
            player_data[player] = [
                player,
                ext.get("players.csv", 2, player),
                choice,
                'nobody'
            ]

        for player in player_data:
            # Write data to players.csv
            ext.write("players.csv", player_data[player])
            # Change roles
            role = discord.utils.get(
                ctx.message.server.roles,
                name=player_data[player][2]
            )
            user = discord.utils.get(
                ctx.message.server.members,
                name=player_data[player][0][:-5]
            )
            try:
                await client.add_roles(user, role)
            except discord.errors.Forbidden:
                await client.say("Unable to add {} role to {}. Forbidden.".format(player_data[player][2], player_data[player][0]))
            except AttributeError:
                await client.say("Unable to add {} role to {}. Role does not exist.".format(player_data[player][2], player_data[player][0]))

        # Write tribes to tribes.csv
        ext.write("tribes.csv", [tribe1, tribe2])
    else:
        await client.say("You are not a host.")


@client.command(pass_context=True)
async def merge_tribes(ctx, tribe):
    """Merges players into a single tribe. (tribe)"""
    if "Host" in [role.name for role in ctx.message.author.roles]:
        ids = ext.get("players.csv", 1)
        for player in ids:
            # Change tribe to new merge tribe
            ext.write(
                "players.csv",
                [player, ext.get("players.csv", 2, player), tribe, 'nobody']
            )
            # Change roles
            role = discord.utils.get(ctx.message.server.roles, name=tribe)
            castaway = discord.utils.get(
                ctx.message.server.roles,
                name="Castaway"
            )
            user = discord.utils.get(
                ctx.message.server.members,
                name=player[:-5]
            )
            try:
                await client.replace_roles(user, role, castaway)
            except discord.errors.Forbidden:
                await client.say("Forbidden to add role.")
            except AttributeError:
                await client.say("Role {} does not exist.".format(tribe))

        # Delete old tribes from tribes.csv
        ext.write("tribes.csv", ext.get("tribes.csv", 1)[1], True)
        # Write new tribe to tribes.csv
        ext.write("tribes.csv", [tribe])
    else:
        await client.say("You are not a host.")

client.run(token)
