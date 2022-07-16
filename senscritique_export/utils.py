import difflib
import logging
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
    if "K" in number and "." in number:
        return number.replace("K", "").replace(".", "") + "00"
    elif "K" in number and "." not in number:
        return number.replace("K", "") + "000"
    else:
        return number


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
    except Exception as e:
        logger.error(e)
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
    dict_links = {
        int(x["data-sc-pager-page"]): "https://old.senscritique.com" + x["href"]
        for x in soup.find_all("a", {"class": "eipa-anchor"})
    }
    return dict_links


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
    current_page = get_collection_current_page_number(soup)
    if current_page:
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
    if next_col:
        try:
            soup = get_soup(next_col)
        except Exception as e:
            logger.error(e)
            return None
    else:
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
    except Exception as e:
        logger.error(f"get_list_work_current_page_number: {e}")
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
    if next_col:
        try:
            soup = get_soup(next_col)
        except Exception as e:
            logger.error(e)
            return None
    else:
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
    rows = get_rows_from_list_work(soup)
    return rows


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
    return urllib.parse.quote_plus(text)


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
    if genre not in GENRE_CHOICES:
        url = f"https://old.senscritique.com/search?q={search_term_sanitized}"
    else:
        url = f"https://old.senscritique.com/search?q={search_term_sanitized}&categories[0][0]={genre}"
    return url


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
    except Exception as e:
        logger.error(e)
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
        closest_match = difflib.get_close_matches(search_term, [x["name"] for x in list_candidates], 1)
        if closest_match:
            closest_dict = next(
                (item for item in list_candidates if item["name"] == closest_match[0]),
                None,
            )
            result = closest_dict.get("url") if closest_dict else None
        else:
            result = list_candidates[0].get("url")
        logger.info(f"{result=}")
        return result
    except Exception as e:
        raise Exception(e)


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


def get_survey_order(category: str) -> List:
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
    if category == "films":
        return get_order_movies_columns()
    elif category == "series":
        return get_order_series_columns()
    elif category == "jeuxvideo":
        return get_order_videogames_columns()
    elif category == "livres":
        return get_order_books_columns()
    elif category == "bd":
        return get_order_comics_columns()
    elif category == "musique":
        return get_order_music_columns()
    else:
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


def get_topchart_info(soup: BeautifulSoup, category: str) -> List[Dict]:
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
    elif category == "series":
        return [get_series_info_from_row(x) for x in rows]
    elif category == "jeuxvideo":
        return [get_videogames_topchart_info_from_row(x) for x in rows]
    elif category == "livres":
        return [get_books_info_from_row(x) for x in rows]
    elif category == "bd":
        return [get_comics_info_from_row(x) for x in rows]
    elif category == "musique":
        return [get_music_info_from_row(x) for x in rows]
    else:
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
    if category == "films":
        return get_order_movies_columns()
    elif category == "series":
        return get_order_series_columns()
    elif category == "jeuxvideo":
        return get_order_videogames_columns()
    elif category == "livres":
        return get_order_books_columns()
    elif category == "bd":
        return get_order_comics_columns()
    elif category == "musique":
        return get_order_music_columns()
    else:
        logger.error(f"Category {category} not supported.")
        return []


class Work:
    def __init__(self, url):
        self.url = url
        self.category = self.get_category()
        self.soup = get_soup(self.url)

    def export(self) -> Dict[str]:
        """Export information

        Returns
        -------
        Dict[str]
            information
        """
        return {
            **{
                "Title": self.title,
                "URL": self.url,
                "Rating": self.main_rating,
                "Rating Details": self.rating_details,
                "Year": self.year,
                "Cover URL": self.cover_url,
                "Review Count": self.review_count,
                "Vote Count": self.vote_count,
                "Favorite Count": self.favorite_count,
                "Wishlist Count": self.wishlist_count,
                "In Progress Count": self.in_progress_count,
                "Description": self.description,
            },
            **self.get_complementary_info(),
            **{"Category": self.category},
        }

    def get_category(self) -> str:
        """Returns a category

        Returns
        -------
        str
            category
        """
        category = self.url.split("/")[3]
        if category == "film":
            return "Movie"
        elif category == "serie":
            return "Series"
        elif category == "jeuvideo":
            return "Video Game"
        elif category == "livre":
            return "Book"
        elif category == "bd":
            return "Comics"
        elif category == "album":
            return "Music"
        elif category == "morceau":
            return "Track"

    def get_details(self) -> Dict[str]:
        """Returns details

        Returns
        -------
        Dict[str]
            details
        """

        self.main_rating = self.get_main_rating()
        self.rating_details = self.get_rating_details()
        self.vote_count = self.get_vote_count()
        self.favorite_count = self.get_favorite_count()
        self.wishlist_count = self.get_wishlist_count()
        self.in_progress_count = self.get_in_progress_count()
        self.title = self.get_title()
        self.year = self.get_year()
        self.cover_url = self.get_cover_url()
        self.review_count = self.get_review_count()
        self.description = self.get_description()
        return self.export()

    def get_main_rating(self) -> Optional[str]:
        """Returns main rating

        Returns
        -------
        Optional[str]
            main rating
        """
        try:
            return self.soup.find("span", {"class": "pvi-scrating-value"}).text
        except Exception as e:
            logger.error("Function get_main_rating : %s.", e)
            return None

    def get_rating_details(self) -> Optional[Dict[int, int]]:
        """Returns rating details

        Returns
        -------
        Optional[Dict[int, int]]
            rating details
        """
        try:
            rating_details = {
                key: int(value.text.strip())
                for (key, value) in enumerate(
                    self.soup.find("div", {"class": "pvi-scrating-graph"}).find_all("li", {"class": "elrg-graph-col"})[
                        0:10
                    ],
                    1,
                )
            }
            return rating_details
        except Exception as e:
            logger.error("Function get_rating_details : %s.", e)
            return None

    def get_vote_count(self) -> Optional[str]:
        """Returns vote count

        Returns
        -------
        Optional[str]
            vote count
        """
        try:
            return self.soup.find("meta", {"itemprop": "ratingCount"})["content"]
        except Exception as e:
            logger.error("Function get_vote_count : %s.", e)
            return None

    def get_favorite_count(self) -> Optional[str]:
        """Returns favorite count

        Returns
        -------
        Optional[str]
            favorite count
        """
        try:
            favorite_count = self.soup.find("li", {"title": "Coups de coeur"}).find("b").text
            return format_number(favorite_count)
        except Exception as e:
            logger.error("Function get_favorite_count : %s.", e)
            return None

    def get_wishlist_count(self) -> Optional[str]:
        try:
            wishlist_count = self.soup.find("li", {"title": "Envies"}).find("b").text
            return format_number(wishlist_count)
        except Exception as e:
            logger.error("Function get_wishlist_count : %s.", e)
            return None

    def get_in_progress_count(self) -> Optional[str]:
        # Tracks and movies don't have in_progress_count.
        if self.category in ["Track", "Movie"]:
            return None
        try:
            in_progress_count = self.soup.find("li", {"title": "En cours"}).find("b").text
            return format_number(in_progress_count)
        except Exception as e:
            logger.warning("Function get_in_progress_count : %s.", e)
            return None

    def get_title(self) -> Optional[str]:
        try:
            return self.soup.find("h1", {"class": "pvi-product-title"}).text.strip()
        except Exception as e:
            logger.error("Function get_title : %s.", e)
            return None

    def get_year(self) -> Optional[str]:
        try:
            return self.soup.find("small", {"class": "pvi-product-year"}).text.replace("(", "").replace(")", "")
        except Exception as e:
            logger.error("Function get_year : %s.", e)
            return None

    def get_cover_url(self) -> Optional[str]:
        try:
            return self.soup.find("img", {"class": "pvi-hero-poster"})["src"]
        except Exception as e:
            logger.error("Function get_cover_url : %s.", e)
            return None

    def get_review_count(self) -> Optional[str]:
        try:
            return self.soup.find("meta", {"itemprop": "reviewCount"})["content"]
        except Exception as e:
            logger.error("Function get_review_count : %s.", e)
            return None

    def get_description(self) -> Optional[str]:
        # Tracks and albums don't have description.
        if self.category in ["Track", "Album"]:
            return None
        try:
            return (
                self.soup.find("p", {"class": "pvi-productDetails-resume"})
                # workaround to delete text from button
                .text.replace("Lire la suite", "").strip()
            )
        except Exception as e:
            logger.error("Function get_description : %s.", e)
            return None

    def get_complementary_info(self) -> Dict:
        try:
            complementary_info = [
                i.text.replace("\n", "").replace("\t", "").strip()
                for i in self.soup.find("section", {"class": "pvi-productDetails"}).find_all("li")
            ]
            creator = ", ".join(
                [
                    x.text.strip()
                    for x in self.soup.find("section", {"class": "pvi-productDetails"})
                    .find("li")
                    .find_all("span", {"itemprop": "name"})
                ]
            )
            if self.category == "Movie":
                return {
                    "Producer": creator,
                    "Genre": complementary_info[1],
                    "Length": complementary_info[2],
                    "Release Date": complementary_info[3],
                }
            elif self.category == "Series":
                return {
                    "Producer": creator,
                    "Genre": complementary_info[1],
                    "Season Number": complementary_info[2],
                    "Editor": complementary_info[3],
                    "Episode Length": complementary_info[4],
                    "Release Date": complementary_info[5],
                }
            elif self.category == "Video Game":
                return {
                    "Developer": creator,
                    "Platforms": complementary_info[1],
                    "Genre": complementary_info[2],
                    "Release Date": complementary_info[3],
                }
            elif self.category == "Book":
                return {
                    "Writer": creator,
                    "Genre": complementary_info[1],
                    "Release Date": complementary_info[2],
                }
            elif self.category == "Comics":
                return {
                    "Writer": creator,
                    "Release Date": complementary_info[1],
                }
            elif self.category == "Music":
                return {
                    "Artist": creator,
                    "Genre": complementary_info[1],
                    "Label": complementary_info[2],
                    "Release Date": complementary_info[3],
                }
            elif self.category == "Track":
                return {
                    "Artist": creator,
                    "Length": complementary_info[1],
                    "Release Date": complementary_info[2],
                }
            else:
                logger.warning(f"Category {self.category} not supported.")
                return {}
        except Exception as e:
            logger.error("Function get_complementary_info : %s.", e)
            return {}
