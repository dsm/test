/*
 * can_conv.c - Saturating raw <-> physical signal conversion
 *              (hand-written, not generated).
 *
 * Every decision has a single condition, so decision coverage equals MC/DC.
 */
#include "can_conv.h"

uint32_t can_conv_encode(const can_conv_t *conv, float32_t phys)
{
    const float32_t raw_f = (phys - conv->offset) / conv->factor;
    uint32_t raw;

    if (raw_f >= (float32_t)conv->raw_max)
    {
        raw = conv->raw_max;
    }
    else if (raw_f > (float32_t)conv->raw_min)
    {
        /* raw_min < raw_f < raw_max: the truncation cannot overflow. */
        raw = (uint32_t)raw_f;
        if ((raw_f - (float32_t)raw) >= 0.5F)
        {
            raw++;
        }
    }
    else
    {
        /* Below the range, or NaN (all comparisons above are false). */
        raw = conv->raw_min;
    }

    return raw;
}

float32_t can_conv_decode(const can_conv_t *conv, uint32_t raw)
{
    uint32_t sat = raw;

    if (sat > conv->raw_max)
    {
        sat = conv->raw_max;
    }
    if (sat < conv->raw_min)
    {
        sat = conv->raw_min;
    }

    return ((float32_t)sat * conv->factor) + conv->offset;
}
