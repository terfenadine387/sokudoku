# -*- coding: utf-8 -*-
"""
文の通し番号と単語リストの通し番号を可能な限り1対1で対応させ、
各文につき「その文が教える対象語彙1語」だけを "v": true にするスクリプト。

単語リストには例文を持たない参考単語が含まれているため、単純な
「N番目の単語=N番目の文」という対応付けはズレてしまう。
そこで、以下のアルゴリズムで自動的に対応付けを行う:

  単語リストの先頭から順に見ていき、
  「今見ている文」にその単語(活用形も含む)が含まれていれば
    → その語を太字にして、単語・文とも次に進める
  含まれていなければ
    → その単語は例文を持たない参考単語とみなしてスキップ(単語だけ次に進める)

処理後、スキップされた単語の一覧と、対応する語が見つからなかった文の一覧を
ログファイル(alignment_report.txt)に出力するので、原著と照らして確認すること。

事前準備:
  pip install lemminflect --break-system-packages

使い方:
  python scripts/align_vocab_words.py sokutan-nyumon
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
_lemma_cache = {}


def get_lemmas(cleaned: str):
    if cleaned in _lemma_cache:
        return _lemma_cache[cleaned]
    lemmas = {cleaned}
    for pos in POS_TAGS:
        lemmas.update(getLemma(cleaned, upos=pos))
    _lemma_cache[cleaned] = lemmas
    return lemmas


def load_vocab_list():
    words = []
    with open(WORDLIST_PATH, encoding="utf-8") as f:
        for line in f:
            w = line.strip()
            if not w:
                continue
            w = w.lower()
            m = re.match(r"^(.+)\(s\)$", w)
            if m:
                words.append(m.group(1))  # 単数形の方を代表として使う
            else:
                words.append(w)
    return words


def lesson_num_key(path):
    m = re.search(r"E(\d+)\.json$", os.path.basename(path))
    return int(m.group(1)) if m else 0


def find_matching_word_index(sentence_words, target):
    """文中の単語リストから、target(見出し語)に一致するもののインデックスを返す。無ければNone。"""
    for idx, w in enumerate(sentence_words):
        cleaned = re.sub(r"^[^a-zA-Z']+|[^a-zA-Z']+$", "", w["w"]).lower()
        if not cleaned:
            continue
        if cleaned == target:
            return idx
        if target in get_lemmas(cleaned):
            return idx
    return None


def main():
    if len(sys.argv) < 2:
        print("使い方: python scripts/align_vocab_words.py <pack-id>")
        return

    pack_id = sys.argv[1]
    data_dir = os.path.join(PROJECT_ROOT, "public", "data", pack_id)
    if not os.path.isdir(data_dir):
        print(f"[エラー] {data_dir} が見つかりません。")
        return

    vocab_list = load_vocab_list()
    json_files = sorted(glob.glob(os.path.join(data_dir, "E*.json")), key=lesson_num_key)

    # 全レッスンの全文を、(ファイルパス, セグメントindex, segmentオブジェクト) のフラットなリストに
    all_data = []  # list of (path, segments_list)
    flat_sentences = []  # list of (data_idx, seg_idx, seg)
    for path in json_files:
        with open(path, encoding="utf-8") as f:
            segments = json.load(f)
        data_idx = len(all_data)
        all_data.append([path, segments])
        for seg_idx, seg in enumerate(segments):
            flat_sentences.append((data_idx, seg_idx))
            # 既存の "v" フラグは一旦すべてクリア
            for w in seg.get("words", []):
                if "v" in w:
                    del w["v"]

    word_ptr = 0
    sent_ptr = 0
    skipped_words = []
    matched_count = 0
    LOOKAHEAD = 15  # 現在の単語から何個先まで探すか(遠くの偶然一致による誤対応を防ぐ)

    def get_seg(idx):
        data_idx, seg_idx = flat_sentences[idx]
        return all_data[data_idx][1][seg_idx]

    unmatched_sent_indices = []

    while word_ptr < len(vocab_list) and sent_ptr < len(flat_sentences):
        seg = get_seg(sent_ptr)
        sentence_words = seg.get("words", [])

        found_offset = None
        found_idx = None
        max_off = min(LOOKAHEAD, len(vocab_list) - word_ptr)
        for offset in range(max_off):
            candidate = vocab_list[word_ptr + offset]
            idx = find_matching_word_index(sentence_words, candidate)
            if idx is not None:
                found_offset = offset
                found_idx = idx
                break

        if found_offset is not None:
            target = vocab_list[word_ptr + found_offset]
            sentence_words[found_idx]["v"] = True
            matched_count += 1
            for skip_i in range(found_offset):
                skipped_words.append((word_ptr + skip_i + 1, vocab_list[word_ptr + skip_i]))
            word_ptr += found_offset
            sent_ptr += 1
            # 同じ単語が次の文にも続けて登場する場合(1語に複数例文があるケース)は
            # 単語ポインタを進めずに同じ語をもう一度その文でも探す
            if sent_ptr < len(flat_sentences):
                next_seg = get_seg(sent_ptr)
                if find_matching_word_index(next_seg.get("words", []), target) is not None:
                    continue
            word_ptr += 1
        else:
            # 近くに対応する単語が見つからない文(締めの挨拶など)は諦めて次の文へ
            unmatched_sent_indices.append(sent_ptr)
            sent_ptr += 1

    while sent_ptr < len(flat_sentences):
        unmatched_sent_indices.append(sent_ptr)
        sent_ptr += 1

    unmatched_sentences = []
    for si in unmatched_sent_indices:
        data_idx, seg_idx = flat_sentences[si]
        path = all_data[data_idx][0]
        unmatched_sentences.append((os.path.basename(path), seg_idx + 1))

    # 書き戻し
    for path, segments in all_data:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(segments, f, ensure_ascii=False)

    # レポート出力
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "alignment_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"文の総数: {len(flat_sentences)}\n")
        f.write(f"単語リストの総数: {len(vocab_list)}\n")
        f.write(f"対応付けできた文: {matched_count}\n")
        f.write(f"例文が無いとみなしてスキップした単語: {len(skipped_words)}\n")
        f.write(f"対応する単語が見つからなかった文: {len(unmatched_sentences)}\n\n")

        f.write("=== スキップした単語(単語リスト内の番号, 単語) ===\n")
        for num, w in skipped_words:
            f.write(f"{num}\t{w}\n")

        f.write("\n=== 対応する単語が見つからなかった文(ファイル, 文番号) ===\n")
        for fname, n in unmatched_sentences:
            f.write(f"{fname}\t{n}文目\n")

    print(f"対応付け完了: {matched_count}文に太字を設定")
    print(f"スキップした単語: {len(skipped_words)}語")
    print(f"未対応の文: {len(unmatched_sentences)}文")
    print(f"詳細は {report_path} を確認してください。")


if __name__ == "__main__":
    main()
