# !/usr/bin/python

from __future__ import print_function
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import mysql.connector
from mysql.connector import errorcode
from time import sleep
from httplib import BadStatusLine
from time import strftime
import codecs


# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyC_yFHSNjox4-pcCKubIZEb1wmy84Af980"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

MAX_RESULTS = 50
err_log = None
out_log = None

config = {
    'user': 'root',
    'password': 'root',
    'host': '127.0.0.1',
    'database': 'youtube'
}

try:
    cnx = mysql.connector.connect(**config)
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)

cursor = cnx.cursor()


def get_channel_id_for_name(options):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    next_page_token = ''

    while next_page_token is not None:
        results = youtube.channels().list(
            part="id",
            forUsername=options.for_username,
            pageToken=next_page_token
        ).execute()

        for item in results["items"]:
            channel_id = item["id"]
            print(channel_id)

        if results['nextPageToken'] is not None:
            next_page_token = results['nextPageToken']


def get_video_info_for_id(video_id):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    results = youtube.videos().list(
        id=video_id,
        part='id,snippet,statistics',
    ).execute()

    for item in results['items']:
        video_id = item['id']
        channel_id = item['snippet']['channelId']
        title = item['snippet']['title']
        published_at = item['snippet']['publishedAt']
        description = item['snippet']['description']
        stats = item['statistics']

        log ("VIDEO INFO: videoId: %s; channelId: %s; title: %s; publishedAt: %s; \ndescription: %s; \nstats: %s" % (
            video_id, channel_id, title, published_at, description, stats))

        # save to DB
        add_video = ("INSERT INTO video "
                     "(video_id, channel_id, title, published_at, description) "
                     "VALUES (%s, %s, %s, %s, %s)")
        data_video = (video_id, channel_id, title, published_at, description)
        cursor.execute(add_video, data_video)
        # save stats
        add_video_stats = ("INSERT INTO video_statistics "
                           "(video_id, view_count, like_count, dislike_count, favourite_count, comment_count) "
                           "VALUES (%s, %s, %s, %s, %s, %s)")
        data_video_stats = (
        video_id, stats['viewCount'], stats['likeCount'], stats['dislikeCount'], stats['favoriteCount'],
        stats['commentCount'])
        cursor.execute(add_video_stats, data_video_stats)
        cnx.commit()
    return results


def get_channel_info(options):
    if options.level <= 0:
        return

    print ("Starting from channel with id: %s", options.id)

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    next_page_token = ''

    while next_page_token is not None:
        results = youtube.channels().list(
            part="snippet,statistics,status,contentDetails",
            id=options.id,
            pageToken=next_page_token
        ).execute()

        for item in results["items"]:
            title = item["snippet"]["title"]
            description = item["snippet"]["description"]
            published_at = item["snippet"]["publishedAt"]
            country = item["snippet"].get("country")
            stats = item["statistics"]

            log ("CHANNEL INFO: title: %s; desc: %s; publAt: %s; country %s; \nstats: %s" % (
                title, description, published_at, country, stats))

            if not channel_already_in_db(options.id):
                # save to DB
                add_channel = ("INSERT INTO channel "
                               "(channel_id, title, description, published_at, country) "
                               "VALUES (%s, %s, %s, %s, %s)")
                data_channel = (options.id, title, description, published_at, country)
                cursor.execute(add_channel, data_channel)
                # save stats
                add_channel_stats = ("INSERT INTO channel_statistics "
                                     "(channel_id, view_count, comment_count, subscriber_count, hidden_subscriber_count, video_count) "
                                     "VALUES (%s, %s, %s, %s, %s, %s)")
                data_channel_stats = (options.id, stats['viewCount'], stats['commentCount'], stats['subscriberCount'],
                                      stats['hiddenSubscriberCount'], stats['videoCount'])
                cursor.execute(add_channel_stats, data_channel_stats)
                cnx.commit()

            uploaded_videos = item["contentDetails"]["relatedPlaylists"]["uploads"]
            log ("Uploaded videos - id of the playlist: %s" % uploaded_videos)
            try:
                get_playlist_items(uploaded_videos)
            except BadStatusLine, e:
                error ("BadStatusLine ocurred while calling get_playlist_items(%s)" % (uploaded_videos))


        next_page_token = results.get('nextPageToken')


def get_playlist_items(playlist_id):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    next_page_token = ''

    while next_page_token is not None:
        results = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            pageToken=next_page_token,
            maxResults=MAX_RESULTS
        ).execute()

        for item in results["items"]:
            video_id = item["contentDetails"]["videoId"]
            log ("VIDEO_ID: %s" % video_id)
            options = {'video_id': video_id}

            get_video_info_for_id(video_id)
            try:
                get_commentators_channels_id(options)
                sleep(1)
            except HttpError, e:
                error ("Video %s omitted due to an HTTP error" % (video_id))

        next_page_token = results.get('nextPageToken')


def get_commentators_channels_id(options):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    next_page_token = ''
    commentators_ids = []

    while next_page_token is not None:
        results = youtube.commentThreads().list(
            part="snippet",
            videoId=options['video_id'],
            textFormat="plainText",
            pageToken=next_page_token,
            maxResults=MAX_RESULTS
        ).execute()

        for item in results["items"]:
            comment_id = item['id']
            channel_id = item['snippet']['channelId']
            video_id = item['snippet'].get(
                'videoId')  # if the comments refer to the channel itself, the snippet.videoId property will not have a value
            total_reply_count = item['snippet'][
                'totalReplyCount']  # The total number of replies that have been submitted in response to the top-level comment.
            comment = item["snippet"]["topLevelComment"]
            text = comment["snippet"]["textDisplay"]
            authorChannelId = comment["snippet"].get("authorChannelId")
            if authorChannelId is not None:
                authorChannelIdValue = authorChannelId.get('value')
            else:
                authorChannelIdValue = None
            parent_id = comment.get('parentId')
            like_count = comment['snippet']['likeCount']
            published_at = comment['snippet']['publishedAt']

            log ("COMMENT INFO: commentId: %s; channelId: %s; " \
                  "videoId: %s; authorChannelId: %s; totalReplyCount: %s; likeCount: %s; publishedAt: %s; \ntext: %s" \
                  % (
                      comment_id, channel_id, video_id, authorChannelIdValue, total_reply_count, like_count,
                      published_at,
                      text))

            if authorChannelIdValue is not None:
                if not channel_already_in_db(authorChannelIdValue):
                    fetch_channel_info(authorChannelIdValue)
                    sleep(0.005)

                add_comment = ("INSERT INTO comment "
                               "(comment_id, author_channel_id, channel_id, video_id, text, total_reply_count, like_count, published_at) "
                               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ")
                data_comment = (
                comment_id, authorChannelIdValue, channel_id, options['video_id'], text, total_reply_count, like_count, published_at)
                try:
                    cursor.execute(add_comment, data_comment)
                except mysql.connector.errors.IntegrityError, e:
                    error ("An IntegrityError:\n%s\nchannel_id: %s, author_channel_id: %s" % (e, channel_id, authorChannelIdValue))
                cnx.commit()

                commentators_ids.append(authorChannelIdValue)

                sleep(0.001)

        next_page_token = results.get('nextPageToken')

    return commentators_ids


# this method do not call get_playlist_items(uploaded_videos), only fetch info and save to db
def fetch_channel_info(channel_id):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    results = youtube.channels().list(
        part="snippet,statistics,status,contentDetails",
        id=channel_id
    ).execute()

    for item in results["items"]:
        title = item["snippet"]["title"]
        description = item["snippet"]["description"]
        published_at = item["snippet"]["publishedAt"]
        country = item["snippet"].get("country")
        stats = item["statistics"]

        # TODO: save this to db (channel table + channel_statistics)
        print ("CHANNEL INFO: title: %s; desc: %s; publAt: %s; country %s; \nstats: %s" % (
            title, description, published_at, country, stats))

        # save to DB
        add_channel = ("INSERT INTO channel "
                       "(channel_id, title, description, published_at, country) "
                       "VALUES (%s, %s, %s, %s, %s)")
        data_channel = (channel_id, title, description, published_at, country)
        cursor.execute(add_channel, data_channel)
        # save stats
        add_channel_stats = ("INSERT INTO channel_statistics "
                             "(channel_id, view_count, comment_count, subscriber_count, hidden_subscriber_count, video_count) "
                             "VALUES (%s, %s, %s, %s, %s, %s)")
        data_channel_stats = (
        channel_id, stats['viewCount'], stats['commentCount'], stats['subscriberCount'], stats['hiddenSubscriberCount'],
        stats['videoCount'])
        cursor.execute(add_channel_stats, data_channel_stats)
        cnx.commit()

        uploaded_videos = item["contentDetails"]["relatedPlaylists"]["uploads"]

def channel_already_in_db(channel_id):
    cursor = cnx.cursor()
    query = ("SELECT 1 FROM youtube.channel WHERE channel.channel_id = '" + channel_id + "'")
    cursor.execute(query, params=None)

    res = cursor._fetch_row()
    cursor.close()

    return res != None

def association_already_in_db(commented_id, commentator_id):
    cursor = cnx.cursor()
    query = ("SELECT 1 FROM youtube.comment WHERE comment.channel_id = '" + commented_id + "' and comment.author_channel_id = '" + commentator_id + "'")
    cursor.execute(query, params=None)

    res = cursor._fetch_row()
    cursor.close()

    return res != None

def error(message):
    print(format(strftime('%H:%M:%S')), ':', message, file=err_log)

def log(message):
    print(message, file=out_log)


if __name__ == "__main__":
    argparser.add_argument("--max-results", help="Max results", default=25)
    argparser.add_argument("--for-username", help="For Username", default="phuckmediocrity")
    argparser.add_argument("--id", help="Id", default="UCXLesGEfmyhxqOjoAqhRwhA")
    argparser.add_argument("--level", help="Max level of search", default=1)
    args = argparser.parse_args()

    try:
        cnx = mysql.connector.connect(**config)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            error ("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            error ("Database does not exist")
        else:
            error (err)

    cursor = cnx.cursor()

    err_log = codecs.open('err.log', 'w+', "utf-8")
    out_log = codecs.open('out.log', 'w+', "utf-8")

    try:
        get_channel_info(args)
        cursor.close()
        cnx.close()
        # get_channel_id_for_name(args)
    except HttpError, e:
        print ("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
