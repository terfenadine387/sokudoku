# 新しい音声セット(パック)を追加する手順

このアプリは「パック」という単位で教材を管理しています。
今の「速読英単語 入門編」も1つのパック(id: `sokutan-nyumon`)です。
新しい音声(次のレベルの教材、自作の練習音声など)を追加したいときは、以下の手順で行います。

自動化されているのは「文字起こし」と「ファイル配置」の部分です。
「音声の用意」と「タイトルを書く」部分は手作業が必要です(教材の内容は把握していないと決められないため)。

---

## 手順

### 1. 音声を用意する(手作業)
新しいレッスンのmp3ファイルを、連番で1つのフォルダにまとめる。
ファイル名は好きな接頭辞 + 2桁連番にする。
例: `new-pack-reibun-E01.mp3` 〜 `new-pack-reibun-E30.mp3`

### 2. 文字起こし(スクリプト・ローカルPCで実行)
`scripts/transcribe_pack.py` を開き、上部の設定を書き換える:
```python
SOURCE_DIR = r"C:\Users\terfe\Downloads\新しいフォルダー2"
FILE_PREFIX = "new-pack-reibun-E"
TOTAL_LESSONS = 30
```
実行:
```powershell
python scripts/transcribe_pack.py
```
→ 同じフォルダに `new-pack-reibun-E01.json` 〜 が生成される
(既にJSONがあるレッスンは自動でスキップされるので、追加収録した分だけ後から回しても大丈夫)

### 3. タイトル一覧のテンプレート生成(スクリプト)
`scripts/make_titles_template.py` の設定を書き換えて実行:
```python
SOURCE_DIR = r"C:\Users\terfe\Downloads\新しいフォルダー2"
FILE_PREFIX = "new-pack-reibun-E"
PACK_ID = "new-pack"
PACK_NAME = "新しい教材名"
```
```powershell
python scripts/make_titles_template.py
```
→ `new-pack.template.ts` が生成される(中身は "TODO" のプレースホルダー)

### 4. タイトルを手入力する(手作業・唯一の本質的な手作業)
生成された `.template.ts` を開き、各レッスンの "TODO タイトル" と "TODO カテゴリ" を
実際のレッスン名・カテゴリに書き換える。
※ 教材本文(例文)ではなく、目次に載っているような短いタイトルでOKです。

書き換え後、ファイル名を `new-pack.ts` のように変更し、
プロジェクトの `lib/packs/` フォルダに置く。

### 5. パック一覧に登録する(コード1行追加)
`lib/packs/index.ts` を開き、2箇所を追記:
```ts
import newPack from "./newPack"; // ← 追加

export const PACK_LIST: Pack[] = [
  sokutanNyumon,
  newPack, // ← 追加
];
```

### 6. 音声・データをpublicフォルダに配置(スクリプト)
`scripts/prepare_public.py` の設定を書き換えて実行:
```python
PACK_ID = "new-pack"
SOURCE_DIR = r"C:\Users\terfe\Downloads\新しいフォルダー2"
FILE_PREFIX = "new-pack-reibun-E"
```
```powershell
python scripts/prepare_public.py
```
→ `public/audio/new-pack/`, `public/data/new-pack/` に配置される

### 7. ローカル確認 → デプロイ
```powershell
npm run dev
```
トップページに新しいパックのセクションが増えているか確認。
問題なければ:
```powershell
git add .
git commit -m "feat: 新パック追加 (new-pack)"
git push
```
Vercelが自動で再デプロイします。

---

## まとめ(繰り返す作業)

| 手順 | 自動/手動 |
|---|---|
| 1. 音声収録・整理 | 手動 |
| 2. 文字起こし | スクリプト(`transcribe_pack.py`) |
| 3. タイトルテンプレ生成 | スクリプト(`make_titles_template.py`) |
| 4. タイトル記入 | 手動(唯一の本質的な作業) |
| 5. パック登録 | 手動(2行のコード追加) |
| 6. ファイル配置 | スクリプト(`prepare_public.py`) |
| 7. デプロイ | `git push`(自動デプロイ) |
