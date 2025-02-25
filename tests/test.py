import pytest
from unittest.mock import patch
import pandas as pd

# Import your MovieAnalysis class
from movie_analysis import MovieAnalysis  # replace with actual import

@patch.object(MovieAnalysis, '_download_data', return_value=None)
@patch.object(MovieAnalysis, '_extract_data', return_value=None)
@patch.object(MovieAnalysis, '_load_data', return_value=None)
def test_movie_type_raises_valueerror_with_non_int_N(mock_download, mock_extract, mock_load):
    """
    Checks that movie_type() raises ValueError when N is not an integer.
    """
    ma = MovieAnalysis(data_url="fake_url")
    ma.data = pd.DataFrame({"Movie_Type": ["Action", "Comedy", "Drama"]})

    with pytest.raises(ValueError):
        ma.movie_type(N="NotAnInteger")


@patch.object(MovieAnalysis, '_download_data', return_value=None)
@patch.object(MovieAnalysis, '_extract_data', return_value=None)
@patch.object(MovieAnalysis, '_load_data', return_value=None)
def test_movie_type_raises_keyerror_if_missing_column(mock_download, mock_extract, mock_load):
    """
    Checks that movie_type() raises KeyError when 'Movie_Type' column is missing.
    """
    ma = MovieAnalysis(data_url="fake_url")
    ma.data = pd.DataFrame({"SomeOtherColumn": [1, 2, 3]})

    with pytest.raises(KeyError):
        ma.movie_type(N=5)


@patch.object(MovieAnalysis, '_download_data', return_value=None)
@patch.object(MovieAnalysis, '_extract_data', return_value=None)
@patch.object(MovieAnalysis, '_load_data', return_value=None)
def test_actor_count_raises_keyerror_if_missing_actors(mock_download, mock_extract, mock_load):
    """
    Checks that actor_count() raises KeyError when 'Actors' column is missing.
    """
    ma = MovieAnalysis(data_url="fake_url")
    ma.data = pd.DataFrame({"SomeOtherColumn": [1, 2, 3]})

    with pytest.raises(KeyError):
        ma.actor_count()


@patch.object(MovieAnalysis, '_download_data', return_value=None)
@patch.object(MovieAnalysis, '_extract_data', return_value=None)
@patch.object(MovieAnalysis, '_load_data', return_value=None)
def test_movie_type_handles_empty_dataframe(mock_download, mock_extract, mock_load):
    """
    Checks that movie_type() raises an appropriate error when the DataFrame is empty.
    """
    ma = MovieAnalysis(data_url="fake_url")
    ma.data = pd.DataFrame()

    with pytest.raises(KeyError):  # Or ValueError, depending on implementation
        ma.movie_type(N=5)
