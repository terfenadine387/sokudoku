import "./globals.css";

export const metadata = {
  title: "速読英単語 入門編 - シャドーイング",
  description: "英単語例文シャドーイング練習アプリ",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
