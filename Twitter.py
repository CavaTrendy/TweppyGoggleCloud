import feedparser
from bs4 import BeautifulSoup
import datetime
from operator import itemgetter
from pyshorteners import Shortener
import os
import csv

API_TINY = os.getenv("API_KEY_TINY")

date_obj = datetime.datetime.now()
s = Shortener(api_key=API_TINY)


class ParseFeed():

    def __init__(self, url):
        self.feed_url = url

    def clean(self, html):
        '''
        Get the text from html and do some cleaning
        '''
        soup = BeautifulSoup(html, features="lxml")
        text = soup.get_text()
        text = text.replace('\xa0', ' ')
        return text

    def parse(self):
        '''
        Parse the URL, and print all the details of the news
        '''
        feeds = feedparser.parse(self.feed_url).entries
        dictionary = {"TITLE": [], "URL": [], "PUBDATE": []}
        for f in feeds:
            dictionary["TITLE"].append(f.get("title", ""))
            dictionary["URL"].append(f.get("link", ""))
            dictionary["PUBDATE"].append(f.get("published", ""))
        new_data = [{"TITLE": s, "URL": t, "PUBDATE": l} for s, t, l in
                    zip(dictionary["TITLE"], dictionary["URL"], dictionary["PUBDATE"])]
        return new_data


class TweetPreparion(ParseFeed):

    def __init__(self, url):
        super().__init__(url)

    def cleaning_link(self):
        ####Look for the right words that i want###
        new_dictionary = {"TITLE": [], "URL": [], "HASHTAG": [], "PUBDATE": []}
        words = ['Agric', 'Agriculture', 'Food', 'AGRIC', 'AGRICULTURE', 'FOOD', 'agric', 'agricultre', 'food',
                 "Blockchain", "blockchain"]
        for data in ParseFeed.parse(self):
            for word in words:
                ####check for the right words that i want###
                if word in data["TITLE"] and data["TITLE"] not in new_dictionary["TITLE"]:
                    ####check for doubles###
                    new_dictionary["TITLE"].append(data["TITLE"])
                    new_dictionary["URL"].append(data["URL"])
                    new_dictionary["PUBDATE"].append(data["PUBDATE"])
                    new_dictionary["HASHTAG"].append("#foodtech #agritech #blockchain #innovation")
        publish_data = sorted([{"TITLE": s, "URL": t, "HASHTAG": l, "PUBDATE": p} for s, t, l, p in
                               zip(new_dictionary["TITLE"], new_dictionary["URL"], new_dictionary["HASHTAG"],
                                   new_dictionary["PUBDATE"])],
                              key=itemgetter('PUBDATE'), reverse=True)
        return publish_data



def twitter_message(title, url, hashtag):
    try:

        print("Creating message for ", title, url, hashtag)
        ####cleaning the . in the title###
        title_clean = title.replace('.', '')
        message = f"{title_clean} at {s.tinyurl.short(url)} {hashtag}"

        if len(title) >= 200:
            ####reducing the the title size###
            title_redux = title_clean[:150]
            message = f"{title_redux} at {s.tinyurl.short(url)} {hashtag}"
        else:
            message
    except ValueError():
        print("error!")
    return message


def twitter_dict(dictionary):
    ####creating the message###
    dict_publish = {"TITLE": []}
    for a in dictionary:
        dict_publish["TITLE"].append(twitter_message(a["TITLE"], a["URL"], a["HASHTAG"]))

    final_publish = [{"TITLE": s} for s in dict_publish["TITLE"]]
    return final_publish


def main_post():
    ####creating the main post###
    feed_food = TweetPreparion(
        "https://news.google.com/rss/search?q=food+blockchain+agriculture+blockchain+when:1d&hl=en-US&gl=US&ceid=US:en")
    link_food = feed_food.cleaning_link()
    post = twitter_dict(link_food)
    return post

# print(main_post())
#####POSTING##########
import tweepy
import time
from decouple import config


####twitter key###
consumer_key = config("CONSUMER_KEY")
consumer_secret = config("CONSUMER_SECRET")
access_token = config("ACCESS_TOKEN")
access_token_secret = config("ACCESS_TOKEN_SECRET")

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
####log in ###
api = tweepy.API(auth)
post = main_post()
####look in the timeline###
time_line = api.user_timeline(screen_name="CavaTrendy", count=10, tweet_mode="extended")
for t in time_line:
    compare = t.full_text
    for item in post:
        print(compare)
        print(item["TITLE"])
        if item["TITLE"][:100] == compare[:100]:
            print("Same")
        else:
            print("Not Same")

# def twitter_message(text):
#     return api.update_status(text)m
#
# def calculate_posting_time(time):11
#     to_time = 0
#     if time in (1, 2, 3, 4):
#         to_time = time * 3000
#     else:
#         to_time = 3000
#     return to_time
#
#
# def main_posting():
#     print(post)
#     while len(post) > 0:
#         print("Still elements? ", len(post))
#         print('Time: ', calculate_posting_time(len(post)))
#         for item in post:
#             print("Still elements? ", len(post))
#             print('Time: ', calculate_posting_time(len(post)))
#             # calculate_posting_time(len(post))
#             posting = twitter_message(item["TITLE"])
#             time.sleep(calculate_posting_time(len(post)))
#             element = post.remove(item)
#             print('The popped element is:', element)
#             print('The dictionary is:', post)
#             print('Time: ', calculate_posting_time(len(post)))
#     if len(post) == 0:
#         print("No Elements ", len(post))
#     return posting