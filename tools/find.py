#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""観測#4・#5・#6 と B-39〜B-42 の横断検索。結果は必ず UTF-8 のファイルへ書き出す（Windows のコンソールは cp932 で化けるため）。
Part2（publish_longrun_20260811/tools/find.py）を、このデータセットのファイル名に合わせて直したもの。

使い方（このフォルダか、リポジトリの直下で実行）:
  python tools/find.py 柏木トア                       # 全 run の発話・本・人格カード・死亡を横断 → out.txt
  python tools/find.py 柏木トア --run obs6            # run を絞る（obs4 obs5 obs6 b39 b40 b41 b42。複数可）
  python tools/find.py 本 見せ --speech --run obs6    # 発話だけ（語は AND）
  python tools/find.py --run obs6 --time 05:30 05:40  # 壁時計の時間帯で抜き出し（0時をまたぐ run は from>to で可）
  python tools/find.py v_24223bdb --events --run obs6 # events（gz）も検索（村人IDでも名前でも）
  python tools/find.py --run b42 --epoch 1790585687188  # epoch(ms) の前後3分（--events と併用可）
出力は out.txt（--out で変更可）。
"""
import argparse, os, sys, json, gzip, re, datetime

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
RUNS = ['obs4', 'obs5', 'obs6', 'b39', 'b40', 'b41', 'b42']


def sources(run, speech_only, events):
    s = [('発話', 'speech_timeline_%s.txt' % run)]
    if not speech_only:
        s += [('本', os.path.join('books', 'books_%s.txt' % run)),
              ('人格カード', os.path.join('persona_cards', 'persona_cards_%s.tsv' % run)),
              ('死亡', os.path.join('deaths', 'deaths_%s.tsv' % run))]
    if events:
        s.append(('events', 'events_%s.jsonl.gz' % run))
    return s


def tsec(t):
    p = [int(x) for x in t.split(':')]
    while len(p) < 3:
        p.append(0)
    return p[0] * 3600 + p[1] * 60 + p[2]


RX_T = re.compile(r'^(\d\d:\d\d:\d\d) ')
RX_PT = re.compile(r'｜[^ ]+ (\d\d:\d\d:\d\d)')
RX_EV = re.compile(r'"wall": "(\d\d:\d\d:\d\d)"')


def line_t(line):
    for rx in (RX_T, RX_PT, RX_EV):
        m = rx.search(line)
        if m:
            return tsec(m.group(1))
    return None


def in_range(ts, lo, hi):
    if ts is None:
        return False
    return lo <= ts <= hi if lo <= hi else (ts >= lo or ts <= hi)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('query', nargs='*', help='検索語（複数指定で AND）')
    ap.add_argument('--run', nargs='+', choices=RUNS, help='run を絞る')
    ap.add_argument('--time', nargs=2, metavar=('FROM', 'TO'), help='壁時計 例: --time 05:30 05:40')
    ap.add_argument('--epoch', type=int, help='epoch(ms) の前後3分')
    ap.add_argument('--speech', action='store_true', help='発話だけ')
    ap.add_argument('--events', action='store_true', help='events（gz）も検索（遅い）')
    ap.add_argument('--out', default='out.txt')
    a = ap.parse_args()
    lo = hi = None
    if a.time:
        lo, hi = tsec(a.time[0]), tsec(a.time[1])
    if a.epoch:
        t = datetime.datetime.fromtimestamp(a.epoch / 1000.0)
        c = t.hour * 3600 + t.minute * 60 + t.second
        lo, hi = (c - 180) % 86400, (c + 180) % 86400
    n = 0
    out_path = os.path.abspath(a.out)
    with open(out_path, 'w', encoding='utf-8') as o:
        o.write('# query=%s run=%s time=%s epoch=%s\n' % (a.query, a.run, a.time, a.epoch))
        for run in (a.run or RUNS):
            for label, fn in sources(run, a.speech, a.events):
                p = os.path.join(HERE, fn)
                if not os.path.exists(p):
                    continue
                op = gzip.open(p, 'rt', encoding='utf-8') if fn.endswith('.gz') else open(p, encoding='utf-8')
                hits = []
                with op as f:
                    for line in f:
                        line = line.rstrip('\n')
                        if a.query and not all(q in line for q in a.query):
                            continue
                        if lo is not None and not in_range(line_t(line), lo, hi):
                            continue
                        hits.append(line)
                if hits:
                    o.write('\n===== %s %s (%s) : %d件 =====\n' % (run, label, fn, len(hits)))
                    o.write('\n'.join(hits) + '\n')
                    n += len(hits)
    print('hits', n, '->', out_path)


if __name__ == '__main__':
    main()
