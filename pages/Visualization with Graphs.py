import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


st.title("Comparisions")

df = st.session_state.data.copy()
df2 = st.session_state.data2.copy()


#Cleaning cast list for dataframe 2 
df2['cast_clean'] = (
    df2['cast']
    .str.replace("'", "", regex=True)
    .str.replace(r"^\s*", "", regex=True)
    .str.replace(r"\s*$", "", regex=True)
    .str.replace(r",\s*", ", ", regex=True)
    .str.strip()
)
#combining and simplifying df and df2
#df
df['Released_Year'] = pd.to_numeric(df['Released_Year'], errors='coerce')
##split genres
all_genres = df['Genre'].str.split(',').explode().str.strip().unique()
##actors
all_actors = list(set(df[['Star1', 'Star2', 'Star3', 'Star4']].apply(lambda x: x.str.strip()).values.flatten()))

#df2
df2['startYear'] = pd.to_numeric(df2['startYear'], errors='coerce')
df2['endYear'] = pd.to_numeric(df2['endYear'], errors='coerce')
df2['numVotes'] = pd.to_numeric(df2['numVotes'], errors='coerce')
all_genres_df2 = df2['genres'].str.split(',').explode().str.strip().unique()
all_actors_df2 = list(set(df2['cast'].str.split(',').explode().str.strip().unique()))

# Combine all genres and actors from df and df2
all_genres = list(set(all_genres).union(set(all_genres_df2)))
all_actors = list(set(all_actors).union(set(all_actors_df2)))


# Sidebar filters
st.sidebar.header("Filters")

## Year range filter
min_year = int(df['Released_Year'].min())
max_year = int(df2['endYear'].max())
selected_years = st.sidebar.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

## Number of votes filter
min_votes, max_votes = int(min(df['No_of_Votes'].min(), df2['numVotes'].min())), int(max(df['No_of_Votes'].max(), df2['numVotes'].max()))
selected_votes = st.sidebar.slider(
    "Select Number of Votes Range",
    min_value=min_votes,
    max_value=max_votes,
    value=(min_votes, max_votes)
)
##Dropdown boxes
selected_genres = st.sidebar.multiselect('Select Genres', all_genres)
selected_directors = st.sidebar.multiselect('Select Directors', df['Director'].unique())
selected_actors = st.sidebar.multiselect('Select Actors', all_actors)



# AND/OR/NOT logic
logic_mode = st.sidebar.radio("Filter Logic", ("OR (Any Selected Genre/Director/Actor)", "AND (All Selected Genre/Director/Actor)", "NOT (Exclude Selected Genre/Director/Actor)"), index=0)

##Initialize show_list
show_list = False

# Filtering logic for df and df2
filtered_df = df[
    (df['Released_Year'] >= selected_years[0]) &
    (df['Released_Year'] <= selected_years[1]) &
    (df['No_of_Votes'] >= selected_votes[0]) &
    (df['No_of_Votes'] <= selected_votes[1])
]

filtered_df2 = df2[
    (df2['startYear'] >= selected_years[0]) &
    (df2['endYear'] <= selected_years[1]) &
    (df2['numVotes'] >= selected_votes[0]) &
    (df2['numVotes'] <= selected_votes[1])
]

if selected_genres or selected_directors or selected_actors:
    show_list = True
    def filter_criteria(movie_genres, movie_directors, movie_actors, logic_mode):
        movie_genres_list = [g.strip().lower() for g in movie_genres.split(',')]
        movie_directors_list = [d.strip().lower() for d in movie_directors.split(',')]
        movie_actors_list = [a.strip().lower() for a in movie_actors]
        selected_genres_lower = [g.lower() for g in selected_genres]
        selected_directors_lower = [d.lower() for d in selected_directors]
        selected_actors_lower = [a.lower() for a in selected_actors]

        if logic_mode == "AND (All Selected Genre/Director/Actor)":
            genre_match = all(genre in movie_genres_list for genre in selected_genres_lower) if selected_genres else True
            director_match = all(director in movie_directors_list for director in selected_directors_lower) if selected_directors else True
            actor_match = all(actor in movie_actors_list for actor in selected_actors_lower) if selected_actors else True
            return genre_match and director_match and actor_match
        elif logic_mode == "OR (Any Selected Genre/Director/Actor)":
            genre_match = any(genre in movie_genres_list for genre in selected_genres_lower) if selected_genres else False
            director_match = any(director in movie_directors_list for director in selected_directors_lower) if selected_directors else False
            actor_match = any(actor in movie_actors_list for actor in selected_actors_lower) if selected_actors else False
            return genre_match or director_match or actor_match
        elif logic_mode == "NOT (Exclude Selected Genre/Director/Actor)":
            genre_match = not any(genre in movie_genres_list for genre in selected_genres_lower) if selected_genres else True
            director_match = not any(director in movie_directors_list for director in selected_directors_lower) if selected_directors else True
            actor_match = not any(actor in movie_actors_list for actor in selected_actors_lower) if selected_actors else True
            return genre_match and director_match and actor_match

    filtered_df = filtered_df[filtered_df.apply(lambda row: filter_criteria(row['Genre'], row['Director'], [row['Star1'], row['Star2'], row['Star3'], row['Star4']], logic_mode), axis=1)]
    filtered_df2 = filtered_df2[filtered_df2.apply(lambda row: filter_criteria(row['genres'], '', row['cast'].split(','), logic_mode), axis=1)]

combined_filtered_df = pd.concat([filtered_df, filtered_df2], ignore_index=True)
# Row 1: Ratings Distribution & Top Directors

tab1, tab2 = st.tabs(["IMDb Top 1000","Netflix List"]) 



with tab1: 
    if filtered_df.empty:
        st.info("No Results Found The selected filters did not return any movies. Please adjust your filters and try again.")
    else:     
        col1, col2 = st.columns(2)
        with col1: #distribution of IMDb ratings
            st.subheader("Rating Distribution")
            fig1, ax1 = plt.subplots(figsize=(6, 4))
            if not filtered_df['IMDB_Rating'].empty:
                sns.histplot(filtered_df['IMDB_Rating'], kde=True, ax=ax1, color='skyblue')
                ax1.set_title("Distribution of IMDb Ratings")
                ax1.set_xlabel("IMDB Rating")
                ax1.set_ylabel("Frequency")
                st.pyplot(fig1)
            else:
                st.write("No IMDB Ratings available for the selected filters.")
        with col2: #Top directors by movie count 
            if not filtered_df['IMDB_Rating'].empty:
                st.subheader("Top Directors (by Movie Count)")
                top_directors = filtered_df['Director'].value_counts().head(10)
                fig2, ax2 = plt.subplots(figsize=(6, 4))
                top_directors.plot(kind='barh', ax=ax2, color='lightgreen')
                ax2.set_title("Top Directors (by Number of Movies)")
                ax2.set_xlabel("Number of Movies")
                st.pyplot(fig2)
            else:
                st.write("No IMDB Ratings available for the selected filters.")
       
        col3, col4 = st.columns(2)
        
        with col3:
            if not filtered_df['IMDB_Rating'].empty:
                st.subheader("Genre Distribution")
                genre_series = filtered_df['Genre'].str.split(',').explode().str.strip()
                genre_counts = genre_series.value_counts()
                fig3, ax3 = plt.subplots(figsize=(6, 4))
                genre_counts.plot(kind='bar', ax=ax3, color='salmon')
                ax3.set_title("Movies by Genre")
                ax3.set_xlabel("Genre")
                ax3.set_ylabel("Number of Movies")
                plt.xticks(rotation=45)
                st.pyplot(fig3)
            else:
                st.write("No IMDB Ratings available for the selected filters.")
        with col4:
            if not filtered_df['IMDB_Rating'].empty:
                st.subheader("IMDB Rating vs Released Year (Every 5 Years)")
                # bins for every 5 years
                col4_bins = range(int(filtered_df['Released_Year'].min()), int(filtered_df['Released_Year'].max()) + 5, 5)
                filtered_df['Year_Bin'] = pd.cut(filtered_df['Released_Year'], col4_bins, right=False, include_lowest=True)
        
                # Ensure the Year_Bin column is not empty
                if not filtered_df['Year_Bin'].isnull().all():
                    fig4, ax4 = plt.subplots(figsize=(6, 4))
                    sns.boxplot(data=filtered_df, x='Year_Bin', y='IMDB_Rating', palette='viridis', ax=ax4)
                    ax4.set_title("IMDB Rating vs Released Year (Every 5 Years)")
                    ax4.set_xlabel("Released Year (Every 5 Years)")
                    ax4.set_ylabel("IMDB Rating")
                    plt.xticks(rotation=45)
                    st.pyplot(fig4)
                else:
                    st.write("No data available for the selected filters.")
            else:
                st.write("No IMDB Ratings available for the selected filters.")

        col5, col6 = st.columns(2)
        with col5:
            if not filtered_df['IMDB_Rating'].empty:
                if not filtered_df['IMDB_Rating'].empty:
                    st.subheader("Runtime vs. IMDB Rating (Runtime Bins)")
                    bins = range(int(filtered_df['Runtime'].min()), int(filtered_df['Runtime'].max()) + 30, 30)
                    filtered_df['Runtime_Bin'] = pd.cut(filtered_df['Runtime'], bins, right=False, include_lowest=True)            
                    fig5, ax5 = plt.subplots(figsize=(6, 4))
                    sns.scatterplot(data=filtered_df, x='Runtime', y='IMDB_Rating', ax=ax5)
                    ax5.set_title("Runtime vs. IMDB Rating (Runtime Bins)")
                    ax5.set_xlabel("Runtime (minutes)")
                    ax5.set_ylabel("IMDB Rating")
                    st.pyplot(fig5)
                else:
                    st.write("No IMDB Ratings available for the selected filters.")
            
with tab2: 
    st.title("Graphs") 
    if combined_filtered_df.empty:
        st.info("No Results Found. The selected filters did not return any movies. Please adjust your filters and try again.")
    else:
        col1, col2 = st.columns(2)
        with col1:  # distribution of IMDb ratings
            st.subheader("Rating Distribution")
            fig1, ax1 = plt.subplots(figsize=(6, 4))
            if not combined_filtered_df['rating'].empty:
                sns.histplot(combined_filtered_df['rating'], kde=True, ax=ax1, color='skyblue')
                ax1.set_title("Distribution of Netflix Ratings")
                ax1.set_xlabel("Netflix Rating")
                ax1.set_ylabel("Frequency")
                st.pyplot(fig1)
            else:
                st.write("No Netflix Ratings available for the selected filters.")
    
