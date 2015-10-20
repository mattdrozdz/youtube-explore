# !/usr/bin/python

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser


# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyC_yFHSNjox4-pcCKubIZEb1wmy84Af980"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def get_channel_info(options):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    results = youtube.channels().list(
        part="snippet,statistics,status,contentDetails",
        id=options.id,
        maxResults=options.max_results
    ).execute()

    for item in results["items"]:
        title = item["snippet"]["title"]
        uploaded_videos = item["contentDetails"]["relatedPlaylists"]["uploads"]
        print "Uploaded videos - id of the playlist: %s" % (uploaded_videos)
        get_playlist_items(uploaded_videos)


def get_playlist_items(playlist_id):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    results = youtube.playlistItems().list(
        part="snippet,status,contentDetails",
        playlistId=playlist_id
    ).execute()

    for item in results["items"]:
        video_id = item["contentDetails"]["videoId"]
        print "Video Id %s" % video_id
        options = {'video_id': video_id, 'max_results': 25}

        get_commentators_channels_id(options)

def get_commentators_channels_id(options):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    results = youtube.commentThreads().list(
        part="snippet",
        videoId=options['video_id'],
        maxResults=options['max_results'],
        textFormat="plainText"
    ).execute()

    commentators_ids = []

    for item in results["items"]:
        comment = item["snippet"]["topLevelComment"]
        text = comment["snippet"]["textDisplay"]
        authorChannelId = comment["snippet"]["authorChannelId"]["value"]
        commentators_ids.append(authorChannelId)
        print "Comment: %s commentator: %s" % (comment, authorChannelId)

    return commentators_ids

if __name__ == "__main__":
    argparser.add_argument("--max-results", help="Max results", default=25)
    argparser.add_argument("--forUsername", help="For Username", default="FightMediocrity")
    argparser.add_argument("--id", help="Id", default="UCbz5R9gNMCNkA92jz4JYi6Q")
    args = argparser.parse_args()

    try:
        get_channel_info(args)
    except HttpError, e:
        print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
