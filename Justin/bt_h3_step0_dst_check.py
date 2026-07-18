# -*- coding: utf-8 -*-
"""
Justin / A Ailesi / H3 - ADIM 0: DST/saat-eslesme BAGIMSIZ dogrulamasi
(justin_backtest_onkontrol_standardi.md Madde 1 - her turde bagimsiz tekrarlanir)

Bu script H1/H2 turlerinin sonuclarini KOPYALAMAZ - ayni yontemi (canli-an capraz kontrolu +
hafta-sonu-gecis/DST donum noktasi taramasi) BU TUR icin SIFIRDAN, guncel veriyle, M30 ve M15
uzerinde (H3'un fiilen kullandigi iki zaman dilimi) calistirir.
"""
import json
import numpy as np
import MetaTrader5 as mt5
from datetime import datetime, timezone, date as _date

assert mt5.initialize(), f"MT5 initialize basarisiz: {mt5.last_error()}"
SYMBOL = "GOLD"
mt5.symbol_select(SYMBOL, True)

out = {}

# (a) Canli-an capraz kontrolu: epoch-UTC okuma vs Python sistem saati (VPS yerel + UTC)
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
    "not": "VPS yerel isletim sistemi saati TST/Turkiye saatidir (2016'dan beri sabit UTC+3, DST "
           "uygulanmiyor) - bu MT5 SUNUCU saatinin sabit oldugu anlamina GELMEZ, asagidaki "
           "hafta-sonu-gecis taramasi sunucu davranisini M30/M15 barlariyla AYRICA olcer.",
}

DST_TRANSITIONS = ["2025-03-30", "2025-10-26", "2026-03-29"]


def dst_check(rates, tf_label, bar_min):
    n = len(rates)
    t = rates['time'].astype(np.int64)
    hours = np.array([datetime.fromtimestamp(int(x), tz=timezone.utc).hour for x in t])
    dates = np.array([str(datetime.fromtimestamp(int(x), tz=timezone.utc).date()) for x in t])
    # hafta sonu (haftalik piyasa kapanisi) tespiti: ardisik barlar arasi bosluk > 23 saat
    gap_threshold_sec = 23 * 3600
    gaps = []
    for i in range(1, n):
        dt = t[i] - t[i - 1]
        if dt > gap_threshold_sec:
            gaps.append({"friday_close_utc_hour": int(hours[i - 1]), "friday_close_date": dates[i - 1],
                         "sunday_open_utc_hour": int(hours[i]), "sunday_open_date": dates[i]})

    def hour_mode_window(gaps_list, center_date_str, days=21):
        cy, cm, cd = [int(x) for x in center_date_str.split("-")]
        center = _date(cy, cm, cd)
        before, after = [], []
        for g in gaps_list:
            gy, gm, gd = [int(x) for x in g["friday_close_date"].split("-")]
            gdate = _date(gy, gm, gd)
            delta = (gdate - center).days
            if -days <= delta < 0:
                before.append(g["friday_close_utc_hour"])
            elif 0 <= delta <= days:
                after.append(g["friday_close_utc_hour"])
        return before, after

    dst_res = []
    for tr in DST_TRANSITIONS:
        before, after = hour_mode_window(gaps, tr)
        kayma = (bool(before) and bool(after) and
                 (max(set(before), key=before.count) != max(set(after), key=after.count)))
        dst_res.append({"gecis_tarihi": tr, "oncesi_cuma_kapanis_saatleri": before,
                         "sonrasi_cuma_kapanis_saatleri": after, "kayma_tespit_edildi_mi": bool(kayma)})
    return {"tf": tf_label, "bar_min": bar_min, "toplam_hafta_sonu_gecis_sayisi": len(gaps),
            "dst_kontrolu": dst_res}


rates_m30 = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M30, 0, 99999)
rates_m15 = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M15, 0, 99999)

dst_m30 = dst_check(rates_m30, "M30", 30)
dst_m15 = dst_check(rates_m15, "M15", 15)
print("M30 DST kontrolu:", json.dumps(dst_m30["dst_kontrolu"], ensure_ascii=False))
print("M15 DST kontrolu:", json.dumps(dst_m15["dst_kontrolu"], ensure_ascii=False))

out["M30"] = dst_m30
out["M15"] = dst_m15
out["sonuc_notu"] = (
    "H3 icin BAGIMSIZ tekrarlanan dogrulama (M30 rejim/kanal ufku + M15 giris-zamanlama ufku, "
    "H1/H2 turlerinden devralinmadi - script bu tur icin yeniden calistirildi). Beklenen: MT5/XM "
    "sunucusu AB/Kibris DST takvimini izliyor (yaz GMT+3, kis GMT+2); asagidaki kayma_tespit_edildi_mi "
    "alanlari True ise bu beklentiyle TUTARLI (hafta kapanis saati DST gecisinde 1 saat kayiyor demektir)."
)

with open(r"C:\MilaYatirim\Justin\bt_h3_step0_dst_check_output.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2, default=str)

mt5.shutdown()
print("TAMAMLANDI")
