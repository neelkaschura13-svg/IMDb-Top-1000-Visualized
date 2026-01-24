import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#Importing Dataframe
base_url = "https://docs.google.com/spreadsheets/d/"
url_id = "1omsl7c0QmuYyJ4uoKtuX_LfowAOwioUpO69B-uhCsTc/"
export = "export/format=excel"
whole_url = base_url + url_id + export


# Function to load data with caching
@st.cache_data()
def load_data():
    try:
        df = pd.read_excel(whole_url, na_values="None")
        return df
    except Exception as e:
        st.error(f"An error occurred while loading data: {e}")
        return pd.DataFrame()

if 'data' not in st.session_state:
    st.session_state.data = load_data()

df = st.session_state.data.copy()


st.set_page_config(layout="wide")
#Homepage title 
st.title("IMDb Top 1000 Movies")
st.markdown("""
This app showcases IMDb's Top 1000 Movies as of 2020. It features an interactive movie catalog with multiple filiters to sort by genre, director, and cast presented by a spreadsheet and list with movie posters. Additionally, the app includes a visualization section where you can select filters to generate graphs, providing a way to analyze and discover top-rated films.
""")

#Increase resolution of movie posters
def enhance_poster_url(poster_url):
    """
    Increase resolution of Amazon movie poster URLs using specific dimensions
    """
    if not poster_url or not poster_url.startswith('https://m.media-amazon.com/images/'):
        return poster_url
    
    enhanced_url = poster_url.replace('_V1_UX67_CR0,0,67,98_AL_', '_V1_SY1000_')
    
    return enhanced_url


#Search Bar 
st.markdown("<h2 style='font-size: 28px;'>IMDb Top 1000 Movies - Advanced Search</h2>", unsafe_allow_html=True)

search_query = st.text_input("Search Movies by Title, Director, Genre, or Actor", "")

# Initialize with empty dataframe
filtered_df = pd.DataFrame()

if search_query.strip():  #Strips spaces
    filtered_df = df[
        df['Series_Title'].str.contains(search_query, case=False, na=False) |
        df['Director'].str.contains(search_query, case=False, na=False) |
        df['Star1'].str.contains(search_query, case=False, na=False) |
        df['Star2'].str.contains(search_query, case=False, na=False) |
        df['Star3'].str.contains(search_query, case=False, na=False) |
        df['Star4'].str.contains(search_query, case=False, na=False) |
        df['Genre'].str.contains(search_query, case=False, na=False)
    ]

# Display results
if search_query.strip():
    st.subheader(f"Showing {len(filtered_df)} movies")
    
    if len(filtered_df) > 0:
        st.subheader("Movie Details")
        for idx, movie in filtered_df.iterrows():
            rank = idx + 1
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if pd.notna(movie['Poster_Link']) and movie['Poster_Link'] != '':
                    st.image(enhance_poster_url(movie['Poster_Link']), width=210)
            
            with col2:
                st.markdown(f"<h2 style='font-size: 24px; margin-top: 0px;'>{rank}. {movie['Series_Title']} ({int(movie['Released_Year'])})</h2>", unsafe_allow_html=True)
                st.markdown(f"*Rating:* {movie['IMDB_Rating']}")
                st.markdown(f"*Genre:* {movie['Genre']}")
                st.markdown(f"*Director:* {movie['Director']}")
                st.markdown(f"*Overview:* {movie['Overview']}")
                st.markdown(f"*Actors:* {movie['Star1']}, {movie['Star2']}, {movie['Star3']}, {movie['Star4']}")
                st.markdown(f"*Votes:* {int(movie['No_of_Votes'])}")
            st.markdown("---")
    else:
        st.write("No movies match your search criteria. Try searching by movie title, director, genre, or lead actor.")
else:
    st.write("Enter a search term above to find movies.")



