import os
from datetime import datetime

# 图片所在目录
folder = r"\frontend\public\images"  # 修改为你的路径

# 允许的图片格式
exts = [".jpg", ".jpeg", ".png", ".bmp", ".webp"]

# 获取所有图片文件
files = [f for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in exts]

# 获取文件完整路径，并按照修改时间排序
files_sorted = sorted(files, key=lambda f: os.path.getmtime(os.path.join(folder, f)))

# 只取最新的42张
latest_42 = files_sorted[-42:]

# 三组命名前缀
prefixes = ["ST01", "ST03", "ST04"]

index = 0
for prefix in prefixes:
    for i in range(14):
        old_name = latest_42[index]
        new_name = f"{prefix}-{i+1:03d}{os.path.splitext(old_name)[1].lower()}"
        os.rename(os.path.join(folder, old_name), os.path.join(folder, new_name))
        index += 1

print("重命名完成！")
