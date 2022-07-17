"""This module aims to fill a Notion Database"""

from notion_df import config, download

from senscritique_export.scrapper import get_user_collection

def get_df_from_notion(notion_database_url: str, api_key:str):
    config(api_key=api_key)
    df = download(notion_database_url)