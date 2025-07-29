from ..._prismcomponent.prismcomponent import _PrismModelComponent, _AbstractPrismComponent
from ..._utils import _validate_args


_data_category = __name__.split(".")[-1]


class _PrismTCModelComponent(_PrismModelComponent):
    _component_category_repr  = _data_category


class almgren(_PrismTCModelComponent):
    r"""
    | Estimates and manage the trading costs associated with executing large orders in financial markets for a given trade.
    | The model was created/calibrated based on the data from Citi's trading desk. It uses 3/5 power laws instead of conventional square-root law.
    |
    .. math:: C = \frac 1 2 + \eta\sigma|\frac X {VT}|^\frac 3 5
    .. math:: I = \sigma\gamma \frac X V(\frac \theta V)^\frac 1 4
    |
    .. math:: X \equiv \text {Transactions in shares}
    .. math:: T \equiv \text {Trade Duration}
    .. math:: V \equiv \text {Average Daily Volume}
    .. math:: \theta \equiv \text {Shares Outstanding}
    .. math:: \gamma = 0.314
    .. math:: \eta = 0.142


    Parameters
    ----------

        transaction : prismstudio._PrismComponent
            | Desired currency for the pricing data.

        tradeduration : int
            | Desired data package in where the pricing data outputs from.

        averageperiod : int
            | Desired data package in where the pricing data outputs from.

    Returns
    -------
        prismstudio._PrismComponent

    References
    ----------
        Almgren, Robert & Thum, Chee & Hauptmann, Emmanuel & Li, Hong. (2005). Direct Estimation of Equity Market Impact. RISK. 18.

    Examples
    --------
        >>> ret = ps.market.close().sample_pct_change(1)
        >>> trade = (ret > 0).map({True:1000_000, False:-1000_000})
        >>> trade_amount = trade.abs()
        >>> ps.tcmodel.almgren(trade_amount, 10, 5).get_data("Korea_primary", "2020-01-01", shownid=["companyname"])
                  listingid        date     value                         Company Name
        0          20108704  2020-01-02  0.235841      Daewon Pharmaceutical Co., Ltd.
        1          20108706  2020-01-02  0.344619                  N.I Steel Co., Ltd.
        2          20108718  2020-01-02  0.046685         Songwon Industrial Co., Ltd.
        3          20108719  2020-01-02  0.275940               Whan In Pharm Co.,Ltd.
        4          20109325  2020-01-02  0.030277               Theragen Etex Co.,Ltd.
        ...             ...         ...       ...                                  ...
        1611478  1833210191  2023-07-28  0.038329                    Suresofttech Inc.
        1611479  1833230315  2023-07-28  0.111412                S.Biomedics CO., LTD.
        1611480  1834641955  2023-07-28  0.034584     ISU Specialty Chemical Co., Ltd.
        1611481  1838438397  2023-07-28  0.069874   Dongkuk Steel Mill Company Limited
        1611482  1838459712  2023-07-28  0.127869                 Dongkuk CM Co., Ltd.
    """
    @_validate_args
    def __init__(
        self,
        transaction: _AbstractPrismComponent,
        tradeduration: int,
        averageperiod: int,
    ):
        super().__init__(
            transaction=transaction,
            tradeduration=tradeduration,
            averageperiod=averageperiod,
            children=[transaction],
        )


class bidaskspread(_PrismTCModelComponent):
    r"""
    | The simple bid-ask spread market impact model calculates the relative impact of a trade.
    | The model provides a basic measure of liquidity and reflects the cost a trader may incur when buying or selling an asset, with a larger spread indicating a higher potential market impact.
    |
    .. math:: \frac {ask-bid} {(ask+bid)/2}

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> bas = ps.tcmodel.bidaskspread()
        >>> bas.get_data("Korea_primary", "2020-01-01", shownid=["companyname"])
                  listingid        date  bidaskspread                        Company Name
        0          20108704  2020-01-02      0.002894     Daewon Pharmaceutical Co., Ltd.
        1          20108706  2020-01-02      0.009009                 N.I Steel Co., Ltd.
        2          20108718  2020-01-02      0.003221        Songwon Industrial Co., Ltd.
        3          20108719  2020-01-02      0.003190              Whan In Pharm Co.,Ltd.
        4          20109325  2020-01-02      0.002410              Theragen Etex Co.,Ltd.
        ...             ...         ...           ...                                 ...
        1611958  1833210191  2023-07-28      0.002315                   Suresofttech Inc.
        1611959  1833230315  2023-07-28      0.003415               S.Biomedics CO., LTD.
        1611960  1834641955  2023-07-28      0.001857    ISU Specialty Chemical Co., Ltd.
        1611961  1838438397  2023-07-28      0.001007  Dongkuk Steel Mill Company Limited
        1611962  1838459712  2023-07-28      0.001129                Dongkuk CM Co., Ltd.
    """
