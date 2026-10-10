#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""REPORT.md を学術体裁のHTML/PDFへ変換する（観測 #4–#6 用。DOI は CITATION.cff から読む）（Google Scholar のインデックス要件に合わせる）。

Scholar の技術要件に対応させている点:
  - 1ページ目の上部にタイトル（大きな文字）→ その下に著者名
  - 要旨（Abstract）を冒頭に配置
  - 末尾に参考文献セクション
  - citation_* メタタグ（HTML側。PDF単体でも書式で認識される）
  - テキストベースのPDF（画像化しない）

使い方（このフォルダの1つ上で）:
  python tools/make_report_pdf.py            # HTML と PDF を生成
出力: REPORT.html / REPORT.pdf
"""
import os
import re
import subprocess
import sys

import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
SRC = os.path.join(ROOT, 'REPORT.md')
OUT_HTML = os.path.join(ROOT, 'REPORT.html')
OUT_PDF = os.path.join(ROOT, 'REPORT.pdf')

import re as _re
TITLE = 'Project Will 観測報告 #4–#6 と総括：本・体・本能を与えられた AI 村人は、社会を作ったか'
TITLE_EN = ('Project Will Observations #4–#6 and series synthesis: did LLM villagers given books, '
            'bodies, and instincts build a society?')
AUTHOR = 'Monocola (モノコーラ)'
DATE = '2026-10-10'
_cff = open(os.path.join(ROOT, 'CITATION.cff'), encoding='utf-8').read()
DOI = _re.search(r'^doi:\s*(\S+)', _cff, _re.M).group(1)
REPO = 'https://github.com/MONOCOLACHANNEL/project-will-observations-4-6'

ABSTRACT = (
    'Minecraft の中に置いた 32 人の LLM 村人を、規則・報酬・「協力せよ」という指示を与えずに 6 時間観測する'
    'シリーズの第 3 弾。観測#4（時間の認識・予期・知覚の正直化・全員に本）、#5（体の能力 15 項目の個体差・飢えで死ぬ）、'
    '#6（不満駆動と系の遺恨の台帳を撤去し、本能・本人が付けた評価と約束の持続・子の依存を入れた）と、'
    '#6 の後に系の欠陥を疑って行った 4 本の検証 run（系全体の監査で見つけた不備 109 件のうち 105 件を直し、'
    '判定の線を凍結してから観測し直した B-42 を含む）を報告する。#4 は殺人 0・本はほぼ独白の「誰も誰も必要としない村」、'
    '#5 は飢えが時間を越えて催促できる借りを生んだが交換 0、#6 では 1 人が殺人 12 件中 10 件を占め、本は「検閲」の名目で'
    '奪われる物になり、村で生まれた子が自分の子を殺した暴君を討った。言葉が行動を変えた例は、本人の記憶と評価が毎回'
    '本人の前に戻されていた場面に限られた。村人は作り手の設定には話し方で強く従い、仲間の命令にはほとんど従わなかった'
    '（170 件中 8 件）。家族以外の協調・言葉で取り決めた交換・集団での対処は、修正後の B-42 を含め一度も出なかった。'
    '報酬も役割の割当ても協力の指示も与えない条件では、少なくともこのモデルと方法で、個体ごとの記録・計画・予測の出力は'
    '増えたが、他人と噛み合わせる仕組みは 6 時間生まれなかった。'
)

CSS = """
@page { size: A4; margin: 20mm 18mm 20mm 18mm; }
body {
  font-family: "Yu Gothic", "Hiragino Kaku Gothic ProN", "Meiryo", "MS Gothic", sans-serif;
  font-size: 10.5pt; line-height: 1.75; color: #111; margin: 0;
}
.titleblock { margin-bottom: 1.6em; }
h1.doctitle { font-size: 20pt; line-height: 1.45; font-weight: 700; margin: 0 0 0.5em 0; }
.subtitle-en { font-size: 11pt; color: #444; font-weight: 400; margin: 0 0 1.1em 0; }
.author { font-size: 12.5pt; font-weight: 600; margin: 0 0 0.25em 0; }
.meta { font-size: 9.5pt; color: #444; margin: 0 0 0.2em 0; }
.abstract { margin: 1.6em 0 2em 0; padding: 1em 1.2em; background: #f6f6f6;
            border-left: 3px solid #999; font-size: 10pt; line-height: 1.8; }
.abstract h2 { font-size: 11pt; margin: 0 0 0.6em 0; letter-spacing: 0.08em; }
h2 { font-size: 13.5pt; margin: 1.9em 0 0.7em 0; padding-bottom: 0.25em;
     border-bottom: 1px solid #ccc; page-break-after: avoid; }
h3 { font-size: 11.5pt; margin: 1.4em 0 0.5em 0; page-break-after: avoid; }
p { margin: 0.65em 0; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 9.5pt;
        page-break-inside: avoid; }
th, td { border: 1px solid #bbb; padding: 5px 8px; text-align: left; vertical-align: top; }
th { background: #eee; }
code { font-family: Consolas, "Courier New", monospace; font-size: 9pt;
       background: #f0f0f0; padding: 1px 3px; }
pre { background: #f4f4f4; padding: 0.8em; overflow-x: auto; font-size: 9pt;
      page-break-inside: avoid; }
blockquote { margin: 1em 0 1em 1.2em; padding-left: 1em; border-left: 3px solid #bbb;
             color: #333; font-size: 10pt; }
ul, ol { margin: 0.6em 0; padding-left: 1.5em; }
li { margin: 0.3em 0; }
hr { border: none; border-top: 1px solid #ddd; margin: 1.8em 0; }
a { color: #1a4f8a; text-decoration: none; word-break: break-all; }
.refs { font-size: 9.5pt; }
"""

HTML_TMPL = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>{title}</title>
<meta name="citation_title" content="{title}">
<meta name="citation_author" content="{author}">
<meta name="citation_publication_date" content="{cdate}">
<meta name="citation_doi" content="{doi}">
<meta name="citation_abstract_html_url" content="{repo}">
<meta name="citation_pdf_url" content="{repo}/raw/main/REPORT.pdf">
<meta name="citation_language" content="ja">
<meta name="description" content="{absshort}">
<style>{css}</style>
</head>
<body>
<div class="titleblock">
  <h1 class="doctitle">{title}</h1>
  <p class="subtitle-en">{title_en}</p>
  <p class="author">{author}</p>
  <p class="meta">{date}</p>
  <p class="meta">DOI: <a href="https://doi.org/{doi}">{doi}</a></p>
  <p class="meta">データ・コード: <a href="{repo}">{repo}</a></p>
</div>
<div class="abstract">
  <h2>要旨</h2>
  <p>{abstract}</p>
</div>
{body}
</body>
</html>
"""


def build_html():
    with open(SRC, encoding='utf-8') as f:
        md = f.read()

    # 先頭のタイトル行とメタ行（著者/観測日/版/付属データ）は titleblock で再構成するため除去
    lines = md.split('\n')
    start = 0
    for i, ln in enumerate(lines):
        if ln.strip() == '---':          # 最初の水平線までがヘッダ
            start = i + 1
            break
    body_md = '\n'.join(lines[start:]).lstrip()

    # 「## 概要」節は要旨として冒頭に出すので本文からは残す（詳細版として機能させる）
    body_html = markdown.markdown(
        body_md,
        extensions=['tables', 'fenced_code', 'toc'],
        output_format='html5',
    )
    # 参考文献セクションに Scholar 向けのクラスを付ける
    body_html = body_html.replace('<h2>参考文献</h2>',
                                  '<h2 id="references">参考文献 / References</h2><div class="refs">')
    body_html = body_html.replace('<h2>引用</h2>', '</div><h2>引用</h2>')

    html = HTML_TMPL.format(
        title=TITLE, title_en=TITLE_EN, author=AUTHOR, date=DATE,
        cdate=DATE.replace('-', '/'), doi=DOI, repo=REPO,
        abstract=ABSTRACT, absshort=ABSTRACT[:200], css=CSS, body=body_html,
    )
    with open(OUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    print('HTML ->', OUT_HTML)
    return OUT_HTML


def build_pdf(html_path):
    chrome = None
    for cand in (r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                 r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
                 r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'):
        if os.path.exists(cand):
            chrome = cand
            break
    if not chrome:
        print('Chrome/Edge が見つからないため PDF はスキップ。HTML を手動で印刷してください。')
        return
    url = 'file:///' + html_path.replace('\\', '/')
    subprocess.run([chrome, '--headless', '--disable-gpu', '--no-pdf-header-footer',
                    f'--print-to-pdf={OUT_PDF}', url], check=True, timeout=180)
    print('PDF  ->', OUT_PDF, '(%.1f KB)' % (os.path.getsize(OUT_PDF) / 1024))


if __name__ == '__main__':
    build_pdf(build_html())
