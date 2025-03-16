import streamlit as st
import matplotlib.pyplot as plt
from src.movie_analyzer import MovieAnalyzer

def main():
    st.title("Chronological Information")
    try:
        analyzer = MovieAnalyzer()
    except Exception as e:
        st.error(f"Could not load data: {e}")
        st.stop()

    st.subheader("Number of Movie Releases per Year")

    # We limit possible genres; the first one is the literal string "None"
    possible_genres = ["None", "Drama", "Comedy", "Action", "Romance", "Horror", "Thriller"]
    chosen_genre = st.selectbox("Filter by Genre (optional)", possible_genres, index=0)

    # Pass the chosen genre directly. Our new signature can handle either "None" or None.
    try:
        releases_df = analyzer.releases(genre=chosen_genre)
        if releases_df.empty:
            st.info("No movies found for that genre or the data is missing.")
        else:
            fig1, ax1 = plt.subplots()
            ax1.bar(releases_df["Year"], releases_df["Count"])
            ax1.set_xlabel("Year")
            ax1.set_ylabel("Number of Movies")
            ax1.set_title("Movie Releases Over Time")
            st.pyplot(fig1)
    except Exception as e:
        st.error(f"Error computing releases: {e}")

    st.subheader("Number of Actor Births")
    mode = st.selectbox("Group births by:", ["Y", "M"], index=0)
    try:
        ages_df = analyzer.ages(mode=mode)
        if ages_df.empty:
            st.info("No valid actor birthdate data found.")
        else:
            if mode == "M":
                x_col = "Birth Month"
            else:
                x_col = "Birth Year"
                
            fig2, ax2 = plt.subplots()
            ax2.bar(ages_df[x_col], ages_df["Count"])
            ax2.set_xlabel(x_col)
            ax2.set_ylabel("Count")
            ax2.set_title("Actor Births Grouped by " + x_col)
            st.pyplot(fig2)
    except Exception as e:
        st.error(f"Error computing ages: {e}")

if __name__ == "__main__":
    main()
