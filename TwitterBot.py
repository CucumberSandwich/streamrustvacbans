import os
import json

import argparse
import requests
import tweepy
import threading

from tweepy import Stream
from tweepy import StreamListener
from urllib.parse import urlparse


headers = {"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
           "(KHTML, like Gecko) Ubuntu Chromium/73.0.3683.86 Chrome/73.0."
           "3683.86 Safari/537.36"}

# API Keys required for Twitter and Steam
consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""
steamkey = ""

filename = "vac_list.txt"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """

    def get_latest(self, value):

        vac_banned = []

        try:
            for tweets in tweepy.Cursor(api.user_timeline,
                                        user_id=3243246400,
                                        tweet_mode="extended",
                                        include_rts=False,
                                        wait_on_rate_limit=True,
                                        wait_on_rate_limit_notify=True).items(value):

                urls = tweets._json['entities']['urls']
                for url in urls:
                    profiles = url['expanded_url']
                    extracted_id = self.extract_id(profiles)
                    vac_banned.append(extracted_id)
        except Exception as error:
            print("Latest fetch:", error)

        saveids = open(os.path.dirname(__file__) + filename, "a")
        for ids in vac_banned:
            saveids.write(ids + '\n')
        saveids.close()

        print("> Bans added:", len(vac_banned))

        file_read = open(os.path.dirname(__file__) + filename, "r")
        lines = file_read.readlines()
        lines = filter(lambda x: not x.isspace(), lines)

        lines_seen = set()
        for line in lines:
            if line not in lines_seen:
                lines_seen.add(line)

        file_read = open(os.path.dirname(__file__) + filename, "w")
        file_read.write("".join(lines_seen))
        file_read.close()

        print("> Bans in file:", len(lines_seen))

    def convert_to_id(self, steam_name):
        steam_id = None
        try:
            url = "http://api.steampowered.com/ISteamUser/"\
                  f"ResolveVanityURL/v0001/?key={steamkey}&"\
                  f"vanityurl={steam_name}"

            resp = requests.get(url, headers=headers)
            steam_id = json.loads(resp.content)['response']['steamid']

        except Exception as httperror:
            print("Error fetching URL:", httperror)
        return steam_id

    def extract_id(self, profile_link):
        steam_id = None
        if "profile" in profile_link:
            steam_id = (urlparse(profile_link).path).strip("profiles\/")

        if "id" in profile_link:
            steam_name = (urlparse(profile_link).path).strip("id\/")
            steam_id = self.convert_to_id(steam_name)
        return steam_id

    def update_file(self, steamID):
        file_read = open(os.path.dirname(__file__) + filename, "r")
        lines = file_read.readlines()
        lines = filter(lambda x: not x.isspace(), lines)

        lines_seen = set()
        lines_seen.add(steamID + '\n')
        for line in lines:
            if line not in lines_seen:
                lines_seen.add(line)

        file_read = open(os.path.dirname(__file__) + filename, "w")
        file_read.write("".join(lines_seen))
        file_read.close()

        print("\n--------\nBan added:", steamID)
        print("Bans in file:", len(lines_seen))
        print("--------")

    def read_add_data(self, tojson):

        profile_link = None

        try:
            profile_link = tojson['entities']['urls'][0]['expanded_url']
        except Exception as a:
            print("URL Failed:", a)

        if profile_link:
            try:
                get_profile_id = self.extract_id(profile_link)
            except Exception as b:
                print("GetID failed:", b)

        try:
            self.update_file(get_profile_id)
            print("Ban process complete, streaming..")
        except:
            print("\nUnable to load tweet data. Running manual fetch\n")
            self.get_latest(20)

    def on_data(self, data):

        tojson = json.loads(data)

        x = threading.Thread(target=self.read_add_data(tojson))
        x.start()

        return True

    def on_error(self, status):
        print(status)

    def first_run(self):
        if not os.path.exists(filename):
            open(filename, 'wb').close()

        if not all([consumer_key,
                   consumer_secret,
                   access_token,
                   access_token_secret,
                   steamkey]):

            print("You need to add your API info for Twitter and Steam")
            quit()


def main(args):

    stdout_listener = StdOutListener()

    stdout_listener.first_run()

    user = api.get_user(screen_name='rusthackreport')

    print("UserName: ", user.name)
    print("UserID: ", user.id)

    if args.stream:
        stream = Stream(auth, stdout_listener)
        stream.filter(follow=['{}'.format(user.id)])
        tweepy.Stream(auth=api, listener=tweepy.StreamListener)

    if args.dupes:
        stdout_listener.get_latest(1000)


def parse_args():
    parser = argparse.ArgumentParser(description='Reads commandline arguments')
    parser.add_argument('--stream', dest="stream", action="store_true",
                        help="Stream twitter account")
    parser.add_argument('--dupes', dest="dupes", action="store_true",
                        help="Get latest tweets and remove dupes from file")
    return parser.parse_args()


if __name__ == '__main__':
    opts = parse_args()
    main(opts)
