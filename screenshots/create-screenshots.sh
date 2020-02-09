#!/bin/bash
google-chrome --headless --disable-gpu --window-size=1920,1080 --screenshot=platforms.png http://localhost:8844/
google-chrome --headless --disable-gpu --window-size=1920,1080 --screenshot=flathub.png http://localhost:8844/platforms/flathub/new
