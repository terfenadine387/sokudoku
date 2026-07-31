import Link from "next/link";
import fs from "fs";
import path from "path";
import { PACK_LIST, getLessonNums } from "@/lib/packs";

function getAvailableLessons(packId: string): Set<string> {
  const dataDir = path.join(process.cwd(), "public", "data", packId);
  const available = new Set<string>();
  if (fs.existsSync(dataDir)) {
    for (const num of getLessonNums(packId)) {
      if (fs.existsSync(path.join(dataDir, `E${num}.json`))) {
        available.add(num);
      }
    }
  }
  return available;
}

export default function HomePage() {
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
          margin: "0 0 22px",
        }}
      >
        シャドーイング練習
      </h1>

      {PACK_LIST.map((pack) => {
        const available = getAvailableLessons(pack.id);
        const nums = getLessonNums(pack.id);
        return (
          <section key={pack.id} style={{ marginBottom: 32 }}>
            <h2
              style={{
                fontFamily: "Georgia, 'Times New Roman', serif",
                fontSize: 17,
                margin: "0 0 4px",
              }}
            >
              {pack.name}
            </h2>
            <div style={{ fontSize: 12, color: "var(--ink-soft)", marginBottom: 12 }}>
              全{nums.length}レッスン ・ タップして再生 ・ グレーアウトは未公開
            </div>
            <div>
              {nums.map((num) => {
                const [title, category] = pack.lessons[num];
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
                    href={`/lesson/${pack.id}/${num}`}
                    style={{ textDecoration: "none" }}
                  >
                    {content}
                  </Link>
                ) : (
                  <div key={num}>{content}</div>
                );
              })}
            </div>
          </section>
        );
      })}
    </div>
  );
}
