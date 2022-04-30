#!/bin/bash

# Intantiate file for tracking, if needed.
FILE="/etc/removable-libraries"
PART=$1

if [[ ! -f "${FILE}" ]]; then
    echo "Creating $FILE"
    touch ${FILE}
fi

# Mount service checks for UUID before adding the drive to steam.
echo "Initializing steam library."
PART_UUID=$(blkid -o value -s UUID /dev/${PART})
grep -qxF ${PART_UUID} ${FILE} || echo ${PART_UUID} >> ${FILE}
