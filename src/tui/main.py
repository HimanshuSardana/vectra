from chromadb import PersistentClient
from google import genai
from google.genai import types
from rich.live import Live
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from questionary import select
import chromadb
from src.core.sync import ChromaDBSync

class VectraTUI:
    def __init__(self, storage_location):
        self.console = Console()
        self.storage_location = storage_location
        self.chroma_client = PersistentClient(path=storage_location)

    def display_banner(self):
        banner_text = Text()
        banner_text.append("Vectra\n", style="bold green")
        banner_text.append("A simple TUI for managing your vector store.", style="dim")
        self.console.print(Panel(banner_text, title="Vectra", expand=False))

    def display_panel(self, title, body, style="cyan"):
        """Utility method to show a panel."""
        panel = Panel(Text(body), title=title, title_align="left", expand=False, border_style=style)
        self.console.print(panel)

    def main_menu(self):
        return select(
            "What would you like to do?",
            choices=[
                "Query",
                "Sync current directory",
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
            elif choice == "Sync current directory":
                sync = ChromaDBSync(self.chroma_client)
                sync.sync()
                self.display_panel("Sync", "Current directory synced with the vector store.", style="green")
            elif choice == "Create new collection":
                self.create_collection()
            elif choice == "View collections":
                self.view_collections()
            elif choice == "Delete a collection":
                self.delete_collection()
            elif choice == "Exit":
                self.display_panel("Exit", "Goodbye! 👋", style="yellow")
                break

    def query(self):
        client = genai.Client()
        collections = self.chroma_client.list_collections()
        if len(collections) == 0:
            self.display_panel("Error", "No collections found.", style="red")
            return

        collection_name = select(
            "Choose the collection",
            choices=[choice.name for choice in collections]
        ).ask()

        collection = self.chroma_client.get_or_create_collection(name=collection_name)
        query = input("Query: ")
        content = Text.from_markup(f"[bold]Query:[/bold] {query} in [bold]{collection_name}[/bold]\n\n[yellow]Fetching results...[/yellow]")

        with Live(Panel(content, title="Query"), refresh_per_second=10, console=self.console) as live:
            try:
                response = collection.query(query_texts=[query], n_results=1)['documents'][0][0]
                llm_response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"""
                    Here's the query: {query}
                    Here are the vector store results: {response}
                    """,
                    config=types.GenerateContentConfig(
                        system_instruction="You are a helpful assistant, you will be provided with content from a vector store, your job is to use that content to answer queries",
                    )
                ).text
                updated_content = Text.from_markup(
                    f"[bold]Query:[/bold] [dim]{query}[/dim] in [bold]{collection_name}[/bold]\n\n"
                    f"[green]Result:[/green]\n{llm_response}"
                )
                live.update(Panel(updated_content, border_style="green", expand=False))
            except Exception as e:
                error_content = Text.from_markup(
                    f"[bold red]Error:[/bold red] {str(e)}"
                )
                live.update(Panel(error_content, title="Query Failed", border_style="red"))

    def create_collection(self):
        name = input("Collection name: ")
        self.chroma_client.get_or_create_collection(name=name)
        self.display_panel("Create Collection", f"Collection '{name}' created.", style="green")

    def view_collections(self):
        collections = self.chroma_client.list_collections()
        if not collections:
            self.display_panel("View Collections", "No collections found.", style="red")
            return

        body = "\n".join(f"{i+1}. {collection.name}" for i, collection in enumerate(collections))
        self.display_panel("Collections", body)

    def delete_collection(self):
        collections = self.chroma_client.list_collections()
        if not collections:
            self.display_panel("Delete Collection", "No collections to delete.", style="red")
            return

        collection_name = select(
            "Choose collection to delete",
            choices=[col.name for col in collections]
        ).ask()

        self.chroma_client.delete_collection(name=collection_name)
        self.display_panel("Delete Collection", f"Collection '{collection_name}' deleted.", style="bold red")

