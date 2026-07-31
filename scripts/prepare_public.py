# -*- coding: utf-8 -*-
"""
Whisperの生データ(mp3 + JSON)を、Next.jsプロジェクトの
public/audio/<PACK_ID>/, public/data/<PACK_ID>/ 用に変換・配置するスクリプト。
新しい教材セット(パック)を追加するたびに、PACK_ID・SOURCE_DIR・FILE_PREFIXを
書き換えて実行する想定。

前提:
  SOURCE_DIR に、文字起こし済みの
    <FILE_PREFIX>01.mp3 / .json 〜 <FILE_PREFIX>NN.mp3 / .json
  が揃っていること (transcribe_pack.py で生成したもの)

使い方:
  1. 下の PACK_ID / SOURCE_DIR / FILE_PREFIX を書き換える
  2. プロジェクトルートで実行:
       python scripts/prepare_public.py
"""

import json
import os
import re
import shutil
import glob

# ==== ここを毎回書き換える ====
PACK_ID = "sokutan-nyumon"
SOURCE_DIR = r"C:\Users\terfe\Downloads\新しいフォルダー"   # ← mp3とjsonが実際にあるフォルダに書き換え
FILE_PREFIX = "sokutan-nyumon_reibun-E"
# ================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_OUT = os.path.join(PROJECT_ROOT, "public", "audio", PACK_ID)
DATA_OUT = os.path.join(PROJECT_ROOT, "public", "data", PACK_ID)


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
        print(f"[エラー] {SOURCE_DIR} にJSONファイルが見つかりません。SOURCE_DIR/FILE_PREFIXを確認してください。")
        return

    done = 0
    for json_path in json_files:
        base = os.path.splitext(os.path.basename(json_path))[0]
        m = re.search(r"(\d+)$", base)
        if not m:
            continue
        num = m.group(1).zfill(2)

        mp3_path = os.path.join(SOURCE_DIR, f"{FILE_PREFIX}{num}.mp3")
        if not os.path.exists(mp3_path):
            print(f"[スキップ] {num}: mp3が見つかりません")
            continue

        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
        segments = simplify_segments(data)

        with open(os.path.join(DATA_OUT, f"E{num}.json"), "w", encoding="utf-8") as f:
            json.dump(segments, f, ensure_ascii=False)

        shutil.copyfile(mp3_path, os.path.join(AUDIO_OUT, f"E{num}.mp3"))

        print(f"[完了] {PACK_ID} E{num}")
        done += 1

    print(f"\n合計 {done} レッスン分を public/audio/{PACK_ID}, public/data/{PACK_ID} に配置しました。")


if __name__ == "__main__":
    main()
