import sqlite3
import json

db_path = r'RegistroOS/registrooficial/backend/registroos_new.db'

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Find the ID for OS 12345
cur.execute("SELECT id FROM ordens_servico WHERE os_numero = '12345'")
os_id = cur.fetchone()
if not os_id:
    print("No OS found")
else:
    os_id = os_id[0]
    print(f"OS ID: {os_id}")

    # Update to JSON
    new_json = json.dumps({"Mecânica": 8.5})
    cur.execute("UPDATE ordens_servico SET horas_orcadas = ? WHERE id = ?", (new_json, os_id))
    conn.commit()
    print(f"Updated OS {os_id} with: {new_json}")

    # Verify
    cur.execute("SELECT horas_orcadas FROM ordens_servico WHERE id = ?", (os_id,))
    result = cur.fetchone()[0]
    print(f"Stored: {result}")
    print(f"Parsed: {json.loads(result)}")

conn.close()
