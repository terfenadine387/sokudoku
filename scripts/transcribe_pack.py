# -*- coding: utf-8 -*-
"""
新しい音声セット(パック)を一括で文字起こしするスクリプト。
既存の run_all.py の文字起こし部分を汎用化したもの
(HTML生成は行わない。Next.js版では prepare_public.py が代わりを担う)。

使い方:
  1. 下の設定を書き換える
  2. 対象フォルダ(SOURCE_DIR)に <FILE_PREFIX>01.mp3 〜 <FILE_PREFIX>{TOTAL_LESSONS}.mp3 を置く
  3. 実行:
       python scripts/transcribe_pack.py

  既にJSONがあるレッスンは自動でスキップされるので、
  追加収録した分だけ後から回しても大丈夫です。

初回のみ: pip install openai-whisper
"""

import json
import os
import time

# ==== ここを毎回書き換える ====
SOURCE_DIR = r"C:\Users\terfe\Downloads\新しいフォルダー"
FILE_PREFIX = "sokutan-nyumon_reibun-E"
TOTAL_LESSONS = 68
LANGUAGE = "en"          # 音声の言語 (英語なら "en")
MODEL_SIZE = "small"     # tiny / small / medium
# ================================


def main():
    import whisper

    print(f"Whisperモデル ({MODEL_SIZE}) を読み込み中...")
    model = whisper.load_model(MODEL_SIZE)
    print("モデル読み込み完了。文字起こしを開始します。\n")

    done = skipped = missing = 0

    for i in range(1, TOTAL_LESSONS + 1):
        num = str(i).zfill(2)
        mp3_path = os.path.join(SOURCE_DIR, f"{FILE_PREFIX}{num}.mp3")
        json_path = os.path.join(SOURCE_DIR, f"{FILE_PREFIX}{num}.json")

        if os.path.exists(json_path):
            print(f"[スキップ] {num}: 既にJSONあり")
            skipped += 1
            continue
        if not os.path.exists(mp3_path):
            print(f"[未検出] {num}: {mp3_path} が見つかりません")
            missing += 1
            continue

        t0 = time.time()
        print(f"[処理中] {num}: 文字起こし中...", end=" ", flush=True)
        result = model.transcribe(mp3_path, language=LANGUAGE, word_timestamps=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"完了 ({time.time()-t0:.1f}秒)")
        done += 1

    print(f"\n新規{done}件 / スキップ{skipped}件 / mp3未検出{missing}件")


if __name__ == "__main__":
    main()
