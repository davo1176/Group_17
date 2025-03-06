import os
import requests
import pandas as pd
import zipfile
import tarfile
from typing import Optional


class InitializeMovieData:
    """
    A class to download, extract, and load movie dataset from CMU Movie Corpus.

    Attributes:
        data_url (str): URL of the dataset.
        download_dir (str): Directory where dataset is downloaded and extracted.
        data_file (str): Full path to the downloaded dataset file (zip or tar.gz).
        extracted_dir (str): Path to the extracted dataset directory.
        movies_df (Optional[pd.DataFrame]): DataFrame containing the movie dataset.
        actors_df (Optional[pd.DataFrame]): DataFrame containing the actors dataset.
    """

    def __init__(
        self,
        data_url: str = "http://www.cs.cmu.edu/~ark/personas/data/MovieSummaries.tar.gz",
        download_dir: str = None
    ):
        """
        Initializes the MovieData class:
        - Creates necessary directories.
        - Downloads the dataset if not already present.
        - Extracts the dataset.
        - Loads datasets into Pandas DataFrames.

        Args:
            data_url (str): URL to download the dataset (zip or tar.gz).
            download_dir (str): Absolute or relative path to where data should be stored.
                                Defaults to a 'downloads' folder in the current directory.
        """
        self.data_url = data_url

        # 1. Set up the download_dir
        if download_dir is None:
            # Default: put it in a local 'downloads' folder
            download_dir = os.path.join(os.getcwd(), "downloads")
        else:
            # If user provided a path, make sure it's absolute
            download_dir = os.path.abspath(download_dir)
        self.download_dir = download_dir

        # 2. Determine data_file name based on URL file extension
        if data_url.endswith(".zip"):
            data_filename = "dataset.zip"
        elif data_url.endswith(".tar.gz") or data_url.endswith(".tgz"):
            data_filename = "dataset.tar.gz"
        else:
            raise ValueError("Unsupported file format. URL must end in .zip or .tar.gz")

        self.data_file = os.path.join(self.download_dir, data_filename)
        self.extracted_dir = os.path.join(self.download_dir, "extracted")

        # DataFrames to be loaded
        self.movies_df: Optional[pd.DataFrame] = None
        self.actors_df: Optional[pd.DataFrame] = None

        # Ensure directories exist
        os.makedirs(self.download_dir, exist_ok=True)
        os.makedirs(self.extracted_dir, exist_ok=True)

        # Download if not present
        if not os.path.exists(self.data_file):
            self._download_data()

        # Extract and load
        self._extract_data()
        self._load_data()

    def _download_data(self):
        """Download the dataset from the provided URL."""
        print(f"Downloading dataset from {self.data_url} ...")
        with requests.get(self.data_url, stream=True) as r:
            r.raise_for_status()
            with open(self.data_file, "wb") as file:
                for chunk in r.iter_content(chunk_size=8192):
                    file.write(chunk)
        print(f"Download complete. File saved to: {self.data_file}")

    def _extract_data(self):
        """Extract the dataset (zip or tar.gz)."""
        print(f"Extracting dataset into {self.extracted_dir} ...")

        if self.data_file.endswith(".zip"):
            try:
                with zipfile.ZipFile(self.data_file, "r") as zip_ref:
                    zip_ref.extractall(self.extracted_dir)
                print("ZIP extraction complete.")
            except zipfile.BadZipFile:
                print("Error: The file is not a valid ZIP archive.")

        elif self.data_file.endswith(".tar.gz") or self.data_file.endswith(".tgz"):
            try:
                with tarfile.open(self.data_file, "r:gz") as tar:
                    tar.extractall(self.extracted_dir)
                print("TAR.GZ extraction complete.")
            except tarfile.TarError:
                print("Error: The file is not a valid TAR.GZ archive.")

        else:
            print("Error: Unsupported file format for extraction.")

    def _load_data(self):
        """Walk through `extracted_dir` to find and load TSV files."""
        print("🔍 Searching for movie.metadata.tsv and character.metadata.tsv ...")

        movie_file_path = None
        character_file_path = None  # Renamed to match actual filename

        # Search all subdirectories
        for root, _, files in os.walk(self.extracted_dir):
            if "movie.metadata.tsv" in files:
                movie_file_path = os.path.join(root, "movie.metadata.tsv")
            if "character.metadata.tsv" in files:  # Updated to match correct file
                character_file_path = os.path.join(root, "character.metadata.tsv")

        try:
            # Load movie data
            if movie_file_path and os.path.exists(movie_file_path):
                self.movies_df = pd.read_csv(movie_file_path, sep='\t', encoding="utf-8")
                print(f"✅ Movie dataset loaded from: {movie_file_path}")
            else:
                raise FileNotFoundError("⚠️ Could not find 'movie.metadata.tsv'.")

            # Load character (actors) data
            if character_file_path and os.path.exists(character_file_path):
                self.actors_df = pd.read_csv(character_file_path, sep='\t', encoding="utf-8")
                print(f"✅ Character dataset loaded from: {character_file_path}")
            else:
                raise FileNotFoundError("⚠️ Could not find 'character.metadata.tsv'.")

            print("🎉 Datasets loaded successfully!")

        except Exception as e:
            print(f"❌ Error loading datasets: {e}")
