import math
import random
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def draw_lightning(draw, x, y, size, color):
    pts = [
        (x + size * 0.55, y),
        (x + size * 0.15, y + size * 0.55),
        (x + size * 0.45, y + size * 0.55),
        (x + size * 0.35, y + size),
        (x + size * 0.85, y + size * 0.42),
        (x + size * 0.55, y + size * 0.42)
    ]
    draw.polygon(pts, fill=color)

def draw_shield(draw, x, y, size, color):
    w = size * 0.85
    h = size
    pts = [
        (x + w * 0.5, y),
        (x + w, y + h * 0.2),
        (x + w * 0.85, y + h * 0.75),
        (x + w * 0.5, y + h),
        (x + w * 0.15, y + h * 0.75),
        (x, y + h * 0.2)
    ]
    draw.polygon(pts, fill=color)
    draw.line([(x + w * 0.28, y + h * 0.5), (x + w * 0.46, y + h * 0.68), (x + w * 0.72, y + h * 0.35)], fill=(12, 16, 28, 255), width=3)

def draw_chip(draw, x, y, size, color):
    w, h = size * 0.8, size * 0.8
    draw.rectangle([x, y, x + w, y + h], fill=color)
    draw.rectangle([x + w * 0.25, y + h * 0.25, x + w * 0.75, y + h * 0.75], fill=(12, 16, 28, 255))
    for p in [0.25, 0.75]:
        draw.line([(x + w * p, y - 5), (x + w * p, y)], fill=color, width=2)
        draw.line([(x + w * p, y + h), (x + w * p, y + h + 5)], fill=color, width=2)
        draw.line([(x - 5, y + h * p), (x, y + h * p)], fill=color, width=2)
        draw.line([(x + w, y + h * p), (x + w + 5, y + h * p)], fill=color, width=2)

def draw_radar(draw, x, y, size, color):
    r = size * 0.45
    cx, cy = x + r, y + r
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=3)
    draw.ellipse([cx - r * 0.5, cy - r * 0.5, cx + r * 0.5, cy + r * 0.5], fill=color)
    draw.line([(cx, cy), (cx + r * 0.7, cy - r * 0.7)], fill=color, width=3)

def get_font(name_list, size):
    for name in name_list:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            try:
                return ImageFont.truetype(f"C:/Windows/Fonts/{name}", size)
            except Exception:
                pass
    return ImageFont.load_default()

def create_social_preview_template(output_path="social_preview.png"):
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    W, H = 2560, 1280
    
    # 1. Base dark background
    img = Image.new("RGBA", (W, H), (10, 13, 22, 255))
    
    # 2. Ambient Lighting
    glow_top = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_top = ImageDraw.Draw(glow_top)
    cx1, cy1 = int(W * 0.5), int(H * 0.32)
    for r in range(1000, 0, -25):
        alpha = int(65 * (1 - r / 1000) ** 1.8)
        draw_top.ellipse([cx1 - r, cy1 - r, cx1 + r, cy1 + r], fill=(0, 190, 255, alpha))
        
    glow_side = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_side = ImageDraw.Draw(glow_side)
    for px, py in [(int(W * 0.12), int(H * 0.65)), (int(W * 0.88), int(H * 0.65))]:
        for r in range(800, 0, -25):
            alpha = int(42 * (1 - r / 800) ** 1.8)
            draw_side.ellipse([px - r, py - r, px + r, py + r], fill=(155, 45, 255, alpha))

    glow_gem = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_gem = ImageDraw.Draw(glow_gem)
    for r in range(500, 0, -20):
        alpha = int(50 * (1 - r / 500) ** 1.8)
        draw_gem.ellipse([W//2 - r, int(H * 0.20) - r, W//2 + r, int(H * 0.20) + r], fill=(0, 255, 170, alpha))

    img = Image.alpha_composite(img, glow_top)
    img = Image.alpha_composite(img, glow_side)
    img = Image.alpha_composite(img, glow_gem)
    
    # 3. Cyber Grid Layer
    grid_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_grid = ImageDraw.Draw(grid_img)
    
    grid_step = 80
    for x in range(0, W, grid_step):
        alpha = int(14 + 10 * math.sin(x / 200.0))
        draw_grid.line([(x, 0), (x, H)], fill=(70, 110, 200, alpha), width=1)
        
    for y in range(0, H, grid_step):
        alpha = int(14 + 10 * math.sin(y / 200.0))
        draw_grid.line([(0, y), (W, y)], fill=(70, 110, 200, alpha), width=1)
        
    random.seed(2026)
    for _ in range(80):
        rx = random.randint(1, W // grid_step - 1) * grid_step
        ry = random.randint(1, H // grid_step - 1) * grid_step
        draw_grid.rectangle([rx - 2, ry - 2, rx + 2, ry + 2], fill=(0, 230, 255, 60))
        if random.random() < 0.2:
            draw_grid.line([(rx - 10, ry), (rx + 10, ry)], fill=(0, 230, 255, 90), width=1)
            draw_grid.line([(rx, ry - 10), (rx, ry + 10)], fill=(0, 230, 255, 90), width=1)

    img = Image.alpha_composite(img, grid_img)
    
    # 4. Concentric Tech Orbital Rings
    ring_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_ring = ImageDraw.Draw(ring_img)
    
    rcx, rcy = W // 2, int(H * 0.20)
    for radius in [200, 340, 500, 700]:
        draw_ring.ellipse([rcx - radius, rcy - radius, rcx + radius, rcy + radius], outline=(100, 160, 255, 25), width=2)
        
    for angle in range(0, 360, 8):
        rad = math.radians(angle)
        rad_end = math.radians(angle + 4)
        r = 340
        x1 = rcx + r * math.cos(rad)
        y1 = rcy + r * math.sin(rad)
        x2 = rcx + r * math.cos(rad_end)
        y2 = rcy + r * math.sin(rad_end)
        draw_ring.line([(x1, y1), (x2, y2)], fill=(0, 220, 255, 70), width=3)
        
    for _ in range(60):
        px = random.randint(180, W - 180)
        py = random.randint(120, H - 120)
        pr = random.randint(2, 5)
        draw_ring.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(180, 220, 255, random.randint(40, 140)))
        
    img = Image.alpha_composite(img, ring_img)
    
    # 5. UI Elements Layer (Centered Layout)
    ui_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_ui = ImageDraw.Draw(ui_img)
    
    font_badge = get_font(["segoeuib.ttf", "arialbd.ttf"], 26)
    font_title = get_font(["segoeuib.ttf", "arialbd.ttf"], 124)
    font_sub = get_font(["segoeuib.ttf", "arialbd.ttf"], 44)
    font_desc = get_font(["segoeui.ttf", "arial.ttf"], 30)
    font_card_h = get_font(["segoeuib.ttf", "arialbd.ttf"], 32)
    font_card_p = get_font(["segoeui.ttf", "arial.ttf"], 22)
    font_footer = get_font(["segoeuib.ttf", "arialbd.ttf"], 26)

    # 5a. Levitating Quantum Core at Top Center
    core_cx, core_cy = W // 2, 205
    
    hex_r = 100
    pts = []
    for deg in range(30, 390, 60):
        rad = math.radians(deg)
        pts.append((core_cx + hex_r * math.cos(rad), core_cy + hex_r * math.sin(rad)))
    draw_ui.polygon(pts, fill=(18, 26, 48, 230), outline=(0, 230, 255, 180), width=3)
    
    for r in range(60, 0, -4):
        alpha = int(220 * (1 - r / 60) ** 1.4)
        draw_ui.ellipse([core_cx - r, core_cy - r, core_cx + r, core_cy + r], fill=(0, 240, 255, alpha))
    for r in range(28, 0, -3):
        alpha = int(255 * (1 - r / 28))
        draw_ui.ellipse([core_cx - r, core_cy - r, core_cx + r, core_cy + r], fill=(255, 255, 255, alpha))
        
    draw_ui.ellipse([core_cx - 85, core_cy - 28, core_cx + 85, core_cy + 28], outline=(0, 255, 170, 210), width=3)
    draw_ui.ellipse([core_cx - 28, core_cy - 85, core_cx + 28, core_cy + 85], outline=(190, 80, 255, 200), width=3)
    
    # 5b. Pill Badge
    pill_text = "ANTIGRAVITY UNLOCKER v2.0  •  ZERO VPN  •  PRODUCTION READY"
    bbox = draw_ui.textbbox((0, 0), pill_text, font=font_badge)
    pw = (bbox[2] - bbox[0]) + 100
    ph = 54
    px = (W - pw) // 2
    py = 345
    
    draw_ui.rounded_rectangle([px, py, px + pw, py + ph], radius=27, fill=(18, 28, 50, 230), outline=(0, 220, 255, 150), width=2)
    # Green pulse LED
    draw_ui.ellipse([px + 22, py + 19, px + 36, py + 33], fill=(0, 255, 160, 255))
    draw_ui.ellipse([px + 18, py + 15, px + 40, py + 37], outline=(0, 255, 160, 120), width=2)
    # Mini lightning bolt inside pill
    draw_lightning(draw_ui, px + 46, py + 16, 22, (0, 230, 255))
    draw_ui.text((px + 78, py + 10), pill_text, fill=(210, 245, 255, 255), font=font_badge)

    # 5c. Giant Main Title (Centered)
    title_text = "ANTIGRAVITY UNLOCKER"
    tbox = draw_ui.textbbox((0, 0), title_text, font=font_title)
    tw = tbox[2] - tbox[0]
    tx = (W - tw) // 2
    ty = 430
    draw_ui.text((tx + 4, ty + 4), title_text, fill=(0, 100, 190, 130), font=font_title)
    draw_ui.text((tx, ty), title_text, fill=(255, 255, 255, 255), font=font_title)
    
    # 5d. Subtitle
    sub_text = "Автономная работа Google Antigravity IDE & Gemini в РФ без VPN"
    sbox = draw_ui.textbbox((0, 0), sub_text, font=font_sub)
    sw = sbox[2] - sbox[0]
    sx = (W - sw) // 2
    sy = ty + 145
    draw_ui.text((sx, sy), sub_text, fill=(180, 210, 245, 255), font=font_sub)
    
    # Tagline
    tag_text = "Прямой интернет на скорости провайдера  •  Smart Auto-Failover  •  Бинарный патч 100% точности"
    tag_box = draw_ui.textbbox((0, 0), tag_text, font=font_desc)
    tag_w = tag_box[2] - tag_box[0]
    tag_x = (W - tag_w) // 2
    tag_y = sy + 62
    draw_ui.text((tag_x, tag_y), tag_text, fill=(0, 225, 255, 230), font=font_desc)

    # 5e. 4 Feature Cards Row (Centered)
    cards = [
        ("lightning", "Zero VPN Routing", "Прямая скорость провайдера", (0, 230, 255)),
        ("shield", "Anti-Leak Hosts", "100% изоляция эндпоинтов", (170, 95, 255)),
        ("chip", "Binary Patch Engine", "Патч Language Server без багов", (0, 255, 170)),
        ("radar", "Auto-Failover 443", "Мгновенный обход сбоев (10054)", (255, 185, 45)),
    ]
    
    card_w = 520
    card_h = 130
    gap = 26
    total_cards_w = 4 * card_w + 3 * gap
    start_cx = (W - total_cards_w) // 2
    cards_y = 765
    
    for i, (icon_t, head, desc, col) in enumerate(cards):
        cx = start_cx + i * (card_w + gap)
        cy = cards_y
        
        draw_ui.rounded_rectangle([cx, cy, cx + card_w, cy + card_h], radius=20, fill=(15, 22, 38, 220), outline=(50, 75, 110, 160), width=2)
        draw_ui.rounded_rectangle([cx + 5, cy + 18, cx + 11, cy + card_h - 18], radius=3, fill=col)
        
        ix, iy = cx + 24, cy + 22
        if icon_t == "lightning":
            draw_lightning(draw_ui, ix, iy, 32, col)
        elif icon_t == "shield":
            draw_shield(draw_ui, ix, iy, 32, col)
        elif icon_t == "chip":
            draw_chip(draw_ui, ix, iy, 32, col)
        elif icon_t == "radar":
            draw_radar(draw_ui, ix, iy, 32, col)
            
        draw_ui.text((cx + 66, cy + 24), head, fill=(245, 250, 255, 255), font=font_card_h)
        draw_ui.text((cx + 66, cy + 74), desc, fill=(145, 170, 200, 255), font=font_card_p)
        
    # 5f. Bottom Footer Badge Strip
    foot_y = 985
    draw_ui.line([(240, foot_y), (W - 240, foot_y)], fill=(45, 68, 100, 130), width=2)
    
    items = [
        "●  Windows 10 / 11",
        "●  Standalone 1-Click EXE",
        "●  Gemini 3.1 & Claude 3.7",
        "●  Open Source (MIT License)",
    ]
    total_w = sum([draw_ui.textbbox((0,0), it, font=font_footer)[2] - draw_ui.textbbox((0,0), it, font=font_footer)[0] for it in items]) + (len(items)-1)*100
    cur_fx = (W - total_w) // 2
    for it in items:
        draw_ui.text((cur_fx, foot_y + 38), it, fill=(160, 195, 235, 230), font=font_footer)
        cur_fx += (draw_ui.textbbox((0,0), it, font=font_footer)[2] - draw_ui.textbbox((0,0), it, font=font_footer)[0]) + 100

    img = Image.alpha_composite(img, ui_img)
    
    final_img = img.resize((1280, 640), Image.Resampling.LANCZOS)
    final_img.convert("RGB").save(output_path, quality=98)
    print(f"Template-aligned banner generated: {output_path} (1280x640)")

if __name__ == "__main__":
    create_social_preview_template("social_preview.png")
    create_social_preview_template("docs/social_preview.png")
