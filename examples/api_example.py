from light_api import with_light
from light_api.client import Light
from light_api.music import LightTrack
from light_api.notes import LightNote
from light_api.podcast import LightPodcast
from light_api.tools import LightTool


@with_light
def music(light: Light):
    lm = light.music
    tracks: list[LightTrack] = lm.get_tracks()

    print("\nAll tracks:")
    for t in tracks:
        print(f"{t.artist} - {t.album} - {t.title} - {t.audio_id}")


@with_light
def notes(light: Light):
    ln = light.notes
    notes: list[LightNote] = ln.get_notes()

    print("\nAll notes:")
    for n in notes:
        print(f"{n.title}")


@with_light
def podcasts(light: Light):
    lp = light.podcast
    podcasts: list[LightPodcast] = lp.get_podcasts()

    print("\nSubscribed to:")
    for p in podcasts:
        print(f"{p.title} - {p.rss_feed_url}")


@with_light
def tools(light: Light):
    lt = light.tools
    tools: list[LightTool] = lt.get_tools()

    print("\nInstalled tools:")
    for t in tools:
        print(f"{t.title}")


if __name__ == "__main__":
    music()
    notes()
    podcasts()
    tools()
