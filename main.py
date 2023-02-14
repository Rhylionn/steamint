#!/usr/bin/env python3

from bs4 import BeautifulSoup
import argparse
import requests
import re
import json
from datetime import datetime
import xmltodict

parser = argparse.ArgumentParser(description="Parser")
parser.add_argument('--username', '-u', type=str, help="Username used to search for data")
parser.add_argument('--steamid', '-s', type=str, help="Steamid used to search for data")

args = parser.parse_args()

username = args.username
steamid = args.steamid

class Steamint:
  def __init__(self, username=None, steamid=None):
    self.url = 'https://steamcommunity.com'

    self.username = username
    self.steamid = steamid

    if username != None:
      self.path = '/id/{}'.format(self.username)
    elif steamid != None:
      self.path = '/profiles/{}'.format(self.steamid)
    else:
      print("Plese enter either a username or a steamid")
      exit()
    
    self.url += self.path

    print("Steamint - Information gathing on steam profiles")
    print("Searching data for {}".format(self.username if username != None else self.steamid))
    
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

      output += "- Username: {0} | Steam link: {1} | Steam ID: {2}\n".format(friend_username, friend_link_id, friend_steamid)

    print(output)

  # Groups

  def get_groups(self, max_output=2):
    groups_url = "{}/groups".format(self.url)
    page = requests.get(groups_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    
    groups_html = soup.find('div', {'id': 'groups_list'}).find_all('div', {'class': 'group_block'})

    if len(groups_html) == 0:
      output = "No groups or private."
    else:
      max_output = len(groups_html) if max_output > len(groups_html) else max_output

      output = "Groups ({0}/{1}):\n".format(max_output, len(groups_html))
      for i in range(max_output):
        group = groups_html[i]
        group_link_element = group.find('a', {'class': 'linkTitle'})
        group_name = group_link_element.text
        group_link = group_link_element.get("href").split("/")[-1]

        group_public = True if group.find('span', {'class': 'pubGroup'}) != None else False

        group_membercount = group.find('a', {'class': 'groupMemberStat'}).text.split()[0]

        output += "- Name: {0} | Link: {1} | Visibility: {2} | {3} Member(s)\n".format(group_name, group_link, "Public" if group_public else "Private", group_membercount)

    print(output)

  # Comments

  def get_comments(self, number=None): 
    comments_url = "https://steamcommunity.com/comment/Profile/render/{}/-1/?start=0&count=500".format(self.profile_data["steamID64"])
    headers = {'Accept': 'application/json'}
    page = requests.get(comments_url, headers=headers)

    data = page.json()
    total_comments = data["total_count"]
    html_data = BeautifulSoup(data['comments_html'], 'html.parser')
    comments = html_data.find_all('div', {'class': 'commentthread_comment'})
    
    nb_comments = len(comments) if number == None or number > len(comments) else number

    output = "Comments: ({0}/{1}) - {2} total\n".format(nb_comments, len(comments), total_comments)

    for i in range(nb_comments):
      comment = comments[i]
      comment_sender = comment.find('bdi').text

      comment_timestamp = int(comment.find('span', {'class': 'commentthread_comment_timestamp'}).get("data-timestamp"))
      comment_time = datetime.fromtimestamp(comment_timestamp).strftime("%d/%m/%Y - %H:%M:%S")

      comment_content = comment.find('div', {'class': 'commentthread_comment_text'}).text

      output += "- Sender: {0} | Time: {1} | Content: {2} \n".format(comment_sender, comment_time, comment_content.strip())

    print(output)

  def get_wishlist(self, number=None):
    wishlist_url = "https://store.steampowered.com/wishlist/{}/wishlistdata".format(self.path)
    headers = {'Accept': 'application/json'}
    wishlist_request = requests.get(wishlist_url, headers=headers)
    wishlist_data = wishlist_request.json()

    wishlist = [wishlist_data[identifier] for identifier in wishlist_data]
    sorted_wishlist = sorted(wishlist, key=lambda x: int(x["added"]), reverse=True)

    nb_games = len(sorted_wishlist) if number == None or number > len(sorted_wishlist) else number

    output = "Wishlist: ({0}/{1})\n".format(nb_games, len(sorted_wishlist))
    for i in range(nb_games):
      game_name = sorted_wishlist[i]["name"]
      game_addedon_timestamp = int(sorted_wishlist[i]["added"])
      game_addedon = datetime.fromtimestamp(game_addedon_timestamp).strftime("%d/%m/%Y - %H:%M:%S")

      output += "- Game: {0} | Added the: {1}\n".format(game_name, game_addedon)
    
    print(output)

if __name__ == "__main__":

  steamint = Steamint(username=username, steamid=steamid)

  # steamint.get_actual_persona()
  # steamint.get_persona_history()
  # steamint.get_real_name()
  # steamint.get_location()
  # steamint.get_level()
  # steamint.get_status()
  # steamint.get_privacystate()
  # steamint.get_membership_duration()
  # steamint.get_ban_info()
  # steamint.get_games(5)
  #steamint.get_description()
  # steamint.get_friends(5)
  steamint.get_groups(6)
  # steamint.get_comments(5)
  # steamint.get_wishlist(4)
