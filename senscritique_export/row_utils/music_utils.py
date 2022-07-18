"""Useful functions of music items"""
import logging
from typing import Dict, List

from bs4 import element

import senscritique_export.constants as cst

from . import row_utils

logger = logging.getLogger(__name__)


def get_music_info_from_row(row: element.Tag) -> Dict:
    """Returns a dict containing info for a music row.

    Parameters
    ----------
    row : element.Tag
        row to consider

    Returns
    -------
    Dict
        music row info
    """
    return {
        cst.RANK: row_utils.get_rank(row),
        cst.TITLE: row_utils.get_title(row),
        cst.URL: row_utils.get_url(row),
        cst.YEAR: row_utils.get_year(row),
        cst.RELEASE_DATE: row_utils.get_baseline_0(row),
        cst.GENRE: row_utils.get_baseline_1(row),
        cst.NB_SONGS: row_utils.get_number_of_seasons(row),
        cst.PICTURE_URL: row_utils.get_picture_url(row),
        cst.ARTIST: row_utils.get_producer(row),
        cst.AVERAGE_RATING: row_utils.get_average_rating(row),
        cst.NB_RATINGS: row_utils.get_number_of_ratings(row),
    }


def get_order_music_columns() -> List:
    """Returns the order of columns for music rows.

    Returns
    -------
    List
        order columns for music rows
    """
    return [
        cst.RANK,
        cst.TITLE,
        cst.AVERAGE_RATING,
        cst.NB_RATINGS,
        cst.URL,
        cst.YEAR,
        cst.RELEASE_DATE,
        cst.GENRE,
        cst.NB_SONGS,
        cst.PICTURE_URL,
        cst.ARTIST,
    ]
