"""Useful functions for generic use"""
import logging
from typing import List, Optional

from bs4 import element

logger = logging.getLogger(__name__)


def parse_baseline(row: element.Tag) -> Optional[List[str]]:
    """Parse the baseline tag of a row.

    Parameters
    ----------
    row : element.Tag
        row to consider

    Returns
    -------
    Optional[List[str]]
        baseline tag of a raw
    """
    try:
        return row.find("p", {"class": "elco-baseline"}).text.replace("\n", "").replace("\t", "").split(".")
    except Exception as exception:
        logger.debug("Function parse_baseline for row %s : %s", row, exception)
        return None


def get_baseline_0(row: element.Tag) -> Optional[str]:
    """Get the first element returned by parse_baseline.

    Parameters
    ----------
    row : element.Tag
        row to consider

    Returns
    -------
    Optional[str]
        first element of baseline
    """
    try:
        return parse_baseline(row)[0].strip()  # type: ignore
    except Exception as exception:
        logger.debug("Function get_baseline_0 for row %s : %s", row, exception)
        return None


def get_baseline_1(row: element.Tag) -> Optional[str]:
    """Get the second element returned by parse_baseline.

    Parameters
    ----------
    row : element.Tag
        row to consider

    Returns
    -------
    Optional[str]
        second element of baseline
    """
    try:
        return parse_baseline(row)[1].strip()  # type: ignore
    except Exception as exception:
        logger.debug("Function get_baseline_1 for row %s : %s", row, exception)
        return None


def get_baseline_2(row: element.Tag) -> Optional[str]:
    """Get the third element returned by parse_baseline.

    Parameters
    ----------
    row : element.Tag
        row to consider

    Returns
    -------
    Optional[str]
        third element of baseline
    """
    try:
        return parse_baseline(row)[2].strip()  # type: ignore
    except Exception as exception:
        logger.debug("Function get_baseline_2 for row %s : %s", row, exception)
        return None


def get_rank(row: element.Tag) -> Optional[str]:
    """Get the rank of a row.

    Parameters
    ----------
    row : element.Tag
        row to consider

    Returns
    -------
    Optional[str]
        rank of a row
    """
    try:
        if row.find("span", {"class": "elpo-rank-item"}):
            return row.find("span", {"class": "elpo-rank-item"}).text
        if row.find("span", {"class": "elto-rank-item"}):
            return row.find("span", {"class": "elto-rank-item"}).text
        return None
    except Exception as exception:
        logger.debug("Function get_rank for row %s : %s", row, exception)
        return None


def get_title(row: element.Tag) -> Optional[str]:
    """Get the title of a row.

    Parameters
    ----------
    row : element.Tag
        row to consider

    Returns
    -------
    Optional[str]
        row title
    """
    try:
        return row.find("a", {"class": "elco-anchor"}).text.strip()
    except Exception as exception:
        logger.debug("Function get_title for row %s : %s", row, exception)
        return None


def get_url(row: element.Tag) -> Optional[str]:
    """Get the url of a row.

    Parameters
    ----------
    row : element.Tag
        row to consider

    Returns
    -------
    Optional[str]
        url of a row
    """
    try:
        return "https://old.senscritique.com" + row.find("a", {"class": "elco-anchor"})["href"]
    except Exception as exception:
        logger.debug("Function get_url for row %s : %s", row, exception)
        return None


def get_original_title(row: element.Tag) -> Optional[str]:
    """Get the original title of a row.

    Parameters
    ----------
    row : element.Tag
        row to consider

    Returns
    -------
    Optional[str]
        original row title
    """
    try:
        if row.find("p", {"class": "elco-original-title"}):
            original_title = row.find("p", {"class": "elco-original-title"}).text.strip()
        else:
            original_title = None
    except Exception as exception:
        logger.debug("Function get_original_title for row %s : %s", row, exception)
        return None
    return original_title


def get_year(row: element.Tag) -> Optional[str]:
    """Get the release year of a row.

    Parameters
    ----------
    row : element.Tag
        row to consider

    Returns
    -------
    Optional[str]
        Release year of a row
    """
    try:
        return row.find("span", {"class": "elco-date"}).text.replace("(", "").replace(")", "")
    except Exception as exception:
        logger.debug("Function get_year for row %s : %s", row, exception)
        return None


def get_picture_url(row: element.Tag) -> Optional[str]:
    """Get the picture url of a row.

    Parameters
    ----------
    row : element.Tag
        row to consider

    Returns
    -------
    Optional[str]
        picture url of a row
    """
    try:
        if row.select("img"):
            try:
                picture_url = row.find("img")["src"]
            except Exception as exception:
                logger.debug(exception)
                picture_url = row.find("img")["data-original"]
        else:
            picture_url = None
    except Exception as exception:
        logger.debug("Function get_picture_url for row %s : %s", row, exception)
        picture_url = None
    return picture_url


def get_genre(row: element.Tag) -> Optional[str]:
    """Get the genre of a row.

    Parameters
    ----------
    row : element.Tag
        row to consider

    Returns
    -------
    Optional[str]
        row genre
    """
    try:
        if not get_number_of_seasons(row):
            genre = parse_baseline(row)[2].strip()  # type: ignore
        else:
            genre = parse_baseline(row)[3].strip()  # type: ignore
    except Exception as exception:
        logger.debug("Function get_genre for row %s : %s", row, exception)
        genre = None
    return genre


def get_producer(row: element.Tag) -> Optional[str]:
    """Get the producer/author of a row.

    Parameters
    ----------
    row : element.Tag
        row to consider

    Returns
    -------
    Optional[str]
        producer or author of a row
    """
    try:
        if row.find("span", {"class": "elco-baseline-a"}):
            producer = ", ".join([x.text.strip() for x in row.find_all("span", {"class": "elco-baseline-a"})])
        else:
            producer = ", ".join([x.text.strip() for x in row.find_all("a", {"class": "elco-baseline-a"})])
    except Exception as exception:
        logger.debug("Function get_producer for row %s : %s", row, exception)
        producer = None
    return producer


def get_description(row: element.Tag) -> Optional[str]:
    """Get the description of a row.

    Parameters
    ----------
    row : element.Tag
        row to consider

    Returns
    -------
    Optional[str]
        row description
    """
    try:
        description = row.find("p", {"class": "elco-description"}).text.strip()
    except Exception as exception:
        logger.debug("Function get_description for row %s : %s", row, exception)
        description = None
    return description


def get_average_rating(row: element.Tag) -> Optional[str]:
    """Get the average rating of a row.

    Parameters
    ----------
    row : element.Tag
        row to consider

    Returns
    -------
    Optional[str]
       average rating of a row
    """
    try:
        average_rating = row.find("a", {"class": "erra-global"}).text.strip()
    except Exception as exception:
        logger.debug("Function get_average_rating for row %s : %s", row, exception)
        average_rating = None
    return average_rating


def get_number_of_ratings(row: element.Tag) -> Optional[str]:
    """Get the number of ratings of a row.

    Parameters
    ----------
    row : element.Tag
        row to consider

    Returns
    -------
    Optional[str]
        number of rating of a row
    """
    try:
        number_of_ratings = row.find("a", {"class": "erra-global"})["title"].split()[-2]
    except Exception as exception:
        logger.debug("Function get_number_of_ratings for row %s : %s", row, exception)
        number_of_ratings = None
    return number_of_ratings


def get_number_of_seasons(row: element.Tag) -> Optional[str]:
    """Get the number of seasons of a row.

    Parameters
    ----------
    row : element.Tag
        row to consider

    Returns
    -------
    Optional[str]
        number of seasons of a row
    """
    try:
        number_of_seasons = parse_baseline(row)[2].strip()  # type: ignore
        if not any(i.isdigit() for i in number_of_seasons):
            return None
    except Exception as exception:
        logger.debug("Function get_number_of_seasons for row %s : %s", row, exception)
        number_of_seasons = None
    return number_of_seasons


def get_platforms(row: element.Tag) -> Optional[str]:
    """Get the supported platforms of a collection row.

    Parameters
    ----------
    row : element.Tag
        row to consider

    Returns
    -------
    Optional[str]
        supported plateforms
    """
    try:
        platforms = row.find("span", {"class": "elco-gamesystem"}).text.strip()
    except Exception as exception:
        logger.debug("Function get_platforms for row %s : %s", row, exception)
        platforms = None
    return platforms


def get_topchart_platforms(row: element.Tag) -> Optional[str]:
    """Get the supported platforms of a topchart row.

    Parameters
    ----------
    row : element.Tag
        row to consider

    Returns
    -------
    Optional[str]
        supported plateform
    """
    try:
        platforms = row.find_all("p", {"class": "elco-baseline"})[1].text.split("sur")[-1].strip()
    except Exception as exception:
        logger.debug("Function get_topchart_platforms for row %s : %s", row, exception)
        platforms = None
    return platforms
