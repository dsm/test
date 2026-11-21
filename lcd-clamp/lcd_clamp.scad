// =====================================================================
//  Ekran / LCD sabitleme klipsi  -  3D yazici icin optimize edilmis
//  Phone screen (LCD) holding clamp  -  optimized for FDM printing
// ---------------------------------------------------------------------
//  Parcalar (her klips icin):
//    1x frame  - C govde      (yan yatirilarak basilir, destek gerekmez)
//    1x jaw    - kayar cene   (yan yatirilarak basilir, destek gerekmez)
//    1x screw  - vida + topuz (topuz asagida, dik basilir)
//    1x nut    - dişli somun  (duz basilir, govdeye alttan bastirilir)
//    2x pad    - TPU ped      (opsiyonel; yoksa 1 mm keçe/silikon yapistir)
//
//  Tamamen baskidir, vida/somun gibi metal parca gerekmez.
//  Kullanim:  part = "frame" | "jaw" | "screw" | "nut" | "pad" | "plate" | "assembly"
// =====================================================================

/* [Cikti] */
part = "assembly"; // [assembly, plate, frame, jaw, screw, nut, pad]

/* [Olculer] */
// Klips genisligi (mm)
W          = 20;
// Ceneler arasi maksimum acilma (mm, pedsiz)
max_open   = 16;
// Cene derinligi (telefona ne kadar uzanir, mm)
reach      = 28;

/* [Dis / Tolerans] */
// Vida dis capi (mm)
thread_d   = 12;
// Dis adimi (mm)
pitch      = 3;
// Dis derinligi (45 derece yanaklar, mm)
t_depth    = 1.1;
// Somun dis boslugu, radyal (mm). Sikiysa artir (0.3-0.35)
t_clear    = 0.25;
// Somunun govdeye gecme boslugu (mm). Gevsekse azalt / yapistir
nut_fit    = 0.15;
// Cene kanalindaki genel bosluk (mm)
slide_clr  = 0.3;

/* [Kalite] */
$fn        = 64;
// Dis agi z cozunurlugu (kucuk = daha puruzsuz, daha yavas)
thread_dz  = 0.1;

// ---------------------------------------------------------------------
// Turetilen olculer
// ---------------------------------------------------------------------
spine_t   = 6;                 // arka govde kalinligi
arm_bot_t = 6;                 // alt kol kalinligi
arm_top_t = 12;                // ust kol (somun yuvasi) kalinligi
jaw_t     = 9;                 // kayar cene kalinligi
ax_y      = 17;                // vida ekseni (y)
fillet_r  = 2;                 // ic koseler
round_r   = 1.5;               // dis koseler

nut_af    = 16;                // somun anahtar agzi
nut_h     = 10;
lip_t     = arm_top_t - nut_h; // somunu tutan ust dudak

z_top_arm = arm_bot_t + jaw_t + max_open;   // ust kolun alt yuzu
H_total   = z_top_arm + arm_top_t;

// Ped yuvasi
pad_x     = 17;
pad_y     = 17;
pad_rec   = 0.8;                // yuva derinligi
pad_t     = 1.2;                // ped kalinligi (0.4 mm disari tasar)
pad_y0    = 9.5;                // ped baslangici (y)

// Vida ucu (T-kanal baglantisi)
disc_d    = 9.4;
disc_h    = 1.2;
cone_h    = 2.2;
neck_d    = 5;
jaw_floor = 2.8;
jaw_cav   = 3.6;               // disk boslugu yuksekligi
jaw_lip   = jaw_t - jaw_floor - jaw_cav;
neck_l    = (jaw_t - jaw_floor) - (disc_h + cone_h) + 0.4;
thread_l  = (H_total + 0.5) - (arm_bot_t + jaw_t + 0.4);
knob_d    = 20;
knob_h    = 10;

echo(str("Toplam yukseklik: ", H_total, " mm,  dis boyu: ", thread_l, " mm"));

// ---------------------------------------------------------------------
// Dis (helis) uretici - radyal profil agi, manifold polyhedron
// ---------------------------------------------------------------------
function tprof(u, P, H, crest) =
    let(root = P - 2*H - crest, a = root, b = root + H, c = b + crest)
    u < a ? 0 : u < b ? (u - a)/H : u < c ? 1 : (P - u)/H;

// r_min: dis dibi yaricapi; L: boy
module thread_mesh(r_min, P, H, L, crest = 0.4, fn = 64, dz = 0.1) {
    M  = ceil(L / dz);
    pts = concat(
        [for (j = [0:M], i = [0:fn-1])
            let(z = j * L / M, th = 360 * i / fn,
                u = (z - P * i / fn) - P * floor((z - P * i / fn) / P),
                r = r_min + H * tprof(u, P, H, crest))
            [r * cos(th), r * sin(th), z]],
        [[0, 0, 0], [0, 0, L]]);
    c0 = (M + 1) * fn;
    c1 = c0 + 1;
    function id(i, j) = j * fn + (i % fn);
    faces = concat(
        [for (j = [0:M-1], i = [0:fn-1])
            [id(i, j), id(i, j+1), id(i+1, j+1), id(i+1, j)]],
        [for (i = [0:fn-1]) [c0, id(i, 0), id(i+1, 0)]],
        [for (i = [0:fn-1]) [c1, id(i+1, M), id(i, M)]]);
    polyhedron(points = pts, faces = faces, convexity = 10);
}

// ---------------------------------------------------------------------
// Yardimcilar
// ---------------------------------------------------------------------
module hex_prism(af, h) {
    rotate([0, 0, 30]) cylinder(d = af / cos(30), h = h, $fn = 6);
}

// Ucu +x yonune bakan damla delik (yan baskida destek istemez)
module teardrop2d(d) {
    hull() {
        circle(d = d);
        translate([d/2 * sqrt(2) / 2 + 0.0, 0])
            rotate(45) square(d/2, center = true);
    }
}

// ---------------------------------------------------------------------
// C GOVDE  (montaj koordinatlari: x genislik, y derinlik, z yukseklik)
// ---------------------------------------------------------------------
module frame_profile() {
    offset(r = round_r) offset(delta = -round_r)
    offset(r = -fillet_r) offset(delta = fillet_r)
    union() {
        square([spine_t, H_total]);
        square([reach, arm_bot_t]);
        translate([0, z_top_arm]) square([reach, arm_top_t]);
    }
}

module frame() {
    difference() {
        rotate([90, 0, 90]) linear_extrude(W, center = true) frame_profile();

        // somun yuvasi (alttan)
        translate([0, ax_y, z_top_arm - 0.01])
            hex_prism(nut_af + 2*nut_fit, nut_h + 0.01);
        // vida gecis deligi (damla - yan baski icin)
        translate([0, ax_y, z_top_arm])
            linear_extrude(arm_top_t + 1) teardrop2d(thread_d + 0.8);
        // ust giris pahi
        translate([0, ax_y, H_total - 0.8])
            cylinder(d1 = thread_d + 0.8, d2 = thread_d + 2.6, h = 0.81);
        // alt kol ped yuvasi
        translate([-pad_x/2, pad_y0, arm_bot_t - pad_rec])
            cube([pad_x, pad_y, pad_rec + 1]);
    }
}

// ---------------------------------------------------------------------
// KAYAR CENE  (z=0 alt yuzu; montajda z = arm_bot_t + acilma)
// ---------------------------------------------------------------------
module jaw() {
    y0 = spine_t + slide_clr;
    ch = 2.8;     // arka kenar pahi (govde ic koselerini acar)
    cav_w = disc_d + 0.5;
    difference() {
        // govde: arka alt/ust kenarlari pahli
        rotate([90, 0, 90]) linear_extrude(W, center = true)
            polygon([[y0, ch], [y0 + ch, 0], [reach, 0], [reach, jaw_t],
                     [y0 + ch, jaw_t], [y0, jaw_t - ch]]);

        // disk boslugu (T-kanal alt kismi), +x yonune acik
        translate([0, ax_y, jaw_floor]) hull() {
            cylinder(d = cav_w, h = jaw_cav);
            translate([W, 0, 0]) cylinder(d = cav_w, h = jaw_cav);
        }
        // boyun kanali
        translate([0, ax_y, jaw_floor]) hull() {
            cylinder(d = neck_d + 0.6, h = jaw_t);
            translate([W, 0, 0]) cylinder(d = neck_d + 0.6, h = jaw_t);
        }
        // kanal agzi pahi
        translate([W/2, ax_y, jaw_floor + jaw_cav/2])
            rotate([0, 90, 0]) cylinder(d1 = cav_w, d2 = cav_w + 2, h = 1.01, center = true);
        // ped yuvasi
        translate([-pad_x/2, pad_y0, -1]) cube([pad_x, pad_y, pad_rec + 1]);
    }
    // kilit cikintilari: disk yerine "tik" diye oturur, kendiliginden cikmaz
    for (s = [-1, 1])
        translate([W/2 - 1.6, ax_y + s * (cav_w/2), jaw_floor + 0.4])
            scale([1, 0.5, 1]) cylinder(d = 1.6, h = jaw_cav - 0.8, $fn = 16);
}

// ---------------------------------------------------------------------
// VIDA + TOPUZ  (z=0: itme diskinin alt yuzu)
// ---------------------------------------------------------------------
module knob() {
    fl = 18;
    difference() {
        hull() {
            translate([0, 0, 1]) cylinder(d = knob_d, h = knob_h - 2);
            cylinder(d = knob_d - 2, h = knob_h);
        }
        for (i = [0:fl-1]) rotate([0, 0, i * 360/fl])
            translate([knob_d/2 + 0.6, 0, -1]) cylinder(d = 2.6, h = knob_h + 2, $fn = 20);
    }
}

module screw() {
    r_min = thread_d/2 - t_depth;
    z_thr = disc_h + cone_h + neck_l;
    // itme diski + koni (koni: baskida destek gerektirmez)
    cylinder(d = disc_d, h = disc_h);
    translate([0, 0, disc_h]) cylinder(d1 = disc_d, d2 = neck_d, h = cone_h);
    // boyun
    cylinder(d = neck_d, h = z_thr + 0.5);
    // dis (alt ucu pahli)
    translate([0, 0, z_thr]) intersection() {
        thread_mesh(r_min, pitch, t_depth, thread_l, fn = $fn, dz = thread_dz);
        union() {
            cylinder(d1 = 2*r_min, d2 = 2*r_min + 2*1.5, h = 1.5);
            translate([0, 0, 1.5]) cylinder(d = thread_d + 1, h = thread_l);
        }
    }
    translate([0, 0, z_thr + thread_l - 0.01]) knob();
}

// ---------------------------------------------------------------------
// DISLI SOMUN  (govdedeki altigen yuvaya alttan bastirilir)
// ---------------------------------------------------------------------
module nut() {
    r_min = thread_d/2 - t_depth + t_clear;
    difference() {
        intersection() {
            hex_prism(nut_af, nut_h);
            // dis koseleri hafif pahla
            cylinder(d1 = nut_af / cos(30) - 1, d2 = nut_af / cos(30) + 2*nut_h, h = nut_h);
        }
        translate([0, 0, -1]) thread_mesh(r_min, pitch, t_depth, nut_h + 2, fn = $fn, dz = thread_dz);
        // giris pahlari
        translate([0, 0, -0.01]) cylinder(d1 = thread_d + 2*t_clear + 1, d2 = 2*r_min, h = 1.3);
        translate([0, 0, nut_h - 1.29]) cylinder(d1 = 2*r_min, d2 = thread_d + 2*t_clear + 1, h = 1.3);
    }
}

module pad() {
    cube([pad_x - 0.3, pad_y - 0.3, pad_t]);
}

// ---------------------------------------------------------------------
// Baski yonleri
// ---------------------------------------------------------------------
module frame_print() { translate([0, 0, W/2]) rotate([0, -90, 0]) frame(); }
module jaw_print()   { translate([0, 0, W/2]) rotate([0, -90, 0]) jaw(); }
module screw_print() {
    tot = disc_h + cone_h + neck_l + thread_l + knob_h;
    translate([0, 0, tot - 0.01]) rotate([180, 0, 0]) screw();
}

module assembly(open = 9) {
    zj = arm_bot_t + open;
    color("Silver") frame();
    color("DimGray") translate([0, ax_y, z_top_arm]) nut();
    color("Black") translate([0, 0, zj]) jaw();
    color("LightGray") translate([0, ax_y, zj + jaw_floor]) screw();
    color("OrangeRed") {
        translate([-pad_x/2 + 0.15, pad_y0 + 0.15, arm_bot_t - pad_rec]) pad();
        translate([-pad_x/2 + 0.15, pad_y0 + 0.15, zj + pad_rec - pad_t]) pad();
    }
}

if (part == "frame")    frame_print();
if (part == "jaw")      jaw_print();
if (part == "screw")    screw_print();
if (part == "nut")      nut();
if (part == "pad")      pad();
if (part == "assembly") assembly();
if (part == "plate") {
    // 1 tam klips seti (4 adet icin 4 kez bas veya dilimleyicide cogalt)
    frame_print();
    translate([0, -30, 0]) jaw_print();
    translate([45, 10, 0]) screw_print();
    translate([45, -25, 0]) nut();
}
