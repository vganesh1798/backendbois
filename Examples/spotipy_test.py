import spotipy
import sys
import spotipy.oauth2 as oauth2
import spotipy.util as util

# Function for getting artist image URL
def getArtistImage(artist_name, sp):

    if len(artist_name) > 1:
        name = ' '.join(sys.argv[1:])
    else:
        name = artist_name
    
    results = sp.search(q='artist:' + name, type='artist')
    items = results['artists']['items']
    print("bbb", items)
    
    if len(items) > 0:
        artist = items[0]
        img = artist['images'][0]['url']
        print(img)
        return img
    
    #if no artist was found
    print("aaaa")
    return None

if __name__ == "__main__":
    from klap4.config import config

    CLIENT_ID = config.config()['spotifyClient']
    CLIENT_SECRET = config.config()['spotifySecret']
    REDIRECT_URI = "http://localhost"
    credentials = oauth2.SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    token = credentials.get_access_token(as_dict=False)

    if token:
        sp = spotipy.Spotify(auth=token)
        if len(sys.argv) > 1:
            name = ' '.join(sys.argv[1:])
        else:
            name = 'Poppy'

        results = sp.search(q='artist:' + name, type='artist')
        items = results['artists']['items']
        if len(items) > 0:
            artist = items[0]
            print(artist['name'], artist['images'][0]['url'])
