#!/usr/bin/env sh

wget https://upload.wikimedia.org/wikipedia/commons/d/da/Bluetooth.svg

magick \
    -background none \
    Bluetooth.svg \
    -background black \
    -resize 512x512 \
    -gravity center \
    -extent 512x512 \
    plugin.program.bluetoothctl/resources/icon.png

rm Bluetooth.svg
