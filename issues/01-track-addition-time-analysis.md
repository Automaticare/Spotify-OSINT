# Issue #01 — Şarkı Ekleme Saati Analizi

## Amaç

Playlist sahibinin hangi saatlerde şarkı eklediğini tespit edip pattern çıkarmak. "Bu kişi gece 2-4 arası aktif" gibi davranışsal içgörüler üretmek.

## Motivasyon

- Şarkı sözü analizi tek başına yeterli OSINT değil — zamansal pattern'ler kişinin yaşam döngüsü hakkında ek bilgi veriyor
- Tweet malzemesi: saat dağılım verileri paylaşılabilir ve ilgi çekici
- Haftalık mood raporunun (gelecek issue) temel yapı taşı

## Mevcut Altyapı

- `tracked_tracks.detected_at` (TIMESTAMPTZ, DEFAULT NOW()) zaten her şarkının tespit zamanını tutuyor
- Veritabanında yeterli veri biriktiğinde analiz yapılabilir durumda

## Timezone

- Saat analizi **Europe/Istanbul (UTC+3)** timezone'u üzerinden yapılır
- `detected_at` UTC olarak kaydediliyor, analiz sırasında Türkiye saatine dönüştürülür
- **NOT:** README'ye timezone bilgisi eklenecek (Issue #03 kapsamında)

## Kapsam

### Commit 1: DB query + saat pattern analiz fonksiyonu
- `database.py`'ye `get_tracks_for_report(playlist_id, days=7)` ekle
  - Son N gündeki track'lerin `detected_at`, `track_name`, `artist_names` bilgilerini döndürür
- `src/report.py` oluştur
  - `detected_at` saatlerinden pattern çıkar: en aktif saat aralığı, gece/gündüz dağılımı, toplam ekleme sayısı
  - Saat dağılımını yapılandırılmış dict olarak döndür

### Commit 2: Groq ile Türkçe saat analizi özeti + Telegram bildirimi
- `src/report.py`'ye Groq entegrasyonu
  - Saat pattern verisini Groq'a gönderip Türkçe pesimist yorum üret
- `telegram.py`'ye `send_time_analysis_notification()` ekle

### Commit 3: GitHub Actions weekly cron + entrypoint
- `src/report.py`'ye `__main__` entrypoint
- `.github/workflows/weekly_report.yml` — haftada 1 kez (Pazartesi 09:00 UTC) tetiklenen workflow

## Doğrulama

- `python -m src.report` ile manuel çalıştır
- Telegram'a saat analizi mesajı geldiğini kontrol et
- Veritabanında yeterli veri yoksa birkaç farklı saatte mock kayıt ekleyerek test et

## Kapsam Dışı

- Haftalık mood raporu (Issue #02)
- README güzelleştirme (Issue #03)
- Analiz metinlerinin veritabanına kaydedilmesi (haftalık rapor issue'sunda ele alınacak)
