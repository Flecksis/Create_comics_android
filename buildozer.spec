[app]
title = ComicsAPP
package.name = ComicsAPP
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.include_patterns = sprite/*, dialog_window/*

version = 0.1

requirements = python3,kivy,kivymd ,sdl2_ttf, pillow , plyer

orientation = landscape
fullscreen = 0


android.api = 32
android.minapi = 21
android.arch = arm64-v8a,armeabi-v7a


icon.filename = 1.jpg
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE


[buildozer]
log_level = 2