// =====================================================================
//  Ekran / LCD sabitleme klipsi - 3D yazici icin (metal M4 vida ile)
//  Phone screen (LCD) holding clamp - printed body, metal M4 hardware
// ---------------------------------------------------------------------
//  Orijinal metal klipsin yapisi:
//    - alt cene + arka govde + ustte kare gove (tek parca baski)
//    - gove icinde kayan silindir mil (piston) ve ucundaki ust cene plakasi
//    - ustte kapak (icinde M4 somun) ve tirtilli topuz/vida
//  Topuz cevrilince vida pistonu iter, ust cene asagi iner.
//  Opsiyonel yay pistonu yukari iter: topuz gevsetilince cene kendiliginden acilir.
//
//  Basilan parcalar (1 klips):
//    frame  - govde         (yan yatik, destek yok)
//    plunger- mil + piston  (piston asagida, dik, destek yok)
//    jaw    - ust cene      (yan yatik, kanal yukari, destek yok)
//    cap    - ust kapak     (ters, duz yuz tablada, destek yok)
//    knob   - topuz         (DIN 933 altıgen baslı vida kullanilirsa)
//    pad    - ped x2        (TPU, opsiyonel)
//
//  Hazir metal parcalar (1 klips):
//    1x M4x20 vida  - DIN 464 tirtilli bas (topuz gerekmez) VEYA
//                     DIN 933 altigen bas + basilan "knob"
//    1x M4 somun    - DIN 934
//    1x basma yayi  - opsiyonel: dis cap <=10, ic cap >=6.6, boy 18-20 mm, tel 0.5-0.6
// =====================================================================

/* [Cikti] */
part = "assembly"; // [assembly, exploded, plate, frame, plunger, jaw, cap, knob, pad]

/* [Olculer] */
// Klips kalinligi (mm)
W          = 16;
// Alt cene derinligi (mm)
reach      = 20;
// Ust cene derinligi (mm)
jaw_reach  = 19;
// Ceneler arasi maksimum acilma, pedsiz (mm)
max_open   = 12;

/* [Tolerans] */
// Piston / mil kayma boslugu, radyal (mm)
slide_clr  = 0.25;
// Kapak kirlangic kuyrugu boslugu (mm)
cap_clr    = 0.15;
// M4 somun / vida basi yuvasi boslugu (mm)
hex_clr    = 0.1;

$fn = 64;

// ---------------------------------------------------------------------
// Turetilen olculer (montaj koordinatlari: x kalinlik, y derinlik, z yukseklik)
// ---------------------------------------------------------------------
spine_t   = 4;
bot_t     = 5;                 // alt cene kalinligi
plate_t   = 5.2;               // ust cene kalinligi
house_d   = 19;                // gove derinligi (y)
ax_y      = 10.5;              // mil ekseni
fillet_r  = 1.5;
edge_r    = 1.5;

shaft_d   = 6;
piston_d  = 10;
piston_h  = 4;
bush_h    = 3;                 // govde tabanindaki mil burcu
spring_min= 6;                 // yayin kapali haldeki boyu

dt_h      = 5;                 // kapak kirlangic yuksekligi
dt_bot    = 12;
dt_top    = 10;
cap_t     = 2;

M4_af     = 7;
M4_nut_h  = 3.2;
M4_hole   = 4.5;

Zb        = bot_t + max_open + plate_t;            // gove alt yuzu
Zbt       = Zb + bush_h;                           // yay oturma yuzu
Ls        = Zbt + spring_min - (bot_t + plate_t);  // cene ustu -> piston alti
Z_bore    = Zb + Ls + piston_h + 0.5;              // delik tavani
Zh        = Z_bore + dt_h;                         // gove ustu
Z_cap     = Zh + cap_t;

// ust cene T-kanal
p_floor   = 1.4;
p_cav     = 2.3;
head_d    = 8.4;
head_flat = 0.8;
head_cone = 1.2;
shaft_top = plate_t + Ls - p_floor;                // plunger: bas altindan piston altina

pad_x = 13.5; pad_y = 12.5; pad_t = 1.0; pad_rec = 0.6;

echo(str("Yukseklik (kapak ustu): ", Z_cap, " mm   vida: M4x", ceil(Z_cap - (bot_t + plate_t + Ls + piston_h) + 0.5)));

// ---------------------------------------------------------------------
module hex_prism(af, h) rotate([0, 0, 30]) cylinder(d = af / cos(30), h = h, $fn = 6);

// yan baskida destek istemeyen, tepesi kesik damla (ucu +x)
module drop2d(d) {
    intersection() {
        hull() {
            circle(d = d);
            translate([d/2 * 0.7071, 0]) rotate(45) square(d/2, center = true);
        }
        translate([-d, -d]) square([d + d/2 + 0.6, 2*d]);
    }
}

// dikey kenarlari yuvarlatilmis zarf
module envelope(yd, h, z0 = -1) {
    translate([0, 0, z0]) hull() for (x = [-W/2 + edge_r, W/2 - edge_r], y = [edge_r, yd - edge_r])
        translate([x, y, 0]) cylinder(r = edge_r, h = h, $fn = 24);
}

// ---------------------------------------------------------------------
// GOVDE
// ---------------------------------------------------------------------
module frame_profile() {
    offset(r = 1) offset(delta = -1)
    offset(r = -fillet_r) offset(delta = fillet_r)
    union() {
        square([spine_t, Zh]);
        square([reach, bot_t]);
        translate([0, Zb]) square([house_d, Zh - Zb]);
    }
}

module frame() {
    difference() {
        intersection() {
            rotate([90, 0, 90]) linear_extrude(W, center = true) frame_profile();
            envelope(max(reach, house_d), Zh + 2);
        }
        // mil burcu
        translate([0, ax_y, Zb - 1]) linear_extrude(bush_h + 1.1) drop2d(shaft_d + 2*slide_clr + 0.1);
        // piston deligi
        translate([0, ax_y, Zbt]) linear_extrude(Z_bore - Zbt + 0.1) drop2d(piston_d + 2*slide_clr);
        // giris pahi
        translate([0, ax_y, Zb - 0.01]) cylinder(d1 = shaft_d + 1.6, d2 = shaft_d + 0.6, h = 0.5);
        // kapak kirlangic kanali (x boyunca)
        rotate([90, 0, 90]) linear_extrude(W + 2, center = true)
            polygon([[ax_y - dt_bot/2, Z_bore], [ax_y + dt_bot/2, Z_bore],
                     [ax_y + dt_top/2, Zh], [ax_y + dt_top/2, Zh + 1],
                     [ax_y - dt_top/2, Zh + 1], [ax_y - dt_top/2, Zh]]);
        // dekor yivi (orijinaldeki bant gorunumu)
        translate([0, 0, Zb + 2.2]) difference() {
            envelope(house_d, 0.8, 0);
            translate([0, 0.4, 0]) resize([W - 0.8, house_d - 0.4, 0.8]) envelope(house_d, 0.8, 0);
        }
        // alt cene ped yuvasi
        translate([-(pad_x + 0.5)/2, 6, bot_t - pad_rec]) cube([pad_x + 0.5, pad_y + 0.5, 1]);
    }
}

// ---------------------------------------------------------------------
// MIL + PISTON  (z=0: T-basinin alt yuzu)
// ---------------------------------------------------------------------
module plunger() {
    cylinder(d = head_d, h = head_flat);
    translate([0, 0, head_flat]) cylinder(d1 = head_d, d2 = shaft_d, h = head_cone);
    cylinder(d = shaft_d, h = shaft_top + 0.1);
    translate([0, 0, shaft_top]) difference() {
        hull() {
            cylinder(d = piston_d - 1, h = piston_h);
            translate([0, 0, 0.5]) cylinder(d = piston_d, h = piston_h - 1);
        }
        // vida ucu icin merkezleme cukuru
        translate([0, 0, piston_h - 0.8]) cylinder(d1 = 3, d2 = 4.6, h = 0.81);
    }
}

// ---------------------------------------------------------------------
// UST CENE PLAKASI  (z=0 alt yuz)
// ---------------------------------------------------------------------
module jaw() {
    y0 = spine_t + 0.3;
    ch = 2.2;
    cav_w = head_d + 0.5;
    difference() {
        intersection() {
            rotate([90, 0, 90]) linear_extrude(W, center = true)
                polygon([[y0, ch], [y0 + ch, 0], [jaw_reach, 0], [jaw_reach, plate_t],
                         [y0 + ch, plate_t], [y0, plate_t - ch]]);
            envelope(jaw_reach, plate_t + 2);
        }
        translate([0, ax_y, p_floor]) hull() {
            cylinder(d = cav_w, h = p_cav);
            translate([W, 0, 0]) cylinder(d = cav_w, h = p_cav);
        }
        translate([0, ax_y, p_floor]) hull() {
            cylinder(d = shaft_d + 0.6, h = plate_t);
            translate([W, 0, 0]) cylinder(d = shaft_d + 0.6, h = plate_t);
        }
        translate([W/2, ax_y, p_floor + p_cav/2])
            rotate([0, 90, 0]) cylinder(d1 = cav_w, d2 = cav_w + 2, h = 1.01, center = true);
    }
    // kilit cikintilari (bas "tik" diye oturur)
    for (s = [-1, 1])
        translate([W/2 - 1.6, ax_y + s * cav_w/2, p_floor + 0.3])
            scale([1, 0.5, 1]) cylinder(d = 1.6, h = p_cav - 0.6, $fn = 16);
}

// ---------------------------------------------------------------------
// UST KAPAK  (z=0: govde ustu; kirlangic asagi sarkar)
// ---------------------------------------------------------------------
module cap() {
    difference() {
        union() {
            // ust plaka
            hull() {
                envelope(house_d, cap_t - 0.6, 0);
                translate([0, 0.6, 0]) resize([W - 1.2, house_d - 1.2, cap_t]) envelope(house_d, cap_t, 0);
            }
            // kirlangic dil
            rotate([90, 0, 90]) linear_extrude(W, center = true)
                polygon([[ax_y - dt_bot/2 + cap_clr, -dt_h + 0.1], [ax_y + dt_bot/2 - cap_clr, -dt_h + 0.1],
                         [ax_y + dt_top/2 - cap_clr, 0.01], [ax_y - dt_top/2 + cap_clr, 0.01]]);
        }
        // M4 somun yuvasi (alttan)
        translate([0, ax_y, -dt_h]) hex_prism(M4_af + 2*hex_clr, M4_nut_h + 0.1 + 0.1);
        // vida deligi
        translate([0, ax_y, -dt_h - 1]) cylinder(d = M4_hole, h = dt_h + cap_t + 2);
        translate([0, ax_y, cap_t - 0.5]) cylinder(d1 = M4_hole, d2 = M4_hole + 1.2, h = 0.51);
    }
}

// ---------------------------------------------------------------------
// TOPUZ  (DIN 933 M4 altigen basli vida icin; z=0 alt yuz)
// ---------------------------------------------------------------------
module knob() {
    kd = 13; kh = 9; fl = 16;
    difference() {
        hull() {
            translate([0, 0, 0.6]) cylinder(d = kd, h = kh - 1.6);
            cylinder(d = kd - 1.2, h = kh);
        }
        for (i = [0:fl-1]) rotate([0, 0, i * 360/fl])
            translate([kd/2 + 0.5, 0, -1]) cylinder(d = 2.2, h = kh + 2, $fn = 16);
        translate([0, 0, -0.01]) hex_prism(M4_af + 2*hex_clr, 2.9);
        translate([0, 0, -1]) cylinder(d = M4_hole, h = 6);
    }
}

module pad() cube([pad_x, pad_y, pad_t]);

// metal parcalar (sadece gorsel)
module m4_screw(L = 20) {
    color("Gainsboro") {
        translate([0, 0, -L]) cylinder(d = 4, h = L, $fn = 24);
        hex_prism(M4_af, 2.8);
    }
}
module m4_nut() color("Gainsboro") difference() {
    hex_prism(M4_af, M4_nut_h);
    translate([0, 0, -1]) cylinder(d = 4, h = 6, $fn = 24);
}

// ---------------------------------------------------------------------
// Baski yonleri
// ---------------------------------------------------------------------
module frame_print()   translate([0, 0, W/2]) rotate([0, -90, 0]) frame();
module jaw_print()     translate([0, 0, W/2]) rotate([0, -90, 0]) jaw();
module plunger_print() translate([0, 0, shaft_top + piston_h]) rotate([180, 0, 0]) plunger();
module cap_print()     translate([0, 0, cap_t]) rotate([180, 0, 0]) cap();
module knob_print()    translate([0, 0, 9]) rotate([180, 0, 0]) knob();

module assembly(open = 6) {
    j = bot_t + open;
    pt = j + plate_t + Ls + piston_h;          // piston ustu
    color("Silver") frame();
    color([0.15, 0.15, 0.15]) translate([0, 0, j]) jaw();
    color("LightGray") translate([0, ax_y, j + p_floor]) plunger();
    color([0.15, 0.15, 0.15]) translate([0, 0, Zh]) cap();
    translate([0, ax_y, Zh - dt_h + 0.1]) m4_nut();
    translate([0, ax_y, pt + 20]) { m4_screw(20); color("Silver") translate([0, 0, -0.1]) knob(); }
    color("OrangeRed") {
        translate([-pad_x/2, 6.25, bot_t - pad_rec]) pad();
        translate([-pad_x/2, 6.25, j - pad_t]) pad();
    }
}

// montaj sirasi: piston ustten, cene ve kapak yandan kayarak takilir
module exploded() {
    color("Silver") frame();
    color("OrangeRed") translate([-pad_x/2, 6.25, bot_t + 3]) pad();
    color([0.15, 0.15, 0.15]) translate([W + 8, 0, bot_t + 3]) jaw();
    color("LightGray") translate([0, ax_y, Zh + 8]) plunger();
    translate([W + 8, ax_y, Zh + 8 + shaft_top + piston_h + 10]) m4_nut();
    color([0.15, 0.15, 0.15]) translate([W + 8, 0, Zh + 8 + shaft_top + piston_h + 20]) cap();
    translate([0, ax_y, Zh + 8 + shaft_top + piston_h + 52]) { m4_screw(20); color("Silver") translate([0, 0, -0.1]) knob(); }
}

if (part == "assembly") assembly();
if (part == "exploded") exploded();
if (part == "frame")    frame_print();
if (part == "jaw")      jaw_print();
if (part == "plunger")  plunger_print();
if (part == "cap")      cap_print();
if (part == "knob")     knob_print();
if (part == "pad")      pad();
if (part == "plate") {
    frame_print();
    translate([0, -26, 0]) jaw_print();
    translate([40, 10, 0]) plunger_print();
    translate([40, -14, 0]) cap_print();
    translate([62, 10, 0]) knob_print();
}
