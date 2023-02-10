#!/usr/bin/env python3

from bs4 import BeautifulSoup
import argparse
import requests


parser = argparse.ArgumentParser(description="Parser")
parser.add_argument('username', type=str, help="Username used to search for data")

args = parser.parse_args()
username = args.username

class Steamint:
    def __init__(self, username):
        self.username = username
        self.url = 'https://steamcommunity.com/id/%s' % username
       
        print("Steamint - Information gathing on steam profiles")
        print("Searching data for %s" % (username))

        self.mainpage = self.get_mainpage()


    def get_mainpage(self):
        page = requests.get(self.url)
        soup = BeautifulSoup(page.text, 'html.parser')
        user_content = soup.find('div', {"id": "responsive_page_template_content"}) 
        return user_content 

    def get_actual_persona(self):
        persona_name = self.mainpage.find('span', {"class", "actual_persona_name"}).text
        print("Actual persona name: %s" % persona_name )
    
    def get_persona_history(self):
        persona_history_url = self.url + "/ajaxaliases"
        history_request = requests.get(persona_history_url)
        persona_history = history_request.json()

        output = "Persona history: \n"
        for history in persona_history:
            output += "- " + history["newname"] + " changed the: " + history["timechanged"] + "\n"

        print(output)

    def get_real_name(self):
        real_name = self.mainpage.find('div', {"div", "header_real_name"}).find('bdi').text
        print("Real name: %s" % real_name.strip())

    def get_location(self):
        location = self.mainpage.find('img', {'class': 'profile_flag'}).find_next(string=True)
        print("Location: %s" % location.strip())
    
    def get_description(self):
        description = self.mainpage.find('div', {"class": "profile_summary"}).text

        print("Profile description: %s" % description)

    def get_level(self):
        level = self.mainpage.find('span', {'class': 'friendPlayerLevelNum'}).text
        print("Player level: %s" % level)

    
if __name__ == "__main__":
    steamint = Steamint(username)
    steamint.get_actual_persona()
    steamint.get_persona_history()
    steamint.get_real_name()
    steamint.get_location()
    steamint.get_location()
    steamint.get_level()
    #steamint.get_description()
