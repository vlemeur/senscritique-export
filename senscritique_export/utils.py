import difflib
import logging
import urllib
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup, element

from senscritique_export.row_utils.books_utils import get_books_infos_from_row, get_order_books_columns
from senscritique_export.row_utils.comics_utils import get_comics_infos_from_row, get_order_comics_columns
from senscritique_export.row_utils.movies_utils import get_movies_infos_from_row, get_order_movies_columns
from senscritique_export.row_utils.music_utils import get_music_infos_from_row, get_order_music_columns
from senscritique_export.row_utils.series_utils import get_order_series_columns, get_series_infos_from_row
from senscritique_export.row_utils.track_utils import get_track_infos_from_row
from senscritique_export.row_utils.videogames_utils import (
    get_order_videogames_columns,
    get_videogames_infos_from_row,
    get_videogames_topchart_infos_from_row,
)

logger = logging.getLogger(__name__)


def get_soup(url: str) -> BeautifulSoup:
    """Returns a BeautifulSoup object for an url."""
    return BeautifulSoup(requests.get(url).content, "lxml")


def format_number(number: str) -> str:
    if "K" in number and "." in number:
        return number.replace("K", "").replace(".", "") + "00"
    elif "K" in number and "." not in number:
        return number.replace("K", "") + "000"
    else:
        return number


def get_collection_current_page_number(soup: BeautifulSoup) -> Optional[int]:
    """Returns the senscritique page number of a BeautifulSoup object."""
    try:
        page_number = int(soup.find("span", {"class": "eipa-current"}).text)
        logger.info("Current collection page number : %s", page_number)
        return page_number
    except Exception as e:
        logger.error(e)
        return None


def get_dict_available_pages(soup: BeautifulSoup) -> Dict[int, str]:
    """Returns a dict of the available pages in a BeautifulSoup object."""
    dict_links = {
        int(x["data-sc-pager-page"]): "https://old.senscritique.com" + x["href"]
        for x in soup.find_all("a", {"class": "eipa-anchor"})
    }
    return dict_links


def get_next_collection_link(soup: BeautifulSoup) -> Optional[str]:
    """Returns the next link of BeautifulSoup object."""
    available_pages = get_dict_available_pages(soup)
    current_page = get_collection_current_page_number(soup)
    if current_page:
        if available_pages.get(current_page + 1):
            return available_pages.get(current_page + 1)
    return None


def get_next_collection_soup(soup: BeautifulSoup) -> BeautifulSoup:
    """Returns the next BeautifulSoup object for an user collection."""
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
    """Returns a list of rows from a collection."""
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


def get_collection_infos(soup: BeautifulSoup) -> List[Dict]:
    """Returns a list of dict containing an user collection information."""
    rows = get_rows_from_collection(soup)
    list_infos = []
    for row in rows:
        info = get_row_infos(row)
        if info:
            list_infos.append(info)
    return list_infos


def get_collection_order():
    """Returns the order of columns for a collection (not implemented yet)."""
    return None


def get_category(row: element.Tag) -> str:
    return row.find("a", {"class": "elco-anchor"})["href"].split("/")[1]


def get_row_infos(row: element.Tag) -> Optional[Dict]:
    """Returns a dict containing a row information."""
    logger.debug("get_row_infos")
    category = get_category(row)
    if category == "film":
        row_info = {
            **get_movies_infos_from_row(row),
            **get_complementary_infos_collection(row),
            **{"Category": "Movie"},
        }
    elif category == "serie":
        row_info = {
            **get_series_infos_from_row(row),
            **get_complementary_infos_collection(row),
            **{"Category": "Series"},
        }
    elif category == "jeuvideo":
        row_info = {
            **get_videogames_infos_from_row(row),
            **get_complementary_infos_collection(row),
            **{"Category": "Video Game"},
        }
    elif category == "livre":
        row_info = {
            **get_books_infos_from_row(row),
            **get_complementary_infos_collection(row),
            **{"Category": "Book"},
        }
    elif category == "bd":
        row_info = {
            **get_comics_infos_from_row(row),
            **get_complementary_infos_collection(row),
            **{"Category": "Comics"},
        }
    elif category == "album":
        row_info = {
            **get_music_infos_from_row(row),
            **get_complementary_infos_collection(row),
            **{"Category": "Music"},
        }
    elif category == "morceau":
        row_info = {
            **get_track_infos_from_row(row),
            **get_complementary_infos_collection(row),
            **{"Category": "Track"},
        }
    else:
        logger.error(f"Category {category} not supported.")
        return None
    # row_info.pop("Description", None)
    # row_info.pop("Rank", None)
    return row_info


def get_complementary_infos_collection(row: element.Tag) -> Dict:
    """Get information specific to a collection row."""
    action = row.find("div", {"class": "elco-collection-rating user"}).find(
        "span", {"class": "elrua-useraction-inner only-child"}
    )

    dict_infos = {}
    if action.find("span", {"class": "eins-wish-list"}):
        dict_infos["User Action"] = "Wishlisted"
    elif action.find("span", {"class": "eins-current"}):
        dict_infos["User Action"] = "In Progress"
    else:
        dict_infos["User Action"] = "Rated"

    dict_infos["Recommended"] = "True" if action.find("span", {"class": "eins-user-recommend"}) else "False"

    dict_infos["User Rating"] = action.text.strip()
    logger.debug(dict_infos)
    return dict_infos


def get_list_work_current_page_number(soup: BeautifulSoup) -> Optional[int]:
    """Returns the senscritique page number of a BeautifulSoup object."""
    try:
        page_number = int(soup.find("span", {"class": "eipa-current"}).text)
        logger.info("Current list_work page number : %s", page_number)
        return page_number
    except Exception as e:
        logger.error(f"get_list_work_current_page_number: {e}")
        return None


def get_dict_available_pages(soup: BeautifulSoup) -> Dict[int, str]:
    """Returns a dict of the available pages in a BeautifulSoup object."""
    dict_links = {
        int(x["data-sc-pager-page"]): "https://old.senscritique.com" + x["href"]
        for x in soup.find_all("a", {"class": "eipa-anchor"})
    }
    return dict_links


def get_next_list_work_link(soup: BeautifulSoup) -> Optional[str]:
    """Returns the next link of BeautifulSoup object."""
    available_pages = get_dict_available_pages(soup)
    logger.debug("Available pages : %s.", available_pages)
    current_page = get_list_work_current_page_number(soup)
    if current_page:
        if available_pages.get(current_page + 1):
            return available_pages.get(current_page + 1)
    return None


def get_next_list_work_soup(soup: BeautifulSoup) -> BeautifulSoup:
    """Returns the next BeautifulSoup object for an user list_work."""
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
    """Returns a list of rows from a list_work."""
    logger.debug("get_rows_from_list_work")
    list_rows = []
    while True:
        for row in soup.find_all("li", {"class": "elpr-item"}):
            list_rows.append(get_row_infos(row))
        soup = get_next_list_work_soup(soup)
        if not soup:
            logger.debug("No rows here. Either it is the last page, the url is not valid or the list_work is private.")
            break
    return list_rows


def get_list_work_infos(soup: BeautifulSoup) -> List[Dict]:
    """Returns a list of dict containing an user list_work information."""
    rows = get_rows_from_list_work(soup)
    return rows


def get_list_work_order():
    """Returns the order of columns for a list_work (not implemented yet)."""
    return None


def get_category(row: element.Tag) -> str:
    return row.find("a", {"class": "elco-anchor"})["href"].split("/")[1]


def get_row_infos(row: element.Tag) -> Optional[Dict]:
    """Returns a dict containing a row information."""
    logger.debug("get_row_infos")
    category = get_category(row)
    if category == "film":
        logger.debug("films")
        row_info = {
            **get_movies_infos_from_row(row),
            **{"Category": "Movie"},
        }
    elif category == "serie":
        logger.debug("series")
        row_info = {
            **get_series_infos_from_row(row),
            **{"Category": "Series"},
        }
    elif category == "jeuvideo":
        logger.debug("jeuxvideo")
        row_info = {
            **get_videogames_infos_from_row(row),
            **{"Category": "Video Game"},
        }
    elif category == "livre":
        logger.debug("livres")
        row_info = {
            **get_books_infos_from_row(row),
            **{"Category": "Book"},
        }
    elif category == "bd":
        logger.debug("bd")
        row_info = {
            **get_comics_infos_from_row(row),
            **{"Category": "Comics"},
        }
    elif category == "album":
        logger.debug("musique")
        row_info = {
            **get_music_infos_from_row(row),
            **{"Category": "Music"},
        }
    else:
        logger.error(f"Error: unsupported category {category}. Skipping.")
        return None
    row_info.pop("Description", None)
    row_info.pop("Rank", None)
    return row_info


GENRE_CHOICES = ["Morceaux", "Albums", "Films", "Livres", "Séries", "BD", "Jeux"]


def sanitize_text(text: str) -> str:
    """Sanitize text to URL-compatible text."""
    return urllib.parse.quote_plus(text)


def get_search_url(search_term: str, genre: str = None) -> str:
    """Returns the senscritique search URL for a search term."""
    search_term_sanitized = sanitize_text(search_term)
    if genre not in GENRE_CHOICES:
        url = f"https://old.senscritique.com/search?q={search_term_sanitized}"
    else:
        url = f"https://old.senscritique.com/search?q={search_term_sanitized}&categories[0][0]={genre}"
    return url


def get_search_result(soup: BeautifulSoup, position: int) -> Optional[str]:
    """Returns the URL result of the BeautifulSoup object at the defined position."""
    try:
        url_list = [
            x.find_all("a")[1]["href"]
            for x in soup.find_all("div", {"class": "ProductListItem__Container-sc-1ci68b-0"})
        ]
        if position > len(url_list):
            logger.error(
                f"Desired result not found in search results (Desired result: position {position}, number of search results: {len(url_list)})."
            )
            return None
        return url_list[position - 1]
    except Exception as e:
        logger.error(e)
        return None


def get_closest_search_result(soup: BeautifulSoup, search_term: str) -> Optional[str]:
    """Returns the closest result of the results for the search_term."""
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
    """Returns a list of rows from a survey."""
    return soup.find("ol", {"class": "pvi-list"}).find_all("li", {"class": "elpo-item"})


def get_category_from_survey(soup: BeautifulSoup) -> str:
    return soup.find("li", {"class": "header-navigation-universe-current"}).find("a")["href"].split("/")[-1]


def get_survey_infos(soup: BeautifulSoup, category: str) -> List[Dict]:
    """Returns a list of dict containing data of a survey."""
    rows = get_rows_from_survey(soup)
    if category == "films":
        list_infos = [get_movies_infos_from_row(x) for x in rows]
    elif category == "series":
        list_infos = [get_series_infos_from_row(x) for x in rows]
    elif category == "jeuxvideo":
        list_infos = [get_videogames_infos_from_row(x) for x in rows]
    elif category == "livres":
        list_infos = [get_books_infos_from_row(x) for x in rows]
    elif category == "bd":
        list_infos = [get_comics_infos_from_row(x) for x in rows]
    elif category == "musique":
        list_infos = [get_music_infos_from_row(x) for x in rows]
    else:
        logger.error(f"Category {category} not supported.")
        return []
    return list_infos


def get_survey_order(category: str) -> List:
    """Returns the order of columns for a survey based on its category."""
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
    """Returns a list of rows from a topchart."""
    return soup.find("ol", {"class": "elto-list"}).find_all("li", {"class": "elto-item"})


def get_topchart_infos(soup: BeautifulSoup, category: str) -> List[Dict]:
    """Returns a list of dict containing data of a topchart."""
    rows = get_rows_from_topchart(soup)
    if category == "films":
        return [get_movies_infos_from_row(x) for x in rows]
    elif category == "series":
        return [get_series_infos_from_row(x) for x in rows]
    elif category == "jeuxvideo":
        return [get_videogames_topchart_infos_from_row(x) for x in rows]
    elif category == "livres":
        return [get_books_infos_from_row(x) for x in rows]
    elif category == "bd":
        return [get_comics_infos_from_row(x) for x in rows]
    elif category == "musique":
        return [get_music_infos_from_row(x) for x in rows]
    else:
        logger.error(f"Category {category} not supported.")
        return []


def get_topchart_order(category: str) -> List:
    """Returns the order of columns for a topchart based on its category."""
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

    def export(self):
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
            **self.get_complementary_infos(),
            **{"Category": self.category},
        }

    def get_category(self):
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

    def get_details(self):
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
        try:
            return self.soup.find("span", {"class": "pvi-scrating-value"}).text
        except Exception as e:
            logger.error("Function get_main_rating : %s.", e)
            return None

    def get_rating_details(self) -> Optional[Dict[int, int]]:
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
        try:
            return self.soup.find("meta", {"itemprop": "ratingCount"})["content"]
        except Exception as e:
            logger.error("Function get_vote_count : %s.", e)
            return None

    def get_favorite_count(self) -> Optional[str]:
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

    def get_complementary_infos(self) -> Dict:
        try:
            complementary_infos = [
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
                    "Genre": complementary_infos[1],
                    "Length": complementary_infos[2],
                    "Release Date": complementary_infos[3],
                }
            elif self.category == "Series":
                return {
                    "Producer": creator,
                    "Genre": complementary_infos[1],
                    "Season Number": complementary_infos[2],
                    "Editor": complementary_infos[3],
                    "Episode Length": complementary_infos[4],
                    "Release Date": complementary_infos[5],
                }
            elif self.category == "Video Game":
                return {
                    "Developer": creator,
                    "Platforms": complementary_infos[1],
                    "Genre": complementary_infos[2],
                    "Release Date": complementary_infos[3],
                }
            elif self.category == "Book":
                return {
                    "Writer": creator,
                    "Genre": complementary_infos[1],
                    "Release Date": complementary_infos[2],
                }
            elif self.category == "Comics":
                return {
                    "Writer": creator,
                    "Release Date": complementary_infos[1],
                }
            elif self.category == "Music":
                return {
                    "Artist": creator,
                    "Genre": complementary_infos[1],
                    "Label": complementary_infos[2],
                    "Release Date": complementary_infos[3],
                }
            elif self.category == "Track":
                return {
                    "Artist": creator,
                    "Length": complementary_infos[1],
                    "Release Date": complementary_infos[2],
                }
            else:
                logger.warning(f"Category {self.category} not supported.")
                return {}
        except Exception as e:
            logger.error("Function get_complementary_infos : %s.", e)
            return {}
