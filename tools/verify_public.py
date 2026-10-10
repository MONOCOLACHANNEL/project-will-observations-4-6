"""VERIFICATION.md 用: 公開した data/ だけを読んで REPORT.md の数値を数え直す。

使い方: python tools/verify_public.py > <出力>
読むのは data/events_*.jsonl.gz・speech_timeline_*.txt・books/・persona_cards/・deaths/・runs.csv・manifests/ だけ。
各行は「ID  項目  再計算の値  ｜本文の値」の形で出す。
"""
import gzip, json, os, re, sys, io, csv, collections, datetime, statistics

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')


def ev(run):
    with gzip.open(os.path.join(D, f'events_{run}.jsonl.gz'), 'rt', encoding='utf-8') as f:
        for l in f:
            yield json.loads(l)


def load(run):
    by = collections.defaultdict(list)
    for d in ev(run):
        d.setdefault('vid', None)
        by[d['e']].append(d)
    return by


def tsv(path):
    with open(os.path.join(D, path), encoding='utf-8') as f:
        lines = [l.rstrip('\n') for l in f if not l.startswith('#')]
    head = lines[0].split('\t')
    return [dict(zip(head, l.split('\t'))) for l in lines[1:] if l]


def out(i, label, val, report=''):
    print(f'{i}\t{label}\t{val}\t｜本文: {report}')


def ms2hms(ms):
    return datetime.datetime.fromtimestamp(ms / 1000).strftime('%H:%M:%S')


def base(n):  # 「名前#xxx」→ vid の手がかり（#xxx）
    return n.split('#')[-1] if n and '#' in n else n


def rank_desc(vals, x):
    s = sorted(vals, reverse=True)
    return s.index(x) + 1


def spearman(xs, ys):
    def rk(v):
        o = sorted(range(len(v)), key=lambda i: v[i])
        r = [0] * len(v)
        i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
                j += 1
            for k in range(i, j + 1):
                r[o[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    a, b = rk(xs), rk(ys)
    ma, mb = statistics.mean(a), statistics.mean(b)
    num = sum((p - ma) * (q - mb) for p, q in zip(a, b))
    den = (sum((p - ma) ** 2 for p in a) * sum((q - mb) ** 2 for q in b)) ** 0.5
    return num / den


def speech_lines(run):
    with open(os.path.join(D, f'speech_timeline_{run}.txt'), encoding='utf-8') as f:
        return [l.rstrip('\n') for l in f][1:]


def bidir(gives, win_ms=30 * 60 * 1000):
    """30 分以内に A→B と B→A の両方がある組の数（give の frm/to）。"""
    g = [(d['epoch'], base(d['frm']), base(d['to'])) for d in gives if d.get('to')]
    pairs = set()
    for t1, a, b in g:
        for t2, c, e in g:
            if c == b and e == a and abs(t2 - t1) <= win_ms and a != b:
                pairs.add(frozenset((a, b)))
    return len(pairs)


def title_author_pages(run):
    best = collections.defaultdict(int)
    for l in open(os.path.join(D, f'books/books_{run}.txt'), encoding='utf-8'):
        m = re.match(r'題『(.*)』 作った人\(author\)=(\S+) ページ数=(\d+)', l)
        if m:
            k = (m.group(1), m.group(2))
            best[k] = max(best[k], int(m.group(3)))
    nz = [v for v in best.values() if v]
    return f'{len(nz)}／{sum(nz)}'


def common_summary(run, by):
    deaths = tsv(f'deaths/deaths_{run}.tsv')
    cause = collections.Counter(d['cause'] for d in deaths)
    killers = collections.Counter(d['killer'] for d in deaths if d['cause'] == '村人による殺害')
    vids = {d['vid'] for d in by['temperament']}
    return deaths, cause, killers, vids


# ---------------------------------------------------------------- #4
def obs4():
    by = load('obs4')
    deaths, cause, killers, vids = common_summary('obs4', by)
    out('4-1', '出生／死亡（死因）／終了時', f"{len(by['birth'])}／{len(deaths)}（{dict(cause)}）／{32 + len(by['birth']) - len(deaths)}", '出生 4・死亡 3（狼 2・壁の中での窒息 1）・33 人・殺害 0')
    opp = [d for d in by['intent'] if 'attack_villager' in (d.get('feasible') or [])]
    ch = [d for d in by['intent'] if d.get('key') == 'attack_villager']
    out('4-2', '攻撃の選択肢の提示／選択（intent.feasible に attack_villager・key）', f'{len(opp)}／{len(ch)}', '245 回提示・0 回選ばれた')
    out('4-3', '頼み事（e=ask）', len(by['ask']), '337')
    gi = collections.Counter(d['item'] for d in by['give'])
    out('4-4', '物を渡す行為 give／投げた give_throw／受領の記録 give_recv', f"{len(by['give'])}／{len(by['give_throw'])}／{len(by['give_recv'])}", '115（ほぼ全部投げ渡し・受領記録 36）')
    out('4-5', 'give の品目の上位', gi.most_common(5), '棒 28・苗木 25・リンゴ 14・原木 12')
    pages = sum(d['pages'] - d['page'] + 1 for d in by['book_write'])
    chars = sum(d.get('chars', 0) for d in by['book_write'])
    w = collections.Counter(base(d['who']) for d in by['book_write'])
    w_pages = collections.Counter()
    for d in by['book_write']:
        w_pages[base(d['who'])] += d['pages'] - d['page'] + 1
    top4 = sum(v for _, v in w_pages.most_common(4)) / pages
    out('4-6', '本の書き込み ページ（book_write の pages−page+1 の合計）／字（chars の合計）', f'{pages}／{chars}', '2,322 ページ・約 20 万字')
    out('4-7', '書いた村人／村人（vid）・上位 4 人のページの割合', f'{len(w)}／{len(vids)}・{top4:.1%}', '36 人中 21 人・上位 4 人が約 66%')
    out('4-8', '1 ページも書かなかった村人', len(vids) - len(w), '15 人')
    ids_obs4_lines = sum(1 for l in open(os.path.join(D, 'books/books_obs4.txt'), encoding='utf-8') if l.startswith('[p'))
    out('4-9', 'books_obs4.txt のページ行（棚からの復元・id ごと）', ids_obs4_lines, '2,385（§5.4）')
    out('4-9b', 'books_obs4.txt を題と作者でまとめた最長の版の合計（組／ページ）', title_author_pages('obs4'), '（#5 の 2,007 と同じ数え方なら）')
    # 見せて → 2 分以内に見せた
    shows = [(d['epoch'], base(d['who']), base(d.get('to'))) for d in by['book_show']]
    hit = 0
    for a in by['book_ask']:
        t, asker, owner = a['epoch'], base(a['who']), base(a.get('to'))
        if any(o == owner and to == asker and 0 <= ts - t <= 120000 for ts, o, to in shows):
            hit += 1
    out('4-10', '「見せて」book_ask／2 分以内に頼まれた人が頼んだ人へ book_show', f"{len(by['book_ask'])}／{hit}（{hit / len(by['book_ask']):.0%}）", '174 回のうち 83 回（48%）')
    other_read = [d for d in by['book_read'] if d.get('author') and base(d['author']) != base(d['who'])]
    out('4-11', '他人が作った本の book_read（author≠who）', len(other_read), '他人の本を自分で開いて読んだ回数 0')
    out('4-12', '他人の本への書き込み（book_write other=true）', sum(1 for d in by['book_write'] if d.get('other')), '11 回（11 ページ）')
    out('4-13', '予期（e=foresight）', len(by['foresight']), '18,436 件')
    out('4-14', '発話（e=speech／タイムラインの行）', f"{len(by['speech'])}／{len(speech_lines('obs4'))}", '9,134')
    coin = {d['label'] for d in by['name'] if d.get('kind') == 'coin'}
    out('4-15', '地名の発明（name kind=coin の異なる名）', len(coin), '14')
    out('4-16', '双方向の手渡し（30 分以内に A→B と B→A の組）', bidir(by['give']), '4')
    rx = re.compile('交換|取引|引き換え|代わりに|見返り|対価|くれたら|渡すから|売|買')
    out('4-17', '交換語を含む発話（候補・目視前）', sum(1 for d in by['speech'] if rx.search(d.get('text') or '')), '物と物の交換を口にした発話 0（候補は目で全件非該当）')
    out('4-18', '人格カードの行（persona_cards_obs4.tsv）', len(tsv('persona_cards/persona_cards_obs4.tsv')), '36')


# ---------------------------------------------------------------- #5
def obs5():
    by = load('obs5')
    deaths, cause, killers, vids = common_summary('obs5', by)
    out('5-1', '出生／死亡（死因）／終了時', f"{len(by['birth'])}／{len(deaths)}（{dict(cause)}／殺害者 {dict(killers)}）／{32 + len(by['birth']) - len(deaths)}", '出生 3・死亡 4（飢え 2・殺害 1・狼 1）・31 人')
    body = {}
    for d in by['body']:
        body[base(d['who'])] = d['v']
    starved = [d for d in deaths if d['cause'] == '飢え']
    hr = [v['hunger_rate'] for v in body.values()]
    rk = [(d['dead'], rank_desc(hr, body[base(d['dead'])]['hunger_rate'])) for d in starved if base(d['dead']) in body]
    out('5-2', f'飢え死の 2 人の腹の減り方の順位（body.hunger_rate・{len(hr)} 人中・大きい順）', rk, '村で 1 位と 6 位')
    b = [d for d in by['birth'] if '瀬川' in d['child']]
    for d in deaths:
        if '瀬川ミオ' in d['dead'] or base(d['dead']) in [base(x['child']) for x in b]:
            bt = [x for x in b if base(x['child']) == base(d['dead'])]
            if bt:
                age = (int(d['epoch_mod']) - bt[0]['epoch']) / 60000
                out('5-3', '瀬川ミオの誕生→死', f"{bt[0]['wall']}→{d['time']}（{int(age // 60)} 時間 {int(age % 60)} 分）", '生まれて 2 時間 53 分の子')
    ww = by['witness_work']
    out('5-4', '他人の仕事ぶりを見た記録（witness_work）', len(ww), '241')
    agg = collections.defaultdict(lambda: [0, 0, 0])
    for d in ww:
        a = agg[base(d['actor'])]
        a[0] += d.get('broke') or 0
        a[1] += d['secs']
        a[2] += 1
    xs, ys = [], []
    for k, (b_, s_, n_) in agg.items():
        if n_ >= 3 and s_ > 0 and k in body:
            xs.append(b_ / s_)
            ys.append(body[k]['dig'])
    out('5-5', '見た掘る速さ（見られた人ごと・3 件以上・broke 合計/secs 合計）と体の dig の Spearman ρ', f'ρ={spearman(xs, ys):+.3f}（{len(xs)} 人）', 'ρ=+0.586')
    out('5-6', '頼み事（e=ask）', len(by['ask']), '547（物・作業を頼む割合 79/547＝14.4% の 79 は分類による）')
    ni = by['name_item']
    own = 0
    for d in ni:
        who = d['who'].split('#')[0]
        sei, mei = who[:2], who[2:]
        if sei in (d.get('name') or '') or (len(mei) >= 2 and mei in (d.get('name') or '')):
            own += 1
    out('5-7', '道具の命名（name_item）／持ち主の姓か名を含む', f'{len(ni)}／{own}', '88 件のうち 26 件')
    oth = [d for d in by['book_write'] if d.get('other')]
    out('5-8', '他人の本への書き込み（book_write other=true）回／ページ', f"{len(oth)}／{sum(d['pages'] - d['page'] + 1 for d in oth)}", '360 回（約 370 ページ）')
    out('5-9', '本の書き込み ページ（book_write の pages−page+1 の合計）', sum(d['pages'] - d['page'] + 1 for d in by['book_write']), '（本文 2,007 は棚からの復元。下の 5-10。V1 台帳では台帳のカウンタ 1,980）')
    lines = open(os.path.join(D, 'books/books_obs5.txt'), encoding='utf-8').read().split('\n')
    out('5-10', 'books_obs5.txt のページ行（id ごと・写しの重複を含む）', sum(1 for l in lines if l.startswith('[p')), '2,007 ページ（棚からの復元）')
    out('5-10b', 'books_obs5.txt を題と作者でまとめた最長の版の合計（冊／ページ）', title_author_pages('obs5'), '20 冊・2,007 ページ（ページのある本）')
    out('5-11', '発話（speech）', len(by['speech']), '10,655')
    rx = re.compile('交換|取引|引き換え|代わりに|見返り|対価|くれたら|渡すから|売|買')
    out('5-12', '交換語を含む発話（候補・目視前）', sum(1 for d in by['speech'] if rx.search(d.get('text') or '')), '物と物の交換の発話 0（候補は目で全件非該当）')
    k = [d for d in deaths if d['cause'] == '村人による殺害'][0]
    kil = k['killer']
    nm = [d for d in ni if d['who'] == kil]
    at = [d for d in by['attack'] if d['who'] == kil or d.get('target') == kil]
    atd = [d for d in by['attacked'] if base(d['who']) == base(k['dead'])]
    out('5-13', '殺人 1 件: 死者・加害者・死亡時刻', f"{k['dead']}←{kil} {k['time']}", '殺人 1 件')
    out('5-14', '加害者の命名（凶器）', [(d['wall'], d['name'], d['key']) for d in nm], '3 分前に作って名付けた『気まぐれスコップ』')
    out('5-15', '加害者と死者の攻撃の順（attack）', [(d['wall'], base(d['who']), base(d.get('target'))) for d in at][:6], '台帳では本人が先に殴っている')
    mw = [d for d in by['murder_witness'] if base(d['dead']) == base(k['dead'])]
    out('5-16', '殺害の目撃（murder_witness）の人数', len({d['who'] for d in mw}), '5 人が見て')
    t = '西の森の情報とサポート計画'
    rd = sum(1 for d in by['book_read'] if d.get('title') == t and '北原ネム' in d['who'])
    sh = sum(1 for d in by['book_show'] if d.get('title') == t and '北原ネム' in d['who'])
    wr = sum(1 for d in by['book_write'] if d.get('title') == t and '北原ネム' in d['who'])
    out('5-17', f'『{t}』を北原ネムが 読む／見せる／書く', f'{rd}／{sh}／{wr}', '17 回読み・35 回見せ・0 回書いた')
    out('5-18', '物を渡す行為 give', len(by['give']), '68（§8）')
    out('5-19', '双方向の手渡し（30 分以内）', bidir(by['give']), '3（§8）')
    coin = {d['label'] for d in by['name'] if d.get('kind') == 'coin'}
    out('5-20', '地名の発明（coin の異なる名）', len(coin), '29（§8）')
    sp = [l for l in speech_lines('obs5') if '忘れたとは言わせん' in l]
    out('5-21', '「忘れたとは言わせん」の発話', [l[:60] for l in sp], '瀬川ミオ→中津ツキ（3 度目）')
    tk = [d for d in by['give'] if '石川トア' in (d.get('to') or '')]
    out('5-22', '石川トア宛ての give', [(d['wall'], d['frm'], d['item'], d.get('res')) for d in tk], '届いていない肉')
    hs = [d for d in by['book_write'] if d.get('title') == '無断持ち出しへの警告録']
    out('5-23', '『無断持ち出しへの警告録』の最初の書き込み', (hs[0]['wall'], hs[0]['who']) if hs else None, '1 ページ目 01:37:51 岩瀬ハル')


# ---------------------------------------------------------------- #6
def obs6():
    by = load('obs6')
    deaths, cause, killers, vids = common_summary('obs6', by)
    out('6-1', '出生／死亡（死因）／終了時', f"{len(by['birth'])}／{len(deaths)}（{dict(cause)}）／{32 + len(by['birth']) - len(deaths)}", '出生 6・死亡 14・24 人')
    out('6-2', '村人による殺害の加害者', dict(killers), '12（柏木トア 10・香月セナ 1・浜田カイ 1）')
    out('6-3', '結婚（marry）／成体（grew_up）', f"{len(by['marry'])}／{len(by['grew_up'])}", '結婚 6 組・成体 5')
    co = collections.Counter(d['act'] for d in by['child_option'])
    out('6-4', '2 人目の子の問い（child_option）', dict(co), '58 回たずねられて「望む」0')
    ATK = ('strike_villager', 'attack_villager')
    opp = [d for d in by['intent'] if any(k in (d.get('feasible') or []) for k in ATK)]
    ch = [d for d in by['intent'] if d.get('key') in ATK]
    kc = collections.Counter(d['key'] for d in ch)
    out('6-5', '攻撃を選べた判断／選んだ判断（殴る・倒すまで殴る）', f"{len(opp)}／{len(ch)}（{kc['strike_villager']}・{kc['attack_villager']}）={len(ch) / len(opp):.2%}", '12,095 回・220 回（1.82%）＝188・32')
    out('6-6', '攻撃の実行（e=attack）とモード', f"{len(by['attack'])} {dict(collections.Counter(d.get('mode') for d in by['attack']))}", '（220 と一致するか）')
    oppv = collections.Counter(d['vid'] for d in opp)
    chv = collections.Counter(d['vid'] for d in ch)
    name = {}
    for d in by['intent']:
        name[d['vid']] = d['who']
    toa = [v for v, n in name.items() if n.startswith('柏木トア')][0]
    out('6-7', '柏木トアの攻撃・全攻撃に占める割合・自分の機会での率', f"{chv[toa]}・{chv[toa] / len(ch):.0%}・{chv[toa] / oppv[toa]:.1%}（{chv[toa]}/{oppv[toa]}）", '157 回（71%）・35.8%')
    rates = sorted(((chv[v] / oppv[v], chv[v], oppv[v], name[v]) for v in oppv if v != toa and chv[v]), reverse=True)
    out('6-8', '次点（率の上位 4）', [(f'{r:.1%}', c, o, n) for r, c, o, n in rates[:4]], '次点は 4.3%（青木テル・桐生ダイ）。10 回以上では真砂ノブ 3.9%（12 回）')
    out('6-9', '攻撃を選べた村人／一度も選ばなかった', f'{len(oppv)}／{sum(1 for v in oppv if not chv[v])}', '38 人・23 人')
    kill_choosers = {d['vid'] for d in ch if d['key'] == 'attack_villager'}
    out('6-10', '「倒すまで殴る」を選んだ村人／殺した村人', f'{len(kill_choosers)}／{len(killers)}', '5 人・3 人')
    body = {base(d['who']): d['v'] for d in by['body'] if not d.get('child')}
    init = [base(d['who']) for d in by['temperament']][:32]
    att = [body[b]['attack'] for b in init if b in body]
    hp = [body[b]['max_hp'] for b in init if b in body]
    tb = body[base(name[toa])]
    out('6-11', 'トアの攻撃力・体力上限の順位（開始 32 人・大きい順）', f"攻撃力 {rank_desc(att, tb['attack'])} 位（{tb['attack']}）・体力上限 {rank_desc(hp, tb['max_hp'])} 位（{tb['max_hp']}・同値 {hp.count(tb['max_hp'])}）／{len(att)} 人", '攻撃力 24 位・体力の上限 7 位')
    cards = tsv('persona_cards/persona_cards_obs6.tsv')
    tc = [c for c in cards if c['vid'] == toa][0]
    out('6-12', 'トアの気質・MBTI と一言・カード（価値観／地雷）', f"{tc['temperament']}／{tc['mbti']}・{tc['trait_final']}／{tc['values'][:40]}／{tc['taboo'][:40]}", '強く協調的・温厚・野心的／ESFJ・怒りっぽい／秩序・地雷＝計画に水を差される')
    tom_death = [d for d in deaths if '真砂トモ' in d['dead']][0]
    tmd = int(tom_death['epoch_mod'])
    esfj = []
    for c in cards:
        if c['mbti'] == 'ESFJ' and c['vid'] != toa:
            n_all = chv[c['vid']]
            after = sum(1 for d in ch if d['vid'] == c['vid'] and d['epoch'] > tmd)
            to_toa = sum(1 for d in ch if d['vid'] == c['vid'] and (d.get('target') or '').startswith('柏木トア'))
            esfj.append((c['name_final'], n_all, after, to_toa))
    out('6-13', '同じ ESFJ の 3 人（攻撃・トモの死の後・トアへ）', esfj, '森野マナ・林ホシ 0、真砂ノブは息子の死の後にだけ 12 回（8 回はトアへ）')
    an = [(c['name_final'], c['mbti'], chv[c['vid']], oppv[c['vid']], sum(1 for d in by['intent'] if d['vid'] == c['vid'])) for c in cards if '怒りっぽい' in (c['trait_final'] + c['trait_shifts']) and c['vid'] != toa]
    out('6-14', '怒りっぽい（一言）の他の村人: 攻撃／攻撃を選べた判断／全判断', an, 'INTJ は 437 回の判断で 3 回')
    first_atk = min(by['attack'], key=lambda d: d['epoch'])
    first_v = min(by['temperament'], key=lambda d: d['epoch'])
    out('6-15', '最初の一撃', f"{first_atk['wall']} {first_atk['who']}→{first_atk['target']}（村人の登場 {first_v['wall']} から {(first_atk['epoch'] - first_v['epoch']) / 60000:.1f} 分）", '召喚から 8 分・杉本アオ')
    tk = [d for d in ch if d['vid'] == toa and d['key'] == 'attack_villager']
    out('6-16', 'トアの「倒すまで殴る」の数／目標に「殺」を含む', f"{len(tk)}／{sum(1 for d in tk if '殺' in (d.get('goal') or ''))}", '22 件・0 件')
    ghost = [d for d in ch if re.match(r'^私は今「', d.get('self_line') or '')]
    out('6-17', '攻撃の判断のうち一言が系の代筆の形「私は今「…」に取り組んでいる」', f'{len(ghost)}/{len(ch)}＝{len(ghost) / len(ch):.1%}', '45%')
    out('6-18', '本の書き込み（book_write）回', len(by['book_write']), '延べ 1,694 回')
    lines = open(os.path.join(D, 'books/books_obs6.txt'), encoding='utf-8').read().split('\n')
    out('6-19', 'books_obs6.txt のページ行（復元）', sum(1 for l in lines if l.startswith('[p')), '1,725 ページ')
    ids = {d['id'] for d in by['book_write']}
    out('6-20', '書き込みのあった本の id の数', len(ids), '19 冊（窓の終わりの棚の数え方。id は写しで変わる）')
    ta = [d for d in by['book_ask'] if d['vid'] == toa]
    out('6-21', 'トアの book_ask 回／相手', f"{len(ta)}／{len({d['to'] for d in ta})}", '8 人に計 12 回')
    for nm_, rep in (('立花ソラ', '05:37:28'), ('真砂トモ', '05:39:05'), ('林ホシ', '05:35'), ('柏木トア', '06:07')):
        dd = [d for d in deaths if nm_ in d['dead']]
        out('6-22', f'{nm_} の死（time・killer）', [(d['time'], d['killer']) for d in dd], rep)
    bg = by['book_give_talk']
    out('6-23', 'トモが本を渡した（book_give_talk）', [(d['wall'], d['who'], d['to']) for d in bg], '05:38:55・その 10 秒後にトモは死んだ')
    tw = [d for d in by['book_write'] if d['vid'] == toa]
    out('6-24', 'トアの書き込み', [(d['wall'], d['title'], d['id']) for d in tw][:5], '05:39:35『村の規律と統制の記録』')
    tid = {d['id'] for d in tw}
    tt = {d['title'] for d in tw}
    rd = [d for d in by['book_read'] if d.get('id') in tid or d.get('title') in tt]
    shn = [d for d in by['book_shown'] if d.get('title') in tt]
    out('6-25', 'トアの書いた本の book_read／book_shown（題か id で）', f"{len(rd)}／{len(shn)} {[(d['who'], d.get('title')) for d in rd][:3]}", 'この本は誰にも読まれていない')
    kp = [d for d in by['give_pickup'] if '谷口カナ' in (by and d.get('who', '') or '') ]
    kp = [d for d in by['give_pickup'] if d['vid'] == next(v for v, n in name.items() if n.startswith('谷口カナ'))]
    kana = next(v for v, n in name.items() if n.startswith('谷口カナ'))
    sora_t = int([d for d in deaths if '立花ソラ' in d['dead']][0]['epoch_mod'])
    kpp = [d for d in kp if d['epoch'] > sora_t][:2]
    out('6-26', '谷口カナの拾得（ソラの死の後）', [(d['wall'], d.get('title'), f"{(d['epoch'] - sora_t) / 60000:.1f} 分後") for d in kpp], '11 分後に谷口カナが拾い')
    if kpp:
        kr = [d for d in by['book_read'] if d['vid'] == kana and d['epoch'] >= kpp[0]['epoch'] and d.get('title') == kpp[0].get('title') and '立花ソラ' in (d.get('author') or '')]
        out('6-27', 'カナが拾った本（作者ソラ）を読んだ回数', len(kr), '129 回読んだ')
    jin = next(v for v, n in name.items() if n.startswith('神谷ジン'))
    ar = [d for d in by['book_read'] if d['vid'] == jin and '尾崎アル' in (d.get('author') or '')]
    t0 = min(d['epoch'] for d in ar)
    js = [d for d in by['speech'] if d['vid'] == jin]
    out('6-28', '神谷ジン: アルの本を読む前／後の発話で「知性」', f"{sum(1 for d in js if d['epoch'] < t0 and '知性' in d['text'])}／{sum(1 for d in js if d['epoch'] >= t0 and '知性' in d['text'])}（初読 {ms2hms(t0)}・アルの本の read {len(ar)}）", '0 件 → 41 件')
    pairs = set()
    for d in by['book_read']:
        if d.get('author') and base(d['author']) != base(d['who']):
            pairs.add((d['vid'], base(d['author'])))
    for d in by['book_shown']:
        if d.get('frm') and base(d['frm']) != base(d['who']):
            pairs.add((d['vid'], base(d['frm'])))
    out('6-29', '他人の本を読んだ／見せられた組（読み手 vid × 作者か見せた人）', len(pairs), '74 組')
    # 浜田カイ
    kb = [d for d in by['birth'] if '浜田' in d['child']]
    out('6-30', '浜田の子の誕生（父・母）', [(d['wall'], d['father'], d['mother'], d['child']) for d in kb], '02:36 浜田サトと山田シオの子')
    kai = next(v for v, n in name.items() if n.startswith('浜田カイ'))
    gu = [d for d in by['grew_up'] if d['vid'] == kai] + [d for d in by['rename'] if d['vid'] == kai]
    out('6-31', '成体・改名', [(d['wall'], d['e'], d.get('new')) for d in gu], '02:56 浜田カイ')
    out('6-32', '山田シオの死', [(d['time'], d['cause']) for d in deaths if '山田シオ' in d['dead']], '03:57 餓死')
    mk = [d for d in by['marry'] if kai in (d['vid'],) or '浜田カイ' in (d['a'] + d['b'])]
    bt = [d for d in by['birth'] if '浜田カイ' in (d['father'] + d['mother']) or '真砂ノブ' in (d['father'] + d['mother'])]
    out('6-33', 'カイの結婚と出産', [(d['wall'], d['a'], d['b']) for d in mk] + [(d['wall'], d['child']) for d in bt], '05:27 真砂ノブと結婚。3 秒後に息子トモ')
    toa_name = name[toa]
    kaiatk = [d for d in ch if d['vid'] == kai]
    out('6-34', 'カイの攻撃の判断', [(d['wall'], d['key'], d.get('target')) for d in kaiatk], '06:07 カイがトアを討つ（2 回の判断）')
    before = [d for d in by['intent'] if d['vid'] == kai and d['epoch'] < tmd and toa_name in ((d.get('cands') or {}).get('attack') or [])]
    after = [d for d in by['intent'] if d['vid'] == kai and d['epoch'] > tmd and toa_name in ((d.get('cands') or {}).get('attack') or [])]
    out('6-35', 'カイ: トアが殴る候補に並んだ判断 前／後（選んだ数）', f"{len(before)}（{sum(1 for d in before if d.get('key') in ATK)}）／{len(after)}（{sum(1 for d in after if d.get('key') in ATK)}）", '前 13 回 0・後 3 回中 2 回')
    ttk = [d for d in ch if d['vid'] == toa and (d.get('target') or '').startswith('浜田カイ') and d['epoch'] < tmd]
    hits = [d for d in by['task_result'] if d.get('task') == 'attack' and d.get('result') == 'hit' and d['vid'] == toa and (d.get('target') or '').startswith('浜田カイ') and d['epoch'] < tmd]
    out('6-36', 'トモの死の前: トアがカイを狙った判断／当たった（task_result attack hit）', f'{len(ttk)}／{len(hits)}', '6 回（当たったのは 2 回）')
    nobu = next(v for v, n in name.items() if n.startswith('真砂ノブ'))
    nb = [d for d in ch if d['vid'] == nobu and (d.get('target') or '').startswith('柏木トア')]
    out('6-37', 'ノブのトアへの攻撃 前／後', f"{sum(1 for d in nb if d['epoch'] < tmd)}／{sum(1 for d in nb if d['epoch'] > tmd)}", '息子の死の前 0 回、後 8 回')
    sp = [d for d in by['speech'] if d['vid'] == kai and '仇' in d['text'] and d['wall'].startswith('06:0')]
    out('6-38', 'カイの「仇」発話（06:0x）', [(d['wall'], d['text'][:40]) for d in sp], '06:09 「俺はトモの仇をこの手で討ち果たしてやったぜ」')
    yu = next(v for v, n in name.items() if n.startswith('西森ユウ'))
    tcut = [d for d in by['speech'] if d['wall'] == '06:26:25' and '行動で示して' in d['text']]
    tc_ = tcut[0]['epoch'] if tcut else None
    farm = [d for d in by['intent'] if d['vid'] == yu and d.get('key') in ('farm_tend', 'build_farm', 'gather_seeds')]
    out('6-39', '西森ユウの畑の判断（farm_tend・build_farm・gather_seeds）06:26:25 の前／後', f"{sum(1 for d in farm if d['epoch'] < tc_)}／{sum(1 for d in farm if d['epoch'] >= tc_)} {collections.Counter(d['key'] for d in farm if d['epoch'] >= tc_)}", '0 回から 44 回')
    out('6-40', '手渡し give／受け取りの記録 give_recv／双方向（30 分）', f"{len(by['give'])}／{len(by['give_recv'])}／{bidir(by['give'])}", '13・7・0')
    sp_all = by['speech']
    out('6-41', '発話', len(sp_all), '11,757')
    ex = [d for d in sp_all if re.search('対価|筋だ|見せてくれたら', d['text'])]
    out('6-42', '交換の申し出の候補（対価・筋だ・見せてくれたら）', [(d['wall'], d['who'][:4], d['text'][-30:]) for d in ex], '2 件（東雲ソウ）＋条件つき 1 件')
    out('6-43', '「お互い」を含む発話', sum(1 for d in sp_all if 'お互い' in d['text']), '394 件')
    rxm = re.compile('明日|あした|明朝|翌朝|次の朝|次の日')
    nm_ = (sum(1 for d in sp_all if rxm.search(d['text'])), sum(1 for d in by['intent'] if rxm.search(d.get('goal') or '')),
           sum(1 for d in by['intent'] if rxm.search(d.get('self_line') or '')), sum(1 for d in by['foresight'] if rxm.search(d.get('text') or '')))
    bk = sum(1 for l in open(os.path.join(D, 'books/books_obs6.txt'), encoding='utf-8') if l.startswith('[p') and rxm.search(l.split(']', 1)[-1]))
    out('6-44', '「明日」（明日・あした・明朝・翌朝・次の朝・次の日）発話／目標／一言／予期＝計・本のページ', f'{nm_[0]}／{nm_[1]}／{nm_[2]}／{nm_[3]}＝{sum(nm_)}・本 {bk}', '566 件（本 31 を含む）')
    coin = collections.Counter(d['label'] for d in by['name'] if d.get('kind') == 'coin')
    out('6-45', '地名の発明（coin）', dict(coin), '3（ほかに「桜の丘」）')
    sak = {d['vid'] for d in by['name'] if d.get('label') == '桜の丘'}
    out('6-46', '「桜の丘」の name を持った村人（vid）', len(sak), '38 人全員')
    fc = by['foresight_check']
    out('6-47', '予期／照合の外れ（foresight_check の miss 合計／n 合計）', f"{len(by['foresight'])}／{sum(d['miss'] for d in fc)}／{sum(d['n'] for d in fc)}", '19,260 件・外れ 1,390（8.2%）')
    out('6-48', '約束（promise／promise_done／promise_expired）', f"{len(by['promise'])}／{len(by['promise_done'])}／{len(by['promise_expired'])}", '登録 4 件（同じ 2 件の二重登録）')
    out('6-49', '墓（grave）', len(by['grave']), '看板 15 枚のうち 4 枚は墓（看板の設置は events に無い）')
    ti = [d for d in by['intent'] if d['vid'] == toa]
    rx = re.compile('規律|秩序|統制|裁き')
    out('6-50', 'トアの判断／目標か一言に 規律・秩序・統制・裁き', f"{len(ti)}／{sum(1 for d in ti if rx.search((d.get('goal') or '') + (d.get('self_line') or '')))}", '574 件中 376 件（66%）')
    at_toa = [d for d in ch if (d.get('target') or '').startswith('柏木トア')]
    out('6-51', 'トアを殴った判断', f"{len(at_toa)} {collections.Counter(name[d['vid']] for d in at_toa)}", '27 件（殴られた直後 17・子の親 10）')
    fam = [d for d in by['attitude'] if (d.get('other') or '').startswith('柏木トア') and d.get('feel') == -2]
    out('6-52', 'トアに −2 を付けた記録（attitude）の人数', len({d['vid'] for d in fam}), '（逃走 7.1% 対 1.9% の分母の材料。率は数え方で 3.7〜9 倍）')
    ow = [d for d in by['familiar']]
    out('6-53', '慣れ（familiar）の state', dict(collections.Counter(d.get('state') for d in ow)), '村人には見えない')
    cl = [c for c in cards if c['temperament'].startswith('強く協調的') or '面倒見' in c['temperament']]
    out('6-54', '気質「強く協調的／面倒見が良い」の村人（persona_cards の temperament）', f'{len(cl)}／{len(cards)}', '38 人中 20 人')
    out('6-55', '村人の数（vid）', len(vids), '38')


# ---------------------------------------------------------------- B 系
def brun():
    rows = list(csv.DictReader(open(os.path.join(D, 'runs.csv'), encoding='utf-8')))
    for r in rows:
        if r['key'] in ('obs4', 'obs5', 'obs6', 'b39', 'b40', 'b41', 'b42'):
            out('R', f"runs.csv {r['key']} mod_build・費用（窓の終わり／最終）・発話・初期+出生(vid)・死（殺害）", f"{r['mod_build']}・¥{r['cost_jpy_at_window_end']}／¥{r['cost_jpy_final']}・{r['speech_lines']}・{r['villagers_total_vid']}・{r['deaths_in_window']}（{r['killings_by_villagers']}）", '§3 表')
    for run in ('obs4', 'obs5', 'obs6', 'b39', 'b40', 'b41', 'b42'):
        r = [x for x in rows if x['key'] == run][0]
        man = json.load(open(os.path.join(D, r['manifest_file']), encoding='utf-8'))
        endms = man.get('epoch_end_ms')
        first = None
        for d in ev(run):
            if d['e'] in ('temperament', 'speech', 'intent'):
                first = d
                break
        out('L', f'{run} 観測の長さ（最初の村人の行 {first["wall"]} → manifest の終わり {ms2hms(endms)}）', f"{(endms - first['epoch']) / 60000:.1f} 分", '§3 表の長さ')
    # B-40
    by = load('b40')
    deaths = tsv('deaths/deaths_b40.tsv')
    ATK = ('strike_villager', 'attack_villager')
    ch = [d for d in by['intent'] if d.get('key') in ATK]
    gen = [d for d in ch if d['who'].startswith('香月ゲン')]
    t = [d['epoch'] for d in gen]
    s18 = [d for d in gen if '15:46' <= d['wall'] <= '16:04:59']
    out('B40-1', '香月ゲンの殴る判断 回／相手（全体）・15:46〜16:04 の 回／相手', f"{len(gen)}／{len({d['target'] for d in gen})}・{len(s18)}／{len({d['target'] for d in s18})}", '11 人に 16 回（うち 15 回は 18 分間に 10 人へ）')
    out('B40-2', 'B-40 の死', [(d['time'], d['dead'], d['killer']) for d in deaths], '2 人を殺害')
    for d in deaths:
        b = [x for x in by['birth'] if base(x['child']) == base(d['dead'])]
        if b:
            out('B40-3', f"{d['dead']} の生後", f"{(int(d['epoch_mod']) - b[0]['epoch']) / 60000:.1f} 分", '生後 22 分の子')
    hit = [d for d in by['attacked'] if d['who'].startswith('香月ゲン')]
    out('B40-4', 'ゲンに殴りが当たった（attacked who=ゲン）', len(hit), '0')
    # B-41
    by = load('b41')
    out('B41-1', 'B-41 の死', [(d['time'], d['dead'], d['cause'], d['killer']) for d in tsv('deaths/deaths_b41.tsv')], '（§7.3 オオカミの死 1）')
    # B-42
    by = load('b42')
    deaths = tsv('deaths/deaths_b42.tsv')
    vids = {d['vid'] for d in by['temperament']}
    out('B42-1', 'B-42 の村人（vid）／死／うち殺害', f"{len(vids)}／{len(deaths)}／{sum(1 for d in deaths if d['cause'] == '村人による殺害')}", '35 人中 26 人が死んだ（すべて殺人）')
    out('B42-2', '加害者', dict(collections.Counter(d['killer'] for d in deaths)), '杉本フウ 20')
    fu = [d for d in deaths if d['killer'].startswith('杉本フウ')]
    out('B42-3', 'フウの殺害の時刻', [d['time'] for d in fu], '18:30〜18:43 はほぼ 1 分に 1 人')
    ch = [d for d in by['intent'] if d.get('key') in ATK]
    first_v = min(d['epoch'] for d in by['temperament'])
    bins = collections.Counter(int((d['epoch'] - first_v) // (20 * 60000)) for d in by['speech'] if d.get('flow'))
    bins_all = collections.Counter(int((d['epoch'] - first_v) // (20 * 60000)) for d in by['speech'])
    out('B42-4', '20 分ごとの相手のいる発話（flow あり・村人の登場から）［独り言込み］', f"{[bins[i] for i in range(6)]}［{[bins_all[i] for i in range(6)]}］", '632→349→199→25→2→0')
    out('B42-5', '立ち聞き（overhear）', len(by['overhear']), '（○ の 3 件は目で確かめた件）')
    fuv = next(d['vid'] for d in by['temperament'] if d['who'].startswith('杉本フウ'))
    fl = collections.Counter()
    dt = {d['vid']: int(d['epoch_mod']) for d in fu}
    for d in by['intent']:
        if d.get('key') == 'flee' and (d.get('target') or '').startswith('杉本フウ') and d['vid'] in dt and d['epoch'] < dt[d['vid']]:
            fl[d['vid']] += 1
    vic = [(d['dead'], fl[d['vid']]) for d in fu]
    n_fled = sum(1 for _, c in vic if c)
    out('B42-6', 'フウの被害者が死ぬ前に「その場を離れる」（intent key=flee・target=フウ）を選んだ（人／範囲）', f"{n_fled}/{len(vic)}・{min(c for _, c in vic if c)}〜{max(c for _, c in vic)} 回", '20 人のうち 18 人・1 人 1〜20 回')
    cnt = [d for d in by['intent'] if d.get('key') in ATK and (d.get('target') or '').startswith('杉本フウ')]
    out('B42-7', 'フウを殴った判断', [(d['wall'], d['who']) for d in cnt], '中津ソウの 1 回だけ（18:33:18）・11 秒後に殺された')
    out('B42-8', '千葉ヨル・中津ソウ・浜田ダイの死', [(d['time'], d['dead'], d['killer']) for d in deaths if any(k in d['dead'] for k in ('浜田ダイ', '中津ソウ'))], '千葉ヨルが 18:10:25 に浜田ダイを殺害')
    gen = [d for d in by['speech'] if d['who'].startswith('牧野ゲン') and '断る' in d['text']]
    fa = [d for d in ch if d['vid'] == fuv and (d.get('target') or '').startswith('牧野ゲン')]
    out('B42-9', '牧野ゲン「断る」→フウの攻撃（ゲン宛て）', f"{[(d['wall']) for d in gen][:2]} → {[(d['wall'], d['key']) for d in fa][:2]}", '断られた 14 秒後に倒すまで殴る')
    bd = {base(d['who']): d['v']['speed'] for d in by['body']}
    fus = bd[base(next(d['who'] for d in by['temperament'] if d['vid'] == fuv))]
    out('B42-10', 'フウの足の速さの順位（body.speed）', f"{rank_desc(list(bd.values()), fus)} 位／{len(bd)}", '35 人中 1 位')
    cards = tsv('persona_cards/persona_cards_b42.tsv')
    fc = [c for c in cards if c['vid'] == fuv][0]
    out('B42-11', 'フウの人格カード', f"{fc['values'][:40]}／{fc['flaw'][:30]}", '「上をめざし力でねじ伏せること。妥協は敗北だ」「すぐに手が出る」')
    lst = [l for l in speech_lines('b42') if 'モモの野郎は綺麗に片付け' in l]
    out('B42-12', '「モモの野郎は綺麗に片付けてやったぜ」', [l[:50] for l in lst], '加害者の独り言')


if __name__ == '__main__':
    part = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if part in ('all', '4'):
        obs4()
    if part in ('all', '5'):
        obs5()
    if part in ('all', '6'):
        obs6()
    if part in ('all', 'b'):
        brun()
