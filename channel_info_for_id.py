from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

__author__ = 'mateusz'

DEVELOPER_KEY = "AIzaSyC_yFHSNjox4-pcCKubIZEb1wmy84Af980"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def get_channel_info(options):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    results = youtube.channels().list(
        part="snippet,statistics,status,contentDetails",
        id=options.id,
    ).execute()

    for item in results["items"]:
        title = item["snippet"]["title"]
        description = item["snippet"]["description"]
        published_at = item["snippet"]["publishedAt"]
        country = item["snippet"].get("country")
        stats = item["statistics"]

        # TODO: save this to db (channel table + channel_statistics)
        # print "CHANNEL INFO: title: %s; desc: %s; publAt: %s; country %s; \nstats: %s" % (
        #     title, description, published_at, country, stats)

        # save to DB
        print "ITEM: \n%s\n" % item
        print "SNIPPET \n%s\n" % item['snippet']
        print "STATISTICS: \n%s\n" % stats
        print "STATUS: \n%s\n" % item['status']
        print "CONTENT DETAILS: \n%s\n" % item['contentDetails']



if __name__ == "__main__":
    argparser.add_argument("--id", help="Channel id", default="UCSpTklmV9l_VYRGrTlWT08Q")
    args = argparser.parse_args()

    try:
        get_channel_info(args)
    except HttpError, e:
        print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)