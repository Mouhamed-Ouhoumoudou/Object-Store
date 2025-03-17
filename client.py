#!/usr/bin/env python3

import argparse
import requests
import json

BASE_URL = "http://localhost:8000"


# Utility function to handle HTTP responses
def handle_response(response):
    try:
        response.raise_for_status()
        print(response.json())
    except requests.HTTPError as e:
        print(f"HTTP Error: {e}")
        try:
            print(response.json())
        except ValueError:
            print(response.text)


# Object operations
def put_object(object_name, file_path, metadata):
    try:
        with open(file_path, "rb") as file:
            files = {"object": file}
            data = {"metadata": json.dumps(metadata)} if metadata else {}
            response = requests.put(
                f"{BASE_URL}/objects/{object_name}", files=files, data=data
            )
        handle_response(response)
    except Exception as e:
        print(f"Error during PUT request: {e}")


def get_object(object_name, output_path, version_id=None):
    try:
        params = {"version_id": version_id} if version_id else {}
        response = requests.get(f"{BASE_URL}/objects/{object_name}", params=params)
        if response.status_code == 200:
            with open(output_path, "wb") as file:
                file.write(response.content)
            print(f"Object '{object_name}' saved to '{output_path}'")
        else:
            handle_response(response)
    except Exception as e:
        print(f"Error during GET request: {e}")


def list_objects(with_versions=False, key=None, value=None, exists=None):
    try:
        params = {
            "with_versions": with_versions,
            "key": key,
            "value": value,
            "exists": exists,
        }
        response = requests.get(
            f"{BASE_URL}/objects",
            params={k: v for k, v in params.items() if v is not None},
        )
        handle_response(response)
    except Exception as e:
        print(f"Error during LIST request: {e}")


def delete_object(object_name, version_id=None):
    try:
        params = {"version_id": version_id} if version_id else {}
        response = requests.delete(f"{BASE_URL}/objects/{object_name}", params=params)
        handle_response(response)
    except Exception as e:
        print(f"Error during DELETE request: {e}")


# Metadata operations
def update_metadata(object_name, metadata):
    try:
        response = requests.put(f"{BASE_URL}/metadata/{object_name}", json=metadata)
        handle_response(response)
    except Exception as e:
        print(f"Error during UPDATE METADATA request: {e}")


def get_metadata(object_name):
    try:
        response = requests.get(f"{BASE_URL}/metadata/{object_name}")
        handle_response(response)
    except Exception as e:
        print(f"Error during GET METADATA request: {e}")


def delete_metadata(object_name, keys):
    try:
        response = requests.delete(
            f"{BASE_URL}/metadata/{object_name}", json={"keys": keys}
        )
        handle_response(response)
    except Exception as e:
        print(f"Error during DELETE METADATA request: {e}")


# Policy operations
def update_policy(object_name, max_versions):
    try:
        response = requests.put(
            f"{BASE_URL}/config/object-policy/{object_name}",
            json={"max_versions": max_versions},
        )
        handle_response(response)
    except Exception as e:
        print(f"Error during UPDATE POLICY request: {e}")


def list_policies():
    try:
        response = requests.get(f"{BASE_URL}/config/object-policies")
        handle_response(response)
    except Exception as e:
        print(f"Error during LIST POLICIES request: {e}")


def main():
    parser = argparse.ArgumentParser(description="Client for Object Store API")
    command_parser = parser.add_subparsers(dest="command", help="Available commands")

    # PUT command
    put_parser = command_parser.add_parser("put", help="Upload an object")
    put_parser.add_argument("object_name", type=str, help="Name of the object")
    put_parser.add_argument("file_path", type=str, help="Path to the file to upload")
    put_parser.add_argument(
        "--metadata",
        type=json.loads,
        help='JSON string of metadata (e.g., \'{"key": "value"}\')',
    )

    # GET command
    get_parser = command_parser.add_parser("get", help="Download an object")
    get_parser.add_argument("object_name", type=str, help="Name of the object")
    get_parser.add_argument(
        "output_path", type=str, help="Path to save the downloaded file"
    )
    get_parser.add_argument(
        "--version_id", type=str, help="Specific version ID to download"
    )

    # LIST command
    list_parser = command_parser.add_parser("list", help="List stored objects")
    list_parser.add_argument(
        "--with_versions", action="store_true", help="List objects with versions"
    )
    list_parser.add_argument("--key", type=str, help="Metadata key to filter objects")
    list_parser.add_argument(
        "--value", type=str, help="Metadata value to filter objects"
    )
    list_parser.add_argument(
        "--exists", type=bool, default=True, help="Check if key exists (default: True)"
    )

    # DELETE command
    delete_parser = command_parser.add_parser("delete", help="Delete an object")
    delete_parser.add_argument("object_name", type=str, help="Name of the object")
    delete_parser.add_argument(
        "--version_id", type=str, help="Specific version ID to delete"
    )

    # METADATA commands
    mget_parser = command_parser.add_parser(
        "mget", help="Retrieve metadata of an object"
    )
    mget_parser.add_argument("object_name", type=str, help="Name of the object")

    mput_parser = command_parser.add_parser(
        "mput", help="Add or update metadata for an object"
    )
    mput_parser.add_argument("object_name", type=str, help="Name of the object")
    mput_parser.add_argument(
        "--metadata",
        type=json.loads,
        required=True,
        help='JSON string of metadata to update (e.g., \'{"key": "value"}\')',
    )

    mdel_parser = command_parser.add_parser(
        "mdel", help="Delete specific metadata keys from an object"
    )
    mdel_parser.add_argument("object_name", type=str, help="Name of the object")
    mdel_parser.add_argument(
        "--keys",
        type=str,
        nargs="+",
        required=True,
        help="List of keys to delete (e.g., key1 key2 key3)",
    )

    # POLICY commands
    policy_parser = command_parser.add_parser("policy", help="Policy operations")
    policy_parser.add_argument(
        "operation", choices=["update", "list"], help="Policy operation"
    )
    policy_parser.add_argument(
        "--object_name", type=str, help="Object name (for 'update')"
    )
    policy_parser.add_argument(
        "--max_versions", type=int, help="Maximum versions to keep (for 'update')"
    )

    args = parser.parse_args()

    if args.command == "put":
        put_object(args.object_name, args.file_path, args.metadata)
    elif args.command == "get":
        get_object(args.object_name, args.output_path, args.version_id)
    elif args.command == "list":
        list_objects(args.with_versions, args.key, args.value, args.exists)
    elif args.command == "delete":
        delete_object(args.object_name, args.version_id)
    elif args.command == "mget":
        get_metadata(args.object_name)
    elif args.command == "mput":
        update_metadata(args.object_name, args.metadata)
    elif args.command == "mdel":
        delete_metadata(args.object_name, args.keys)
    elif args.command == "policy":
        if args.operation == "update":
            update_policy(args.object_name, args.max_versions)
        elif args.operation == "list":
            list_policies()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
