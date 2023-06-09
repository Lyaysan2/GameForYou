import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from pandas import DataFrame

from web.models import Game

matplotlib.use('agg')
import warnings

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

os_df = None
processor_df = None
graphics_df = None
directx_df = None

video_games_df = None
video_games_df_plots = None

vg_distances = None
vg_indices = None
vectorizer = None
game_names = None
video_games_df_recommend = None
game_title_vectors = None

tags_list = []


def init_video_game_model():
    prepare_static_txt_files()
    print('prepare_static_txt_files')

    mlb = MultiLabelBinarizer()
    global video_games_df

    video_games_df = DataFrame([o.__dict__ for o in Game.objects.all()]).drop(columns=['_state'], axis=1)

    video_games_df['tags'] = video_games_df['tags'].apply(lambda x: x.split(', '))
    get_tags_list(mlb)

    video_games_df.columns = video_games_df.columns.str.lower()
    video_games_df['release_date'] = video_games_df['release_date'].astype(str)
    video_games_df['release_date_month'] = video_games_df['release_date'].str[5:7]
    video_games_df['release_date_day'] = video_games_df['release_date'].str[8:10]
    video_games_df['release_date'] = video_games_df['release_date'].str[0:4]
    video_games_df['release_date'] = pd.to_numeric(video_games_df['release_date'], errors='coerce')
    video_games_df['release_date'].fillna('2022', inplace=True)
    video_games_df['release_date'].unique()
    video_games_df["release_date"] = pd.to_numeric(video_games_df["release_date"], errors='coerce')
    video_games_df["reviews"] = video_games_df["reviews"].replace(['1 user reviews',
                                                                   '2 user reviews',
                                                                   '3 user reviews',
                                                                   '4 user reviews',
                                                                   '5 user reviews',
                                                                   '6 user reviews',
                                                                   '7 user reviews',
                                                                   '8 user reviews',
                                                                   '9 user reviews', ], 'No user reviews')
    video_games_df["ram"] = pd.to_numeric(video_games_df["ram"], errors='coerce')
    video_games_df = video_games_df.dropna(subset=['ram'])
    steps = [8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384]
    steps = np.array(steps)
    video_games_df["ram"] = video_games_df["ram"].apply(lambda x: steps[np.argmin(np.abs(x - steps))])

    video_games_df = video_games_df.dropna(subset=['popularity'])
    video_games_df['popularity'] = video_games_df['popularity'].div(100)
    video_games_df['critics_score'] = video_games_df['critics_score'].fillna(
        video_games_df['critics_score'].mean() - 10)
    video_games_df['processor'] = video_games_df['processor'].fillna('AMDRyzen97950X3D')
    video_games_df['processor'] = video_games_df['processor'].apply(lambda x: x.split(','))
    video_games_df['developer'] = video_games_df['developer'].apply(lambda x: x.split(','))

    # mlb = MultiLabelBinarizer()
    video_games_df["os"] = video_games_df["os"].fillna('7')
    video_games_df["os"] = video_games_df["os"].astype(str).str.replace("Windows ", "")
    video_games_df["os"] = video_games_df["os"].astype(str).str.replace("Vista", "6")
    video_games_df["os"] = video_games_df["os"].astype(str).str.replace("XP", "5.2")
    video_games_df['os'] = video_games_df['os'].apply(lambda x: x.split(','))
    video_games_df['os'] = video_games_df['os'].apply(lambda x: [float(el) for el in x])
    video_games_df['os_min'] = video_games_df.os.apply(lambda x: min(x))
    video_games_df['os_max'] = video_games_df.os.apply(lambda x: max(x))

    video_games_df["directx"] = video_games_df["directx"].replace('90c', '9.0c')
    video_games_df["directx"] = video_games_df["directx"].replace('7', '7.0')
    video_games_df["directx"] = video_games_df["directx"].replace('8', '8.0')
    video_games_df["directx"] = video_games_df["directx"].replace('9', '9.0')
    video_games_df["directx"] = video_games_df["directx"].replace('10', '10.0')
    video_games_df["directx"] = video_games_df["directx"].replace('11', '11.0')
    video_games_df["directx"] = video_games_df["directx"].replace('12', '12.0')
    video_games_df["directx"] = video_games_df["directx"].fillna('10.0')

    video_games_df = video_games_df.dropna(subset=['storage'])
    video_games_df["storage"] = pd.to_numeric(video_games_df["storage"], errors='coerce')
    video_games_df['popularity'] = video_games_df['popularity'].fillna(video_games_df['popularity'].mean().round(0))

    video_games_df['graphics'] = video_games_df['graphics'].fillna('Nvidia RTX 4090')
    video_games_df["graphics"] = video_games_df['graphics'].apply(lambda x: x.split(','))

    global video_games_df_plots
    video_games_df_plots = video_games_df.copy()
    video_games_df_plots.rename(columns={'release_date': 'date'}, inplace=True)
    video_games_df = video_games_df.join(pd.DataFrame(mlb.fit_transform(video_games_df.pop("tags")),
                                                      columns=mlb.classes_,
                                                      index=video_games_df.index))

    label_encoder = LabelEncoder()

    video_games_df['reviews'] = label_encoder.fit_transform(video_games_df['reviews'].values)
    video_games_df = video_games_df.dropna(subset=['storage'])

    global video_games_df_recommend
    video_games_df_recommend = video_games_df.drop(
        columns=['processor', 'ram', 'price', 'release_date', 'graphics', 'critics_score', 'storage', 'os', 'os_min',
                 'os_max', 'developer', 'directx', 'release_date_month', 'release_date_day'], axis=1)
    video_games_df_dummy = pd.get_dummies(data=video_games_df_recommend, columns=['reviews'])

    features = video_games_df_dummy.drop(columns=['name', 'link'], axis=1)

    scale = StandardScaler()
    scaled_features = scale.fit_transform(features)
    scaled_features = pd.DataFrame(scaled_features, columns=features.columns)

    model = NearestNeighbors(n_neighbors=15, metric='cosine', algorithm='brute').fit(scaled_features)

    global vg_distances
    global vg_indices
    vg_distances, vg_indices = model.kneighbors(scaled_features)

    global game_names
    game_names = video_games_df['name'].drop_duplicates()
    game_names = game_names.reset_index(drop=True)

    global vectorizer
    vectorizer = TfidfVectorizer(use_idf=True).fit(game_names)

    video_games_df_recommend = video_games_df_recommend.reset_index()
    video_games_df_recommend = video_games_df_recommend.drop_duplicates(subset=['link'], keep='first')

    global game_title_vectors
    game_title_vectors = vectorizer.transform(game_names)
    print(vectorizer)


def recommend_game_title(video_game_name):
    '''
    This function will recommend a game title that has the closest match to the input
    '''
    query_vector = vectorizer.transform([video_game_name])
    similarity_scores = cosine_similarity(query_vector, game_title_vectors)

    closest_match_index = similarity_scores.argmax()
    closest_match_game_name = game_names[closest_match_index]

    return closest_match_game_name


def recommend_game(video_game_name):
    '''
    This function will provide game recommendations based on various features of the game
    '''
    video_game_idx = video_games_df_recommend.query("name == @video_game_name").index

    if video_game_idx.empty:
        # If the game entered by the user doesn't exist in the records, the program will recommend a new game similar to the input
        closest_match_game_name = recommend_game_title(video_game_name)

        print(f"'{video_game_name}' doesn't exist in the records.\n")
        print(f"You may want to try '{closest_match_game_name}', which is the closest match to the input.")

    else:
        # Place in a separate dataframe the indices and distances, then sort the record by distance in ascending order
        vg_combined_dist_idx_df = pd.DataFrame()
        for idx in video_game_idx:
            # Remove from the list any game that shares the same name as the input
            vg_dist_idx_df = pd.concat([pd.DataFrame(vg_indices[idx][1:]), pd.DataFrame(vg_distances[idx][1:])], axis=1)
            vg_combined_dist_idx_df = pd.concat([vg_combined_dist_idx_df, vg_dist_idx_df])

        vg_combined_dist_idx_df = vg_combined_dist_idx_df.set_axis(['index', 'distance'], axis=1)
        vg_combined_dist_idx_df = vg_combined_dist_idx_df.reset_index(drop=True)
        vg_combined_dist_idx_df = vg_combined_dist_idx_df.sort_values(by='distance', ascending=True)

        video_game_list = video_games_df_recommend.iloc[vg_combined_dist_idx_df['index']]

        # Remove any duplicate game names to provide the user with a diverse selection of recommended games
        video_game_list = video_game_list.drop_duplicates(subset=['name'], keep='first')

        # Get the first 10 games in the list
        video_game_list = video_game_list.head()

        # Get the distance of the games similar to the input
        recommended_distances = np.array(vg_combined_dist_idx_df['distance'].head())

        video_game_list = video_game_list.reset_index(drop=True)
        recommended_video_game_list = pd.concat([video_game_list,
                                                 pd.DataFrame(recommended_distances, columns=['Similarity_Distance'])],
                                                axis=1)
        return recommended_video_game_list


def get_less(df, column, value):
    df = df.reset_index()
    value_str_num = df[df[column] == value].index
    result = []
    for index, row in df.iterrows():
        if index >= value_str_num:
            result.append(row[column])
    return result


def compare(df, list_to_comp):
    result = []
    for index, row in df.items():
        result.append(all(value in row for value in list_to_comp))
    return result


def compare_pc(df, list_to_comp):
    result = []
    for index, row in df.items():
        result.append(any(value in row for value in list_to_comp))
    return result


def get_games_by_PC(os=0, processor=0, graphics=0, directx=0, ram=0):
    df_user_pc_filtered = video_games_df_plots.copy()
    filterarr = {'os': os, 'processor': processor, 'graphics': graphics, 'directx': directx, 'ram': ram}
    for key, value in filterarr.items():
        if value != 0:
            if key != 'ram':
                try:
                    values_list = get_less(globals()[f'{key}_df'], key, value)
                    mask = compare_pc(df_user_pc_filtered[key].astype(str), np.array(values_list).astype(str))
                    df_user_pc_filtered = df_user_pc_filtered[mask]
                except KeyError:
                    pass
            else:
                try:
                    df_user_pc_filtered = df_user_pc_filtered[df_user_pc_filtered[key] <= value]
                except KeyError:
                    pass
    return df_user_pc_filtered


def prepare_static_txt_files():
    global os_df, processor_df, graphics_df, directx_df

    os_df = pd.read_csv("txt_static_list/os.txt")
    processor_df = pd.read_csv("txt_static_list/processor.txt")
    graphics_df = pd.read_csv("txt_static_list/graphics.txt")
    directx_df = pd.read_csv("txt_static_list/directx.txt")

    os_df["os"] = os_df["os"].astype(str).str.replace("Windows ", "")
    os_df["os"] = os_df["os"].astype(str).str.replace("Vista", "6")
    os_df["os"] = os_df["os"].astype(str).str.replace("XP", "5.2")
    os_df["os"] = os_df["os"].astype(float).astype(str)

    os_df = os_df.drop_duplicates()
    processor_df = processor_df.drop_duplicates()
    graphics_df = graphics_df.drop_duplicates()
    directx_df = directx_df.drop_duplicates()


def plots_by_parameter():
    cut_bins = [0, 250, 500, 1000, 2000, 4000, 6000]
    df_price = pd.DataFrame()
    df_price['price'] = pd.cut(video_games_df_plots['price'], bins=cut_bins)
    df_price.price.explode().value_counts().plot(kind='pie', figsize=(6, 4), colors=plt.cm.Set2(np.arange(5)))
    plt.title("Data Distribution of Video Game prices")
    plt.savefig('media/plots/price_plot.png')

    video_games_df_plots['ram'] = video_games_df_plots['ram'].div(1024).round(1)
    features = video_games_df_plots[['date', 'ram']].columns
    for idx, feature in enumerate(features):
        plt.figure(figsize=(10, 8))
        sns.countplot(data=video_games_df_plots, x=feature)
        plt.ylabel('Frequency')
        plt.title("Data Distribution of Video Game " + feature + "s")
        plt.savefig(f"media/plots/{feature}_plot.png")

    plt.figure(figsize=(19, 8))
    sns.countplot(data=video_games_df_plots, x='reviews')
    plt.ylabel('Frequency')
    plt.title("Data Distribution of Video Game reviews")
    plt.savefig(f"media/plots/reviews_plot.png")

    video_games_df_plots.tags.explode().value_counts().head(30).plot(kind='bar', figsize=(10, 14),
                                                                     color=plt.cm.Set2(np.arange(5)))
    plt.title("Data Distribution of Video Game tags")
    plt.savefig('media/plots/tags_plot.png')

    video_games_df_plots.os.explode().value_counts().head(30).plot(kind='bar', figsize=(10, 8),
                                                                   color=plt.cm.Set2(np.arange(5)))
    plt.title("Data Distribution of Video Game os")
    plt.savefig('media/plots/os_plot.png')


def get_filtered_games(price_asc=None, date_asc=None, popularity_asc=None, tags=[]):
    df_filtered = video_games_df_plots.copy()
    filterarr = {'price': price_asc, 'date': date_asc, 'popularity': popularity_asc, 'tags': tags}
    for key, value in filterarr.items():
        if key != 'tags' and key != 'date' and value is not None:
            df_filtered.sort_values(by=key, ascending=value, inplace=True)
        elif key == 'date' and value is not None:
            df_filtered.sort_values(by=[key, 'release_date_month', 'release_date_day'], ascending=value, inplace=True)
        elif key == 'tags':
            if len(tags) != 0:
                mask = compare(df_filtered[key].astype(str), tags)
                df_filtered = df_filtered[mask]
    return df_filtered


def get_tags_list(mlb):
    video_games_df_copy = video_games_df.copy()
    global tags_list
    tags_list = pd.DataFrame(mlb.fit_transform(video_games_df_copy.pop("tags")),
                             columns=mlb.classes_).columns


def get_tags_list_choices():
    choice_tags_list = []
    for tag in tags_list:
        choice_tags_list.append((tag, tag))
    return choice_tags_list
