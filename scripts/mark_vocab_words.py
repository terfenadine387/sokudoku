# -*- coding: utf-8 -*-
"""
public/data/{pack}/E*.json の各単語について、巻末INDEXの単語リスト(vocab_words_list.txt)と
活用形も考慮して突き合わせ、一致した単語に "v": true を付与するスクリプト。

活用形の判定には lemminflect を使用(例: enjoyed→enjoy, opinions→opinion, went→go)。
判定結果はJSONファイルに直接書き込まれるので、フロントエンド側は追加の処理をせずに
そのまま太字表示に使える(高速・オフラインで動作)。

事前準備:
  pip install lemminflect --break-system-packages

使い方:
  python scripts/mark_vocab_words.py sokutan-nyumon
  (全パックまとめて処理したい場合は pack-id を省略)
"""

import json
import os
import re
import sys
import glob

try:
    from lemminflect import getLemma
except ImportError:
    print("lemminflect がインストールされていません。")
    print("先に実行してください: pip install lemminflect --break-system-packages")
    sys.exit(1)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORDLIST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vocab_words_list.txt")

POS_TAGS = ("VERB", "NOUN", "ADJ", "ADV")


def load_vocab_set():
    words = set()
    with open(WORDLIST_PATH, encoding="utf-8") as f:
        for line in f:
            w = line.strip()
            if not w:
                continue
            w = w.lower()
            # "afterward(s)" のような表記は両方の形を登録する
            m = re.match(r"^(.+)\(s\)$", w)
            if m:
                words.add(m.group(1))
                words.add(m.group(1) + "s")
            else:
                words.add(w)
    return words


VOCAB_SET = load_vocab_set()
_lemma_cache = {}


def is_vocab_word(raw_word: str) -> bool:
    cleaned = re.sub(r"^[^a-zA-Z']+|[^a-zA-Z']+$", "", raw_word).lower()
    if not cleaned:
        return False
    if cleaned in VOCAB_SET:
        return True
    if cleaned in _lemma_cache:
        lemmas = _lemma_cache[cleaned]
    else:
        lemmas = set()
        for pos in POS_TAGS:
            lemmas.update(getLemma(cleaned, upos=pos))
        _lemma_cache[cleaned] = lemmas
    return any(l in VOCAB_SET for l in lemmas)


def process_pack(pack_id: str):
    data_dir = os.path.join(PROJECT_ROOT, "public", "data", pack_id)
    if not os.path.isdir(data_dir):
        print(f"[スキップ] {data_dir} が見つかりません")
        return

    json_files = sorted(glob.glob(os.path.join(data_dir, "E*.json")))
    total_words = 0
    total_marked = 0

    for path in json_files:
        with open(path, encoding="utf-8") as f:
            segments = json.load(f)

        for seg in segments:
            for w in seg.get("words", []):
                total_words += 1
                if is_vocab_word(w["w"]):
                    w["v"] = True
                    total_marked += 1
                elif "v" in w:
                    del w["v"]

        with open(path, "w", encoding="utf-8") as f:
            json.dump(segments, f, ensure_ascii=False)

    print(f"[{pack_id}] {len(json_files)}ファイル処理 / {total_marked}/{total_words} 語を太字対象に設定")


def main():
    data_root = os.path.join(PROJECT_ROOT, "public", "data")
    if len(sys.argv) >= 2:
        process_pack(sys.argv[1])
    else:
        if not os.path.isdir(data_root):
            print(f"[エラー] {data_root} が見つかりません。")
            return
        for name in sorted(os.listdir(data_root)):
            if os.path.isdir(os.path.join(data_root, name)):
                process_pack(name)


if __name__ == "__main__":
    main()
