import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import requests
import zipfile

class MovieAnalysis:
    def __init__(self, data_url, download_dir="downloads/MovieSummaries"):
        self.download_dir = download_dir
        self.data_url = data_url
        self.data_file = os.path.join(download_dir, "data.zip")
        self.extracted_dir = os.path.join(download_dir, "extracted")
        self.data = None  # Initialize data attribute

        os.makedirs(self.download_dir, exist_ok=True)

        if not os.path.exists(self.data_file):
            self._download_data()
        
        self._extract_data()
        self._load_data()

    def _download_data(self):
        """Downloads the dataset from the provided URL."""
        response = requests.get(self.data_url, stream=True)
        with open(self.data_file, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)

    def _extract_data(self):
        """Extracts the downloaded ZIP file if not already extracted."""
        if not os.path.exists(self.extracted_dir):
            os.makedirs(self.extracted_dir)
            with zipfile.ZipFile(self.data_file, "r") as zip_ref:
                zip_ref.extractall(self.extracted_dir)

    def _load_data(self):
        """Loads the extracted CSV file into a Pandas DataFrame."""
        csv_file = os.path.join(self.extracted_dir, "movies.csv")
        if os.path.exists(csv_file):
            self.data = pd.read_csv(csv_file)
        else:
            raise FileNotFoundError(f"CSV file not found in extracted directory: {csv_file}")

    def get_data(self):
        """Returns the loaded movie dataset as a Pandas DataFrame."""
        return self.data
    
    def movie_type(self, N = 10):
        """Returns a datafram with the N most common movie types and their count. """
        if not isinstance(N, int):
            raise ValueError("N must be an integer.")

        if 'Movie_Type' not in self.data.columns:
            raise KeyError("Column 'Movie_Type' not found in dataset.")
        
        movie_counts = self.data['Movie_Type'].value_counts().nlargest(N).reset_index()
        movie_counts.columns = ["Movie_Type", "Count"]
        
        return movie_counts
    
    def actor_count(self):
        """Returns a DataFrame with a histogram of 'number of actors' vs 'movie counts'."""
        if 'Actors' not in self.data.columns:
            raise KeyError("Column 'Actors' not found in dataset.")
        
        # Assume actors are stored as a comma-separated string
        self.data['Actor_Count'] = self.data['Actors'].apply(lambda x: len(str(x).split(',')) if pd.notna(x) else 0)
        actor_hist = self.data['Actor_Count'].value_counts().reset_index()
        actor_hist.columns = ["Number of Actors", "Movie Count"]

        return actor_hist

    def actor_distributions(self, gender="All", max_height=2.0, min_height=1.5, plot=False):
        """Returns a filtered DataFrame based on gender and height range. Optionally plots height distribution."""
        if not isinstance(gender, str):
            raise ValueError("Gender must be a string.")

        if not isinstance(max_height, (int, float)) or not isinstance(min_height, (int, float)):
            raise ValueError("Height values must be numerical.")

        if 'Gender' not in self.data.columns or 'Height' not in self.data.columns:
            raise KeyError("Columns 'Gender' or 'Height' not found in dataset.")

        # Filtering data
        df_filtered = self.data.copy()
        df_filtered = df_filtered[(df_filtered['Height'] >= min_height) & (df_filtered['Height'] <= max_height)]

        if gender != "All":
            df_filtered = df_filtered[df_filtered['Gender'] == gender]

        if plot:
            plt.figure(figsize=(8, 5))
            sns.histplot(df_filtered['Height'], bins=20, kde=True)
            plt.xlabel("Height (m)")
            plt.ylabel("Count")
            plt.title(f"Height Distribution for {gender}")
            plt.show()

        return df_filtered