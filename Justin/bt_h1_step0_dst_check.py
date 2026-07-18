# -*- coding: utf-8 -*-
"""
Justin / A Ailesi / H1 - ADIM 0: DST/saat-eslesme BAGIMSIZ dogrulamasi
(justin_backtest_onkontrol_standardi.md Madde 1 - her turde bagimsiz tekrarlanir)

Bu script onceki turlerin (Hipotez1/2/3) sonuclarini KOPYALAMAZ - ayni yontemi (canli-an
capraz kontrolu + DST donum noktasi taramasi) bu tur icin SIFIRDAN, guncel veriyle calistirir.
"""
import MetaTrader5 as mt5
import numpy as np
from datetime import datetime, timezone, timedelta
import json

assert mt5.initialize(), "MT5 initialize basarisiz"
SYMBOL = "GOLD"
mt5.symbol_select(SYMBOL, True)

out = {}

# (a) Canli-an capraz kontrolu: epoch-UTC okuma vs Python sistem saati (VPS yerel)
tick = mt5.symbol_info_tick(SYMBOL)
epoch_utc = datetime.fromtimestamp(tick.time, tz=timezone.utc)
sys_utc_now = datetime.now(timezone.utc)
sys_local_now = datetime.now()

out["canli_capraz_kontrol"] = {
    "tick_time_epoch": int(tick.time),
    "tick_time_utc": str(epoch_utc),
    "python_sistem_utc_now": str(sys_utc_now),
    "python_sistem_yerel_now": str(sys_local_now),
    "fark_saniye_tick_vs_sysutc": (sys_utc_now - epoch_utc).total_seconds(),
}

rates_h1 = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_H1, 0, 5)
last_bar_time = datetime.fromtimestamp(int(rates_h1[-1]['time']), tz=timezone.utc)
out["son_h1_bar_sunucu_zamani_ham"] = str(last_bar_time)
out["vps_yerel_simdi"] = str(datetime.now())
out["vps_utc_simdi"] = str(datetime.now(timezone.utc))

print(json.dumps(out, indent=2, ensure_ascii=False, default=str))

# (b) DST donum noktasi taramasi - H1 verisiyle, Cuma kapanis saatlerini birkac DST gecis
# tarihi civarinda incele (bagimsiz, script yeniden yazilarak - onceki turden kopyalanmadi)
rates_h1_all = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_H1, 0, 99999)
times = [datetime.fromtimestamp(int(t), tz=timezone.utc).replace(tzinfo=None) for t in rates_h1_all['time']]


def nearest_friday_close_hour(target_date):
    cands = [t for t in times if abs((t.date() - target_date).days) <= 6 and t.weekday() == 4]
    if not cands:
        return None
    last_day = max(cands).date()
    day_bars = [t for t in cands if t.date() == last_day]
    return max(day_bars) if day_bars else None


dst_checkpoints = [
    ("2025-03-30", "AB/Kibris yaz-saatine gecis"),
    ("2025-10-26", "AB/Kibris kis-saatine gecis"),
    ("2026-03-29", "AB/Kibris yaz-saatine gecis (bu yil)"),
]
dst_results = []
for dstr, label in dst_checkpoints:
    d = datetime.strptime(dstr, "%Y-%m-%d").date()
    before = nearest_friday_close_hour(d - timedelta(days=3))
    after = nearest_friday_close_hour(d + timedelta(days=4))
    dst_results.append({
        "donum_tarihi": dstr, "aciklama": label,
        "once_cuma_kapanis": str(before) if before else None,
        "sonra_cuma_kapanis": str(after) if after else None,
        "saat_once": before.hour if before else None,
        "saat_sonra": after.hour if after else None,
    })

out["dst_donum_taramasi"] = dst_results
print(json.dumps(dst_results, indent=2, ensure_ascii=False, default=str))

with open(r"C:\MilaYatirim\Justin\bt_h1_step0_dst_check_output.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2, default=str)

mt5.shutdown()
print("TAMAMLANDI")
