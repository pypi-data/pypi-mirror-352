import time
from phiona import (
    get_refresh_token,
    get_new_access_token,
    get_file_status,
    generate_playlist_raw,
    generate_playlist_from_songs,
    generate_playlist_presets,
    get_similar_songs,
    add_new_file,
)

# generate access and refresh token
username = 'testaccount2'
password = 'kRdw0ZsoajajvtN'
# refresh token lasts for 1 week
refresh_token = get_refresh_token(username, password)
print(refresh_token)
# access token lasts for 4 hours
access_token = get_new_access_token(refresh_token)
print('access')
print(access_token)

# feed the access token to the api call

start_time = time.time()
track_id = add_new_file(access_token, r"C:\Users\Carl\developer\web_product\web_product\test1.wav", 'test1', 'artist1', '', '', '')
process_time = time.time() - start_time
print(f"Process song time: {process_time:.2f} seconds")


start_time = time.time()
song_info = get_file_status(access_token)
status_time = time.time() - start_time
print(f"Get file status time: {status_time:.2f} seconds")

# get the file status but sorted
start_time = time.time()
song_info = get_file_status(access_token, sorting_mechanism=['-friendship_love', 'frustration'])
status_time = time.time() - start_time
print(f"Get file status time: {status_time:.2f} seconds")


# generate a playlist 
# single hybrid
targets1 = [
    {
        'genre': 'Dance Pop',
        'target_circumplex': [0.5, 0.3],
        'target_fingerprint': [0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89],
        'weighting': '100', 
        'avg_date': '2018-12-12',
    },
]
# multi hybrid
targets2 = [
    {
        'genre': 'Dance Pop',
        'target_circumplex': [0.5, 0.3],
        'target_fingerprint': [0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89],
        'weighting': '60', 
        'avg_date': '2018-12-12',
    },
    {
        'genre': 'House',
        'target_circumplex': [0.5, 0.3],
        'target_fingerprint': [0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89],
        'weighting': '40', 
        'avg_date': '2022-12-12',
    },
]

start_time = time.time()
playlist_info = generate_playlist_raw(access_token, targets2)
status_time = time.time() - start_time
print(f"Get playlist status time: {status_time:.2f} seconds")

start_time = time.time()
playlist_info = generate_playlist_presets(access_token, 'fitness-pop')
status_time = time.time() - start_time
print(f"Get playlist status time: {status_time:.2f} seconds")

song_ids = [53, 54, 55, 56, 57]

start_time = time.time()
playlist_info = generate_playlist_from_songs(access_token, song_ids)
status_time = time.time() - start_time
print(f"Get playlist status time: {status_time:.2f} seconds")


song_ids = [56]

start_time = time.time()
playlist_info = generate_playlist_from_songs(access_token, song_ids)
status_time = time.time() - start_time
print(f"Get playlist status time: {status_time:.2f} seconds")


song_id = 56

start_time = time.time()
playlist_info = get_similar_songs(access_token, song_id)
status_time = time.time() - start_time
print(f"Get playlist status time: {status_time:.2f} seconds")
