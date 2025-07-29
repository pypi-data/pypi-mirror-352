import os


def init():
    # Specify the file path
    file_path = '/Users/welcome/.zprofile.sh'
    # Read the file content
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Parse and set environment variables
    for line in lines:
        # Remove any leading/trailing whitespaces
        line = line.strip()

        # Skip empty lines or comments
        if not line or line.startswith('#'):
            continue

        # Remove 'export' and split into key-value pair
        if line.startswith('export '):
            line = line[len('export '):]  # Remove 'export ' part

        # Split the line at the first '=' and strip spaces
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()  # Remove leading/trailing spaces from the key
            value = value.strip().strip('"')  # Remove spaces and quotes from value
            os.environ[key] = value  # Set the environment variable


def single_store_connect():
    init()
    import os
    import singlestoredb as s2

    conn = s2.connect(
        host=os.getenv("SINGLESTORE_HOST"),
        user=os.getenv("SINGLESTORE_USER"),
        password=os.getenv("SINGLESTORE_PASS"),
        database=os.getenv("SINGLESTORE_DB"),
        port=int(os.getenv("SINGLESTORE_PORT", 33335))
    )
    with conn:
        with conn.cursor() as cur:
            flag = cur.is_connected()
            print(flag)


def connect_qdrant_client():
    pass


def connect_pg_vector_client():
    pass


def connect_opensearch_client():
    pass
