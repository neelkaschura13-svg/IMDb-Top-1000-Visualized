import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# Importing Dataframes
##df
base_url = "https://docs.google.com/spreadsheets/d/"
url_id = "1omsl7c0QmuYyJ4uoKtuX_LfowAOwioUpO69B-uhCsTc/"
export = "export/format=excel"
whole_url = base_url + url_id + export
##df2
base_url2 = "https://docs.google.com/spreadsheets/d/"
url_id2 = "1PrK_WYNta_6f18WxnsjPVlEQdYCytL2yAv2EKQDTzQg/"
export2 = "export/format=excel"
whole_url2 = base_url2 + url_id2 + export2



#Caching
## Loading data with caching for df
@st.cache_data()
def load_data():
    try:
        df = pd.read_excel(whole_url, na_values="None")
        return df
    except Exception as e:
        st.error(f"An error occurred while loading data: {e}")
        return pd.DataFrame()

## Loading data with caching for df2
@st.cache_data()
def load_data2():
    try:
        import requests
        response = requests.get(whole_url2)
        response.raise_for_status() 
        df2 = pd.read_excel(response.content, na_values="None")
        return df2
    except Exception as e:
        st.error(f"An error occurred while loading df2: {e}")
        return pd.DataFrame()


        
#Loading Dataframes
## Load dfs and store them in session state
if 'data' not in st.session_state:
    st.session_state.data = load_data()
if 'data2' not in st.session_state:
    st.session_state.data2 = load_data2()
    
df = st.session_state.data.copy()
df2 = st.session_state.data2.copy()

##load watched list 
if 'watched_list' not in st.session_state:
    st.session_state.watched_list = []
if 'watched_count' not in st.session_state:
    st.session_state.watched_count = 0

if 'watched_list2' not in st.session_state:
    st.session_state.watched_list2 = []
if 'watched_count2' not in st.session_state:
    st.session_state.watched_count2 = 0



#Increasing/Decreasing resolution of movie posters for both dataframes
def enhance_poster_url(poster_url):
    """
    Increase resolution of Amazon movie poster URLs using specific dimensions
    """
    if not poster_url or not poster_url.startswith('https://m.media-amazon.com/images/'):
        return poster_url
    enhanced_url = poster_url.replace('_V1_UX67_CR0,0,67,98_AL_', '_V1_UX200_CR0,0,200,300_AL_')
    return enhanced_url

def reduce_poster_url(image_url):
    """
    Reduce resolution of Amazon movie poster URLs using specific dimensions
    """
    if not image_url or not image_url.startswith('https://m.media-amazon.com/images/'):
        return image_url
    reduced_url = image_url.replace('_V1_FMjpg_UX1000_', '_V1_UX200_CR0,0,200,300_AL_')
    return reduced_url


    
#Cleaning cast list for dataframe 2    
df2['cast_clean'] = (
    df2['cast']
    .str.replace("'", "", regex=True)
    .str.replace(r"$\s*", "", regex=True)
    .str.replace(r"\s*$", "", regex=True)
    .str.replace(r",\s*", ", ", regex=True)
    .str.strip("[]")   
    .str.strip()
)
#ignores missing values in df2 for votes
def safe_votes(value, placeholder="–"):
    return placeholder if pd.isna(value) else f"{int(value):,}"



# Page layout
st.set_page_config(layout="wide")

## Homepage title and summary
st.markdown("<h1 style='font-size: 69px;'>Film List: IMDb & Netflix</h1>", unsafe_allow_html=True)
st.markdown("""
This app showcases IMDb's Top 1000 Movies as of 2020 and a catalog of 7000 movies, TV shows and specials from Netflix. It features an interactive movie catalog with multiple filters to sort by genre, director, and cast presented by a spreadsheet and list with movie posters. Additionally, the app allows you to track the movies you watched. It also has a visualization section where you can select filters to generate graphs, providing a way to analyze and discover top-rated films.
""")

# Tabs
tab1, tab2, tab3 = st.tabs(["Imdb Top 1000", "Netflix TV Shows and Movies", "Watched Movies and Shows"])

with tab1:
    #Search
    search_query = st.text_input("", placeholder="Search Movies by Title, Director, Genre, or Actor").strip() 
    # Initialize with empty dataframe
    filtered_df = pd.DataFrame()
    #case and space sensetivity 
    if search_query.strip():
        filtered_df = df[
            df['Series_Title'].str.contains(search_query, case=False, na=False) |
            df['Director'].str.contains(search_query, case=False, na=False) |
            df['Star1'].str.contains(search_query, case=False, na=False) |
            df['Star2'].str.contains(search_query, case=False, na=False) |
            df['Star3'].str.contains(search_query, case=False, na=False) |
            df['Star4'].str.contains(search_query, case=False, na=False) |
            df['Genre'].str.contains(search_query, case=False, na=False)
        ]

    # Display results of df1 
    if search_query.strip():
        st.subheader(f"Showing {len(filtered_df)} movies")

        if len(filtered_df) > 0:
            st.subheader("Movie Details")
            for idx, movie in filtered_df.iterrows():
                rank = idx + 1
                col1, col2, col3 = st.columns([1, 4, 1])

                with col1:
                    if pd.notna(movie['Poster_Link']) and movie['Poster_Link'] != '':
                        st.image(enhance_poster_url(movie['Poster_Link']), width=210)

                with col2:
                    st.markdown(f"<h2 style='font-size: 24px; margin-top: 0px;'>{rank}. {movie['Series_Title']} ({int(movie['Released_Year'])})</h2>", unsafe_allow_html=True)
                    st.markdown(f"*Director:* {movie['Director']}")
                    st.markdown(f"*Rating:* {movie['IMDB_Rating']}")
                    st.markdown(f"*Genre:* {movie['Genre']}")
                    st.markdown(f"*Runtime:* {movie['Runtime']}*min*")
                    st.markdown(f"*Overview:* {movie['Overview']}")
                    st.markdown(f"*Actors:* {movie['Star1']}, {movie['Star2']}, {movie['Star3']}, {movie['Star4']}")
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

        else:
            st.write("No movies match your search criteria. Try searching by movie title, director, genre, or lead actor.")

with tab2:
    search_query2 = st.text_input("", placeholder="Search Movies TV Shows by Title, Language, Genre or by Actor")
    filtered_df2 = pd.DataFrame()
    if search_query2.strip():
        try:
            filtered_df2 = df2[
                df2['title'].str.contains(search_query2, case=False, na=False) |
                df2['language'].str.contains(search_query2, case=False, na=False) |
                df2['cast'].str.contains(search_query2, case=False, na=False) |
                df2['genres'].str.contains(search_query2, case=False, na=False)
            ]
        except KeyError as e:
            st.error(f"Column not found: {e}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        filtered_df2 = df2.copy()

    # Display results df2 + logic for showing end years
    if search_query2.strip():
        st.subheader(f"Showing {len(filtered_df2)} movies and TV shows")

        if len(filtered_df2) > 0:
            st.subheader("Movie and TV Show Details")
            for idx, movie in filtered_df2.iterrows():
                col1, col2, col3 = st.columns([1, 4, 1])

                with col1:
                    if pd.notna(movie['image_url']) and movie['image_url'] != '':
                        st.image(reduce_poster_url(movie['image_url']), width=210)

                with col2:
                    #def empty votes 
                    def safe_int(value, default="?"):
                        return int(value) if pd.notna(value) else default
                    
                    start_year = safe_int(movie['startYear'])
                    
                    # checks if a movie
                    if movie['type'] == 'movie':
                        years_text = f"({start_year})"
                    # if not movie:
                    elif movie['type'] in ['tvSeries', 'tvMiniSeries']:
                        if pd.isna(movie['endYear']):
                            #if series still running
                            years_text = f"({start_year}) – (Present (as of 2021))"
                        else:
                            # Series ended
                            end_year = safe_int(movie['endYear'])
                            years_text = f"({start_year}) – ({end_year})"
                    else:
                        # safety incase unknown
                        years_text = f"({start_year})"

                    
                    #finally display results
                    st.markdown(
                        f"<h2 style='font-size: 24px; margin-top: 0px;'>{movie['title']} {years_text}</h2>",
                        unsafe_allow_html=True
                    )
                    st.markdown(f"*Rating:* {movie['rating']}")
                    st.markdown(f"*Genre:* {movie['genres']}")
                    st.markdown(f"*Language:* {movie['language']}")
                    st.markdown(f"*Overview:* {movie['plot']}")
                    st.markdown(f"*Actors:* {movie['cast_clean']}")
                    st.markdown(f"*Country:* {movie['orign_country']}")
                    st.markdown(f"<span style='font-family: monospace;'>*Votes:* {safe_votes(movie['numVotes'])}</span>",unsafe_allow_html=True)

                with col3:
                    if st.checkbox(f"Did you watch this movie?", key=f"watched_{idx}", value=(movie['title'] in st.session_state.watched_list2)):
                        if movie['title'] not in st.session_state.watched_list2:
                            st.session_state.watched_list2.append(movie['title'])
                            st.session_state.watched_count2 += 1
                    else:
                        if movie['title'] in st.session_state.watched_list2:
                            st.session_state.watched_list2.remove(movie['title'])
                            st.session_state.watched_count2 -= 1
                            
                st.markdown("---")
        else:
            st.write("No movies match your search criteria. Try searching by movie title, director, genre, or lead actor.")

with tab3: 
    st.title("All Movies Watched (Combined)")

    # combine both lists
    combined_watched = st.session_state.watched_list + st.session_state.watched_list2

    # remove duplicates incase
    unique_combined = list(set(combined_watched))

    # sort alphabetically 
    unique_combined.sort()

    # Display list
    if unique_combined:
        st.write(f"Total unique movies watched: {len(unique_combined)}")
        for idx, movie in enumerate(unique_combined, start=1):
            st.write(f"{idx}. {movie}")
    else:
        st.write("No movies have been marked as watched yet.")
