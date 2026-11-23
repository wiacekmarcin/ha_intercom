"""HA Intercom - aplikacja testowa domofonu (tablet MT8768E, 192.168.10.22).

Tylko wiadomości głosowe przez Home Assistant: przycisk "Przytrzymaj i mów" (do 30 s,
licznik w dół) oraz odtwarzanie przychodzących wiadomości z zapowiedzią
"Nowa wiadomość głosowa". Kod domofonu jest wspólny z kioskiem (kiosk/voice.py,
kiosk/widgets/voice_dialog.py) - kopiowany przed budowaniem przez sync_kiosk.sh.

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

from kivy.app import App  # noqa: E402
from kivy.core.window import Window  # noqa: E402
from kivy.lang import Builder  # noqa: E402
from kivy.properties import BooleanProperty, NumericProperty, StringProperty  # noqa: E402
from kivy.uix.boxlayout import BoxLayout  # noqa: E402

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


class IntercomApp(App):
    title = "HA Intercom"
    tablet_name = StringProperty("Tablet 2")
    voice_last = StringProperty("")

    def build(self):
        Window.clearcolor = (0, 0, 0, 1)
        icons.register_font()
        # intercom.kv Kivy wczytuje sam (nazwa jak IntercomApp); klasy z kiosku:
        for name in ("widgets.kv", "settings.kv", "voice_dialog.kv"):
            Builder.load_file(str(KV_DIR / name))
        self.voice = None
        self.voice_recorder = voice.Recorder()
        self.voice_player = voice.Player()
        settings = json.loads((HERE / "settings.json").read_text(encoding="utf-8"))
        self.tablet_name = settings.get("tablet_name", "Tablet 2")
        self.ha_url = settings["url"]
        self.voice = voice.VoiceLink(settings, self.tablet_name, voice.cache_dir(),
                                     self._on_message)
        self.voice.start()
        return IntercomRoot()

    def on_start(self):
        self.root.init_talk()

    def on_pause(self):
        return True                     # wygaszony ekran nie zamyka aplikacji

    def _on_message(self, info, path):
        dur = info.get("duration")
        self.voice_last = (f"od: {info.get('from', '?')}, {info.get('time', '')}"
                           + (f", {dur:.0f} s" if isinstance(dur, (int, float)) else ""))
        self.voice_player.play([voice.INTRO, path])


if __name__ == "__main__":
    IntercomApp().run()
