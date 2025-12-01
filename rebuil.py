# migrate_add_columns.py
import sqlite3, os, shutil

DB = "data/cards/eff/cards.db"

# 备份（再次）
bak = DB + ".bak"
if not os.path.exists(bak):
    shutil.copy2(DB, bak)
    print("Backup created:", bak)
else:
    print("Backup already exists:", bak)

conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("PRAGMA table_info(card);")
existing = [row[1] for row in c.fetchall()]
print("Existing columns:", existing)

to_add = [
    ("series", "TEXT"),
    ("category", "TEXT"),
    ("rarity", "TEXT"),
    ("product_series", "TEXT"),
    ("image_url", "TEXT")
]

added = []
for name, dtype in to_add:
    if name not in existing:
        sql = f"ALTER TABLE card ADD COLUMN {name} {dtype};"
        print("Executing:", sql)
        c.execute(sql)
        added.append(name)
    else:
        print("Already has column:", name)

conn.commit()
conn.close()
print("Migration complete. Added:", added)
