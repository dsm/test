/*
 * can_display_db.h - CAN message/signal database.
 *
 * GENERATED FILE - DO NOT EDIT.
 * Generator : dbcgen 1.0.0
 * Source    : example_vehicle.dbc
 * SHA-256   : cd508e7d0359ae9ced385bbd6d432c46be738e263894852d68857ae0b2596786
 * Node      : DISPLAY (rx)
 */
#ifndef CAN_DISPLAY_DB_H
#define CAN_DISPLAY_DB_H

#include "can_db_types.h"

/* Index into can_display_messages (ascending frame id). */
typedef enum
{
    CAN_DISPLAY_MSG_VCU_HEARTBEAT = 0, /* VCU_Heartbeat (0x10, standard, DLC 3, RX) */
    CAN_DISPLAY_MSG_VCU_COMMAND, /* VCU_Command (0x100, standard, DLC 8, RX) */
    CAN_DISPLAY_MSG_BMS_STATUS, /* BMS_Status (0x200, standard, DLC 8, RX) */
    CAN_DISPLAY_MSG_MCU_STATUS, /* MCU_Status (0x300, standard, DLC 8, RX) */
    CAN_DISPLAY_MSG_MCU_DIAG, /* MCU_Diag (0x310, standard, DLC 6, RX) */
    CAN_DISPLAY_MSG_BMS_ENERGY, /* BMS_Energy (0x18FF50E5, extended, DLC 8, RX) */
    CAN_DISPLAY_MSG_COUNT
} can_display_msg_index_t;

/* Index into can_vcu_heartbeat_signals. */
typedef enum
{
    CAN_VCU_HEARTBEAT_SIG_HB_COUNTER = 0,
    CAN_VCU_HEARTBEAT_SIG_VCU_STATE,
    CAN_VCU_HEARTBEAT_SIG_SW_VERSION,
    CAN_VCU_HEARTBEAT_SIG_COUNT
} can_vcu_heartbeat_sig_index_t;

/* Index into can_vcu_command_signals. */
typedef enum
{
    CAN_VCU_COMMAND_SIG_DRIVE_MODE = 0,
    CAN_VCU_COMMAND_SIG_COUNT
} can_vcu_command_sig_index_t;

/* Index into can_bms_status_signals. */
typedef enum
{
    CAN_BMS_STATUS_SIG_PACK_VOLTAGE = 0,
    CAN_BMS_STATUS_SIG_PACK_CURRENT,
    CAN_BMS_STATUS_SIG_SOC,
    CAN_BMS_STATUS_SIG_STATE,
    CAN_BMS_STATUS_SIG_FAULT_ACTIVE,
    CAN_BMS_STATUS_SIG_MAX_CELL_TEMP,
    CAN_BMS_STATUS_SIG_COUNT
} can_bms_status_sig_index_t;

/* Index into can_mcu_status_signals. */
typedef enum
{
    CAN_MCU_STATUS_SIG_MOTOR_SPEED = 0,
    CAN_MCU_STATUS_SIG_ODOMETER_TICKS,
    CAN_MCU_STATUS_SIG_INVERTER_TEMP,
    CAN_MCU_STATUS_SIG_COUNT
} can_mcu_status_sig_index_t;

/* Index into can_mcu_diag_signals. */
typedef enum
{
    CAN_MCU_DIAG_SIG_ERROR_FLAGS = 0,
    CAN_MCU_DIAG_SIG_LIMP_MODE,
    CAN_MCU_DIAG_SIG_COUNT
} can_mcu_diag_sig_index_t;

/* Index into can_bms_energy_signals. */
typedef enum
{
    CAN_BMS_ENERGY_SIG_ENERGY_COUNTER = 0,
    CAN_BMS_ENERGY_SIG_DERATING,
    CAN_BMS_ENERGY_SIG_COUNT
} can_bms_energy_sig_index_t;

extern const can_db_signal_t can_vcu_heartbeat_signals[CAN_VCU_HEARTBEAT_SIG_COUNT];
extern const can_db_signal_t can_vcu_command_signals[CAN_VCU_COMMAND_SIG_COUNT];
extern const can_db_signal_t can_bms_status_signals[CAN_BMS_STATUS_SIG_COUNT];
extern const can_db_signal_t can_mcu_status_signals[CAN_MCU_STATUS_SIG_COUNT];
extern const can_db_signal_t can_mcu_diag_signals[CAN_MCU_DIAG_SIG_COUNT];
extern const can_db_signal_t can_bms_energy_signals[CAN_BMS_ENERGY_SIG_COUNT];
extern const can_db_message_t can_display_messages[CAN_DISPLAY_MSG_COUNT];

#endif /* CAN_DISPLAY_DB_H */
