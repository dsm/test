/*
 * can_vcu.c - CAN message pack/unpack (raw values).
 *
 * GENERATED FILE - DO NOT EDIT.
 * Generator : dbcgen 1.0.0
 * Source    : example_vehicle.dbc
 * SHA-256   : cd508e7d0359ae9ced385bbd6d432c46be738e263894852d68857ae0b2596786
 * Node      : VCU (tx+rx)
 */
#include "can_vcu.h"

/* VCU_Heartbeat (0x10, standard, DLC 3, TX) */
void can_vcu_heartbeat_pack(const can_vcu_heartbeat_t *msg, uint8_t *data)
{
    uint32_t window32;

    data[0] = 0U;
    data[1] = 0U;
    data[2] = 0U;

    /* HbCounter: start 7, len 8 -> byte 0, shift 0, mask 0xFF */
    window32 = ((uint32_t)msg->hb_counter & 0xFFU);
    data[0] |= (uint8_t)(window32 & 0xFFU);

    /* VcuState: start 15, len 4 -> byte 1, shift 4, mask 0xF */
    window32 = ((uint32_t)msg->vcu_state & 0xFU) << 4U;
    data[1] |= (uint8_t)(window32 & 0xFFU);

    /* SwVersion: start 11, len 12 -> bytes 1..2, shift 0, mask 0xFFF */
    window32 = ((uint32_t)msg->sw_version & 0xFFFU);
    data[1] |= (uint8_t)((window32 >> 8U) & 0xFFU);
    data[2] |= (uint8_t)(window32 & 0xFFU);
}

/* VCU_Command (0x100, standard, DLC 8, TX) */
void can_vcu_command_pack(const can_vcu_command_t *msg, uint8_t *data)
{
    uint32_t window32;

    data[0] = 0U;
    data[1] = 0U;
    data[2] = 0U;
    data[3] = 0U;
    data[4] = 0U;
    data[5] = 0U;
    data[6] = 0U;
    data[7] = 0U;

    /* TorqueRequest: start 7, len 16 -> bytes 0..1, shift 0, mask 0xFFFF */
    window32 = ((uint32_t)msg->torque_request & 0xFFFFU);
    data[0] |= (uint8_t)((window32 >> 8U) & 0xFFU);
    data[1] |= (uint8_t)(window32 & 0xFFU);

    /* SpeedLimit: start 23, len 13 -> bytes 2..3, shift 3, mask 0x1FFF */
    window32 = ((uint32_t)msg->speed_limit & 0x1FFFU) << 3U;
    data[2] |= (uint8_t)((window32 >> 8U) & 0xFFU);
    data[3] |= (uint8_t)(window32 & 0xFFU);

    /* DriveMode: start 26, len 3 -> byte 3, shift 0, mask 0x7 */
    window32 = ((uint32_t)msg->drive_mode & 0x7U);
    data[3] |= (uint8_t)(window32 & 0xFFU);

    /* ContactorRequest: start 39, len 1 -> byte 4, shift 7, mask 0x1 */
    window32 = ((uint32_t)msg->contactor_request & 0x1U) << 7U;
    data[4] |= (uint8_t)(window32 & 0xFFU);

    /* ChargeEnable: start 38, len 1 -> byte 4, shift 6, mask 0x1 */
    window32 = ((uint32_t)msg->charge_enable & 0x1U) << 6U;
    data[4] |= (uint8_t)(window32 & 0xFFU);

    /* MaxChargeCurrent: start 37, len 10 -> bytes 4..5, shift 4, mask 0x3FF */
    window32 = ((uint32_t)msg->max_charge_current & 0x3FFU) << 4U;
    data[4] |= (uint8_t)((window32 >> 8U) & 0xFFU);
    data[5] |= (uint8_t)(window32 & 0xFFU);

    /* CmdCounter: start 59, len 4 -> byte 7, shift 0, mask 0xF */
    window32 = ((uint32_t)msg->cmd_counter & 0xFU);
    data[7] |= (uint8_t)(window32 & 0xFFU);
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

    /* ContactorClosed: start 46, len 1 -> byte 5, shift 6, mask 0x1 */
    window32 = (uint32_t)data[5];
    msg->contactor_closed = (uint8_t)((window32 >> 6U) & 0x1U);

    /* FaultActive: start 45, len 1 -> byte 5, shift 5, mask 0x1 */
    window32 = (uint32_t)data[5];
    msg->fault_active = (uint8_t)((window32 >> 5U) & 0x1U);

    /* MaxCellTemp: start 55, len 8 -> byte 6, shift 0, mask 0xFF */
    window32 = (uint32_t)data[6];
    msg->max_cell_temp = (uint8_t)(window32 & 0xFFU);

    /* AliveCounter: start 59, len 4 -> byte 7, shift 0, mask 0xF */
    window32 = (uint32_t)data[7];
    msg->alive_counter = (uint8_t)(window32 & 0xFU);
}

/* MCU_Status (0x300, standard, DLC 8, RX) */
void can_mcu_status_unpack(can_mcu_status_t *msg, const uint8_t *data)
{
    uint32_t window32;
    uint64_t window64;

    /* MotorSpeed: start 7, len 16 -> bytes 0..1, shift 0, mask 0xFFFF */
    window32 = ((uint32_t)data[0] << 8U) | (uint32_t)data[1];
    msg->motor_speed = (uint16_t)(window32 & 0xFFFFU);

    /* ActualTorque: start 23, len 12 -> bytes 2..3, shift 4, mask 0xFFF */
    window32 = ((uint32_t)data[2] << 8U) | (uint32_t)data[3];
    msg->actual_torque = (uint16_t)((window32 >> 4U) & 0xFFFU);

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

    /* ErrorCount: start 39, len 9 -> bytes 4..5, shift 7, mask 0x1FF */
    window32 = ((uint32_t)data[4] << 8U) | (uint32_t)data[5];
    msg->error_count = (uint16_t)((window32 >> 7U) & 0x1FFU);

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

    /* BalancingActive: start 47, len 1 -> byte 5, shift 7, mask 0x1 */
    window32 = (uint32_t)data[5];
    msg->balancing_active = (uint8_t)((window32 >> 7U) & 0x1U);

    /* Derating: start 46, len 1 -> byte 5, shift 6, mask 0x1 */
    window32 = (uint32_t)data[5];
    msg->derating = (uint8_t)((window32 >> 6U) & 0x1U);

    /* ChargeCycles: start 45, len 22 -> bytes 5..7, shift 0, mask 0x3FFFFF */
    window32 = ((uint32_t)data[5] << 16U) | ((uint32_t)data[6] << 8U) | (uint32_t)data[7];
    msg->charge_cycles = (uint32_t)(window32 & 0x3FFFFFU);
}
