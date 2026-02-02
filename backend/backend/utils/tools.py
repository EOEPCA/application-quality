import os

# Usage: feature_1=getenv_bool('FEATURE_1', False)
# Credits: https://stackoverflow.com/a/68259416
def getenv_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in ("yes", "y", "true", "1", "t")
