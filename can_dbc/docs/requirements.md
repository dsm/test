# Gereksinimler

Bu doküman, DBC'den üretilen CAN pack/unpack kodu, veritabanı tabloları, dönüşüm kütüphanesi ve
üretecin kendisi için gereksinimleri tanımlar. Her düşük seviye gereksinim (LLR) en az bir doğrulama
testine bağlıdır; bağ `tests/verification` altındaki testlerde `@pytest.mark.req(...)` ile kurulur ve
`build/report/trace_matrix_<varyant>.md` dosyasına raporlanır.

Tanımlar:
- **DBC bit numarası**: `bayt * 8 + bayt_içi_bit`; bayt içi bit 7 baytın en anlamlı bitidir.
- **Motorola sinyali**: start bit sinyalin en anlamlı bitidir (MSB). Bir sonraki daha az anlamlı bit
  aynı baytta bir alt bittir; baytın 0. bitinden sonra bir sonraki baytın 7. biti gelir.
- **Çerçeve sırası**: sinyallerin MSB konumuna göre sırası (önce küçük bayt, bayt içinde önce büyük bit).
- **raw**: çerçevedeki işaretsiz tamsayı değer. **fiziksel** = `raw * factor + offset`.

## Yüksek seviye gereksinimler (HLR)

| Kimlik | Gereksinim |
|---|---|
| HLR-001 | Yazılım, DBC'de tanımlı CAN mesajlarını raw sinyal değerlerinden paketleyebilmeli ve raw sinyal değerlerine çözebilmelidir. |
| HLR-002 | Üretilen kod işlemci endianness'inden bağımsız olmalı, tanımsız/gerçeklemeye bağlı davranış içermemeli ve sabit çalışma süresine sahip olmalıdır. |
| HLR-003 | Her node için yalnız o node'un gönderdiği/aldığı mesajlar ve sinyaller üretilmeli; yön (yalnız RX / yalnız TX) seçilebilmelidir. |
| HLR-004 | Mesaj ve sinyal özellikleri, donanım yapılandırması (mailbox/filtre) ve dönüşüm için sabit tablolar olarak sunulmalıdır. |
| HLR-005 | Fiziksel değer ile raw değer arasındaki dönüşüm, saturasyonlu ve ayrı bir kütüphane olarak sağlanmalıdır. |
| HLR-006 | Üreteç, aslına uygun çeviremeyeceği hiçbir DBC içeriğini sessizce kabul etmemeli; çıktısı tekrarlanabilir ve kaynağına izlenebilir olmalıdır. |

## Düşük seviye gereksinimler (LLR)

### Pack (`can_<mesaj>_pack`)

| Kimlik | Gereksinim | Üst |
|---|---|---|
| LLR-PACK-001 | Pack, her sinyalin raw değerini DBC'deki Motorola yerleşimine göre çerçeveye yazmalıdır: değerin `length-1` numaralı biti start bit konumuna, sonraki bitler Motorola sırasına göre yerleştirilir. | HLR-001 |
| LLR-PACK-002 | Pack, yapı üyesindeki değerin yalnız en düşük `length` bitini kullanmalıdır; fazla bitler başka hiçbir sinyali ve kullanılmayan biti etkilememelidir. | HLR-001 |
| LLR-PACK-003 | Pack, `data[0..DLC-1]` içinde hiçbir sinyale ait olmayan bitleri 0 yazmalıdır. | HLR-001 |
| LLR-PACK-004 | Pack, tamponun önceki içeriğinden bağımsız olarak tam `data[0..DLC-1]` baytlarını yazmalı, bu aralığın dışına yazmamalıdır. | HLR-002 |

### Unpack (`can_<mesaj>_unpack`)

| Kimlik | Gereksinim | Üst |
|---|---|---|
| LLR-UNPACK-001 | Unpack, her yapı üyesine ilgili sinyalin DBC'deki Motorola yerleşimine göre çerçeveden okunan raw değerini yazmalıdır. | HLR-001 |
| LLR-UNPACK-002 | Bir yapı üyesinin değeri yalnız kendi sinyaline ait çerçeve bitlerine bağlı olmalıdır (diğer sinyaller ve kullanılmayan bitler etkilememelidir). | HLR-001 |
| LLR-UNPACK-003 | Unpack yalnız `data[0..DLC-1]` baytlarını okumalı, girişi değiştirmemeli ve yapının tüm üyelerini yazmalıdır. | HLR-002 |

### Arayüz

| Kimlik | Gereksinim | Üst |
|---|---|---|
| LLR-IF-001 | Her mesaj için `can_<mesaj>_t` yapısı üretilmelidir; üyeler çerçeve sırasındadır, adları sinyal adının snake_case halidir ve tipi sinyal uzunluğunu alan en küçük `uint8_t/uint16_t/uint32_t/uint64_t` tipidir. | HLR-001 |
| LLR-IF-002 | Her mesaj için `CAN_<MESAJ>_FRAME_ID`, `_IS_EXTENDED`, `_DLC`, `_CYCLE_TIME_MS` makroları ve değer tablosu (VAL_) olan sinyaller için `CAN_<MESAJ>_<SINYAL>_<AD>` makroları üretilmelidir. | HLR-004 |

### Veritabanı (`can_<node>_db`)

| Kimlik | Gereksinim | Üst |
|---|---|---|
| LLR-DB-001 | `can_<node>_messages` tablosu node için seçilen her mesaja tam bir kayıt içermelidir: kimlik (bayrak biti olmadan), `is_extended`, DLC, yön (TX=0, RX=1), çevrim süresi (`GenMsgCycleTime`, yoksa 0), sinyal tablosu ve sinyal sayısı. | HLR-004 |
| LLR-DB-002 | Mesaj tablosu kimliğe göre kesin artan sırada olmalıdır. | HLR-004 |
| LLR-DB-003 | `can_<mesaj>_signals` tablosu node için seçilen her sinyali çerçeve sırasında içermelidir: DBC start bit, uzunluk, `factor` ve `offset` (en yakın float32). | HLR-004 |
| LLR-DB-004 | `CAN_<NODE>_MSG_<MESAJ>` ve `CAN_<MESAJ>_SIG_<SINYAL>` sabitleri ilgili tablo konumuna eşit olmalı; `..._COUNT` sabitleri tablo boyutunu vermelidir. | HLR-004 |
| LLR-DB-005 | Saturasyon sınırları: DBC `[min\|max]` verilmişse `raw_min = ceil((min-offset)/factor)`, `raw_max = floor((max-offset)/factor)`, sinyalin tam ölçeğine kırpılır; `[0\|0]` ise tam ölçek kullanılır. `phys_min/phys_max` bu raw sınırların fiziksel karşılığıdır. 32 bitten geniş sinyallerde (yalnız `factor=1, offset=0` kabul edilir) sınırlar `0..0xFFFFFFFF` olur. | HLR-005 |

### Dönüşüm kütüphanesi (`can_conv`)

| Kimlik | Gereksinim | Üst |
|---|---|---|
| LLR-CONV-001 | `can_conv_encode`, `(phys - offset) / factor` değerini (float32 aritmetiği) en yakın tamsayıya, tam yarımlarda yukarı yuvarlayarak döndürmelidir. | HLR-005 |
| LLR-CONV-002 | `can_conv_encode` sonucu `[raw_min, raw_max]` aralığına sature edilmelidir; `+Inf` için `raw_max`, `-Inf` için `raw_min` döner. | HLR-005 |
| LLR-CONV-003 | `can_conv_encode`, NaN girişi için `raw_min` döndürmelidir. | HLR-005 |
| LLR-CONV-004 | `can_conv_decode`, raw değeri önce `[raw_min, raw_max]` aralığına sature etmeli, sonra `raw * factor + offset` değerini (float32) döndürmelidir. | HLR-005 |

### Node seçimi

| Kimlik | Gereksinim | Üst |
|---|---|---|
| LLR-NODE-001 | Node'un gönderdiği (BO_ göndericisi olduğu) her mesaj için tüm sinyalleriyle `pack` üretilmeli, `unpack` üretilmemelidir. | HLR-003 |
| LLR-NODE-002 | Node'un en az bir sinyalinin alıcısı olduğu her mesaj için `unpack` üretilmeli, `pack` üretilmemelidir; yapı ve tablolar yalnız node'un alıcısı olduğu sinyalleri içermelidir. | HLR-003 |
| LLR-NODE-003 | `NODE:rx` ile yalnız RX mesajları, `NODE:tx` ile yalnız TX mesajları üretilmelidir; node ile ilgisi olmayan mesajlar için hiçbir sembol üretilmemelidir. | HLR-003 |

### Üreteç (`dbcgen`)

| Kimlik | Gereksinim | Üst |
|---|---|---|
| LLR-GEN-001 | Üreteç desteklenmeyen içeriği (Intel bayt sırası, signed sinyal, multiplex, float sinyal, DLC > 8, tanınmayan ifade) hata koduyla reddetmeli, sıfırdan farklı çıkış kodu vermeli ve hiçbir dosya yazmamalıdır. | HLR-006 |
| LLR-GEN-002 | Üreteç tutarsız içeriği (çakışan sinyaller, DLC'yi aşan sinyal, geçersiz uzunluk/ölçek/aralık, geçersiz veya yinelenen ad, bilinmeyen node) hata koduyla reddetmeli ve hiçbir dosya yazmamalıdır. | HLR-006 |
| LLR-GEN-003 | Aynı girdiyle üretim bayt-bayt aynı çıktıyı vermelidir; her dosyanın başlığında üreteç sürümü ve DBC dosyasının SHA-256 özeti bulunmalıdır. Depodaki `generated/` içeriği güncel üretimle aynı olmalıdır. | HLR-006 |
| LLR-GEN-004 | Üretecin DBC ayrıştırıcısının çıkardığı model (node'lar, mesajlar, sinyaller, ölçekler, alıcılar, değer tabloları, çevrim süreleri) bağımsız bir ayrıştırıcının (cantools) modeliyle aynı olmalıdır. | HLR-006 |

### Kod kalitesi

| Kimlik | Gereksinim | Üst |
|---|---|---|
| LLR-CODE-001 | Üretilen kod ve kütüphane ISO C99'a uygun olmalı; `gcc` ve `clang` ile katı uyarı kümesi altında uyarısız derlenmeli ve statik analizde hata vermemelidir. | HLR-002 |
| LLR-CODE-002 | Kod işlemci endianness'inden bağımsız olmalıdır: union, bitfield, işaretçi tip dönüşümü ve `memcpy` kullanılmamalı; aynı testler big-endian hedefte de geçmelidir. | HLR-002 |
| LLR-CODE-003 | Pack/unpack fonksiyonları dalsız ve döngüsüz düz kod olmalıdır (`if`, `switch`, `for`, `while`, `do`, `goto`, `?:` ve fonksiyon çağrısı içermez). | HLR-002 |
