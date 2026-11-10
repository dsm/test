# Doğrulama Planı

## Yaklaşım

- **Gereksinim tabanlı**: her test `docs/requirements.md` içindeki bir LLR'ye bağlıdır. Testsiz
  gereksinim veya gereksinimsiz test paketi başarısız yapar (`test_traceability.py`).
- **Üretilen kod, kaynak kod olarak doğrulanır**: doğrulama üretecin doğruluğuna dayanmaz; bu nedenle
  üretecin araç kalifikasyonu (DO-330) yerine çıktısının doğrulanması esas alınır.
- **Bağımsızlık**: beklenen değerler hiçbir zaman üreteçten gelmez.
  - `oracle/bit_oracle.py`: Motorola yerleşimini bit bit yürüyen referans model (üretecin
    pencere/kaydırma/maske formüllerini kullanmaz).
  - `cantools`: üçüncü parti DBC ayrıştırıcı ve kodlayıcı. Beklenen model (mesajlar, sinyaller, alıcılar)
    bununla okunur; kodlama/çözme sonuçları ikinci oracle olarak karşılaştırılır.
  - Elle hesaplanmış altın vektörler: iki oracle'dan da bağımsız çapa.
  - `oracle/conv_oracle.py`: dönüşüm için float32 referans modeli; ayrıca rasyonel aritmetikle bağımsız
    beklentiler (ızgara noktaları, tam yarımlar, hata sınırı).
- **Kara kutu**: testler derlenmiş nesne kodu, `harness_gen.py` tarafından (beklenen modelden) üretilen
  ince bir C sürücüsü üzerinden çalıştırır. Sürücü yalnız argüman aktarır; karar vermez.

## Test sınıfları

| Sınıf | Dosya | İçerik |
|---|---|---|
| VT-GOLDEN | `test_pack_unpack.py` | Her mesaj için elle hesaplanmış vektör |
| VT-LAYOUT | `test_pack_unpack.py` | Her sinyalin her biti için walking-1 / walking-0; çerçevede tam bir bit değişir |
| VT-FRAMEBITS | `test_pack_unpack.py` | Çerçevenin her biti (ve tümleyeni): yalnız sahibi olan üye, doğru ağırlıkla değişir |
| VT-MASK | `test_pack_unpack.py` | Tip genişliğinde / sinyalden geniş değerler komşu sinyali ve boş bitleri bozmaz |
| VT-ROUNDTRIP | `test_pack_unpack.py` | Rastgele (sabit tohumlu) vektörler; gönderen node'un paketi her alıcı node'da çözülür; `pack(unpack(b)) == b & maske` |
| VT-BUFFER | `test_pack_unpack.py` | Ön dolgulu tampon ve koruma baytları: tam `DLC` bayt yazılır; unpack girişi değiştirmez, tüm üyeleri yazar, `DLC` ötesini okumaz |
| VT-DB | `test_db.py` | Tablolar, indeks sabitleri, makrolar, üye tipleri beklenen modelle birebir |
| VT-CONV | `test_conv.py` | Yuvarlama, tam yarımlar, saturasyon, ±Inf, NaN, decode, gidiş-dönüş hata sınırı |
| VT-NODE | `test_node.py` | `nm` ile sembol kümesi; yapı üyeleri; `:rx` / `:tx` varyantları |
| VT-GEN | `test_generator.py` | Ret kuralları (hata kodu, dosya yazılmaması), determinizm, güncellik, ayrıştırıcı eşdeğerliği |
| VT-STATIC | `test_static.py` | gcc/clang katı uyarılar, cppcheck, cppcheck MISRA eklentisi, yapısal kurallar |
| VT-ENDIAN | `test_static.py` + `ppc` varyantı | Big-endian hedefte (PowerPC, qemu) yürütme |
| VT-COVERAGE | `tools/coverage_gate.py` | Fonksiyonel testlerden %100 satır ve dal kapsaması |
| VT-MUTATION | `tools/mutation_check.py` | Hata enjeksiyonu ile test paketinin yeterliliği |

## Derleme varyantları

Fonksiyonel testler (`-m functional`) her varyantta aynen çalıştırılır:

| Varyant | Amaç |
|---|---|
| `gcc` | Referans; tam paket |
| `clang` | Derleyici bağımsızlığı |
| `asan` | ASan + UBSan + float dönüşüm taşması: bellek hataları ve tanımsız davranış |
| `ppc` | Big-endian, 32 bit hedef |
| `cov` | Yapısal kapsama ölçümü |

Üretilen kod ve kütüphane her varyantta katı uyarı kümesiyle (`-std=c99 -pedantic -Wall -Wextra
-Wconversion -Wsign-conversion ... -Werror`) derlenir.

## Yapısal kapsama

Kapsama, yalnız gereksinim tabanlı fonksiyonel testlerin çalıştırılmasıyla ölçülür. Pack/unpack
dalsızdır; `can_conv.c` içindeki her karar tek koşulludur, dolayısıyla dal kapsaması MC/DC'ye denktir.
Kapı: tüm dosyalarda %100 satır ve %100 dal.

## Mutasyon kontrolü

Üretilen koda ve kütüphaneye tek tek hata enjekte edilir: kaydırma sabiti, maske, bayt indeksi,
`|=`→`&=`, `|`→`&`, sıfırlama satırının silinmesi, tablo sabitleri (tamsayı, float, yön) ve dönüşüm
mantığı (işleç, sınır, yuvarlama eşiği). Her mutant fonksiyonel testlerle çalıştırılır; yakalanmayan
mutant kampanyayı başarısız yapar. Yapısı gereği eşdeğer mutantlar (tam temsil edilebilir sınırda
`>=`/`>`) listeye alınmamıştır.

## Sınırlamalar

- MISRA kontrolü cppcheck eklentisinin uyguladığı kural alt kümesiyle sınırlıdır; tam MISRA C:2012
  uyumluluk beyanı için sertifikalı bir analiz aracı gerekir. Kütüphane tek başına analiz edildiğinde
  beklenen tavsiye niteliğindeki bulgular (2.3, 2.4, 2.5, 8.7) testte gerekçesiyle listelenmiştir.
- Testler ana makinede (x86-64) ve emülatörde (PowerPC) koşar; hedef donanım ve hedef derleyici
  üzerindeki yürütme proje entegrasyonunda aynı test paketiyle tekrarlanmalıdır.
- NULL işaretçi ve kısa tampon, pack/unpack için ön koşul ihlalidir; çağıran katmanın sorumluluğundadır.
