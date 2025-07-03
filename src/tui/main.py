from chromadb import PersistentClient
from rich.console import Console
from questionary import select
import chromadb

class VectraTUI:
    def __init__(self, storage_location):
        self.console = Console()
        self.storage_location = storage_location
        self.chroma_client = chromadb.PersistentClient(path=storage_location)

    def display_banner(self):
        self.console.print("[bold green]Vectra[/bold green]")

    def main_menu(self):
        return select(
            "What would you like to do?",
            choices=[
                "Query",
                "Create new collection",
                "View collections",
                "Delete a collection",
                "Exit"
            ]
        ).ask()

    def run(self):
        self.display_banner()

        while True:
            choice = self.main_menu()

            if choice == "Query":
                self.query()
            elif choice == "Create new collection":
                self.create_collection()
            elif choice == "View collections":
                self.view_collections()
            elif choice == "Delete a collection":
                self.delete_collection()
            elif choice == "Exit":
                self.console.print("[bold yellow]Goodbye![/bold yellow]")
                break

    def query(self):
        self.console.print("[italic cyan]Querying...[/italic cyan]")
        collections = self.chroma_client.list_collections()
        if len(collections) == 0:
            self.console.print("[red]No collections found[/red]")
        else:
            collection_name = select(
                "Choose the collection",
                choices=[choice.name for choice in collections]
            ).ask()

            collection = self.chroma_client.get_or_create_collection(name=collection_name)
            query = input("Query: ")


    def create_collection(self):
        self.console.print("[italic cyan]Creating collection...[/italic cyan]")

    def view_collections(self):
        collections = self.chroma_client.list_collections()
        for idx, collection in enumerate(collections):
            print(idx+1, collection.name)

    def delete_collection(self):
        self.console.print("[italic cyan]Deleting collection...[/italic cyan]")

