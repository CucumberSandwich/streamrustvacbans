# Rust Twitter Vac Stream

## Overview

Small script I created a long while ago, setup as a service on a spare box running centos to gather all Steam IDs posted on twitter.

Excuse the coding, I'm not a developer just an enthusiast. I've never had to make any changes/restart the service so it's never been improved.

## Features

+ Streams the rust hack report twitter account, adding all newly announced Vac bans to a file
+ Manual run to collect the latest, de dupes the list

## Requirements

pip3 install -r requirements.txt

These will need to be filled out inside the TwitterBot.py file at the top.

consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""

Needed to pull the steamID from the profiles posted

steamkey = ""

## Usage

python3 TwitterBot.py --stream // will stream the account
python3 TwitterBot.py --dupes // Will gather latest tweets then dedupe
