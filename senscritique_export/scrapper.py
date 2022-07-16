import logging
from typing import Dict, List, Optional

from senscritique_export.utils import (
    Work,
    get_category_from_survey,
    get_closest_search_result,
    get_collection_info,
    get_list_work_info,
    get_search_result,
    get_search_url,
    get_soup,
    get_survey_info,
    get_topchart_info,
)

logger = logging.getLogger(__name__)


def get_user_collection(user: Optional[str] = None, url: Optional[str] = None) -> List[Dict]:
    """Export an user collection in a list of dictionaries.

    Parameters
    ----------
    user :  Optional[str]
        Username, by default None
    url :  Optional[str]
        Url of the profile page of the user, by default None

    Returns
    -------
    List[Dict]
        user collection

    Raises
    ------
    Exception
        raised if get soup method failed
    """

    if user:
        url = f"https://old.senscritique.com/{user}/collection/all/all/all/all/all/all/all/all/all/page-1"
    if not url:
        raise Exception("user or url not defined")
    logger.info("URL : %s", url)
    try:
        soup = get_soup(url)
    except Exception as e:
        logger.error(e)
        exit()

    collection = get_collection_info(soup)
    return collection


def create_collection_filename(user: str, ext: str = "csv") -> str:
    """Return a filename for a collection.

    Parameters
    ----------
    user : str
        user to consider
    ext : str
        extension used, by default "csv"

    Returns
    -------
    str
        collection filename
    """
    return f"export_collection_{user}.{ext}"


def get_topchart(url: str) -> List[Dict]:
    """Export a topchart from its url in a list of dictionaries.

    Warning: a topchart is different from a survey.
    A topchart is an automatically generated ranking (i.e. Top 111 Films),
    a survey is filled in by the community (i.e. Best Movies for 2013).

    Parameters
    ----------
    url : str
        Url of the senscritique topchart

    Returns
    -------
    List[Dict]
        List of dictionaries containing the topchart information
    """

    logger.info("URL : %s", url)
    try:
        soup = get_soup(url)
    except Exception as e:
        logger.error(e)
        exit()

    category = get_category_from_topchart_url(url)
    topchart = get_topchart_info(soup, category)
    return topchart


def get_category_from_topchart_url(url: str) -> str:
    """Return the category from an url.

    Parameters
    ----------
    url : str
        url to consider

    Returns
    -------
    str
        category

    Raises
    ------
    Exception
        Throws an error if the url isn't recognized.
    """

    category = url.split("/")[3]
    # check category
    if category not in [
        "films",
        "series",
        "jeuxvideo",
        "livres",
        "bd",
        "musique",
    ]:
        raise Exception("URL malformed. Check that the url contains a Senscritique Top (not a Survey).")
    return category


def create_topchart_filename(url: str, ext: str = "csv") -> str:
    """Return a filename for a topchart.

    Parameters
    ----------
    url : str
        url to topchart
    ext : str
        extension, by default "csv"

    Returns
    -------
    str
        topchart filename
    """
    category = get_category_from_topchart_url(url)
    return f"export_topchart_{category}_{url.split('/')[-1]}.{ext}"


def get_survey(url: str) -> List[Dict]:
    """Export a survey from its url in a list of dictionaries.

    Warning: a survey is different from a topchart.
    A topchart is an automatically generated ranking (i.e. Top 111 Films),
    a survey is filled in by the community (i.e. Best Movies for 2013).

    Parameters
    ----------
    url : str
        url of the senscritique topchart.

    Returns
    -------
    List[Dict]
        survey information
    """

    logger.info("URL : %s", url)
    try:
        soup = get_soup(url)
    except Exception as e:
        logger.error(e)
        exit()

    category = get_category_from_survey(soup)
    survey = get_survey_info(soup, category)
    return survey


def create_survey_filename(url: str, ext: str = "csv") -> str:
    """Return a filename for a survey.

    Parameters
    ----------
    url : str
        url of survey
    ext : str
        extension, by default "csv"

    Returns
    -------
    str
        filename for a survey
    """
    return f"export_survey_{url.split('/')[-1]}.{ext}"


def get_list_work(url: str) -> List[Dict]:
    """Export a list of work from its url in a list of dictionaries.

    Parameters
    ----------
    url : str
        url (str): Url (example : https://old.senscritique.com/films/oeuvres)
        Available urls : - https://old.senscritique.com/films/oeuvres
                         - https://old.senscritique.com/series/oeuvres
                         - https://old.senscritique.com/jeuxvideo/oeuvres
                         - https://old.senscritique.com/livres/oeuvres
                         - https://old.senscritique.com/jeuxvideo/oeuvres
                         - https://old.senscritique.com/musique/oeuvres

    Returns
    -------
    List[Dict]
        list of work object
    """

    logger.info("URL : %s", url)
    try:
        soup = get_soup(url)
    except Exception as e:
        logger.error(e)
        exit()

    list_work = get_list_work_info(soup)
    return list_work


def create_list_work_filename(url: str, ext: str = "csv") -> str:
    """Return a filename for a list of work.

    Parameters
    ----------
    url : str
        url to consider
    ext : str
        extension, by default "csv"

    Returns
    -------
    str
        filename for a list of work
    """
    category = get_category_from_topchart_url(url)
    return f"export_listwork_{category}_{url.split('/')[-1]}.{ext}"


def get_work_details(url: str) -> Dict:
    """Extract details about a work regardless of its category.

    Parameters
    ----------
    url : str
        url to consider

    Returns
    -------
    Dict
        Dictionary containing the work details.
    """

    logger.info("URL : %s", url)

    work = Work(url)
    return work.get_details()


def get_url(search_term: str, rank: int = 1, genre: Optional[str] = None) -> Optional[str]:
    """Return the first result URL for the search term.
    Rank can be changed (default 1: first result).
    Genre can be changed

    Parameters
    ----------
    search_term : str
        search term
    rank : int
        rank of page, by default 1
    genre : Optional[str]
        genre to consider, by default None

    Returns
    -------
    Optional[str]
        first URL result of search
    """

    logger.info("Search term: %s", search_term)

    url = get_search_url(search_term, genre)

    try:
        soup = get_soup(url)
    except Exception as e:
        logger.error(e)
        exit()

    return get_search_result(soup, rank)


def get_url_closest_match(search_term: str, genre: Optional[str] = None) -> Optional[str]:
    """Return the result URL for the search term that is also the closest match to the search term.
    Genre can be changed

    Parameters
    ----------
    search_term : str
        search term to consider
    genre : Optional[str]
        genre to consider, by default None

    Returns
    -------
    Optional[str]
        closest result for the search term results

    Raises
    ------
    Exception
        exception is raised if get soup failed
    """

    logger.info("Search term: %s", search_term)

    url = get_search_url(search_term, genre)

    try:
        soup = get_soup(url)
    except Exception as e:
        raise Exception(e)

    return get_closest_search_result(soup, search_term)
