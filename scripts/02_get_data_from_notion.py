from pathlib import Path
from senscritique_export.utils import get_token

if __name__ == "__main__":
    PATH_TOKEN = Path(__file__).parent / "token.txt"
    tss = get_token(path_token_file=PATH_TOKEN)