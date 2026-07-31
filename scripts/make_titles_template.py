# -*- coding: utf-8 -*-
"""
新しいパック用の lib/packs/<パックID>.ts テンプレートを自動生成するスクリプト。
タイトル・カテゴリの中身は "TODO" のままなので、後で手作業で埋める必要がある
(教材のタイトルは自分で書き起こす必要があり、自動化できない箇所です)。

使い方:
  1. 下の設定を書き換える
  2. 実行:
       python scripts/make_titles_template.py
  3. 同じフォルダに <PACK_ID>.template.ts が生成される
  4. 中の "TODO" をレッスンごとのタイトル・カテゴリに書き換える
  5. 完成したら lib/packs/<パックID>.ts として保存し、
     lib/packs/index.ts に1行追加する (詳しくは ADD_NEW_PACK.md 参照)
"""

import glob
import os
import re

# ==== ここを書き換える ====
SOURCE_DIR = r"C:\Users\terfe\Downloads\新しいフォルダー2"
FILE_PREFIX = "new-pack-reibun-E"
PACK_ID = "new-pack"            # 英数字・ハイフンのみ推奨
PACK_NAME = "新しい教材名"
# ============================


def main():
    json_files = sorted(glob.glob(os.path.join(SOURCE_DIR, f"{FILE_PREFIX}*.json")))
    nums = []
    for path in json_files:
        base = os.path.splitext(os.path.basename(path))[0]
        m = re.search(r"(\d+)$", base)
        if m:
            nums.append(m.group(1).zfill(2))
    nums = sorted(set(nums), key=lambda x: int(x))

    if not nums:
        print(f"[エラー] {SOURCE_DIR} に {FILE_PREFIX}*.json が見つかりません。")
        return

    lines = []
    lines.append('import { Pack } from "./types";')
    lines.append("")
    lines.append(f"const lessons: Pack[\"lessons\"] = {{")
    for num in nums:
        lines.append(f'  "{num}": ["TODO タイトル{num}", "TODO カテゴリ"],')
    lines.append("};")
    lines.append("")
    lines.append("const pack: Pack = {")
    lines.append(f'  id: "{PACK_ID}",')
    lines.append(f'  name: "{PACK_NAME}",')
    lines.append("  lessons,")
    lines.append("};")
    lines.append("")
    lines.append("export default pack;")

    out_path = f"{PACK_ID}.template.ts"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[完了] {out_path} を生成しました ({len(nums)}レッスン分)")
    print("中身の TODO 部分を実際のタイトル・カテゴリに書き換えてください。")


if __name__ == "__main__":
    main()
