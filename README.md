# Project Title
# Welcome to project RAG-TAG
---
# Movie Analysis App (Group 17)

Welcome to the **Movie Analysis App**, a Streamlit-based application that explores movie data (titles, genres, actor information, etc.) from the [CMU Movie Summary](https://www.cs.cmu.edu/~ark/personas/) corpus. This repository also includes a **third page** that demonstrates using a local Large Language Model (LLM), via [Ollama](https://github.com/jmorganca/ollama), to classify a movie’s genre by its plot summary.

---

## Repository Structure

GROUP_17/ ├── Movie_Analyzer.py ├── pages/ │ ├── 2_Movie_Releases_Over_Time.py │ └── 3_Genre_Classifier.py ├── src/ │ ├── init.py │ └── movie_analyzer.py ├── tests/ │ ├── init.py │ └── test_methods.py └── README.md <-- (You are here)


- **Movie_Analyzer.py**: The main Streamlit entry point with core functionalities (common movie types, actor count, actor distributions).
- **pages/2_Movie_Releases_Over_Time.py**: A second Streamlit page displaying chronological movie releases and actor birth data.
- **pages/3_Genre_Classifier.py**: **New** page that uses a local LLM for genre classification based on the movie’s plot summary.
- **src/movie_analyzer.py**: Main Python class `MovieAnalyzer` that loads and analyzes the data.
- **tests/test_methods.py**: Pytest-based unit tests for validating certain user inputs and behaviors in `MovieAnalyzer`.

---

## Data Source

This app downloads and works with the CMU Movie Summary dataset:
- [MovieSummaries.tar.gz](https://www.cs.cmu.edu/~ark/personas/data/MovieSummaries.tar.gz)

Upon first run, the dataset is automatically downloaded into a `downloads/` folder. Files are extracted and loaded into `pandas` DataFrames for analysis.

**Note**: The dataset includes:
- `movie.metadata.tsv` for movie info.
- `character.metadata.tsv` for actor info.
- `plot_summaries.txt` for plot summaries (used by the new LLM page).

---

## Setup & Installation

1. **Clone** or download this repository:
   ```bash
   git clone https://github.com/your-username/GROUP_17.git
   cd GROUP_17

Install dependencies. We recommend using a virtual environment:

    '''bash
    Copy
    Edit
    python -m venv venv
    source venv/bin/activate  # or "venv\Scripts\activate" on Windows
    pip install -r requirements.txt'''
(Optional) Install Pytest if not included:

    '''bash
    Copy
    Edit
    pip install pytest'''
[Local LLM Prerequisite for 3rd page]

The third page (3_Genre_Classifier.py) uses a local LLM from Ollama.

Install ollama on your system following their instructions.
Pull a model of your choice, e.g., llama2. In our case, the model works best with 'deepseek-r1:7b':
    '''bash
    Copy
    Edit
    ollama pull deepseek-r1:7b'''
Make sure the Python package ollama is installed (add to requirements.txt if needed):
    '''bash
    Copy
    Edit
    pip install ollama'''
Once installed, the third page can connect to your local model.
If you do not set up Ollama, the third page may fail or display errors, but the other two pages (Movie_Analyzer.py and 2_Movie_Releases_Over_Time.py) should continue to work.

Running the App
After installing all dependencies:

    '''bash
    Copy
    Edit
    streamlit run Movie_Analyzer.py'''
Streamlit will launch and usually open in your browser at http://localhost:8501.

Available Pages
When Streamlit starts, you will see a navigation menu (sidebar) with:

Movie_Analyzer.py (the default)

Most Common Movie Types: A bar chart of how often each genre appears.
Actor Count Distribution: Number of actors in each movie.
Actor Distributions: Filter actors by gender and height range, optionally showing a histogram.

2_Movie_Releases_Over_Time.py (listed as 'Movie Releases Over Time' in the sidebar)

Plots the number of movies released each year (optionally filtered by genre).
Plots actor births grouped by year or month.

3_Genre_Classifier.py (listed as 'Genre Classifier' in the sidebar)

Shuffle: Fetch a random movie, display its title & summary, show its genres from the database, then query the local LLM to classify its genre.
The LLM also checks if the classification matches the database’s list.

Running the Tests

If you have Pytest installed, you can run the tests by:

    '''bash
    Copy
    Edit
    pytest tests
These tests primarily validate:

movie_type method raises exceptions on invalid inputs.
actor_distributions method checks for valid gender and realistic height values.
Notes & Limitations
Large Data: The CMU Movie Summaries dataset can be sizable (a few hundred MBs). The app automatically downloads and extracts the data only once.
Performance: The local LLM calls (page 3) may take some time, depending on your hardware and the model size.
Genres: The genre data in movie.metadata.tsv is stored as JSON-like strings. The code parses and explodes them.
Plot Summaries: Not all movies have a summary. If a random movie’s summary is missing, the third page will display an empty summary.
Contributing
Pull requests, suggestions, and improvements are welcome!

For major changes, please open an issue first to discuss what you would like to change.
License
This project is licensed under your chosen license. (e.g., MIT, Apache 2.0, etc.)

sql
Copy
Edit

Enjoy exploring movie data and experimenting with local LLM-based genre classification!


Essay:




