# streamlit_app.py

import streamlit as st
import matplotlib.pyplot as plt
from analyzer import MovieAnalyzer

def main():
    st.title("CMU Movie Dataset Analyzer")

    # Create or reuse a global instance of MovieAnalyzer
    # (You could also do caching with st.cache_data or st.cache_resource)
    analyzer = MovieAnalyzer("http://www.cs.cmu.edu/~ark/personas/data/MovieSummaries.tar.gz")

    # --- 1. Movie Type Analysis ---
    st.header("Top N Movie Types")
    N = st.number_input("Select N", min_value=1, max_value=100, value=10)
    movie_type_df = analyzer.movie_type(N=N)
    st.bar_chart(data=movie_type_df, x="Movie_Type", y="Count")

    # --- 2. Actor Count ---
    st.header("Actor Count Distribution")
    actor_count_df = analyzer.actor_count()
    # For demonstration, let's just show a bar chart or line chart
    st.bar_chart(data=actor_count_df, x="NumberOfActors", y="MovieCount")

    # --- 3. Actor Distributions ---
    st.header("Actor Height Distributions")
    gender_options = ["All", "Male", "Female", "Unknown"]  # or derive from your data
    gender = st.selectbox("Select Gender", options=gender_options)
    min_height = st.number_input("Min Height (cm)", value=150.0)
    max_height = st.number_input("Max Height (cm)", value=200.0)
    plot_flag = st.checkbox("Show Plot?", value=False)

    # Retrieve the distribution DataFrame
    dist_df = analyzer.actor_distributions(
        gender=gender, 
        min_height=min_height, 
        max_height=max_height, 
        plot=plot_flag
    )
    st.write(dist_df.head(20))  # Just show a sample

    if plot_flag:
        # Possibly your method already plots via matplotlib. 
        # If so, you can capture that figure or re-plot it here:
        fig, ax = plt.subplots()
        ax.hist(dist_df["Height"], bins=20)
        ax.set_title(f"Height Distribution for {gender}")
        st.pyplot(fig)

if __name__ == "__main__":
    main()
