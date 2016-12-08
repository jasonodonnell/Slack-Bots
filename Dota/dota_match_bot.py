#!/usr/bin/python

# This bot is for getting live dota games currently being played.
# Since trackdota tracks all games, we are only interested in those in
# the whitelist file.  When a game is live, it sends a message to our
# Slack chat room #dota
from bs4 import BeautifulSoup
import urllib2
import subprocess

slack_hook_url = ''
whitelist_file = './team_whitelist.txt'
trackdota_links_file = './trackdota_links.txt'

with open(whitelist_file, 'r') as f:
    whitelist = f.read().splitlines()

with open(trackdota_links_file, 'a+') as f:
    trackdota_links = f.read().splitlines()

# Get current games from trackdota.com widget
response = urllib2.urlopen('http://www.trackdota.com/data/embed/dark/')
soup = BeautifulSoup(response, 'lxml')

# loop through trackdota games
for li in soup.find_all('li'):
    for game in li.find_all('a'):
        # parse game data we want
        team_radiant = game.find('span', {'class' : 'radiant'}).get_text()
        team_dire = game.find('span', {'class' : 'dire'}).get_text()
        match_url = game.get('href')

        # clean team names
        team_radiant = team_radiant.replace('\'', '').replace('`', '')
        team_dire = team_dire.replace('\'', '').replace('`', '')

        # skip teams not on the white list or that were already sent
        if (team_radiant not in whitelist and team_dire not in whitelist) or match_url in trackdota_links:
            continue

        # write trackdota url to file to check for later
        with open(trackdota_links_file, 'a') as f:
            f.write('%s\n' % match_url)

        # format message to be posted to slack
        slack_message = '%s VS %s :: <%s|Click here> for TrackDota.' % (team_radiant, team_dire, match_url)
        # format slack payload
        slack_payload = 'payload={"channel": "#dota", "username": "brunobot", "text": "%s", "icon_emoji": ":brunoface:"}' % (slack_message)

        # execute curl
        curl_command = 'curl -X POST --data-urlencode \'%s\' \'%s\'' % (slack_payload, slack_hook_url)
        subprocess.call('%s' % curl_command, shell=True)
