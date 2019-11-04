"""
MIT License

Copyright (c) 2018-2019 Evan Liapakis

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
    if ext.is_vote_time():
        await client.change_presence(game=discord.Game(name="{} tribal council".format(ext.get_tribal())))
    else:
        await client.change_presence(game=discord.Game(name="j.help"))


@client.command(pass_context=True)
async def add(ctx, *args):
    """Adds a player, vote, or strike to the database"""
    if not ext.host(ctx):
        # Checks to see if user running the command is a host
        await client.say("You are not a host.")
        return 1

    if len(args) != 2:
        # Check for valid amount of arguments
        if len(args) == 3:
            cmd, user_id, name = args
        else:
            await client.say("Please enter a valid amount of arguments.")
            return 1
    else:
        cmd, player = args
        if not ext.exists("players.csv", player):
            await client.say("Player does not exist.")
            return 1

    if cmd == "player":
        if ext.exists("players.csv", user_id):
            # Check if player already exists
            await client.say('Player already exists.')
        elif user_id[:-5] not in [mem.name for mem in ctx.message.server.members]:
            # Check for player in server
            await client.say("There is no {} in the server.".format(user_id))
        else:
            # Write to players.csv with the player data
            player = discord.utils.get(ctx.message.server.members, name=user_id[:-5])
            ext.Player(player.mention[2:-1]).write(name, 'no')
            # Change nickname and role
            user = ext.get_player_object(ctx, user_id)
            role = ext.get_role_object(ctx, "Castaway")
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
                await client.say("Unable to add role *Castaway*. Please manually add role to player {}.".format(user_id))
    elif cmd == "vote":
        exists = ext.exists("players.csv", user_id)

        if not exists:
            await client.say("{} is not a player.".format(user_id))
            return 1

        voter = ext.Player(ext.get("players.csv", 1, user_id))
        if ext.exists("players.csv", name):
            voter.write(vote=name)
            await client.say("{} has voted for {}.".format(voter.nick, name))

            players = ext.get_players()
            voted = [player for player in players if ext.voted(player.user_id)]

            if len(players) == len(voted):
                await client.send_message(ext.get_channel(ctx, "host-channel"), content="{} Everyone has voted.".format(ext.get_role_object(ctx, "Host").mention))
        else:
            await client.say("{} is not a player.".format(player))
    elif cmd == "strike":
        player = ext.Player(ext.get("players.csv", 1, player))
        if player.strikes == 2:
            await client.say("{} has 3 strikes and is eliminated".format(player.nick))
            if len(ext.get_players()) <= 10:
                role = "Juror"
            else:
                role = "Spectator"
            ext.remove_player(client, ctx, player.nick, role)
        else:
            player.write(strike=True)
            if player.strikes > 1:
                await client.say("{} now has {} strikes.".format(player.nick, player.strikes))
            else:
                await client.say("{} now has {} strike.".format(player.nick, player.strikes))
            nick = player.nick
            channel = ext.get_channel(ctx, "{}-confessional".format(nick.lower()))
            await client.edit_channel(channel, topic="Strikes: {}".format(player.strikes))
    else:
        await client.say("Invalid command. Commands are `player`, `vote`, and `strike`.")


@client.command(pass_context=True)
async def remove(ctx, *args):
    """Removes a player or vote from the database"""
    if not ext.host(ctx):
        await client.say("You are not a host.")
        return 1

    if len(args) != 2:
        await client.say("Please enter a valid amount of arguments.")
        return 1

    cmd, player = args

    if not ext.exists("players.csv", player):
        await client.say("Player does not exist.")
        return 1

    if cmd == "player":
        # Remove the player
        await ext.remove_player(client, ctx, player, "Spectator")
        await client.say("Removed {} from player list.".format(player))
    elif cmd == "vote":
        await client.say("This doesn't really do anything.")
    else:
        await client.say("Please enter a valid argument.")


@client.command(pass_context=True)
async def show(ctx, *args):
    """Lists either the players in the player list, the players who have
    voted, or the players who haven't voted"""

    if not ext.host(ctx):
        await client.say("You are not a host.")
        return 1

    if len(args) < 1:
        await client.say("Please enter an argument.")
        return 1

    if args[0] == "players":
        # Store player ids and then print data
        players = ext.get_players()
        data = ''
        # Store all data in one string
        # makes it quicker to print in Discord
        for item in players:
            data += "{}: {}, {} tribe".format(discord.utils.get(ctx.message.server.members, id=item.user_id), item.nick, item.tribe)
            if players[-1] != item:
                data += '\n'
        await client.say(data)
    elif args[0] == "voted":
        # Get players who have voted
        players = ext.get_players()
        voted = [player.nick for player in players if ext.voted(player.user_id)]
        if not voted:
            await client.say("Nobody has voted.")
        elif len(players) == len(voted):
            await client.say("Everybody has voted.")
        else:
            data = ''
            for player in voted:
                data += player
                if voted[-1] != player:
                    data += '\n'
            await client.say(data)
    elif args[0] == "not_voted":
        # Get players who haven't voted
        players = ext.get_players()
        not_voted = [player.nick for player in players if player.tribe == ext.get_tribal() and player.vote == "nobody"]
        if not not_voted:
            await client.say("Everybody has voted.")
        # Check to see if nobody has voted
        # HACK: this only works because any new data written is added
        # to the bottom
        # However, it changes O(n) to O(1)
        elif players[-1].vote != "nobody":
            await client.say("Nobody has voted.")
        else:
            data = ''
            for player in not_voted:
                data += player
                if not_voted[-1] != player:
                    data += '\n'
            await client.say(data)
    elif args[0] == "tribe":
        # Show the players in a tribe
        if len(args) < 2:  # Check for a second argument
            await client.say("Please enter a tribe.")
        elif not ext.exists("tribes.csv", args[1]):
            await client.say("Tribe {} does not exist.".format(args[1]))
        else:
            data = ''
            players = ext.get_players()
            for player in players:
                # Add nickname to data if player is in the tribe
                if player.tribe == args[1]:
                    data += player.nick
                    if players[-1] != player:
                        # Add a new line char if not last player in list
                        data += '\n'
            await client.say(data)
    elif args[0] == "votes":
        # Get each player's vote
        players = ext.get_players()
        if ext.is_vote_time():
            # Check to see if anyone has voted
            # HACK: this only works because any new data written is added
            # to the bottom
            # However, it changes O(n) to O(1)
            if players[-1].vote != "nobody":
                data = ""
                for player in players:
                    if player.tribe == ext.get_tribal():
                        if player.vote == "nobody":
                            data += "{} hasn't voted yet.".format(player.nick)
                        else:
                            data += "{} is voting {}.".format(player.nick, player.vote)
                        if player != players[-1]:
                            data += '\n'
                await client.say(data)
            else:
                await client.say("Nobody has voted.")
        else:
            await client.say("Players cannot vote.")
    elif args[0] == "strikes":
        players = ext.get_players()
        data = ""
        for player in players:
            if player.strikes != 1:
                data += "{} has {} strikes.".format(player.nick, player.strikes)
            else:
                data += "{} has 1 strike.".format(player.nick)
            if player != players[-1]:
                data += "\n"
        await client.say(data)


@client.command(pass_context=True)
async def tribal_council(ctx, tribe=''):
    """Manually toggle if players can vote or not"""

    if not ext.host(ctx):
        await client.say("You are not a host.")
        return 1

    if not tribe and not ext.is_vote_time():
        await client.say("Specify a tribe to go to tribal council.")
    elif not ext.is_vote_time() and ext.exists("tribes.csv", tribe):
        # Toggle vote time and set tribal to tribe
        await client.change_presence(game=discord.Game(name="{} tribal council".format(tribe)))
        ext.toggle()
        ext.set_tribal(tribe)
        await client.say("You can now add votes.")
    elif not ext.is_vote_time() and not ext.exists("tribes.csv", tribe):
        await client.say("Tribe {} does not exist.".format(tribe))
    else:
        await client.change_presence(game=discord.Game(name="j.help"))
        ext.toggle()
        ext.set_tribal('none')
        await client.say("You can now no longer add votes.")


@client.command(pass_context=True)
async def eliminate(ctx, castaway=''):
    """Manually read the votes"""

    if not ext.host(ctx):
        await client.say("You are not a host.")
        return 1

    if not castaway:
        await client.say("Please specify a player to eliminate.")
        return 1

    # Toggle vote time
    ext.toggle()

    players = ext.get_players()
    for player in players:
        # Set vote to nobody
        player.write()

    player = ext.Player(ext.get("players.csv", 1, castaway))
    obj = ext.get_player_object(ctx, player)
    jury = False
    with open("tribes.csv") as f:
        tribes = f.read().split("\n")
        if "," not in tribes:
            jury = True
    if jury:
        spec = "Juror"
    else:
        spec = "Spectator"

    nick = player.nick
    channel = ext.get_channel(ctx, "{}-confessional".format(nick.lower()))
    channel_name = "{}-{}".format(nick.lower(), ext.get_final_place())
    await client.edit_channel(channel, name="{}-{}".format(nick.lower(), ext.get_final_place()))

    # Remove the player
    await ext.remove_player(client, ctx, castaway, spec)

    # Reset tribal
    ext.set_tribal('none')
    await client.change_presence(game=discord.Game(name="j.help"))

    await client.say("{} has successfully been eliminated.".format(nick))


@client.command(pass_context=True)
async def sort_tribes(ctx, tribe1, tribe2, swap=''):
    """Sorts players into tribes. (tribe1, tribe2)"""

    if not ext.host(ctx):
        await client.say("You are not a host.")
        return 1

    players = ext.get_players()
    tribes = [tribe1, tribe2]
    counter = {tribe1: 0, tribe2: 0}
    for player in players:
        # Choose a random tribe
        while True:
            choice = random.choice(tribes)
            if counter[choice] < len(players) / 2:
                counter[choice] += 1
                break
        # Assign tribe to player
        player.write(tribe=choice)
        # Change roles
        role = ext.get_role_object(ctx, player.tribe)
        user = ext.get_player_object(ctx, player)
        try:
            await client.add_roles(user, role)
        except discord.errors.Forbidden:
            await client.say(("Unable to add {} role to {}. Forbidden."
                              "").format(player.tribe, player.nick))
        except AttributeError:
            await client.say(("Unable to add {} role to {}. Role does not "
                              "exist.").format(player.tribe, player.nick))

    # Write tribes to tribes.csv
    ext.write("tribes.csv", [tribe1, tribe2])

    if not swap:
        player_count = len(ext.get("players.csv", 1))
        with open("playernum", 'w') as f:
            f.write(str(player_count))


@client.command(pass_context=True)
async def merge_tribes(ctx, tribe):
    """Merges players into a single tribe. (tribe)"""

    if not ext.host(ctx):
        await client.say("You are not a host.")
        return 1

    players = ext.get_players()
    for player in players:
        # Change tribe to new merge tribe
        player.write(tribe=tribe)
        # Change roles
        role = ext.get_role_object(ctx, tribe)
        castaway = ext.get_role_object(ctx, "Castaway")
        user = ext.get_player_object(ctx, player)
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


client.run(token)
