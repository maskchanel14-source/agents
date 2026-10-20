# docs/screenshots/

Screenshot dashboard **belum bisa digenerate dari lingkungan build ini** (sandbox
tanpa browser dan unduhan browser diblokir — lihat DECISIONS.md D9).

Cara mengisi folder ini (5 menit di Windows):

```bat
:: 1. jalankan bot (dashboard terbuka otomatis)
venv\Scripts\python.exe -m bot --mode paper

:: 2. di terminal lain, ambil screenshot headless
venv\Scripts\pip install playwright
venv\Scripts\playwright install chromium
venv\Scripts\python scripts\take_screenshots.py
```

Hasil: `overview-desktop.png`, `scanner-desktop.png`, `risk-desktop.png`
(plus varian laptop/wide). Script juga memeriksa error console dan menolak
hasil jika ada (exit code 2).

Checklist verifikasi visual:

- [ ] Tidak ada elemen rusak/tumpang tindih di 1920x1080, 1366x768, 2560x1080
- [ ] Boot sequence bisa di-skip
- [ ] KPI terbaca < 3 detik tanpa scroll
- [ ] Tabel Scanner sortable/filter berfungsi
- [ ] Empty state tampil saat belum ada peluang
- [ ] Indikator koneksi (WS/API/DATA) bukan warna saja — ada teks
- [ ] Mode PAPER tampil hijau; LIVE (jika diuji) merah mencolok
