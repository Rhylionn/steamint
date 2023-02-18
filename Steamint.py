from bs4 import BeautifulSoup
import requests
import re
import json
from datetime import datetime
import xmltodict
from Colors import Colors
import os

class Steamint:
  def __init__(self, user, is_steamid=False):
    self.url = 'https://steamcommunity.com'

    self.user = user

    self.path = '/profiles/{}'.format(self.user) if is_steamid else '/id/{}'.format(self.user)
    
    self.url += self.path

    print("Searching data for: {}".format(Colors.ORANGE + self.user + Colors.EOL))

    if self.exists():
      self.profile_data = self.get_xml_mainpage()["profile"]
      self.mainpage = self.get_mainpage()
      self.gamespage = self.get_games_page()
      self.friendlist = self.get_friendlist_page()
    else:
      print(Colors.RED + Colors.BOLD + "Profile does not exists" + Colors.EOL)

      if self.user.isnumeric() and len(self.user) == 17 and not is_steamid:
        print(Colors.RED + Colors.BOLD + "The user you entered seems to be a SteamID. If so, please use the -s flag." + Colors.EOL)
      elif not self.user.isnumeric() and len(self.user) != 17 and is_steamid:
        print(Colors.RED + Colors.BOLD + "The user you entered does not seems to be a SteamID. Try without -s flag." + Colors.EOL)

      exit()

    self.output_directory = self.make_output_dir()

    self.output_dict = {
      "profileUrl": self.url,
    }

  # Profile

  def get_mainpage(self):
    request = requests.get(self.url)
    html = BeautifulSoup(request.text, 'html.parser')
    user_content = html.find('div', {"id": "responsive_page_template_content"}) 
    return user_content 

  def exists(self):
    xml_mainpage = self.get_xml_mainpage()
    if "response" in xml_mainpage and "error" in xml_mainpage["response"]:
      return False
    else:
      return True

  def get_xml_mainpage(self):
    xml_page_url = "{}/?xml=1".format(self.url)
    xml_page = requests.get(xml_page_url)
    profile_data = xmltodict.parse(xml_page.text)

    return profile_data
  
  def get_privacystate(self):
    privacy_state = self.profile_data["privacyState"]
    output = "Privacy state: {}".format(Colors.ORANGE + privacy_state + Colors.EOL)

    self.output_dict["privacyState"] = privacy_state
    print(output)

  def get_actual_persona(self):
    persona = self.profile_data["steamID"]
    output = "Actual persona: {}".format(Colors.ORANGE + persona + Colors.EOL)

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

      output += "- {0} changed the: {1} \n".format(Colors.ORANGE + name + Colors.END, Colors.ORANGE + timechanged + Colors.END)

    print(output)

  def get_real_name(self):
    real_name = self.profile_data["realname"] or None
    output = "Real name: {}".format(Colors.ORANGE + str(real_name) + Colors.EOL)

    self.output_dict["realName"] = real_name
    print(output)

  def get_location(self):
    location = self.profile_data["location"] or None
    output = "Location: {}".format(Colors.ORANGE + location + Colors.EOL)

    self.output_dict["location"] = location
    print(output)
  
  def get_description(self):
    description = self.mainpage.find('div', {"class": "profile_summary"}).text.strip()
    output = "Profile description: {}\n".format(description)

    self.output_dict["description"] = description
    print(output)

  def get_level(self):
    level = int(self.mainpage.find('span', {'class': 'friendPlayerLevelNum'}).text.strip())
    output = "Player level: {}".format(Colors.ORANGE + str(level) + Colors.EOL)

    self.output_dict["level"] = level

    print(output)

  def get_status(self):
    current_status = self.profile_data["stateMessage"]
    output = "Current status: {}".format(Colors.ORANGE + current_status + Colors.EOL)

    self.output_dict["currentStatus"] = current_status

    print(output)

  def get_membership_duration(self):
    member_since = self.profile_data["memberSince"]
    output = "Member since: {}".format(Colors.ORANGE + member_since + Colors.EOL)

    self.output_dict["memberDuration"] = member_since

    print(output)

  def get_ban_info(self):
    is_vacban = False if self.profile_data["vacBanned"] == '0' else True
    is_tradeban = False if self.profile_data["tradeBanState"] == 'None' else True
    is_limited = False if self.profile_data["isLimitedAccount"] == '0' else True
    output = ""
    output = "Ban informations:\n \t- VAC Ban: {0}\n\t- Trade Ban: {1}\n\t- Limited account: {2}\n".format(Colors.ORANGE + str(is_vacban) + Colors.END, Colors.ORANGE + str(is_tradeban) + Colors.END, Colors.ORANGE + str(is_limited) + Colors.END)

    self.output_dict["banInfo"] = {
      "vacBanned": is_vacban,
      "tradeBanned": is_tradeban,
      "limited": is_limited
    }

    print(output)

  def get_profile_picture(self):
    img_link = self.mainpage.find('div', {'class': 'playerAvatar'}).find_all('img')[1].get("src")
    res = requests.get(img_link)

    output_path = self.output_directory + "/profile_picture.jpg"

    if res.status_code == 200:
      with open(output_path, "wb") as file:
        file.write(res.content)

    print(Colors.ORANGE + "Profile picture saved..." + Colors.EOL)

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

      output += "\t- {0} with {1} hours on record. Last time played: {2}\n".format(Colors.ORANGE + game_name + Colors.END, Colors.ORANGE + str(game_hourplayed) + Colors.END, Colors.ORANGE + last_played + Colors.END)

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

    if len(friend_list) == 0:
      output = Colors.ORANGE + "No friends or private" + Colors.EOL
    else:
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

        output += "\t- Username: {0} | Profile link: {1} | Steam ID: {2}\n".format(Colors.ORANGE + friend_username + Colors.END, Colors.ORANGE + friend_link_id + Colors.END, Colors.ORANGE + friend_steamid + Colors.END)
  
    print(output)

  # Groups

  def get_groups(self, max_output=2):
    groups_url = "{}/groups".format(self.url)
    page = requests.get(groups_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    
    groups_html = soup.find('div', {'id': 'groups_list'}).find_all('div', {'class': 'group_block'})

    self.output_dict["groupList"] = []

    if len(groups_html) == 0:
      output = Colors.ORANGE + "No groups or private." + Colors.EOL
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

        output += "\t- Name: {0} | Link: {1} | Visibility: {2} | {3} Member(s)\n".format(Colors.ORANGE + group_name + Colors.END, Colors.ORANGE + group_link + Colors.END, Colors.ORANGE + group_visibility + Colors.END, Colors.ORANGE + str(group_membercount) + Colors.END)

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

    if total_comments == 0:
      output = Colors.ORANGE + "No comments or private." + Colors.EOL
    else:
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

        output += "\t- Sender: {0} | Time: {1} | Content: {2} \n".format(Colors.ORANGE + comment_sender + Colors.END, Colors.ORANGE + comment_time + Colors.END, Colors.ORANGE + comment_content.strip() + Colors.END)

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

      output += "\t- Game: {0} | Added the: {1}\n".format(Colors.ORANGE + game_name + Colors.END, Colors.ORANGE + game_addedon + Colors.END)
    
    print(output)

  # Output json

  def json_output(self):
    json_data = json.dumps(self.output_dict)
    output_path = self.output_directory + "/profile_data.json"

    with open(output_path, "w") as outfile:
      outfile.write(json_data)

      print(Colors.ORANGE + "File saved in: " + output_path + Colors.EOL)

  def make_output_dir(self):
    output_name = "steamint_" + self.profile_data["steamID64"]
    if not os.path.exists(output_name):
      os.makedirs(output_name, exist_ok=True)
      
    return output_name