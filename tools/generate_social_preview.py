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
    inner_pts = [
        (x + w * 0.5, y + 4),
        (x + w - 4, y + h * 0.2 + 2),
        (x + w * 0.85 - 3, y + h * 0.75 - 2),
        (x + w * 0.5, y + h - 4),
        (x + w * 0.15 + 3, y + h * 0.75 - 2),
        (x + 4, y + h * 0.2 + 2)
    ]
    draw.polygon(inner_pts, fill=(20, 15, 35, 255))
    # Core checkmark inside shield
    draw.line([(x + w * 0.3, y + h * 0.5), (x + w * 0.48, y + h * 0.68), (x + w * 0.75, y + h * 0.35)], fill=color, width=3)

def draw_chip(draw, x, y, size, color):
    w, h = size * 0.8, size * 0.8
    draw.rectangle([x, y, x + w, y + h], fill=(20, 35, 30, 255), outline=color, width=3)
    draw.rectangle([x + w * 0.25, y + h * 0.25, x + w * 0.75, y + h * 0.75], fill=color)
    # Pins
    for p in [0.25, 0.75]:
        draw.line([(x + w * p, y - 5), (x + w * p, y)], fill=color, width=2)
        draw.line([(x + w * p, y + h), (x + w * p, y + h + 5)], fill=color, width=2)
        draw.line([(x - 5, y + h * p), (x, y + h * p)], fill=color, width=2)
        draw.line([(x + w, y + h * p), (x + w + 5, y + h * p)], fill=color, width=2)

def draw_radar(draw, x, y, size, color):
    r = size * 0.45
    cx, cy = x + r, y + r
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=3)
    draw.ellipse([cx - r * 0.5, cy - r * 0.5, cx + r * 0.5, cy + r * 0.5], outline=color, width=2)
    draw.line([(cx - r, cy), (cx + r, cy)], fill=color, width=2)
    draw.line([(cx, cy - r), (cx, cy + r)], fill=color, width=2)
    # Sweep beam
    draw.line([(cx, cy), (cx + r * 0.7, cy - r * 0.7)], fill=(255, 255, 255, 255), width=3)

def draw_win_logo(draw, x, y, size, color):
    s = size * 0.45
    gap = size * 0.1
    draw.rectangle([x, y, x + s, y + s], fill=color)
    draw.rectangle([x + s + gap, y, x + 2*s + gap, y + s], fill=color)
    draw.rectangle([x, y + s + gap, x + s, y + 2*s + gap], fill=color)
    draw.rectangle([x + s + gap, y + s + gap, x + 2*s + gap, y + 2*s + gap], fill=color)

def draw_terminal_icon(draw, x, y, size, color):
    w, h = size, size * 0.75
    draw.rounded_rectangle([x, y, x + w, y + h], radius=4, fill=(15, 22, 35, 255), outline=color, width=2)
    draw.line([(x + 6, y + 8), (x + 14, y + 15), (x + 6, y + 22)], fill=color, width=2)
    draw.line([(x + 16, y + 22), (x + 24, y + 22)], fill=color, width=2)

def draw_ai_spark(draw, x, y, size, color):
    cx, cy = x + size * 0.5, y + size * 0.5
    r1 = size * 0.5
    r2 = size * 0.15
    pts = []
    for i in range(8):
        ang = i * math.pi / 4
        r = r1 if i % 2 == 0 else r2
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    draw.polygon(pts, fill=color)

def draw_lock_icon(draw, x, y, size, color):
    w, h = size * 0.8, size * 0.6
    draw.rounded_rectangle([x, y + size * 0.35, x + w, y + size * 0.35 + h], radius=4, fill=color)
    draw.arc([x + w * 0.2, y, x + w * 0.8, y + size * 0.55], start=180, end=0, fill=color, width=3)

def create_social_preview(output_path="social_preview.png"):
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    W, H = 2560, 1280
    
    # 1. Base dark background
    img = Image.new("RGBA", (W, H), (9, 11, 19, 255))
    
    # 2. Ambient Lighting
    glow_cyan = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_cyan = ImageDraw.Draw(glow_cyan)
    cx, cy = int(W * 0.18), int(H * 0.28)
    for r in range(900, 0, -25):
        alpha = int(48 * (1 - r / 900) ** 1.8)
        draw_cyan.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(0, 210, 255, alpha))
    
    glow_purple = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_purple = ImageDraw.Draw(glow_purple)
    px, py = int(W * 0.82), int(H * 0.38)
    for r in range(950, 0, -25):
        alpha = int(55 * (1 - r / 950) ** 1.7)
        draw_purple.ellipse([px - r, py - r, px + r, py + r], fill=(160, 45, 255, alpha))
        
    glow_green = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_green = ImageDraw.Draw(glow_green)
    gx, gy = int(W * 0.45), int(H * 0.9)
    for r in range(750, 0, -25):
        alpha = int(35 * (1 - r / 750) ** 2.0)
        draw_green.ellipse([gx - r, gy - r, gx + r, gy + r], fill=(0, 245, 160, alpha))
        
    img = Image.alpha_composite(img, glow_cyan)
    img = Image.alpha_composite(img, glow_purple)
    img = Image.alpha_composite(img, glow_green)
    
    # 3. Cyber Grid Layer
    grid_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_grid = ImageDraw.Draw(grid_img)
    
    for x in range(0, W, 80):
        alpha = int(16 + 10 * math.sin(x / 220.0))
        draw_grid.line([(x, 0), (x, H)], fill=(75, 125, 220, alpha), width=1)
        
    for y in range(0, H, 80):
        alpha = int(16 + 10 * math.sin(y / 220.0))
        draw_grid.line([(0, y), (W, y)], fill=(75, 125, 220, alpha), width=1)
        
    random.seed(1337)
    for _ in range(80):
        rx = random.randint(1, W // 80 - 1) * 80
        ry = random.randint(1, H // 80 - 1) * 80
        size = random.choice([2, 3, 4])
        draw_grid.rectangle([rx - size, ry - size, rx + size, ry + size], fill=(0, 230, 255, 75))
        if random.random() < 0.3:
            draw_grid.line([(rx - 12, ry), (rx + 12, ry)], fill=(0, 230, 255, 110), width=1)
            draw_grid.line([(rx, ry - 12), (rx, ry + 12)], fill=(0, 230, 255, 110), width=1)

    img = Image.alpha_composite(img, grid_img)
    
    # 4. HUD Rings & Orbital Celestial Tech in background
    hud_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_hud = ImageDraw.Draw(hud_img)
    
    hud_center_x, hud_center_y = int(W * 0.80), int(H * 0.48)
    for radius in [260, 360, 480, 640]:
        draw_hud.ellipse([hud_center_x - radius, hud_center_y - radius,
                          hud_center_x + radius, hud_center_y + radius],
                         outline=(100, 160, 255, 30), width=2)
                         
    # Orbital ticks
    for angle in range(0, 360, 10):
        rad = math.radians(angle)
        rad_end = math.radians(angle + 4)
        r = 360
        x1 = hud_center_x + r * math.cos(rad)
        y1 = hud_center_y + r * math.sin(rad)
        x2 = hud_center_x + r * math.cos(rad_end)
        y2 = hud_center_y + r * math.sin(rad_end)
        draw_hud.line([(x1, y1), (x2, y2)], fill=(0, 220, 255, 90), width=3)
        
    for _ in range(70):
        px = random.randint(int(W * 0.58), W - 50)
        py = random.randint(40, H - 90)
        pr = random.randint(2, 5)
        draw_hud.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(190, 230, 255, random.randint(50, 180)))
        
    img = Image.alpha_composite(img, hud_img)
    
    # Fonts
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
        
    font_badge = get_font(["segoeuib.ttf", "arialbd.ttf"], 28)
    font_title = get_font(["segoeuib.ttf", "arialbd.ttf"], 108)
    font_sub = get_font(["segoeui.ttf", "arial.ttf"], 42)
    font_card_h = get_font(["segoeuib.ttf", "arialbd.ttf"], 36)
    font_card_p = get_font(["segoeui.ttf", "arial.ttf"], 25)
    font_footer = get_font(["segoeuib.ttf", "arialbd.ttf"], 28)

    # UI Elements Layer
    ui_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_ui = ImageDraw.Draw(ui_img)
    
    # Frame tech brackets
    draw_ui.line([(40, 60), (40, H - 60)], fill=(0, 220, 255, 180), width=6)
    draw_ui.line([(40, 60), (110, 60)], fill=(0, 220, 255, 180), width=6)
    draw_ui.line([(40, H - 60), (110, H - 60)], fill=(0, 220, 255, 180), width=6)
    
    # Top Status Pill
    bx, by = 120, 110
    bw, bh = 1060, 64
    draw_ui.rounded_rectangle([bx, by, bx + bw, by + bh], radius=32, fill=(20, 32, 54, 210), outline=(0, 220, 255, 150), width=2)
    # Green pulse LED
    draw_ui.ellipse([bx + 26, by + 24, bx + 42, by + 40], fill=(0, 255, 160, 255))
    draw_ui.ellipse([bx + 21, by + 19, bx + 47, by + 45], outline=(0, 255, 160, 120), width=2)
    
    badge_str = "ANTIGRAVITY UNLOCKER v2.0   •   PRODUCTION READY   •   ZERO VPN"
    draw_ui.text((bx + 60, by + 14), badge_str, fill=(210, 245, 255, 255), font=font_badge)

    # Title
    title_y = 210
    draw_ui.text((124, title_y + 4), "ANTIGRAVITY UNLOCKER", fill=(0, 100, 190, 130), font=font_title)
    draw_ui.text((120, title_y), "ANTIGRAVITY UNLOCKER", fill=(255, 255, 255, 255), font=font_title)
    
    # Subtitle
    sub_y = title_y + 132
    draw_ui.text((120, sub_y), "Комплекс автономной работы Google Antigravity & Gemini без VPN", fill=(170, 195, 230, 255), font=font_sub)
    draw_ui.text((120, sub_y + 58), "Прямой интернет на скорости провайдера  •  Умный Auto-Failover  •  Бинарный патч", fill=(0, 228, 255, 230), font=font_card_p)

    # Feature Cards Grid (2x2)
    card_info = [
        {
            "icon_type": "lightning",
            "title": "Zero VPN Architecture",
            "desc": "Прямая скорость без просадок и скрытых задержек",
            "color": (0, 230, 255)
        },
        {
            "icon_type": "shield",
            "title": "Anti-Leak Hosts Pinning",
            "desc": "100% изоляция DNS и защита эндпоинтов Google",
            "color": (170, 95, 255)
        },
        {
            "icon_type": "chip",
            "title": "Binary Patch Engine",
            "desc": "Патч Language Server без повреждения Protobuf",
            "color": (0, 255, 170)
        },
        {
            "icon_type": "radar",
            "title": "Auto-Failover Watchdog",
            "desc": "Мгновенное переключение при сбоях (10054)",
            "color": (255, 185, 45)
        },
    ]
    
    start_x = 120
    start_y = 480
    card_w = 660
    card_h = 135
    gap_x = 40
    gap_y = 30
    
    for i, card in enumerate(card_info):
        row = i // 2
        col = i % 2
        cx = start_x + col * (card_w + gap_x)
        cy = start_y + row * (card_h + gap_y)
        
        # Card Background
        draw_ui.rounded_rectangle([cx, cy, cx + card_w, cy + card_h], radius=20, fill=(16, 23, 40, 220), outline=(55, 78, 110, 150), width=2)
        # Left Accent bar
        draw_ui.rounded_rectangle([cx + 5, cy + 18, cx + 11, cy + card_h - 18], radius=3, fill=card["color"])
        
        # Draw custom vector icon
        ix, iy = cx + 28, cy + 24
        itype = card["icon_type"]
        if itype == "lightning":
            draw_lightning(draw_ui, ix, iy, 34, card["color"])
        elif itype == "shield":
            draw_shield(draw_ui, ix, iy, 34, card["color"])
        elif itype == "chip":
            draw_chip(draw_ui, ix, iy, 34, card["color"])
        elif itype == "radar":
            draw_radar(draw_ui, ix, iy, 34, card["color"])
            
        draw_ui.text((cx + 72, cy + 22), card["title"], fill=(245, 250, 255, 255), font=font_card_h)
        draw_ui.text((cx + 72, cy + 74), card["desc"], fill=(145, 168, 198, 255), font=font_card_p)
        
    # Right Side Graphic: Holographic Shield & Levitating Quantum Core
    right_cx = 1960
    right_cy = 580
    
    # Outer Tech Hexagon
    hex_r = 240
    points = []
    for deg in range(30, 390, 60):
        rad = math.radians(deg)
        points.append((right_cx + hex_r * math.cos(rad), right_cy + hex_r * math.sin(rad)))
    draw_ui.polygon(points, outline=(0, 220, 255, 160), width=4)
    
    # Inner Hexagon
    inner_points = []
    for deg in range(30, 390, 60):
        rad = math.radians(deg)
        inner_points.append((right_cx + (hex_r - 30) * math.cos(rad), right_cy + (hex_r - 30) * math.sin(rad)))
    draw_ui.polygon(inner_points, fill=(18, 25, 48, 220), outline=(160, 85, 255, 180), width=3)
    
    # Core Glowing Orb
    for r in range(120, 0, -6):
        alpha = int(220 * (1 - r / 120) ** 1.5)
        draw_ui.ellipse([right_cx - r, right_cy - r, right_cx + r, right_cy + r], fill=(0, 225, 255, alpha))
    for r in range(60, 0, -4):
        alpha = int(255 * (1 - r / 60) ** 1.2)
        draw_ui.ellipse([right_cx - r, right_cy - r, right_cx + r, right_cy + r], fill=(255, 255, 255, alpha))
        
    # Floating Quantum Rings
    draw_ui.ellipse([right_cx - 185, right_cy - 65, right_cx + 185, right_cy + 65], outline=(0, 255, 180, 210), width=4)
    draw_ui.ellipse([right_cx - 65, right_cy - 185, right_cx + 65, right_cy + 185], outline=(210, 85, 255, 190), width=4)

    # Telemetry Badges
    pill1_x, pill1_y = right_cx - 240, right_cy - 200
    draw_ui.rounded_rectangle([pill1_x, pill1_y, pill1_x + 230, pill1_y + 54], radius=18, fill=(10, 25, 42, 240), outline=(0, 255, 160, 190), width=2)
    draw_ui.ellipse([pill1_x + 18, pill1_y + 20, pill1_x + 32, pill1_y + 34], fill=(0, 255, 160, 255))
    draw_ui.text((pill1_x + 42, pill1_y + 12), "PING: 38 ms", fill=(0, 255, 160, 255), font=font_badge)

    pill2_x, pill2_y = right_cx + 70, right_cy + 170
    draw_ui.rounded_rectangle([pill2_x, pill2_y, pill2_x + 250, pill2_y + 54], radius=18, fill=(28, 16, 45, 240), outline=(190, 90, 255, 190), width=2)
    draw_ui.ellipse([pill2_x + 18, pill2_y + 20, pill2_x + 32, pill2_y + 34], fill=(190, 90, 255, 255))
    draw_ui.text((pill2_x + 42, pill2_y + 12), "TLS 1.3 PASS", fill=(215, 150, 255, 255), font=font_badge)

    # Bottom Banner / Footer Bar
    foot_y = H - 150
    draw_ui.line([(120, foot_y), (W - 120, foot_y)], fill=(50, 75, 110, 130), width=2)
    
    footer_items = [
        ("win", "Windows 10 / 11"),
        ("term", "Standalone 1-Click EXE"),
        ("spark", "Gemini 3.1 & Claude 3.7"),
        ("lock", "Open Source (MIT)"),
    ]
    
    fx = 120
    for icon_name, item_text in footer_items:
        iy = foot_y + 38
        if icon_name == "win":
            draw_win_logo(draw_ui, fx, iy, 28, (0, 220, 255, 230))
        elif icon_name == "term":
            draw_terminal_icon(draw_ui, fx, iy, 30, (0, 220, 255, 230))
        elif icon_name == "spark":
            draw_ai_spark(draw_ui, fx, iy, 28, (200, 110, 255, 240))
        elif icon_name == "lock":
            draw_lock_icon(draw_ui, fx, iy, 28, (0, 255, 170, 230))
            
        draw_ui.text((fx + 44, foot_y + 34), item_text, fill=(170, 195, 230, 240), font=font_footer)
        fx += 580
        
    img = Image.alpha_composite(img, ui_img)
    
    # Downsample from 2560x1280 to exactly 1280x640 with high quality Lanczos filter
    final_img = img.resize((1280, 640), Image.Resampling.LANCZOS)
    final_img.convert("RGB").save(output_path, quality=98)
    print(f"Banner generated: {output_path}")

if __name__ == "__main__":
    create_social_preview("social_preview.png")
    create_social_preview("docs/social_preview.png")
