import os
import sys
from requests_oauthlib import OAuth1Session
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
import logging

UPDATE_URL = 'https://api.twitter.com/1.1/statuses/update.json'

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

twitter_ck = os.getenv('TWITTER_CK', None)
twitter_cs = os.getenv('TWITTER_CS', None)
twitter_at = os.getenv('TWITTER_AT', None)
twitter_as = os.getenv('TWITTER_AS', None)

channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    logger.error('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    logger.error('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

def tweet(text):
    params = {"status": text }
    twitter = OAuth1Session(twitter_ck, twitter_cs, twitter_at, twitter_as)
    twitter.post(UPDATE_URL, params = params)

def lambda_handler(event, context):
    signature = event["headers"]["X-Line-Signature"]
    body = event["body"]
    ok_json = {"isBase64Encoded": False,
               "statusCode": 200,
               "headers": {},
               "body": ""}
    error_json = {"isBase64Encoded": False,
                  "statusCode": 403,
                  "headers": {},
                  "body": "Error"}

    @handler.add(MessageEvent, message=TextMessage)
    def message(line_event):
        text = line_event.message.text
        tweet(text)
        #line_bot_api.reply_message(line_event.reply_token, TextSendMessage(text=text))

    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        logger.error("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            logger.error("  %s: %s" % (m.property, m.message))
        return error_json
    except InvalidSignatureError:
        return error_json

    return ok_json