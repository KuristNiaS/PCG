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

from typing import Optional
from fastapi import Query

@app.get("/api/search")
def search(
    q: Optional[str] = None,
    series: Optional[str] = None,
    color: Optional[str] = None,
    min_cost: Optional[int] = None,
    max_cost: Optional[int] = None,
    min_PP: Optional[int] = None,
    max_PP: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    db=Depends(get_db)
):
    sql = "SELECT id, name, color, eff, cost, PP, DP, image_url FROM card"
    where = []
    params = []
    if q:
        where.append("(name LIKE ? OR eff LIKE ?)")
        qlike = f"%{q}%"
        params.extend([qlike, qlike])
    if series:
        where.append("series = ?")
        params.append(series)
    if color:
        where.append("color = ?")
        params.append(color)
    if min_cost is not None:
        where.append("cost >= ?"); params.append(min_cost)
    if max_cost is not None:
        where.append("cost <= ?"); params.append(max_cost)
    if min_PP is not None:
        where.append("PP >= ?"); params.append(min_PP)
    if max_PP is not None:
        where.append("PP <= ?"); params.append(max_PP)

    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    c = db.cursor()
    c.execute(sql, params)
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
