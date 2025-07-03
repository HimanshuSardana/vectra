from src.tui.main import VectraTUI
from src.core.sync import ChromaDBSync

app = VectraTUI("./vector_store/")
app.run()
