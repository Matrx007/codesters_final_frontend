#!/bin/sh

if [ $# -eq 0 ]; then
    printf '%s\n' "./curlfetch.sh <filename> <GET|POST|PUT|DELETE> <url>"
else
    OUTPUT=$(curl --header 'Content-Type: application/json' \
                  --cookie /tmp/cookies.txt \
                  --cookie-jar /tmp/newcookies.txt \
                  --request $2 \
                  --data "$(cat $1)" \
                  http://localhost:5000$3)
    NEW_COOKIES=$(cat /tmp/newcookies.txt)

    echo "--- JSON response ---"
    printf '%s\n\n' "$OUTPUT"

    echo "--- New cookies that were set ---"
    printf '%s\n\n' "$NEW_COOKIES"
fi

