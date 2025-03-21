"""
movie_analyzer.py
"""

import os
import tarfile
import json
import requests
import pandas as pd
import matplotlib.pyplot as plt
from pydantic import validate_call
from typing import Optional

# ADDED: Additional imports for random sampling
import random

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

        # Load Movies
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

        # Load Actors
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

        # ADDED: Load Plot Summaries if present (plot_summaries.txt)
        plot_summaries_path = os.path.join(self.extracted_folder, "plot_summaries.txt")
        if os.path.exists(plot_summaries_path):
            # This file has format: movie_id \t summary
            self.summaries_df = pd.read_csv(
                plot_summaries_path,
                sep="\t",
                header=None,
                names=["movie_id", "summary"],
                encoding="utf-8",
                quoting=3,  # to handle any quotation issues
                on_bad_lines="skip"
            )
        else:
            self.summaries_df = pd.DataFrame(columns=["movie_id", "summary"])

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

    @validate_call
    def releases(self, genre: Optional[str] = None) -> pd.DataFrame:
        """
        Returns a DataFrame with columns ["Year", "Count"] representing
        how many movies were released per year.
        If 'genre' is None or the string "None", it does not filter.
        Otherwise, it filters for movies containing that genre.
        """
        if self.movies_df.empty:
            raise Exception("Movie data not loaded.")

        df = self.movies_df.copy()
        # Convert 'release_date' to datetime; drop invalid or missing
        df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
        df.dropna(subset=["release_date"], inplace=True)

        # Extract year
        df["Year"] = df["release_date"].dt.year

        # Handle the case where genre is None or the literal string "None"
        if genre is None or genre == "None":
            # No filtering: group *all* movies by year
            result = df.groupby("Year").size().reset_index(name="Count")
            return result.sort_values("Year")
        else:
            # Filter by the given genre
            def extract_genres(genre_str: str) -> list:
                if not genre_str or genre_str.strip() in ("", "{}"):
                    return []
                try:
                    d = json.loads(genre_str)
                    return list(d.values())
                except:
                    return []

            df["parsed_genres"] = df["genres"].fillna("").apply(extract_genres)
            df = df[df["parsed_genres"].apply(lambda g_list: genre in g_list)]
            result = df.groupby("Year").size().reset_index(name="Count")
            return result.sort_values("Year")

    @validate_call
    def ages(self, mode: str = "Y") -> pd.DataFrame:
        """
        Counts how many births happened per chosen interval: 'Y' for Year or 'M' for Month.
        Default is 'Y'. If the user selects something else, we default to 'Y'.
        """
        if self.actors_df.empty:
            raise Exception("Actor data not loaded.")

        df = self.actors_df.copy()
        df["birthdate"] = pd.to_datetime(df["actor_birthdate"], errors="coerce")
        df.dropna(subset=["birthdate"], inplace=True)

        if mode == "M":
            df["Birth_Month"] = df["birthdate"].dt.month
            result = df.groupby("Birth_Month").size().reset_index(name="Count")
            return result
        else:
            # Default to Year if "M" is not selected
            df["Birth_Year"] = df["birthdate"].dt.year
            result = df.groupby("Birth_Year").size().reset_index(name="Count")
            return result

    # --------------------------------------------------------------------
    # ADDED: Helper to get a random movie, its summary, and its genres
    # --------------------------------------------------------------------
    @validate_call
    def get_random_movie_info(self) -> dict:
        """
        Returns a dictionary containing:
            {
              'title': ...,
              'summary': ...,
              'genres_list': [list of genres as strings],
              'movie_id': ...
            }
        If no summary is found for a chosen movie, returns an empty summary.
        """
        if self.movies_df.empty:
            raise Exception("No movies data available.")

        # Merge with summaries to ensure we can get the summary
        merged_df = pd.merge(self.movies_df, self.summaries_df, on="movie_id", how="left")

        # Convert genres from JSON to list
        def parse_genres(genre_str):
            if pd.isna(genre_str) or genre_str.strip() in ("", "{}"):
                return []
            try:
                d = json.loads(genre_str)
                return list(d.values())
            except:
                return []

        merged_df["genres_list"] = merged_df["genres"].apply(parse_genres)
        if merged_df.empty:
            raise Exception("Merged movies & summaries is empty or invalid.")

        random_row = merged_df.sample(n=1).iloc[0]

        return {
            "movie_id": random_row["movie_id"],
            "title": str(random_row["title"]),
            "summary": str(random_row["summary"]) if not pd.isna(random_row["summary"]) else "",
            "genres_list": random_row["genres_list"]
        }
