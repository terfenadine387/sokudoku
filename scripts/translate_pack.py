# -*- coding: utf-8 -*-
"""
public/data/{pack}/E*.json の各文に、機械翻訳による日本語訳 ("ja" フィールド) を追加するスクリプト。

注意:
  ここで生成される日本語訳は機械翻訳による独自生成のものです。
  教科書に印刷されている公式の日本語訳とは異なります(表現の質・ニュアンスも異なります)。
  あくまで「意味を素早く確認するための補助」としてお使いください。

事前準備:
  pip install deep-translator --break-system-packages

使い方:
  python scripts/translate_pack.py sokutan-nyumon

  既に "ja" が入っている文はスキップされるので、途中で止めても再実行で続きから処理されます。
"""

import json
import os
import sys
import time
import glob

try:
    from deep_translator import GoogleTranslator
except ImportError:
    print("deep-translator がインストールされていません。")
    print("先に実行してください: pip install deep-translator --break-system-packages")
    sys.exit(1)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    if len(sys.argv) < 2:
        print("使い方: python scripts/translate_pack.py <pack-id>")
        print("例:     python scripts/translate_pack.py sokutan-nyumon")
        return

    pack_id = sys.argv[1]
    data_dir = os.path.join(PROJECT_ROOT, "public", "data", pack_id)

    if not os.path.isdir(data_dir):
        print(f"[エラー] {data_dir} が見つかりません。")
        return

    translator = GoogleTranslator(source="en", target="ja")

    json_files = sorted(glob.glob(os.path.join(data_dir, "E*.json")))
    if not json_files:
        print(f"[エラー] {data_dir} にJSONファイルが見つかりません。")
        return

    total_translated = 0
    total_skipped = 0

    for path in json_files:
        with open(path, encoding="utf-8") as f:
            segments = json.load(f)

        changed = False
        for seg in segments:
            if seg.get("ja"):
                total_skipped += 1
                continue
            try:
                ja = translator.translate(seg["text"])
                seg["ja"] = ja
                changed = True
                total_translated += 1
                time.sleep(0.3)  # 連続リクエストを避けるための小休止
            except Exception as e:
                print(f"[警告] 翻訳失敗: {seg['text'][:30]}... ({e})")

        if changed:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(segments, f, ensure_ascii=False)
            print(f"[完了] {os.path.basename(path)}")

    print(f"\n翻訳: 新規{total_translated}文 / 既存スキップ{total_skipped}文")


if __name__ == "__main__":
    main()
