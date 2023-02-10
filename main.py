#!/usr/bin/env python3

from bs4 import BeautifulSoup
import argparse
import requests
import re
import json
from datetime import datetime

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
    self.gamespage = self.get_games_page()

  # Profile

  def get_mainpage(self):
    page = requests.get(self.url)
    soup = BeautifulSoup(page.text, 'html.parser')
    user_content = soup.find('div', {"id": "responsive_page_template_content"}) 
    return user_content 

  def get_actual_persona(self):
    persona_name = self.mainpage.find('span', {"class", "actual_persona_name"}).text
    print("Actual persona name: {}".format(persona_name))
  
  def get_persona_history(self):
    persona_history_url = self.url + "/ajaxaliases"
    history_request = requests.get(persona_history_url)
    persona_history = history_request.json()

    output = "Persona history: \n"
    for history in persona_history:
      output += "- {0} changed the: {1} \n".format(history["newname"], history["timechanged"])

    print(output)

  def get_real_name(self):
    real_name = self.mainpage.find('div', {"div", "header_real_name"}).find('bdi').text
    print("Real name: {}".format(real_name.strip()))

  def get_location(self):
    location = self.mainpage.find('img', {'class': 'profile_flag'}).find_next(string=True)
    print("Location: {}".format(location.strip()))
  
  def get_description(self):
    description = self.mainpage.find('div', {"class": "profile_summary"}).text
    print("Profile description: {}".format(description))

  def get_level(self):
    level = self.mainpage.find('span', {'class': 'friendPlayerLevelNum'}).text
    print("Player level: {}".format(level))

  def get_status(self):
    status = self.mainpage.find('div', {'class': 'profile_in_game_header'}).text
    print("Status: {}".format(status))

  # Games

  def get_games_page(self):
    games_url = self.url + "/games/?tab=all"
    page = requests.get(games_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    content = soup.find('div', {'id': 'responsive_page_template_content'})
    return content

  def get_games(self, number):
    scripts = self.gamespage.find_all("script")

    gamesScript = None
    for script in scripts:
      if script.find_parent() == self.gamespage:
        gamesScript = script.text

    games_text = re.search(r'var rgGames = (.+?);', gamesScript).group(1)
    games = json.loads(games_text)

    output = "Games (top {}): \n".format(number)
    for i in range(number):
      game = games[i]
      last_played = datetime.fromtimestamp(game["last_played"]).date().strftime("%d/%m/%Y")
      output += "- {0} with {1} hours on record. Last time played the: {2}\n".format(game["name"], game["hours_forever"], last_played)

    print(output)

if __name__ == "__main__":
  steamint = Steamint(username)
  #steamint.get_actual_persona()
  #steamint.get_persona_history()
  #steamint.get_real_name()
  #steamint.get_location()
  #steamint.get_level()
  #steamint.get_status()
  steamint.get_games(3)
  #steamint.get_description()
