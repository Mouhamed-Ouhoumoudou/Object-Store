# Object Store

## Project Overview

This project is an Object Store implemented using FastAPI as the RESTful API framework and a local filesystem for storing objects. The API provides functionalities for storing, retrieving, and managing objects.

## Project Structure

Here is the basic structure of the project repository:

```
object-store/
├── client.py               # Client script for interacting with the API
├── README.md               # Project documentation
├── app/
│   ├── main.py             # Entry point for the FastAPI application
│   ├── routers.py          # API routes and endpoints
│   ├── storage_manager.py  # Logic for interacting with the filesystem to store/retrieve objects
|   ├── metadata_manager.py # Logic for interacting with metadata files
│   ├── config.py           # Configuration settings for the application
│   └── schemas.py          # Pydantic schemas for data validation
├── data/                   # Directory for storing objects and metadata
│   └── metadata.json       # Global metadata file of the object store
├── tests/                  # Directory for test scripts and files
├── .gitignore              # Files and folders to ignore in version control
└── requirements.txt        # Python dependencies
```

## Directory Details

### client.py

This script provides a command-line interface for interacting with the Object
Store API. It allows users to upload, download, delete, and manage objects using
the API endpoints. The script uses the `requests` library to make HTTP requests
to the server.

To see the available commands and options, run:

```bash
source venv/bin/activate
pip install requests
python3 client.py --help
```

Some examples :

````bash
# Object Management
python3 client.py put my_object_name /path/to/file                       # Upload an object
python3 client.py get my_object_name /path/to/output                     # Download an object
python3 client.py delete my_object_name                                  # Delete an object
python3 client.py put folder/object_name /path/to/file                   # Upload an object inside a folder
python3 client.py get folder/object_name /path/to/output                 # Download an object from a folder

# Metadata Management
python3 client.py mget my_object_name                                    # Retrieve metadata of an object
python3 client.py mput my_object_name --metadata '{"key1": "value1"}'    # Add a metadata key-value pair
python3 client.py mput my_object_name --metadata '{"key1": "new_value"}' # Update a metadata key-value pair
python3 client.py mdel my_object_name --keys key1                        # Delete a specific metadata key
python3 client.py mdel my_object_name --keys key1 key2                   # Delete multiple metadata keys
python3 client.py mput folder/object_name --metadata '{"author": "John"}' # Add metadata to an object in a folder

# Listing and Searching
python3 client.py list --with_versions                                  # List all objects with their versions
python3 client.py list --key author --value John                       # Search objects with a specific key-value pair in metadata
python3 client.py list --key tag --exists                              # Search objects having a specific metadata key
```


### app/

This directory contains the core logic of the application:

- `main.py`: Defines the FastAPI application and includes the server setup.
- `routers.py`: Contains the API endpoints for managing objects.
- `storage.py`: Handles filesystem operations such as storing and retrieving objects.
- `config.py`: Centralized configuration for the application, such as paths and settings.
- `schemas.py`: Defines data models and validation rules using Pydantic.

### data/

This directory acts as the storage backend:

- `metadata.json`: (Optional) Contains metadata pertaining to the object store configuration and object details such as the list of objects.

## How to Run the Server Application

1. Clone the repository:

   ```bash
   git clone https://gitlab.com/jilkarnas/m2-cns-sr-r-d-project-object-store.git object-store
   cd object-store
   ```

2. Create and activate a Python virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows, use 'venv\Scripts\activate'
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the FastAPI server:

   ```bash
   fastapi run main.py
   ```

5. Access the API documentation at:

   - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Dependencies

The project uses the following Python libraries:

- `fastapi`: Framework for building APIs.
- `pydantic`: Data validation and parsing using Python type hints. Used by
    FastAPI for request/response validation.

## Development

To contribute or modify the project, follow these steps:

1. Ensure you have the repository cloned and the virtual environment set up (see "How to Run the Application").
2. Run the application in development mode :
   ```bash
   fastapi dev main.py
   ```
3. Make your changes in the appropriate files within the `app/` or `tests/` directories.
4. Run the test suite to ensure your changes do not break existing functionality:
   ```bash
   # python module for test not yet defined, pytest ?
   ```
5. (Optional) Use formatting tools like `black` to maintain code quality:
   ```bash
   black .
   # Setup automatic reformating ? Githooks, CI/CD ?
   ```
6. Submit a pull request with a clear description of your changes, starting with a verb in the Simple Past tense, such as :
   ```
   added a new endpoint for file upload
   fixed a bug in the object retrieval logic
   deleted deprecated code for obsolete API routes
   refactored the storage module for better performance
   ```

## License

Not set yet.
