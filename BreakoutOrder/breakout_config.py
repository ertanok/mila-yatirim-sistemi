"""
breakout_config.py
Breakout Order icin TV/harici kaynak - MT5/XM fiyat offset degerleri.

Yontem: breakout_price_compare.py (30 ornek, 10sn araliklarla, ~5 dakika).
Iki ayri offset olcusu tutulur:
  {SEMBOL}_BID_OFFSET = TV kaynak fiyati - MT5 Bid ortalamasi (ort_diff_bid)
  {SEMBOL}_ASK_OFFSET = TV kaynak fiyati - MT5 Ask ortalamasi (ort_diff_ask)

Kullanim (emir gonderme mantigi - Breakout Order trading agent'i henuz
yazilmadi, bu kural ileride o kod icin gecerli):
  - BUY_STOP  hesaplamasi ASK_OFFSET kullanir (alis fiyat karsilastirmasi ask'a gore yapilir)
  - SELL_STOP hesaplamasi BID_OFFSET kullanir (satis fiyat karsilastirmasi bid'e gore yapilir)
  mt5_seviye = tv_seviye - ILGILI_OFFSET

Ilk finalize: 16 Temmuz 2026, 14:00 TR (gunduz, Londra/NY ortak seans) olcumu.
Ham veriler: breakout_price_comparison_{ad}_20260716_1400.csv
"""

GOLD_BID_OFFSET   = 0.262833    # TV kaynagi: OANDA:XAUUSD
GOLD_ASK_OFFSET   = -0.3115

SILVER_BID_OFFSET = 0.03487     # TV kaynagi: OANDA:XAGUSD
SILVER_ASK_OFFSET = -0.035597

US100_BID_OFFSET  = 28.061667   # TV kaynagi: FPMARKETS:US100
US100_ASK_OFFSET  = 25.246667

EURUSD_BID_OFFSET = 0.0000947   # TV kaynagi: FX:EURUSD (FXCM verisi)
EURUSD_ASK_OFFSET = -0.000099

USDJPY_BID_OFFSET = 0.011433    # TV kaynagi: FX:USDJPY (FXCM verisi)
USDJPY_ASK_OFFSET = -0.012667

GBPJPY_BID_OFFSET = 0.015533    # TV kaynagi: FX:GBPJPY (FXCM verisi)
GBPJPY_ASK_OFFSET = -0.022433

# GER40_BID_OFFSET / GER40_ASK_OFFSET: HENUZ FINALIZE EDILMEDI.
# 16 Temmuz 2026 14:00 (gunduz) olcumu: Bid=9.75, Ask=7.45 — 15 Temmuz 2026
# 23:51 (gece, sadece referans, kullanilmayacak) olcumunden (Bid=13.46)
# belirgin farkli. Ikinci bir gunduz olcumu bekleniyor (Task Scheduler:
# "Breakout Price Compare - Ger40 Tekrar", 17 Temmuz 14:00), sonuc gelince
# iki gunduz olcumunun (Bid ve Ask ayri ayri) ortalamasi buraya eklenecek.
# TV kaynagi: FPMARKETS:GER40.
