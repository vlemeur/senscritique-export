from pathlib import Path
from senscritique_export.utils import get_token

if __name__ == "__main__":
    PATH_TOKEN = Path(__file__).parent / "credentials.txt"

    api_token = get_token(path_credentials=PATH_TOKEN)
