from google import genai
from google.genai import types
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from questionary import select
from chromadb import PersistentClient

class VectraQuery:
    def __init__(self, prompt):
        self.prompt = prompt
        self.client = genai.Client()
        self.console = Console()

    def run_query(self):
    try:
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"""
                    Here's the query: {self.prompt}

                    """,
            config=types.GenerativeModelConfig(
                system_instruction="You are a helpful assistant, you will be provided with content from a vector store, your job is to use that content to answer queries",
            )
        )

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
                updated_content = Text.from_markup(
                    f"[bold]Query:[/bold] [dim]{query}[/dim] in [bold]{collection_name}[/bold]\n\n"
                        f"[green]Top result:[/green]\n{response}"
                )
                live.update(Panel(updated_content, border_style="green", expand=False))
            except Exception as e:
                error_content = Text.from_markup(
                    f"[bold red]Error:[/bold red] {str(e)}"
                )
                live.update(Panel(error_content, title="Query Failed", border_style="red"))

