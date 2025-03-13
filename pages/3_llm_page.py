import re
import streamlit as st
import matplotlib.pyplot as plt

from src.movie_analyzer import MovieAnalyzer

# pip install ollama
from ollama import chat

def main():
    st.title("Local LLM Genre Classifier")

    try:
        analyzer = MovieAnalyzer()
    except Exception as e:
        st.error(f"Could not initialize MovieAnalyzer: {e}")
        st.stop()

    st.write("Click **Shuffle** to classify a random movie by its plot summary.")

    if "random_movie_info" not in st.session_state:
        st.session_state["random_movie_info"] = None
    if "final_reply" not in st.session_state:
        st.session_state["final_reply"] = None

    def shuffle_and_classify():
        random_movie = analyzer.get_random_movie_info()
        summary_text = random_movie["summary"]
        db_genres_list = random_movie["genres_list"]

        # Combined prompt letting the model think, including chain-of-thought.
        prompt = f"""
You are a concise movie-genre classifier and verifier.
Given the following movie summary and the database genres, determine the genres that apply, then verify if they match the database.
Output in this format:

(START OF FORMAT DONT OUTPUT THIS LINE)
I've identified the genres: (LIST GENRES HERE) 
Do they match the database? (YES/NO)
(END OF FORMAT DONT OUTPUT THIS LINE)

        
Movie Summary:
{summary_text}

Database Genres:
{', '.join(db_genres_list)}
"""
        try:
            response = chat(model="deepseek-r1:7b", messages=[{"role": "user", "content": prompt}])
            full_reply = response['message']['content'].strip()
            # Remove chain-of-thought: delete anything between <think> and </think> (including the tags)
            final_reply = re.sub(r'<think>.*?</think>', '', full_reply, flags=re.DOTALL).strip()
        except Exception as e:
            final_reply = f"Error with LLM: {e}"

        st.session_state["random_movie_info"] = random_movie
        st.session_state["final_reply"] = final_reply

    if st.button("Shuffle"):
        shuffle_and_classify()

    if st.session_state["random_movie_info"] is not None:
        info = st.session_state["random_movie_info"]
        st.text_area("Title & Summary", f"{info['title']}\n\n{info['summary']}", height=200)
        st.text_area("Database Genres", ", ".join(info["genres_list"]), height=68)
        st.text_area("LLM Response", st.session_state["final_reply"] or "", height=100)

if __name__ == "__main__":
    main()
