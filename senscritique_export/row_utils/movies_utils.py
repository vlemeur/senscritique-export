import logging
from typing import Dict, List

from bs4 import element

from . import row_utils

logger = logging.getLogger(__name__)


def get_movies_info_from_row(row: element.Tag) -> Dict:
    """Returns a dict containing info for a movie row.

    Parameters
    ----------
    row : element.Tag
        row to consider

    Returns
    -------
    Dict
        movie row info
    """
    return {
        "Rank": row_utils.get_rank(row),
        "Title": row_utils.get_title(row),
        "URL": row_utils.get_url(row),
        "Original Title": row_utils.get_original_title(row),
        "Year": row_utils.get_year(row),
        "Release Date": row_utils.get_baseline_1(row),
        "Length": row_utils.get_baseline_0(row),
        "Picture URL": row_utils.get_picture_url(row),
        "Genre": row_utils.get_genre(row),
        "Producer": row_utils.get_producer(row),
        "Description": row_utils.get_description(row),
        "Average Rating": row_utils.get_average_rating(row),
        "Number of Ratings": row_utils.get_number_of_ratings(row),
    }


def get_order_movies_columns() -> List:
    """Returns the order of columns for movies rows.

    Returns
    -------
    List
        order of columns for movies rows
    """
    return [
        "Rank",
        "Title",
        "Producer",
        "Average Rating",
        "Number of Ratings",
        "URL",
        "Original Title",
        "Year",
        "Release Date",
        "Length",
        "Picture URL",
        "Genre",
        "Description",
    ]
