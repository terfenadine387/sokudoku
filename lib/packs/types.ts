export type LessonMeta = [title: string, category: string];

export type Pack = {
  id: string; // フォルダ名にも使う。英数字とハイフンのみ推奨 (例: "sokutan-nyumon")
  name: string; // 表示用の教材名 (例: "速読英単語 入門編")
  lessons: Record<string, LessonMeta>; // キーは "01".."NN" のゼロ埋め2桁
};
