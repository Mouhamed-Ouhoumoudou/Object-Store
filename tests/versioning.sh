#!/usr/bin/env bash

INPUT_FOLDER="in-files"
BASE_URL="http://localhost:8000"

OBJECT_NAME="versioning-test-object"
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

test_versioning() {
    # PUT Object (First Version)
    if $STEP; then
        read -p "Press enter to PUT first version"
    fi
    echo "=== Uploading first version ==="
    python3 client.py put "$OBJECT_NAME" "$FILE_PATH"

    # PUT Object (Second Version)
    if $STEP; then
        read -p "Press enter to PUT second version"
    fi
    echo "=== Uploading second version ==="
    echo "Adding 'Second Version' to file"
    echo "Second Version" >> "$FILE_PATH"
    python3 client.py put "$OBJECT_NAME" "$FILE_PATH"

    # List Versions
    if $STEP; then
        read -p "Press enter to list versions"
    fi
    echo "=== Listing versions ==="
    curl -X GET "$BASE_URL/objects/$OBJECT_NAME/versions"

    # GET Specific Version
    if $STEP; then
        read -p "Press enter to GET a specific version"
    fi
    echo "=== Downloading first version ==="
    FIRST_VERSION=$(curl -s "$BASE_URL/objects/$OBJECT_NAME/versions" | jq -r '.versions[-1]')
    python3 client.py get "$OBJECT_NAME?version=$FIRST_VERSION" "out-files/first-version.txt"

    # DELETE Specific Version
    if $STEP; then
        read -p "Press enter to DELETE a specific version"
    fi
    echo "=== Deleting first version ==="
    curl -X DELETE "$BASE_URL/objects/$OBJECT_NAME?version=$FIRST_VERSION"

    # DELETE Object
    if $STEP; then
        read -p "Press enter to DELETE object"
    fi
    echo "=== Deleting all versions of object ==="
    python3 client.py delete "$OBJECT_NAME"
}

main() {
    read_option "$@"
    check_server
    test_versioning
}

main "$@"
