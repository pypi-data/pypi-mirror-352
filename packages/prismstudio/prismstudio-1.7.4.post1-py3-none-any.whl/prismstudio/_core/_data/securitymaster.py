import pandas as pd

from ..._common.config import *
from ..._common.const import *
from ..._prismcomponent.prismcomponent import _PrismComponent, _PrismDataComponent
from ..._utils.validate_utils import _validate_args, get_sm_attributeid
from ..._utils import get


__all__ = ['attribute', 'list_attribute']


_data_category = __name__.split(".")[-1]


class attribute(_PrismDataComponent, _PrismComponent):
    """
    Return the security master attribute for a given listingids. Default frequency is daily.

    Parameters
    ----------
        attribute : str, {"Trading Item ID", "Security ID", "Company ID", "Trade Currency", "MIC", "Ticker", "CIQ Primary", "Country", "Company Name", "GVKEY", "GVKEYIID", "ISIN", "SEDOL", "VALOR", "WKN", "Share Class FIGI", "CUSIP", "CINS", "Barra ID", "FIGI", "Composite FIGI", "SIC", "NAICS", "IBES Ticker", "Compustat Primary", "GICS Sector", "GICS Group", "GICS Industry", "GICS Sub-Industry", "LEI", "SNL Institution ID", "Moody's Issuer Number", "RatingsXpress Entity ID", "MarkIt Red Code", "Fitch Issuer ID", "CMA Entity ID", "Factset Listing ID", "Factset Security ID", "Fackset Company ID", "Factset Entity ID", “Current Ticker”, “ISIN”}
            | Security master attribute includes security codes and meta data from multiple vendors.

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> gics = ps.securitymaster.attribute(attribute="Trade Currency")
        >>> gics.get_data(universe="S&P 500", startdate="2010-01-01", enddate="2015-01-01")
                listingid        date  Trade Currency  Company Name
        0         2586086  2010-01-01             USD     AFLAC INC
        1         2586086  2010-01-02             USD     AFLAC INC
        2         2586086  2010-01-03             USD     AFLAC INC
        3         2586086  2010-01-04             USD     AFLAC INC
        4         2586086  2010-01-05             USD     AFLAC INC
        ...           ...         ...             ...           ...
        914740  344286611  2011-10-27             USD      ITT CORP
        914741  344286611  2011-10-28             USD      ITT CORP
        914742  344286611  2011-10-29             USD      ITT CORP
        914743  344286611  2011-10-30             USD      ITT CORP
        914744  344286611  2011-10-31             USD      ITT CORP
    """

    _component_category_repr = _data_category

    @_validate_args
    def __init__(self, attribute: str, offset: int = 0):
        attributeid = get_sm_attributeid(attribute)
        super().__init__(attributeid=attributeid, offset=offset)


def list_attribute():
    """
    Return the all usable attributes in the security master.

    Returns
    -------
        list : Usable attribute.

    Examples
    --------
        >>> ps.securitymaster.list_attribute()
        ['Trading Item ID',
        'VALOR',
        'GVKEY',
        'MarkIt Red Code',
        'Country',
        'GICS Sector',
        'WKN',
        'CINS',
        "Moody's Issuer Number",
        'GICS Group',
        'SEDOL',
        'Company Name',
        'CMA Entity ID',
        'CIQ Primary',
        'NAICS',
        'Factset Security ID',
        'Composite FIGI',
        'Share Class FIGI',
        'FIGI',
        'Compustat Primary',
        'Factset Company ID',
        'Ticker',
        'Factset Entity ID',
        'GVKEYIID',
        'Company ID',
        'Factset Listing ID',
        'LEI',
        'IBES Ticker',
        'CUSIP',
        'GICS Sub-Industry',
        'Barra ID',
        'ISIN',
        'MIC',
        'ISIN',
        'SIC',
        'Security ID',
        'Trade Currency',
        'GICS Industry',
        'Fitch Issuer ID',
        'RatingsXpress Entity ID',
        'Current Ticker',
        'SNL Institution ID']
    """
    smattributes = get(f'{URL_SM}/attributes')
    smattributes_df = pd.DataFrame(smattributes)
    return smattributes_df.sort_values(by='attributeorder')['attributerepr'].tolist()
