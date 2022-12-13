from flask import Flask, Response, request
from flask_cors import CORS
import json
from typing import *
from requests_futures.sessions import FuturesSession
import requests
from utils import DTEncoder
import os

app = Flask(__name__)
CORS(app)

session = FuturesSession()
def get_complete_user_profile(userid):
    rsp_data = {'user_info':None, 'partner_info':None, 'post_info':None}
    future1 = session.get(f'{os.environ.get("MS2_URL")}api/userprofile/{userid}')
    future2 = session.get(f'{os.environ.get("MS1_URL")}api/user/{userid}/partner')
    response1 = future1.result().json()
    response2 = future2.result().json()

    # if user not found
    if not response1['success']:
        rsp = {'success':False, 'data':rsp_data}
        return rsp
    
    rsp_data['user_info'] = response1['data'][0]


    # if the user has a partner, get partner's infomation
    if response2['success']:
        partner_id = list(response2['data'][0].values())[0]
        future21 = session.get(f'http://localhost:5011/api/userprofile/{partner_id}')
        response21 = future21.result().json()
        rsp_data['partner_info'] = response21['data'][0]

    rsp = {'success':True, 'data':rsp_data}
    return rsp

@app.route("/api/composite/user_profile_all/<userid>", methods=["GET"])
def user_profile_all(userid):

    result = get_complete_user_profile(userid)
    if result['success']:
        rsp = Response(json.dumps(result, cls=DTEncoder), status=200, content_type="application.json")
    else:
        rsp = Response(json.dumps(result, cls=DTEncoder), status=200, content_type="application.json")
    return rsp

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5013, debug=True)


