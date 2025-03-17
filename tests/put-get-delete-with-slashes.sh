#!/usr/bin/env bash

INPUT_FOLDER="in-files"
OUTPUT_FOLDER="out-files"
BASE_URL="http://localhost:8000"

PREFIX_1="object-with-slash/"

INPUT_FILES=(
    "plan-etat-de-l-art.txt"
    "state-of-the-art-object-store.pdf"
    "universite-evry.jpg"
    
)

STEP=false

usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    #echo "  --debug, -d: Enable debug mode"
    echo "  --step, -s: Enable step-by-step mode"
    exit 1
}

read_option() {
    while [ "$#" -gt 0 ]; do
        case "$1" in
            --debug | -d)
                set -x
                ;;
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

    # Tester la disponibilité du serveur avec une requête GET à la racine de l'API
    response=$(curl --write-out "%{http_code}" --silent --output /dev/null "$BASE_URL/")

    if [ "$response" -ne 200 ]; then
        echo "Error: Server is not running (HTTP code: $response)"
        exit 1
    else
        echo "Server is up and running!"
    fi
    echo
}

diff_objects() {
    for FILE_NAME in "${INPUT_FILES[@]}"; do
        FILE_PATH="$INPUT_FOLDER/$FILE_NAME"
        OUTPUT_PATH="$OUTPUT_FOLDER/$FILE_NAME"
        echo "Comparing $FILE_PATH and $OUTPUT_PATH..."
        diff "$FILE_PATH" "$OUTPUT_PATH" > /dev/null
        if [ $? -eq 0 ]; then
            echo "Files are identical."
        else
            echo "Files are different!"
        fi
    done
}

# Fonction pour tester les commandes PUT, GET et DELETE en utilisant le client
test_object_store() {
    file_name_1="${INPUT_FILES[0]}"
    file_name_2="${INPUT_FILES[1]}"
    file_name_3="${INPUT_FILES[2]}"

    file_path_1="$INPUT_FOLDER/$file_name_1"
    file_path_2="$INPUT_FOLDER/$file_name_2"
    file_path_3="$INPUT_FOLDER/$file_name_3"

    object_name_1="$PREFIX_1${file_name_1}"
    object_name_2="$PREFIX_1${file_name_2}"
    object_name_3="${file_name_3}"

    # PUT
    if $STEP; then
        read -p "Press enter to continue to PUT"
    fi
    echo "=== Testing PUT command... ==="
    python3 client.py put "$object_name_1" "$file_path_1"
    python3 client.py put "$object_name_2" "$file_path_2"
    python3 client.py put "$object_name_3" "$file_path_3"

    # GET
    if $STEP; then
        read -p "Press enter to continue to GET"
    fi
    echo "=== Testing GET command... ==="
    python3 client.py get "$object_name_1" "$OUTPUT_FOLDER/$file_name_1"
    python3 client.py get "$object_name_2" "$OUTPUT_FOLDER/$file_name_2"
    python3 client.py get "$object_name_3" "$OUTPUT_FOLDER/$file_name_3"

    # Diff
    diff_objects

    # DELETE
    if $STEP; then
        read -p "Press enter to continue to DELETE"
    fi
    echo "=== Testing DELETE command... ==="
    python3 client.py delete "$object_name_1"
    python3 client.py delete "$object_name_2"
    python3 client.py delete "$object_name_3"

    echo
}

# Remove all files in the output folder
clean() {
    echo "Cleaning up the output folder..."
    rm -f "$OUTPUT_FOLDER"/*
    echo "Cleaned up!"
}

main() {
    read_option "$@"

    mkdir -p "$OUTPUT_FOLDER"

    check_server
    test_object_store

    if $STEP; then
        read -p "Press enter to continue to clean output folder"
    fi
    clean
}

main "$@"
