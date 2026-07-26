from sqlalchemy import text

from app.db.session import engine


def main() -> None:
    with engine.connect() as connection:
        result = connection.execute(
            text(
                "SELECT VERSION() AS version, "
                "DATABASE() AS database_name, "
                "@@session.time_zone AS time_zone"
            )
        )
        row = result.mappings().one()

    print(f"MySQL version: {row['version']}")
    print(f"Database: {row['database_name']}")
    print(f"Session time zone: {row['time_zone']}")
    print("Database connection succeeded")


if __name__ == "__main__":
    main()
