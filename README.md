# Project Will — 観測 #4〜#6 と総括（2026-09-13〜09-28）

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXXX)

🌐 **English summary: [README_EN.md](README_EN.md)**

Minecraft の中に置いた 32 人の LLM 村人を、規則・報酬・「協力しろ」という指示を与えずに 6 時間観測するシリーズ（役割の欄の扱いは報告書 §1.4）「Project Will」の第 3 弾です。観測 #4（頭と本）・#5（体と飢え）・#6（本能）の 3 本の 6 時間ロングランと、#6 のあとに「系（私が作った仕組み）の欠陥のせいではないか」を確かめた 4 本の検証 run（B-39〜B-42。系全体の監査で見つけた不備 109 件のうち 105 件の修正を含む）の、全記録と全分析を収めています。報告書は #1 から #6 までを同じ物差しで並べ直した**シリーズの総括**を兼ねます。

📺 動画: 準備中（公開後にここへ追記します）
📄 報告書: [REPORT.md](REPORT.md)（PDF: [REPORT.pdf](REPORT.pdf)）
🔎 主張↔データ対応表: [VERIFICATION.md](VERIFICATION.md) ／ 公開前の全数再検証台帳: [VERIFICATION_LEDGER.md](VERIFICATION_LEDGER.md)
📚 データ辞書: [DATA.md](DATA.md)
🧬 足した仕組みの設計: [DESIGN_GEN3.md](DESIGN_GEN3.md)
🔧 #6 のあとの全系監査（不備 109 件）: [AUDIT_109.md](AUDIT_109.md)
⚖️ 計測の限界と正直な開示: [METHOD_AND_LIMITS.md](METHOD_AND_LIMITS.md)
📦 前作: 観測 #1 https://github.com/MONOCOLACHANNEL/project-will-observation-1（DOI [10.5281/zenodo.21723921](https://doi.org/10.5281/zenodo.21723921)）／観測 #2–#3 https://github.com/MONOCOLACHANNEL/project-will-observations-2-3（DOI [10.5281/zenodo.22040887](https://doi.org/10.5281/zenodo.22040887)）

## あらまし（主な数値は本リポジトリのデータで再計算できる。プロンプトの中身に依存する主張は分析文書の逐語による）

| | |
|---|---|
| #4 頭と本 | 時間の認識・予期・知覚の正直化・全員に本 1 冊。**殺人 0**（攻撃の提示 245・選択 0）。本は 2,322 ページ書かれたがほぼ全部が独白。物と物の交換の発話 0＝「誰も誰も必要としない村」 |
| #5 体と飢え | 体の能力 15 項目を個体ごとに独立にランダム化・飢えで死ぬ。「以前頼んだ食料の件、忘れたとは言わせんぞ」＝時間を越えて催促できる借り。本が告発状・規範の形に。物・作業を頼む割合 5.6%→14.4%。それでも交換 0・賠償 0 |
| #6 本能 | 不満駆動と系の「遺恨」の台帳・攻撃の門を撤去し、本能・本人が付けた評価の持続・約束・子の依存へ。**1 人（柏木トア）が殺人 12 件中 10 件**。攻撃を選べた 38 人中 23 人は一度も選ばなかった。本は「検閲」の名目で取り上げられる物になった（中身を検閲した事実は無い）。村で生まれた子が育ち、生後 11 分の息子を殺され、暴君を討った |
| 言葉が行動を変えたとき | 本人の記憶と評価が毎回その人の前に戻されていた場面に限られた（3 例・対照なし。復讐・−2 を付けた相手からの回避 3.7 倍・畑仕事 0→44）。**作り手が書いた設定には従い、仲間の命令にはほとんど従わなかった**（秩序系 7 人の命令 170 件で実行 8） |
| 社会 | 家族以外が話し合って一緒に動いた件 0・言葉で取り決めた交換 0・暴君への団結 0。社会は二者・家族の単位で止まった |
| #6 のあとの検証 | 会話の指示文を外す（B-39・B-40）→ 知らせの通り道を直す（B-41）→ 系全体の監査で**不備 109 件**を見つけ、105 件を直す（#6 のあとの修正は合わせて 148 件） → 判定の線を凍結して 2 時間観測（B-42）。**本線（協調・知らせ・交換）は 0**。B-42 では 1 人が 20 人を殺し、35 人中 26 人が死んだ（その後は会話がほぼ尽き、死を聞き手のいる場で伝えた発話も 0） |
| 総括 | 1 作目は、言葉だけの社会。2 作目は、4 枚の看板。3 作目は、二人のあいだだけで続く関係。この条件では、村はまだ生まれなかった |

## クイックスタート

```bash
# 人物・語句・時間帯でログを横断検索（結果は out.txt に UTF-8 で出力）
python tools/find.py 柏木トア --run obs6 --time 05:35 05:40
python tools/find.py 忘れたとは言わせん --run obs5 --speech
```

## 収録

| 文書・フォルダ | 内容 |
|---|---|
| [REPORT.md](REPORT.md) | 技術報告書 本体（#4〜#6・#6 後の検証・シリーズの総括） |
| [VERIFICATION.md](VERIFICATION.md) | 主張↔データ対応表 |
| [VERIFICATION_LEDGER.md](VERIFICATION_LEDGER.md) | 公開前の全数再検証の台帳（本文の主張を生データから独立に数え直した全件） |
| [DATA.md](DATA.md) | データ辞書と既知の注意点 |
| [DESIGN_GEN3.md](DESIGN_GEN3.md) | #4〜#6 で足した・外した仕組みの設計と、その判断の理由 |
| [AUDIT_109.md](AUDIT_109.md) | 全系監査の不備 109 件の一覧と対応 |
| [METHOD_AND_LIMITS.md](METHOD_AND_LIMITS.md) | 計測の限界・実装欠陥の正直な開示 |
| `data/` | 各 run の出来事の台帳・全発話・本の全文・人格カード・死亡の一覧 |
| [INVENTORY.md](INVENTORY.md) | 期間中の全 run（35 本）と改良の数 |

## 著者と引用

本データセットは **Project Will シリーズ**（著者: モノコーラ / Monocola）の第 3 弾であり、観測 #1・#2–#3 と同一著者による継続観測です。引用は [CITATION.cff](CITATION.cff) を参照：

> Monocola (モノコーラ). (2026). Project Will: Observations #4–#6 and series synthesis — LLM villagers given books, bodies, and instincts [Dataset]. Zenodo. https://doi.org/10.5281/zenodo.XXXXXXXX

（DOI は全バージョンを指し、常に最新版へ解決します。シリーズ全体に言及する場合は観測 #1（10.5281/zenodo.21723921）・観測 #2–#3（10.5281/zenodo.22040887）の DOI と併記してください。質問・指摘は GitHub Issue へ）

ライセンス：データ・文書 **CC BY 4.0** ／ スクリプト **MIT**（[LICENSE](LICENSE)）
