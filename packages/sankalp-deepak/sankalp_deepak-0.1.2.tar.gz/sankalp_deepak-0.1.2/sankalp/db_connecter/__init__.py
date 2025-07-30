from peewee import PostgresqlDatabase
from urllib.parse import urlparse
import os

# Default URI
db_uri = os.getenv("SANKALP_DB_URI", "postgresql://postgres:password@localhost:5432/sankalp_db")
parsed = urlparse(db_uri)

# Extract parts
db = PostgresqlDatabase(
    parsed.path[1:],  # strip leading slash
    user=parsed.username,
    password=parsed.password,
    host=parsed.hostname,
    port=parsed.port
)


# db = SqliteDatabase("sankalp.db")
