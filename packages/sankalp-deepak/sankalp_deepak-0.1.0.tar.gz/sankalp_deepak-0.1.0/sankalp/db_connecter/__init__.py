from peewee import PostgresqlDatabase, SqliteDatabase

db = PostgresqlDatabase(
    "sankalp_db",
    user="postgres",
    password="password",  # optional
    host="localhost",  # optional, defaults to localhost
    port=5432,  # optional, defaults to 5432
)
# db = SqliteDatabase("sankalp.db")
