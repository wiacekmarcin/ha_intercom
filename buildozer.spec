[app]
title = HA Intercom
package.name = haintercom
package.domain = pl.mieszkanie
version = 0.7

source.dir = .
source.include_exts = py,png,kv,ttf,json,ogg
# kiosk/ i assets/ kopiuje sync_kiosk.sh z ../ha_kiosk (wspólny kod domofonu);
# settings.json (z tokenem HA) jest wbudowany w APK - nie udostępniaj pliku APK
source.exclude_dirs = bin, .buildozer, __pycache__, .venv, venv
source.exclude_patterns = buildozer.spec, sync_kiosk.sh

requirements = python3,kivy==2.3.1,requests,urllib3,certifi,charset-normalizer,idna,openssl

orientation = landscape
fullscreen = 1

# --- Android ---
android.permissions = INTERNET, ACCESS_NETWORK_STATE, RECORD_AUDIO, WAKE_LOCK
android.api = 33
android.minapi = 21
android.ndk_api = 21
# tablet testowy: MediaTek MT8768E (Helio P22) - ARM 64-bit
android.archs = arm64-v8a
android.accept_sdk_license = True
android.allow_backup = False
# ekran nie gaśnie, dopóki aplikacja jest otwarta (odbiór wiadomości)
android.wakelock = True
# jedna aktywność - ponowne uruchomienie trafia do działającej aplikacji (jak w kiosku)
android.manifest.launch_mode = singleTask
android.release_artifact = apk

[buildozer]
# wspólny katalog budowania kiosków (ha_kiosk, ha_kiosk_dzieci, ha_intercom) - biblioteki
# skompilowane raz dla danej architektury; budować po kolei, nie równolegle
build_dir = ../.buildozer-wspolny
log_level = 2
warn_on_root = 1
