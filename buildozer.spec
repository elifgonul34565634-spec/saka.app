[app]
title = Saka Oyunum
package.name = sakaoyun
package.domain = org.saka

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ogg,gif

version = 0.1
requirements = python3,kivy
orientation = portrait
osx.python_version = 3
osx.kivy_version = 1.9.1
fullscreen = 0

# Android Kararlılık Ayarları (Hataları kökten kesen kısım)
android.api = 33
android.ndk = 25b
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
