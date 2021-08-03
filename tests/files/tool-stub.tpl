#! /bin/bash

TOOL_URL=%TOOL_URL%
TOOL_MD5SUM=%TOOL_MD5SUM%
TOOL_CMD=%TOOL_CMD%

TOOL_FILE="$(basename $TOOL_URL)"
TOOL_DIR=$(echo $TOOL_FILE | sed s/.tar.gz//)
TOOLS_DIR="$HOME/.steam/root/compatibilitytools.d"

pushd "$TOOLS_DIR"
rm -f "$TOOL_FILE"
curl -L -O $TOOL_URL

if ! echo "$TOOL_MD5SUM $TOOL_FILE" | md5sum --status -c; then
	echo "checksum mismatch"
	exit
fi

rm -rf "$TOOL_DIR"
tar xf "$TOOL_FILE"
rm "$TOOL_FILE"
popd

exec "$TOOLS_DIR/$TOOL_DIR/$TOOL_CMD" $@
