import streamlit as st
import matplotlib.pyplot as plt

from src.movie_analyzer import MovieAnalyzer

def main():
    st.title("Movie Analysis App")

    try:
        with st.spinner("Downloading and processing data..."):
            st.write("Initializing MovieAnalyzer...")
            analyzer = MovieAnalyzer()
            st.write("Data loaded successfully!")
    except Exception as e:
        st.error(f"Error initializing MovieAnalyzer: {e}")
        st.stop()

    # 1. Movie Types
    st.header("Most Common Movie Types")
    N = st.number_input("Select N:", min_value=1, max_value=100, value=10, step=1)
    try:
        movie_type_df = analyzer.movie_type(N=N)
        fig_1, ax_1 = plt.subplots()
        ax_1.bar(movie_type_df["Movie_Type"], movie_type_df["Count"])
        ax_1.set_xlabel("Movie Type")
        ax_1.set_ylabel("Count")
        # Rotate x-axis labels for clarity.
        plt.setp(ax_1.get_xticklabels(), rotation=45, ha="right")
        st.pyplot(fig_1)
    except Exception as e:
        st.error(f"Error in movie_type: {e}")

    # 2. Actor Count Distribution
    st.header("Actor Count Distribution")
    try:
        actor_count_df = analyzer.actor_count()
        fig_2, ax_2 = plt.subplots()
        ax_2.bar(actor_count_df["Number_of_Actors"], actor_count_df["Movie_Count"])
        ax_2.set_xlabel("Number of Actors")
        ax_2.set_ylabel("Movie Count")
        st.pyplot(fig_2)
    except Exception as e:
        st.error(f"Error in actor_count: {e}")

    # 3. Actor Distributions
    st.header("Actor Distributions")
    gender = st.selectbox("Select Gender:", ["All", "M", "F"])
    min_height = st.number_input("Min Height:", value=130.0)
    max_height = st.number_input("Max Height:", value=210.0)
    do_plot = st.checkbox("Show Distribution Plot?", value=False)
    try:
        # If plot is requested, actor_distributions returns (df, fig)
        result = analyzer.actor_distributions(
            gender=gender,
            max_height=max_height,
            min_height=min_height,
            plot=do_plot
        )
        if do_plot:
            df, fig = result
            st.pyplot(fig)
            if df.empty:
                st.info("No actor data matches the given criteria.")
            else:
                st.write(df)
        else:
            if result.empty:
                st.info("No actor data matches the given criteria.")
            else:
                st.write(result)
    except Exception as e:
        st.error(f"Error in actor_distributions: {e}")

if __name__ == "__main__":
    main()
