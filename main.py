#!/usr/bin/env python3

from bs4 import BeautifulSoup
import argparse
import requests
import re
import json
from datetime import datetime
import xmltodict

parser = argparse.ArgumentParser(description="Parser")
parser.add_argument('username', type=str, help="Username used to search for data")

args = parser.parse_args()
username = args.username

class Steamint:
  def __init__(self, username):
    self.username = username
    self.url = 'https://steamcommunity.com/id/%s' % username
    
    print("Steamint - Information gathing on steam profiles")
    print("Searching data for {}".format(self.username))
    
    self.mainpage = self.get_mainpage()
    self.profile_data = self.get_xml_mainpage()
    self.gamespage = self.get_games_page()
    self.friendlist = self.get_friendlist_page()

  # Profile

  def get_mainpage(self):
    page = requests.get(self.url)
    soup = BeautifulSoup(page.text, 'html.parser')
    user_content = soup.find('div', {"id": "responsive_page_template_content"}) 
    return user_content 

  def get_xml_mainpage(self):
    xml_page_url = "{}/?xml=1".format(self.url)
    xml_page = requests.get(xml_page_url)
    profile_data = xmltodict.parse(xml_page.text)
    return profile_data["profile"]
  
  def get_privacystate(self):
    output = "Privacy state: {}".format(self.profile_data["privacyState"])
    print(output)

  def get_actual_persona(self):
    output = "Actual persona: {}".format(self.profile_data["steamID"])
    print(output)

  def get_persona_history(self):
    persona_history_url = self.url + "/ajaxaliases"
    history_request = requests.get(persona_history_url)
    persona_history = history_request.json()

    output = "Persona history: \n"
    for history in persona_history:
      output += "- {0} changed the: {1} \n".format(history["newname"], history["timechanged"])

    print(output)

  def get_real_name(self):
    output = "Real name: {}".format(self.profile_data["realname"])
    print(output)

  def get_location(self):
    output = "Location: {}".format(self.profile_data["location"])
    print(output)
  
  def get_description(self):
    description = self.mainpage.find('div', {"class": "profile_summary"}).text
    print("Profile description: {}".format(description))

  def get_level(self):
    level = self.mainpage.find('span', {'class': 'friendPlayerLevelNum'}).text
    print("Player level: {}".format(level))

  def get_status(self):
    output = "Current status: {}".format(self.profile_data["stateMessage"])
    print(output)

  def get_membership_duration(self):
    output = "Member since: {}".format(self.profile_data["memberSince"])
    print(output)

  def get_ban_info(self):
    is_vacban = False if self.profile_data["vacBanned"] == '0' else True
    is_tradeban = False if self.profile_data["tradeBanState"] == 'None' else True
    is_limited = False if self.profile_data["isLimitedAccount"] == '0' else True
    output = "VAC Ban: {0} | Trade Ban: {1} | Limited account: {2}".format(is_vacban, is_tradeban, is_limited)

    print(output)

  # Games

  def get_games_page(self):
    games_url = self.url + "/games/?tab=all"
    page = requests.get(games_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    content = soup.find('div', {'id': 'responsive_page_template_content'})
    return content

  def get_games(self, number=None):
    scripts = self.gamespage.find_all("script")

    games_script = None
    for script in scripts:
      if script.find_parent() == self.gamespage:
        games_script = script.text

    games_text = re.search(r'var rgGames = (.+?);', games_script).group(1)
    games = json.loads(games_text)

    nb_script = len(games) if number == None or number > len(games) else number

    output = "Games ({0}/{1}): \n".format(nb_script, len(games))
    for i in range(nb_script):
      game = games[i]
      last_played = datetime.fromtimestamp(game["last_played"]).date().strftime("%d/%m/%Y")
      output += "- {0} with {1} hours on record. Last time played the: {2}\n".format(game["name"], game["hours_forever"], last_played)

    print(output)

  # Friends

  def get_friendlist_page(self):
    friends_url = "{}/friends".format(self.url)
    page = requests.get(friends_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    friend_list = soup.find('div', {'class', 'friends_content'})
    return friend_list
  
  def get_friends(self, number=None):
    friend_list = self.friendlist.find_all('div', {'class': 'persona'})

    nb_friends = len(friend_list) if number == None or number > len(friend_list) else number

    output = "Friend list {0}/{1}:\n".format(nb_friends, len(friend_list))
    for i in range(nb_friends):
      friend = friend_list[i]
      friend_username = friend.find('div', {'class': 'friend_block_content'}).find_next(string=True)

      friend_link = friend.find('a', {'class': 'selectable_overlay'}).get("href")
      friend_link_text = re.search(r'https://steamcommunity.com/(id|profiles)/(\w+)', friend_link)
      friend_link_id = "/{0}/{1}".format(friend_link_text.group(1), friend_link_text.group(2))
      friend_steamid = friend.get("data-steamid")

      output += "Username: {0} | Steam link: {1} | Steam ID: {2}\n".format(friend_username, friend_link_id, friend_steamid)

    print(output)

  # Groups
  
  def get_groups(self, number=None):
    group_list = self.profile_data["groups"]["group"]

    nb_groups = len(group_list) if number == None or number > len(group_list) else number

    output = "Groups: ({0}/{1}):\n".format(nb_groups, len(group_list))
    for i in range(nb_groups):
      group = group_list[i]
      is_primary = True if group["@isPrimary"] == "1" else False
      output += "- Name: {0} | Link: /{1} | {2} Member(s) | Primary: {3}\n".format(group["groupName"], group["groupURL"], group["memberCount"], "Yes" if is_primary else "No")

    print(output)

if __name__ == "__main__":
  steamint = Steamint(username)
  steamint.get_actual_persona()
  steamint.get_persona_history()
  steamint.get_real_name()
  steamint.get_location()
  steamint.get_level()
  steamint.get_status()
  steamint.get_ban_info()
  steamint.get_games(5)
  #steamint.get_description()
  steamint.get_friends(5)
  steamint.get_groups(3)
