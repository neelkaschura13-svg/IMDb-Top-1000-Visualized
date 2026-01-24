import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


st.title("Movie Catalogue")
st.markdown("""
This Page allows you to search for movies as per year, votes, genres, directors and actors.
""")

df = st.session_state.data.copy()

df['Released_Year'] = pd.to_numeric(df['Released_Year'], errors='coerce')


# Convert Released_Year to numeric
df['Released_Year'] = pd.to_numeric(df['Released_Year'], errors='coerce')

# Split genres into individual genres and create a unique list
all_genres = df['Genre'].str.split(',').explode().str.strip().unique()

# Combine all actor columns into a single series
all_actors = pd.concat([df['Star1'], df['Star2'], df['Star3'], df['Star4']]).str.strip().unique()


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

# Number of votes filter
min_votes, max_votes = int(df['No_of_Votes'].min()), int(df['No_of_Votes'].max())
selected_votes = st.sidebar.slider(
    "Select Number of Votes Range",
    min_value=min_votes,
    max_value=max_votes,
    value=(min_votes, max_votes)
)

selected_genres = st.sidebar.multiselect('Select Genres', all_genres)
selected_directors = st.sidebar.multiselect('Select Directors', df['Director'].unique())
selected_actors = st.sidebar.multiselect('Select Actors', all_actors)

# AND/OR/NOT logic
logic_mode = st.sidebar.radio("Filter Logic", ("OR (Any Selected Genre/Director/Actor)", "AND (All Selected Genre/Director/Actor)", "NOT (Exclude Selected Genre/Director/Actor)"), index=0)

# Initialize show_list
show_list = False

# Filtering logic
filtered_df = df[
    (df['Released_Year'] >= selected_years[0]) &
    (df['Released_Year'] <= selected_years[1]) &
    (df['No_of_Votes'] >= selected_votes[0]) &
    (df['No_of_Votes'] <= selected_votes[1])
]


if selected_genres or selected_directors or selected_actors:
    show_list = True
    if logic_mode == "AND (All Selected Genre/Director/Actor)":
        def has_all_criteria(movie_genres, movie_directors, movie_actors):
            movie_genres_list = [g.strip().lower() for g in movie_genres.split(',')]
            movie_directors_list = [d.strip().lower() for d in movie_directors.split(',')]
            movie_actors_list = [a.strip().lower() for a in movie_actors]
            selected_genres_lower = [g.lower() for g in selected_genres]
            selected_directors_lower = [d.lower() for d in selected_directors]
            selected_actors_lower = [a.lower() for a in selected_actors]

            genre_match = all(genre in movie_genres_list for genre in selected_genres_lower) if selected_genres else True
            director_match = all(director in movie_directors_list for director in selected_directors_lower) if selected_directors else True
            actor_match = all(actor in movie_actors_list for actor in selected_actors_lower) if selected_actors else True

            return genre_match and director_match and actor_match

        filtered_df = filtered_df[filtered_df.apply(lambda row: has_all_criteria(row['Genre'], row['Director'], [row['Star1'], row['Star2'], row['Star3'], row['Star4']]), axis=1)]
    elif logic_mode == "OR (Any Selected Genre/Director/Actor)":
        def has_any_criteria(movie_genres, movie_directors, movie_actors):
            movie_genres_list = [g.strip().lower() for g in movie_genres.split(',')]
            movie_directors_list = [d.strip().lower() for d in movie_directors.split(',')]
            movie_actors_list = [a.strip().lower() for a in movie_actors]
            selected_genres_lower = [g.lower() for g in selected_genres]
            selected_directors_lower = [d.lower() for d in selected_directors]
            selected_actors_lower = [a.lower() for a in selected_actors]

            genre_match = any(genre in movie_genres_list for genre in selected_genres_lower) if selected_genres else False
            director_match = any(director in movie_directors_list for director in selected_directors_lower) if selected_directors else False
            actor_match = any(actor in movie_actors_list for actor in selected_actors_lower) if selected_actors else False

            return genre_match or director_match or actor_match

        filtered_df = filtered_df[filtered_df.apply(lambda row: has_any_criteria(row['Genre'], row['Director'], [row['Star1'], row['Star2'], row['Star3'], row['Star4']]), axis=1)]
    elif logic_mode == "NOT (Exclude Selected Genre/Director/Actor)":
        def has_not_criteria(movie_genres, movie_directors, movie_actors):
            movie_genres_list = [g.strip().lower() for g in movie_genres.split(',')]
            movie_directors_list = [d.strip().lower() for d in movie_directors.split(',')]
            movie_actors_list = [a.strip().lower() for a in movie_actors]
            selected_genres_lower = [g.lower() for g in selected_genres]
            selected_directors_lower = [d.lower() for d in selected_directors]
            selected_actors_lower = [a.lower() for a in selected_actors]

            genre_match = not any(genre in movie_genres_list for genre in selected_genres_lower) if selected_genres else True
            director_match = not any(director in movie_directors_list for director in selected_directors_lower) if selected_directors else True
            actor_match = not any(actor in movie_actors_list for actor in selected_actors_lower) if selected_actors else True

            return genre_match and director_match and actor_match

        filtered_df = filtered_df[filtered_df.apply(lambda row: has_not_criteria(row['Genre'], row['Director'], [row['Star1'], row['Star2'], row['Star3'], row['Star4']]), axis=1)]

# Display the number of filtered movies
st.sidebar.markdown(f"**Movies shown:** {len(filtered_df)}")

# Check if any filters are applied
if selected_genres or selected_directors or selected_actors or (selected_years != (min_year, max_year)) or (selected_votes != (min_votes, max_votes)):
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

# Initialize watched_count and watched_list in session state
if 'watched_count' not in st.session_state:
    st.session_state.watched_count = 0
if 'watched_list' not in st.session_state:
    st.session_state.watched_list = []

tab1, tab2 = st.tabs(["Movie List", "Movies Watched"])
# Display results
with tab1:
    if len(filtered_df) > 0:
        if show_list:  # Only show list if filters are applied
            st.subheader("Movie Details")
            for idx, movie in filtered_df.iterrows():
                rank = idx + 1
                col1, col2, col3 = st.columns([1, 4, 1])
            
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
             
                with col3:
                    if st.checkbox(f"Did you watch this movie?", key=f"watched_{idx}", value=(movie['Series_Title'] in st.session_state.watched_list)):
                        if movie['Series_Title'] not in st.session_state.watched_list:
                            st.session_state.watched_list.append(movie['Series_Title'])
                            st.session_state.watched_count += 1
                    else:
                        if movie['Series_Title'] in st.session_state.watched_list:
                            st.session_state.watched_list.remove(movie['Series_Title'])
                            st.session_state.watched_count -= 1

                st.markdown("---")

            st.sidebar.markdown(
                f"""
                <style>
                .sidebar-watched-count {{
                    position: fixed;
                    top: 10px;
                    right: 1400px;
                    background-color: rgba(0, 0, 0, 0);
                    padding: 10px;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0, 0, 0, 0);
                    z-index: 1000;
                    font-size: 22px;
                }}
                </style>
                <div class="sidebar-watched-count">
                    <strong>Movies Watched: {st.session_state.watched_count}</strong>
                </div>
                """,
                unsafe_allow_html=True
            )
              
        else:
            # Show initial message when no filters applied
            st.info("Apply filters above to see movie details")
    else:
        if show_list:
            st.write("No movies match your search criteria.")
        else:
            st.info("Apply filters above to see movie details")
with tab2:
    st.title("Movies Watched")
    st.write(f"Number of movies watched: {st.session_state.watched_count}")
    for idx, movie in enumerate(st.session_state.watched_list, start=1):
        st.write(f"{idx}. {movie}")
        
