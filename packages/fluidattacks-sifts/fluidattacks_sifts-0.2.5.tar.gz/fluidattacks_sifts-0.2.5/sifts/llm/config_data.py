import os
from pathlib import Path

import yaml

from sifts.llm.types import ModelParameters

model_path = Path("model_parameters.yaml").absolute()
model_path = model_path if model_path.exists() else Path(os.environ["MODEL_PARAMETERS_PATH"])
with Path(model_path).open() as reader:
    MODEL_PARAMETERS: ModelParameters = yaml.safe_load(reader.read())

TOP_FINDINGS = MODEL_PARAMETERS["top_findings"]
