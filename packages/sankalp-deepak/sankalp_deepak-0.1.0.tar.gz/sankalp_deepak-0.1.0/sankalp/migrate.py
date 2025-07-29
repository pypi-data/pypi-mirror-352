import subprocess
import os
import sys

if len(sys.argv) < 2:
    print("Usage: python migrate.py <command> <migration_name>")
    sys.exit(1)

command = sys.argv[1]
# Set the environment variable for the current process
DB_URI = "postgresql://postgres:password@localhost:5432/sankalp_db"

# Ensure the migrations directory exists
if not os.path.exists("migrations"):
    os.makedirs("migrations")

# Create a new migration name
if command == "create":
    migration_name = f"migration_{len(os.listdir('migrations')) + 1:05}"
    # Run the pw_migrate create command
    create_result = subprocess.run(
        [
            "pw_migrate",
            "create",
            "--directory",
            "migrations",
            "--database",
            DB_URI,
            migration_name,
        ],
        capture_output=True,
        text=True,
    )

    if create_result.stdout:
        print("CREATE OUTPUT:")
        print(create_result.stdout)
    if create_result.stderr:
        print("CREATE ERRORS:")
        print(create_result.stderr)

elif command == "migrate":
    migration_name = (
        sys.argv[2]
        if len(sys.argv) > 2
        else f"migration_{len(os.listdir('migrations')):05}"
    )
    # Run the pw_migrate migrate command
    migrate_result = subprocess.run(
        [
            "pw_migrate",
            "migrate",
            "--directory",
            "migrations",
            "--database",
            DB_URI,
            "--name",
            migration_name,
        ],
        capture_output=True,
        text=True,
    )

    if migrate_result.stdout:
        print("MIGRATE OUTPUT:")
        print(migrate_result.stdout)
    if migrate_result.stderr:
        print("MIGRATE ERRORS:")
        print(migrate_result.stderr)
