import spotipy
import sys
import spotipy.oauth2 as oauth2

# Function for getting artist image URL
def getArtistImage(artist_name):
    from klap4.config import config

    CLIENT_ID = config.config()['spotifyClient']
    CLIENT_SECRET = config.config()['spotifySecret']

    try:

        credentials = oauth2.SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        token = credentials.get_access_token(as_dict=False)

        if token:
            sp = spotipy.Spotify(auth=token)
            if len(sys.argv) > 1:
                name = ' '.join(sys.argv[1:])
            else:
                name = artist_name

            results = sp.search(q='artist:' + name, type='artist')
            items = results['artists']['items']
            if len(items) > 0:
                artist = items[0]
                print(artist['name'], artist['images'][0]['url'])
                return artist['images'][0]['url']
            else:
                return None
    except:
        return None

# Function for getting related artists (for a given artist)
def getRelatedArtists(artist_name):
    from klap4.config import config

    CLIENT_ID = config.config()['spotifyClient']
    CLIENT_SECRET = config.config()['spotifySecret']

    try:

        credentials = oauth2.SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        token = credentials.get_access_token(as_dict=False)

        if token:
            sp = spotipy.Spotify(auth=token)
            results = sp.search(q='artist:' + artist_name, type="artist")
            items = results['artists']['items']
            
            if len(items) > 0:
                artist = items[0]
                id = artist['id']
                artists = sp.artist_related_artists(id)
                return artists
    except:    
        return None


# Function for getting album image
def getAlbumCover(album_name, artist_name):
    from klap4.config import config

    CLIENT_ID = config.config()['spotifyClient']
    CLIENT_SECRET = config.config()['spotifySecret']

    try:

        credentials = oauth2.SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        token = credentials.get_access_token(as_dict=False)

        if token:
            sp = spotipy.Spotify(auth=token)

            query = 'album:{0} artist:{1}'.format(album_name, artist_name)
            results = sp.search(q=query, type='album')
            items = results['albums']['items']
            
            if len(items) > 0:
                album = items[0]
                img = album['images'][0]['url']
                return img
    except:
        return None