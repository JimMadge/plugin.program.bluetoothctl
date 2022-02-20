#!/usr/bin/env sh

wget https://upload.wikimedia.org/wikipedia/commons/d/da/Bluetooth.svg

magick \
    -background none \
    Bluetooth.svg \
    -background black \
    -resize 500x500 \
    -gravity center \
    -extent 512x512 \
    plugin.program.bluetoothctl/resources/icon.png

magick \
    -background none \
    Bluetooth.svg \
    -background black \
    -resize 700x700 \
    -gravity center \
    -extent 1280x720 \
    plugin.program.bluetoothctl/resources/fanart.jpg

rm Bluetooth.svg
