import { Pack } from "./types";
import sokutanNyumon from "./sokutanNyumon";

// ここに新しいパックを追加していく
// 例: import newPack from "./newPack"; を上に足して、下の配列にも追加する
export const PACK_LIST: Pack[] = [
  sokutanNyumon,
  // newPack,
];

export const PACKS: Record<string, Pack> = Object.fromEntries(
  PACK_LIST.map((p) => [p.id, p])
);

export function getPack(packId: string): Pack | undefined {
  return PACKS[packId];
}

export function getLessonNums(packId: string): string[] {
  const pack = PACKS[packId];
  if (!pack) return [];
  return Object.keys(pack.lessons).sort((a, b) => parseInt(a) - parseInt(b));
}

export function getAllParams(): { pack: string; num: string }[] {
  const out: { pack: string; num: string }[] = [];
  for (const pack of PACK_LIST) {
    for (const num of getLessonNums(pack.id)) {
      out.push({ pack: pack.id, num });
    }
  }
  return out;
}
