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

def generate_color_palette(base_color_hex, theme): #기본 색상 바탕 팔레트 생성
    base_rgb = hex_to_rgb(base_color_hex)
    base_hsl = rgb_to_hsl(base_rgb)

    h, l, s = base_hsl

    #다양한 색 조합 생성
    if theme == 'complementary':
        h_secondary = (h+0.5) % 1
    elif theme == 'monochrome':
        h_secondary = h
    else:
        h_secondary = (h+0.3) % 1

    colors = {
        'primary': base_rgb,
        'secondary': hsl_to_rgb((h_secondary, l, s)),
        'accent': hsl_to_rgb((h, min(l + 0.2, 1), s)),
        'light': hsl_to_rgb((h, 0.95, 0.1)),
        'dark': hsl_to_rgb((h, 0.1, s)),
        }
    return colors

def get_font_path():
    font_dir = os.path.join(settings.BASE_DIR, 'static', 'fonts')
    return {
        'regular': os.path.join(font_dir, 'NanumGothic.ttf'),
        'bold': os.path.join(font_dir, 'NanumGothicBold.ttf'),
        'extrabold': os.path.join(font_dir, 'NanumGothicExtraBold.ttf'),
        'retro' : os.path.join(font_dir, 'BoldDunggeunmo.ttf'),
        'cute' : os.path.join(font_dir, 'Cutefont.ttf'),
        'grunge' : os.path.join(font_dir, 'BlackHanSans-Regular.ttf'),
    }

def get_font(size, weight='regular', font_name=None):
    font_paths = get_font_path()
    font_to_use = None

    if font_name and font_name in font_paths:
        font_to_use = font_paths[font_name]
    elif weight == 'bold' and os.path.exists(font_paths['bold']):
        font_to_use = font_paths['bold']
    elif weight == 'extrabold' and os.path.exists(font_paths['extrabold']):
        font_to_use = font_paths['extrabold']
    elif os.path.exists(font_paths['regular']):
        font_to_use = font_paths['regular']

    try:
        if font_to_use and os.path.exists(font_to_use):
            return ImageFont.truetype(font_to_use, size)
        else:
            print(f"폰트 파일을 찾을 수 없습니다: {font_name} 또는 {weight}")
            return ImageFont.load_default()
    except Exception as e:
        print(f"폰트 로드 오류: {e}")
        return ImageFont.load_default()

def create_business_card(user_data): #명함 이미지 생성
    template = random.choice(TEMPLATES)

    available_themes = COLOR_THEMES.copy()
    if template == 'neon':
        if 'pastel' in available_themes:
            available_themes.remove('pastel')
    elif template == 'minimalist':
        if 'complementary' in available_themes:
            available_themes.remove('complementary')

    theme = random.choice(available_themes)

    if template == 'modern':
        layout = 'left_align'
    elif template == 'cute':
        layout = 'center'
    elif template == 'retro':
        layout = 'center'
    elif template == 'minimalist':
        layout = 'left_align'
    elif template == 'galaxy':
        layout = 'left_align'
    else:
        layout = 'center'

    colors = generate_color_palette(user_data['favorite_color'], theme)

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
    draw.rectangle([0, 0, width, height], fill=colors['light'])
    draw.rectangle([0, 0, width // 4, height], fill=colors['primary'])
    draw.line([(width // 4, 0), (width // 4, height)], fill=colors['accent'], width=3)

    font_large = get_font(48, 'bold')
    font_medium = get_font(32, 'regular')
    font_small = get_font(24, 'regular')
    text_color = colors['dark']

    name_text = user_data['name']
    school_text = user_data['school']
    phone_text = user_data['phone']

    try:
        phone_width = draw.textbbox((0,0), phone_text, font=font_small)[2]
    except AttributeError:
        phone_width = font_small.getlength(phone_text)

    base_x = (width // 4) + 100
    name_x = base_x
    name_y = 150
    school_x = base_x
    school_y = 220

    draw.text((name_x, name_y), name_text, fill=text_color, font=font_large)
    draw.text((school_x, school_y), school_text, fill=text_color, font=font_medium)

    phone_x = width - phone_width - 100
    phone_y = height - 100

    draw.text((phone_x, phone_y), phone_text, fill=text_color, font=font_small)

def draw_cute_sparkle(draw, x, y, size, fill):
    half_size = size // 2
    draw.line([(x - half_size, y), (x + half_size, y)], fill=fill, width=2)
    draw.line([(x, y - half_size), (x, y + half_size)], fill=fill, width=2)
    if random.random() < 0.3:
        diag_size = half_size // 2
        draw.line([(x - diag_size, y - diag_size), (x + diag_size, y + diag_size)], fill=fill, width=1)
        draw.line([(x + diag_size, y - diag_size), (x - diag_size, y + diag_size)], fill=fill, width=1)

def draw_polka_dot(draw, x, y, size, fill):
    radius = size // 2
    draw.ellipse([x - radius, y -radius, x + radius, y + radius], fill=fill)

def draw_cute_template(draw, width, height, colors, user_data, layout): #큐트 템플릿
    pastel_bg = random.choice([colors['light'], tuple(min(255, c+50) for c in colors['primary'])])
    draw.rectangle([0, 0, width, height], fill=pastel_bg)
    pattern_color_1 = colors['accent']
    pattern_color_2 = colors['secondary']
    for i in range(25):
        x = random.randint(30, width - 30)
        y = random.randint(30, height - 30)
        size = random.randint(10, 25)

        if random.random() < 0.6:
            fill_color = random.choice([pattern_color_1, pattern_color_2, (255, 255, 255)])
            draw_polka_dot(draw, x, y, size, fill_color)
        else:
            fill_color = random.choice([pattern_color_1, (255, 255, 255)])
            draw_cute_sparkle(draw, x, y, size, fill_color)

    draw.rounded_rectangle([40, 40, width-40, height-40], radius=20, outline=colors['primary'], width=4)
    
    font_large = get_font(42, 'bold', font_name='cute')
    font_medium = get_font(28, 'regular', font_name='cute')
    font_small = get_font(22, 'regular', font_name='cute')
    text_color = colors['dark']

    name_text = user_data['name']
    school_text = user_data['school']
    phone_text = user_data['phone']

    name_width = draw.textbbox((0,0), name_text, font = font_large)[2]
    school_width = draw.textbbox((0,0), school_text, font = font_medium)[2]
    phone_width = draw.textbbox((0,0), phone_text, font = font_small)[2]

    name_x = (width - name_width) // 2
    name_y = 180
    school_x = (width - school_width) // 2
    school_y = 240

    draw.text((name_x, name_y), name_text, fill=text_color, font=font_large)
    draw.text((school_x, school_y), school_text, fill=text_color, font=font_medium)

    phone_x = (width - phone_width) // 2
    phone_y = height - 100

    draw.text((phone_x, phone_y), phone_text, fill=text_color, font=font_small)

def draw_retro_template(draw, width, height, colors, user_data, layout): #레트로 템플릿
    retro_bg = (245, 222, 179)
    draw.rectangle([0, 0, width, height], fill=retro_bg)
    grid_color = tuple(c - 15 for c in retro_bg)
    for i in range(0, width, 30):
        draw.line([(i, 0), (i, height)], fill=grid_color, width=1)
    for i in range(0, height, 30):
        draw.line([(0, i), (width, i)], fill=grid_color, width=1)
    draw.polygon([(width - 200, height), (width, height - 200), (width, height)], fill=colors['primary'])
    draw.polygon([(width - 150, height), (width, height - 150), (width, height)], fill=colors['accent'])
    for i in range(5):
        draw.rectangle([10+i*2, 10+i*2, width-10-i*2, height-10-i*2], outline=colors['primary'], width=2)

    font_large = get_font(44, 'bold', font_name='retro')
    font_medium = get_font(30, 'regular', font_name='retro')
    font_small = get_font(26, 'regular', font_name='retro')
    text_color = colors['dark']

    name_text = user_data['name']
    school_text = user_data['school']
    phone_text = user_data['phone']

    phone_width = draw.textbbox((0,0), school_text, font = font_medium)[2]

    name_x = 120
    name_y = 160
    school_x = 120
    school_y = 220

    draw.text((name_x, name_y), name_text, fill=text_color, font=font_large)
    draw.text((school_x, school_y), school_text, fill=text_color, font=font_medium)

    phone_x = width - phone_width - 120
    phone_y = height - 80

    draw.text((phone_x, phone_y), phone_text, fill=text_color, font=font_small)

def draw_neon_template(draw, width, height, colors, user_data, layout): #네온 템플릿
    draw.rectangle([0, 0, width, height], fill=(20, 20, 20))

    neon_color = colors['primary']
    for thickness in range(8, 0, -1):
        draw.rectangle([60-thickness, 60-thickness, width-60+thickness, height-60+thickness], outline=neon_color, width=thickness)

    font_large = get_font(46, 'bold')
    font_medium = get_font(32, 'regular')
    font_small = get_font(28, 'regular')

    name_text = user_data['name']
    school_text = user_data['school']
    phone_text = user_data['phone']

    name_width = draw.textbbox((0,0), name_text, font = font_large)[2]
    school_width = draw.textbbox((0,0), school_text, font = font_medium)[2]
    phone_width = draw.textbbox((0,0), phone_text, font = font_small)[2]

    name_x = (width - name_width) // 2
    name_y = 150

    glow_color = colors['accent']
    main_color = (255, 255, 255)

    offsets = [-2, 2, -3, 3]
    for offset in offsets:
        draw.text((name_x + offset, name_y), name_text, fill=glow_color, font=font_large)
        draw.text((name_x, name_y + offset), name_text, fill=glow_color, font=font_large)

    draw.text((name_x, name_y), name_text, fill=main_color, font=font_large)

    school_x = (width - school_width) // 2
    school_y = height - 120
    phone_x = (width - phone_width) // 2
    phone_y = height - 80

    draw.text((school_x, school_y), school_text, fill=colors['accent'], font=font_medium)
    draw.text((phone_x, phone_y), phone_text, fill=colors['secondary'], font=font_small)

def draw_galaxy_template(draw, width, height, colors, user_data, layout): #갤럭시 템플릿
    draw.rectangle([0, 0, width, height], fill=(5, 5, 15))
    nebula_color_1 = tuple(c // 4 for c in colors['accent'])
    nebula_color_2 = tuple(c // 4 for c in colors['secondary'])
    draw.ellipse([-width // 4, -height // 4, width // 2, height // 2], fill=nebula_color_1)
    draw.ellipse([width // 4, height // 2, width + width // 4, height + height // 2], fill=nebula_color_2)

    for i in range(100):
        x = random.randint(0, width)
        y = random.randint(0, height)
        brightness = random.randint(150, 255)
        draw.point((x, y), fill=(brightness, brightness, brightness))

    font_large = get_font(48, 'bold')
    font_medium = get_font(34, 'regular')
    font_small = get_font(30, 'regular')

    name_text = user_data['name']
    school_text = user_data['school']
    phone_text = user_data['phone']

    phone_width = draw.textbbox((0,0), phone_text, font = font_small)[2]

    name_x = 110
    name_y = 150
    school_x = 110
    school_y = 220

    draw.text((name_x, name_y), name_text, fill=(255, 255, 255), font=font_large)
    draw.text((school_x, school_y), school_text, fill=(200, 200, 255), font=font_medium)

    phone_x = width - phone_width - 110
    phone_y = height - 100

    draw.text((phone_x, phone_y), phone_text, fill=(255, 255, 200), font=font_small)

def draw_minimalist_template(draw, width, height, colors, user_data, layout): #미니멀 템플릿
    draw.rectangle([0, 0, width, height], fill=(255, 255, 255))

    draw.line([(100, 140), (width-300, 140)], fill=colors['primary'], width=2)
    draw.line([(300, height-100), (width-100, height-100)], fill=colors['primary'], width=2)

    font_large = get_font(42, 'bold')
    font_medium = get_font(28, 'regular')
    font_small = get_font(24, 'regular')

    name_text = user_data['name']
    school_text = user_data['school']
    phone_text = user_data['phone']

    name_x = 120
    name_y = 180
    school_x = 120
    school_y = 240

    draw.text((name_x, name_y), name_text, fill=(50, 50, 50), font=font_large)
    draw.text((school_x, school_y), school_text, fill=(100, 100, 100), font=font_medium)

    try:
        phone_width = draw.textbbox((0, 0), phone_text, font_small)[2]
    except AttributeError:
        phone_width = font_small.getlength(phone_text)

    phone_x = width - phone_width - 120
    phone_y = height - 100 - 40

    draw.text((phone_x, phone_y), phone_text, fill=(100, 100, 100), font=font_small)
    
def draw_grunge_template(draw, width, height, colors, user_data, layout): #그런지 템플릿
    base_color = tuple(max(0, c-30) for c in colors['primary'])
    draw.rectangle([0, 0, width, height], fill=base_color)

    accent_rgb = colors['accent']
    secondary_rgb = colors['secondary']

    for i in range(100):
        x, y = random.randint(0, width), random.randint(0, height)
        size = random.randint(1, 5)
        fill_color = random.choice([base_color] * 3 + [accent_rgb] * 5 + [secondary_rgb] * 2)
        draw.ellipse([x, y, x+size, y+size], fill=fill_color)

    for i in range(20):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill=colors['accent'], width=random.randint(1,3))

    font_large = get_font(44, 'bold', font_name='grunge')
    font_medium = get_font(30, 'regular', font_name='grunge')
    font_small = get_font(26, 'regular', font_name='grunge')
    text_color = colors['light']

    name_text = user_data['name']
    school_text = user_data['school']
    phone_text = user_data['phone']

    phone_width = draw.textbbox((0,0), phone_text, font = font_small)[2]

    name_x = 100
    name_y = 160
    school_x = 100
    school_y = 220

    draw.text((name_x, name_y), name_text, fill=text_color, font=font_large)
    draw.text((school_x, school_y), school_text, fill=text_color, font=font_medium)

    phone_x = width - phone_width - 100
    phone_y = height - 100

    draw.text((phone_x, phone_y), phone_text, fill=text_color, font=font_small)

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