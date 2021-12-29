from spotify import MySpotify

ms = MySpotify()

#ms.create_all(omit=["Trauma 8","Sleep"])

id = ms.get_playlist_by_name("all")

data = ms.song_data(id)

data.to_csv("data.csv")
