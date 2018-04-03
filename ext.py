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

import random


def get(file, col, cond=''):
    # Gets a column from the specified csv file.
    # Data is stored as player_id,nickname,tribe,vote
    # If the player has not voted, vote equals "nobody"
    # If cond is set, it will only return the specified column if cond is in
    # any column.
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
    # Writes a row to the specified csv file.
    # Data is stored as player_id,nickname,tribe,vote
    # Line to be written is passed as a list ([player_id, nickname, vote])
    # If the player has not voted, vote equals "nobody"
    # If delete is True, it will instead delete the row with the passed data
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
    # Toggles vote time
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
    # Returns true if an item is in a file
    exist = get(file, 1, item)
    if exist:
        return True
    return False


def is_vote_time():
    # Returns true if it voting has been allowed
    time = get("vote_time", 1)
    if time[0] == '1':
        return True
    return False


def voted(voter):
    # Checks if player has already voted
    # voter is the player's Discord id
    vote = get("players.csv", 4, voter)
    if vote != 'nobody':
        return True
    return False


def same(player, vote):
    # Checks to see if the vote is the same
    # player is the player's Discord id
    # vote is the nickname of the person they have voted
    who = get("players.csv", 4, player)
    if vote == who:
        return True
    return False


def get_tribal():
    # Returns the tribe at tribal council
    tribe = get("tribes.csv", 2, 'voting')
    return tribe


def set_tribal(tribe):
    # Sets tribal council to a tribe
    # tribe is the tribe to set tribal council to
    write("tribes.csv", ['voting', tribe])


class Player:
    # Class for a player

    file = "players.csv"

    def __init__(self, user_id):
        self.user_id = user_id
        self.nick = get(self.file, 2, user_id)
        self.tribe = get(self.file, 3, user_id)
        self.vote = get(self.file, 4, user_id)

    def write(self, nick='', tribe='', vote='nobody'):
        # Write data for a player
        if nick:
            self.nick = nick
        if tribe:
            self.tribe = tribe
        self.vote = vote
        write(self.file, [self.user_id, self.nick, self.tribe, self.vote])

    def destroy(self):
        # Delete a player
        write(self.file, [self.user_id], True)


def get_players():
    # Return a list of all players
    ids = get("players.csv", 1)
    players = [Player(id) for id in ids]
    return players


def sort_votes(votes):
    # Return a list which contains the most amounts of votes that can be read
    tally = {}
    for item in votes:
        if item in tally:
            tally[item] += 1
        else:
            tally[item] = 1
    highest = max(tally.values())
    most = [a for a, b in tally.items() if b == highest]
    if len(most) > 1:
        random.shuffle(votes)
        return votes, None
    most = most[0]
    majority = len(votes) // 2
    if tally[most] > majority:
        extra = tally[most] - majority
        tally[most] -= extra
        new = []
        for item in tally:
            for n in range(tally[item]):
                new.append(item)
        random.shuffle(new)
        for n in range(extra):
            new.append(most)
    else:
        tally[most] -= 1
        new = []
        for item in tally:
            for n in range(tally[item]):
                new.append(item)
        random.shuffle(new)
        new.append(most)
    return new, most
