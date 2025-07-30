import requests
import yaml

from sifts.config.settings import YAML_PATH_REQUIREMENTS, YAML_PATH_VULNERABILITIES

if not YAML_PATH_VULNERABILITIES.exists():
    response = requests.get(
        (
            "https://gitlab.com/fluidattacks/universe/-/raw"
            "/f593cedbfb782d0d6a6c1a932e8a1e55a5ae450c/defines/src/vulnerabilities/data.yaml"
        ),
        timeout=30,
    )
    YAML_PATH_VULNERABILITIES.write_text(response.text)

if not YAML_PATH_REQUIREMENTS.exists():
    response = requests.get(
        (
            "https://gitlab.com/fluidattacks/universe/-/raw"
            "/3f8e14937c26bae7ceff8f19263249b9a383a2b9/defines/src/requirements/data.yaml"
        ),
        timeout=30,
    )
    YAML_PATH_REQUIREMENTS.write_text(response.text)

DEFINES_VULNERABILITIES: dict[str, dict[str, dict[str, str]]] = yaml.safe_load(
    YAML_PATH_VULNERABILITIES.read_text(),
)
DEFINES_REQUIREMENTS: dict[str, dict[str, dict[str, str]]] = yaml.safe_load(
    YAML_PATH_REQUIREMENTS.read_text(),
)
