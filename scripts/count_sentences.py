# -*- coding: utf-8 -*-
"""
public/data/{pack}/E01.json 〜 E68.json (レッスン番号順) の文の数を数え、
累積の通し番号を確認するためのスクリプト。

単語リスト(vocab_words_list.txt)の総語数と、実際の例文総数を突き合わせて
ズレが無いかを確認する目的で使う。

使い方:
  python scripts/count_sentences.py sokutan-nyumon
"""

import json
import os
import re
import sys
import glob

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORDLIST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vocab_words_list.txt")


def lesson_num_key(path):
    m = re.search(r"E(\d+)\.json$", os.path.basename(path))
    return int(m.group(1)) if m else 0


def main():
    if len(sys.argv) < 2:
        print("使い方: python scripts/count_sentences.py <pack-id>")
        return

    pack_id = sys.argv[1]
    data_dir = os.path.join(PROJECT_ROOT, "public", "data", pack_id)
    if not os.path.isdir(data_dir):
        print(f"[エラー] {data_dir} が見つかりません。")
        return

    json_files = sorted(glob.glob(os.path.join(data_dir, "E*.json")), key=lesson_num_key)

    total = 0
    print(f"{'レッスン':>8} {'文数':>6} {'累積':>6}")
    for path in json_files:
        with open(path, encoding="utf-8") as f:
            segments = json.load(f)
        n = len(segments)
        total += n
        label = os.path.basename(path).replace(".json", "")
        print(f"{label:>8} {n:>6} {total:>6}")

    print(f"\n例文の総数: {total}")

    if os.path.exists(WORDLIST_PATH):
        with open(WORDLIST_PATH, encoding="utf-8") as f:
            word_count = sum(1 for line in f if line.strip())
        print(f"単語リストの総数: {word_count}")
        print(f"差: {word_count - total} (単語数 - 例文数)")
    else:
        print("(vocab_words_list.txt が見つからないため単語数との比較はスキップ)")


if __name__ == "__main__":
    main()
