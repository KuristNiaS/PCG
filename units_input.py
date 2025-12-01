import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import json
import os
from pathlib import Path

# ==========================================
# 数据库配置（跨平台路径）
# ==========================================

DB_PATH = Path(__file__).parent / "data" / "cards" / "eff" / "cards.db"

def init_db():
    # 创建目录（跨平台兼容）
    db_dir = DB_PATH.parent
    os.makedirs(db_dir, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS card (
            id TEXT PRIMARY KEY,
            name TEXT,
            series TEXT,
            color TEXT,  -- 属性（物理/冰/火/雷/暗/无）
            category TEXT,
            rarity TEXT,
            eff TEXT,
            cost INTEGER,
            PP INTEGER,
            DP INTEGER
        )
    """)
    conn.commit()
    conn.close()


def insert_card(data):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO card
            (id, name, series, color, category, rarity, eff, cost, PP, DP)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["id"], data["name"], data["series"], data["color"],
            data["category"], data["rarity"], data["eff"], data["cost"],
            data["PP"], data["DP"]
        ))
        conn.commit()
    except sqlite3.Error as e:
        messagebox.showerror("数据库错误", f"保存失败：{str(e)}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()


def fetch_all_cards():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, name, series, color, category, rarity, eff, cost, PP, DP
        FROM card ORDER BY id
    """)
    rows = c.fetchall()
    conn.close()
    return rows


def delete_card(cid):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM card WHERE id=?", (cid,))
        conn.commit()
    except sqlite3.Error as e:
        messagebox.showerror("数据库错误", f"删除失败：{str(e)}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()


# ==========================================
# GUI 主程序
# ==========================================

class CardManagerApp:

    CATEGORY_OPTIONS = ["升变", "战术", "普通", "瞬时", "装备", "角色", "道具", "辅助机"]
    RARITY_OPTIONS = ["C", "R", "U", "SR", "ST"]
    SERIES_OPTIONS = ["BP01", "ST01", "ST02", "ST03", "ST04"]
    COLOR_OPTIONS = ["物理", "冰", "火", "雷", "暗", "无"]  # 属性添加“无”选项

    def __init__(self, root):
        self.root = root
        root.title("PCG 卡查工具")
        root.geometry("1100x650")

        self.selected_card_id = None

        # 主布局
        main_frame = ttk.Frame(root)
        main_frame.grid(row=0, column=0, sticky="nsew")
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        left_frame = ttk.Frame(main_frame, width=380, padding=8)
        left_frame.grid(row=0, column=0, sticky="ns")

        right_frame = ttk.Frame(main_frame, padding=8)
        right_frame.grid(row=0, column=1, sticky="nsew")
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # 左侧分两列：输入栏 + 按钮栏
        entries_col = ttk.Frame(left_frame)
        entries_col.grid(row=0, column=0, sticky="nw")

        buttons_col = ttk.Frame(left_frame)
        buttons_col.grid(row=0, column=1, sticky="ne", padx=8)

        # 数据绑定变量
        self.vars = {
            "id": tk.StringVar(),
            "name": tk.StringVar(),
            "series": tk.StringVar(),
            "color": tk.StringVar(),  # 属性
            "eff": tk.StringVar(),
            "cost": tk.IntVar(value=0),
            "PP": tk.IntVar(value=0),
            "DP": tk.IntVar(value=0),
            "category": tk.StringVar(),
            "rarity": tk.StringVar()
        }

        # 输入框布局（移除颜色输入框，改为按钮）
        ENTRY_W = 28
        rowi = 0

        for label, key in [
            ("卡牌 ID *", "id"),
            ("卡牌名称", "name"),
            ("效果", "eff"),
            ("费用", "cost"),
            ("PP 值", "PP"),
            ("DP 值", "DP")
        ]:
            ttk.Label(entries_col, text=label).grid(row=rowi, column=0, sticky="w", pady=2)
            rowi += 1
            ttk.Entry(entries_col, textvariable=self.vars[key], width=ENTRY_W).grid(row=rowi, column=0, pady=2)
            rowi += 1

        # 按钮样式
        BTN_W = 12
        BTN_PADX = 4
        BTN_PADY = 4

        # ======================================
        # 类别按钮（可多选）
        # ======================================
        frm_cat = ttk.LabelFrame(buttons_col, text="卡牌类别（可多选）", padding=6)
        frm_cat.grid(row=0, column=0, sticky="n", pady=4)

        self._default_btn_bg = None
        self._cat_buttons = []

        def toggle_category(value, btn):
            current = self.vars["category"].get().split("/") if self.vars["category"].get() else []
            if value in current:
                current.remove(value)
                btn.config(relief="raised", bg=self._default_btn_bg)
            else:
                current.append(value)
                btn.config(relief="sunken", bg="#cfe8ff")
            self.vars["category"].set("/".join(current))

        r = 0
        for i, cat in enumerate(self.CATEGORY_OPTIONS):
            btn = tk.Button(frm_cat, text=cat, width=BTN_W)
            btn.grid(row=r, column=i % 2, padx=BTN_PADX, pady=BTN_PADY)
            if self._default_btn_bg is None:
                self._default_btn_bg = btn.cget("background")
            btn.config(command=lambda v=cat, b=btn: toggle_category(v, b))
            self._cat_buttons.append((cat, btn))
            if i % 2 == 1:
                r += 1

        # ======================================
        # 稀有度按钮（单选）
        # ======================================
        frm_rarity = ttk.LabelFrame(buttons_col, text="稀有度", padding=6)
        frm_rarity.grid(row=1, column=0, sticky="n", pady=4)

        self._rar_buttons = []

        def pick_rarity(v, btn):
            self.vars["rarity"].set(v)
            for _, b in self._rar_buttons:
                b.config(relief="raised", bg=self._default_btn_bg)
            btn.config(relief="sunken", bg="#ffd9a6")

        r = 0
        for i, rty in enumerate(self.RARITY_OPTIONS):
            btn = tk.Button(frm_rarity, text=rty, width=8)
            btn.grid(row=r, column=i % 3, padx=BTN_PADX, pady=BTN_PADY)
            btn.config(command=lambda v=rty, b=btn: pick_rarity(v, b))
            self._rar_buttons.append((rty, btn))
            if i % 3 == 2:
                r += 1

        # ======================================
        # 属性按钮（单选，包含“无”）
        # ======================================
        frm_color = ttk.LabelFrame(buttons_col, text="属性", padding=6)
        frm_color.grid(row=2, column=0, sticky="n", pady=4)

        self._color_buttons = []

        def pick_color(v, btn):
            self.vars["color"].set(v)
            for _, b in self._color_buttons:
                b.config(relief="raised", bg=self._default_btn_bg)
            btn.config(relief="sunken", bg="#ffcccc")

        r = 0
        for i, color in enumerate(self.COLOR_OPTIONS):
            btn = tk.Button(frm_color, text=color, width=8)
            btn.grid(row=r, column=i % 3, padx=BTN_PADX, pady=BTN_PADY)
            btn.config(command=lambda v=color, b=btn: pick_color(v, b))
            self._color_buttons.append((color, btn))
            if i % 3 == 2:
                r += 1

        # ======================================
        # 系列按钮（单选，必填）
        # ======================================
        frm_series = ttk.LabelFrame(buttons_col, text="系列 *（必填）", padding=6)
        frm_series.grid(row=3, column=0, sticky="n", pady=4)

        self._series_buttons = []

        def pick_series(v, btn):
            self.vars["series"].set(v)
            for _, b in self._series_buttons:
                b.config(relief="raised", bg=self._default_btn_bg)
            btn.config(relief="sunken", bg="#d1ffd1")

        r = 0
        for i, series in enumerate(self.SERIES_OPTIONS):
            btn = tk.Button(frm_series, text=series, width=BTN_W)
            btn.grid(row=r, column=i % 2, padx=BTN_PADX, pady=BTN_PADY)
            btn.config(command=lambda v=series, b=btn: pick_series(v, b))
            self._series_buttons.append((series, btn))
            if i % 2 == 1:
                r += 1

        # 操作按钮
        op_frame = ttk.Frame(entries_col)
        op_frame.grid(row=rowi, column=0, pady=8)
        ttk.Button(op_frame, text="保存/更新", command=self.save_card).grid(row=0, column=0, padx=4)
        ttk.Button(op_frame, text="清空", command=self.clear_form).grid(row=0, column=1, padx=4)
        ttk.Button(op_frame, text="导出 JSON", command=self.export_json).grid(row=0, column=2, padx=4)

        # ======================================
        # 右侧列表
        # ======================================
        ttk.Label(right_frame, text="已保存卡牌（点击编辑）").grid(row=0, column=0, sticky="w")

        self.listbox = tk.Listbox(right_frame)
        self.listbox.grid(row=1, column=0, sticky="nsew", pady=6)
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        btns = ttk.Frame(right_frame)
        btns.grid(row=2, column=0, sticky="w")
        ttk.Button(btns, text="删除选中", command=self.delete_selected).grid(row=0, column=0, padx=4)
        ttk.Button(btns, text="刷新", command=self.load_list).grid(row=0, column=1, padx=4)

        self.load_list()

    # ==========================================
    # 表单数据处理
    # ==========================================

    def get_form_data(self):
        return {
            "id": self.vars["id"].get().strip(),
            "name": self.vars["name"].get().strip(),
            "series": self.vars["series"].get().strip(),
            "color": self.vars["color"].get().strip(),
            "category": self.vars["category"].get().strip(),
            "rarity": self.vars["rarity"].get().strip(),
            "eff": self.vars["eff"].get().strip(),
            "cost": self.vars["cost"].get(),
            "PP": self.vars["PP"].get(),
            "DP": self.vars["DP"].get()
        }

    def save_card(self):
        data = self.get_form_data()
        
        # 验证必填项
        if not data["id"]:
            messagebox.showerror("错误", "卡牌ID不能为空！")
            return
        if not data["series"]:
            messagebox.showerror("错误", "系列不能为空！请从按钮选择系列")
            return
        
        # 自动拼接最终ID
        final_id = f"{data['series']}-{data['id']}"
        data["id"] = final_id

        insert_card(data)
        messagebox.showinfo("成功", f"卡牌 {final_id} 已保存/更新")
        self.load_list()

    def clear_form(self):
        for k, v in self.vars.items():
            try:
                if k in ["cost", "PP", "DP"]:
                    v.set(0)
                else:
                    v.set("")
            except:
                pass

        # 清空所有按钮状态
        for _, btn in self._cat_buttons:
            btn.config(relief="raised", bg=self._default_btn_bg)
        for _, btn in self._rar_buttons:
            btn.config(relief="raised", bg=self._default_btn_bg)
        for _, btn in self._color_buttons:
            btn.config(relief="raised", bg=self._default_btn_bg)
        for _, btn in self._series_buttons:
            btn.config(relief="raised", bg=self._default_btn_bg)

        self.selected_card_id = None

    # ==========================================
    # 列表操作
    # ==========================================

    def load_list(self):
        self.listbox.delete(0, tk.END)
        rows = fetch_all_cards()
        self._rows = rows

        for r in rows:
            # 显示属性（包括“无”）
            display = f"{r[0]} | {r[1]} [{r[3]}属性] [{r[4]}] ({r[5]}) cost:{r[7]} PP:{r[8]} DP:{r[9]}"
            self.listbox.insert(tk.END, display)

    def on_select(self, evt):
        if not self.listbox.curselection():
            return

        i = self.listbox.curselection()[0]
        row = self._rows[i]

        # 分解ID
        card_id = row[0]
        numeric_id = card_id.split("-")[1] if "-" in card_id else card_id

        # 填充表单
        self.vars["id"].set(numeric_id)
        self.vars["name"].set(row[1])
        self.vars["series"].set(row[2])
        self.vars["color"].set(row[3])
        self.vars["category"].set(row[4])
        self.vars["rarity"].set(row[5])
        self.vars["eff"].set(row[6])
        self.vars["cost"].set(row[7])
        self.vars["PP"].set(row[8])
        self.vars["DP"].set(row[9])

        self.selected_card_id = row[0]

        # 恢复按钮选中状态
        # 类别按钮
        selected_cats = row[4].split("/") if row[4] else []
        for cat, btn in self._cat_buttons:
            btn.config(relief="sunken" if cat in selected_cats else "raised",
                       bg="#cfe8ff" if cat in selected_cats else self._default_btn_bg)
        
        # 稀有度按钮
        for rty, btn in self._rar_buttons:
            btn.config(relief="sunken" if rty == row[5] else "raised",
                       bg="#ffd9a6" if rty == row[5] else self._default_btn_bg)
        
        # 属性按钮（包含“无”的选中状态）
        for color, btn in self._color_buttons:
            btn.config(relief="sunken" if color == row[3] else "raised",
                       bg="#ffcccc" if color == row[3] else self._default_btn_bg)
        
        # 系列按钮
        for series, btn in self._series_buttons:
            btn.config(relief="sunken" if series == row[2] else "raised",
                       bg="#d1ffd1" if series == row[2] else self._default_btn_bg)

    def delete_selected(self):
        if not self.selected_card_id:
            messagebox.showwarning("提示", "请先选择要删除的卡牌")
            return
        
        if messagebox.askyesno("确认删除", f"确定要删除卡牌 {self.selected_card_id} 吗？"):
            delete_card(self.selected_card_id)
            self.load_list()
            self.clear_form()

    # ==========================================
    # JSON导出
    # ==========================================

    def export_json(self):
        rows = fetch_all_cards()
        if not rows:
            messagebox.showinfo("提示", "暂无卡牌数据可导出")
            return
        
        cards = []
        keys = ["id", "name", "series", "color", "category", "rarity", "eff", "cost", "PP", "DP"]
        
        for r in rows:
            card_data = dict(zip(keys, r))
            card_data["image_path"] = f"images/{card_data['id']}.png"
            cards.append(card_data)

        try:
            with open("cards.json", "w", encoding="utf8") as f:
                json.dump(cards, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("成功", f"已导出 {len(cards)} 张卡牌数据到 cards.json")
        except Exception as e:
            messagebox.showerror("导出失败", f"导出失败：{str(e)}")


# ==========================================
# 程序入口
# ==========================================

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = CardManagerApp(root)
    root.mainloop()