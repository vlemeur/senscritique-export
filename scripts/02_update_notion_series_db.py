"""Script used to update a notion series database from senscritique"""
from pathlib import Path
from senscritique_export.utils import get_token, get_db_series_url
from senscritique_export.notion_export import update_notion_db_series

# Fill credentials file before running this script

if __name__ == "__main__":

    PATH_CREDENTIALS = Path(__file__).parent / "credentials.txt"
    USER_NAME = "Jigot"

    api_key = get_token(path_credentials=PATH_CREDENTIALS)
    db_url = get_db_series_url(path_credentials=PATH_CREDENTIALS)

    update_notion_db_series(notion_database_url=db_url, api_key=api_key, user="Jigot", title_page="Series")
