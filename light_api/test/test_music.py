# Test file

from light_api import with_light
from light_api.music import LightMusic


@with_light
def main(light):
    light_music = LightMusic(light)
    tracks = light_music.get_tracks()

    for track in tracks:
        print(f"{track.artist} - {track.album} - {track.title}")


if __name__ == "__main__":
    main()
