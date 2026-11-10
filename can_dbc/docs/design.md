# Tasarım

## 1. Pack/unpack: "big-endian pencere" yöntemi

DBC'deki tüm sinyaller Motorola olduğundan çerçeve tek bir big-endian sayı gibi ele alınır: çerçeve bit
indeksi 0, bayt 0'ın 7. biti; indeks 63, bayt 7'nin 0. bitidir. Bu numaralamada **her sinyal bitişik bir
alandır**. Üreteç her sinyal için aşağıdaki sabitleri hesaplar (`generator/dbcgen/layout.py`):

```
top        = (start / 8) * 8 + (7 - start % 8)     # MSB'nin çerçeve indeksi
bottom     = top + length - 1                      # LSB'nin çerçeve indeksi
first_byte = top / 8,  last_byte = bottom / 8
shift      = last_byte * 8 + 7 - bottom            # LSB'nin last_byte içindeki konumu
mask       = (1 << length) - 1
```

Üretilen kod sinyalin dokunduğu baytları yalnız kaydırma ve OR ile bir pencereye taşır
(en fazla 4 bayt → `uint32_t`, 5–8 bayt → `uint64_t`), `shift` kadar kaydırır ve `mask` uygular.

Örnek (`BMS_Status`, `Soc : 27|10@0+`): `top = 28`, `bottom = 37`, baytlar 3..4, `shift = 2`, `mask = 0x3FF`.

```c
/* pack */
window32 = ((uint32_t)msg->soc & 0x3FFU) << 2U;
data[3] |= (uint8_t)((window32 >> 8U) & 0xFFU);
data[4] |= (uint8_t)(window32 & 0xFFU);

/* unpack */
window32 = ((uint32_t)data[3] << 8U) | (uint32_t)data[4];
msg->soc = (uint16_t)((window32 >> 2U) & 0x3FFU);
```

Doğrulama vektörü (`BMS_Status`): raw `PackVoltage=4000, PackCurrent=2500, Soc=800, State=2,
ContactorClosed=1, FaultActive=0, MaxCellTemp=65, AliveCounter=5` → `0F A0 9C 4C 81 40 41 05`.

Özellikler ve gerekçeleri:

| Özellik | Gerekçe |
|---|---|
| Yalnız `uint8_t` dizi erişimi, kaydırma, maske | İşlemci endianness'inden bağımsız; union, bitfield, işaretçi dönüşümü yok |
| Dal, döngü, tablo, fonksiyon çağrısı yok | Sabit çalışma süresi ve stack; tek çağrı tüm yapısal kapsamayı sağlar |
| Tüm sabitler `U`/`ULL` sonekli, işlemler `uint32_t`/`uint64_t` üzerinde | Örtük işaretli tamsayı yükseltmesi ve tanımsız kaydırma yok |
| Pack önce `data[0..DLC-1]` baytlarını sıfırlar, sonra OR'lar | Kullanılmayan bitler deterministik olarak 0 |
| Pack her değeri `mask` ile sınırlar | Aralık dışı değer komşu sinyali bozamaz |
| Her sinyal bloğunun üstünde DBC referans yorumu | Kod ↔ DBC izlenebilirliği, gözden geçirme kolaylığı |
| RX yapısında yalnız abone olunan sinyaller | Deaktif/ölü kod üretilmez |

DLC ve aralık kontrolü bilinçli olarak bu katmanda yoktur: DLC sürücü/donanım seviyesinde doğrulanır,
aralık `can_conv` tarafından saturasyonla ele alınır.

## 2. Veritabanı

`can_<node>_messages[]` (kimliğe göre artan) ve mesaj başına `can_<mesaj>_signals[]` (çerçeve sırasında)
tabloları `lib/can_db_types.h` içindeki tiplerle üretilir. `CAN_<NODE>_MSG_<MESAJ>` ve
`CAN_<MESAJ>_SIG_<SINYAL>` sabitleri tablo indeksleridir. ROM tasarrufu için isim string'i üretilmez.

Saturasyon sınırları DBC `[min|max]` alanından tam (rasyonel) aritmetikle türetilir:
`raw_min = ceil((min - offset) / factor)`, `raw_max = floor((max - offset) / factor)`, sinyalin tam
ölçeğine kırpılır; `[0|0]` tam ölçek demektir. 32 bitten geniş sinyaller yalnız raw kullanılır
(`factor = 1`, `offset = 0` zorunlu); tablo sınırları `0..0xFFFFFFFF` olur ve `can_conv` bu sinyaller
için kullanılmaz.

## 3. Dönüşüm kütüphanesi

`can_conv_encode`: `raw_f = (phys - offset) / factor`; `raw_f >= raw_max` ise `raw_max`,
`raw_f > raw_min` ise yarımlarda yukarı yuvarlanmış değer, aksi halde (aralık altı veya NaN) `raw_min`.
Karşılaştırmalar float alanında yapıldığı için tamsayıya dönüşüm hiçbir girişte taşmaz.
`can_conv_decode`: raw değeri sınırlar arasına sature eder, `raw * factor + offset` döndürür.
Her karar tek koşulludur (karar kapsaması = MC/DC). `factor > 0` üreteç tarafından garanti edilir.

float32 çözünürlüğü 24 bittir; bundan geniş raw aralığına sahip ölçekli sinyallerde dönüşüm doğal
olarak en yakın temsil edilebilir değere yuvarlanır.

## 4. Üreteç

`dbc_parser` → `validate` → `nodesel` → `layout` → `emit_c` / `emit_db`. Yalnız Python standart
kütüphanesi kullanılır. Hata durumunda hiçbir dosya yazılmaz; hata kodları `errors.py` içindedir
(E001 sözdizimi/desteklenmeyen ifade, E002 Intel, E003 signed, E004 multiplex, E005 float,
E006 çakışma, E007 DLC aşımı, E008 ad, E009 node, E010 DLC, E011 ölçek, E012 uzunluk, E013 aralık,
E014 kimlik, E015 boş mesaj/node).
