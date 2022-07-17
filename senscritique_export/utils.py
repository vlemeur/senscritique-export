"""Useful functions used to scrap senscritique"""

import difflib
import logging
from pathlib import Path
import urllib
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup, element

from senscritique_export.row_utils.books_utils import get_books_info_from_row, get_order_books_columns
from senscritique_export.row_utils.comics_utils import get_comics_info_from_row, get_order_comics_columns
from senscritique_export.row_utils.movies_utils import get_movies_info_from_row, get_order_movies_columns
from senscritique_export.row_utils.music_utils import get_music_info_from_row, get_order_music_columns
from senscritique_export.row_utils.series_utils import get_order_series_columns, get_series_info_from_row
from senscritique_export.row_utils.track_utils import get_track_info_from_row
from senscritique_export.row_utils.videogames_utils import (
    get_order_videogames_columns,
    get_videogames_info_from_row,
    get_videogames_topchart_info_from_row,
)

logger = logging.getLogger(__name__)
GENRE_CHOICES = ["Morceaux", "Albums", "Films", "Livres", "Séries", "BD", "Jeux"]


def get_soup(url: str) -> BeautifulSoup:
    """Returns a BeautifulSoup object for an url.

    Parameters
    ----------
    url : str
        url to consider

    Returns
    -------
    BeautifulSoup
        BeautifulSoup object built from url
    """
    return BeautifulSoup(requests.get(url).content, "lxml")


def format_number(number: str) -> str:
    """Format number

    Parameters
    ----------
    number : str
        number to format

    Returns
    -------
    str
        formatted number
    """
    result = number
    if "K" in result:
        if "." in result:
            result = result.replace("K", "").replace(".", "") + "00"
        else:
            result = result.replace("K", "") + "000"

    return result


def get_collection_current_page_number(soup: BeautifulSoup) -> Optional[int]:
    """Returns the senscritique page number of a BeautifulSoup object.

    Parameters
    ----------
    soup : BeautifulSoup
        BeautifulSoup object

    Returns
    -------
    Optional[int]
        page number
    """
    try:
        page_number = int(soup.find("span", {"class": "eipa-current"}).text)
        logger.info("Current collection page number : %s", page_number)
        return page_number
    except Exception as exception:
        logger.error(exception)
        return None


def get_dict_available_pages(soup: BeautifulSoup) -> Dict[int, str]:
    """Returns a dict of the available pages in a BeautifulSoup object.

    Parameters
    ----------
    soup : BeautifulSoup
        senscritique BeautifulSoup object

    Returns
    -------
    Dict[int, str]
        available pages
    """
    return {
        int(x["data-sc-pager-page"]): "https://old.senscritique.com" + x["href"]
        for x in soup.find_all("a", {"class": "eipa-anchor"})
    }


def get_next_collection_link(soup: BeautifulSoup) -> Optional[str]:
    """Returns the next link of BeautifulSoup object.

    Parameters
    ----------
    soup : BeautifulSoup
        senscritique BeautifulSoup object

    Returns
    -------
    Optional[str]
        Next link
    """
    available_pages = get_dict_available_pages(soup)
    if current_page := get_collection_current_page_number(soup):
        if available_pages.get(current_page + 1):
            return available_pages.get(current_page + 1)
    return None


def get_next_collection_soup(soup: BeautifulSoup) -> BeautifulSoup:
    """Returns the next BeautifulSoup object for an user collection.

    Parameters
    ----------
    soup : BeautifulSoup
        senscritique BeautifulSoup object

    Returns
    -------
    BeautifulSoup
        next BeautifulSoup for an user collection
    """
    next_col = get_next_collection_link(soup)
    logger.debug("Next collection link : %s", next_col)
    if not next_col:
        return None
    try:
        soup = get_soup(next_col)
    except Exception as exception:
        logger.error(exception)
        return None
    return soup


def get_rows_from_collection(soup: BeautifulSoup) -> List[element.ResultSet]:
    """Returns a list of rows from a collection.

    Parameters
    ----------
    soup : BeautifulSoup
        senscritique BeautifulSoup object

    Returns
    -------
    List[element.ResultSet]
        List of rows from a collection
    """
    logger.debug("get_rows_from_collection")
    list_rows = []
    while True:
        list_rows += soup.find_all("li", {"class": "elco-collection-item"})
        soup = get_next_collection_soup(soup)
        if not soup:
            logger.debug(
                "No rows here. Either it is the last page, the url is not valid or the collection  is private."
            )
            break
    return list_rows


def get_collection_info(soup: BeautifulSoup) -> List[Dict]:
    """Returns a list of dict containing an user collection information.

    Parameters
    ----------
    soup : BeautifulSoup
        senscritique BeautifulSoup object

    Returns
    -------
    List[Dict]
        List of dict containing user collection information
    """
    rows = get_rows_from_collection(soup)
    list_info = []
    for row in rows:
        info = get_row_info(row)
        if info:
            list_info.append(info)
    return list_info


def get_category(row: element.Tag) -> str:
    """Returns a category from a row

    Parameters
    ----------
    row : element.Tag
        row to consider

    Returns
    -------
    str
        category
    """
    return row.find("a", {"class": "elco-anchor"})["href"].split("/")[1]


def get_row_info(row: element.Tag) -> Optional[Dict]:
    """Returns a dict containing a row information.

    Parameters
    ----------
    row : element.Tag
        row to consider

    Returns
    -------
    Optional[Dict]
        row information
    """
    logger.debug("get_row_info")
    category = get_category(row)
    if category == "film":
        row_info = {
            **get_movies_info_from_row(row),
            **get_complementary_info_collection(row),
            **{"Category": "Movie"},
        }
    elif category == "serie":
        row_info = {
            **get_series_info_from_row(row),
            **get_complementary_info_collection(row),
            **{"Category": "Series"},
        }
    elif category == "jeuvideo":
        row_info = {
            **get_videogames_info_from_row(row),
            **get_complementary_info_collection(row),
            **{"Category": "Video Game"},
        }
    elif category == "livre":
        row_info = {
            **get_books_info_from_row(row),
            **get_complementary_info_collection(row),
            **{"Category": "Book"},
        }
    elif category == "bd":
        row_info = {
            **get_comics_info_from_row(row),
            **get_complementary_info_collection(row),
            **{"Category": "Comics"},
        }
    elif category == "album":
        row_info = {
            **get_music_info_from_row(row),
            **get_complementary_info_collection(row),
            **{"Category": "Music"},
        }
    elif category == "morceau":
        row_info = {
            **get_track_info_from_row(row),
            **get_complementary_info_collection(row),
            **{"Category": "Track"},
        }
    else:
        logger.error(f"Category {category} not supported.")
        return None

    return row_info


def get_complementary_info_collection(row: element.Tag) -> Dict:
    """Get information specific to a collection row.

    Parameters
    ----------
    row : element.Tag
        row to consider

    Returns
    -------
    Dict
        information from a c collection row
    """
    action = row.find("div", {"class": "elco-collection-rating user"}).find(
        "span", {"class": "elrua-useraction-inner only-child"}
    )

    dict_info = {}
    if action.find("span", {"class": "eins-wish-list"}):
        dict_info["User Action"] = "Wishlisted"
    elif action.find("span", {"class": "eins-current"}):
        dict_info["User Action"] = "In Progress"
    else:
        dict_info["User Action"] = "Rated"

    dict_info["Recommended"] = "True" if action.find("span", {"class": "eins-user-recommend"}) else "False"

    dict_info["User Rating"] = action.text.strip()
    logger.debug(dict_info)
    return dict_info


def get_list_work_current_page_number(soup: BeautifulSoup) -> Optional[int]:
    """Returns the senscritique page number of a BeautifulSoup object

    Parameters
    ----------
    soup : BeautifulSoup
        senscritique BeautifulSoup object

    Returns
    -------
    Optional[int]
        senscritique page number
    """
    try:
        page_number = int(soup.find("span", {"class": "eipa-current"}).text)
        logger.info("Current list_work page number : %s", page_number)
        return page_number
    except Exception as exception:
        logger.error(f"get_list_work_current_page_number: {exception}")
        return None


def get_next_list_work_link(soup: BeautifulSoup) -> Optional[str]:
    """Returns the next link of BeautifulSoup object.

    Parameters
    ----------
    soup : BeautifulSoup
        senscritique BeautifulSoup object

    Returns
    -------
    Optional[str]
        Next link of BeautifulSoup
    """
    available_pages = get_dict_available_pages(soup)
    logger.debug("Available pages : %s.", available_pages)
    current_page = get_list_work_current_page_number(soup)
    if current_page:
        if available_pages.get(current_page + 1):
            return available_pages.get(current_page + 1)
    return None


def get_next_list_work_soup(soup: BeautifulSoup) -> BeautifulSoup:
    """Returns the next BeautifulSoup object for an user list_work.

    Parameters
    ----------
    soup : BeautifulSoup
        senscritique BeautifulSoup object

    Returns
    -------
    BeautifulSoup
        Next BeautifulSoup for an user list
    """
    next_col = get_next_list_work_link(soup)
    soup.decompose()
    logger.debug("Next list_work link : %s", next_col)
    if not next_col:
        return None
    try:
        soup = get_soup(next_col)
    except Exception as exception:
        logger.error(exception)
        return None
    return soup


def get_rows_from_list_work(soup: BeautifulSoup) -> List[element.ResultSet]:
    """Returns rows from list work

    Parameters
    ----------
    soup : BeautifulSoup
        senscritique BeautifulSoup object

    Returns
    -------
    List[element.ResultSet]
        rows from list work
    """
    logger.debug("get_rows_from_list_work")
    list_rows = []
    while True:
        for row in soup.find_all("li", {"class": "elpr-item"}):
            list_rows.append(get_row_info(row))
        soup = get_next_list_work_soup(soup)
        if not soup:
            logger.debug("No rows here. Either it is the last page, the url is not valid or the list_work is private.")
            break
    return list_rows


def get_list_work_info(soup: BeautifulSoup) -> List[Dict]:
    """Returns a list of dict containing an user list_work information.

    Parameters
    ----------
    soup : BeautifulSoup
        senscritique BeautifulSoup object

    Returns
    -------
    List[Dict]
        user list work information
    """
    return get_rows_from_list_work(soup)


def sanitize_text(text: str) -> str:
    """Sanitize text to URL-compatible text.

    Parameters
    ----------
    text : str
        text to sanitize

    Returns
    -------
    str
        sanitized text
    """
    return urllib.parse.quote_plus(text)  # type: ignore


def get_search_url(search_term: str, genre: Optional[str] = None) -> str:
    """Returns the senscritique search URL for a search term.

    Parameters
    ----------
    search_term : str
        search term
    genre : Optional[str]
        genre , by default None

    Returns
    -------
    str
        search url
    """
    search_term_sanitized = sanitize_text(search_term)
    return (
        f"https://old.senscritique.com/search?q={search_term_sanitized}"
        if genre not in GENRE_CHOICES
        else f"https://old.senscritique.com/search?q={search_term_sanitized}&categories[0][0]={genre}"
    )


def get_search_result(soup: BeautifulSoup, position: int) -> Optional[str]:
    """Returns the URL result of the BeautifulSoup object at the defined position.

    Parameters
    ----------
    soup : BeautifulSoup
        senscritique BeautifulSoup object
    position : int
        position

    Returns
    -------
    Optional[str]
        URL result
    """
    try:
        url_list = [
            x.find_all("a")[1]["href"]
            for x in soup.find_all("div", {"class": "ProductListItem__Container-sc-1ci68b-0"})
        ]
        if position > len(url_list):
            logger.error(
                f"Desired result not found in search results"
                f"(Desired result: position {position}, number of search results: {len(url_list)})."
            )
            return None
        return url_list[position - 1]
    except Exception as exception:
        logger.error(exception)
        return None


def get_closest_search_result(soup: BeautifulSoup, search_term: str) -> Optional[str]:
    """Returns the closest result of the results for the search_term.

    Parameters
    ----------
    soup : BeautifulSoup
        senscritique BeautifulSoup object
    search_term : str
        search term

    Returns
    -------
    Optional[str]
        closest result of the search term results

    Raises
    ------
    Exception
        an exception is raised if operation failed
    """
    try:
        list_candidates = []
        for url in [
            x.find_all("a")[1]["href"]
            for x in soup.find_all("div", {"class": "ProductListItem__Container-sc-1ci68b-0"})
        ]:
            name = url.split("/")[-2:][0].replace("_", " ") if url else None
            list_candidates.append({"url": url, "name": name})
        if closest_match := difflib.get_close_matches(search_term, [x["name"] for x in list_candidates], 1):
            closest_dict = next(
                (item for item in list_candidates if item["name"] == closest_match[0]),
                None,
            )
            result = closest_dict.get("url") if closest_dict else None
        else:
            result = list_candidates[0].get("url")
        logger.info(f"{result=}")
        return result
    except Exception as exception:
        raise Exception(exception) from exception


def get_rows_from_survey(soup: BeautifulSoup) -> List[element.ResultSet]:
    """Returns a list of rows from a survey.

    Parameters
    ----------
    soup : BeautifulSoup
        senscritique BeautifulSoup object

    Returns
    -------
    List[element.ResultSet]
        list of survey rows
    """
    return soup.find("ol", {"class": "pvi-list"}).find_all("li", {"class": "elpo-item"})


def get_category_from_survey(soup: BeautifulSoup) -> str:
    """Returns category from survey

    Parameters
    ----------
    soup : BeautifulSoup
        senscritique BeautifulSoup object

    Returns
    -------
    str
        category
    """
    return soup.find("li", {"class": "header-navigation-universe-current"}).find("a")["href"].split("/")[-1]


def get_survey_info(soup: BeautifulSoup, category: str) -> List[Dict]:
    """Returns a list of dict containing data of a survey.

    Parameters
    ----------
    soup : BeautifulSoup
        senscritique BeautifulSoup object
    category : str
        category to consider

    Returns
    -------
    List[Dict]
        data of a survey
    """
    rows = get_rows_from_survey(soup)
    if category == "films":
        list_info = [get_movies_info_from_row(x) for x in rows]
    elif category == "series":
        list_info = [get_series_info_from_row(x) for x in rows]
    elif category == "jeuxvideo":
        list_info = [get_videogames_info_from_row(x) for x in rows]
    elif category == "livres":
        list_info = [get_books_info_from_row(x) for x in rows]
    elif category == "bd":
        list_info = [get_comics_info_from_row(x) for x in rows]
    elif category == "musique":
        list_info = [get_music_info_from_row(x) for x in rows]
    else:
        logger.error(f"Category {category} not supported.")
        return []
    return list_info


def get_survey_order(category: str) -> List:  # pylint: disable=too-many-return-statements
    """Returns the order of columns for a survey based on its category.

    Parameters
    ----------
    category : str
        category

    Returns
    -------
    List
        order of columns
    """
    if category == "bd":
        return get_order_comics_columns()
    if category == "films":
        return get_order_movies_columns()
    if category == "jeuxvideo":
        return get_order_videogames_columns()
    if category == "livres":
        return get_order_books_columns()
    if category == "musique":
        return get_order_music_columns()
    if category == "series":
        return get_order_series_columns()
    logger.error(f"Category {category} not supported.")
    return []


def get_rows_from_topchart(soup: BeautifulSoup) -> List[element.ResultSet]:
    """Returns a list of rows from a topchart.

    Parameters
    ----------
    soup : BeautifulSoup
        senscritique BeautifulSoup object

    Returns
    -------
    List[element.ResultSet]
        list of topchart rows
    """
    return soup.find("ol", {"class": "elto-list"}).find_all("li", {"class": "elto-item"})


def get_topchart_info(soup: BeautifulSoup, category: str) -> List[Dict]:  # pylint: disable=too-many-return-statements
    """Returns a list of dict containing data of a topchart.

    Parameters
    ----------
    soup : BeautifulSoup
        senscritique BeautifulSoup object
    category : str
        category to consider

    Returns
    -------
    List[Dict]
        data of a topchart
    """
    rows = get_rows_from_topchart(soup)
    if category == "films":
        return [get_movies_info_from_row(x) for x in rows]
    if category == "series":
        return [get_series_info_from_row(x) for x in rows]
    if category == "jeuxvideo":
        return [get_videogames_topchart_info_from_row(x) for x in rows]
    if category == "livres":
        return [get_books_info_from_row(x) for x in rows]
    if category == "bd":
        return [get_comics_info_from_row(x) for x in rows]
    if category == "musique":
        return [get_music_info_from_row(x) for x in rows]
    logger.error(f"Category {category} not supported.")
    return []


def get_topchart_order(category: str) -> List:
    """Returns the order of columns for a topchart based on its category.

    Parameters
    ----------
    category : str
        category to consider

    Returns
    -------
    List
        topchart order columns
    """
    if category == "bd":
        result = get_order_comics_columns()
    elif category == "films":
        result = get_order_movies_columns()
    elif category == "jeuxvideo":
        result = get_order_videogames_columns()
    elif category == "livres":
        result = get_order_books_columns()
    elif category == "musique":
        result = get_order_music_columns()
    elif category == "series":
        result = get_order_series_columns()
    else:
        result = []
        logger.error(f"Category {category} not supported.")
    return result

def get_token(path_token_file: Path) -> str:
    with open(path_token_file, "w") as token_file:
        lines = token_file.readlines()
    stop = "here"