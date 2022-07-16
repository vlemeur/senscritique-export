import logging
from typing import Dict, List

from bs4 import element

from . import row_utils

logger = logging.getLogger(__name__)


def get_videogames_infos_from_row(row: element.Tag) -> Dict:
    """Returns a dict containing infos for a videogame row.

    Parameters
    ----------
    row : element.Tag
        row to consider

    Returns
    -------
    Dict
        videogame row infos
    """
    return {
        "Rank": row_utils.get_rank(row),
        "Title": row_utils.get_title(row),
        "URL": row_utils.get_url(row),
        "Original Title": row_utils.get_original_title(row),
        "Year": row_utils.get_year(row),
        "Release Date": row_utils.get_baseline_0(row),
        "Picture URL": row_utils.get_picture_url(row),
        "Genre": row_utils.get_baseline_1(row),
        "Developer": row_utils.get_producer(row),
        "Platforms": row_utils.get_platforms(row),
        "Description": row_utils.get_description(row),
        "Average Rating": row_utils.get_average_rating(row),
        "Number of Ratings": row_utils.get_number_of_ratings(row),
    }


def get_videogames_topchart_infos_from_row(row: element.Tag) -> Dict:
    """Returns a dict containing infos for a videogame row.

    Workaround to properly extract infos from a topchart.
    Previously the platform function was compatible with both
    collection and topchart, but as of early February 2022 the format
    has changed between both.

    Parameters
    ----------
    row : element.Tag
        row to consider

    Returns
    -------
    Dict
        videogame row infos
    """
    return {
        "Rank": row_utils.get_rank(row),
        "Title": row_utils.get_title(row),
        "URL": row_utils.get_url(row),
        "Original Title": row_utils.get_original_title(row),
        "Year": row_utils.get_year(row),
        "Release Date": row_utils.get_baseline_0(row),
        "Picture URL": row_utils.get_picture_url(row),
        "Genre": row_utils.get_baseline_1(row),
        "Developer": row_utils.get_producer(row),
        "Platforms": row_utils.get_topchart_platforms(row),
        "Description": row_utils.get_description(row),
        "Average Rating": row_utils.get_average_rating(row),
        "Number of Ratings": row_utils.get_number_of_ratings(row),
    }


def get_order_videogames_columns() -> List:
    """Returns the order of columns for videogames rows.

    Returns
    -------
    List
       videogames order column
    """
    return [
        "Rank",
        "Title",
        "Developer",
        "Platforms",
        "Average Rating",
        "Number of Ratings",
        "URL",
        "Original Title",
        "Year",
        "Release Date",
        "Picture URL",
        "Genre",
        "Description",
    ]
