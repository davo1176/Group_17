import streamlit as st
import matplotlib.pyplot as plt
from src.movie_analyzer import MovieAnalyzer

def main():
    st.title("Chronological Information")

    # 1. Initialize the analyzer
    try:
        analyzer = MovieAnalyzer()  # If large, you could cache with st.cache_data
    except Exception as e:
        st.error(f"Could not load data: {e}")
        st.stop()

    # =========================
    # PART A: Releases by Year
    # =========================
    st.subheader("Number of Movie Releases per Year")
    # Limiting the genres to a few examples for time's sake:
    possible_genres = [None, "Drama", "Comedy", "Action", "Romance", "Horror", "Thriller"]
    chosen_genre = st.selectbox("Filter by Genre (optional)", possible_genres, index=0)

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
            # Optionally display the raw dataframe
            # st.write(releases_df)
    except Exception as e:
        st.error(f"Error computing releases: {e}")

    # ====================================
    # PART B: Actor Births (ages) by Year
    # ====================================
    st.subheader("Number of Actor Births")
    mode = st.selectbox("Group births by:", ["Y", "M", "D"], index=0)

    try:
        ages_df = analyzer.ages(mode=mode)
        if ages_df.empty:
            st.info("No valid actor birthdate data found.")
        else:
            # For clarity, rename columns for plotting
            if mode == "Y":
                x_col = "Birth_Year"
            elif mode == "M":
                x_col = "Birth_Month"
            else:
                x_col = "Birth_Day"

            fig2, ax2 = plt.subplots()
            ax2.bar(ages_df[x_col], ages_df["Count"])
            ax2.set_xlabel(x_col)
            ax2.set_ylabel("Count")
            ax2.set_title("Actor Births Grouped by " + x_col)
            st.pyplot(fig2)
            # Optionally display the raw dataframe
            # st.write(ages_df)
    except Exception as e:
        st.error(f"Error computing ages: {e}")

if __name__ == "__main__":
    main()
