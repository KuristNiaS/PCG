# tcg_card_manager.py
# 依赖：Python 标准库（tkinter, sqlite3, json）
# 运行：python tcg_card_manager.py

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import json
import os

DB_PATH = "data/cards/eff/cards.db"

# ---------- 数据库部分 ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS card (
        id TEXT PRIMARY KEY,
        name TEXT,
        color TEXT,
        eff TEXT,
        cost INTEGER,
        PP INTEGER,
        DP INTEGER
    )
    ''')
    conn.commit()
    conn.close()

def insert_card(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO card (id, name, color, eff, cost, PP, DP)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (data['id'], data['name'], data['color'], data['eff'], data['cost'], data['PP'], data['DP']))
    conn.commit()
    conn.close()

def update_card(selected_card_id,data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE card
        SET id=?, name=?, color=?, eff=?, cost=?, PP=?, DP=?
        WHERE id=?
    ''', (data['id'], data['name'], data['color'], data['eff'], data['cost'], data['PP'], data['DP'], selected_card_id))
    conn.commit()
    conn.close()

def delete_card(card_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM card WHERE id=?', (card_id,))
    conn.commit()
    conn.close()

def fetch_all_cards():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, name, color, eff, cost, PP, DP FROM card ORDER BY id DESC')
    rows = c.fetchall()
    conn.close()
    return rows

# ---------- GUI 部分 ----------
class CardManagerApp:
    def __init__(self, root):
        self.root = root
        root.title("PCG 卡查")
        root.geometry("900x500")
        self.selected_card_id = None

        # 左侧：表单
        frm_form = ttk.Frame(root, padding=12)
        frm_form.pack(side=tk.LEFT, fill=tk.Y)

        # 字段
        self.vars = {
            'id': tk.StringVar(),
            'name': tk.StringVar(),
            'color': tk.StringVar(),
            'eff': tk.StringVar(),
            'cost': tk.IntVar(),
            'PP': tk.IntVar(),
            'DP': tk.IntVar()
        }

        ttk.Label(frm_form, text="卡牌id *").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frm_form, textvariable=self.vars['id'], width=40).grid(row=1, column=0, pady=2)

        ttk.Label(frm_form, text="卡牌名称").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frm_form, textvariable=self.vars['name'], width=40).grid(row=3, column=0, pady=2)

        ttk.Label(frm_form, text="颜色").grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frm_form, textvariable=self.vars['color'], width=40).grid(row=5, column=0, pady=2)

        ttk.Label(frm_form, text="效果").grid(row=6, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frm_form, textvariable=self.vars['eff'], width=40).grid(row=7, column=0, pady=2)

        ttk.Label(frm_form, text="费用").grid(row=8, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frm_form, textvariable=self.vars['cost'], width=40).grid(row=9, column=0, pady=2)

        ttk.Label(frm_form, text="PP值").grid(row=10, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frm_form, textvariable=self.vars['PP'], width=40).grid(row=11, column=0, pady=2)

        ttk.Label(frm_form, text="DP值").grid(row=12, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frm_form, textvariable=self.vars['DP'], width=40).grid(row=13, column=0, pady=2)

        # 按钮
        frm_buttons = ttk.Frame(frm_form)
        frm_buttons.grid(row=14, column=0, pady=8, sticky=tk.W)

        ttk.Button(frm_buttons, text="保存/更新", command=self.save_card).grid(row=0, column=0, padx=4)
        ttk.Button(frm_buttons, text="清空表单", command=self.clear_form).grid(row=0, column=1, padx=4)
        ttk.Button(frm_buttons, text="导出为 JSON", command=self.export_json).grid(row=0, column=2, padx=4)

        # 右侧：列表显示
        frm_list = ttk.Frame(root, padding=12)
        frm_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(frm_list, text="已保存的卡牌（选中可编辑/删除）").pack(anchor=tk.W)
        self.listbox = tk.Listbox(frm_list, height=20)
        self.listbox.pack(fill=tk.BOTH, expand=True, pady=6)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        frm_list_btn = ttk.Frame(frm_list)
        frm_list_btn.pack(anchor=tk.W, pady=6)
        ttk.Button(frm_list_btn, text="删除选中卡牌", command=self.delete_selected).grid(row=0, column=0, padx=6)
        ttk.Button(frm_list_btn, text="刷新列表", command=self.load_list).grid(row=0, column=1, padx=6)

        # 载入数据
        self.load_list()

    def get_form_data(self):
        return {
            'id': self.vars['id'].get().strip(),
            'name': self.vars['name'].get().strip(),
            'color': self.vars['color'].get().strip(),
            'eff': self.vars['eff'].get().strip(),
            'cost': self.vars['cost'].get(),
            'PP': self.vars['PP'].get(),
            'DP': self.vars['DP'].get()
        }

    def set_form_data(self, data):
        self.vars['id'].set(data.get('id', ''))
        self.vars['name'].set(data.get('name', ''))
        self.vars['color'].set(data.get('color', ''))
        self.vars['eff'].set(data.get('cost', ''))
        self.vars['cost'].set(data.get('cost', ''))
        self.vars['PP'].set(data.get('PP', ''))
        self.vars['DP'].set(data.get('DP', ''))

    def clear_form(self):
        self.selected_card_id = None
        for v in self.vars.values():
            v.set('')
        self.listbox.selection_clear(0, tk.END)

    def save_card(self):
        data = self.get_form_data()
        if not data['id']:
            messagebox.showwarning("缺少id", "id为必填项")
            return

        if self.selected_card_id is None:
            insert_card(data)
            messagebox.showinfo("已保存", f"id：{data['id']} 卡牌「{data['name']}」已添加")
        else:
            update_card(self.selected_card_id, data)
            messagebox.showinfo("已更新", f"id：{data['id']} 卡牌「{data['name']}」已更新")

        self.load_list()
        self.clear_form()

    def load_list(self):
        self.listbox.delete(0, tk.END)
        rows = fetch_all_cards()
        self._rows = rows
        for r in rows:
            display = f"{r[0]} | {r[1]} [{r[2]}] 「{r[3]}」 ({r[4]}) {r[5]}/{r[6]}"
            self.listbox.insert(tk.END, display)

    def on_select(self, evt):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        row = self._rows[idx]
        self.selected_card_id = row[0]
        data = {
            'id': row[0],
            'name': row[1],
            'color': row[2],
            'eff': row[3],
            'cost': row[4],
            'PP': row[5],
            'DP': row[6]
        }
        self.set_form_data(data)

    def delete_selected(self):
        if self.selected_card_id is None:
            messagebox.showwarning("未选择", "请先从右侧列表中选择要删除的卡牌")
            return
        if messagebox.askyesno("确认删除", "确定删除选中的卡牌吗？此操作无法撤销"):
            delete_card(self.selected_card_id)
            messagebox.showinfo("已删除", f"卡牌 ID={self.selected_card_id} 已删除")
            self.selected_card_id = None
            self.load_list()
            self.clear_form()

    def export_json(self):
        rows = fetch_all_cards()
        cards = []
        for r in rows:
            cards.append({
                'id': r[0],
                'name': r[1],
                'color': r[2],
                'eff': r[3],
                'cost': r[4],
                'PP': r[5],
                'DP': r[6]
            })
        out_path = "cards_export.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(cards, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("导出完成", f"已导出 {len(cards)} 张卡到 {os.path.abspath(out_path)}")

# ---------- 启动 ----------
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = CardManagerApp(root)
    root.mainloop()
