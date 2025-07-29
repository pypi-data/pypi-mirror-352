
from .._req_builder import _list_dataitem
from ..._prismcomponent.prismcomponent import _PrismDataComponent, _PrismComponent
from ..._utils import _validate_args, _get_params


__all__ = [
    'social',
    'governance',
    'overall',
    'environmental',
    'diversity'
]


_data_category = __name__.split(".")[-1]


class _PrismESGComponent(_PrismComponent, _PrismDataComponent):
    _component_category_repr = _data_category

    @classmethod
    def _dataitems(cls, search : str = None, package : str = None):
        return _list_dataitem(
            datacategoryid=cls.categoryid,
            datacomponentid=cls.componentid,
            search=search,
            package=package,
        )


class environmental(_PrismESGComponent):
    """
    Retrieves detailed criteria scores and weights that constitute the Environmental Dimension evaluation.

    The Environmental Dimension allows you to access to comprehensive information concerning the company's environmental impact and sustainability practices. It examines the company's efforts to mitigate environmental risks, conserve resources, reduce emissions, and promote eco-friendly initiatives.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the value.

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> esg = ps.esg.environmental(700088)
        >>> esg.get_data("Semiconductor", "2020-01-01", shownid=['Company Name'])
                listingid        date  value          Company Name
        0         2597014  2020-01-17    0.0   CMC Materials, Inc.
        1         2597014  2020-01-17   67.0   CMC Materials, Inc.
        2         2597014  2020-01-17   33.0   CMC Materials, Inc.
        3         2597014  2020-01-17   26.0   CMC Materials, Inc.
        4         2597014  2020-01-17   41.0   CMC Materials, Inc.
        ...           ...         ...    ...                   ...
        36680  1682846833  2023-01-20   44.0  GLOBALFOUNDRIES Inc.
        36681  1682846833  2023-01-20   74.0  GLOBALFOUNDRIES Inc.
        36682  1682846833  2023-01-20   50.0  GLOBALFOUNDRIES Inc.
        36683  1682846833  2023-01-20    0.0  GLOBALFOUNDRIES Inc.
        36684  1682846833  2023-01-20   33.0  GLOBALFOUNDRIES Inc.
    """
    @_validate_args
    def __init__(
        self,
        dataitemid: int,
    ):
        super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None, package: str = None):
        """
        Usable dataitems for criteria in Environmental Dimension.

        Parameters
        ----------
            search : str, default None
                | Search word for dataitems name, the search is case-insensitive.

            package : str, default None
                | Search word for package name, the search is case-insensitive.

        Returns
        -------
            pandas.DataFrame
                Data items that belong to cash flow statement data component.

            Columns:
                - *dataitemid*
                - *dataitemname*
                - *datamodule*
                - *package*
                - *datadescription*


        Examples
        --------
            >>> ps.esg.environmental.dataitems()
                dataitemid                              dataitemname  datamodule                package                                dataitemdescription
            0       700088                      Biodiversity - Score       Score  S&P Global ESG Scores  Score of Biodiversity\nExtractive industries a...
            1       700089                Building Materials - Score       Score  S&P Global ESG Scores  Score of Building Materials\nA substantial per...
            2       700090  Business Risks and Opportunities - Score       Score  S&P Global ESG Scores  Score of Business Risks and Opportunities\nFin...
            3       700091                  Climate Strategy - Score       Score  S&P Global ESG Scores  Score of Climate Strategy\nMost industries are...
            4       700092                     Co-Processing - Score       Score  S&P Global ESG Scores  Score of Co-Processing\nCo-processing involves...
            ..         ...                                       ...         ...                                                                       ...
            65      700233                       Energy Mix - Weight      Weight  S&P Global ESG Scores  Scoring Weight of Energy Mix\nOil & Gas produc...
            66      700234                 Fleet Management - Weight      Weight  S&P Global ESG Scores  Scoring Weight of Fleet Management\nThe airlin...
            67      700235         Sustainable Construction - Weight      Weight  S&P Global ESG Scores  Scoring Weight of Sustainable Construction\nTh...
            68      700236                 Circular Fashion - Weight      Weight  S&P Global ESG Scores  Scoring Weight of Circular Fashion\nThe fashio...
            69      700237         Decarbonization Strategy - Weight      Weight  S&P Global ESG Scores  Scoring Weight of Decarbonization Strategy\nAs...
        """
        return cls._dataitems(search=search, package=package)


class social(_PrismESGComponent):
    """
    Retrieves detailed criteria scores and weights that constitute the Social Dimension evaluation.

    The Social Dimension allows you to access comprehensive information about how the company manages its internal and external relationships, including interactions with employees and the communities where it operates. The provided criteria scores and weights give you a deeper insight into the company's social impact and performance.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the value.

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> esg = ps.esg.social(700008)
        >>> esg.get_data("Semiconductor", "2020-01-01", shownid=['Company Name'])
                listingid        date  value          Company Name
        0         2597014  2020-01-17    0.0   CMC Materials, Inc.
        1         2597014  2020-01-17   33.0   CMC Materials, Inc.
        2         2597014  2020-01-17   67.0   CMC Materials, Inc.
        3         2597014  2020-01-17   26.0   CMC Materials, Inc.
        4         2597014  2020-01-17   10.0   CMC Materials, Inc.
        ...           ...         ...    ...                   ...
        36680  1682846833  2023-01-20   44.0  GLOBALFOUNDRIES Inc.
        36681  1682846833  2023-01-20   74.0  GLOBALFOUNDRIES Inc.
        36682  1682846833  2023-01-20   50.0  GLOBALFOUNDRIES Inc.
        36683  1682846833  2023-01-20    0.0  GLOBALFOUNDRIES Inc.
        36684  1682846833  2023-01-20   33.0  GLOBALFOUNDRIES Inc.
    """
    @_validate_args
    def __init__(
        self,
        dataitemid: int,
    ):
        super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None, package: str = None):
        """
        Usable dataitems for criteria in Social Dimension.

        Parameters
        ----------
            search : str, default None
                | Search word for dataitems name, the search is case-insensitive.

            package : str, default None
                | Search word for package name, the search is case-insensitive.

        Returns
        -------
            pandas.DataFrame
                Data items that belong to cash flow statement data component.

            Columns:
                - *dataitemid*
                - *dataitemname*
                - *datamodule*
                - *package*
                - *datadescription*

        Examples
        --------
            >>> ps.esg.social.dataitems()
                dataitemid                                       dataitemname  datamodule                package  dataitemdescription
            0       700008                            Access to Water - Score       Score  S&P Global ESG Scores  Score of Access to Water\nWater is a pre-requi...
            1       700009                     Addressing Cost Burden - Score       Score  S&P Global ESG Scores  Score of Addressing Cost Burden\nDue to aging ...
            2       700010                   Asset Closure Management - Score       Score  S&P Global ESG Scores  Score of Asset Closure Management\nMining acti...
            3       700011                                  Bioethics - Score       Score  S&P Global ESG Scores  Score of Bioethics\nDetailed and transparent p...
            4       700012  Controversial Issues: Dilemmas in Lending & Fi...       Score  S&P Global ESG Scores  Score of Controversial Issues: Dilemmas in Len...
            ..         ...                                                ...         ...                    ...
            69      700155                        Health & Nutrition - Weight      Weight  S&P Global ESG Scores  Scoring Weight of Health & Nutrition\nPoor die...
            70      700156                        Privacy Protection - Weight      Weight  S&P Global ESG Scores  Scoring Weight of Privacy Protection\nNetworke...
            71      700157          Customer Relationship Management - Weight      Weight  S&P Global ESG Scores  Scoring Weight of Customer Relationship Manage...
            72      700158                       Marketing Practices - Weight      Weight  S&P Global ESG Scores  Scoring Weight of Marketing Practices\nAggress...
            73      700159  Sustainable Marketing & Brand Perception - Weight      Weight  S&P Global ESG Scores  Scoring Weight of Sustainable Marketing & Bran...
        """
        return cls._dataitems(search=search, package=package)


class governance(_PrismESGComponent):
    """
    Retrieves detailed criteria scores and weights that constitute the Governance & Economic Dimension evaluation.

    The Governance & Economic Dimension allows you to access comprehensive information about company's leadership, executive pay, audits, internal controls, and shareholder rights and the relations to external stakeholders such as suppliers and customers. The provided criteria scores and weights give you a deeper insight into the company's governance practices and economic performance.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the value.

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> esg = ps.esg.governance(700045)
        >>> esg.get_data("Semiconductor", "2020-01-01", shownid=['Company Name'])
                listingid        date  value          Company Name
        0         2597014  2020-01-17    0.0   CMC Materials, Inc.
        1         2597014  2020-01-17   33.0   CMC Materials, Inc.
        2         2597014  2020-01-17   26.0   CMC Materials, Inc.
        3         2597014  2020-01-17   67.0   CMC Materials, Inc.
        4         2597014  2020-01-17   10.0   CMC Materials, Inc.
        ...           ...         ...    ...                   ...
        36680  1682846833  2023-01-20   44.0  GLOBALFOUNDRIES Inc.
        36681  1682846833  2023-01-20   74.0  GLOBALFOUNDRIES Inc.
        36682  1682846833  2023-01-20   50.0  GLOBALFOUNDRIES Inc.
        36683  1682846833  2023-01-20   33.0  GLOBALFOUNDRIES Inc.
        36684  1682846833  2023-01-20    0.0  GLOBALFOUNDRIES Inc.
    """
    @_validate_args
    def __init__(
        self,
        dataitemid: int,
    ):
        super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None, package: str = None):
        """
        Usable dataitems for criteria in Governance & Economic Dimension.

        Parameters
        ----------
            search : str, default None
                | Search word for dataitems name, the search is case-insensitive.

            package : str, default None
                | Search word for package name, the search is case-insensitive.

        Returns
        -------
            pandas.DataFrame
                Data items that belong to cash flow statement data component.

            Columns:
                - *dataitemid*
                - *dataitemname*
                - *datamodule*
                - *package*
                - *datadescription*


        Examples
        --------
            >>> ps.esg.environmental.dataitems()
                dataitemid                                 dataitemname datamodule  package   dataitemdescription
            0       700045         Anti-crime Policy & Measures - Score      Score  S&P Global ESG Scores  Score of Anti-crime Policy & Measures\nCrimina...
            1       700046                     Antitrust Policy - Score      Score  S&P Global ESG Scores  Score of Antitrust Policy\nAs global competiti...
            2       700047                     Brand Management - Score      Score  S&P Global ESG Scores  Score of Brand Management\nA brand is a living...
            3       700048  Financial Stability & Systemic Risk - Score      Score  S&P Global ESG Scores  Score of Financial Stability & Systemic Risk\n...
            4       700049                      Business Ethics - Score      Score  S&P Global ESG Scores  Score of Business Ethics\nThe criterion evalua...
            ..         ...                                          ...        ...                                                                       ...
            81      700198             Supply Chain Management - Weight     Weight  S&P Global ESG Scores  Scoring Weight of Supply Chain Management\nIn ...
            82      700199            Sustainable Construction - Weight     Weight  S&P Global ESG Scores  Scoring Weight of Sustainable Construction\nTh...
            83      700200                 Sustainable Finance - Weight     Weight  S&P Global ESG Scores  Scoring Weight of Sustainable Finance\nFinanci...
            84      700201                        Tax Strategy - Weight     Weight  S&P Global ESG Scores  Scoring Weight of Tax Strategy\nTax competitio...
            85      700202                    Water Operations - Weight     Weight  S&P Global ESG Scores  Scoring Weight of Water Operations\nWater Oper...
        """
        return cls._dataitems(search=search, package=package)


class overall(_PrismESGComponent):
    """
    Provides the overall ESG score and provide dimension level scores and weights.

    Takes in ESG scores and their corresponding weights to calculate the overall Environmental, Social, and Governance (ESG) score for a company. It also provides dimension level scores and weights, offering insights into the company's performance in each ESG dimension.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the value.

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> esg = ps.esg.overall(700001)
        >>> esg.get_data("Semiconductor", "2020-01-01", shownid=['Company Name'])
                listingid        date  value                                     Company Name
        0         2597014  2020-01-17     16                              CMC Materials, Inc.
        1         2597014  2020-01-17     39                              CMC Materials, Inc.
        2         2597014  2020-01-17     14                    Universal Display Corporation
        3         2597014  2020-01-17     30                    Universal Display Corporation
        4       412298450  2020-01-17     18                             Ichor Holdings, Ltd.
        ...           ...         ...    ...                                              ...
        36680    79144374  2023-01-20     84                         WIN Semiconductors Corp.
        36681   140445201  2023-01-20     23                                 SÜSS MicroTec SE
        36682   627069513  2023-01-20     14  Advanced Micro-Fabrication Equipment Inc. China
        36683   627069513  2023-01-20     23  Advanced Micro-Fabrication Equipment Inc. China
        36684  1682846833  2023-01-20     40                             GLOBALFOUNDRIES Inc.
    """
    @_validate_args
    def __init__(
        self,
        dataitemid: int,
    ):
        super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None, package: str = None):
        """
        Usable dataitems for overall esg scores.

        Parameters
        ----------
            search : str, default None
                | Search word for dataitems name, the search is case-insensitive.

            package : str, default None
                | Search word for package name, the search is case-insensitive.

        Returns
        -------
            pandas.DataFrame
                Data items that belong to cash flow statement data component.

            Columns:
                - *dataitemid*
                - *dataitemname*
                - *datamodule*
                - *package*
                - *datadescription*


        Examples
        --------
            >>> ps.esg.overall.dataitems()
            dataitemid              dataitemname  datamodule                package                                dataitemdescription
            0      700001       ESG Overall - Score       Score  S&P Global ESG Scores  The overarching score reflecting a company's p...
            1      700002     Environmental - Score       Score  S&P Global ESG Scores  The Environment dimension-level score that ref...
            2      700003            Social - Score       Score  S&P Global ESG Scores  The Social dimension-level score that reflects...
            3      700004        Governance - Score       Score  S&P Global ESG Scores  The Governance and Economic dimension-level sc...
            4      700005    Environmental - Weight      Weight  S&P Global ESG Scores  The sum of Environmental criteria weights. Thi...
            5      700006           Social - Weight      Weight  S&P Global ESG Scores  The sum of the Social criteria weights. This r...
            6      700007       Governance - Weight      Weight  S&P Global ESG Scores  The sum of the Governance and Economic criteri...
        """
        return cls._dataitems(search=search, package=package)


def dataitems(search: str = None, package: str = None):
    return _list_dataitem(
        datacategoryid=_PrismESGComponent.categoryid,
        datacomponentid=None,
        search=search,
        package=package,
    )


class diversity(_PrismESGComponent):
    """
    Provides the diversity scores for a firm

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the value.

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> esg = ps.esg.diversity(350017)
        >>> esg.get_data("Semiconductor", "2020-01-01", shownid=['Company Name'])
                listingid        date  value                                     Company Name
        0         2597014  2020-01-17     16                              CMC Materials, Inc.
        1         2597014  2020-01-17     39                              CMC Materials, Inc.
        2         2597014  2020-01-17     14                    Universal Display Corporation
        3         2597014  2020-01-17     30                    Universal Display Corporation
        4       412298450  2020-01-17     18                             Ichor Holdings, Ltd.
        ...           ...         ...    ...                                              ...
        36680    79144374  2023-01-20     84                         WIN Semiconductors Corp.
        36681   140445201  2023-01-20     23                                 SÜSS MicroTec SE
        36682   627069513  2023-01-20     14  Advanced Micro-Fabrication Equipment Inc. China
        36683   627069513  2023-01-20     23  Advanced Micro-Fabrication Equipment Inc. China
        36684  1682846833  2023-01-20     40                             GLOBALFOUNDRIES Inc.
    """
    @_validate_args
    def __init__(
        self,
        dataitemid: int,
    ):
        super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None, package: str = None):
        """
        Usable dataitems for diversity and inclusion ratings.

        Diversity and inclusion ratings measure the relative performance of companies against factors that define diverse and inclusive workplaces.

        Parameters
        ----------
            search : str, default None
                | Search word for dataitems name, the search is case-insensitive.

            package : str, default None
                | Search word for package name, the search is case-insensitive.

        Returns
        -------
            pandas.DataFrame
                Data items that belong to cash flow statement data component.

            Columns:
                - *dataitemid*
                - *dataitemname*
                - *datamodule*
                - *package*
                - *datadescription*


        Examples
        --------
            >>> ps.esg.diversity.dataitems()
            dataitemid                       dataitemname      datamodule      package                                dataitemdescription
            0      350017                     TRDIR Score           Score  LSEG ESG V2  Refinitiv's Diversity Inclusion Rating is an o...
            1      350018           TRDIR Diversity Score  Category Score  LSEG ESG V2  Diversity category measures a company's commit...
            2      350019  TRDIR People Development Score  Category Score  LSEG ESG V2  People Development category measures a company...
            3      350020           TRDIR Inclusion Score  Category Score  LSEG ESG V2  Inclusion category measures a company's commit...
            4      350021       TRDIR Controversies Score  Category Score  LSEG ESG V2  Controversies category accounts for the negati...

        """
        return cls._dataitems(search=search, package=package)


def dataitems(search: str = None, package: str = None):
    return _list_dataitem(
        datacategoryid=_PrismESGComponent.categoryid,
        datacomponentid=None,
        search=search,
        package=package,
    )
