/*
 * can_mcu.h - CAN message pack/unpack (raw values).
 *
 * GENERATED FILE - DO NOT EDIT.
 * Generator : dbcgen 1.0.0
 * Source    : example_vehicle.dbc
 * SHA-256   : cd508e7d0359ae9ced385bbd6d432c46be738e263894852d68857ae0b2596786
 * Node      : MCU (tx+rx)
 */
#ifndef CAN_MCU_H
#define CAN_MCU_H

#include <stdint.h>

/* ---- VCU_Heartbeat (0x10, standard, DLC 3, RX) ---- */

#define CAN_VCU_HEARTBEAT_FRAME_ID (0x10U)
#define CAN_VCU_HEARTBEAT_IS_EXTENDED (0U)
#define CAN_VCU_HEARTBEAT_DLC (3U)
#define CAN_VCU_HEARTBEAT_CYCLE_TIME_MS (50U)

typedef struct
{
    uint8_t hb_counter; /* raw, 8 bit */
    uint8_t vcu_state; /* raw, 4 bit */
} can_vcu_heartbeat_t;

/*
 * Reads data[0..2] and writes every member of *msg.
 * Preconditions: msg != NULL, data != NULL.
 */
void can_vcu_heartbeat_unpack(can_vcu_heartbeat_t *msg, const uint8_t *data);

/* ---- VCU_Command (0x100, standard, DLC 8, RX) ---- */

#define CAN_VCU_COMMAND_FRAME_ID (0x100U)
#define CAN_VCU_COMMAND_IS_EXTENDED (0U)
#define CAN_VCU_COMMAND_DLC (8U)
#define CAN_VCU_COMMAND_CYCLE_TIME_MS (10U)

#define CAN_VCU_COMMAND_DRIVE_MODE_PARK (0U)
#define CAN_VCU_COMMAND_DRIVE_MODE_REVERSE (1U)
#define CAN_VCU_COMMAND_DRIVE_MODE_NEUTRAL (2U)
#define CAN_VCU_COMMAND_DRIVE_MODE_DRIVE (3U)
#define CAN_VCU_COMMAND_DRIVE_MODE_SPORT (4U)

typedef struct
{
    uint16_t torque_request; /* raw, 16 bit [Nm] */
    uint16_t speed_limit; /* raw, 13 bit [rpm] */
    uint8_t drive_mode; /* raw, 3 bit */
    uint8_t cmd_counter; /* raw, 4 bit */
} can_vcu_command_t;

/*
 * Reads data[0..7] and writes every member of *msg.
 * Preconditions: msg != NULL, data != NULL.
 */
void can_vcu_command_unpack(can_vcu_command_t *msg, const uint8_t *data);

/* ---- MCU_Status (0x300, standard, DLC 8, TX) ---- */

#define CAN_MCU_STATUS_FRAME_ID (0x300U)
#define CAN_MCU_STATUS_IS_EXTENDED (0U)
#define CAN_MCU_STATUS_DLC (8U)
#define CAN_MCU_STATUS_CYCLE_TIME_MS (20U)

typedef struct
{
    uint16_t motor_speed; /* raw, 16 bit [rpm] */
    uint16_t actual_torque; /* raw, 12 bit [Nm] */
    uint32_t odometer_ticks; /* raw, 30 bit */
    uint8_t inverter_temp; /* raw, 6 bit [degC] */
} can_mcu_status_t;

/*
 * Writes data[0..7]. Each value is masked to its signal
 * length, unused bits are written as 0.
 * Preconditions: msg != NULL, data != NULL.
 */
void can_mcu_status_pack(const can_mcu_status_t *msg, uint8_t *data);

/* ---- MCU_Diag (0x310, standard, DLC 6, TX) ---- */

#define CAN_MCU_DIAG_FRAME_ID (0x310U)
#define CAN_MCU_DIAG_IS_EXTENDED (0U)
#define CAN_MCU_DIAG_DLC (6U)
#define CAN_MCU_DIAG_CYCLE_TIME_MS (0U)

typedef struct
{
    uint32_t error_flags; /* raw, 32 bit */
    uint16_t error_count; /* raw, 9 bit */
    uint8_t limp_mode; /* raw, 1 bit */
} can_mcu_diag_t;

/*
 * Writes data[0..5]. Each value is masked to its signal
 * length, unused bits are written as 0.
 * Preconditions: msg != NULL, data != NULL.
 */
void can_mcu_diag_pack(const can_mcu_diag_t *msg, uint8_t *data);

#endif /* CAN_MCU_H */
