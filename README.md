# TR3-VR Bot

A Discord re-creation of TR3-VR from the Destiny2 mission "Zero Hour".

This bot "walks" through channels, plays sounds and randomly kicks users from channels.



This bot is intended as a joke and was created in a hurry for our server's Halloween event. Please excuse the messy code.


## Requirements
* Python 3.6.0+
* aiohttp
* discord.py (>=1.6)
* pyopenssl
* requests

## Installation

Clone this repository and proceed to install the required packages using your preferred method.

##### With Pipenv
```bash
pipenv install
```

##### With Pip
```bash
pip install -r Requirements.txt
```

## Updating

##### With Pipenv
```bash
git pull
pipenv update
```

##### With Pip

```bash
git pull
pip install --upgrade -r Requirements.txt
```

## Setup
To set up the bot, paste your token into the `TOKEN` variable in `main.py`

## Running the bot

##### Linux & OSX
```bash
./run.sh
```

##### Windows
```cmd
run.bat
```
(or simply double-click run.bat)


### Additional arguments
* `--allow-root`: Enabled the bot to be run as the `root` user on Linux. (Not recommended!)


## Configuring the bot

The bot will create a new configuration file within the `config` folder on first boot.
This file will look like this:

```json
{
    "global": {
        "kill_enabled": false
    }
}
```

To add settings for a specific server, add another entry to the config file:

```json
{
    "global": {
        "kill_enabled": false
    },
    "<YOUR SERVER ID HERE>": {
        "kill_enabled": true
    }
}
```


## Adding the bot to your server

The bot will display an invite link in your terminal once the bot is ready to receive commands.


## Usage in Discord

* `startWalking`: Makes the bot "walk" through channels
* `stopWalking`: Stops the bot from "walking" through channels 
* `restartWalking`:  Restarts the "walking" process (in case it gets stuck on something)

## Adding more sounds

To add more sounds to the bot, simply put them into one of the folders in `res/Sounds`.

## Credits & Copyright

* All TR3-VR sounds belong to Bungie Inc.
* Additional kick sounds added by Sync1211, Surrendercat and Butterbauch
