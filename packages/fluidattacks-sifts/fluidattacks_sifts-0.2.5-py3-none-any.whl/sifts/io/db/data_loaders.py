import json
import os
from pathlib import Path

typology_path = Path("typology_embedding.json").absolute()
typology_path = (
    typology_path if typology_path.exists() else Path(os.environ["TYPOLOGY_EMBEDDING_PATH"])
)
with Path(typology_path).open() as f:
    KNN_DATA = json.load(f)
