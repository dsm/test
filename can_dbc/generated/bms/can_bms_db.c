/*
 * can_bms_db.c - CAN message/signal database.
 *
 * GENERATED FILE - DO NOT EDIT.
 * Generator : dbcgen 1.0.0
 * Source    : example_vehicle.dbc
 * SHA-256   : cd508e7d0359ae9ced385bbd6d432c46be738e263894852d68857ae0b2596786
 * Node      : BMS (tx+rx)
 */
#include "can_bms_db.h"

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
    { 26U, 3U, { 1.0F, 0.0F, 0.0F, 4.0F, 0U, 4U } }, /* DriveMode */
    { 39U, 1U, { 1.0F, 0.0F, 0.0F, 1.0F, 0U, 1U } }, /* ContactorRequest */
    { 38U, 1U, { 1.0F, 0.0F, 0.0F, 1.0F, 0U, 1U } }, /* ChargeEnable */
    { 37U, 10U, { 0.5F, 0.0F, 0.0F, 500.0F, 0U, 1000U } }, /* MaxChargeCurrent */
    { 59U, 4U, { 1.0F, 0.0F, 0.0F, 15.0F, 0U, 15U } }  /* CmdCounter */
};

/* BMS_Status (0x200, standard, DLC 8, TX) */
const can_db_signal_t can_bms_status_signals[CAN_BMS_STATUS_SIG_COUNT] =
{
    /* start, len, { factor, offset, phys_min, phys_max, raw_min, raw_max } */
    { 7U, 16U, { 0.1F, 0.0F, 0.0F, 6553.5F, 0U, 65535U } }, /* PackVoltage */
    { 23U, 12U, { 0.1F, -200.0F, -200.0F, 200.0F, 0U, 4000U } }, /* PackCurrent */
    { 27U, 10U, { 0.1F, 0.0F, 0.0F, 100.0F, 0U, 1000U } }, /* Soc */
    { 33U, 3U, { 1.0F, 0.0F, 0.0F, 5.0F, 0U, 5U } }, /* State */
    { 46U, 1U, { 1.0F, 0.0F, 0.0F, 1.0F, 0U, 1U } }, /* ContactorClosed */
    { 45U, 1U, { 1.0F, 0.0F, 0.0F, 1.0F, 0U, 1U } }, /* FaultActive */
    { 55U, 8U, { 1.0F, -40.0F, -40.0F, 215.0F, 0U, 255U } }, /* MaxCellTemp */
    { 59U, 4U, { 1.0F, 0.0F, 0.0F, 15.0F, 0U, 15U } }  /* AliveCounter */
};

/* BMS_Energy (0x18FF50E5, extended, DLC 8, TX) */
const can_db_signal_t can_bms_energy_signals[CAN_BMS_ENERGY_SIG_COUNT] =
{
    /* start, len, { factor, offset, phys_min, phys_max, raw_min, raw_max } */
    { 7U, 40U, { 1.0F, 0.0F, 0.0F, 4294967296.0F, 0U, 4294967295U } }, /* EnergyCounter */
    { 47U, 1U, { 1.0F, 0.0F, 0.0F, 1.0F, 0U, 1U } }, /* BalancingActive */
    { 46U, 1U, { 1.0F, 0.0F, 0.0F, 1.0F, 0U, 1U } }, /* Derating */
    { 45U, 22U, { 1.0F, 0.0F, 0.0F, 4000000.0F, 0U, 4000000U } }  /* ChargeCycles */
};

const can_db_message_t can_bms_messages[CAN_BMS_MSG_COUNT] =
{
    /* id, is_extended, dlc, dir, cycle_time_ms, signals, signal_count */
    { 0x10U, 0U, 3U, CAN_DB_DIR_RX, 50U, can_vcu_heartbeat_signals, (uint8_t)CAN_VCU_HEARTBEAT_SIG_COUNT },
    { 0x100U, 0U, 8U, CAN_DB_DIR_RX, 10U, can_vcu_command_signals, (uint8_t)CAN_VCU_COMMAND_SIG_COUNT },
    { 0x200U, 0U, 8U, CAN_DB_DIR_TX, 100U, can_bms_status_signals, (uint8_t)CAN_BMS_STATUS_SIG_COUNT },
    { 0x18FF50E5U, 1U, 8U, CAN_DB_DIR_TX, 1000U, can_bms_energy_signals, (uint8_t)CAN_BMS_ENERGY_SIG_COUNT }
};
