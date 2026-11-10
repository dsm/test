/*
 * can_vcu.h - CAN message pack/unpack (raw values).
 *
 * GENERATED FILE - DO NOT EDIT.
 * Generator : dbcgen 1.0.0
 * Source    : example_vehicle.dbc
 * SHA-256   : cd508e7d0359ae9ced385bbd6d432c46be738e263894852d68857ae0b2596786
 * Node      : VCU (tx+rx)
 */
#ifndef CAN_VCU_H
#define CAN_VCU_H

#include <stdint.h>

/* ---- VCU_Heartbeat (0x10, standard, DLC 3, TX) ---- */

#define CAN_VCU_HEARTBEAT_FRAME_ID (0x10U)
#define CAN_VCU_HEARTBEAT_IS_EXTENDED (0U)
#define CAN_VCU_HEARTBEAT_DLC (3U)
#define CAN_VCU_HEARTBEAT_CYCLE_TIME_MS (50U)

typedef struct
{
    uint8_t hb_counter; /* raw, 8 bit */
    uint8_t vcu_state; /* raw, 4 bit */
    uint16_t sw_version; /* raw, 12 bit */
} can_vcu_heartbeat_t;

/*
 * Writes data[0..2]. Each value is masked to its signal
 * length, unused bits are written as 0.
 * Preconditions: msg != NULL, data != NULL.
 */
void can_vcu_heartbeat_pack(const can_vcu_heartbeat_t *msg, uint8_t *data);

/* ---- VCU_Command (0x100, standard, DLC 8, TX) ---- */

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
    uint8_t contactor_request; /* raw, 1 bit */
    uint8_t charge_enable; /* raw, 1 bit */
    uint16_t max_charge_current; /* raw, 10 bit [A] */
    uint8_t cmd_counter; /* raw, 4 bit */
} can_vcu_command_t;

/*
 * Writes data[0..7]. Each value is masked to its signal
 * length, unused bits are written as 0.
 * Preconditions: msg != NULL, data != NULL.
 */
void can_vcu_command_pack(const can_vcu_command_t *msg, uint8_t *data);

/* ---- BMS_Status (0x200, standard, DLC 8, RX) ---- */

#define CAN_BMS_STATUS_FRAME_ID (0x200U)
#define CAN_BMS_STATUS_IS_EXTENDED (0U)
#define CAN_BMS_STATUS_DLC (8U)
#define CAN_BMS_STATUS_CYCLE_TIME_MS (100U)

#define CAN_BMS_STATUS_STATE_INIT (0U)
#define CAN_BMS_STATUS_STATE_STANDBY (1U)
#define CAN_BMS_STATUS_STATE_DRIVE (2U)
#define CAN_BMS_STATUS_STATE_CHARGE (3U)
#define CAN_BMS_STATUS_STATE_FAULT (4U)
#define CAN_BMS_STATUS_STATE_SHUTDOWN (5U)

typedef struct
{
    uint16_t pack_voltage; /* raw, 16 bit [V] */
    uint16_t pack_current; /* raw, 12 bit [A] */
    uint16_t soc; /* raw, 10 bit [%] */
    uint8_t state; /* raw, 3 bit */
    uint8_t contactor_closed; /* raw, 1 bit */
    uint8_t fault_active; /* raw, 1 bit */
    uint8_t max_cell_temp; /* raw, 8 bit [degC] */
    uint8_t alive_counter; /* raw, 4 bit */
} can_bms_status_t;

/*
 * Reads data[0..7] and writes every member of *msg.
 * Preconditions: msg != NULL, data != NULL.
 */
void can_bms_status_unpack(can_bms_status_t *msg, const uint8_t *data);

/* ---- MCU_Status (0x300, standard, DLC 8, RX) ---- */

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
 * Reads data[0..7] and writes every member of *msg.
 * Preconditions: msg != NULL, data != NULL.
 */
void can_mcu_status_unpack(can_mcu_status_t *msg, const uint8_t *data);

/* ---- MCU_Diag (0x310, standard, DLC 6, RX) ---- */

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
 * Reads data[0..5] and writes every member of *msg.
 * Preconditions: msg != NULL, data != NULL.
 */
void can_mcu_diag_unpack(can_mcu_diag_t *msg, const uint8_t *data);

/* ---- BMS_Energy (0x18FF50E5, extended, DLC 8, RX) ---- */

#define CAN_BMS_ENERGY_FRAME_ID (0x18FF50E5U)
#define CAN_BMS_ENERGY_IS_EXTENDED (1U)
#define CAN_BMS_ENERGY_DLC (8U)
#define CAN_BMS_ENERGY_CYCLE_TIME_MS (1000U)

typedef struct
{
    uint64_t energy_counter; /* raw, 40 bit [Wh] */
    uint8_t balancing_active; /* raw, 1 bit */
    uint8_t derating; /* raw, 1 bit */
    uint32_t charge_cycles; /* raw, 22 bit */
} can_bms_energy_t;

/*
 * Reads data[0..7] and writes every member of *msg.
 * Preconditions: msg != NULL, data != NULL.
 */
void can_bms_energy_unpack(can_bms_energy_t *msg, const uint8_t *data);

#endif /* CAN_VCU_H */
