from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from globals import *
from requests import get, post, delete
from pandas import DataFrame
import json
import numpy as np

class MySpotify:
	def __init__(self):
		#super().__init__()
		scopes = ' '.join(['ugc-image-upload',
			'user-read-playback-state',
			'user-modify-playback-state',
			'user-read-currently-playing',
			'user-read-private',
			'user-read-email',
			'user-follow-modify',
			'user-follow-read',
			'user-library-modify',
			'user-library-read',
			'app-remote-control',
			'user-read-playback-position',
			'user-top-read',
			'user-read-recently-played',
			'playlist-modify-private',
			'playlist-read-collaborative',
			'playlist-read-private',
			'playlist-modify-public'])

		#sp = Spotify(auth_manager=SpotifyOAuth(username=user_id,client_id=client_id,client_secret=client_secret,redirect_uri=redirect_uri,scope=scopes))
		auth_manager=SpotifyOAuth(username=user_id,client_id=client_id,client_secret=client_secret,redirect_uri=redirect_uri,scope=scopes)
		token = auth_manager.get_access_token(as_dict=False)
		self.headers = {"Accept": "application/json",
				"Content-Type": "application/json",
				"Authorization": f"Bearer {token}"}
		self.params = {"market":"ES"}


	def get_track(self,id):
		"""
		id: song id
		name: song name
		artists: list of artist ids
		album: album id
		release date: YYYY-MM-DD
		explicit: boolean
		popularity: 0-100 based on # times played and recency
		duration_ms: length of song in ms

		features
		========
		all below categories range from 0.0 to 1.0 unless otherwise stated.

		acousticness: how acoustic a song is
		danceability: how suitable a track is for dancing
		energy: high energy is fast loud and noisy
		instrumentalness: high value implies no vocals
		key: 0=C, 1=C#, 2=D, ..., 11=B
		liveness: detects audience in the recording
		loudness: average loudness of track ranging -60 to 0 db
		mode: major key is represented as 1, minor 0
		speechiness: detects presence of spoken words in a track
		tempo: measured in BPM
		time_signature: range is from 3 to 7 namely "3/4" to "7/4"
		valence: high value is happy, cheerful, euphoric
			 low value is sad, depressed, angry
		"""
		song = {"id":id}

		track_info = get(url=f"https://api.spotify.com/v1/tracks/{id}",
			headers = self.headers,
			params = self.params).json()

		try:
			song["name"] = track_info["name"]
		except:
			song["name"] = None

		try:
			song["artists"] = [artist["id"] for artist in track_info["artists"]]
		except:
			song["artists"] = None

		try:
			song["album"] = track_info["album"]["id"]
		except:
			song["album"] = None

		try:
			song["release_date"] = track_info["album"]["release_date"]
		except:
			song["release_date"] = None

		try:
			song["explicit"] = track_info["explicit"]
		except:
			song["explicit"] = None

		try:
			song["popularity"] = track_info["popularity"]
		except:
			song["popularity"] = None

		audio_features = ["danceability","energy","key","loudness",
				"mode","speechiness","acousticness",
				"instrumentalness","liveness","valence",
				"tempo","time_signature","duration_ms"]

		track_info = get(url = f"https://api.spotify.com/v1/audio-features/{id}",
			headers = self.headers).json()

		for feature in audio_features:
			try:
				song[feature] = track_info[feature]
			except:
				song[feature] = None

		return song

	def get_album(self,id):
		"""
		id: album id
		name: name of album
		artists: list of artist ids
		tracks: list of track ids
		release_date: release date
		"""
		result = get(url=f"https://api.spotify.com/v1/albums/{id}",
			headers = self.headers,
			params = self.params).json()
		album = {"id": id}
		album["name"] = result["name"]
		album["artists"] = [artist["id"] for artist in result["artists"]]
		album["tracks"] = [track["id"] for track in result["tracks"]["items"]]

		return album

	def get_artist(self,id):
		"""
		id: artist id
		name: name of artist
		followers: number of followers
		genres: list of genres, none if not classified
		popularity: 0-100
		albums: list of all album ids
		tracks: list of top 10 track ids
		"""
		result = get(url=f"https://api.spotify.com/v1/artists/{id}",
			headers = self.headers,
			params = self.params).json()

		artist = {"id": id}
		artist["name"] = result["name"]
		artist["followers"] = result["followers"]["total"]
		artist["genres"] = result["genres"]
		artist["popularity"] = result["popularity"]

		result = get(url=f"https://api.spotify.com/v1/artists/{id}/albums",
			headers = self.headers,
			params = self.params).json()

		artist["albums"] = [album["id"] for album in result["items"]]

		result = get(url=f"https://api.spotify.com/v1/artists/{id}/top-tracks",
			headers = self.headers,
			params = self.params).json()

		artist["tracks"] = [track["id"] for track in result["tracks"]]

		return artist

	def get_liked_songs(self):
		params = self.params
		params["limit"] = 50
		params["offset"] = 0
		liked_songs = []
		while True:
			result = get(url="https://api.spotify.com/v1/me/tracks",
				headers = self.headers,
				params = params).json()

			params["offset"] += 50

			tracks = [track["track"]["id"] for track in result["items"]]
			if tracks == []:
				break
			liked_songs += tracks

		return liked_songs

	def get_recommendation(self,**kwargs):
		"""
		seed_artists: artist ids comma separated, max 5
		seed_genres: genres comma separated, max 5
		seed_tracks: track ids comma separated, max 5
		limit: number of returned songs

		features:
		=========
		*all features below have a min_,max_,and target_ argument

		acousticness: float
		danceability: float
		energy: float
		instrumentalness: float
		key: int 0-11
		liveness: float
		loudness: float
		mode: int 0-1
		popularity: int 0-100
		speechiness: float
		tempo: float
		time_signature: int 3-7
		valence: float
		"""

		params = self.params
		for key,value in kwargs.items():
			params[key] = value

		result = get(url="https://api.spotify.com/v1/recommendations",
			headers = self.headers,
			params = params).json()

		tracks = [track["id"] for track in result["tracks"]]

		return tracks

	def get_playlists(self,limit=50):
		params = self.params
		params["limit"] = limit
		result = get(url="https://api.spotify.com/v1/me/playlists",
			headers = self.headers,
			params = params).json()

		playlists = [{"id":playlist["id"],"name":playlist["name"]} for playlist in result["items"]]

		return playlists

	def get_playlist_tracks(self,id):
		params = {"limit":100,"offset":0}
		all_tracks = []
		while True:
			result = get(url=f"https://api.spotify.com/v1/playlists/{id}/tracks",
				headers = self.headers,
				params = params).json()

			tracks = [track["track"]["id"] for track in result["items"]]

			if tracks == []:
				break

			all_tracks += tracks

			params["offset"] += 100

		return all_tracks

	def get_playlist_by_name(self,name):
		playlists = self.get_playlists()
		for playlist in playlists:
			if playlist["name"] == name:
				return playlist["id"]
		return False

	def create_playlist(self,name,description="",public=False):
		id = self.get_playlist_by_name(name)
		if id:
			return id

		request_body = json.dumps({
		          "name": name,
		          "description": description,
		          "public": public
		        })
		post(url=f"https://api.spotify.com/v1/users/{user_id}/playlists",
				headers = self.headers,
				data = request_body)

		return self.get_playlist_by_name(name)

	def add_to_playlist(self,id,tracks):
		"""
		id: playlist id
		tracks: list of track ids
		"""
		for i in range(0,len(tracks),50):
			uris = ','.join(["spotify:track:"+track for track in tracks[i:i+50]])

			result = post(url=f"https://api.spotify.com/v1/playlists/{id}/tracks",
				headers = self.headers,
				params = {"uris":uris}).json()


	def del_from_playlist(self,id,tracks):
		"""
		id: playlist id
		tracks: list of track ids
		"""
		for i in range(0,len(tracks),100):

			uris = [{"uri":"spotify:track:"+track} for track in tracks[i:i+100]]

			request_body = json.dumps({
				"tracks": uris
				})
			delete(url=f"https://api.spotify.com/v1/playlists/{id}/tracks",
				headers = self.headers,
				data = request_body)

	def create_all(self,omit=[]):
		"""
		creates "all" playlist
		"""
		omit.append("all")
		# create playlist
		id = self.create_playlist("all")

		# clear playlist
		tracks = self.get_playlist_tracks(id)
		self.del_from_playlist(id,tracks)

		# add songs to playlist
		playlists = self.get_playlists()

		tracks = self.get_liked_songs()
		for playlist in playlists:
			if playlist["name"] in omit:
				continue
			tracks += self.get_playlist_tracks(playlist["id"])

		tracks = list(np.unique(tracks))
		self.add_to_playlist(id,tracks)


	def song_data(self,id):
		tracks = []
		for track in self.get_playlist_tracks(id):
			tracks.append(self.get_track(track))
		return DataFrame(tracks)
