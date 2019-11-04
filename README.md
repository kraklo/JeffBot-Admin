# JeffBot

A Discord bot to help run Discord Survivor ORGs

This was written mainly for my own ORGs, but it can also be used by anyone in their own ORGs. You'll have to create your own Discord bot to do this, though, as I didn't write this to handle more than one season at a time.

## JeffBot-Admin

This is a special version of JeffBot which removes all player interactivity from the original version of JeffBot and makes it so only hosts can interact with it. This is for the purpose of allowing more flexibility on the host's end yet still providing the useful automation of admin tasks in an ORG.

> NOTE: All idol functionality has been removed from JeffBot-Admin to allow hosts to play with their own ways to use idols.

## Installing

To install, copy all files to a single directory, then run `setup.py`. It will ask you for the token of your Discord bot. You are then ready to run `jeffbot.py`.

> NOTE: The bot must be run from the directory it is in.

## Requirements

* Python 3.6.2+
* Rapptz's `discord.py` library

`pip` should handle the library for you. I recommend checking the [discord.py repository](https://github.com/Rapptz/discord.py) out yourself.
