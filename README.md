# HA Intercom

Aplikacja testowa domofonu na tablet Android (TCL Tab 10, MT8768E, arm64-v8a), działająca
razem z kioskiem [ha_kiosk_hol](https://github.com/wiacekmarcin/ha_kiosk_hol).

- przycisk "Przytrzymaj i mów" (albo dotknij - mów - dotknij), nagranie do 30 s z licznikiem,
- nagranie idzie przez Home Assistant do pozostałych tabletów (plik w `/media` HA
  i encja `sensor.kiosk_wiadomosc_glosowa`),
- przychodzące wiadomości i komunikaty tekstowe (`script.kiosk_komunikat`, mowa TTS Nabu Casa)
  odtwarzane po zapowiedzi z gongiem.

Kod domofonu jest wspólny z kioskiem (`kiosk/voice.py`, `kiosk/widgets/voice_dialog.py`).

## Budowanie

Repozytorium `ha_kiosk_hol` musi leżeć obok, w katalogu `../ha_kiosk`.

```bash
./sync_kiosk.sh "Tablet 2"            # kopia kodu kiosku, zasobów i settings.json (token z kiosku)
buildozer android release             # APK arm64-v8a w bin/
```

Drugi argument `sync_kiosk.sh` to adres HA (domyślnie `http://192.168.10.250:8123`).
`settings.json` z tokenem jest wbudowany w APK - nie udostępniaj pliku APK.

## Instalacja (ADB bezprzewodowe, Android 11+)

```bash
adb pair <ip>:<port_parowania> <kod>
adb connect <ip>:<port>
adb install -r bin/haintercom-*-arm64-v8a-release.apk
adb shell pm grant pl.mieszkanie.haintercom android.permission.RECORD_AUDIO
```

Aplikacja odbiera wiadomości, gdy jest otwarta (ekran nie gaśnie, dopóki działa).
