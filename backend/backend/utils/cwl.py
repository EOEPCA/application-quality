from typing import Any


def get_secret_params(cwl_data: dict[str, Any]) -> list[str]:
    """Inspects a parsed CWL dictionary and returns parameter names listed in cwltool:Secrets.
    In CWL, secrets are declared under the `requirements` or `hints` section under the
    extension key `cwltool:Secrets`. The `secrets` parameter contains an array of input
    parameter names that should be treated as sensitive.
    """
    secrets: list[str] = []
    if not isinstance(cwl_data, dict):
        return secrets

    # Check both 'requirements' and 'hints' blocks
    sections = []
    for key in ("requirements", "hints"):
        block = cwl_data.get(key)
        if isinstance(block, list):
            sections.extend(block)
        elif isinstance(block, dict):
            # Handles dictionary-style requirements mapping
            for req_name, req_val in block.items():
                if isinstance(req_val, dict):
                    sections.append({"class": req_name, **req_val})
                else:
                    sections.append({"class": req_name})

    # Search for cwltool:Secrets
    for item in sections:
        if isinstance(item, dict) and item.get("class") == "cwltool:Secrets":
            secret_list = item.get("secrets", [])
            if isinstance(secret_list, list):
                secrets.extend(secret_list)

    return secrets


def get_all_secret_params(cwl_data: object) -> list[str]:
    """Recursively searches a CWL document tree (workflows, sub-workflows, tools, $graph)
    for all input parameters declared in 'cwltool:Secrets'.
    """
    secrets: set[str] = set()

    def _extract_from_section(section: object) -> None:
        """Helper to extract secrets from a requirements or hints section."""
        items: list[object] = []
        if isinstance(section, list):
            items = section
        elif isinstance(section, dict):
            for name, val in section.items():
                if isinstance(val, dict):
                    items.append({"class": name, **val})
                else:
                    items.append({"class": name})

        for item in items:
            if isinstance(item, dict) and item.get("class") == "cwltool:Secrets":
                secret_list = item.get("secrets", [])
                if isinstance(secret_list, list):
                    secrets.update(str(s) for s in secret_list)

    def _traverse(node: object) -> None:
        if isinstance(node, dict):
            # Check requirements and hints at the current node level
            _extract_from_section(node.get("requirements"))
            _extract_from_section(node.get("hints"))

            # Recurse into dict values (handles 'steps', inline 'run' objects, etc.)
            for value in node.values():
                _traverse(value)

        elif isinstance(node, list):
            # Recurse into list items (handles '$graph', steps array, requirement lists)
            for item in node:
                _traverse(item)

    _traverse(cwl_data)
    return sorted(secrets)
