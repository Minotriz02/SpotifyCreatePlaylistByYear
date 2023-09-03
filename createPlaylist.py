import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime

# Configura las credenciales de tu aplicación
SPOTIPY_CLIENT_ID = 'XXXXX'
SPOTIPY_CLIENT_SECRET = 'XXXXX'
SPOTIPY_REDIRECT_URI = 'XXXXXX'  # Debe coincidir con la configuración de tu aplicación

# Inicializa la instancia de Spotipy con OAuth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope="playlist-read-private playlist-modify-private user-library-read"))

# Obtiene todas las canciones guardadas
def get_all_saved_tracks():
    all_saved_tracks = []
    limit = 20  # Este es el máximo permitido por Spotify
    results = sp.current_user_saved_tracks(limit=limit)
    all_saved_tracks.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        all_saved_tracks.extend(results['items'])
    return all_saved_tracks

# Obtiene el año en el que se añadió la canción
def get_year_added(added_at):
    added_at = datetime.strptime(added_at, "%Y-%m-%dT%H:%M:%SZ")
    return added_at.year

#Agrupar las canciones
saved_tracks = get_all_saved_tracks()
# Obtén todas las playlists del usuario
user_playlists = sp.current_user_playlists()
tracks_by_year = {}
for item in saved_tracks:
    track = item['track']
    year = get_year_added(item['added_at'])
    if year not in tracks_by_year:
        tracks_by_year[year] = []
    tracks_by_year[year].append(track)

# Crea una playlist por cada año y agrega las canciones correspondientes
for year, tracks in tracks_by_year.items():
    # Crea una nueva playlist
    playlist_name = f"Canciones Añadidas en {year}"
    playlist_description = f"Canciones añadidas en {year}"

     # Verifica si la playlist ya existe
    playlist_exists = any(playlist['name'] == playlist_name for playlist in user_playlists['items'])

    if not playlist_exists:
        # Crea una nueva playlist si no existe
        playlist = sp.user_playlist_create(sp.current_user()['id'], playlist_name, public=False, description=playlist_description)

        # Obtiene los URI de las canciones
        track_uris = [track['uri'] for track in tracks]

        # Divide las canciones en lotes de 100 (límite de Spotify por solicitud)
        batch_size = 100
        for i in range(0, len(track_uris), batch_size):
            batch = track_uris[i:i + batch_size]
            sp.playlist_add_items(playlist['id'], batch)

        print(f"Playlist '{playlist_name}' creada con éxito con {len(tracks)} canciones.")
    else:
        print(f"La playlist '{playlist_name}' ya existe. No se ha creado una nueva.")


# # En caso de tener que borrar playlist
# # Obtiene la lista de playlists del usuario actual
# playlists = sp.current_user_playlists(limit=50)

# # Borra las playlist que inicien con Mis favoritas
# for index, playlist in enumerate(playlists['items']):
#     if playlist['name'].startswith('Mis Favoritas'):
#         sp.current_user_unfollow_playlist(playlist['id'])
#         print(f"La playlist '{playlist['name']}' ha sido eliminada.")
