import os
import errno
import orjson
import logging
import requests
import sys
import time
import uuid

from prismstudio._utils.exceptions import PrismAuthError

from .._common.config import *


credential_file = ""
logger = logging.getLogger()
access_token_time = ""

def _get_credential_file(cred_file = None):
    global credential_file
    if cred_file:
        credential_file = cred_file
    else:
        cred_file = credential_file
    try:
        with open(cred_file, 'r') as f:
            username = f.readline().strip()
            password = f.readline().strip()
    except:
        logger.warning("Please check credential file path!")
        return
    return {'username': username, 'password': password}


def _login_helper(cred_query):
    req_id = str(uuid.uuid4())[:8]
    headers = {"client": "python", 'requestid': req_id}
    res = requests.post(url=URL_LOGIN, data=cred_query, headers=headers)
    if res.ok:
        _create_token(res)
        result = f"Login success! Welcome {cred_query['username']}"
    else:
        _delete_token()
        logger.warning(f"\033[91mLogin Failed\033[0m: {orjson.loads(res.content).get('message', None)}")
        return None
    return result


def _authentication():
    global auth_token, refresh_token, access_token_time, credential_file
    try:
        current_time = time.time()
        if access_token_time is None:
            raise PrismAuthError("Please Login First")
        if current_time - access_token_time > 2500:
            res = requests.post(url=URL_REFRESH, cookies={"refresh_token": refresh_token})
            if res.status_code > 400:
                if credential_file:
                    cred_query = _get_credential_file()
                    res = _login_helper(cred_query)
                else:
                    raise PrismAuthError("Session Expired! Please login again!")
            elif res.ok:
                _create_token(res)
        headers = HEADERS.copy()
        if not auth_token:
            raise PrismAuthError(f"Please Login First")
        token = auth_token
        headers.update({"Authorization": "Bearer {}".format(token)})
        req_id = str(uuid.uuid4())[:8]
        headers.update({"requestid": req_id})
    except FileNotFoundError:
        raise PrismAuthError(f"Please Login First")
    return headers


def _delete_token():
    global auth_token, refresh_token, access_token_time, credential_file
    auth_token = ''
    refresh_token = ''
    access_token_time = ''
    credential_file = ''


def _create_token(response: requests.models.Response):
    global auth_token, refresh_token, access_token_time
    token = response.json()["access_token"]
    ref_token = response.cookies.get("refresh_token")
    auth_token = token
    refresh_token = ref_token
    access_token_time = time.time()


def _find_file_path(file_name: str):
    sys.path.append(os.getcwd())
    for path in sys.path:
        if os.path.exists(path + "/" + file_name):
            return path + "/" + file_name
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file_name)


class TokenDoesNotExistError(Exception):
    def __init__(self):
        super().__init__("You should first login to create a token")


def _get_web_authentication_token():
    headers = _authentication()
    res = requests.post(URL_WEB_AUTH, headers=headers)
    web_auth_token = res.json().get("access_token")
    return web_auth_token

def _get_document_authentication_token():
    headers = _authentication()
    res = requests.post(URL_DOC_AUTH, headers=headers)
    web_auth_token = res.json().get("access_token")
    return web_auth_token
