"""Define a Work class"""
import logging
from typing import Dict, Optional

from senscritique_export.utils import format_number, get_soup

logger = logging.getLogger(__name__)


class Work:  # pylint: disable=too-many-instance-attributes
    """
    Worker used for generic purposes
    """

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
            result = "Movie"
        elif category == "serie":
            result = "Series"
        elif category == "jeuvideo":
            result = "Video Game"
        elif category == "livre":
            result = "Book"
        elif category == "bd":
            result = "Comics"
        elif category == "album":
            result = "Music"
        elif category == "morceau":
            result = "Track"
        return result

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
        except Exception as exception:
            logger.error("Function get_main_rating : %s.", exception)
            return None

    def get_rating_details(self) -> Optional[Dict[int, int]]:
        """Returns rating details

        Returns
        -------
        Optional[Dict[int, int]]
            rating details
        """
        try:
            return {
                key: int(value.text.strip())
                for key, value in enumerate(
                    self.soup.find("div", {"class": "pvi-scrating-graph"}).find_all("li", {"class": "elrg-graph-col"})[
                        :10
                    ],
                    1,
                )
            }

        except Exception as exception:
            logger.error("Function get_rating_details : %s.", exception)
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
        except Exception as exception:
            logger.error("Function get_vote_count : %s.", exception)
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
        except Exception as exception:
            logger.error("Function get_favorite_count : %s.", exception)
            return None

    def get_wishlist_count(self) -> Optional[str]:
        """Returns wish-list count

        Returns
        -------
        Optional[str]
            wish-list count
        """
        try:
            wishlist_count = self.soup.find("li", {"title": "Envies"}).find("b").text
            return format_number(wishlist_count)
        except Exception as exception:
            logger.error("Function get_wishlist_count : %s.", exception)
            return None

    def get_in_progress_count(self) -> Optional[str]:
        """Return progress count

        Returns
        -------
        Optional[str]
            progress count
        """
        # Tracks and movies don't have in_progress_count.
        if self.category in ["Track", "Movie"]:
            return None
        try:
            in_progress_count = self.soup.find("li", {"title": "En cours"}).find("b").text
            return format_number(in_progress_count)
        except Exception as exception:
            logger.warning("Function get_in_progress_count : %s.", exception)
            return None

    def get_title(self) -> Optional[str]:
        """Returns title

        Returns
        -------
        Optional[str]
            title
        """
        try:
            return self.soup.find("h1", {"class": "pvi-product-title"}).text.strip()
        except Exception as exception:
            logger.error("Function get_title : %s.", exception)
            return None

    def get_year(self) -> Optional[str]:
        """Returns year

        Returns
        -------
        Optional[str]
            year
        """
        try:
            return self.soup.find("small", {"class": "pvi-product-year"}).text.replace("(", "").replace(")", "")
        except Exception as exception:
            logger.error("Function get_year : %s.", exception)
            return None

    def get_cover_url(self) -> Optional[str]:
        """Returns cover url

        Returns
        -------
        Optional[str]
            cover url
        """
        try:
            return self.soup.find("img", {"class": "pvi-hero-poster"})["src"]
        except Exception as exception:
            logger.error("Function get_cover_url : %s.", exception)
            return None

    def get_review_count(self) -> Optional[str]:
        """Returns review count

        Returns
        -------
        Optional[str]
            review count
        """
        try:
            return self.soup.find("meta", {"itemprop": "reviewCount"})["content"]
        except Exception as exception:
            logger.error("Function get_review_count : %s.", exception)
            return None

    def get_description(self) -> Optional[str]:
        """Returns description

        Returns
        -------
        Optional[str]
            description
        """
        # Tracks and albums don't have description.
        if self.category in ["Track", "Album"]:
            return None
        try:
            return (
                self.soup.find("p", {"class": "pvi-productDetails-resume"})
                # workaround to delete text from button
                .text.replace("Lire la suite", "").strip()
            )
        except Exception as exception:
            logger.error("Function get_description : %s.", exception)
            return None

    def get_complementary_info(self) -> Dict:  # pylint: disable=too-many-return-statements
        """Returns complementary info

        Returns
        -------
        Dict
            complementary info
        """
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
            if self.category == "Series":
                return {
                    "Producer": creator,
                    "Genre": complementary_info[1],
                    "Season Number": complementary_info[2],
                    "Editor": complementary_info[3],
                    "Episode Length": complementary_info[4],
                    "Release Date": complementary_info[5],
                }
            if self.category == "Video Game":
                return {
                    "Developer": creator,
                    "Platforms": complementary_info[1],
                    "Genre": complementary_info[2],
                    "Release Date": complementary_info[3],
                }
            if self.category == "Book":
                return {
                    "Writer": creator,
                    "Genre": complementary_info[1],
                    "Release Date": complementary_info[2],
                }
            if self.category == "Comics":
                return {
                    "Writer": creator,
                    "Release Date": complementary_info[1],
                }
            if self.category == "Music":
                return {
                    "Artist": creator,
                    "Genre": complementary_info[1],
                    "Label": complementary_info[2],
                    "Release Date": complementary_info[3],
                }
            if self.category == "Track":
                return {
                    "Artist": creator,
                    "Length": complementary_info[1],
                    "Release Date": complementary_info[2],
                }
            logger.warning(f"Category {self.category} not supported.")
            return {}
        except Exception as exception:
            logger.error("Function get_complementary_info : %s.", exception)
            return {}
