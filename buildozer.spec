[app]
title = Заметки
package.name = mynotes
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.5

# СЮДА ПИШЕМ НАЗВАНИЕ ВАШЕЙ ИКОНКИ
icon.filename = icon.png

requirements = python3,kivy

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
