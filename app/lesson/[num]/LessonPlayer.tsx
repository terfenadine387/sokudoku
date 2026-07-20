"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { LESSON_TITLES, ALL_LESSON_NUMS } from "@/lib/lessonTitles";

type Word = { w: string; s: number; e: number };
type Segment = { start: number; end: number; text: string; words: Word[] };

function fmtTime(t: number) {
  if (!isFinite(t)) return "0:00";
  const m = Math.floor(t / 60);
  const s = Math.floor(t % 60)
    .toString()
    .padStart(2, "0");
  return `${m}:${s}`;
}

export default function LessonPlayer({ num }: { num: string }) {
  const [segments, setSegments] = useState<Segment[] | null>(null);
  const [error, setError] = useState(false);
  const [currentSegIndex, setCurrentSegIndex] = useState(-1);
  const [loopSegIndex, setLoopSegIndex] = useState<number | null>(null);
  const [curTime, setCurTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [rate, setRate] = useState(1.0);

  const audioRef = useRef<HTMLAudioElement>(null);
  const rowRefs = useRef<(HTMLDivElement | null)[]>([]);

  const idx = ALL_LESSON_NUMS.indexOf(num);
  const [title, category] = LESSON_TITLES[num] ?? ["", ""];
  const prevNum = idx > 0 ? ALL_LESSON_NUMS[idx - 1] : null;
  const nextNum = idx < ALL_LESSON_NUMS.length - 1 ? ALL_LESSON_NUMS[idx + 1] : null;

  useEffect(() => {
    setSegments(null);
    setError(false);
    fetch(`/data/E${num}.json`)
      .then((r) => {
        if (!r.ok) throw new Error("not found");
        return r.json();
      })
      .then(setSegments)
      .catch(() => setError(true));
  }, [num]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio || !segments) return;

    function onTimeUpdate() {
      const t = audio!.currentTime;
      setCurTime(t);

      let i = segments!.findIndex((s) => t >= s.start && t < s.end);
      if (i === -1) {
        for (let k = 0; k < segments!.length; k++) {
          if (t < segments![k].start) {
            i = Math.max(0, k - 1);
            break;
          }
        }
        if (i === -1) i = segments!.length - 1;
      }
      setCurrentSegIndex((prev) => {
        if (prev !== i) {
          rowRefs.current[i]?.scrollIntoView({ behavior: "smooth", block: "center" });
        }
        return i;
      });

      if (loopSegIndex !== null) {
        const seg = segments![loopSegIndex];
        if (t >= seg.end || t < seg.start - 0.05) {
          audio!.currentTime = seg.start;
        }
      }
    }
    function onLoadedMetadata() {
      setDuration(audio!.duration);
    }
    function onPlay() {
      setPlaying(true);
    }
    function onPause() {
      setPlaying(false);
    }

    audio.addEventListener("timeupdate", onTimeUpdate);
    audio.addEventListener("loadedmetadata", onLoadedMetadata);
    audio.addEventListener("play", onPlay);
    audio.addEventListener("pause", onPause);
    return () => {
      audio.removeEventListener("timeupdate", onTimeUpdate);
      audio.removeEventListener("loadedmetadata", onLoadedMetadata);
      audio.removeEventListener("play", onPlay);
      audio.removeEventListener("pause", onPause);
    };
  }, [segments, loopSegIndex]);

  function seekTo(t: number) {
    if (audioRef.current) audioRef.current.currentTime = t;
  }

  function togglePlay() {
    const audio = audioRef.current;
    if (!audio) return;
    if (audio.paused) audio.play();
    else audio.pause();
  }

  function toggleLoop(i: number) {
    if (loopSegIndex === i) {
      setLoopSegIndex(null);
    } else {
      setLoopSegIndex(i);
      seekTo(segments![i].start);
      audioRef.current?.play();
    }
  }

  function changeRate(r: number) {
    setRate(r);
    if (audioRef.current) audioRef.current.playbackRate = r;
  }

  if (error) {
    return (
      <div style={{ maxWidth: 720, margin: "0 auto", padding: 24 }}>
        <p>
          E{num} のデータ (/data/E{num}.json) が見つかりません。
          public/data と public/audio にファイルが配置されているか確認してください。
        </p>
        <Link href="/">目次に戻る</Link>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 720, margin: "0 auto", padding: "20px 20px 130px" }}>
      <audio ref={audioRef} src={`/audio/E${num}.mp3`} preload="metadata" />

      {/* トップナビ */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: 14,
        }}
      >
        <NavLink href={prevNum ? `/lesson/${prevNum}` : undefined} label={`← E${prevNum ?? ""}`} />
        <Link
          href="/"
          style={{
            fontSize: 12,
            fontWeight: 700,
            textDecoration: "none",
            color: "var(--ink)",
          }}
        >
          ☰ 目次
        </Link>
        <NavLink href={nextNum ? `/lesson/${nextNum}` : undefined} label={`E${nextNum ?? ""} →`} />
      </div>

      {/* ヘッダー */}
      <div style={{ borderBottom: "2px solid var(--ink)", paddingBottom: 10, marginBottom: 4 }}>
        <div style={{ fontSize: 11, color: "var(--accent)", fontWeight: 700, letterSpacing: "0.08em" }}>
          [{category}]
        </div>
        <h1
          style={{
            fontFamily: "Georgia, 'Times New Roman', serif",
            fontSize: 19,
            fontWeight: 700,
            margin: "4px 0 0",
          }}
        >
          {title}
        </h1>
        <div style={{ fontSize: 12, color: "var(--ink-soft)" }}>E{num} ・ 速読英単語 入門編</div>
      </div>

      <div style={{ fontSize: 12, color: "var(--ink-soft)", margin: "10px 0 22px" }}>
        文をタップして再生 / 🔁 でその文だけリピート / 下の速度ボタンでゆっくり再生
      </div>

      {/* 文リスト */}
      <div>
        {segments === null && <p style={{ fontSize: 13, color: "var(--ink-soft)" }}>読み込み中...</p>}
        {segments?.map((seg, i) => (
          <div
            key={i}
            ref={(el) => {
              rowRefs.current[i] = el;
            }}
            onClick={() => seekTo(seg.start)}
            style={{
              display: "grid",
              gridTemplateColumns: "34px 1fr auto",
              alignItems: "center",
              gap: 12,
              padding: i === currentSegIndex ? "12px 7px" : "12px 10px",
              borderRadius: 6,
              cursor: "pointer",
              borderBottom: "1px solid var(--paper-line)",
              borderLeft: i === currentSegIndex ? "3px solid var(--accent)" : "none",
              background: i === currentSegIndex ? "var(--accent-soft)" : "transparent",
            }}
          >
            <div
              style={{
                fontFamily: "Georgia, serif",
                fontSize: 12,
                color: i === currentSegIndex ? "var(--accent)" : "var(--ink-soft)",
                fontWeight: i === currentSegIndex ? 700 : 400,
                textAlign: "right",
              }}
            >
              {(i + 1).toString().padStart(2, "0")}
            </div>
            <div
              style={{
                fontFamily: "Georgia, 'Times New Roman', serif",
                fontSize: 17,
                lineHeight: 1.55,
                color: i < currentSegIndex ? "#9aa5b1" : "var(--ink)",
              }}
            >
              {seg.words.map((w, wi) => {
                const isCurrent = curTime >= w.s && curTime < w.e && i === currentSegIndex;
                return (
                  <span
                    key={wi}
                    style={{
                      color: isCurrent ? "var(--paper)" : undefined,
                      background: isCurrent ? "var(--accent)" : undefined,
                      borderRadius: 3,
                      padding: "0 1px",
                    }}
                  >
                    {w.w}{wi < seg.words.length - 1 ? " " : ""}
                  </span>
                );
              })}
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                toggleLoop(i);
              }}
              style={{
                width: 34,
                height: 34,
                borderRadius: "50%",
                border: "1px solid var(--paper-line)",
                background: loopSegIndex === i ? "var(--gold)" : "transparent",
                borderColor: loopSegIndex === i ? "var(--gold)" : "var(--paper-line)",
                color: loopSegIndex === i ? "white" : "var(--ink-soft)",
                fontSize: 14,
                cursor: "pointer",
              }}
            >
              🔁
            </button>
          </div>
        ))}
      </div>

      {/* コントロールバー */}
      <div
        style={{
          position: "fixed",
          bottom: 0,
          left: 0,
          right: 0,
          background: "var(--ink)",
          color: "var(--paper)",
          padding: "12px 20px calc(12px + env(safe-area-inset-bottom))",
        }}
      >
        <div style={{ maxWidth: 720, margin: "0 auto" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
            <span style={{ fontSize: 11, color: "#c8cdd4", minWidth: 38 }}>{fmtTime(curTime)}</span>
            <input
              type="range"
              min={0}
              max={duration || 100}
              step={0.1}
              value={curTime}
              onChange={(e) => seekTo(parseFloat(e.target.value))}
              style={{ flex: 1, accentColor: "var(--gold)" }}
            />
            <span style={{ fontSize: 11, color: "#c8cdd4", minWidth: 38 }}>{fmtTime(duration)}</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <button
              onClick={() => seekTo(segments?.[Math.max(0, currentSegIndex - 1)]?.start ?? 0)}
              style={ctrlBtnStyle}
            >
              ⏮
            </button>
            <button
              onClick={togglePlay}
              style={{
                width: 46,
                height: 46,
                borderRadius: "50%",
                background: "var(--paper)",
                color: "var(--ink)",
                fontSize: 16,
                border: "none",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: "pointer",
              }}
            >
              {playing ? "⏸" : "▶"}
            </button>
            <button
              onClick={() =>
                seekTo(
                  segments?.[Math.min((segments?.length ?? 1) - 1, currentSegIndex + 1)]?.start ?? 0
                )
              }
              style={ctrlBtnStyle}
            >
              ⏭
            </button>
            <div
              style={{
                display: "flex",
                gap: 4,
                marginLeft: "auto",
                background: "rgba(255,255,255,0.08)",
                borderRadius: 20,
                padding: 3,
              }}
            >
              {[0.7, 0.85, 1.0, 1.2].map((r) => (
                <button
                  key={r}
                  onClick={() => changeRate(r)}
                  style={{
                    padding: "6px 10px",
                    borderRadius: 16,
                    fontSize: 11,
                    border: "none",
                    background: rate === r ? "var(--gold)" : "transparent",
                    color: "var(--paper)",
                    cursor: "pointer",
                  }}
                >
                  {r}x
                </button>
              ))}
            </div>
          </div>
          <div style={{ fontSize: 10, color: "#8b93a1", textAlign: "center", marginTop: 8 }}>
            {loopSegIndex !== null ? `文 ${loopSegIndex + 1} をリピート再生中` : "通し再生モード"}
          </div>
        </div>
      </div>
    </div>
  );
}

const ctrlBtnStyle: React.CSSProperties = {
  background: "transparent",
  border: "none",
  color: "var(--paper)",
  cursor: "pointer",
  fontSize: 15,
  padding: 8,
};

function NavLink({ href, label }: { href?: string; label: string }) {
  const style: React.CSSProperties = {
    fontSize: 12,
    color: "var(--ink-soft)",
    textDecoration: "none",
    border: "1px solid var(--paper-line)",
    borderRadius: 14,
    padding: "5px 12px",
    background: "white",
    opacity: href ? 1 : 0.35,
    pointerEvents: href ? "auto" : "none",
  };
  return href ? (
    <Link href={href} style={style}>
      {label}
    </Link>
  ) : (
    <span style={style}>{label}</span>
  );
}
