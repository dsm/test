/*
 * can_mcu.c - CAN message pack/unpack (raw values).
 *
 * GENERATED FILE - DO NOT EDIT.
 * Generator : dbcgen 1.0.0
 * Source    : example_vehicle.dbc
 * SHA-256   : cd508e7d0359ae9ced385bbd6d432c46be738e263894852d68857ae0b2596786
 * Node      : MCU (tx+rx)
 */
#include "can_mcu.h"

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
}

/* VCU_Command (0x100, standard, DLC 8, RX) */
void can_vcu_command_unpack(can_vcu_command_t *msg, const uint8_t *data)
{
    uint32_t window32;

    /* TorqueRequest: start 7, len 16 -> bytes 0..1, shift 0, mask 0xFFFF */
    window32 = ((uint32_t)data[0] << 8U) | (uint32_t)data[1];
    msg->torque_request = (uint16_t)(window32 & 0xFFFFU);

    /* SpeedLimit: start 23, len 13 -> bytes 2..3, shift 3, mask 0x1FFF */
    window32 = ((uint32_t)data[2] << 8U) | (uint32_t)data[3];
    msg->speed_limit = (uint16_t)((window32 >> 3U) & 0x1FFFU);

    /* DriveMode: start 26, len 3 -> byte 3, shift 0, mask 0x7 */
    window32 = (uint32_t)data[3];
    msg->drive_mode = (uint8_t)(window32 & 0x7U);

    /* CmdCounter: start 59, len 4 -> byte 7, shift 0, mask 0xF */
    window32 = (uint32_t)data[7];
    msg->cmd_counter = (uint8_t)(window32 & 0xFU);
}

/* MCU_Status (0x300, standard, DLC 8, TX) */
void can_mcu_status_pack(const can_mcu_status_t *msg, uint8_t *data)
{
    uint32_t window32;
    uint64_t window64;

    data[0] = 0U;
    data[1] = 0U;
    data[2] = 0U;
    data[3] = 0U;
    data[4] = 0U;
    data[5] = 0U;
    data[6] = 0U;
    data[7] = 0U;

    /* MotorSpeed: start 7, len 16 -> bytes 0..1, shift 0, mask 0xFFFF */
    window32 = ((uint32_t)msg->motor_speed & 0xFFFFU);
    data[0] |= (uint8_t)((window32 >> 8U) & 0xFFU);
    data[1] |= (uint8_t)(window32 & 0xFFU);

    /* ActualTorque: start 23, len 12 -> bytes 2..3, shift 4, mask 0xFFF */
    window32 = ((uint32_t)msg->actual_torque & 0xFFFU) << 4U;
    data[2] |= (uint8_t)((window32 >> 8U) & 0xFFU);
    data[3] |= (uint8_t)(window32 & 0xFFU);

    /* OdometerTicks: start 27, len 30 -> bytes 3..7, shift 6, mask 0x3FFFFFFF */
    window64 = ((uint64_t)msg->odometer_ticks & 0x3FFFFFFFULL) << 6U;
    data[3] |= (uint8_t)((window64 >> 32U) & 0xFFULL);
    data[4] |= (uint8_t)((window64 >> 24U) & 0xFFULL);
    data[5] |= (uint8_t)((window64 >> 16U) & 0xFFULL);
    data[6] |= (uint8_t)((window64 >> 8U) & 0xFFULL);
    data[7] |= (uint8_t)(window64 & 0xFFULL);

    /* InverterTemp: start 61, len 6 -> byte 7, shift 0, mask 0x3F */
    window32 = ((uint32_t)msg->inverter_temp & 0x3FU);
    data[7] |= (uint8_t)(window32 & 0xFFU);
}

/* MCU_Diag (0x310, standard, DLC 6, TX) */
void can_mcu_diag_pack(const can_mcu_diag_t *msg, uint8_t *data)
{
    uint32_t window32;

    data[0] = 0U;
    data[1] = 0U;
    data[2] = 0U;
    data[3] = 0U;
    data[4] = 0U;
    data[5] = 0U;

    /* ErrorFlags: start 7, len 32 -> bytes 0..3, shift 0, mask 0xFFFFFFFF */
    window32 = ((uint32_t)msg->error_flags & 0xFFFFFFFFU);
    data[0] |= (uint8_t)((window32 >> 24U) & 0xFFU);
    data[1] |= (uint8_t)((window32 >> 16U) & 0xFFU);
    data[2] |= (uint8_t)((window32 >> 8U) & 0xFFU);
    data[3] |= (uint8_t)(window32 & 0xFFU);

    /* ErrorCount: start 39, len 9 -> bytes 4..5, shift 7, mask 0x1FF */
    window32 = ((uint32_t)msg->error_count & 0x1FFU) << 7U;
    data[4] |= (uint8_t)((window32 >> 8U) & 0xFFU);
    data[5] |= (uint8_t)(window32 & 0xFFU);

    /* LimpMode: start 46, len 1 -> byte 5, shift 6, mask 0x1 */
    window32 = ((uint32_t)msg->limp_mode & 0x1U) << 6U;
    data[5] |= (uint8_t)(window32 & 0xFFU);
}
