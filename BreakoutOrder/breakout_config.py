"""
breakout_config.py
Breakout Order icin TV/harici kaynak - MT5/XM fiyat offset degerleri.

Yontem: breakout_price_compare.py (30 ornek, 10sn araliklarla, ~5 dakika).
Deger = TV kaynak fiyati - MT5 Bid ortalamasi (ort_diff_bid).
Kullanim: MT5/XM'de bir fiyat seviyesi belirlerken, TV/harici kaynaktan
okunan (orn. chart'ta gorulen) seviyeden bu offset dusulerek MT5 karsiligi
bulunur: mt5_seviye = tv_seviye - OFSET.

Ilk finalize: 16 Temmuz 2026, 14:00 TR (gunduz, Londra/NY ortak seans) olcumu.
Ham veriler: breakout_price_comparison_{ad}_20260716_1400.csv
"""

GOLD_OFFSET   = 0.262833   # TV kaynagi: OANDA:XAUUSD
SILVER_OFFSET = 0.03487    # TV kaynagi: OANDA:XAGUSD
US100_OFFSET  = 28.061667  # TV kaynagi: FPMARKETS:US100
EURUSD_OFFSET = 0.0000947  # TV kaynagi: FX:EURUSD (FXCM verisi)
USDJPY_OFFSET = 0.011433   # TV kaynagi: FX:USDJPY (FXCM verisi)
GBPJPY_OFFSET = 0.015533   # TV kaynagi: FX:GBPJPY (FXCM verisi)

# GER40_OFFSET: HENUZ FINALIZE EDILMEDI.
# 16 Temmuz 2026 14:00 (gunduz) olcumu: 9.75 — 15 Temmuz 2026 23:51 (gece,
# sadece referans, kullanilmayacak) olcumunden (13.46) belirgin farkli.
# Ikinci bir gunduz olcumu bekleniyor (Task Scheduler: "Breakout Price
# Compare - Ger40 Tekrar"), sonuc gelince iki gunduz olcumunun ortalamasi
# GER40_OFFSET olarak buraya eklenecek. TV kaynagi: FPMARKETS:GER40.
