"""This module aims to fill and get data from a Notion Database"""
import logging
from datetime import datetime
from typing import List, Optional

import pandas as pd
from notion_df import config, download, upload

import senscritique_export.constants as cst
from senscritique_export.scrapper import get_user_collection

logger = logging.getLogger(__name__)


def remove_accent_from_df(df: pd.DataFrame) -> pd.DataFrame:
    """Remove all accents from data entries

    Parameters
    ----------
    df : pd.DataFrame
        series data

    Returns
    -------
    pd.DataFrame
        series data without accent
    """
    return df.apply(lambda x: x.str.normalize("NFKD").str.encode("ascii", errors="ignore").str.decode("utf-8"))


def get_df_from_notion(notion_database_url: str, api_key: Optional[str] = None) -> pd.DataFrame:
    """Get notion database from url

    Parameters
    ----------
    notion_database_url : str
        url to notion database
    api_key : Optional[str], optional
        notion API key, by default None

    Returns
    -------
    pd.DataFrame
        notion database
    """
    if api_key is not None:
        config(api_key=api_key)
    return download(notion_database_url).dropna(how="all")


def convert_french_date_to_str(french_date: str) -> str:
    """Convert french letter string date to proposer string date

    Parameters
    ----------
    french_date : str
        french letter string date

    Returns
    -------
    str
        string date
    """

    french_date = french_date.replace(" (France)", "").replace(" (Etats-Unis)", "")
    french_split = french_date.split(" ")
    if len(french_split) == 1:
        year = french_split[0]
        day = 1
        month = 1
    else:
        day, month, year = french_split  # type: ignore
        month = cst.FRENCH_MONTHS[month]  # type: ignore
        day = int(day)
    year = int(year)  # type: ignore

    return datetime(year=year, month=month, day=day).strftime("%m/%d/%Y")  # type: ignore


def convert_nb_seasons(nb_seasons: str) -> int:
    """Converts number of seasons to int

    Parameters
    ----------
    nb_seasons : str
        number of seasons in letter

    Returns
    -------
    int
        number of seasons
    """
    return None if nb_seasons is None else int(nb_seasons.split(" ")[0])


def convert_genre(genre: str) -> str:
    """Replace coma by space in genre string

    Parameters
    ----------
    genre : str
        series genre

    Returns
    -------
    str
        series genre without comma
    """
    return genre.replace(",", " ")


def prepare_sens_critique_series(user: str, target_columns: List[str], api_key: Optional[str] = None) -> pd.DataFrame:
    """Perform all conversion before upload to notion

    Parameters
    ----------
    user : str
        senscritique user name
    target_columns : List[str]
        columns to consider
    api_key : Optional[str], optional
        notion API key, by default None

    Returns
    -------
    pd.DataFrame
        senscritique series data ready to be uploaded to notion
    """

    if api_key is not None:
        config(api_key=api_key)
    df_sens_critique = pd.DataFrame(get_user_collection(user=user))
    df_series = df_sens_critique[df_sens_critique[cst.CATEGORY] == "Series"].loc[:, target_columns]
    df_series = remove_accent_from_df(df=df_series)
    df_series[cst.RELEASE_DATE] = df_series[cst.RELEASE_DATE].apply(lambda x: convert_french_date_to_str(x))
    df_series[cst.NB_SEASONS] = df_series[cst.NB_SEASONS].apply(lambda x: convert_nb_seasons(x))
    df_series[cst.GENRE] = df_series[cst.GENRE].apply(lambda x: convert_genre(x))

    df_series = df_series.astype(dtype=cst.SERIES_TYPES, errors="ignore")
    return df_series


def update_notion_db_series(notion_database_url: str, api_key: str, user: str, title_page: str):
    """Updates a notion series database from senscritique

    Parameters
    ----------
    notion_database_url : str
        url to notion database
    api_key : str
        notion API key
    user : str
        senscritique user name
    title_page : str
        Name of notion series database page
    """
    config(api_key=api_key)
    logger.info("Getting existing entries from notion")
    df_notion = get_df_from_notion(notion_database_url=notion_database_url)

    logger.info("Getting existing entries from senscritique")
    df_series = prepare_sens_critique_series(user=user, target_columns=df_notion.columns.tolist())

    df_diff = pd.concat(objs=[df_notion, df_series])
    # Necessary to convert list to string
    df_diff = df_diff.loc[df_diff.astype(str).drop_duplicates(keep=False, subset=[cst.TITLE]).index]
    nb_diff = len(df_diff)

    # Upload the diff
    if nb_diff == 0:
        logger.warning("No new entry to upload from senscritique.")
    else:
        logger.warning(f"Uploading {nb_diff} new entries to notion...")
        upload(df=df_diff, notion_url=notion_database_url, title=title_page)
        logger.warning("Upload completed.")
