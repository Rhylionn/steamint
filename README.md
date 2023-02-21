# Steamint

Information gathering on steam profiles.
This tool allows you to get a lot of information about a steam profile as long as it is public. This tool does not require any API key.

**Disclaimer**: This tool is intended for **educational purposes only.** The **author disclaim any responsibility** for any misuse or illegal use of this tool. The **user is fully responsible** for any inappropriate use of this tool.

**Informations include**:

- Real name
- Location
- Actual username
- Username history with change time
- Description
- Player level
- Privacy state
- Profile picture
- Account creation date
- Ban informations
- Owned games with playtime and last time played
- Groups with links, visibility and member count
- Comments with sender and add time
- Wishlist with add time

## Installation

Clone this repository:

```
git clone https://github.com/Rhylionn/steamint
```

Install dependencies:

```
pip install -r requirements.txt
```

## Basic usage

To search for a user with username (e.g: https://steamcommunity.com/id/username)

```
python main.py <username>
```

To search for a user with a steamid (e.g: https://steamcommunity.com/profiles/steamID):

```
python main.py -s <steamID>
```

## Commands

| Tools                | Description                                         |
| -------------------- | --------------------------------------------------- |
| -s / --steamid       | Search a user using steamid                         |
| -o / --output        | Save data into json file                            |
| -mG / --max-games    | Set number of games to be displayed                 |
| -mT / --max-groups   | Set number of groups to be displayed                |
| -mC / --max-comments | Set number of comments to be displayed              |
| -mW / --max-wishlist | Set number of games in the wishlist to be displayed |
| -mF / --max-friends  | Set number of friends to be displayed               |
