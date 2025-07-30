import toml
import snowflake.connector

def load_config(path="config.toml"):
    config = toml.load(path)
    return config["connections"]["my_example_connection"]

def test_snowflake_connection(config):
    try:
        conn = snowflake.connector.connect(
            user=config["user"],
            password=config["password"],
            account=config["account"],
            role=config.get("role", None),
            warehouse=config.get("warehouse", None),
            database=config.get("database", None),
            schema=config.get("schema", None)
        )
        cs = conn.cursor()
        cs.execute("SELECT CURRENT_VERSION()")
        version = cs.fetchone()
        print(f"✅ Connected to Snowflake! Version: {version[0]}")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
    finally:
        try:
            cs.close()
            conn.close()
        except:
            pass

if __name__ == "__main__":
    config = load_config()
    test_snowflake_connection(config)
