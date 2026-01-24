import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


st.title("Comparisions")

df = st.session_state.data.copy()



# Convert Released_Year to integer
df['Released_Year'] = pd.to_numeric(df['Released_Year'], errors='coerce')

# Sidebar filters
st.sidebar.header("Filters")

# Year range filter
min_year, max_year = int(df['Released_Year'].min()), int(df['Released_Year'].max())
selected_years = st.sidebar.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Genre filter
all_genres = df['Genre'].str.split(',').explode().str.strip().unique()
selected_genres = st.sidebar.multiselect(
    "Select Genres",
    options=all_genres,
    default=[]
)

# Director filter
all_directors = df['Director'].str.split(',').explode().str.strip().unique()
selected_directors = st.sidebar.multiselect(
    "Select Directors",
    options=all_directors,
    default=[]
)

#AND/OR logic
logic_mode = st.sidebar.radio("Filter Logic", ("OR (Any Selected Genre/Director)", "AND (All Selected Genre/Director)"), index=0)
filtered_df = df[
    (df['Released_Year'] >= selected_years[0]) &
    (df['Released_Year'] <= selected_years[1])
]

show_list = False

# Genre and director filtering based on logic mode
if selected_genres or selected_directors:
    if logic_mode == "AND (All Selected Genre/Director)":
        def has_all_criteria(movie_genres, movie_directors):
            movie_genres_list = [g.strip().lower() for g in movie_genres.split(',')]
            movie_directors_list = [d.strip().lower() for d in movie_directors.split(',')]
            selected_genres_lower = [g.lower() for g in selected_genres]
            selected_directors_lower = [d.lower() for d in selected_directors]
            
            genre_match = all(genre in movie_genres_list for genre in selected_genres_lower) if selected_genres else True
            director_match = all(director in movie_directors_list for director in selected_directors_lower) if selected_directors else True
            
            return genre_match and director_match
        
        filtered_df = filtered_df[filtered_df.apply(lambda row: has_all_criteria(row['Genre'], row['Director']), axis=1)]
    else:
        def has_any_criteria(movie_genres, movie_directors):
            movie_genres_list = [g.strip().lower() for g in movie_genres.split(',')]
            movie_directors_list = [d.strip().lower() for d in movie_directors.split(',')]
            selected_genres_lower = [g.lower() for g in selected_genres]
            selected_directors_lower = [d.lower() for d in selected_directors]
            
            genre_match = any(genre in movie_genres_list for genre in selected_genres_lower) if selected_genres else False
            director_match = any(director in movie_directors_list for director in selected_directors_lower) if selected_directors else False
            
            return genre_match or director_match
        
        filtered_df = filtered_df[filtered_df.apply(lambda row: has_any_criteria(row['Genre'], row['Director']), axis=1)]

st.sidebar.markdown(f"**Movies shown:** {len(filtered_df)}")


# Row 1: Ratings Distribution & Top Directors
col1, col2 = st.columns(2)

with col1:
    st.subheader("Rating Distribution")
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    sns.histplot(filtered_df['IMDB_Rating'], bins=20, kde=True, ax=ax1, color='skyblue')
    ax1.set_title("Distribution of IMDb Ratings")
    ax1.set_xlabel("IMDB Rating")
    ax1.set_ylabel("Frequency")
    st.pyplot(fig1)

with col2:
    st.subheader("Top Directors (by Movie Count)")
    top_directors = filtered_df['Director'].value_counts().head(10)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    top_directors.plot(kind='barh', ax=ax2, color='lightgreen')
    ax2.set_title("Top Directors (by Number of Movies)")
    ax2.set_xlabel("Number of Movies")
    st.pyplot(fig2)


    # Row 2: Genre Distribution & Box Office
col3, col4 = st.columns(2)

with col3:
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

with col4:
    st.subheader("Box Office Performance (Top 20)")
    top_grossing = filtered_df[['Series_Title', 'Gross']].dropna().sort_values(by='Gross', ascending=False).head(20)
    fig4, ax4 = plt.subplots(figsize=(6, 4))
    ax4.barh(top_grossing['Series_Title'], top_grossing['Gross'], color='gold')
    ax4.set_title("Top 20 Highest Grossing Movies")
    ax4.set_xlabel("Gross (in USD)")
    st.pyplot(fig4)
    
