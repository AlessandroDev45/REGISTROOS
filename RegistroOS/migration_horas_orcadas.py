import sqlite3
import json

db_path = r'RegistroOS/registrooficial/backend/registroos_new.db'

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Migrate data: if old > 0, set new to {"geral": old}, else '{}'
cur.execute('SELECT id, horas_orcadas_old FROM ordens_servico WHERE horas_orcadas_old IS NOT NULL AND horas_orcadas_old > 0')
rows = cur.fetchall()

migrated_count = 0
for row in rows:
    os_id, old_value = row
    try:
        new_json = json.dumps({"geral": float(old_value)})
        cur.execute('UPDATE ordens_servico SET horas_orcadas = ? WHERE id = ?', (new_json, os_id))
        migrated_count += 1
    except Exception as e:
        print(f"Error migrating OS {os_id}: {e}")

# Set default '{}' for others
cur.execute("UPDATE ordens_servico SET horas_orcadas = '{}' WHERE horas_orcadas IS NULL OR horas_orcadas = '' OR horas_orcadas_old IS NULL OR horas_orcadas_old <= 0")

# Drop old column after migration
cur.execute('ALTER TABLE ordens_servico DROP COLUMN horas_orcadas_old')

conn.commit()
conn.close()

print(f"Migration completed. Updated {migrated_count} records with non-zero old values.")
