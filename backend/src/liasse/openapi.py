"""Print the OpenAPI schema, used by `make api-client`."""

import json

from liasse.main import create_app
from liasse.settings import Settings

if __name__ == "__main__":
    # The schema doesn't depend on settings; a placeholder URL avoids needing a real database.
    settings = Settings(database_url="postgresql+psycopg://schema@localhost/schema")
    print(json.dumps(create_app(settings).openapi(), indent=2))
