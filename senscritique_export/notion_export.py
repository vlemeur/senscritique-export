"""This module aims to fill and get data from a Notion Database"""
from typing import Optional
import pandas as pd
from notion_df import config, download, upload

import senscritique_export.constants as cst
from senscritique_export.scrapper import get_user_collection
from senscritique_export.utils import get_token


def remove_accent_from_df(df: pd.DataFrame) -> pd.DataFrame:
    return df.apply(lambda x: x.str.normalize("NFKD").str.encode("ascii", errors="ignore").str.decode("utf-8"))


def get_df_from_notion(notion_database_url: str, api_key: Optional[str] = None) -> pd.DataFrame:
    if api_key is not None:
        config(api_key=api_key)
    return download(notion_database_url).dropna()


def update_notion_db_series(notion_database_url: str, api_key: str, user: str, title_page: str):
    config(api_key=api_key)
    df_notion = remove_accent_from_df(df=get_df_from_notion(notion_database_url=notion_database_url))

    df_sens_critique = pd.DataFrame(get_user_collection(user=user))
    df_series = remove_accent_from_df(
        df=df_sens_critique[df_sens_critique[cst.CATEGORY] == "Series"].loc[:, df_notion.columns]
    )

    df_diff = pd.concat(objs=[df_notion, df_series])
    # Necessary to convert list to string
    df_diff = df_diff.loc[df_diff.astype(str).drop_duplicates(keep=False).index]

    # Upload the diff
    upload(df=df_diff, notion_url=notion_database_url, title=title_page)
    stop = "here"


if __name__ == "__main__":
    from pathlib import Path

    path_token = Path(__file__).parent.parent / "scripts" / "credentials.txt"
    db_url = "https://www.notion.so/b4602cea33fe403a9e1a92e9ebcad263?v=2339e7890a5d43689d1ffd73e2282029"

    api_key = get_token(path_credentials=path_token)

    update_notion_db_series(notion_database_url=db_url, api_key=api_key, user="Jigot", title_page="Series")
#  tss = get_df_from_notion(notion_database_url=db_url, api_key=api_key)
#    topop = get_user_collection(user="Jigot")
