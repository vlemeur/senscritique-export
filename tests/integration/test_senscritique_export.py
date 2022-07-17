import pandas as pd
import pytest

from senscritique_export.scrapper import get_user_collection


@pytest.mark.parametrize("user_name", ["Jigot", "SubwaySam", "FS-10"])
def test_get_user_colection(user_name):

    user_collection = get_user_collection(user=user_name)
    df_user_collection = pd.DataFrame(user_collection)
    assert len(df_user_collection) > 1
