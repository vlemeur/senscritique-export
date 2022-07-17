"""Useful functions for videogames items"""
import logging
from typing import Dict, List

from bs4 import element

import senscritique_export.constants as cst

from . import row_utils

logger = logging.getLogger(__name__)


def get_videogames_info_from_row(row: element.Tag) -> Dict:
    """Returns a dict containing info for a videogame row.

    Parameters
    ----------
    row : element.Tag
        row to consider

    Returns
    -------
    Dict
        videogame row info
    """
    return {
        cst.RANK: row_utils.get_rank(row),
        cst.TITLE: row_utils.get_title(row),
        cst.URL: row_utils.get_url(row),
        cst.ORIGINAL_TITLE: row_utils.get_original_title(row),
        cst.YEAR: row_utils.get_year(row),
        cst.RELEASE_DATE: row_utils.get_baseline_0(row),
        cst.PICTURE_URL: row_utils.get_picture_url(row),
        cst.GENRE: row_utils.get_baseline_1(row),
        cst.DEVELOPER: row_utils.get_producer(row),
        cst.PLATEFORMS: row_utils.get_platforms(row),
        cst.DESCRIPTION: row_utils.get_description(row),
        cst.AVERAGE_RATING: row_utils.get_average_rating(row),
        cst.NB_RATINGS: row_utils.get_number_of_ratings(row),
    }


def get_videogames_topchart_info_from_row(row: element.Tag) -> Dict:
    """Returns a dict containing info for a videogame row.

    Workaround to properly extract info from a topchart.
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
        videogame row info
    """
    return {
        cst.RANK: row_utils.get_rank(row),
        cst.TITLE: row_utils.get_title(row),
        cst.URL: row_utils.get_url(row),
        cst.ORIGINAL_TITLE: row_utils.get_original_title(row),
        cst.YEAR: row_utils.get_year(row),
        cst.RELEASE_DATE: row_utils.get_baseline_0(row),
        cst.PICTURE_URL: row_utils.get_picture_url(row),
        cst.GENRE: row_utils.get_baseline_1(row),
        cst.DEVELOPER: row_utils.get_producer(row),
        cst.PLATEFORMS: row_utils.get_topchart_platforms(row),
        cst.DESCRIPTION: row_utils.get_description(row),
        cst.AVERAGE_RATING: row_utils.get_average_rating(row),
        cst.NB_RATINGS: row_utils.get_number_of_ratings(row),
    }


def get_order_videogames_columns() -> List:
    """Returns the order of columns for videogames rows.

    Returns
    -------
    List
       videogames order column
    """
    return [
        cst.RANK,
        cst.TITLE,
        cst.DEVELOPER,
        cst.PLATEFORMS,
        cst.AVERAGE_RATING,
        cst.NB_RATINGS,
        cst.URL,
        cst.ORIGINAL_TITLE,
        cst.YEAR,
        cst.RELEASE_DATE,
        cst.PICTURE_URL,
        cst.GENRE,
        cst.DESCRIPTION,
    ]
