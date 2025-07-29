import hashlib
import logging
import pandas as pd
import re

import prismstudio
from ..._common import const
from ..._common.config import *
from ..._utils.exceptions import PrismValueError
from ..._utils import _validate_args, _delete_token, post, _get_credential_file, _login_helper, get

__all__ = ['login', 'change_password', 'logout']


@_validate_args
def login(username: str = '', password: str = '', credential_file: str = ''):
    """
    Log in to PrismStudio.

    Parameters
    ----------
        username : str, default ''
            A string representing the username of the user.
        password : str, default ''
            A string representing the password of the user.
        credential_file : str, default ''
            | Provide credential text files.
            | The first line of the file should be username and the second line should be password.
            | Please provide either valid credential file or username and password pair.

    Returns
    -------
        str
            A string with a success message if the login is successful, or **None** if the login fails.
    """
    logger = logging.getLogger()
    if not(bool(username and password) ^ bool(credential_file)):
        logger.warning("Please provide valid credential!")
        logger.warning("You are only allowed to enter a pair of username and password or a credential file with txt extension.")
        return
    if bool(credential_file) & (not(credential_file[-4:] == ".txt")):
        logger.warning("Please enter a valid file path. Only txt file is allowed!")
        return
    if password:
        password = hashlib.sha512(password.encode())
        password = password.hexdigest()
        cred_query = {'username': username, 'password': password}
    if credential_file:
        cred_query = _get_credential_file(credential_file)
    result = _login_helper(cred_query)
    if not result:
        return None

    smattributes = get(f'{URL_SM}/attributes')
    const.SMValues = pd.DataFrame(smattributes).sort_values("attributeorder", ascending=True)
    const.SMAttributemap = dict(zip(
        const.SMValues["attributename"].str.lower().str.replace(" ", "").str.replace('_', ''),
        const.SMValues["attributeid"]
    ))
    const.SMAttributemap.update(
        dict(zip(
            const.SMValues["attributerepr"].str.lower().str.replace(" ", "").str.replace('_', ''),
            const.SMValues["attributeid"]
        ))
    )
    const.PreferenceType = get(f'{URL_PREFERENCES}/types')
    const.CategoryComponent = get(URL_CATEGORYCOMPONENTS)
    const.FunctionComponents = get(URL_FUNCTIONCOMPONENTS)
    const.DataComponents = get(URL_DATACOMPONENTS)
    prismstudio.username = cred_query['username']
    return result


def logout():
    """
    Log out from PrismStudio.

    Returns
    -------
        str
            A string with a logout message.
    """
    _delete_token()
    prismstudio.username = None
    return 'Logout success!'


def change_password(new_password: str):
    """
    Change password for current user. It requires user to login to the service again with new password.

    Parameters
    ----------
    new_password : str, default ''
        | A new password for current user.
        | Password is minimum 8 characters and must contain at least one uppercase letter, one lowercase letter, one number and one special character.

    Returns
    -------
        str
            A string with a success message if password changing is successful.
    """
    regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    p = re.compile(regex)
    if not p.match(new_password):
        raise PrismValueError("Password is minimum 8 characters and must contain at least one uppercase letter, one lowercase letter, one number and one special character.")

    password = hashlib.sha512(new_password.encode())
    password = password.hexdigest()
    query = {'username': prismstudio.username, 'password': password}

    # res = requests.post(url=URL_PASSWORD, headers=headers, json=query)
    res = post(url=URL_PASSWORD, params={}, body=query)
    if res.get('status', None) == 'success':
        _delete_token()
        prismstudio.username = None
        return "Password changed successfully! Please login again using new password!"
    return "Failed to get response"

