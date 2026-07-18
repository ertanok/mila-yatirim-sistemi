# -*- coding: utf-8 -*-
"""
Justin - Gold Scalping, Strateji Ailesi Plani ADIM 0 EK - M5 DONEM DOGRULAMASI
Tetikleyici: arastirmaci_gold_scalping_pivot_kanal_tarama_raporu.md (14 Temmuz),
"Onerilen Sonraki Adim" madde 3 (Arastirmaci'nin kendi onerdigi dogrulama).

Kapsam: Bu bir tam Yol1/pipeline turu veya yeni bir kanal taramasi DEGILDIR. Amac,
mevcut M5 GOLD verisinin (~17 ay, 2025-02-11/17 -> 2026-07) MT5 uzerinden daha genis/
farkli bir donemde elde EDILIP EDILEMEYECEGINI teknik olarak sinamaktir:
  1) maxbars=100000 siniri copy_rates_from_pos'un bir CAGRI-BASINA siniri mi, yoksa
     terminal/broker'in GERCEK M5 gecmis derinligi mi?
  2) copy_rates_range ile eski/genis bir tarih araligi istendiginde terminal server'dan
     ek gecmis indirip zamanla daha fazla veri veriyor mu (retry/delay ile)?
  3) Alternatif GOLD-benzeri sembollerin (XAUEUR, XAUCNH, XAUJPY) M5 gecmisi daha mi genis?

Veri kaynagi: XM/MT5 (dogrudan MetaTrader5 kutuphanesi), sunucu saati (GMT+3).
Izolasyon notu: Bu script MilaGold/Lisa/Signal GPT'ye ait hicbir dosyayi okumaz/kullanmaz,
sadece ham MT5 API cagrilari (fiyat verisi DEGIL, veri-varligi/derinligi) yapar.
"""
import MetaTrader5 as mt5
from datetime import datetime, timezone
import time
import json

assert mt5.initialize(), "MT5 initialize basarisiz"

SYMBOL = "GOLD"
mt5.symbol_select(SYMBOL, True)

out = {"olusturma_zamani_not": "Bu script calistirildiginda sistem saati kullanilir, "
                                "sonuclar output JSON'a yazilir."}


def ts(t):
    return datetime.fromtimestamp(int(t), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


# ------------------------------------------------------------------
# 1) maxbars terminal ayari
# ------------------------------------------------------------------
tinfo = mt5.terminal_info()
out["terminal_maxbars"] = tinfo.maxbars
out["terminal_build"] = tinfo.build
out["terminal_name"] = tinfo.name

# ------------------------------------------------------------------
# 2) M5 GOLD - pos0 penceresi (mevcut tarama ile ayni cagri)
# ------------------------------------------------------------------
r_pos0 = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M5, 0, 99999)
out["m5_pos0_99999"] = {
    "n_bar": int(len(r_pos0)),
    "baslangic": ts(r_pos0[0]['time']),
    "bitis": ts(r_pos0[-1]['time']),
}

# ------------------------------------------------------------------
# 3) Sayfalama testi: pos0 penceresinin OTESINE gecmise gidebiliyor muyuz?
#    (maxbars bir CAGRI-BASINA sinir ise, position offset ile daha eskiye
#    gidilebilmeli; gercek veri o noktada bitiyorsa ek bar donmemeli)
# ------------------------------------------------------------------
r_pos99999 = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M5, 99999, 99999)
out["m5_pos99999_99999"] = {
    "n_bar": int(len(r_pos99999)) if r_pos99999 is not None else None,
    "detay": [{"time": ts(row['time'])} for row in r_pos99999] if r_pos99999 is not None else None,
}

r_pos99998_5 = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M5, 99998, 5)
out["m5_pos99998_count5"] = {
    "n_bar": int(len(r_pos99998_5)) if r_pos99998_5 is not None else None,
    "zamanlar": [ts(row['time']) for row in r_pos99998_5] if r_pos99998_5 is not None else None,
}

r_pos100000 = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M5, 100000, 100)
out["m5_pos100000_count100"] = {
    "sonuc": None if r_pos100000 is None else int(len(r_pos100000)),
    "mt5_last_error": mt5.last_error(),
}

# ------------------------------------------------------------------
# 4) copy_rates_range ile eski tarih araliklari + retry/delay
#    (asenkron server-indirme ihtimalini test etmek icin)
# ------------------------------------------------------------------
eski_araliklar = [
    (datetime(2010, 1, 1), datetime(2010, 3, 1)),
    (datetime(2019, 1, 1), datetime(2019, 2, 28)),
    (datetime(2024, 1, 1), datetime(2024, 3, 1)),
]
range_testleri = []
for d0, d1 in eski_araliklar:
    denemeler = []
    for attempt in range(3):
        r = mt5.copy_rates_range(SYMBOL, mt5.TIMEFRAME_M5, d0, d1)
        denemeler.append({
            "deneme": attempt,
            "n_bar": None if r is None else int(len(r)),
            "ilk_bar_zamani": ts(r[0]['time']) if r is not None and len(r) > 0 else None,
            "mt5_last_error": mt5.last_error(),
        })
        time.sleep(5)
    range_testleri.append({
        "istenen_aralik": f"{d0.date()} -> {d1.date()}",
        "denemeler": denemeler,
    })
out["m5_eski_aralik_range_testi_retry"] = range_testleri

# H1 kontrol: fonksiyonun eski tarihlerde genel olarak calistigini teyit (M5'e ozgu mu?)
r_h1_2005 = mt5.copy_rates_range(SYMBOL, mt5.TIMEFRAME_H1, datetime(2005, 1, 1), datetime(2005, 3, 1))
out["h1_2005_kontrol"] = {
    "n_bar": None if r_h1_2005 is None else int(len(r_h1_2005)),
    "ilk_bar_zamani": ts(r_h1_2005[0]['time']) if r_h1_2005 is not None and len(r_h1_2005) > 0 else None,
}

# ------------------------------------------------------------------
# 5) Alternatif XAU-cross sembolleri (GOLD/USD disinda broker ne sunuyor,
#    M5 gecmisleri daha genis mi? -- FARKLI ENSTRUMAN, ikame degil, bilgi amacli)
# ------------------------------------------------------------------
alt_semboller = ["XAUEUR", "XAUCNH", "XAUJPY"]
alt_sonuc = {}
for sym in alt_semboller:
    ok = mt5.symbol_select(sym, True)
    r = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_M5, 0, 99999)
    if r is None or len(r) == 0:
        alt_sonuc[sym] = {"veri": "yok"}
        continue
    alt_sonuc[sym] = {
        "n_bar": int(len(r)),
        "baslangic": ts(r[0]['time']),
        "bitis": ts(r[-1]['time']),
    }
out["alternatif_xau_cross_semboller_m5"] = alt_sonuc

# Broker'da mevcut GOLD/XAU sembol listesi (bilgi amacli)
syms = mt5.symbols_get()
matches = [s.name for s in syms if 'GOLD' in s.name.upper() or 'XAU' in s.name.upper()]
out["broker_gold_xau_sembol_listesi"] = matches

with open(r"C:\MilaYatirim\Justin\arastirmaci_gold_scalping_pivot_kanal_m5_donem_dogrulama_output.json",
          "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2, default=str)

print("TAMAMLANDI. JSON yazildi.")
mt5.shutdown()
