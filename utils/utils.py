from pathlib import Path

def load_qss_file(filename: str) -> str:
    """Charge un fichier .qss et renvoie son contenu."""
    path = Path(__file__).parent.parent / "styles" / filename
    with path.open(encoding="utf-8") as f:
        return f.read()