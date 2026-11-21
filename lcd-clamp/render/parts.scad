// Render icin parcalari montaj koordinatlarinda tek tek disa aktarir.
include <../lcd_clamp.scad>
$fn = 128;
comp = "frame";
view = "assembly";   // assembly | exploded
open = 6;

j  = bot_t + open;
pt = j + plate_t + Ls + piston_h;
E  = Zh + 8 + shaft_top + piston_h;   // exploded referans

module place(c) {
    if (view == "assembly") {
        if (c == "frame")   frame();
        if (c == "jaw")     translate([0, 0, j]) jaw();
        if (c == "plunger") translate([0, ax_y, j + p_floor]) plunger();
        if (c == "cap")     translate([0, 0, Zh]) cap();
        if (c == "nut")     translate([0, ax_y, Zh - dt_h + 0.1]) nut_solid();
        if (c == "screw")   translate([0, ax_y, pt + 20]) screw_solid();
        if (c == "knob")    translate([0, ax_y, pt + 20 - 0.1]) knob();
        if (c == "pad1")    translate([-pad_x/2, 6.25, bot_t - pad_rec]) pad();
        if (c == "pad2")    translate([-pad_x/2, 6.25, j - pad_t]) pad();
    } else {
        if (c == "frame")   frame();
        if (c == "pad1")    translate([-pad_x/2, 6.25, bot_t + 3]) pad();
        if (c == "jaw")     translate([W + 10, 0, bot_t + 3]) jaw();
        if (c == "plunger") translate([0, ax_y, Zh + 8]) plunger();
        if (c == "nut")     translate([W + 10, ax_y, E + 10]) nut_solid();
        if (c == "cap")     translate([W + 10, 0, E + 20]) cap();
        if (c == "screw")   translate([0, ax_y, E + 52]) screw_solid();
        if (c == "knob")    translate([0, ax_y, E + 52 - 0.1]) knob();
    }
}

module screw_solid() {
    translate([0, 0, -20]) cylinder(d = 3.9, h = 20 - 0.01, $fn = 48);
    translate([0, 0, -20]) cylinder(d1 = 3.2, d2 = 3.9, h = 0.4, $fn = 48);
    hex_prism(M4_af, 2.8);
}
module nut_solid() difference() {
    intersection() {
        hex_prism(M4_af, M4_nut_h);
        cylinder(d1 = M4_af / cos(30) - 0.6, d2 = M4_af / cos(30) + 2*M4_nut_h, h = M4_nut_h);
    }
    translate([0, 0, -1]) cylinder(d = 4, h = 6, $fn = 48);
}

place(comp);
