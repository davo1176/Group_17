from typing import Optional
import pandas as pd
import matplotlib.pyplot as plt

class MovieAnalyzer:
    """
    A class to perform various analyses on movie and actor data.
    """

    def __init__(
        self,
        movies_df: pd.DataFrame,
        actors_df: pd.DataFrame
    ):
        self.movies_df = movies_df
        self.actors_df = actors_df

    def movie_type(self, N: int = 10) -> pd.DataFrame:
        """
        Returns a dataframe with columns ["Movie_Type", "Count"] showing the top N movie types.
        Raises ValueError if N is not an integer.
        """
        if not isinstance(N, int):
            raise ValueError("Parameter 'N' must be an integer.")

        # Pseudocode, depends on how "genres" are stored:
        # 1) Identify the column that holds the genres
        # 2) Count frequency of each genre
        # 3) Sort and select top N
        # 4) Return DataFrame with "Movie_Type", "Count"
        
        # Example (adjust column indexing/naming as needed):
        if 'movie_genres' not in self.movies_df.columns:
            # or the correct column name if different
            raise ValueError("No column named 'movie_genres' found in movies_df.")
        
        # Suppose each row's 'movie_genres' has a pipe-separated list of genres
        # (You will need to confirm the real structure in your dataset)
        # Flatten them:
        all_genres = []
        for genres_str in self.movies_df['movie_genres'].dropna():
            # e.g. "['Action','Comedy']" or something similar
            # Parse properly (e.g., literal_eval if needed)
            # For demonstration, let's assume we do a naive split:
            # all_genres.extend(genres_str.split('|'))
            pass  # <--- parse logic here

        # Then do a frequency count
        # freq = pd.Series(all_genres).value_counts()
        # topN = freq.head(N).reset_index()
        # topN.columns = ["Movie_Type", "Count"]
        # return topN

        return pd.DataFrame()  # replace with your real logic

    def actor_count(self) -> pd.DataFrame:
        """
        Calculates a histogram of "number of actors per movie" vs "movie counts".
        i.e., how many movies have 1 actor, how many have 2, etc.
        """
        # 1) group by movie_id in self.actors_df
        # 2) count how many actors each movie_id has
        # 3) create a distribution / frequency table of that count
        # 4) return that frequency distribution as a DataFrame

        # Example logic:
        actor_count_series = self.actors_df.groupby('movie_id').size()  # counts
        histogram = actor_count_series.value_counts().reset_index()
        histogram.columns = ['number_of_actors', 'movie_counts']
        return histogram

    def actor_distributions(
        self, 
        gender: str, 
        max_height: float, 
        min_height: float, 
        plot: bool = False
    ) -> pd.DataFrame:
        """
        Returns a subset of the actor data (or some aggregated distribution)
        where 'gender' matches and 'height' is between [min_height, max_height].
        If plot=True, display a matplotlib histogram of that subset's heights.
        
        Raises ValueError if inputs are of incorrect type or if min_height, max_height are invalid.
        """
        # Validate inputs
        if not isinstance(gender, str):
            raise ValueError("Parameter 'gender' must be a string.")
        if not (isinstance(max_height, (float, int)) and isinstance(min_height, (float, int))):
            raise ValueError("max_height and min_height must be numeric.")
        if min_height > max_height:
            raise ValueError("min_height cannot exceed max_height.")

        df = self.actors_df.copy()

        # Filter by gender if not "All"
        if gender != "All":
            df = df[df['gender'] == gender]

        # Filter by height
        # (Replace 'height' with your real column name in the dataset)
        df = df[(df['height'] >= min_height) & (df['height'] <= max_height)]

        if plot:
            # For a simple distribution plot:
            plt.hist(df['height'].dropna(), bins=20, edgecolor='black')
            plt.title(f"Height Distribution ({gender}, {min_height}-{max_height})")
            plt.xlabel("Height")
            plt.ylabel("Frequency")
            plt.show()

        return df  # or you may return an aggregated result
