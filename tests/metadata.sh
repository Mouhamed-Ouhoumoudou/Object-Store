#!/usr/bin/env bash

INPUT_FOLDER="in-files"
BASE_URL="http://localhost:8000"

OBJECT_NAME="metadata-test-object"
FILE_NAME="plan-etat-de-l-art.txt"
FILE_PATH="$INPUT_FOLDER/$FILE_NAME"

STEP=false

usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  --step, -s: Enable step-by-step mode"
    exit 1
}

read_option() {
    while [ "$#" -gt 0 ]; do
        case "$1" in
            --step | -s)
                STEP=true
                ;;
            --help | -h)
                usage
                ;;
            *)
                return
                ;;
        esac
        shift
    done
}

check_server() {
    echo "Checking if the server is running..."
    response=$(curl --write-out "%{http_code}" --silent --output /dev/null "$BASE_URL/")
    if [ "$response" -ne 200 ]; then
        echo "Error: Server is not running (HTTP code: $response)"
        exit 1
    else
        echo "Server is up and running!"
    fi
    echo
}

test_metadata() {
    # PUT Object
    if $STEP; then
        read -p "Press enter to continue to PUT object"
    fi
    echo "=== Uploading object for metadata test ==="
    python3 client.py put "$OBJECT_NAME" "$FILE_PATH"

    # Add Metadata
    if $STEP; then
        read -p "Press enter to update metadata"
    fi
    echo "=== Adding metadata ==="
    curl -X PUT -H "Content-Type: application/json" -d '{"author": "John Doe", "project": "Metadata Testing"}' \
        "$BASE_URL/metadata/$OBJECT_NAME"

    # Read Metadata
    if $STEP; then
        read -p "Press enter to read metadata"
    fi
    echo "=== Reading metadata ==="
    curl -X GET "$BASE_URL/metadata/$OBJECT_NAME"

    # Delete Metadata Key
    if $STEP; then
        read -p "Press enter to delete a metadata key"
    fi
    echo "=== Deleting metadata key 'project' ==="
    curl -X DELETE -H "Content-Type: application/json" -d '["project"]' "$BASE_URL/metadata/$OBJECT_NAME"

    # Read Metadata Again
    if $STEP; then
        read -p "Press enter to read metadata again"
    fi
    echo "=== Reading metadata after deletion ==="
    curl -X GET "$BASE_URL/metadata/$OBJECT_NAME"

    # DELETE Object
    if $STEP; then
        read -p "Press enter to delete the object"
    fi
    echo "=== Deleting object ==="
    python3 client.py delete "$OBJECT_NAME"
}

main() {
    read_option "$@"
    check_server
    test_metadata
}

main "$@"
