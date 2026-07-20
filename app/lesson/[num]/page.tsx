import { ALL_LESSON_NUMS } from "@/lib/lessonTitles";
import LessonPlayer from "./LessonPlayer";

// 静的書き出し用: 全レッスン番号を事前生成
export function generateStaticParams() {
  return ALL_LESSON_NUMS.map((num) => ({ num }));
}

export default function LessonPage({ params }: { params: { num: string } }) {
  return <LessonPlayer num={params.num} />;
}
