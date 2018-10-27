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
async def add(ctx, *args):
    """Adds a player, idol, or strike to the database"""
    if ext.host(ctx):
        # Checks to see if user running the command is a host

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
                ext.Player(user_id).write(name, 'no')
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
        elif cmd == "idol":
            if ext.exists("idols.csv", player):
                # Check if player already has an idol
                # TODO: Allow players to have as many idols as they have found
                await client.say("Player already has an idol.")
            else:
                # Add idol
                ext.write("idols.csv", [player, "no"])
                await client.say("Added idol.")
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
        else:
            await client.say("Invalid command. Commands are `player`, `idol`, and `strike`.")
    else:
        await client.say("You are not a host.")


@client.command(pass_context=True)
async def remove(ctx, *args):
    """Removes a player or idol from the database"""
    if ext.host(ctx):
        if len(args) == 0:
            await client.say("Please enter an argument (player, idol).")
        elif args[0] == "player":
            nick = args[1]
            if ext.exists("players.csv", nick):
                # Remove the player
                await ext.remove_player(client, ctx, nick, "Spectator")
                await client.say("Removed {} from player list.".format(nick))
            else:
                await client.say("{} was already not a player.".format(nick))
        elif args[0] == "idol":
            if len(args) < 2:
                await client.say("Please specify a player.")
            else:
                player = args[1]
                if ext.exists("players.csv", player):
                    if ext.exists("idols.csv", player):
                        ext.write("idols.csv", [player], True)
                        await client.say("Removed idol.")
                    else:
                        await client.say("Player does not have an idol.")
                else:
                    await client.say("Player does not exist.")
    else:
        await client.say("You are not a host.")


@client.command(pass_context=True)
async def show(ctx, *args):
    """Lists either the players in the player list, the players who have
    voted, or the players who haven't voted"""
    if ext.host(ctx):
        if len(args) < 1:
            # If no argument given, throw error message
            await client.say("Please enter an argument.")
        elif args[0] == "players":
            # Store player ids and then print data
            players = ext.get_players()
            data = ''
            # Store all data in one string
            # makes it quicker to print in Discord
            for item in players:
                data += "{}: {}, {} tribe".format(item.user_id, item.nick, item.tribe)
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
        elif args[0] == "idols":
            # Get all players with idols
            idols = ext.get("idols.csv", 1)
            if idols:
                data = ""
                for player in idols:
                    using = ext.get("idols.csv", 2, player)
                    if using == "yes":
                        data += "{}: using".format(player)
                    else:
                        data += "{}: not using".format(player)
                    if player != idols[-1]:
                        data += '\n'
                await client.say(data)
            else:
                await client.say("Nobody has an idol.")
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
        else:
            await client.say("Please enter a valid argument.")
    else:
        await client.say("You are not a host.")


@client.command(pass_context=True)
async def vote_time(ctx, tribe=''):
    """Manually toggle if players can vote or not"""
    if ext.host(ctx):
        if not tribe and not ext.is_vote_time():
            await client.say("Specify a tribe to allow players to vote.")
        elif not ext.is_vote_time() and ext.exists("tribes.csv", tribe):
            # Toggle vote time and set tribal to tribe
            ext.toggle()
            ext.set_tribal(tribe)
            await client.say("Players can now vote.")
        elif not ext.is_vote_time() and not ext.exists("tribes.csv", tribe):
            await client.say("Tribe {} does not exist.".format(tribe))
        else:
            ext.toggle()
            ext.set_tribal('none')
            await client.say("Players can now no longer vote.")
    else:
        await client.say("You are not a host.")


@client.command(pass_context=True)
async def read_votes(ctx):
    """Manually read the votes"""
    if ext.host(ctx):
        # Toggle vote time
        ext.toggle()

        # Store votes in a list
        votes = []
        players = ext.get_players()
        for player in players:
            if ext.voted(player.user_id):
                votes.append(player.vote)
            elif player.tribe == ext.get_tribal():
                votes.append(player.nick)
            # Set vote to nobody
            player.write()

        # Get the order to read the votes and who is out
        final, out = ext.sort_votes(votes)
        idols = ext.get_idols()

        # Read out idols
        if idols:
            msg = ""
            for player in idols:
                if player == idols[0]:
                    msg += "A reminder that {}".format(player)
                elif player == idols[-1]:
                    msg += " and {}".format(player)
                else:
                    msg += ", {}".format(player)
            if len(idols) > 1:
                msg += " are using idols."
            else:
                msg += " is using an idol."
            await client.say(msg)

        # Read the votes
        count = 1
        for vote in final:
            if count == 1:
                read = "1st vote: {}".format(vote)
            elif count == 2:
                read = "2nd vote: {}".format(vote)
            elif count == 3:
                read = "3rd vote: {}".format(vote)
            else:
                read = "{}th vote: {}".format(count, vote)
            count += 1
            if vote in idols:
                read += ", does not count"
            await client.say(read)

        # Remove any idols being used
        for player in ext.get("idols.csv", 1):
            if ext.get("idols.csv", 2, player) == "yes":
                ext.write("idols.csv", [player], True)

        if out is None:
            # Print tie if more than two people with the highest count
            await client.say("We have a tie!")
        else:
            player = ext.Player(ext.get("players.csv", 1, out))
            obj = ext.get_player_object(ctx, player)
            await client.say("{}, the tribe has spoken.".format(obj.mention))
            if len(players) <= 10:
                spec = "Juror"
            else:
                spec = "Spectator"
            # Remove the player
            await ext.remove_player(client, ctx, out, spec)
        # Reset tribal
        ext.set_tribal('none')
    else:
        await client.say("You are not a host.")


@client.command(pass_context=True)
async def vote(ctx, player):
    """Vote for a player for Tribal Council (player's nickname)"""
    exists = ext.exists("players.csv", str(ctx.message.author))
    if ext.is_vote_time() and exists:
        user = ext.Player(str(ctx.message.author))
        tribe = ext.get_tribal()
        if "#" in player:
            await client.say("Please use a player's nickname, not their id.")
        elif tribe != user.tribe:
            await client.say("You are not in {} tribe.".format(tribe))
        elif tribe != ext.get("players.csv", 3, player):
            await client.say("{} is not in your tribe.".format(player))
        elif ext.voted(user.user_id):
            if ext.same(user.user_id, player):
                await client.say("Vote is already {}.".format(player))
            else:
                user.write(vote=player)
                await client.say("Vote changed to {}.".format(player))
        else:
            if ext.exists("players.csv", player):
                user.write(vote=player)
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
    if ext.host(ctx):
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
    else:
        await client.say("You are not a host.")


@client.command(pass_context=True)
async def merge_tribes(ctx, tribe):
    """Merges players into a single tribe. (tribe)"""
    if ext.host(ctx):
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
    else:
        await client.say("You are not a host.")


@client.command(pass_context=True)
async def rocks(ctx, *players):
    """Do rocks. (players who the vote was between)"""
    if ext.host(ctx):
        if players:
            await client.say("All players will draw a rock.")
            await client.say(("The player who draws the black rock "
                              "will be eliminated."))
            # Get all players who will draw
            player_list = ext.get_players()
            tribe = ext.get("players.csv", 3, players[0])
            choices = []
            for player in player_list:
                if player.nick not in players and player.tribe == tribe:
                    choices.append(player)
            # Choose a random player
            out = random.choice(choices)
            obj = ext.get_player_object(ctx, out)
            await client.say("{} has the black rock.".format(out.nick))
            await client.say("{}, the tribe has spoken.".format(obj.mention))
            role = "Spectator"
            if len(players_list) <= 10:
                role = "Juror"
            else:
                role = "Spectator"
            # Eliminate
            await ext.remove_player(client, ctx, out.nick, role)
        else:
            await client.say("Please specify players who are safe.")
    else:
        await client.say("You are not a host.")


@client.command(pass_context=True)
async def use_idol(ctx):
    """Allow a player to use their idol"""
    player = ext.get("players.csv", 2, str(ctx.message.author))
    if ext.exists("players.csv", player):
        if ext.exists("idols.csv", player):
            if ext.get("idols.csv", 2, player) == "yes":
                await client.say("You are already using your idol.")
            else:
                ext.write("idols.csv", [player, "yes"])
                await client.say("I can confirm this is a hidden immunity idol.")
        else:
            await client.say("You do not have an idol.")
    else:
        await client.say("You are not a player.")

client.run(token)
