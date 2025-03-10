import sqlite3
import json
from pathlib import Path


def get_db_structure(db_path):
    """Get the structure of a SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    structure = {}
    for table in tables:
        table_name = table[0]
        # Get table info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        # Format column information
        structure[table_name] = [
            {
                "name": col[1],
                "type": col[2],
                "notnull": bool(col[3]),
                "default": col[4],
                "pk": bool(col[5])
            }
            for col in columns
        ]

    conn.close()
    return structure


def count_records():
    """Count records in each table of all databases."""
    base_dir = Path(__file__).parent / 'sqlite'
    counts = {}

    # Process each .sqlite3 file
    for db_file in base_dir.glob('*.sqlite3'):
        db_name = db_file.stem
        conn = sqlite3.connect(str(db_file))
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';")
        tables = cursor.fetchall()

        db_counts = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            db_counts[table_name] = count

        counts[db_name] = db_counts
        conn.close()

    # Print results in a formatted way
    print("\nDatabase Records Count:")
    print("=" * 50)
    for db_name, tables in counts.items():
        print(f"\n{db_name.upper()} database:")
        print("-" * 30)
        for table, count in tables.items():
            print(f"{table}: {count:,} records")

    return counts


def save_db_structures():
    """Save the structure of all SQLite databases to JSON."""
    base_dir = Path(__file__).parent / 'sqlite'
    output = {}

    # Process each .sqlite3 file
    for db_file in base_dir.glob('*.sqlite3'):
        db_name = db_file.stem
        output[db_name] = get_db_structure(str(db_file))

    # Save to JSON file
    output_path = base_dir / 'db_structure.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Database structures have been saved to {output_path}")


if __name__ == "__main__":
    save_db_structures()
    count_records()
