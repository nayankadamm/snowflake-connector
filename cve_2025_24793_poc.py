import snowflake.connector
import toml

# Load config from TOML
config = toml.load("config.toml")["connections"]["my_example_connection"]

# Connect to Snowflake
conn = snowflake.connector.connect(
    user=config["user"],
    password=config["password"],
    account=config["account"],
    role=config["role"],
    warehouse=config["warehouse"],
    database=config["database"],
    schema=config["schema"]
)

cur = conn.cursor()

def init_users_table():
    cur.execute("CREATE OR REPLACE TABLE users (username STRING, password STRING);")
    cur.execute("DELETE FROM users;")
    cur.execute("INSERT INTO users VALUES ('guest', 'guestpass'), ('admin', 'adminpass');")
    print("[INFO] Dummy users inserted.\n")

def vulnerable_lookup(user_input):
    query = f"SELECT * FROM users WHERE username = '{user_input}'"
    print(f"[DEBUG] Executing: {query}")
    cur.execute(query)
    return cur.fetchall()

# Step 1: Setup dummy users
init_users_table()

# Step 2: Normal user input
print("[TEST] Legitimate user lookup:")
result = vulnerable_lookup("guest")
print("[RESULT]", result)

# Step 3: SQL Injection attempt
print("\n[TEST] SQL Injection attempt:")
payload = "guest' OR '1'='1"
result = vulnerable_lookup(payload)
print("[RESULT]", result)

cur.close()
conn.close()
