# !/usr/bin/python
__author__ = 'mateusz'

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


def get_channel_id_for_name(options):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    results = youtube.channels().list(
        part="id",
        forUsername=options.for_username,
    ).execute()

    for item in results["items"]:
        channel_id = item["id"]
        print channel_id


if __name__ == "__main__":
    argparser.add_argument("--for-username", help="For Username", default="phuckmediocrity")
    args = argparser.parse_args()

    try:
        get_channel_id_for_name(args)
    except HttpError, e:
        print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
