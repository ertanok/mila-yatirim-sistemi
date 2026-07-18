import csv, random, math

random.seed(42)
KASA = 2000.0

def load_pnl(path, split_col=None, split_val=None):
    pnls = []
    with open(path, encoding='utf-8-sig') as f:
        r = csv.DictReader(f)
        for row in r:
            if split_col is not None:
                if row.get(split_col) != split_val:
                    continue
            pnls.append(float(row['pnl_usd']))
    return pnls

def monte_carlo(pnls, kasa=KASA, n_iter=500):
    worst_dds = []
    for _ in range(n_iter):
        shuffled = pnls[:]
        random.shuffle(shuffled)
        equity = 1.0
        peak = 1.0
        mdd = 0.0
        for p in shuffled:
            equity += p / kasa
            peak = max(peak, equity)
            dd = (peak - equity) / peak * 100 if peak > 0 else 0
            mdd = max(mdd, dd)
        worst_dds.append(mdd)
    worst_dds.sort()
    pct5 = worst_dds[int(len(worst_dds) * 0.05)]
    median = worst_dds[len(worst_dds) // 2]
    worst = worst_dds[-1]
    return pct5, median, worst

def max_consecutive_losses(pnls):
    # in original (non-shuffled) order
    max_run = 0
    cur = 0
    for p in pnls:
        if p < 0:
            cur += 1
            max_run = max(max_run, cur)
        else:
            cur = 0
    return max_run

def profit_concentration(pnls):
    wins = sorted([p for p in pnls if p > 0], reverse=True)
    total_profit = sum(wins)
    top3 = sum(wins[:3])
    top10 = sum(wins[:10])
    if total_profit == 0:
        return None, None, 0
    return (top3/total_profit*100, top10/total_profit*100, len(wins))

def win_rate(pnls):
    wins = sum(1 for p in pnls if p > 0)
    return wins/len(pnls)*100 if pnls else 0

def theoretical_max_losing_streak(wr_pct):
    wr = wr_pct/100
    if wr <= 0 or wr >= 1:
        return None
    return math.log(0.05)/math.log(1-wr)

def avg_loss(pnls):
    losses = [p for p in pnls if p < 0]
    return sum(losses)/len(losses) if losses else 0

def analyze(name, pnls):
    print(f"\n=== {name} (n={len(pnls)}) ===")
    if not pnls:
        print("BOS - veri yok")
        return
    pct5, med, worst = monte_carlo(pnls)
    print(f"Monte Carlo (500 shuffle, oransal DD%): pct5(en kotu %5)={pct5:.2f}%  medyan={med:.2f}%  en_kotu={worst:.2f}%")
    mcl = max_consecutive_losses(pnls)
    wr = win_rate(pnls)
    theo = theoretical_max_losing_streak(wr)
    print(f"Gercek max ardisik kayip: {mcl}  | WR={wr:.2f}%  | Teorik beklenen (log(0.05)/log(1-WR)): {theo:.2f}" if theo else f"Gercek max ardisik kayip: {mcl} | WR={wr:.2f}%")
    al = avg_loss(pnls)
    print(f"Ortalama kayip (USD, sadece zarar islemler): {al:.2f}")
    print(f"  -> {mcl} pes pese kayip olursa: {mcl} x {al:.2f} = {mcl*al:.2f} USD ({mcl*al/KASA*100:.2f}% / {KASA:.0f} kasa)")
    top3, top10, nwins = profit_concentration(pnls)
    if top3 is not None:
        print(f"Kar konsantrasyonu: en iyi 3 islem = toplam karin %{top3:.2f}'si | en iyi 10 = %{top10:.2f} (kazanan islem sayisi={nwins})")
    else:
        print("Kar konsantrasyonu hesaplanamadi (kazanan islem yok)")

# H1 Test split
h1_test = load_pnl('backtest_A_ailesi_H1_islem_logu_tam.csv', 'split', 'test')
h1_train = load_pnl('backtest_A_ailesi_H1_islem_logu_tam.csv', 'split', 'train')
analyze('H1 - Test (OOS)', h1_test)
analyze('H1 - Train', h1_train)

# H2 Test split
h2_test = load_pnl('backtest_A_ailesi_H2_islem_logu_tam.csv', 'split', 'test')
h2_train = load_pnl('backtest_A_ailesi_H2_islem_logu_tam.csv', 'split', 'train')
analyze('H2 - Test (OOS)', h2_test)
analyze('H2 - Train', h2_train)

# H3 pooled OOS
h3_oos = load_pnl('backtest_A_ailesi_H3_islem_logu_oos.csv')
h3_train = load_pnl('backtest_A_ailesi_H3_islem_logu_train_foldlar.csv')
analyze('H3 - Havuzlanmis OOS', h3_oos)
analyze('H3 - Train (fold birlesik)', h3_train)
