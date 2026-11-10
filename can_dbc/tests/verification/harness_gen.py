"""Generates the C test driver of one node.

Part of the verification environment, independent of dbcgen: message and
signal lists come from the cantools based expected model (support.py), and
identifier names are derived from the naming rules of the requirements.

Protocol (one command per stdin line, one result line per command):
  P <msg> <fill> <v1> <v2> ...   pack; prints 4 guard + DLC + 4 guard bytes (hex)
  U <msg> <fill> <hex>           unpack; prints "<v1> <v2> ... | <input after call>"
  E <msg_idx> <sig_idx> <f32>    can_conv_encode via database entry; prints raw
  C <msg_idx> <sig_idx> <raw>    can_conv_decode via database entry; prints f32 bits
  D                              dumps the database tables
  K                              dumps generated constants and member sizes
"""

from .support import node_views, snake

_PRELUDE = r'''
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "can_%(node)s.h"
#include "can_%(node)s_db.h"
#include "can_conv.h"

static void fail(const char *why)
{
    printf("ERR %%s\n", why);
    exit(3);
}

static const char *arg(void)
{
    const char *token = strtok(NULL, " \r\n");
    if (token == NULL) { fail("missing argument"); }
    return token;
}

static uint64_t arg_u64(void)
{
    return (uint64_t)strtoull(arg(), NULL, 0);
}

static void print_hex(const uint8_t *bytes, size_t count)
{
    size_t i;
    for (i = 0; i < count; i++) { printf("%%02x", (unsigned)bytes[i]); }
}

static uint32_t float_bits(float value)
{
    uint32_t bits;
    memcpy(&bits, &value, sizeof bits);
    return bits;
}

static float bits_float(uint32_t bits)
{
    float value;
    memcpy(&value, &bits, sizeof value);
    return value;
}

static uint8_t *read_hex(size_t count)
{
    const char *text = arg();
    uint8_t *bytes = malloc(count);
    size_t i;
    if ((bytes == NULL) || (strlen(text) != (2U * count))) { fail("bad hex"); }
    for (i = 0; i < count; i++)
    {
        unsigned value;
        if (sscanf(&text[2U * i], "%%2x", &value) != 1) { fail("bad hex digit"); }
        bytes[i] = (uint8_t)value;
    }
    return bytes;
}

static const can_conv_t *conv_arg(void)
{
    uint64_t m = arg_u64();
    uint64_t s = arg_u64();
    if (m >= (uint64_t)%(count)s) { fail("message index"); }
    if (s >= %(table)s[m].signal_count) { fail("signal index"); }
    return &%(table)s[m].signals[s].conv;
}
'''


def _k(name: str, expr: str) -> str:
    return f'    printf("K {name} %" PRIu64 "\\n", (uint64_t)({expr}));'


def generate(node: str, mode: str) -> str:
    views = node_views(node, mode)
    low_node, up_node = snake(node), snake(node).upper()
    table = f"can_{low_node}_messages"
    count = f"CAN_{up_node}_MSG_COUNT"
    out = [_PRELUDE % {"node": low_node, "table": table, "count": count}]

    dispatch = []
    constants = [_k(count, count)]
    for view in views:
        low, up = f"can_{snake(view.msg.name)}", f"CAN_{snake(view.msg.name).upper()}"
        dlc = view.msg.dlc
        if view.direction == "TX":
            out += [f"static void do_pack_{low}(void)", "{",
                    f"    {low}_t msg;",
                    "    uint8_t fill = (uint8_t)arg_u64();",
                    f"    uint8_t *buffer = malloc({dlc + 8}U);",
                    '    if (buffer == NULL) { fail("malloc"); }',
                    f"    memset(buffer, (int)fill, {dlc + 8}U);"]
            out += [f"    msg.{snake(s.name)} = (uint{s.field_bits}_t)arg_u64();"
                    for s in view.signals]
            out += [f"    {low}_pack(&msg, &buffer[4]);",
                    f"    print_hex(buffer, {dlc + 8}U);", '    printf("\\n");',
                    "    free(buffer);", "}", ""]
            dispatch.append(f'    if ((command == \'P\') && (strcmp(name, "{view.msg.name}") == 0))'
                            f" {{ do_pack_{low}(); return; }}")
        else:
            out += [f"static void do_unpack_{low}(void)", "{",
                    f"    {low}_t msg;",
                    "    uint8_t fill = (uint8_t)arg_u64();",
                    f"    uint8_t *buffer = read_hex({dlc}U);",
                    "    memset(&msg, (int)fill, sizeof msg);",
                    f"    {low}_unpack(&msg, buffer);"]
            out += [f'    printf("%" PRIu64 " ", (uint64_t)msg.{snake(s.name)});'
                    for s in view.signals]
            out += ['    printf("| ");', f"    print_hex(buffer, {dlc}U);", '    printf("\\n");',
                    "    free(buffer);", "}", ""]
            dispatch.append(f'    if ((command == \'U\') && (strcmp(name, "{view.msg.name}") == 0))'
                            f" {{ do_unpack_{low}(); return; }}")

        msg_idx = f"CAN_{up_node}_MSG_{snake(view.msg.name).upper()}"
        constants += [_k(msg_idx, msg_idx), _k(f"{up}_SIG_COUNT", f"{up}_SIG_COUNT"),
                      _k(f"{msg_idx}.signals_ok", f"{table}[{msg_idx}].signals == {low}_signals")]
        constants += [_k(f"{up}_{suffix}", f"{up}_{suffix}")
                      for suffix in ("FRAME_ID", "IS_EXTENDED", "DLC", "CYCLE_TIME_MS")]
        for sig in view.signals:
            sig_up = snake(sig.name).upper()
            constants.append(_k(f"{up}_SIG_{sig_up}", f"{up}_SIG_{sig_up}"))
            constants.append(_k(f"sizeof.{low}_t.{snake(sig.name)}",
                                f"sizeof ((({low}_t *)0)->{snake(sig.name)})"))
            for _, text in sig.choices:
                macro = f"{up}_{sig_up}_{snake(text).upper()}"
                constants.append(_k(macro, macro))

    out += ["static void do_constants(void)", "{"] + constants + ["}", ""]
    out += [
        "static void do_dump(void)", "{", "    unsigned m;",
        f"    for (m = 0U; m < (unsigned){count}; m++)", "    {",
        f"        const can_db_message_t *msg = &{table}[m];", "        unsigned s;",
        '        printf("M %u %" PRIu32 " %u %u %d %u %u\\n", m, msg->id,',
        "               (unsigned)msg->is_extended, (unsigned)msg->dlc, (int)msg->dir,",
        "               (unsigned)msg->cycle_time_ms, (unsigned)msg->signal_count);",
        "        for (s = 0U; s < msg->signal_count; s++)", "        {",
        "            const can_db_signal_t *sig = &msg->signals[s];",
        '            printf("S %u %u %u %u %08" PRIx32 " %08" PRIx32 " %08" PRIx32 " %08" PRIx32',
        '                   " %" PRIu32 " %" PRIu32 "\\n", m, s,',
        "                   (unsigned)sig->start_bit, (unsigned)sig->length,",
        "                   float_bits(sig->conv.factor), float_bits(sig->conv.offset),",
        "                   float_bits(sig->conv.phys_min), float_bits(sig->conv.phys_max),",
        "                   sig->conv.raw_min, sig->conv.raw_max);",
        "        }", "    }", "}", "",
        "static void do_line(char *line)", "{",
        '    const char *token = strtok(line, " \\r\\n");', "    char command;",
        "    const char *name;",
        "    if (token == NULL) { return; }", "    command = token[0];",
        "    if (command == 'D') { do_dump(); return; }",
        "    if (command == 'K') { do_constants(); return; }",
        "    if (command == 'E')", "    {",
        "        const can_conv_t *conv = conv_arg();",
        "        float phys = bits_float((uint32_t)arg_u64());",
        '        printf("%" PRIu32 "\\n", can_conv_encode(conv, phys));', "        return;", "    }",
        "    if (command == 'C')", "    {",
        "        const can_conv_t *conv = conv_arg();",
        '        printf("%08" PRIx32 "\\n", float_bits(can_conv_decode(conv, (uint32_t)arg_u64())));',
        "        return;", "    }",
        "    name = arg();",
    ] + dispatch + ['    fail("unknown command");', "}", "",
                    "int main(void)", "{", "    static char line[4096];",
                    "    while (fgets(line, (int)sizeof line, stdin) != NULL) { do_line(line); }",
                    "    return 0;", "}", ""]
    return "\n".join(out)
