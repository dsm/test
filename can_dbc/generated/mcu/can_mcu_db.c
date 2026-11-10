/*
 * can_mcu_db.c - CAN message/signal database.
 *
 * GENERATED FILE - DO NOT EDIT.
 * Generator : dbcgen 1.0.0
 * Source    : example_vehicle.dbc
 * SHA-256   : cd508e7d0359ae9ced385bbd6d432c46be738e263894852d68857ae0b2596786
 * Node      : MCU (tx+rx)
 */
#include "can_mcu_db.h"

/* VCU_Heartbeat (0x10, standard, DLC 3, RX) */
const can_db_signal_t can_vcu_heartbeat_signals[CAN_VCU_HEARTBEAT_SIG_COUNT] =
{
    /* start, len, { factor, offset, phys_min, phys_max, raw_min, raw_max } */
    { 7U, 8U, { 1.0F, 0.0F, 0.0F, 255.0F, 0U, 255U } }, /* HbCounter */
    { 15U, 4U, { 1.0F, 0.0F, 0.0F, 9.0F, 0U, 9U } }  /* VcuState */
};

/* VCU_Command (0x100, standard, DLC 8, RX) */
const can_db_signal_t can_vcu_command_signals[CAN_VCU_COMMAND_SIG_COUNT] =
{
    /* start, len, { factor, offset, phys_min, phys_max, raw_min, raw_max } */
    { 7U, 16U, { 0.1F, -1000.0F, -1000.0F, 1000.0F, 0U, 20000U } }, /* TorqueRequest */
    { 23U, 13U, { 1.0F, 0.0F, 500.0F, 8000.0F, 500U, 8000U } }, /* SpeedLimit */
    { 26U, 3U, { 1.0F, 0.0F, 0.0F, 4.0F, 0U, 4U } }, /* DriveMode */
    { 59U, 4U, { 1.0F, 0.0F, 0.0F, 15.0F, 0U, 15U } }  /* CmdCounter */
};

/* MCU_Status (0x300, standard, DLC 8, TX) */
const can_db_signal_t can_mcu_status_signals[CAN_MCU_STATUS_SIG_COUNT] =
{
    /* start, len, { factor, offset, phys_min, phys_max, raw_min, raw_max } */
    { 7U, 16U, { 0.5F, -10000.0F, -10000.0F, 10000.0F, 0U, 40000U } }, /* MotorSpeed */
    { 23U, 12U, { 0.5F, -1000.0F, -1000.0F, 1000.0F, 0U, 4000U } }, /* ActualTorque */
    { 27U, 30U, { 1.0F, 0.0F, 0.0F, 1073741824.0F, 0U, 1073741823U } }, /* OdometerTicks */
    { 61U, 6U, { 2.0F, -40.0F, -40.0F, 86.0F, 0U, 63U } }  /* InverterTemp */
};

/* MCU_Diag (0x310, standard, DLC 6, TX) */
const can_db_signal_t can_mcu_diag_signals[CAN_MCU_DIAG_SIG_COUNT] =
{
    /* start, len, { factor, offset, phys_min, phys_max, raw_min, raw_max } */
    { 7U, 32U, { 1.0F, 0.0F, 0.0F, 4294967296.0F, 0U, 4294967295U } }, /* ErrorFlags */
    { 39U, 9U, { 1.0F, 0.0F, 0.0F, 511.0F, 0U, 511U } }, /* ErrorCount */
    { 46U, 1U, { 1.0F, 0.0F, 0.0F, 1.0F, 0U, 1U } }  /* LimpMode */
};

const can_db_message_t can_mcu_messages[CAN_MCU_MSG_COUNT] =
{
    /* id, is_extended, dlc, dir, cycle_time_ms, signals, signal_count */
    { 0x10U, 0U, 3U, CAN_DB_DIR_RX, 50U, can_vcu_heartbeat_signals, (uint8_t)CAN_VCU_HEARTBEAT_SIG_COUNT },
    { 0x100U, 0U, 8U, CAN_DB_DIR_RX, 10U, can_vcu_command_signals, (uint8_t)CAN_VCU_COMMAND_SIG_COUNT },
    { 0x300U, 0U, 8U, CAN_DB_DIR_TX, 20U, can_mcu_status_signals, (uint8_t)CAN_MCU_STATUS_SIG_COUNT },
    { 0x310U, 0U, 6U, CAN_DB_DIR_TX, 0U, can_mcu_diag_signals, (uint8_t)CAN_MCU_DIAG_SIG_COUNT }
};
