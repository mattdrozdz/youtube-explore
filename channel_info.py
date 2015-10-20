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

#pobiera informacje o kanale
#miedzy innymi identyfikator playlisty do wszystkich filmow - potem bedzie mozna pobierac komentarze z tych filmikow
def get_channel_info(options):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    results = youtube.channels().list(
        part="snippet,statistics,status,contentDetails",
        #forUsername=options.forUsername,
        id=options.id,
        maxResults=options.max_results
    ).execute()

    for item in results["items"]:
        title = item["snippet"]["title"]
        description = item["snippet"]["description"],
        status = item["status"],
        view_count = item["statistics"]["viewCount"]
        subscriber_count = item["statistics"]["subscriberCount"]
        video_count = item["statistics"]["videoCount"]
        uploaded_videos = item["contentDetails"]["relatedPlaylists"]["uploads"]
        print "Channel: %s Description: %s Status %s" % (title, description, status)
        print "ViewCount %s" % (view_count)
        print "Subscribers: %s" % (subscriber_count)
        print "Video count: %s" % (video_count)
        print "Uploaded videos: %s" % (uploaded_videos)
        get_playlist_items(uploaded_videos)


def get_playlist_items(uploaded_videos):

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    results = youtube.playlistItems().list(
        part="snippet,status,contentDetails",
        playlistId=uploaded_videos
    ).execute()

    for item in results["items"]:
        id = item["id"]
        videoId = item["contentDetails"]["videoId"]
        print "Channel item id %s" % (id)
        print "Video Id %s" % (videoId)



if __name__ == "__main__":
    argparser.add_argument("--max-results", help="Max results", default=25)
    argparser.add_argument("--forUsername", help="For Username", default="FightMediocrity")
    argparser.add_argument("--id", help="Id", default="UCbz5R9gNMCNkA92jz4JYi6Q")
    args = argparser.parse_args()

    try:
        get_channel_info(args)
    except HttpError, e:
        print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)


#channel Ids for tests
#UChGoz4u-wRWjn6rMsqYPlnA
#UCPAAsVfLJt9cz4u8JL50E0g