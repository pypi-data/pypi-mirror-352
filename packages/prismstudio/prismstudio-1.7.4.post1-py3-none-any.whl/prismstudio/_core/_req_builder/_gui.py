import webbrowser

from prismstudio._utils.auth_utils import _get_document_authentication_token

from ..._common.config import *
from ..._utils import _get_web_authentication_token


__all__ = ['job_manager', 'preference_setting', 'securitymaster_search', 'dataitem_search']


def job_manager():
    """
    Open job manager in a new web browser tab.

    Returns
    -------
        None

    Notes
    -----
        The user might be asked to login if not already logged in.

    Examples
    --------
        >>> import prism
        >>> ps.job_manager()

        .. image:: ../../_static/jobmanager-api-ref-screenshot.png

    """
    web_auth_token = _get_web_authentication_token()
    link = ROOT_EXT_WEB_URL + '/jobmanager?token=' + str(web_auth_token)
    webbrowser.open(link, new=2)


def preference_setting():
    """
    Open preference setting window on a new browser tab.

    Returns
    -------
        None

    Notes
    -----
        The user will be asked to login if not already logged in.

    Examples
    --------
        >>> import prism
        >>> ps.preference_setting()
    """

    web_auth_token = _get_web_authentication_token()
    link = ROOT_EXT_WEB_URL + '/preference?token=' + str(web_auth_token)
    webbrowser.open(link, new=2)


def securitymaster_search():
    """
    Opens the security master search window on a new browser tab.

    Notes
    -----
        This function opens the security master search page on the Prism web application in a new browser tab.
        The user will be asked to login if they are not already logged in.

    Returns
    -------
        None
    """
    web_auth_token = _get_web_authentication_token()
    link = ROOT_EXT_WEB_URL + '/securitymaster?token=' + str(web_auth_token)
    webbrowser.open(link, new=2)


def dataitem_search():
    """
    Opens the data item search window on a new browser tab.

    Notes
    -----
        This function opens the data item search page on the Prism web application in a new browser tab.
        The user will be asked to login if they are not already logged in.

    Returns
    -------
        None
    """
    web_auth_token = _get_web_authentication_token()
    link = ROOT_EXT_WEB_URL + '/dataitems?token=' + str(web_auth_token)
    webbrowser.open(link, new=2)


def finder():
    web_auth_token = _get_web_authentication_token()
    link = ROOT_EXT_WEB_URL + '/finder?token=' + str(web_auth_token)
    webbrowser.open(link, new=2)


def finder(file_type='dataquery'):
    """
    | Open query manager window on a new browser tab.
    | Users are able to:

    1. Share files or a folder within the same account.
    2. File operations, such as Copy, Cut, Paste, Delete, Move etc..
    3. Create, Delete Folders.
    4. Check properties of a file.

    Parameters
    ----------
        file_type: str {'dataquery', 'taskquery', 'universe', 'portfolio'}, default 'dataquery'
            Open correspoding type of file in browser tab.

    Returns
    -------
        None
            .. admonition:: Warning
                :class: warning

                The user will be asked to login if not already logged in.

    Examples
    --------
        >>> ps.finder()

        .. image:: ../../_static/finder.png
    """
    web_auth_token = _get_web_authentication_token()
    link = ROOT_EXT_WEB_URL + f'/finder?type={file_type}&token={web_auth_token}'
    webbrowser.open(link, new=2)


def open_document(version: str = 'latest'):
    doc_auth_token = _get_document_authentication_token()
    link = ROOT_DOCUMENT_URL + '/' + version + '/?token=' + str(doc_auth_token)
    webbrowser.open(link, new=2)
