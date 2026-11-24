"""HA Intercom - domofon i gry na Tablecie 2 (MT8768E, Android 12).

Ekran domofonu: przycisk "Przytrzymaj i mów" (do 30 s, licznik w dół) i odtwarzanie
przychodzących wiadomości po zapowiedzi "Nowa wiadomość głosowa". Menu po prawej:
słuchawka - domofon, pad - gry (kółko i krzyżyk, warcaby, szachy, kostka, rysowanie),
także przez sieć z innymi tabletami.

Kod domofonu jest wspólny z kioskiem (kiosk/voice.py, kiosk/widgets/voice_dialog.py),
a gry z Kioskiem dzieci (dzieci/games) - kopiowane przed budowaniem przez sync_kiosk.sh.
Ustawienia: settings.json (url, token HA, tablet_name) wbudowany w APK.
"""
import json
import os
from pathlib import Path

IS_ANDROID = "ANDROID_ARGUMENT" in os.environ or "ANDROID_PRIVATE" in os.environ
os.environ.setdefault("KIVY_NO_ARGS", "1")
if IS_ANDROID:
    # układ w pikselach jak w kiosku - bez skalowania DPI
    os.environ.setdefault("KIVY_METRICS_DENSITY", "1")
    os.environ.setdefault("KIVY_METRICS_FONTSCALE", "1")

from kivy.config import Config  # noqa: E402

if IS_ANDROID:
    # SDL zamienia dotyk także na zdarzenie myszy - bez dostawcy myszy (podwójne dotknięcia)
    if Config.has_section("input"):
        for key in list(Config.options("input")):
            if Config.get("input", key).startswith("mouse"):
                Config.remove_option("input", key)
else:
    Config.set("graphics", "width", "1280")
    Config.set("graphics", "height", "800")
# Esc nie zamyka aplikacji na PC; przyciski tabletu obsługuje GamesHost (systemowo tylko na
# ekranie domofonu)
Config.set("kivy", "exit_on_escape", "0")

from kivy.app import App  # noqa: E402
from kivy.core.window import Window  # noqa: E402
from kivy.factory import Factory  # noqa: E402
from kivy.lang import Builder  # noqa: E402
from kivy.properties import BooleanProperty, NumericProperty, StringProperty  # noqa: E402
from kivy.uix.boxlayout import BoxLayout  # noqa: E402
from kivy.uix.screenmanager import NoTransition  # noqa: E402

from dzieci.games import chess, checkers, dice, dots, football, paint, pdots, ships, snake, tetris, tictactoe  # noqa: E402,F401 - klasy gier dla gry.kv
from dzieci.games.host import GamesHost  # noqa: E402
from dzieci.music import MusicPlayer  # noqa: E402
from dzieci import coloring  # noqa: E402,F401 - klasy kolorowanek dla kolorowanki.kv
from kiosk import icons, voice  # noqa: E402
from kiosk.widgets.voice_dialog import TalkMixin  # noqa: E402

HERE = Path(__file__).resolve().parent
KV_DIR = HERE / "kiosk" / "kv"


class IntercomRoot(TalkMixin, BoxLayout):
    status = StringProperty("")
    remaining = NumericProperty(voice.MAX_SECONDS)
    recording = BooleanProperty(False)
    can_record = BooleanProperty(False)
    max_seconds = NumericProperty(voice.MAX_SECONDS)


class IntercomApp(GamesHost, App):
    title = "HA Intercom"
    tablet_name = StringProperty("Tablet 2")
    voice_last = StringProperty("")
    section = StringProperty("home")

    def build(self):
        Window.clearcolor = (0, 0, 0, 1)
        icons.register_font()
        # klasy z kiosku, gry, potem własny ekran (ekran_intercom.kv celowo nie nazywa się
        # intercom.kv - Kivy wczytałby go sam przed build(), zanim są klasy gier)
        for name in ("widgets.kv", "settings.kv", "voice_dialog.kv"):
            Builder.load_file(str(KV_DIR / name))
        Builder.load_file(str(HERE / "dzieci" / "games" / "gry.kv"))
        Builder.load_file(str(HERE / "dzieci" / "music" / "muzyka.kv"))
        Builder.load_file(str(HERE / "dzieci" / "coloring" / "kolorowanki.kv"))
        Builder.load_file(str(HERE / "ekran_intercom.kv"))
        self.voice = None
        self.voice_recorder = voice.Recorder()
        self.voice_player = voice.Player()
        self.music = MusicPlayer(self.voice_player)    # ekran Muzyka
        settings = json.loads((HERE / "settings.json").read_text(encoding="utf-8"))
        self.tablet_name = settings.get("tablet_name", "Tablet 2")
        self.ha_url = settings["url"]
        self.voice = voice.VoiceLink(settings, self.tablet_name, voice.cache_dir(),
                                     self._on_message)
        self.voice.start()
        self.setup_games(settings, self.tablet_name)      # gra przez sieć z innymi tabletami
        return Factory.IntercomMain()

    def on_start(self):
        # Android 12 (TCL): przy zimnym starcie powierzchnia GL powstaje po obrocie do
        # poziomu, a statyczny ekran domofonu nie wymusza nowej klatki - zostaje czarny
        # ekran do pierwszego dotyku. Odświeżanie co sekundę rysuje go zawsze.
        from kivy.clock import Clock
        Clock.schedule_interval(lambda _dt: Window.canvas.ask_update(), 1.0)
        Window.bind(on_resize=lambda *_a: Clock.schedule_once(
            lambda _dt: Window.canvas.ask_update(), 0.1))
        self.root.ids.talk.init_talk()

    def on_pause(self):
        return True                     # wygaszony ekran nie zamyka aplikacji

    def nav(self, target: str):
        """Menu: home - domofon, games - siatka gier, inna nazwa - ekran gry."""
        sm = self.root.ids.sm
        screen = "start" if target in ("home", "voice") else target
        if sm.has_screen(screen):
            self.leave_network_games(keep=screen)
            sm.transition = NoTransition()
            sm.current = screen
            self.section = "home" if screen == "start" else "games"

    def _on_message(self, info, path):
        dur = info.get("duration")
        self.voice_last = (f"od: {info.get('from', '?')}, {info.get('time', '')}"
                           + (f", {dur:.0f} s" if isinstance(dur, (int, float)) else ""))
        self.voice_player.play([voice.INTRO, path])


if __name__ == "__main__":
    IntercomApp().run()
