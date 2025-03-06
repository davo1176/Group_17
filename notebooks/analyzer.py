#analyzer.py

import os
import urllib.request
import tarfile
import pandas as pd
from pathlib import Path

class MovieAnalyzer:
    def __init__(self, download_url: str, download_path: str = "downloads"):
        self.download_url = download_url
        self.download_path = Path(download_path)
        self.download_file_name = "MovieSummaries.tar.gz"
        
        self._download_data_if_needed()
        self._extract_data()
        self._load_dataframes()

    def _download_data_if_needed(self):
        """Download if not already present."""
        file_path = self.download_path / self.download_file_name
        if not file_path.is_file():
            urllib.request.urlretrieve(self.download_url, file_path)
            print("Download complete.")
        else:
            print("Data file already exists. No download needed.")

    def _extract_data(self):
        """Extract if not already extracted."""
        file_path = self.download_path / self.download_file_name
        extract_folder = self.download_path / "MovieSummaries"
        if not extract_folder.exists():
            with tarfile.open(file_path, "r:gz") as tar:
                tar.extractall(path=self.download_path)
            print("Extraction complete.")
        else:
            print("Data already extracted.")

    def _load_dataframes(self):
        """Load the relevant CSV files into pandas DataFrames."""
        # Here is where you can safely reference `self`:
        movies_file = self.download_path / "MovieSummaries" / "movie.metadata.tsv"
        actors_file = self.download_path / "MovieSummaries" / "character.metadata.tsv"

        self.movies_df = pd.read_csv(movies_file, sep="\t", header=None)
        # Assign column names so we can rename one to "movie_type" if needed
        self.movies_df.columns = [
            "wiki_id",
            "freebase_id",
            "movie_name",
            "release_date",
            "box_office",
            "runtime",
            "languages",
            "countries",
            "genres",
        ]

        # Rename genres to movie_type if your methods expect that column name:
        self.movies_df.rename(columns={"genres": "movie_type"}, inplace=True)

        

        print("DataFrames loaded successfully.")


    
    def movie_type(self, N: int = 10) -> pd.DataFrame:
        """
        Returns a DataFrame with the N most common movie types and their frequencies.

        Args:
            N (int): Number of most common movie types to return. Default is 10.

        Raises:
            TypeError: If N is not an integer.

        Returns:
            pd.DataFrame: With columns ["Movie_Type", "Count"].
        """

        if not isinstance(N, int):
            raise TypeError("N must be an integer.")

        if "movie_type" not in self.movies_df.columns:
            raise ValueError("The dataset does not contain a 'movie_type' column.")

        # Suppose self.movies_df has a column named 'movie_type'
        movie_type_counts = (
            self.movies_df["movie_type"]
            .value_counts()
            .nlargest(N)
            .reset_index()
        )
        movie_type_counts.columns = ["Movie_Type", "Count"]
        return movie_type_counts

    def actor_count(self) -> pd.DataFrame:
        """
        Returns a histogram of 'number of actors' vs 'movie counts'.
        In other words, how many movies have exactly 1 actor, 2 actors, etc.

        Returns:
            pd.DataFrame: With columns ["NumberOfActors", "MovieCount"].
        """

        # Let's assume `self.actors_df` (or `self.people_df`) has columns:
        #   - "movie_id"
        #   - "actor_id"
        #
        # The logic here is:
        #   1. Group by movie_id.
        #   2. Count how many unique actor_ids each movie has.
        #   3. Get the frequency of each possible actor-count.

        # Count number of actors per movie
        counts_per_movie = (
            self.actors_df
            .groupby("movie_id")["actor_id"]
            .nunique()  # Or .count() if actor_id is guaranteed unique anyway
        )

        # Now get the histogram: how many movies have 1 actor, 2 actors, 3 actors, etc.
        hist = (
            counts_per_movie
            .value_counts()
            .reset_index()
            .sort_values("index")  # to get ascending order of #actors
        )
        hist.columns = ["NumberOfActors", "MovieCount"]

        return hist

    def actor_distributions(self, 
                            gender: str, 
                            min_height: float, 
                            max_height: float, 
                            plot: bool = False) -> pd.DataFrame:
        """
        Filters the actor dataset based on gender and height range, and optionally plots
        the height distribution.

        Args:
            gender (str): "All" or one of the distinct gender values in the data.
            min_height (float): Minimum height boundary.
            max_height (float): Maximum height boundary.
            plot (bool): If True, display a matplotlib histogram of the height distribution.

        Raises:
            TypeError: If gender is not a string or if min_height/max_height are not numeric.

        Returns:
            pd.DataFrame: Filtered DataFrame of actors, typically with columns like
                        ["actor_id", "gender", "height"].
        """
        # --- Validate Inputs ---
        if not isinstance(gender, str):
            raise TypeError("gender must be a string.")

        # min_height and max_height must be numeric
        if not isinstance(min_height, (int, float)) or not isinstance(max_height, (int, float)):
            raise TypeError("min_height and max_height must be numeric values (int or float).")

        # Optional: check that min_height <= max_height
        if min_height > max_height:
            raise ValueError("min_height cannot be greater than max_height.")

        # --- Filter Data ---
        # Assume `self.actors_df` (or `self.people_df`) has columns "actor_id", "gender", "height", etc.
        df = self.actors_df[["actor_id", "gender", "height"]].copy()

        # Remove rows with missing gender or height
        df.dropna(subset=["gender", "height"], inplace=True)

        # Filter by gender if not "All"
        if gender != "All":
            df = df[df["gender"] == gender]

        # Filter by height range
        df = df[(df["height"] >= min_height) & (df["height"] <= max_height)]

        # --- Optional Plotting ---
        if plot:
            import matplotlib.pyplot as plt
            plt.hist(df["height"], bins=20, edgecolor="black")
            plt.title(f"Height Distribution for Gender={gender}")
            plt.xlabel("Height")
            plt.ylabel("Count")
            plt.show()

        return df

