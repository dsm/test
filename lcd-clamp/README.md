# Ekran (LCD) Sabitleme Klipsi – 3D Baskı

Telefon ekranı / arka kapak yapıştırırken kullanılan metal klipsin 3D yazıcı için yeniden tasarlanmış hali. **Tamamen baskı**, metal vida/somun gerekmez.

![Montaj](img/assembly.png)

## Parçalar (1 klips için)

| Dosya | Adet | Malzeme | Baskı yönü |
|---|---|---|---|
| `stl/frame.stl` – C gövde | 1 | PETG / PLA | Yan yatık (dosyadaki gibi) – destek yok |
| `stl/jaw.stl` – kayar çene | 1 | PETG / PLA | Yan yatık, kanal yukarı – destek yok |
| `stl/screw.stl` – vida + topuz | 1 | PETG / PLA | Topuz aşağıda, dik – destek yok |
| `stl/nut.stl` – dişli somun | 1 | PETG / PLA | Düz – destek yok |
| `stl/pad.stl` – koruma pedi | 2 | TPU (95A) | Düz |

4'lü set için hepsini 4 kez basın. Ped basamıyorsanız 17×17 mm, ~1 mm keçe/silikon/EVA kesip yuvalara yapıştırın.

**Önerilen ayarlar:** 0.4 nozul, 0.16–0.2 mm katman, 4 duvar (perimeter), %30+ dolgu. Gövde yan yatık basıldığı için katmanlar C profiline paraleldir; sıkma kuvveti katmanları ayırmaya çalışmaz.

## Montaj

1. Somunu gövdenin üst kolundaki altıgen yuvaya **alttan** bastırın (gevşekse bir damla yapıştırıcı).
2. Vidayı yukarıdan somuna çevirerek takın, alt ucu kolun altından çıksın.
3. Çeneyi yandan vidanın ucundaki diske kaydırın – "tık" diye oturur. Çenenin düz arka yüzü gövdeye dayanır, böylece dönmez.
4. Pedleri alt kol ve çene altındaki yuvalara yapıştırın.

Topuzu çevirince çene aşağı iner (sıkar), geri çevirince disk çeneyi yukarı çeker.

## Ölçüler

- Gövde: 20 × 28 × 43 mm, vida ile toplam ≈ 60 mm
- Çene açıklığı: 0 – 16 mm (pedlerle ≈ 15 mm)
- Diş: Ø12 mm, 3 mm adım, 45° yanak (baskı dostu)

## Özelleştirme

`lcd_clamp.scad` dosyasını OpenSCAD'de açın (Customizer paneli):

- `t_clear` – vida somunda sıkıysa 0.30–0.35 yapın, boşluklu ise 0.2
- `nut_fit` – somun yuvaya girmiyorsa artırın
- `max_open`, `reach`, `W` – açıklık, derinlik, genişlik

STL üretmek için: `openscad -o stl/screw.stl -D 'part="screw"' lcd_clamp.scad` (`frame`, `jaw`, `nut`, `pad`, `plate`, `assembly`).
