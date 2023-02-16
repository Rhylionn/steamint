#!/usr/bin/env python3

import argparse
from Steamint import Steamint

parser = argparse.ArgumentParser()
parser.add_argument('user', type=str, help="Username used to search for data")
parser.add_argument('--steamid', '-s', action=argparse.BooleanOptionalAction, help="Search will be conducted using steamid")
parser.add_argument('--output', '-o', action=argparse.BooleanOptionalAction, help="Save the result as a json file")

parser.add_argument('--max-games', '-mG', type=int, help="Number of games to be displayed (default 5)")
parser.add_argument('--max-friends', '-mF', type=int, help="Number of friends to be displayed (default 5)")
parser.add_argument('--max-groups', '-mT', type=int, help="Number of groups to be displayed (default 3)")
parser.add_argument('--max-comments', '-mC', type=int, help="Number of comments to be displayed (default 5)")
parser.add_argument('--max-wishlist', '-mW', type=int, help="Number of wishlist games to be displayed (default 5)")


args = parser.parse_args()


if __name__ == "__main__":
  user = args.user
  output = args.output

  print(args.max_games)

  steamint = Steamint(user=args.user, is_steamid=args.steamid)

  steamint.get_actual_persona()
  steamint.get_persona_history()
  steamint.get_real_name()
  steamint.get_location()
  steamint.get_level()
  steamint.get_status()
  steamint.get_privacystate()
  steamint.get_membership_duration()
  steamint.get_ban_info()

  steamint.get_games(args.max_games or 5)

  steamint.get_description()
  steamint.get_friends(args.max_friends or 5)
  steamint.get_groups(args.max_groups or 3)
  steamint.get_comments(args.max_comments or 5)
  steamint.get_wishlist(args.max_wishlist or 5)

  if output:
    steamint.json_output()
