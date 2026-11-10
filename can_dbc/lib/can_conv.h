/*
 * can_conv.h - Saturating raw <-> physical signal conversion
 *              (hand-written, not generated).
 *
 * Preconditions for both functions: conv != NULL and conv->factor > 0.
 * Only applicable to signals of at most 32 bits.
 */
#ifndef CAN_CONV_H
#define CAN_CONV_H

#include <stdint.h>
#include "can_db_types.h"

/*
 * Physical -> raw.
 * raw = round_half_up((phys - offset) / factor), saturated to
 * [raw_min, raw_max]. +Inf saturates to raw_max, -Inf and NaN to raw_min.
 */
uint32_t can_conv_encode(const can_conv_t *conv, float32_t phys);

/*
 * Raw -> physical.
 * raw is first saturated to [raw_min, raw_max], then
 * phys = (raw * factor) + offset.
 */
float32_t can_conv_decode(const can_conv_t *conv, uint32_t raw);

#endif /* CAN_CONV_H */
