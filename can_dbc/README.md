# can_dbc — DBC'den C CAN pack/unpack üreteci

DBC dosyasından, gömülü hedefler için CAN mesajlarını paketleyen/çözen C99 kodu ve mesaj veritabanı
üretir. Kapsam: **Motorola (big-endian) bayt sırası, unsigned sinyaller, klasik CAN (DLC ≤ 8)**.
Bunların dışındaki içerik (Intel, signed, multiplex, float, CAN FD) sessizce atlanmaz; üreteç hata
koduyla durur.

| Katman | Dosya | Kaynak | İçerik |
|---|---|---|---|
| Pack/Unpack | `generated/<node>/can_<node>.h/.c` | üretilir | Yalnız bit yerleşimi; dalsız, döngüsüz, raw unsigned |
| Veritabanı | `generated/<node>/can_<node>_db.h/.c` | üretilir | `const` tablolar: mesajlar, sinyaller, dönüşüm parametreleri |
| Dönüşüm | `lib/can_conv.h/.c` | elle yazılmış | Saturasyonlu fiziksel ↔ raw dönüşüm |
| Tipler | `lib/can_db_types.h` | elle yazılmış | Veritabanı yapı tipleri |

Ayrıntılar: [tasarım](docs/design.md), [gereksinimler](docs/requirements.md),
[doğrulama planı](docs/verification_plan.md).

## Üretim

```sh
PYTHONPATH=generator python3 -m dbcgen --dbc dbc/example_vehicle.dbc --out generated \
    --node VCU --node BMS --node MCU --node DISPLAY:rx
```

- `NODE` — node'un gönderdiği mesajlar için `pack`, aldığı mesajlar için `unpack`.
- `NODE:rx` — yalnız `unpack` (yalnız RX); `NODE:tx` — yalnız `pack`.
- RX yapıları ve tabloları yalnız node'un alıcısı olduğu sinyalleri içerir (kullanılmayan kod/veri üretilmez).
- Üreteç yalnız Python standart kütüphanesini kullanır; çıktı deterministiktir ve başlığında DBC'nin
  SHA-256 özetini taşır.

## Kullanım

```c
#include "can_bms.h"
#include "can_bms_db.h"
#include "can_conv.h"

/* Gönderim: fiziksel -> raw (saturasyonlu) -> çerçeve */
can_bms_status_t status = { 0 };
uint8_t data[CAN_BMS_STATUS_DLC];

status.soc = (uint16_t)can_conv_encode(
    &can_bms_status_signals[CAN_BMS_STATUS_SIG_SOC].conv, 80.0F);
status.state = CAN_BMS_STATUS_STATE_DRIVE;
can_bms_status_pack(&status, data);

/* Alım: çerçeve -> raw -> fiziksel */
can_vcu_command_t command;
can_vcu_command_unpack(&command, rx_data);
float32_t limit_a = can_conv_decode(
    &can_vcu_command_signals[CAN_VCU_COMMAND_SIG_MAX_CHARGE_CURRENT].conv,
    command.max_charge_current);
```

Mailbox/filtre kurulumu veritabanı tablosu üzerinden yapılır:

```c
for (uint8_t i = 0U; i < (uint8_t)CAN_BMS_MSG_COUNT; i++)
{
    const can_db_message_t *m = &can_bms_messages[i];   /* kimliğe göre artan sıralı */
    if (m->dir == CAN_DB_DIR_RX)
    {
        hal_can_add_rx_filter(m->id, m->is_extended, m->dlc);
    }
    else
    {
        hal_can_config_tx_box(m->id, m->is_extended, m->dlc, m->cycle_time_ms);
    }
}
```

Sözleşme: `pack`/`unpack` işaretçileri NULL olamaz ve tampon en az `DLC` bayt olmalıdır; DLC ve aralık
kontrolü bu katmanda yapılmaz (DLC sürücü/donanım seviyesinde, aralık `can_conv` içinde ele alınır).
`pack` her değeri sinyal uzunluğuna maskeler, kullanılmayan bitleri 0 yazar.

## Doğrulama

```sh
pip install -r tests/requirements.txt
make test       # tam test paketi, referans derleme (gcc)
make verify     # + clang, ASan/UBSan, big-endian (PowerPC/qemu), kapsama kapısı, rapor
make mutation   # + mutasyon kontrolü (testlerin kendisinin doğrulanması)
```

Raporlar `build/report/` altına yazılır: `verification_report.md`, `trace_matrix_<varyant>.md`
(gereksinim ↔ test), `coverage.md`, `mutation.md`, JUnit XML. Aracı kurulu olmayan adımlar geçti
sayılmaz, **NOT RUN** olarak raporlanır (big-endian adımı `gcc-powerpc-linux-gnu` ve
`qemu-user-static`, statik analiz `cppcheck` gerektirir).
