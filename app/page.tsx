import Link from "next/link";
import { LESSON_TITLES, ALL_LESSON_NUMS } from "@/lib/lessonTitles";
import fs from "fs";
import path from "path";

// public/data/E{num}.json が存在するレッスンだけ「利用可能」として扱う
function getAvailableLessons(): Set<string> {
  const dataDir = path.join(process.cwd(), "public", "data");
  const available = new Set<string>();
  if (fs.existsSync(dataDir)) {
    for (const num of ALL_LESSON_NUMS) {
      if (fs.existsSync(path.join(dataDir, `E${num}.json`))) {
        available.add(num);
      }
    }
  }
  return available;
}

export default function HomePage() {
  const available = getAvailableLessons();

  return (
    <div
      style={{
        maxWidth: 720,
        margin: "0 auto",
        padding: "28px 20px 60px",
      }}
    >
      <h1
        style={{
          fontFamily: "Georgia, 'Times New Roman', serif",
          fontSize: 22,
          borderBottom: "2px solid var(--ink)",
          paddingBottom: 12,
          margin: "0 0 6px",
        }}
      >
        速読英単語 入門編 — シャドーイング
      </h1>
      <div
        style={{
          fontSize: 12,
          color: "var(--ink-soft)",
          marginBottom: 22,
        }}
      >
        全68レッスン ・ タップして再生 ・ グレーアウトは未公開
      </div>

      <div>
        {ALL_LESSON_NUMS.map((num) => {
          const [title, category] = LESSON_TITLES[num];
          const isAvailable = available.has(num);
          const content = (
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "34px 1fr auto",
                alignItems: "center",
                gap: 12,
                padding: "11px 8px",
                borderBottom: "1px solid var(--paper-line)",
                opacity: isAvailable ? 1 : 0.4,
              }}
            >
              <div
                style={{
                  fontFamily: "Georgia, serif",
                  fontSize: 12,
                  color: "var(--ink-soft)",
                  textAlign: "right",
                }}
              >
                {num}
              </div>
              <div
                style={{
                  fontFamily: "Georgia, 'Times New Roman', serif",
                  fontSize: 16,
                }}
              >
                {title}
              </div>
              <div
                style={{
                  fontSize: 10,
                  color: "white",
                  background: isAvailable ? "var(--accent)" : "var(--ink-soft)",
                  borderRadius: 10,
                  padding: "3px 9px",
                  whiteSpace: "nowrap",
                }}
              >
                {category}
              </div>
            </div>
          );

          return isAvailable ? (
            <Link
              key={num}
              href={`/lesson/${num}`}
              style={{ textDecoration: "none" }}
            >
              {content}
            </Link>
          ) : (
            <div key={num}>{content}</div>
          );
        })}
      </div>
    </div>
  );
}
