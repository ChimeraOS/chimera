#!/bin/bash
# Make sure we're running in the correct directory
cd "$(dirname "$0")"

# Set the browser to use
CHROME=""
BROWSERS="chromium google-chrome-stable google-chrome"
for browser in ${BROWSERS}; do
	if which "${browser}" > /dev/null 2>&1; then
		CHROME="${browser}"
		echo "Using ${browser}"
		break
	else
		echo "Could not find ${browser}"
	fi
done

if [ -z "${CHROME}" ]; then
	echo "Chromium or Chrome needs to be installed to be able to make screenshots"
	exit 1
fi

# Start chimera
cd ..
./chimera &
sleep 3

# Take the screenshots
cd -
${CHROME} --headless --disable-gpu --window-size=1920,1080 --screenshot=platforms.png http://localhost:8844/
${CHROME} --headless --disable-gpu --window-size=1920,1080 --screenshot=flathub.png http://localhost:8844/library/flathub/new

# Stop chimera
kill %1
