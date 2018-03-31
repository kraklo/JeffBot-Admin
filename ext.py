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
    # Data is stored as player_id,nickname,tribe,vote
    # If the player has not voted, vote equals "nobody"
    # If cond is set, it will only return the specified column if cond is in
    # any column.
    f = open(file)
    col -= 1
    if cond:
        for line in f:
            data = line.strip().split(',')
            if cond in data:
                f.close()
                return data[col]
    else:
        data = [line.strip().split(',')[col] for line in f]
        f.close()
        return data


def write(file, data, delete=False):
    # Writes a row to the specified csv file.
    # Data is stored as player_id,nickname,tribe,vote
    # Line to be written is passed as a list ([player_id, nickname, vote])
    # If the player has not voted, vote equals "nobody"
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
        f.write('1')
    f.close()


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
