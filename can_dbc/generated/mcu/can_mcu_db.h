/*
 * can_mcu_db.h - CAN message/signal database.
 *
 * GENERATED FILE - DO NOT EDIT.
 * Generator : dbcgen 1.0.0
 * Source    : example_vehicle.dbc
 * SHA-256   : cd508e7d0359ae9ced385bbd6d432c46be738e263894852d68857ae0b2596786
 * Node      : MCU (tx+rx)
 */
#ifndef CAN_MCU_DB_H
#define CAN_MCU_DB_H

#include "can_db_types.h"

/* Index into can_mcu_messages (ascending frame id). */
typedef enum
{
    CAN_MCU_MSG_VCU_HEARTBEAT = 0, /* VCU_Heartbeat (0x10, standard, DLC 3, RX) */
    CAN_MCU_MSG_VCU_COMMAND, /* VCU_Command (0x100, standard, DLC 8, RX) */
    CAN_MCU_MSG_MCU_STATUS, /* MCU_Status (0x300, standard, DLC 8, TX) */
    CAN_MCU_MSG_MCU_DIAG, /* MCU_Diag (0x310, standard, DLC 6, TX) */
    CAN_MCU_MSG_COUNT
} can_mcu_msg_index_t;

/* Index into can_vcu_heartbeat_signals. */
typedef enum
{
    CAN_VCU_HEARTBEAT_SIG_HB_COUNTER = 0,
    CAN_VCU_HEARTBEAT_SIG_VCU_STATE,
    CAN_VCU_HEARTBEAT_SIG_COUNT
} can_vcu_heartbeat_sig_index_t;

/* Index into can_vcu_command_signals. */
typedef enum
{
    CAN_VCU_COMMAND_SIG_TORQUE_REQUEST = 0,
    CAN_VCU_COMMAND_SIG_SPEED_LIMIT,
    CAN_VCU_COMMAND_SIG_DRIVE_MODE,
    CAN_VCU_COMMAND_SIG_CMD_COUNTER,
    CAN_VCU_COMMAND_SIG_COUNT
} can_vcu_command_sig_index_t;

/* Index into can_mcu_status_signals. */
typedef enum
{
    CAN_MCU_STATUS_SIG_MOTOR_SPEED = 0,
    CAN_MCU_STATUS_SIG_ACTUAL_TORQUE,
    CAN_MCU_STATUS_SIG_ODOMETER_TICKS,
    CAN_MCU_STATUS_SIG_INVERTER_TEMP,
    CAN_MCU_STATUS_SIG_COUNT
} can_mcu_status_sig_index_t;

/* Index into can_mcu_diag_signals. */
typedef enum
{
    CAN_MCU_DIAG_SIG_ERROR_FLAGS = 0,
    CAN_MCU_DIAG_SIG_ERROR_COUNT,
    CAN_MCU_DIAG_SIG_LIMP_MODE,
    CAN_MCU_DIAG_SIG_COUNT
} can_mcu_diag_sig_index_t;

extern const can_db_signal_t can_vcu_heartbeat_signals[CAN_VCU_HEARTBEAT_SIG_COUNT];
extern const can_db_signal_t can_vcu_command_signals[CAN_VCU_COMMAND_SIG_COUNT];
extern const can_db_signal_t can_mcu_status_signals[CAN_MCU_STATUS_SIG_COUNT];
extern const can_db_signal_t can_mcu_diag_signals[CAN_MCU_DIAG_SIG_COUNT];
extern const can_db_message_t can_mcu_messages[CAN_MCU_MSG_COUNT];

#endif /* CAN_MCU_DB_H */
