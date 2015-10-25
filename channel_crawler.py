# !/usr/bin/python

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

#TODO: support for channels with disabled comments (see below)
# An HTTP error 403 occurred:
# {
#  "error": {
#   "errors": [
#    {
#     "domain": "youtube.commentThread",
#     "reason": "commentsDisabled",
#     "message": "The video identified by the \u003ccode\u003e\u003ca href=\"/youtube/v3/docs/commentThreads/list#videoId\"\u003evideoId\u003c/a\u003e\u003c/code\u003e parameter has disabled comments.",
#     "locationType": "parameter",
#     "location": "videoId"
#    }
#   ],
#   "code": 403,
#   "message": "The video identified by the \u003ccode\u003e\u003ca href=\"/youtube/v3/docs/commentThreads/list#videoId\"\u003evideoId\u003c/a\u003e\u003c/code\u003e parameter has disabled comments."
#  }
# }

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyC_yFHSNjox4-pcCKubIZEb1wmy84Af980"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


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
            print channel_id

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
        # TODO: include video stats in db schema
        stats = item['statistics']

        # TODO: save this to db (video table + video_stats table)
        print "VIDEO INFO: videoId: %s; channelId: %s; title: %s; publishedAt: %s; \ndescription: %s; \nstats: %s" % (
            video_id, channel_id, title, published_at, description, stats)


def get_channel_info(options):
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

            # TODO: save this to db (channel table + channel_statistics)
            print "CHANNEL INFO: title: %s; desc: %s; publAt: %s; country %s; \nstats: %s" % (
                title, description, published_at, country, stats)

            uploaded_videos = item["contentDetails"]["relatedPlaylists"]["uploads"]
            print "Uploaded videos - id of the playlist: %s" % uploaded_videos
            get_playlist_items(uploaded_videos)

        next_page_token = results.get('nextPageToken')


def get_playlist_items(playlist_id):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    next_page_token = ''

    while next_page_token is not None:
        results = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            pageToken=next_page_token
        ).execute()

        for item in results["items"]:
            video_id = item["contentDetails"]["videoId"]
            print "VIDEO_ID: %s" % video_id
            options = {'video_id': video_id}

            get_video_info_for_id(video_id)
            get_commentators_channels_id(options)

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

            # TODO: save this to db (comment table)
            print "COMMENT INFO: commentId: %s; channelId: %s; " \
                  "videoId: %s; authorChannelId: %s; totalReplyCount: %s; likeCount: %s; publishedAt: %s; \ntext: %s" \
                  % (
                  comment_id, channel_id, video_id, authorChannelIdValue, total_reply_count, like_count, published_at,
                  text)
            commentators_ids.append(authorChannelIdValue)

        next_page_token = results.get('nextPageToken')

    return commentators_ids


if __name__ == "__main__":
    argparser.add_argument("--max-results", help="Max results", default=25)
    argparser.add_argument("--for-username", help="For Username", default="phuckmediocrity")
    argparser.add_argument("--id", help="Id", default="UCXLesGEfmyhxqOjoAqhRwhA")
    args = argparser.parse_args()

    try:
        get_channel_info(args)
        # get_channel_id_for_name(args)
    except HttpError, e:
        print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
