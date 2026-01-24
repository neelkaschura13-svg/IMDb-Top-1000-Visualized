import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


st.title("Movie Catalogue")
st.markdown("""
This page allows you to find movies based on your Genre prefrences or Director prefrence. 
""")

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



if selected_genres or selected_directors or (selected_years != (min_year, max_year)):
    show_list = True
    
# Display results
st.markdown("<style>img {max-width: 100%; height: auto;}</style>", unsafe_allow_html=True)

st.title("IMDb Top 1000 Movies")
st.subheader(f"Showing {len(filtered_df)} movies")

#Increasing resolution of Movie posters
def enhance_poster_url(poster_url):
    """Use 720p resolution images for better performance"""
    if not poster_url or not poster_url.startswith('https://m.media-amazon.com/images/'):
        return poster_url
    
    # Use 720p resolution (smaller than full size but still good quality)
    # Replace with 720p dimensions
    enhanced_url = poster_url.replace('_V1_UX67_CR0,0,67,98_AL_', '_V1_UX200_CR0,0,200,300_AL_')
    return enhanced_url

# Display movie list with table
if len(filtered_df) > 0:
    display_df = filtered_df[[
        'Series_Title', 
        'Released_Year', 
        'Genre', 
        'IMDB_Rating',
        'Director',
        'Star1','Star2','Star3','Star4'
    ]].copy()

    # Add rank column
    display_df.insert(0, 'Rank', range(1, len(display_df) + 1))

    # Display without pandas index
    st.dataframe(display_df, use_container_width=True, hide_index=True)

# Display results
if len(filtered_df) > 0:
    if show_list:  # Only show list if filters are applied
        st.subheader("Movie Details")
        for idx, movie in filtered_df.iterrows():
            rank = idx + 1
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if pd.notna(movie['Poster_Link']) and movie['Poster_Link'] != '':
                    st.image(enhance_poster_url(movie['Poster_Link']), width=210)
            
            with col2:
                st.markdown(f"<h2 style='font-size: 24px;'>{rank}. {movie['Series_Title']} ({int(movie['Released_Year'])})</h2>", unsafe_allow_html=True)
                st.markdown(f"*Rating:* {movie['IMDB_Rating']}")
                st.markdown(f"*Genre:* {movie['Genre']}")
                st.markdown(f"*Director:* {movie['Director']}")
                st.markdown(f"*Overview:* {movie['Overview']}")
                st.markdown(f"*Stars:* {movie['Star1']}, {movie['Star2']}, {movie['Star3']}, {movie['Star4']}")
                st.markdown(f"<span style='font-family: monospace;'>*Votes:* {int(movie['No_of_Votes']):,}</span>", unsafe_allow_html=True)
            st.markdown("---")
    else:
        # Show initial message when no filters applied
        st.info("Apply filters above to see movie details")
else:
    if show_list:
        st.write("No movies match your search criteria.")
    else:
        st.info("Apply filters above to see movie details")

        