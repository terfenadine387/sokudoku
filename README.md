# 速読英単語 入門編 シャドーイングアプリ (Next.js + Vercel)

## 概要
E01〜E68の例文シャドーイング練習用アプリ。目次ページ・レッスン再生ページ(文単位ハイライト・単語ハイライト・文リピート・速度調整・前後移動)を含む。

## 事前準備
- Node.js がPCにインストールされていること
- `run_all.py` で生成した以下のファイルが、既存のフォルダ(例: `C:\Users\terfe\Downloads\新しいフォルダー`)に揃っていること
  - `sokutan-nyumon_reibun-E01.mp3` 〜 `E68.mp3`
  - `sokutan-nyumon_reibun-E01.json` 〜 `E68.json`

## セットアップ手順

### 1. 依存パッケージのインストール
プロジェクトのルート(このREADMEがあるフォルダ)で:
```bash
npm install
```

### 2. 音声・データをpublicフォルダに配置
`scripts/prepare_public.py` を開き、`SOURCE_DIR` を実際のmp3/json格納フォルダのパスに書き換える:
```python
SOURCE_DIR = r"C:\Users\terfe\Downloads\新しいフォルダー"
```
書き換えたら実行:
```bash
python scripts/prepare_public.py
```
`public/audio/E01.mp3`〜、`public/data/E01.json`〜 が生成されます。

### 3. ローカルで動作確認
```bash
npm run dev
```
ブラウザで `http://localhost:3000` を開いて確認。

### 4. ビルド確認(念のため)
```bash
npm run build
```
エラーが出なければOK。

## Vercelへのデプロイ手順(既存ワークフローと同じ)

1. このプロジェクトをGitHubリポジトリにpush
   ```bash
   git init
   git add .
   git commit -m "init: shadowing app"
   git branch -M main
   git remote add origin <あなたのGitHubリポジトリURL>
   git push -u origin main
   ```
2. [vercel.com](https://vercel.com) でこのリポジトリをImport
3. Framework Preset は自動で "Next.js" 認識されるはずなので、そのままDeploy
4. デプロイ完了後に発行されるURL(例: `https://sokutan-shadowing.vercel.app`)にiPhoneのSafariでアクセス

普段の開発フロー(featureブランチ → Vercel Preview URL → mainにマージ)もそのまま使えます。

## iPhoneでの使い方
- SafariでデプロイURLを開く
- 共有ボタン → 「ホーム画面に追加」しておくと、アプリのように起動できて便利
- オフライン再生はできません(通信が必要)。オフラインで使いたい場合は、以前作成した「自己完結型HTML版」(`generate_players.py`)を使ってください

## ファイル構成
```
app/
  page.tsx                 目次ページ
  lesson/[num]/page.tsx    レッスンページ(静的生成)
  lesson/[num]/LessonPlayer.tsx  実際の再生UI(クライアント側)
lib/
  lessonTitles.ts           全68レッスンのタイトル・カテゴリ
public/
  audio/E01.mp3 ...         音声(prepare_public.pyで自動配置)
  data/E01.json ...         文字起こしデータ(同上)
scripts/
  prepare_public.py         既存のWhisperデータをpublicへ変換配置
```

## 音声データの容量について
mp3を68本、`public/audio/`に置くことになります(合計で数百MB程度になる見込み)。Vercelの無料枠(Hobby)でも静的アセットとしての配信自体は問題ありませんが、リポジトリサイズやデプロイ時間が気になる場合は、GitHubの代わりに音声だけ外部ストレージ(Cloudflare R2 や Vercel Blobなど)に置く方法もあります。必要であれば案内します。
