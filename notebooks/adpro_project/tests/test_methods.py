import pytest
from src.movie_analyzer import MovieAnalyzer

def test_movie_type_invalid_argument():
    analyzer = MovieAnalyzer()
    with pytest.raises(Exception):
        analyzer.movie_type(N="not an integer")  # pydantic will raise an error

def test_actor_distributions_invalid_args():
    analyzer = MovieAnalyzer()

    # Check invalid gender (non-string)
    with pytest.raises(Exception):
        analyzer.actor_distributions(gender=123, max_height=200.0, min_height=150.0)

    # Check invalid height (non-numeric max_height)
    with pytest.raises(Exception):
        analyzer.actor_distributions(gender="All", max_height="big", min_height=150.0)

    # Check unrealistic height values (min_height >= max_height)
    with pytest.raises(Exception):
        analyzer.actor_distributions(gender="All", max_height=150.0, min_height=200.0)
