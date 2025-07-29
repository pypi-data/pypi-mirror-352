from prismstudio._utils.exceptions import PrismValueError
from ..._common.config import *
from ..._common.const import *
from ..._utils import _validate_args, post
from ..._utils.validate_utils import get_sm_attributeid


__all__ = ['get_securitymaster', 'get_securitymaster_advanced']


@_validate_args
def get_securitymaster(attribute: str, search: str):
    """
    Return Security information search result with single condition.

    Parameters
    ----------
        attribute : str
            Security Master attribute to search on.

        search : str
            Search word to condition on the attribute.

    Returns
    -------
        pandas.Dataframe
            | Security information.
            | Columns:

            - *listingid*
            - *valuetype*
            - *value*
            - *startdate*
            - *enddate*

            .. admonition:: Note
                :class: note

                | Returns only first 100 results

    Examples
    --------
        >>> ps.get_securitymaster(attribute='companyname', search='Samsung')
             listingid      valuetype     value	 startdate      enddate
        0      2647420  tradingitemid   2647420  1700-01-01  2199-12-31
        1     20174680  tradingitemid  20174680  1700-01-01  2199-12-31
        2     30562725  tradingitemid  30562725  1700-01-01  2199-12-31
        3      2647422  tradingitemid   2647422  1700-01-01  2199-12-31
        4     30562723  tradingitemid  30562723  1700-01-01  2199-12-31
        ...	       ...            ...       ...         ...         ...
        96    20194961  fsym_entityid  05HXF2-E  1700-01-01  2199-12-31
        97    20191195  fsym_entityid  05HWPG-E  1700-01-01  2199-12-31
        98    31778919  fsym_entityid  05VHCF-E  1700-01-01  2199-12-31
        99    62339029  fsym_entityid  07LZ7F-E  1700-01-01  2199-12-31
        100   62339030  fsym_entityid  07LZ7F-E  1700-01-01  2199-12-31
    """
    attributeid = get_sm_attributeid(attribute)
    query = [{'attributeid': attributeid, 'search': search}]
    return post(URL_SM, None, query)


@_validate_args
def get_securitymaster_advanced(queries: list):
    """
    Return Security information search result with multiple conditions.

    Parameters
    ----------
        queries: list of dict
            | List of security information search criteria. Each dictionary contains three keys: “operator”, “attribute”, “search”

            - operator: {”AND”, “OR”}
            - attribute: Security Master attribute to search on.
            - search: Search word to condition on the attribute.

    Returns
    -------
        pandas.Dataframe
            | Security information
            | Columns:

            - *listingid*
            - *valuetype*
            - *value*
            - *startdate*
            - *enddate*

            .. admonition:: Note
                :class: note

                | Returns only first 100 results

    Examples
    --------
        >>> ps.get_securitymaster_advanced([{'attribute': 'country', 'search': 'US'}, {'attribute': 'GICS sector', 'search': '30'}])
              listingid      valuetype     value   startdate     enddate
        0       2585879  tradingitemid   2585879  1987-05-08  1993-10-15
        1       2587041  tradingitemid   2587041  1983-09-20  2002-09-13
        2       2588957  tradingitemid   2588957  1984-10-22  1993-02-25
        3       2588959  tradingitemid   2588959  1984-10-22  1993-02-25
        4       2587848  tradingitemid   2587848  1986-04-23  2003-11-05
        ...         ...            ...       ...         ...         ...
        96     27580549  fsym_entityid  0044NF-E  1700-01-01  2199-12-31
        97     27580549  fsym_entityid  06GRML-E  1700-01-01  2199-12-31
        98     40843715  fsym_entityid  000LNJ-E  1700-01-01  2199-12-31
        99     99731436  fsym_entityid  05N251-E  1700-01-01  2199-12-31
        100   144070140  fsym_entityid  00D843-E  1700-01-01  2199-12-31
    """
    if len(queries) == 0: raise PrismValueError('At least one query must be provided.')
    for i in range(len(queries)):
        assert isinstance(queries[i], dict), 'queries must be list of dicts.'
        assert set(queries[i].keys()) - {'operator'} == {'attribute', 'search'}, \
            'Valid arguments are "attribute", "search", and "operator".'
        queries[i]['attributeid'] = get_sm_attributeid(queries[i].pop('attribute'))

    return post(URL_SM, None, queries)
