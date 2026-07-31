import { Suspense } from "react";
import { getAllParams } from "@/lib/packs";
import LessonPlayer from "./LessonPlayer";

// 静的書き出し用: 全パック×全レッスン番号を事前生成
export function generateStaticParams() {
  return getAllParams();
}

export default function LessonPage({
  params,
}: {
  params: { pack: string; num: string };
}) {
  return (
    <Suspense fallback={null}>
      <LessonPlayer pack={params.pack} num={params.num} />
    </Suspense>
  );
}
