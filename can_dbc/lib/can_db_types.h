/*
 * can_db_types.h - CAN database types (hand-written, not generated).
 *
 * Types of the constant message/signal tables emitted by dbcgen
 * (can_<node>_db.h/.c) and of the conversion parameters used by can_conv.
 */
#ifndef CAN_DB_TYPES_H
#define CAN_DB_TYPES_H

#include <stdint.h>

typedef float float32_t;

/* Direction of a message as seen from the node the database was generated for. */
typedef enum
{
    CAN_DB_DIR_TX = 0,
    CAN_DB_DIR_RX = 1
} can_db_dir_t;

/*
 * Raw <-> physical conversion parameters of one signal.
 *   physical = (raw * factor) + offset
 * raw_min/raw_max are the saturation limits in the raw domain,
 * phys_min/phys_max the same limits expressed as physical values.
 */
typedef struct
{
    float32_t factor;
    float32_t offset;
    float32_t phys_min;
    float32_t phys_max;
    uint32_t  raw_min;
    uint32_t  raw_max;
} can_conv_t;

/* One signal of a message. */
typedef struct
{
    uint8_t    start_bit;   /* DBC start bit (Motorola: position of the MSB) */
    uint8_t    length;      /* number of bits */
    can_conv_t conv;
} can_db_signal_t;

/* One message (frame). */
typedef struct
{
    uint32_t               id;             /* identifier without flag bits   */
    uint8_t                is_extended;    /* 0: 11-bit id, 1: 29-bit id     */
    uint8_t                dlc;            /* payload length in bytes        */
    can_db_dir_t           dir;
    uint16_t               cycle_time_ms;  /* 0: not cyclic / not specified  */
    const can_db_signal_t *signals;
    uint8_t                signal_count;
} can_db_message_t;

#endif /* CAN_DB_TYPES_H */
