"""Script used to get a collection from senscritique from a user name"""
import pandas as pd

from senscritique_export.scrapper import get_user_collection

if __name__ == "__main__":
    # Name of the user
    user_name = "Jigot"

    user_collection = get_user_collection(user=user_name)
    df_user_collection = pd.DataFrame(user_collection)
