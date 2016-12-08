#!/usr/bin/python
# This bot is for getting live dota games currently being played.
# Since trackdota tracks all games, we are only interested in those in
# the whitelist file.  When a game is live, it sends a message to our
# Slack chat room #dota
from bs4 import BeautifulSoup
import urllib2
import subprocess

chat_url = ''
whitelist_dir = './team_whitelist.txt'
trackdota_links_dir = './trackdota_links.txt'

with open(whitelist_dir) as whitelist_file:
    whitelist = whitelist_file.read().splitlines()

with open(trackdota_links_dir) as trackdota_file:
    trackdota_links = trackdota_file.read().splitlines()

# Get current games from trackdota.com widget
response = urllib2.urlopen('http://www.trackdota.com/data/embed/dark/')
soup = BeautifulSoup(response, 'lxml')
links = []
radiant = []
dire = []

# Get all the trackdota links first
for li in soup.find_all('li'):
    for each in li.find_all('a'):
        track_dota_link = each.get('href')
        links.append(track_dota_link)

# Get all the radiant team names
spans = soup.find_all('span', {'class' : 'radiant'})
for span in spans:
    radiant_team = span.get_text()
    radiant.append(radiant_team)

# Get all the dire team names
spans = soup.find_all('span', {'class' : 'dire'})
for span in spans:
    dire_team= span.get_text()
    dire.append(dire_team)

# Since all three lists are 1:1:1, loop on link count, check if its in whitelist
# We don't want the bot to spam our chat so first we check if its already notified the room
# This is done by taking the track dota link and putting it into a file.  Every game has a unique
# trackdota url.
# If all criteria is acceptable, message is finally sent to our chat room.
for i in range(0, len(links)):
    if radiant[i] in whitelist or dire[i] in whitelist:
        if links[i] not in trackdota_links:
            # Construct payload
            radiant_team = radiant[i].replace('\'', '')
            radiant_team = radiant_team.replace('`', '')
            dire_team= dire[i].replace('\'', '')
            dire_team = dire_team.replace('`', '')
            match_string = '%s VS %s :: <%s|Click here> for TrackDota.' % (radiant_team, dire_team, links[i])
            curl_message = 'payload={"channel": "#dota", "username": "brunobot", "text": "%s", "icon_emoji": ":brunoface:"}' % (match_string)

            # Write trackdota url to file to check for later
            f = open(trackdota_links_dir, 'a')
            link = links[i] + '\n'
            f.write(link)
            f.close()

            # Execute curl
            curl_command = 'curl -X POST --data-urlencode \'%s\' %s' % (curl_message, chat_url)
            subprocess.call('%s' % curl_command, shell=True)
