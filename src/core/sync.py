import chromadb
import os
from rich.console import Console

class ChromaDBSync:
    def __init__(self, client: chromadb.Client):
        self.client = client
        self.console = Console()

    def sync(self):
        """
        Syncs data to a ChromaDB collection.

        :param collection_name: Name of the ChromaDB collection.
        :param data: List of dictionaries containing the data to be synced.
        """
        cwd = os.getcwd()

        # check if cwd has a .vectra file
        if not os.path.exists(os.path.join(cwd, '.vectra')):
            self.console.print(f"[bold red]No .vectra file found in {cwd}.[/bold red]. Creating one")
            # ask for collection name
            collection_name = input("Enter the ChromaDB collection name: ")
            with open(os.path.join(cwd, '.vectra'), 'w') as f:
                f.write(collection_name)

        else:
            with open(os.path.join(cwd, '.vectra'), 'r') as f:
                collection_name = f.read().strip()

        collection = self.client.get_or_create_collection(name=collection_name)

        # walk through the current directory and subdirectories, check for .txt and .md and .typ files and add those to the collection
        total_files = 0
        for root, dirs, files in os.walk(cwd):
            for file in files:
                if file.endswith(('.txt', '.md', '.typ')):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Add the content to the collection
                        collection.add(documents=[content], metadatas=[{"file_name": file}], ids=[file_path])
                    total_files += 1
        self.console.print(f"[bold green]Synced {total_files} files to the collection '{collection_name}'[/bold green]")

    def check_collection_exists(self, collection_name: str) -> bool:
        """
        Checks if a ChromaDB collection exists.

        :param collection_name: Name of the ChromaDB collection.
        :return: True if the collection exists, False otherwise.
        """
        try:
            self.client.get_collection(name=collection_name)
            return True
        except chromadb.CollectionNotFoundError:
            return False
