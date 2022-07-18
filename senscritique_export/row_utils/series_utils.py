"""Useful functions for series items"""
import logging
from typing import Dict, List

from bs4 import element

import senscritique_export.constants as cst

from . import row_utils

logger = logging.getLogger(__name__)


def get_series_info_from_row(row: element.Tag) -> Dict:
    """Returns a dict containing info for a series row.

    Parameters
    ----------
    row : element.Tag
        row to consider

    Returns
    -------
    Dict
        info for a series row
    """
    return {
        cst.RANK: row_utils.get_rank(row),
        cst.TITLE: row_utils.get_title(row),
        cst.URL: row_utils.get_url(row),
        cst.ORIGINAL_TITLE: row_utils.get_original_title(row),
        cst.YEAR: row_utils.get_year(row),
        cst.RELEASE_DATE: row_utils.get_baseline_1(row),
        cst.NB_SEASONS: row_utils.get_number_of_seasons(row),
        cst.PICTURE_URL: row_utils.get_picture_url(row),
        cst.GENRE: row_utils.get_genre(row),
        cst.PRODUCER: row_utils.get_producer(row),
        cst.DESCRIPTION: row_utils.get_description(row),
        cst.AVERAGE_RATING: row_utils.get_average_rating(row),
        cst.NB_RATINGS: row_utils.get_number_of_ratings(row),
    }


def get_order_series_columns() -> List:
    """Returns the order of columns for series rows.

    Returns
    -------
    List
       columns order for series rows
    """
    return [
        cst.RANK,
        cst.TITLE,
        cst.PRODUCER,
        cst.AVERAGE_RATING,
        cst.NB_RATINGS,
        cst.URL,
        cst.ORIGINAL_TITLE,
        cst.YEAR,
        cst.RELEASE_DATE,
        cst.NB_SEASONS,
        cst.PICTURE_URL,
        cst.GENRE,
        cst.DESCRIPTION,
    ]
