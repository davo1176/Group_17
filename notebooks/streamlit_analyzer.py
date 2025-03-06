import streamlit as st
import pandas as pd

# If the methods are in InitializeMovieData:
from initiate_data import InitializeMovieData
from movie_analyzer import MovieAnalyzer

# Or if you created a separate class:
# from src.analyzer import MovieAnalyzer

def main():
    st.title("Movie Analysis App")

    # 1. Initialize or load data
    st.subheader("Data Initialization")
    init_obj = InitializeMovieData()
    st.write("Data successfully loaded!")

    # (Optional) If you used a separate Analyzer class:
    # analyzer = MovieAnalyzer(
    #     init_obj.movies_df, 
    #     init_obj.actors_df
    # )

    # 2. movie_type
    st.subheader("1) Most Common Movie Types")
    N = st.number_input("Select the top N movie types:", min_value=1, value=10)
    movie_type_df = MovieAnalyzer.movie_type(N)  # or analyzer.movie_type(N)
    st.dataframe(movie_type_df)
    # Optionally plot as a bar chart
    if not movie_type_df.empty:
        st.bar_chart(movie_type_df.set_index("Movie_Type")["Count"])

    # 3. actor_count
    st.subheader("2) Distribution of Number of Actors per Movie")
    actor_count_df = init_obj.actor_count()  # or analyzer.actor_count()
    st.dataframe(actor_count_df)
    # Plot
    if not actor_count_df.empty:
        st.bar_chart(actor_count_df.set_index("number_of_actors")["movie_counts"])

    # 4. actor_distributions
    st.subheader("3) Actor Height Distributions")
    gender_options = ["All", "Male", "Female"]  # or glean from data
    selected_gender = st.selectbox("Select Gender", gender_options)
    col1, col2 = st.columns(2)
    with col1:
        min_h = st.number_input("Min Height", value=150.0)
    with col2:
        max_h = st.number_input("Max Height", value=200.0)

    # Toggle for plotting
    do_plot = st.checkbox("Show Height Distribution Plot", value=False)
    distribution_df = init_obj.actor_distributions(
        gender=selected_gender,
        max_height=float(max_h),
        min_height=float(min_h),
        plot=do_plot
    )
    st.dataframe(distribution_df.head(50))  # show top 50 rows as example

if __name__ == "__main__":
    main()
