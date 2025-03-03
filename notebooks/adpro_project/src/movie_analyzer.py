import os
import tarfile
import json
import requests
import pandas as pd
import matplotlib.pyplot as plt

from pydantic import validate_call


class MovieAnalyzer:
    """
    A class to handle movie data analysis. Downloads the data into a
    "downloads" folder at the project root.
    """

    @validate_call
    def __init__(self) -> None:
        # Determine the project root (assumes this file is in <project_root>/src/)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.download_dir = os.path.join(base_dir, "downloads")
        self.data_filename = "MovieSummaries.tar.gz"
        self.data_url = "https://www.cs.cmu.edu/~ark/personas/data/MovieSummaries.tar.gz"
        self.data_filepath = os.path.join(self.download_dir, self.data_filename)

        # Ensure the downloads folder exists.
        os.makedirs(self.download_dir, exist_ok=True)

        # Download the file if it doesn't exist.
        if not os.path.exists(self.data_filepath):
            self._download_data()

        # Extract the file if not already extracted.
        self.extracted_folder = os.path.join(self.download_dir, "MovieSummaries")
        if not os.path.exists(self.extracted_folder):
            if self.data_filepath.endswith(".tar.gz"):
                with tarfile.open(self.data_filepath, "r:gz") as tar:
                    tar.extractall(path=self.download_dir)
            else:
                raise Exception("Unsupported archive format.")

        # Load the datasets.
        self._load_data()

    def _download_data(self) -> None:
        print("Downloading data...")
        response = requests.get(self.data_url, stream=True)
        response.raise_for_status()
        with open(self.data_filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Download complete.")

    def _load_data(self) -> None:
        # For movies, we use column names based on your sample:
        # movie_id, freebase_id, title, release_date, imdb_id, runtime, languages, countries, genres
        movie_metadata_path = os.path.join(self.extracted_folder, "movie.metadata.tsv")
        # For actors, the sample data has 13 columns.
        character_metadata_path = os.path.join(self.extracted_folder, "character.metadata.tsv")

        if os.path.exists(movie_metadata_path):
            self.movies_df = pd.read_csv(
                movie_metadata_path,
                sep="\t",
                header=None,
                names=["movie_id", "freebase_id", "title", "release_date",
                       "imdb_id", "runtime", "languages", "countries", "genres"],
                encoding="utf-8",
                na_values=["\\N"]
            )
        else:
            self.movies_df = pd.DataFrame()

        if os.path.exists(character_metadata_path):
            self.actors_df = pd.read_csv(
                character_metadata_path,
                sep="\t",
                header=None,
                names=[
                    "movie_id",
                    "persona_id",
                    "movie_date",
                    "character_name",
                    "actor_birthdate",
                    "gender",
                    "height",
                    "col8",
                    "actor_name",
                    "age",
                    "col10",
                    "col11",
                    "col12"
                ],
                encoding="utf-8",
                na_values=["\\N"]
            )
            # Convert height to numeric (in meters)
            self.actors_df["height"] = pd.to_numeric(self.actors_df["height"], errors="coerce")
        else:
            self.actors_df = pd.DataFrame()

    @validate_call
    def movie_type(self, N: int = 10) -> pd.DataFrame:
        """
        Returns a DataFrame listing the top-N most common movie genres.
        The method processes the 'genres' field (a JSON-like dictionary string)
        by:
          - Parsing the string as JSON.
          - Extracting the genre names (dictionary values).
          - Returning ["Unknown"] if the field is empty.
        """
        if self.movies_df.empty or "genres" not in self.movies_df.columns:
            raise Exception("Movie data not loaded or 'genres' column missing.")

        def extract_genres(genre_str: str) -> list:
            if not genre_str or genre_str.strip() in ("", "{}"):
                return ["Unknown"]
            try:
                d = json.loads(genre_str)
                if not d:
                    return ["Unknown"]
                return list(d.values())
            except Exception:
                return ["Unknown"]

        df = self.movies_df.copy()
        df["genres"] = df["genres"].fillna("").apply(extract_genres)
        df = df.explode("genres")
        counts = df["genres"].value_counts().reset_index()
        counts.columns = ["Movie_Type", "Count"]
        return counts.head(N)

    def actor_count(self) -> pd.DataFrame:
        """
        Returns a DataFrame histogram of unique actor counts per movie.
        Uses the actor's name for uniqueness.
        """
        if self.actors_df.empty:
            raise Exception("Actor data not loaded.")
        actor_counts = self.actors_df.groupby("movie_id")["actor_name"].nunique()
        hist = actor_counts.value_counts().reset_index()
        hist.columns = ["Number_of_Actors", "Movie_Count"]
        return hist.sort_values("Number_of_Actors")

    @validate_call
    def actor_distributions(
        self,
        gender: str,
        max_height: float,
        min_height: float,
        plot: bool = False,
    ):
        """
        Filters actor data by gender and height range.
        Since height is now in meters, plausible values are assumed between 1.0 and 2.5.
        If plot is True, returns a tuple (filtered DataFrame, matplotlib figure)
        showing the height distribution.
        Otherwise, returns just the filtered DataFrame.
        """
        if self.actors_df.empty:
            raise Exception("Actor data not loaded.")

        # Check height range (in meters)
        if not (1.0 <= min_height < max_height <= 2.5):
            raise Exception("Height values are unrealistic. Please check (expected in meters).")

        df = self.actors_df.copy()
        # Fill missing gender values.
        df["gender"] = df["gender"].fillna("Unknown")
        if gender != "All":
            df = df[df["gender"] == gender]
        df = df.dropna(subset=["height"])
        df = df[(df["height"] >= min_height) & (df["height"] <= max_height)]

        if plot:
            if df.empty:
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.text(0.5, 0.5, "No Data", horizontalalignment="center",
                        verticalalignment="center", transform=ax.transAxes)
                ax.set_title("Actor Height Distribution")
                ax.set_xlabel("Height (m)")
                ax.set_ylabel("Frequency")
                return df, fig
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.hist(df["height"], bins=20, edgecolor="black")
            ax.set_title("Actor Height Distribution")
            ax.set_xlabel("Height (m)")
            ax.set_ylabel("Frequency")
            return df, fig

        return df
