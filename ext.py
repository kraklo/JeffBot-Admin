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

import random
import discord


def get(file, col, cond=''):
    """Gets a column from the specified csv file.
    Data is stored as player_id,nickname,tribe,vote
    If the player has not voted, vote equals "nobody"
    If cond is set, it will only return the specified column if cond is in
    any column."""
    with open(file) as f:
        col -= 1
        if cond:
            for line in f:
                data = line.strip().split(',')
                if cond in data:
                    return data[col]
        else:
            data = [line.strip().split(',')[col] for line in f]
            return data


def write(file, data, delete=False):
    """Writes a row to the specified csv file.
    Data is stored as player_id,nickname,tribe,vote
    Line to be written is passed as a list ([player_id, nickname, vote])
    If the player has not voted, vote equals "nobody"
    If delete is True, it will instead delete the row with the passed data"""
    new = ''
    with open(file) as f:
        for line in f:
            if data[0] not in line:
                new += line
        if not delete:
            new += ','.join(data) + '\n'
    with open(file, 'w') as f:
        f.write(new)


def toggle():
    """Toggles vote time"""
    file = "vote_time"
    content = ''
    with open(file) as f:
        content = f.read().strip()
    with open(file, 'w') as f:
        if content == '1':
            f.write('0')
        elif content == '0':
            f.write('1')


def exists(file, item):
    """Returns true if an item is in a file"""
    exist = get(file, 1, item)
    if exist:
        return True
    return False


def is_vote_time():
    """Returns true if it voting has been allowed"""
    time = get("vote_time", 1)
    if time[0] == '1':
        return True
    return False


def voted(voter):
    """Checks if player has already voted
    voter is the player's Discord id"""
    vote = get("players.csv", 4, voter)
    if vote != 'nobody':
        return True
    return False


def same(player, vote):
    """Checks to see if the vote is the same
    player is the player's Discord id
    vote is the nickname of the person they have voted"""
    who = get("players.csv", 4, player)
    if vote == who:
        return True
    return False


def get_tribal():
    """Returns the tribe at tribal council"""
    tribe = get("tribes.csv", 2, 'voting')
    return tribe


def set_tribal(tribe):
    """Sets tribal council to a tribe
    tribe is the tribe to set tribal council to"""
    write("tribes.csv", ['voting', tribe])


class Player:
    """Class for a player"""

    file = "players.csv"

    def __init__(self, user_id):
        self.user_id = user_id
        self.nick = get(self.file, 2, user_id)
        self.tribe = get(self.file, 3, user_id)
        self.vote = get(self.file, 4, user_id)
        if exists("players.csv", user_id):
            self.strikes = int(get(self.file, 5, user_id))
        else:
            self.strikes = 0

    def write(self, nick='', tribe='', vote='nobody', strike=False):
        """Write data for a player"""
        if nick:
            self.nick = nick
        if tribe:
            self.tribe = tribe
        if strike:
            self.strikes += 1
        self.vote = vote
        write(self.file, [self.user_id, self.nick, self.tribe, self.vote, str(self.strikes)])

    def destroy(self):
        """Delete a player"""
        write(self.file, [self.user_id], True)


def get_players():
    """Return a list of all players"""
    ids = get("players.csv", 1)
    players = [Player(id) for id in ids]
    return players


def get_player_object(ctx, player):
    """Returns the object for a player"""
    if isinstance(player, Player):
        user_id = player.user_id
    elif '#' in player:
        user_id = player[:-5]
    else:
        user_id = player
    obj = discord.utils.get(ctx.message.server.members, id=user_id)
    return obj


def get_role_object(ctx, role):
    """Returns the object for a role"""
    return discord.utils.get(ctx.message.server.roles, name=role)


async def remove_player(client, ctx, nick, role):
    """Removes a player and replaces their roles"""
    player = Player(get("players.csv", 1, nick))
    # Delete player from players.csv
    player.destroy()
    # Replace roles with role
    user = get_player_object(ctx, player)
    spec = get_role_object(ctx, role)
    try:
        await client.replace_roles(user, spec)
    except discord.errors.Forbidden:
        await client.say("Unable to replace role.")
    except AttributeError:
        await client.say("Unable to replace role.")


def host(ctx):
    """Returns true if player has host role"""
    if "Host" in [role.name for role in ctx.message.author.roles]:
        return True
    return False


def get_channel(ctx, name):
    return discord.utils.get(ctx.message.server.channels, name=name)


def player_num():
    with open("playernum") as f:
        return f.read().strip()


def get_placing():
    player_num = len(get("players.csv", 1))
    total_num = int(get("playernum", 1)[0])
    place = str(total_num - player_num + 1)

    if place[-1] == '1':
        place += "st"
    elif place[-1] == '2':
        place += "nd"
    elif place[-1] == '3':
        place += "rd"
    else:
        place += "th"

    return place


def get_final_place():
    place = str(len(get("players.csv", 1)))

    if place[-1] == '1':
        place += "st"
    elif place[-1] == '2':
        place += "nd"
    elif place[-1] == '3':
        place += "rd"
    else:
        place += "th"

    return place
