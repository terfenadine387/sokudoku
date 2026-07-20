# -*- coding: utf-8 -*-
"""
既存の sokutan-nyumon_reibun-E01.mp3/.json 〜 E68 を、
Next.jsプロジェクトの public/audio, public/data 用に変換・配置するスクリプト。

前提:
  run_all.py (以前のHTML版で使ったスクリプト) で生成した
  sokutan-nyumon_reibun-E01.mp3〜E68.mp3 と E01.json〜E68.json が
  SOURCE_DIR に揃っていること。

使い方:
  1. このファイルの SOURCE_DIR を、mp3/jsonが入っているフォルダの絶対パスに書き換える
  2. プロジェクトのルートで実行:
       python scripts/prepare_public.py
  3. public/audio/E01.mp3... と public/data/E01.json... が生成される
"""

import json
import os
import re
import shutil
import glob

# ここを実際のフォルダパスに書き換えてください
# 例: r"C:\Users\terfe\Downloads\新しいフォルダー"
SOURCE_DIR = r"C:\Users\terfe\Downloads\新しいフォルダー"

FILE_PREFIX = "sokutan-nyumon_reibun-E"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_OUT = os.path.join(PROJECT_ROOT, "public", "audio")
DATA_OUT = os.path.join(PROJECT_ROOT, "public", "data")


def simplify_segments(whisper_json):
    out = []
    for seg in whisper_json["segments"]:
        out.append({
            "start": round(seg["start"], 2),
            "end": round(seg["end"], 2),
            "text": seg["text"].strip(),
            "words": [
                {"w": w["word"].strip(), "s": round(w["start"], 2), "e": round(w["end"], 2)}
                for w in seg.get("words", [])
            ],
        })
    return out


def main():
    os.makedirs(AUDIO_OUT, exist_ok=True)
    os.makedirs(DATA_OUT, exist_ok=True)

    json_files = sorted(glob.glob(os.path.join(SOURCE_DIR, f"{FILE_PREFIX}*.json")))
    if not json_files:
        print(f"[エラー] {SOURCE_DIR} にJSONファイルが見つかりません。SOURCE_DIRを確認してください。")
        return

    done = 0
    for json_path in json_files:
        base = os.path.splitext(os.path.basename(json_path))[0]
        m = re.search(r"E(\d+)", base)
        if not m:
            continue
        num = m.group(1).zfill(2)

        mp3_path = os.path.join(SOURCE_DIR, f"{FILE_PREFIX}{num}.mp3")
        if not os.path.exists(mp3_path):
            print(f"[スキップ] E{num}: mp3が見つかりません")
            continue

        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
        segments = simplify_segments(data)

        data_out_path = os.path.join(DATA_OUT, f"E{num}.json")
        with open(data_out_path, "w", encoding="utf-8") as f:
            json.dump(segments, f, ensure_ascii=False)

        audio_out_path = os.path.join(AUDIO_OUT, f"E{num}.mp3")
        shutil.copyfile(mp3_path, audio_out_path)

        print(f"[完了] E{num}")
        done += 1

    print(f"\n合計 {done} レッスン分を public/audio, public/data に配置しました。")


if __name__ == "__main__":
    main()
