from .._req_builder import _list_dataitem
from ..._common.const import CompanyRelAttributeType as _CompanyRelAttributeType
from ..._prismcomponent.prismcomponent import _PrismComponent, _PrismDataComponent
from ..._utils import _get_params, _validate_args
from ..._utils.exceptions import PrismValueError


__all__ = [
    "competitor",
    "description",
    "product",
    "relationship",
]


_data_category = __name__.split(".")[-1]


class _PrismCompanyComponent(_PrismDataComponent, _PrismComponent):
    _component_category_repr = _data_category


class competitor(_PrismCompanyComponent):
    """
    Retrieve data about equity securities' competitors.

    Parameters
    ----------
    target : bool
        Specifies whether the company is identified as a competitor by another company:
        - If True, the data will display all the companies that have identified the companies within the universe as competitors.
        - If False, the data will display all the companies that the companies within the universe have identified as competitors.

    attribute : str
        Desired security attribute identifier to be displayed for the counterparty company.

    Returns
    -------
    prismstudio._PrismComponent

    Examples
    --------
        >>> competitor = ps.company.competitor(True, 'companyname')
        >>> ps.get_data(competitor, 'Korea_primary', '2020-01-01', '2021-01-01')
              listingid                        value
        0      20108718                      BASF SE
        1      20108718            Adeka Corporation
        2      20108718             Chang Chun Group
        3      20108718          Sunko Ink Co., Ltd.
        4      20108718          Rianlon Corporation
        ...         ...                          ...
        4191  670598900              NEXON Co., Ltd.
        4192  670598900        Netmarble Corporation
        4193  693108646  Logitech International S.A.
        4194  693108646                    Cherry SE
        4195  693108646         Corsair Gaming, Inc.
    """
    @_validate_args
    def __init__(
        self,
        target: bool,
        attribute: _CompanyRelAttributeType,
        package : str = None,
    ):
        super().__init__(**_get_params(vars()))


class description(_PrismCompanyComponent):
    """
    | Retrieve the business description of a company.

    Parameters
    ----------
    long : bool, default True
        Specifies whether to display the extended version of the business description, if available.

    package : str {'LSEG Business Descriptions', 'CIQ Company Intelligence'}, default None
        | Desired data package in where the pricing data outputs from.

        .. admonition:: Warning
            :class: warning

            If an invalid package is entered without a license, an error will be generated as output.

    Returns
    -------
    prismstudio._PrismComponent

    Examples
    --------
        >>> desc = ps.company.description(True)
        >>> ps.get_data(desc, 'Korea_primary', '2020-01-01', '2021-01-01')
               listingid                                              value
        0       20108704  Daewon Pharmaceutical Co., Ltd., a pharmaceuti...
        1       20108706  N.I Steel Co., Ltd. produces and sells steel p...
        2       20108718  Songwon Industrial Co., Ltd., together with it...
        3       20108719  Whan In Pharm Co.,Ltd., a pharmaceutical compa...
        4       20109325  Theragen Etex Co.,Ltd., together with its subs...
        ...          ...                                                ...
        1850  1795845686  Saltware Co., Ltd. provides various IT service...
        1851  1801379557  Finger Story Co., Ltd. produces and distribute...
        1852  1819922381  Opticore.Inc manufactures and sells optical mo...
        1853  1824738416  Fine Circuit Co., Ltd. engages in manufacturin...
        1854  1830288132  Kostecsys. Co. Ltd. provides low thermal expan...
    """

    @_validate_args
    def __init__(
        self,
        long: bool = True,
        package : str = None,
    ):
        super().__init__(**_get_params(vars()))


class product(_PrismCompanyComponent):
    """
    | Retrieve information about a company's available products.

    Parameters
    ----------

    Returns
    -------
    prismstudio._PrismComponent

    Examples
    --------
        >>> product = ps.company.product()
        >>> ps.get_data(product, 'Korea_primary', '2020-01-01', '2021-01-01')
                listingid        productname                                 productdescription  currentflag  updatedate
        0        20108704        Pelubi Tab.  Pelubi Tab an Anti-inflammatory, analgesic ind...            1         NaT
        1        20108704     Pelubi CR Tab.  Pelubi CR Tab. reduce symptoms of Osteoarthrit...            1         NaT
        2        20108704       Curefen Syr.  Curefen Syr. is an antipyretic analgesic, offe...            1         NaT
        3        20108704       Senafen Tab.  Senafen Tab. is indicated for Rheumatoid arthr...            1         NaT
        4        20108704  Tapain Tab./ Inj.  Tapain Tab./ Inj. is indicated for Rheumatoid ...            1         NaT
        ...           ...                ...                                                ...          ...         ...
        51031  1789113982       RF AQUASUNNY  Aquasunny RF system is an innovative injector ...            1         NaT
        51032  1789113982                FEI  Fei RF Needle offers a superior solution for s...            1         NaT
        51033  1789113982      CLABIANE THOR  CLABIANE THOR is Anti-aging microneedle skin r...            1         NaT
        51034  1789113982       Hifin Liften                                               None            1         NaT
        51035  1789113982          Hair Boom                                               None            1         NaT
    """
    @_validate_args
    def __init__(
        self,
        package : str = None,
    ):
        super().__init__(**_get_params(vars()))


class relationship(_PrismCompanyComponent):
    """
    | Retrieve data about specific business relationships involving equity securities.

    Parameters
    ----------
    target : bool, default True
        Specifies whether the company is identified as having certain business relationships by other companies:
        - If True, the data will display all companies that have identified the companies within the universe with certain business relationships.
        - If False, the data will display all companies within the universe that have been identified with certain business relationships.

    attribute : str, default 'companyname'
        Desired security attribute identifier to be displayed for the counterparty company.

    Returns
    -------
    prismstudio._PrismComponent

    Examples
    --------
        >>> rel = ps.company.relationship(True, 'companyname')
        >>> ps.get_data(rel, 'Korea_primary', '2020-01-01', '2021-01-01')
                listingid  businessreltypeid  sourcerelationship  targetrelationship  currentflag                                          source  updatedate
        0        20108704                  2            Supplier            Customer            0                               KX NexG Co., LTD.         NaT
        1        20108704                  4            Supplier         Distributor            0                                  Enzymotec Ltd.         NaT
        2        20108706                  2            Supplier            Customer            0  Suzhou Chunxing Precision Mechanical Co., Ltd.         NaT
        3        20108718                  2            Supplier            Customer            0                          SGC eTEC E&C Co., Ltd.         NaT
        4        20108718                  2            Supplier            Customer            0                           KOLON BENIT Co., Ltd.         NaT
        ...           ...                ...                 ...                 ...          ...                                             ...         ...
        19827   706837957                  8            Landlord              Tenant            0                         KB Securities Co., Ltd.         NaT
        19828   706837957                  2            Supplier            Customer            0                                        SSR Inc.         NaT
        19829   706837957                 20             Company  Strategic Alliance            0                                 HancomWITH Inc.         NaT
        19830  1675455809                  2            Supplier            Customer            0                                  METIS Co. Ltd.         NaT
        19831  1790081744                  4            Supplier         Distributor            0                        Eukor Car Carriers, Inc.         NaT
    """
    @_validate_args
    def __init__(
        self,
        target: bool,
        attribute: _CompanyRelAttributeType,
        package : str = None,
    ):
        super().__init__(**_get_params(vars()))
