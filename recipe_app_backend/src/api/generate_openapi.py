"""Generate OpenAPI spec into openapi.json (used by manifest generateOpenapiCommand)."""

import json
from pathlib import Path

from src.api.main import app


# PUBLIC_INTERFACE
def main() -> None:
    """Generate and write the OpenAPI schema to openapi.json at repository root."""
    schema = app.openapi()
    out_path = Path(__file__).resolve().parents[3] / "openapi.json"
    out_path.write_text(json.dumps(schema, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
