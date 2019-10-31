import json
from urllib.request import urlopen, Request
from pprint import pprint
from datetime import datetime
from urllib.error import HTTPError

from time import sleep
import random

mainUrl = "https://stage.wepayapi.com/v2/checkout/create "
accountId = 143658 
userId = 1067923907
accessToken = "STAGE_3940d7e40dbc7e3d8ff4a6fe5cea7ddef1a594ec50754c272a55fbb5f231f65c"
creditCard = 3803294492
newId = 1046399939

headers = {"Content-Type": "application/json"}

##params = {
##            "client_id": accountId,
##            "user_name": "Bob Smith",
##            "email": "test@example.com",
##            "cc_number": "5496198584584769",
##            "cvv": "123",
##            "expiration_month": 4,
##            "expiration_year": 2020,
##            "address": {
##                "country": "US",
##                "postal_code": "94025"
##            },
##            "card_on_file": False,
##            "recurring": False
##        }

params = {'account_id': newId,
            'amount': '25.50',
            'currency': 'USD',
            'short_description': 'VICTORY!!!!!!!!!!!!!!!!!!',
            'type': 'goods',
            'payment_method': {
                    'type': 'credit_card',
                    'credit_card': {
                        'id': creditCard
                    }
            }
          }
##params = {
##           "client_id": accountId,
##           "client_secret": "c4cddb1166",
##           "email": "api@wepay.com",
##           "scope": "manage_accounts,collect_payments,view_user,send_money,preapprove_payments",
##           "first_name": "Bill",
##           "last_name": "Clerico",
##           "original_ip": "74.125.224.84",
##           "original_device": "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; en-US) AppleWebKit/534.13 (KHTML, like Gecko) Chrome/9.0.597.102 Safari/534.13",
##           "tos_acceptance_time": 1209600
##        }

for x in range(50):
    req = Request(mainUrl)
    req.add_header("Content-Type", "application/json; charset=utf-8'")
    jsondata = json.dumps(params)
    jsonbytes = jsondata.encode("utf-8")
    req.add_header("Content-Length", len(jsonbytes))
    req.add_header("Authorization", "Bearer {}".format(accessToken))
    pprint(jsonbytes)
    print("\n\n")
    response = urlopen(req, jsonbytes)
    pprint(response.readlines())
    sleep(int(random.random()*30))

