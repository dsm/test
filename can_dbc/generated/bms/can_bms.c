/*
 * can_bms.c - CAN message pack/unpack (raw values).
 *
 * GENERATED FILE - DO NOT EDIT.
 * Generator : dbcgen 1.0.0
 * Source    : example_vehicle.dbc
 * SHA-256   : cd508e7d0359ae9ced385bbd6d432c46be738e263894852d68857ae0b2596786
 * Node      : BMS (tx+rx)
 */
#include "can_bms.h"

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

    /* DriveMode: start 26, len 3 -> byte 3, shift 0, mask 0x7 */
    window32 = (uint32_t)data[3];
    msg->drive_mode = (uint8_t)(window32 & 0x7U);

    /* ContactorRequest: start 39, len 1 -> byte 4, shift 7, mask 0x1 */
    window32 = (uint32_t)data[4];
    msg->contactor_request = (uint8_t)((window32 >> 7U) & 0x1U);

    /* ChargeEnable: start 38, len 1 -> byte 4, shift 6, mask 0x1 */
    window32 = (uint32_t)data[4];
    msg->charge_enable = (uint8_t)((window32 >> 6U) & 0x1U);

    /* MaxChargeCurrent: start 37, len 10 -> bytes 4..5, shift 4, mask 0x3FF */
    window32 = ((uint32_t)data[4] << 8U) | (uint32_t)data[5];
    msg->max_charge_current = (uint16_t)((window32 >> 4U) & 0x3FFU);

    /* CmdCounter: start 59, len 4 -> byte 7, shift 0, mask 0xF */
    window32 = (uint32_t)data[7];
    msg->cmd_counter = (uint8_t)(window32 & 0xFU);
}

/* BMS_Status (0x200, standard, DLC 8, TX) */
void can_bms_status_pack(const can_bms_status_t *msg, uint8_t *data)
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

    /* PackVoltage: start 7, len 16 -> bytes 0..1, shift 0, mask 0xFFFF */
    window32 = ((uint32_t)msg->pack_voltage & 0xFFFFU);
    data[0] |= (uint8_t)((window32 >> 8U) & 0xFFU);
    data[1] |= (uint8_t)(window32 & 0xFFU);

    /* PackCurrent: start 23, len 12 -> bytes 2..3, shift 4, mask 0xFFF */
    window32 = ((uint32_t)msg->pack_current & 0xFFFU) << 4U;
    data[2] |= (uint8_t)((window32 >> 8U) & 0xFFU);
    data[3] |= (uint8_t)(window32 & 0xFFU);

    /* Soc: start 27, len 10 -> bytes 3..4, shift 2, mask 0x3FF */
    window32 = ((uint32_t)msg->soc & 0x3FFU) << 2U;
    data[3] |= (uint8_t)((window32 >> 8U) & 0xFFU);
    data[4] |= (uint8_t)(window32 & 0xFFU);

    /* State: start 33, len 3 -> bytes 4..5, shift 7, mask 0x7 */
    window32 = ((uint32_t)msg->state & 0x7U) << 7U;
    data[4] |= (uint8_t)((window32 >> 8U) & 0xFFU);
    data[5] |= (uint8_t)(window32 & 0xFFU);

    /* ContactorClosed: start 46, len 1 -> byte 5, shift 6, mask 0x1 */
    window32 = ((uint32_t)msg->contactor_closed & 0x1U) << 6U;
    data[5] |= (uint8_t)(window32 & 0xFFU);

    /* FaultActive: start 45, len 1 -> byte 5, shift 5, mask 0x1 */
    window32 = ((uint32_t)msg->fault_active & 0x1U) << 5U;
    data[5] |= (uint8_t)(window32 & 0xFFU);

    /* MaxCellTemp: start 55, len 8 -> byte 6, shift 0, mask 0xFF */
    window32 = ((uint32_t)msg->max_cell_temp & 0xFFU);
    data[6] |= (uint8_t)(window32 & 0xFFU);

    /* AliveCounter: start 59, len 4 -> byte 7, shift 0, mask 0xF */
    window32 = ((uint32_t)msg->alive_counter & 0xFU);
    data[7] |= (uint8_t)(window32 & 0xFFU);
}

/* BMS_Energy (0x18FF50E5, extended, DLC 8, TX) */
void can_bms_energy_pack(const can_bms_energy_t *msg, uint8_t *data)
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

    /* EnergyCounter: start 7, len 40 -> bytes 0..4, shift 0, mask 0xFFFFFFFFFF */
    window64 = ((uint64_t)msg->energy_counter & 0xFFFFFFFFFFULL);
    data[0] |= (uint8_t)((window64 >> 32U) & 0xFFULL);
    data[1] |= (uint8_t)((window64 >> 24U) & 0xFFULL);
    data[2] |= (uint8_t)((window64 >> 16U) & 0xFFULL);
    data[3] |= (uint8_t)((window64 >> 8U) & 0xFFULL);
    data[4] |= (uint8_t)(window64 & 0xFFULL);

    /* BalancingActive: start 47, len 1 -> byte 5, shift 7, mask 0x1 */
    window32 = ((uint32_t)msg->balancing_active & 0x1U) << 7U;
    data[5] |= (uint8_t)(window32 & 0xFFU);

    /* Derating: start 46, len 1 -> byte 5, shift 6, mask 0x1 */
    window32 = ((uint32_t)msg->derating & 0x1U) << 6U;
    data[5] |= (uint8_t)(window32 & 0xFFU);

    /* ChargeCycles: start 45, len 22 -> bytes 5..7, shift 0, mask 0x3FFFFF */
    window32 = ((uint32_t)msg->charge_cycles & 0x3FFFFFU);
    data[5] |= (uint8_t)((window32 >> 16U) & 0xFFU);
    data[6] |= (uint8_t)((window32 >> 8U) & 0xFFU);
    data[7] |= (uint8_t)(window32 & 0xFFU);
}
