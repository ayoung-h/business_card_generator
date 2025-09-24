from PIL import Image, ImageDraw, ImageFont
import random
import colorsys
import os
from django.conf import settings
import qrcode

TEMPLATES = [
    'modern', 'cute', 'retro', 'neon', 'galaxy', 'minimalist', 'grunge'
]

COLOR_THEMES = [
    'monochrome', 'gradient', 'complementary', 'pastel', 'vibrant'
]

LAYOUTS = [
    'center', 'left_align', 'diagonal', 'corner'
]

def hex_to_rgb(hex_color): #HEX 색상 RGB 변환
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hsl(rgb): #RGB를 HSL로 변환
    r, g, b = [x/255.0 for x in rgb]
    return colorsys.rgb_to_hls(r, g, b)

def hsl_to_rgb(hsl): #HSL을 RGB로 변환
    h, l, s = hsl
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return tuple(int(x * 255) for x in (r, g, b))

def generate_color_palette(base_color_hex): #기본 색상 바탕 팔레트 생성
    base_rgb = hex_to_rgb(base_color_hex)
    base_hsl = rgb_to_hsl(base_rgb)

    h, l, s = base_hsl

    #다양한 색 조합 생성
    colors = {
        'primary': base_rgb,
        'secondary': hsl_to_rgb(((h + 0.3) % 1, l, s)),
        'accent': hsl_to_rgb((h, min(l + 0.2, 1), s)),
        'light': hsl_to_rgb((h, min(l + 0.4, 1), max(s - 0.3, 0))),
        'dark': hsl_to_rgb((h, max(l - 0.3, 0), s)),
    }

    return colors

def create_business_card(user_data): #명함 이미지 생성
    template = random.choice(TEMPLATES)
    theme = random.choice(COLOR_THEMES)
    layout = random.choice(LAYOUTS)

    colors = generate_color_palette(user_data['favorite_color'])

    width, height = 800, 500

    img = Image.new('RGB', (width, height), colors['light'])
    draw = ImageDraw.Draw(img)

    if template == 'modern':
        draw_modern_template(draw, width, height, colors, user_data, layout)
    elif template == 'cute':
        draw_cute_template(draw, width, height, colors, user_data, layout)
    elif template == 'retro':
        draw_retro_template(draw, width, height, colors, user_data, layout)
    elif template == 'neon':
        draw_neon_template(draw, width, height, colors, user_data, layout)
    elif template == 'galaxy':
        draw_galaxy_template(draw, width, height, colors, user_data, layout)
    elif template == 'minimalist':
        draw_minimalist_template(draw, width, height, colors, user_data, layout)
    else:
        draw_grunge_template(draw, width, height, colors, user_data, layout)

    return img, template

def draw_modern_template(draw, width, height, colors, user_data, layout): #모던 템플릿
    for y in range(height):
        alpha = y / height
        color = tuple(int(colors['primary'][i] * (1 - alpha) + colors['secondary'][i] * alpha) for i in range(3))
        draw.line([(0, y), (width, y)], fill=color)

    draw.rectangle([50, 50, width-50, height-50], outline=colors['accent'], width=3)

    try:
        font_large = ImageFont.truetype("arial.ttf", 48)
        font_medium = ImageFont.truetype("arial.ttf", 32)
        font_small = ImageFont.truetype("arial.ttf", 24)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.text((100, 150), user_data['name'], fill=colors['dark'], font=font_large)
    draw.text((100, 220), user_data['school'], fill=colors['dark'], font=font_medium)
    draw.text((100, 280), user_data['phone'], fill=colors['dark'], font=font_small)

def draw_cute_template(draw, width, height, colors, user_data, layout): #큐트 템플릿
    pastel_color = tuple(min(255, c+50) for c in colors['primary'])
    draw.rectangle([0, 0, width, height], fill=pastel_color)

    for i in range(5):
        x = random.randint(50, width-100)
        y = random.randint(50, height-100)
        draw.ellipse([x, y, x+30, y+30], fill=colors['accent'])

    draw.rounded_rectangle([40, 40, width-40, height-40], radius=20, outline=colors['primary'], width=4)

    try:
        font_large = ImageFont.truetype("arial.ttf", 42)
        font_medium = ImageFont.truetype("arial.ttf", 28)
        font_small = ImageFont.truetype("arial.ttf", 22)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.text((width//2-100, 180), user_data['name'], fill=colors['dark'], font=font_large)
    draw.text((width//2-80, 240), user_data['school'], fill=colors['dark'], font=font_medium)
    draw.text((width//2-70, 300), user_data['phone'], fill=colors['dark'], font=font_small)

def draw_retro_template(draw, width, height, colors, user_data, layout): #레트로 템플릿
    retro_bg = (245, 222, 179)
    draw.rectangle([0, 0, width, height], fill=retro_bg)

    for i in range(5):
        draw.rectangle([10+i*2, 10+i*2, width-10-i*2, height-10-i*2], outline=colors['primary'], width=2)

    try:
        font_large = ImageFont.truetype("arial.ttf", 44)
        font_medium = ImageFont.truetype("arial.ttf", 30)
        font_small = ImageFont.truetype("arial.ttf", 26)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.text((120, 160), user_data['name'], fill=colors['dark'], font=font_large)
    draw.text((120, 220), user_data['school'], fill=colors['dark'], font=font_medium)
    draw.text((120, 280), user_data['phone'], fill=colors['dark'], font=font_small)

def draw_neon_template(draw, width, height, colors, user_data, layout): #네온 템플릿
    draw.rectangle([0, 0, width, height], fill=(20, 20, 20))

    neon_color = colors['primary']
    for thickness in range(8, 0, -1):
        alpha = 255 - thickness * 20
        draw.rectangle([60-thickness, 60-thickness, width-60+thickness, height-60+thickness], outline=neon_color, width=thickness)

    try:
        font_large = ImageFont.truetype("arial.ttf", 46)
        font_medium = ImageFont.truetype("arial.ttf", 32)
        font_small = ImageFont.truetype("arial.ttf", 28)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.text((100, 150), user_data['name'], fill=(255, 255, 255), font=font_large)
    draw.text((100, 220), user_data['school'], fill=colors['accent'], font=font_medium)
    draw.text((100, 280), user_data['phone'], fill=colors['secondary'], font=font_small)

def draw_galaxy_template(draw, width, height, colors, user_data, layout): #갤럭시 템플릿
    draw.rectangle([0, 0, width, height], fill=(10, 10, 30))

    for i in range(50):
        x = random.randint(0, width)
        y = random.randint(0, height)
        brightness = random.randint(100, 255)
        draw.point((x, y), fill=(brightness, brightness, brightness))

    try:
        font_large = ImageFont.truetype("arial.ttf", 48)
        font_medium = ImageFont.truetype("arial.ttf", 34)
        font_small = ImageFont.truetype("arial.ttf", 30)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.text((110, 150), user_data['name'], fill=['accent'], font=font_large)
    draw.text((110, 220), user_data['school'], fill=(200, 200, 255), font=font_medium)
    draw.text((110, 280), user_data['phone'], fill=(255, 255, 200), font=font_small)

def draw_minimalist_template(draw, width, height, colors, user_data, layout): #미니멀 템플릿
    draw.rectangle([0, 0, width, height], fill=(255, 255, 255))

    draw.line([(100, 140), (width-100, 140)], fill=colors['primary'], width=2)
    draw.line([(100, height-100), (width-100, height-100)], fill=colors['primary'], width=2)

    try:
        font_large = ImageFont.truetype("arial.ttf", 42)
        font_medium = ImageFont.truetype("arial.ttf", 28)
        font_small = ImageFont.truetype("arial.ttf", 24)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.text((120, 180), user_data['name'], fill=(50, 50, 50), font=font_large)
    draw.text((120, 240), user_data['school'], fill=(100, 100, 100), font=font_medium)
    draw.text((120, 300), user_data['phone'], fill=(150, 150, 150), font=font_small)

def draw_grunge_template(draw, width, height, colors, user_data, layout): #그런지 템플릿
    base_color = tuple(max(0, c-30) for c in colors['primary'])
    draw.rectangle([0, 0, width, height], fill=base_color)

    for i in range(20):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill=colors['accent'], width=random.randint(1,3))

    try:
        font_large = ImageFont.truetype("arial.ttf", 44)
        font_medium = ImageFont.truetype("arial.ttf", 30)
        font_small = ImageFont.truetype("arial.ttf", 26)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.text((100, 160), user_data['name'], fill=colors['light'], font=font_large)
    draw.text((100, 220), user_data['school'], fill=colors['light'], font=font_medium)
    draw.text((100, 280), user_data['phone'], fill=colors['light'], font=font_small)

def generate_qr_code(download_url): #QR코드 생성
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(download_url)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white")
    return qr_img