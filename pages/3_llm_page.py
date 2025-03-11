import streamlit as st
import matplotlib.pyplot as plt

from src.movie_analyzer import MovieAnalyzer

# If using the ollama Python client, import it here.
# If not installed or you have a different approach, adjust as needed.
# pip install ollama
import ollama

def main():
    st.title("Local LLM Genre Classifier")

    # Initialize analyzer
    try:
        analyzer = MovieAnalyzer()
    except Exception as e:
        st.error(f"Could not initialize MovieAnalyzer: {e}")
        st.stop()

    st.write("Click **Shuffle** to classify a random movie by its plot summary.")

    if "random_movie_info" not in st.session_state:
        st.session_state["random_movie_info"] = None
    if "last_classification" not in st.session_state:
        st.session_state["last_classification"] = None
    if "match_answer" not in st.session_state:
        st.session_state["match_answer"] = None

    # Define a function to get random movie and classify with LLM
    def shuffle_and_classify():
        # 1. Get a random movie from the database
        random_movie = analyzer.get_random_movie_info()

        # 2. Prepare LLM prompt for classification
        summary_text = random_movie["summary"]
        prompt = f"""
You are a concise movie-genre classifier. 
Given the following movie summary, respond ONLY with one or more genres in a comma-separated list. 
Do NOT include extra text.

Summary:
{summary_text}
"""
        # 3. Call the local LLM (model name can be changed if you have another local model)
        try:
            response = ollama.complete(prompt=prompt, model="deepseek-r1:1.5B")
            # Typically, the .complete() returns a dict with { 'choices': [ { 'text': ... } ] }
            llm_genres_text = response["choices"][0]["text"].strip()
        except Exception as e:
            llm_genres_text = f"Error with LLM: {e}"

        # 4. Ask LLM if its recognized genres appear in the DB’s genre list
        #    We do a second prompt to check for "Yes" or "No".
        db_genres_list = random_movie["genres_list"]
        check_prompt = f"""
You identified these genres for the movie: {llm_genres_text}.
The database says these are the movie’s genres: {db_genres_list}.
Do all of your identified genres appear in the database's list? 
Answer with only "Yes" or "No".
"""
        try:
            check_response = ollama.complete(prompt=check_prompt, model="deepseek-r1:1.5B")
            match_answer = check_response["choices"][0]["text"].strip()
        except Exception as e:
            match_answer = f"Error with LLM: {e}"

        # 5. Update session_state
        st.session_state["random_movie_info"] = random_movie
        st.session_state["last_classification"] = llm_genres_text
        st.session_state["match_answer"] = match_answer

    # Button to shuffle
    if st.button("Shuffle"):
        shuffle_and_classify()

    # Display the results in text boxes
    # 1. Title & summary
    if st.session_state["random_movie_info"] is not None:
        info = st.session_state["random_movie_info"]
        st.text_area("Title & Summary", f"{info['title']}\n\n{info['summary']}", height=200)

        # 2. Genres from DB
        st.text_area("Database Genres", ", ".join(info["genres_list"]), height=50)

        # 3. LLM Classification
        st.text_area("LLM Classified Genres", st.session_state["last_classification"] or "", height=50)

        # 4. The yes/no check from the LLM
        st.write(f"**LLM says the classification matches the DB’s genres:** {st.session_state['match_answer']}")


# Streamlit convention to call main()
if __name__ == "__main__":
    main()
