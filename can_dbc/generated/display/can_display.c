/*
 * can_display.c - CAN message pack/unpack (raw values).
 *
 * GENERATED FILE - DO NOT EDIT.
 * Generator : dbcgen 1.0.0
 * Source    : example_vehicle.dbc
 * SHA-256   : cd508e7d0359ae9ced385bbd6d432c46be738e263894852d68857ae0b2596786
 * Node      : DISPLAY (rx)
 */
#include "can_display.h"

/* VCU_Heartbeat (0x10, standard, DLC 3, RX) */
void can_vcu_heartbeat_unpack(can_vcu_heartbeat_t *msg, const uint8_t *data)
{
    uint32_t window32;

    /* HbCounter: start 7, len 8 -> byte 0, shift 0, mask 0xFF */
    window32 = (uint32_t)data[0];
    msg->hb_counter = (uint8_t)(window32 & 0xFFU);

    /* VcuState: start 15, len 4 -> byte 1, shift 4, mask 0xF */
    window32 = (uint32_t)data[1];
    msg->vcu_state = (uint8_t)((window32 >> 4U) & 0xFU);

    /* SwVersion: start 11, len 12 -> bytes 1..2, shift 0, mask 0xFFF */
    window32 = ((uint32_t)data[1] << 8U) | (uint32_t)data[2];
    msg->sw_version = (uint16_t)(window32 & 0xFFFU);
}

/* VCU_Command (0x100, standard, DLC 8, RX) */
void can_vcu_command_unpack(can_vcu_command_t *msg, const uint8_t *data)
{
    uint32_t window32;

    /* DriveMode: start 26, len 3 -> byte 3, shift 0, mask 0x7 */
    window32 = (uint32_t)data[3];
    msg->drive_mode = (uint8_t)(window32 & 0x7U);
}

/* BMS_Status (0x200, standard, DLC 8, RX) */
void can_bms_status_unpack(can_bms_status_t *msg, const uint8_t *data)
{
    uint32_t window32;

    /* PackVoltage: start 7, len 16 -> bytes 0..1, shift 0, mask 0xFFFF */
    window32 = ((uint32_t)data[0] << 8U) | (uint32_t)data[1];
    msg->pack_voltage = (uint16_t)(window32 & 0xFFFFU);

    /* PackCurrent: start 23, len 12 -> bytes 2..3, shift 4, mask 0xFFF */
    window32 = ((uint32_t)data[2] << 8U) | (uint32_t)data[3];
    msg->pack_current = (uint16_t)((window32 >> 4U) & 0xFFFU);

    /* Soc: start 27, len 10 -> bytes 3..4, shift 2, mask 0x3FF */
    window32 = ((uint32_t)data[3] << 8U) | (uint32_t)data[4];
    msg->soc = (uint16_t)((window32 >> 2U) & 0x3FFU);

    /* State: start 33, len 3 -> bytes 4..5, shift 7, mask 0x7 */
    window32 = ((uint32_t)data[4] << 8U) | (uint32_t)data[5];
    msg->state = (uint8_t)((window32 >> 7U) & 0x7U);

    /* FaultActive: start 45, len 1 -> byte 5, shift 5, mask 0x1 */
    window32 = (uint32_t)data[5];
    msg->fault_active = (uint8_t)((window32 >> 5U) & 0x1U);

    /* MaxCellTemp: start 55, len 8 -> byte 6, shift 0, mask 0xFF */
    window32 = (uint32_t)data[6];
    msg->max_cell_temp = (uint8_t)(window32 & 0xFFU);
}

/* MCU_Status (0x300, standard, DLC 8, RX) */
void can_mcu_status_unpack(can_mcu_status_t *msg, const uint8_t *data)
{
    uint32_t window32;
    uint64_t window64;

    /* MotorSpeed: start 7, len 16 -> bytes 0..1, shift 0, mask 0xFFFF */
    window32 = ((uint32_t)data[0] << 8U) | (uint32_t)data[1];
    msg->motor_speed = (uint16_t)(window32 & 0xFFFFU);

    /* OdometerTicks: start 27, len 30 -> bytes 3..7, shift 6, mask 0x3FFFFFFF */
    window64 = ((uint64_t)data[3] << 32U) | ((uint64_t)data[4] << 24U) | ((uint64_t)data[5] << 16U) | ((uint64_t)data[6] << 8U) | (uint64_t)data[7];
    msg->odometer_ticks = (uint32_t)((window64 >> 6U) & 0x3FFFFFFFULL);

    /* InverterTemp: start 61, len 6 -> byte 7, shift 0, mask 0x3F */
    window32 = (uint32_t)data[7];
    msg->inverter_temp = (uint8_t)(window32 & 0x3FU);
}

/* MCU_Diag (0x310, standard, DLC 6, RX) */
void can_mcu_diag_unpack(can_mcu_diag_t *msg, const uint8_t *data)
{
    uint32_t window32;

    /* ErrorFlags: start 7, len 32 -> bytes 0..3, shift 0, mask 0xFFFFFFFF */
    window32 = ((uint32_t)data[0] << 24U) | ((uint32_t)data[1] << 16U) | ((uint32_t)data[2] << 8U) | (uint32_t)data[3];
    msg->error_flags = (uint32_t)(window32 & 0xFFFFFFFFU);

    /* LimpMode: start 46, len 1 -> byte 5, shift 6, mask 0x1 */
    window32 = (uint32_t)data[5];
    msg->limp_mode = (uint8_t)((window32 >> 6U) & 0x1U);
}

/* BMS_Energy (0x18FF50E5, extended, DLC 8, RX) */
void can_bms_energy_unpack(can_bms_energy_t *msg, const uint8_t *data)
{
    uint32_t window32;
    uint64_t window64;

    /* EnergyCounter: start 7, len 40 -> bytes 0..4, shift 0, mask 0xFFFFFFFFFF */
    window64 = ((uint64_t)data[0] << 32U) | ((uint64_t)data[1] << 24U) | ((uint64_t)data[2] << 16U) | ((uint64_t)data[3] << 8U) | (uint64_t)data[4];
    msg->energy_counter = (uint64_t)(window64 & 0xFFFFFFFFFFULL);

    /* Derating: start 46, len 1 -> byte 5, shift 6, mask 0x1 */
    window32 = (uint32_t)data[5];
    msg->derating = (uint8_t)((window32 >> 6U) & 0x1U);
}
