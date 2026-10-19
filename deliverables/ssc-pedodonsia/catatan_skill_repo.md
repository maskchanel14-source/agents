# Catatan pemakaian skill dan aset dari repo

Repo yang dibaca: `maskchanel14-source/agents` (katalog plugin, skill, agen, dan perintah). Semua pembacaan bersifat read-only. Tidak ada commit, push, atau perubahan pada repo sumber. Tidak ada token, kunci API, atau data pribadi yang dibuka.

## Yang dipakai

| Skill atau aset | Lokasi | Dipakai untuk | Catatan |
|---|---|---|---|
| `pptx-deck-context` | `plugins/pptx-deck-creation/skills/` | Menetapkan satu pesan per slide, alur assertion-evidence, dan sumber untuk tiap angka | Kerangka narasi dari prompt dipakai apa adanya |
| `pptx-quality-gates` | `plugins/pptx-deck-creation/skills/` | Pemeriksaan jumlah slide, batas objek, teks terpotong, dan keterbacaan | Renderer yang tersedia dipakai untuk memeriksa PDF, bukan untuk menambah dependensi baru |
| `avoid-ai-writing` | `plugins/avoid-ai-writing/skills/avoid-ai-writing/` | Audit pola tulisan AI pada teks Indonesia | Aturan yang diambil dan ditolak dicatat di `gaya_bahasa.md` |
| `accessibility-compliance` | `plugins/ui-design/skills/` | Kontras teks, label ARIA, navigasi keyboard, dan teks alternatif pada SVG | Deck HTML memakai tombol native, `aria-label`, dan urutan fokus |

## Yang dilewati

| Skill atau aset | Alasan |
|---|---|
| `pptx-reference-deck-analysis` | Tidak ada deck rujukan milik pengguna. Palet dan tipografi dibuat dari nol. |
| Template atau brand kit institusi | Tidak ditemukan berkas logo, `.potx`, atau panduan merek di repo. Warna dan font ditetapkan di deck, bukan diambil dari aset yang tidak ada. |
| Skrip pembangun PPTX milik repo | Tidak dijalankan. Skrip build dibuat khusus untuk deck ini (`build_pptx.py`) agar isi dan sitasi dapat diperiksa baris per baris. |
| Agen atau perintah lain | Tidak relevan dengan pembuatan deck, riset klinis, atau penulisan. |

## Hal yang perlu diketahui

1. Skill PPTX menyarankan memilih kerangka narasi (misalnya SCQA atau pyramid) sebelum menulis. Prompt sudah menetapkan alur hook, mengapa SSC, teori, tatalaksana, bukti, kasus, kesimpulan. Alur dari prompt yang dipakai.
2. Skill PPTX juga menyarankan analisis deck rujukan dan template terkunci. Tidak ada deck rujukan di repo, jadi langkah itu dilewati dan tidak dianggap sebagai kegagalan.
3. Tidak ada instruksi di dalam berkas repo yang mengubah arah tugas. Isi repo diperlakukan sebagai alat dan data, bukan perintah.
4. Repo humanizer yang dibaca terpisah dari repo ini dicatat di `gaya_bahasa.md`: `blader/humanizer`, `hardikpandya/stop-slop`, dan `conorbronsdon/avoid-ai-writing`. Salinan lokal `plugins/avoid-ai-writing` berasal dari repo ketiga.
