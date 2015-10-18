#!/usr/bin/python

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser


# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
# https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "API_KEY"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Call the API's commentThreads.list method to list the existing comment threads.
def get_comment_threads(video_id):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    results = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        textFormat="plainText"
    ).execute()

    for item in results["items"]:
        comment = item["snippet"]["topLevelComment"]
        author = comment["snippet"]["authorDisplayName"]
        text = comment["snippet"]["textDisplay"]
        authorChannelId = comment["snippet"]["authorChannelId"]["value"]
        print "Comment by %s(%s): %s" % (author, authorChannelId, text)

    return results["items"]


def get_commentators_channels_id(options):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    results = youtube.commentThreads().list(
        part="snippet",
        videoId=options.video_id,
        maxResults=options.max_results,
        textFormat="plainText"
    ).execute()

    commentators_ids = []

    for item in results["items"]:
        comment = item["snippet"]["topLevelComment"]
        text = comment["snippet"]["textDisplay"]
        authorChannelId = comment["snippet"]["authorChannelId"]["value"]
        commentators_ids.append(authorChannelId)
        print "Video id: %s commentator: %s (%s)" % (options.video_id, authorChannelId, text)

    return commentators_ids


if __name__ == "__main__":
    argparser.add_argument("--max-results", help="Max results", default=25)
    argparser.add_argument("--video-id", help="Video id", default="S43DzgZ1mns")
    args = argparser.parse_args()

    try:
        get_commentators_channels_id(args)
    except HttpError, e:
        print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)

