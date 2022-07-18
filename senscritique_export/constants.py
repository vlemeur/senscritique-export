"""Provide constants used in other modules"""

# Sens critique related
RANK = "Rank"
USER_RATING = "User Rating"
TITLE = "Title"
DEVELOPER = "Developer"
PLATEFORMS = "Platforms"
AVERAGE_RATING = "Average Rating"
NB_RATINGS = "Number of Ratings"
URL = "URL"
ORIGINAL_TITLE = "Original Title"
YEAR = "Year"
RELEASE_DATE = "Release Date"
PICTURE_URL = "Picture URL"
GENRE = "Genre"
DESCRIPTION = "Description"
AUTHOR = "Author"
NB_SONGS = "Number of Songs"
ARTIST = "Artist"
LENGTH = "Length"
PRODUCER = "Producer"
NB_SEASONS = "Number of Seasons"
CATEGORY = "Category"

SERIES_TYPES = {
    USER_RATING: int,
    NB_SEASONS: int,
    RELEASE_DATE: str,
    GENRE: str,
    URL: str,
    AVERAGE_RATING: int,
    PRODUCER: int,
    NB_RATINGS: int,
    YEAR: str,
    TITLE: str,
}


# Notion related
NOTION_TOKEN = "NOTION_TOKEN"
SERIES_DB_URL = "SERIES_DB_URL"
JANVIER = "janvier"
FEVRIER = "fevrier"
MARS = "mars"
AVRIL = "avril"
MAI = "mai"
JUIN = "juin"
JUILLET = "juillet"
AOUT = "aout"
SEPTEMBRE = "septembre"
OCTOBRE = "octobre"
NOVEMBRE = "novembre"
DECEMBRE = "decembre"

FRENCH_MONTHS = {
    JANVIER: 1,
    FEVRIER: 2,
    MARS: 3,
    AVRIL: 4,
    MAI: 5,
    JUIN: 6,
    JUILLET: 7,
    AOUT: 8,
    SEPTEMBRE: 9,
    OCTOBRE: 10,
    NOVEMBRE: 11,
    DECEMBRE: 12,
}
