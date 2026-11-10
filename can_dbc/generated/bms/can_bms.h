/*
 * can_bms.h - CAN message pack/unpack (raw values).
 *
 * GENERATED FILE - DO NOT EDIT.
 * Generator : dbcgen 1.0.0
 * Source    : example_vehicle.dbc
 * SHA-256   : cd508e7d0359ae9ced385bbd6d432c46be738e263894852d68857ae0b2596786
 * Node      : BMS (tx+rx)
 */
#ifndef CAN_BMS_H
#define CAN_BMS_H

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
    uint8_t drive_mode; /* raw, 3 bit */
    uint8_t contactor_request; /* raw, 1 bit */
    uint8_t charge_enable; /* raw, 1 bit */
    uint16_t max_charge_current; /* raw, 10 bit [A] */
    uint8_t cmd_counter; /* raw, 4 bit */
} can_vcu_command_t;

/*
 * Reads data[0..7] and writes every member of *msg.
 * Preconditions: msg != NULL, data != NULL.
 */
void can_vcu_command_unpack(can_vcu_command_t *msg, const uint8_t *data);

/* ---- BMS_Status (0x200, standard, DLC 8, TX) ---- */

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
 * Writes data[0..7]. Each value is masked to its signal
 * length, unused bits are written as 0.
 * Preconditions: msg != NULL, data != NULL.
 */
void can_bms_status_pack(const can_bms_status_t *msg, uint8_t *data);

/* ---- BMS_Energy (0x18FF50E5, extended, DLC 8, TX) ---- */

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
 * Writes data[0..7]. Each value is masked to its signal
 * length, unused bits are written as 0.
 * Preconditions: msg != NULL, data != NULL.
 */
void can_bms_energy_pack(const can_bms_energy_t *msg, uint8_t *data);

#endif /* CAN_BMS_H */
