# youtube-to-m3u8

Generator playlist M3U pribadi dari channel YouTube Live publik (mis. siaran
berita free-to-air), pakai `yt-dlp` + GitHub Actions untuk auto-refresh.

**Catatan penggunaan:** hanya untuk channel YouTube publik/gratis yang
memang kamu tonton sendiri. Jangan tambahkan stream berbayar atau yang
dilindungi DRM — ini di luar cakupan tool ini dan melanggar ToS
penyedia layanan tersebut.

## Cara kerja

1. `channels.txt` berisi daftar channel YouTube (format `Nama|tvg-id|URL`).
2. `generate_m3u.py` memanggil `yt-dlp -g` untuk tiap channel, mengambil URL
   HLS (`.m3u8`) langsung dari siaran live yang sedang berjalan.
3. Hasilnya ditulis ke `playlist.m3u` dalam format M3U standar.
4. GitHub Actions (`update-playlist.yml`) menjalankan langkah 2–3 setiap
   4 jam dan meng-commit ulang `playlist.m3u` jika berubah — karena URL
   HLS dari YouTube kedaluwarsa setelah beberapa jam.

## Setup

### 1. Buat repo di GitHub

Buat repository baru (bisa privat) di GitHub, lalu clone ke komputer kamu.

### 2. Salin file-file ini ke repo

Salin `generate_m3u.py`, `channels.txt`, `requirements.txt`, dan folder
`.github/workflows/update-playlist.yml` ke dalam repo tersebut.

### 3. Sesuaikan channels.txt

Edit `channels.txt`, tambah/hapus baris sesuai channel YouTube Live yang
mau kamu masukkan. Format:

```
Nama Channel|tvg-id|https://www.youtube.com/channel/<CHANNEL_ID>/live
```

### 4. Tes lokal (opsional tapi disarankan)

```bash
pip install -r requirements.txt
python generate_m3u.py
cat playlist.m3u
```

Pastikan `playlist.m3u` berisi entri dengan URL yang diawali `https://` dan
berakhiran mengandung `.m3u8`.

### 5. Push ke GitHub

```bash
git add .
git commit -m "Initial commit"
git push
```

### 6. Aktifkan Actions

- Buka tab **Actions** di repo GitHub kamu, terima prompt untuk
  mengaktifkan workflows jika muncul.
- Buka **Settings → Actions → General → Workflow permissions**, pilih
  **Read and write permissions** supaya job bisa commit balik ke repo.
- Jalankan workflow sekali secara manual (tombol **Run workflow** di tab
  Actions) untuk memastikan semuanya berjalan.

### 7. Pakai playlist di aplikasi IPTV

Setelah minimal satu kali commit berhasil, playlist bisa diakses via raw
URL:

```
https://raw.githubusercontent.com/<username>/<nama-repo>/main/playlist.m3u
```

Masukkan URL itu ke aplikasi IPTV kamu (VLC, Tivimate, dll) sebagai sumber
playlist. Karena workflow jalan tiap 4 jam, aplikasi IPTV akan selalu
mengambil URL HLS yang masih segar tiap kali me-refresh playlist.

## Menambah channel lain

Tambahkan baris baru di `channels.txt` dengan format yang sama. Pastikan
URL yang dipakai adalah channel YouTube publik (pakai akhiran `/live`),
bukan video privat/unlisted atau siaran berbayar.

## Kalau muncul error "Sign in to confirm you're not a bot"

YouTube kadang menandai IP milik GitHub Actions (atau cloud provider lain)
sebagai mencurigakan dan meminta autentikasi sebelum memberi URL stream.
Ini bukan bug di script — perlu ditambahkan cookies dari akun YouTube yang
sudah login.

**Sebelum mulai — soal keamanan:** sebaiknya pakai akun Google
kedua/khusus untuk ini, bukan akun pribadi/utama kamu. Menjalankan
ekstraksi otomatis berulang dengan cookies suatu akun (walau jarang)
bisa membuat akun itu kena flag oleh YouTube. Kalau itu terjadi pada
akun sekunder, dampaknya minim; kalau itu akun utama kamu, lebih
merepotkan.

1. **Login ke YouTube** di browser pakai akun yang akan dipakai.
2. **Export cookies** pakai ekstensi browser resmi yang direkomendasikan
   yt-dlp: [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
   untuk Chrome, atau [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)
   untuk Firefox. Buka youtube.com saat masih login, lalu export cookies
   untuk domain tersebut ke file `cookies.txt` (format Netscape — baris
   pertama harus `# HTTP Cookie File` atau `# Netscape HTTP Cookie File`).
3. **Simpan sebagai GitHub Secret**, jangan pernah commit file ini ke
   repo:
   - Buka repo → **Settings → Secrets and variables → Actions → New
     repository secret**
   - Nama: `YT_COOKIES`
   - Value: tempel seluruh isi file `cookies.txt`
4. Push perubahan `generate_m3u.py` dan `update-playlist.yml` yang sudah
   mendukung cookies (lihat repo ini), lalu jalankan ulang workflow.
5. Cookies session bisa kedaluwarsa setelah beberapa minggu/bulan. Kalau
   suatu saat workflow gagal lagi dengan pesan yang sama, cukup ulangi
   langkah 1–3 untuk memperbarui secret `YT_COOKIES`.

