# app.py  --- FastAPI 后端（使用 SQLite）
import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

# 默认数据库路径（可被环境变量 DB_PATH 覆盖）
DEFAULT_DB_PATH = "data/cards/eff/cards.db"
DB_PATH = os.environ.get("DB_PATH", DEFAULT_DB_PATH)

app = FastAPI(title="PCG Card Database API")

# CORS：允许前端访问后端
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发阶段允许所有；生产可限制域名
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库连接
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# ---------------- API ----------------

@app.get("/api/search")
def search(q: str = None, limit: int = 50, db=Depends(get_db)):
    c = db.cursor()
    if q:
        q_like = f"%{q}%"
        c.execute("""
            SELECT id, name, color, eff, cost, PP, DP
            FROM card
            WHERE name LIKE ? OR eff LIKE ? OR color LIKE ?
            LIMIT ?
        """, (q_like, q_like, q_like, limit))
    else:
        c.execute("""
            SELECT id, name, color, eff, cost, PP, DP
            FROM card
            LIMIT ?
        """, (limit,))

    rows = c.fetchall()
    return [dict(r) for r in rows]


@app.get("/api/card/{card_id}")
def get_card(card_id: str, db=Depends(get_db)):
    c = db.cursor()
    c.execute("""
        SELECT id, name, color, eff, cost, PP, DP
        FROM card
        WHERE id = ?
    """, (card_id,))
    r = c.fetchone()

    if not r:
        raise HTTPException(status_code=404, detail="Card not found")

    return dict(r)
