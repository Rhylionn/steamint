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

    self.output_dict = {
      "profileUrl": self.url,
    }

  # Profile

  def get_mainpage(self):
    request = requests.get(self.url)
    html = BeautifulSoup(request.text, 'html.parser')
    user_content = html.find('div', {"id": "responsive_page_template_content"}) 
    return user_content 

  def get_xml_mainpage(self):
    xml_page_url = "{}/?xml=1".format(self.url)
    xml_page = requests.get(xml_page_url)
    profile_data = xmltodict.parse(xml_page.text)
    return profile_data["profile"]
  
  def get_privacystate(self):
    privacy_state = self.profile_data["privacyState"]
    output = "Privacy state: {}".format(privacy_state)

    self.output_dict["privacyState"] = privacy_state
    print(output)

  def get_actual_persona(self):
    persona = self.profile_data["steamID"]
    output = "Actual persona: {}".format(persona)

    self.output_dict["persona"] = persona
    print(output)

  def get_persona_history(self):
    persona_history_url = self.url + "/ajaxaliases"
    history_request = requests.get(persona_history_url)
    persona_history = history_request.json()

    self.output_dict["personaHistory"] = []
    output = "Persona history: \n"
    for history in persona_history:
      name = history["newname"]
      timechanged = history["timechanged"]

      self.output_dict["personaHistory"].append({"name": name, "timechanged": timechanged})

      output += "- {0} changed the: {1} \n".format(name, timechanged)

    print(output)

  def get_real_name(self):
    real_name = self.profile_data["realname"] or None
    output = "Real name: {}".format(real_name)

    self.output_dict["realName"] = real_name
    print(output)

  def get_location(self):
    location = self.profile_data["location"] or None
    output = "Location: {}".format(location)

    self.output_dict["location"] = location
    print(output)
  
  def get_description(self):
    description = self.mainpage.find('div', {"class": "profile_summary"}).text.strip()
    output = "Profile description: {}".format(description)

    self.output_dict["description"] = description
    print(output)

  def get_level(self):
    level = int(self.mainpage.find('span', {'class': 'friendPlayerLevelNum'}).text.strip())
    output = "Player level: {}".format(level)

    self.output_dict["level"] = level

    print(output)

  def get_status(self):
    current_status = self.profile_data["stateMessage"]
    output = "Current status: {}".format(current_status)

    self.output_dict["currentStatus"] = current_status

    print(output)

  def get_membership_duration(self):
    member_since = self.profile_data["memberSince"]
    output = "Member since: {}".format(member_since)

    self.output_dict["memberDuration"] = member_since

    print(output)

  def get_ban_info(self):
    is_vacban = False if self.profile_data["vacBanned"] == '0' else True
    is_tradeban = False if self.profile_data["tradeBanState"] == 'None' else True
    is_limited = False if self.profile_data["isLimitedAccount"] == '0' else True
    output = "VAC Ban: {0} | Trade Ban: {1} | Limited account: {2}".format(is_vacban, is_tradeban, is_limited)

    self.output_dict["banInfo"] = {
      "vacBanned": is_vacban,
      "tradeBanned": is_tradeban,
      "limited": is_limited
    }

    print(output)

  # Games

  def get_games_page(self):
    games_url = "{}/games/?tab=all".format(self.url)
    request = requests.get(games_url)
    html = BeautifulSoup(request.text, 'html.parser')
    content = html.find('div', {'id': 'responsive_page_template_content'})
    return content

  def get_games(self, max_output=5):
    scripts = self.gamespage.find_all("script")

    games_script = None
    for script in scripts:
      if script.find_parent() == self.gamespage:
        games_script = script.text

    games_text = re.search(r'var rgGames = (.+?);', games_script).group(1)
    games = json.loads(games_text)

    max_output = len(games) if max_output > len(games) else max_output

    self.output_dict["ownedGames"] = []

    output = "Games ({0}/{1}): \n".format(max_output, len(games))
    for i in range(max_output):
      game = games[i]
      game_name = game["name"]
      game_hourplayed = int(game["hours_forever"].replace(",", ""))
      last_played = datetime.fromtimestamp(game["last_played"]).strftime("%d/%m/%Y - %H:%M:%S")

      self.output_dict["ownedGames"].append({
        "name": game_name,
        "totalPlayed": game_hourplayed,
        "lastPlayed": last_played
      })

      output += "- {0} with {1} hours on record. Last time played the: {2}\n".format(game_name, game_hourplayed, last_played)

    print(output)

  # Friends

  def get_friendlist_page(self):
    friends_url = "{}/friends".format(self.url)
    request = requests.get(friends_url)
    html = BeautifulSoup(request.text, 'html.parser')
    friend_list = html.find('div', {'class', 'friends_content'})
    return friend_list
  
  def get_friends(self, max_output=5):
    friend_list = self.friendlist.find_all('div', {'class': 'persona'})

    max_output = len(friend_list) if max_output > len(friend_list) else max_output

    self.output_dict["friendsList"] = []

    output = "Friend list ({0}/{1}):\n".format(max_output, len(friend_list))
    for i in range(max_output):
      friend = friend_list[i]
      friend_username = friend.find('div', {'class': 'friend_block_content'}).find_next(string=True).strip()

      friend_link = friend.find('a', {'class': 'selectable_overlay'}).get("href")
      friend_link_text = re.search(r'https://steamcommunity.com/(id|profiles)/(\w+)', friend_link)
      friend_link_id = "/{0}/{1}".format(friend_link_text.group(1), friend_link_text.group(2))
      friend_steamid = friend.get("data-steamid")

      self.output_dict["friendsList"].append({
        "username": friend_username,
        "link": friend_link_id,
        "steamId": friend_steamid
      })

      output += "- Username: {0} | Steam link: {1} | Steam ID: {2}\n".format(friend_username, friend_link_id, friend_steamid)

    print(output)

  # Groups

  def get_groups(self, max_output=2):
    groups_url = "{}/groups".format(self.url)
    page = requests.get(groups_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    
    groups_html = soup.find('div', {'id': 'groups_list'}).find_all('div', {'class': 'group_block'})

    self.output_dict["groupList"] = []

    if len(groups_html) == 0:
      output = "No groups or private."
    else:
      max_output = len(groups_html) if max_output > len(groups_html) else max_output

      output = "Groups ({0}/{1}):\n".format(max_output, len(groups_html))
      for i in range(max_output):
        group = groups_html[i]
        group_link_element = group.find('a', {'class': 'linkTitle'})
        group_name = group_link_element.text.strip()
        group_link = group_link_element.get("href").split("/")[-1]

        group_visibility = "Public" if group.find('span', {'class': 'pubGroup'}) != None else "Private"

        group_membercount_element = group.find('a', {'class': 'groupMemberStat'})
        group_membercount = int(group_membercount_element.text.split()[0].strip().replace(",", ""))

        self.output_dict["groupList"].append({
          "name": group_name,
          "link": group_link,
          "visibility": group_visibility,
          "memberCount": group_membercount
        })

        output += "- Name: {0} | Link: {1} | Visibility: {2} | {3} Member(s)\n".format(group_name, group_link, group_visibility, group_membercount)

    print(output)

  # Comments

  def get_comments(self, max_output=5): 
    comments_url = "https://steamcommunity.com/comment/Profile/render/{}/-1/?start=0&count=500".format(self.profile_data["steamID64"])
    headers = {'Accept': 'application/json'}
    request = requests.get(comments_url, headers=headers)

    data = request.json()
    total_comments = data["total_count"]
    html_data = BeautifulSoup(data['comments_html'], 'html.parser')
    comments = html_data.find_all('div', {'class': 'commentthread_comment'})
    
    max_output = len(comments) if max_output > len(comments) else max_output

    self.output_dict["comments"] = []

    output = "Comments: ({0}/{1}) - {2} total\n".format(max_output, len(comments), total_comments)
    for i in range(max_output):
      comment = comments[i]
      comment_sender = comment.find('bdi').text.strip()

      comment_timestamp = int(comment.find('span', {'class': 'commentthread_comment_timestamp'}).get("data-timestamp"))
      comment_time = datetime.fromtimestamp(comment_timestamp).strftime("%d/%m/%Y - %H:%M:%S")

      comment_content = comment.find('div', {'class': 'commentthread_comment_text'}).text.strip()

      self.output_dict["comments"].append({
        "sender": comment_sender,
        "date": comment_time,
        "content": comment_content
      })

      output += "- Sender: {0} | Time: {1} | Content: {2} \n".format(comment_sender, comment_time, comment_content.strip())

    print(output)

  def get_wishlist(self, max_output=5):
    wishlist_url = "https://store.steampowered.com/wishlist/{}/wishlistdata".format(self.path)
    headers = {'Accept': 'application/json'}
    wishlist_request = requests.get(wishlist_url, headers=headers)
    wishlist_data = wishlist_request.json()

    wishlist = [wishlist_data[identifier] for identifier in wishlist_data]
    sorted_wishlist = sorted(wishlist, key=lambda x: int(x["added"]), reverse=True)

    max_output = len(sorted_wishlist) if max_output > len(sorted_wishlist) else max_output

    self.output_dict["wishlist"] = []

    output = "Wishlist: ({0}/{1})\n".format(max_output, len(sorted_wishlist))
    for i in range(max_output):
      game_name = sorted_wishlist[i]["name"].strip()
      game_addedon_timestamp = int(sorted_wishlist[i]["added"])
      game_addedon = datetime.fromtimestamp(game_addedon_timestamp).strftime("%d/%m/%Y - %H:%M:%S")

      self.output_dict["wishlist"].append({
        "name": game_name,
        "addedOn": game_addedon
      })

      output += "- Game: {0} | Added the: {1}\n".format(game_name, game_addedon)
    
    print(output)

  # Output json

  def json_output(self):
    json_data = json.dumps(self.output_dict)
    output_name = "steamint_{}.json".format(self.profile_data["steamID64"])
    with open(output_name, "w") as outfile:
      outfile.write(json_data)

if __name__ == "__main__":
  steamint = Steamint(username=username, steamid=steamid)

  steamint.get_actual_persona()
  steamint.get_persona_history()
  steamint.get_real_name()
  steamint.get_location()
  steamint.get_level()
  steamint.get_status()
  steamint.get_privacystate()
  steamint.get_membership_duration()
  steamint.get_ban_info()
  steamint.get_games(5)
  steamint.get_description()
  steamint.get_friends(5)
  steamint.get_groups(6)
  steamint.get_comments(5)
  steamint.get_wishlist(4)

  steamint.json_output()
