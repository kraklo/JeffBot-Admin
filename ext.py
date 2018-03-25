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


def get(file, col, cond=''):
    # Gets a column from the specified csv file.
    # Data is stored as playerid,nickname,vote
    # If no one has voted, vote equals "nobody"
    # If cond is set, it will only return the specified column if cond is in any column.
    f = open(file)
    if cond:
        for line in f:
            data = line.strip().split('\n')
            if cond in data:
                f.close()
                return data[col + 1]
    else:
        data = [line.strip().split(',')[col + 1] for line in f]
        f.close()
        return data
    f.close()


def write(file, data, delete=False):
    # Writes a row to the specified csv file.
    # Data is stored as playerid,nickname,vote
    # Line to be written is passed as a list ([playerid, nickname])
    # If delete is True, it will instead delete the row with the passed data
    f = open(file)
    new = ''
    for line in f:
        if data[0] not in line:
            new += line
    f.close()
    if not delete:
        new += ','.join(data) + '\n'
    f = open(file, 'w')
    f.write(new)
    f.close()


def toggle(file):
    # Toggles vote time
    f = open(file)
    content = f.read().strip()
    f.close()
    f = open(file, 'w')
    if content == '1':
        f.write('0')
    elif content == '0':
        f.write('0')
    f.close()


def exists(playerid):
    # Returns true if a player is in the player list
    exist = get("players.csv", 1, playerid)
    if exist:
        return True
    return False


def isvotetime():
    # Returns true if it voting has been allowed
    time = get("votetime", 1)
    if time[0] == '1':
        return True
    return False


def voted(voter):
    # Checks if player has already voted
    # voter is the player's Discord id
    vote = get("players.csv", 3, voter)
    if vote != 'nobody':
        return True
    return False


def same(player, vote):
    # Checks to see if the vote is the same
    # player is the player's Discord id
    # vote is the nickname of the person they have voted
    who = get("players.csv", 3, player)
    if vote == who:
        return True
    return False
