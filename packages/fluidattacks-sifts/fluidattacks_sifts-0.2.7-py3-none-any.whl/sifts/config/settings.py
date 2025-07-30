import os
from pathlib import Path

DATA_DIR = Path(".data")


FI_AWS_OPENSEARCH_HOST = os.environ.get("AWS_OPENSEARCH_HOST", "https://localhost:9200")


FI_AWS_REGION_NAME = "us-east-1"


FI_ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")


YAML_PATH_VULNERABILITIES = DATA_DIR / "vulnerabilities.yaml"
YAML_PATH_REQUIREMENTS = DATA_DIR / "requirements.yaml"
