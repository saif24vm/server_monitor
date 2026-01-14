def list_directory(client, remote_path="/"):
    print(f"Listing directory: {remote_path}")
    items = client.list(remote_path)

    for item in items:
        print(item)
