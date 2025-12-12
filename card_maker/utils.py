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
        'galaxy' : os.path.join(font_dir, 'Hakgyoansim Byeolbichhaneul TTF B.ttf'),
        'neon' : os.path.join(font_dir, 'EliceDigitalBaeum_Regular.ttf'),
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
    
TEMPLATE_CONFIG = {
    'modern': {
        'fonts': {
            'large': {'size': 48, 'weight': 'bold'},
            'medium': {'size': 32, 'weight': 'regular'},
            'small': {'size': 24, 'weight': 'regular'},
        },
        'colors': {
            'name': 'dark', 'school': 'dark', 'phone': 'dark'
        },
        'layout': {
            'name':   {'align': 'left', 'x': lambda w, h: 100, 'y': lambda w, h: 100},
            'school': {'align': 'left', 'x': lambda w, h: 100, 'y': lambda w, h: 170},
            'phone':  {'align': 'right', 'x': lambda w, h: w - 100, 'y': lambda w, h: h - 100}
        }
    },
    'cute': {
        'fonts': {
            'large': {'size': 42, 'weight': 'bold', 'font_name': 'cute'},
            'medium': {'size': 28, 'weight': 'regular', 'font_name': 'cute'},
            'small': {'size': 22, 'weight': 'regular', 'font_name': 'cute'},
        },
        'colors': {
            'name': 'dark', 'school': 'dark', 'phone': 'dark'
        },
        'layout': {
            'name':   {'align': 'center', 'x': lambda w, h: w // 2, 'y': lambda w, h: 180},
            'school': {'align': 'center', 'x': lambda w, h: w // 2, 'y': lambda w, h: 240},
            'phone':  {'align': 'center', 'x': lambda w, h: w // 2, 'y': lambda w, h: h - 100}
        }
    },
    'retro': {
        'fonts': {
            'large': {'size': 44, 'weight': 'bold', 'font_name': 'retro'},
            'medium': {'size': 30, 'weight': 'regular', 'font_name': 'retro'},
            'small': {'size': 26, 'weight': 'regular', 'font_name': 'retro'},
        },
        'colors': {
            'name': 'dark', 'school': 'dark', 'phone': 'dark'
        },
        'layout': {
            'name':   {'align': 'left', 'x': lambda w, h: 120, 'y': lambda w, h: 160},
            'school': {'align': 'left', 'x': lambda w, h: 120, 'y': lambda w, h: 220},
            'phone':  {'align': 'right', 'x': lambda w, h: w - 120, 'y': lambda w, h: h - 80}
        }
    },
    'galaxy': {
        'fonts': {
            'large': {'size': 48, 'weight': 'bold', 'font_name': 'galaxy'},
            'medium': {'size': 34, 'weight': 'regular', 'font_name': 'galaxy'},
            'small': {'size': 30, 'weight': 'regular', 'font_name': 'galaxy'},
        },
        'colors': {
            'name': (255, 255, 255),
            'school': (200, 200, 255),
            'phone': (255, 255, 200),
        },
        'layout': {
            'name':   {'align': 'left', 'x': lambda w, h: 110, 'y': lambda w, h: 150},
            'school': {'align': 'left', 'x': lambda w, h: 110, 'y': lambda w, h: 220},
            'phone':  {'align': 'right', 'x': lambda w, h: w - 110, 'y': lambda w, h: h - 100}
        }
    },
    'minimalist': {
        'fonts': {
            'large': {'size': 42, 'weight': 'bold'},
            'medium': {'size': 28, 'weight': 'regular'},
            'small': {'size': 24, 'weight': 'regular'},
        },
        'colors': {
            'name': (50, 50, 50),
            'school': (100, 100, 100),
            'phone': (100, 100, 100),
        },
        'layout': {
            'name':   {'align': 'center', 'x': lambda w, h: w // 2, 'y': lambda w, h: 150},
            'school': {'align': 'center', 'x': lambda w, h: w // 2, 'y': lambda w, h: 210},
            'phone':  {'align': 'center', 'x': lambda w, h: w // 2, 'y': lambda w, h: h - 100}
        }
    },
    'neon': {
        'fonts': {
            'large': {'size': 46, 'weight': 'regular', 'font_name': 'neon'},
            'medium': {'size': 32, 'weight': 'regular', 'font_name': 'neon'},
            'small': {'size': 28, 'weight': 'regular', 'font_name': 'neon'},
        },
        'colors' : {
            'name': (255, 255, 255),
            'school' : 'light',
            'phone' : 'light',
        },
        'layout': {
            'name':   {'align': 'center', 'x': lambda w, h: w // 2, 'y': lambda w, h: 150},
            'school': {'align': 'center', 'x': lambda w, h: w // 2, 'y': lambda w, h: h - 150},
            'phone':  {'align': 'center', 'x': lambda w, h: w // 2, 'y': lambda w, h: h - 110}
        },
    },
    'grunge': {
        'fonts': {
            'large': {'size': 40, 'weight': 'bold', 'font_name': 'grunge'},
            'medium': {'size': 26, 'weight': 'regular', 'font_name': 'grunge'},
            'small': {'size': 20, 'weight': 'regular', 'font_name': 'grunge'},
        },
        'colors': {
            'name': 'accent',
            'school': 'light',
            'phone': 'secondary'
        },
        'layout': {
            'name': {'align': 'left', 'x': lambda w, h: 80, 'y': lambda w, h: 100},
            'school': {'align': 'left', 'x': lambda w, h: 80, 'y': lambda w, h: 160},
            'phone': {'align': 'left', 'x': lambda w, h: 80, 'y': lambda w, h: h - 100}
        }
    },
}

def draw_common_text_layout(draw, width, height, template, colors, user_data):
    config = TEMPLATE_CONFIG[template]
    
    fonts = {
        'large': get_font(**config['fonts']['large']),
        'medium': get_font(**config['fonts']['medium']),
        'small': get_font(**config['fonts']['small']),
    }

    text_data = {
        'name': {'text': user_data['name'], 'font': fonts['large']},
        'school': {'text': user_data['school'], 'font': fonts['medium']},
        'phone': {'text': user_data['phone'], 'font': fonts['small']},
    }

    for key in ['name', 'school', 'phone']:
        text = text_data[key]['text']
        font = text_data[key]['font']
        layout = config['layout'][key]
        
        color_key = config['colors'][key]
        color = colors[color_key] if isinstance(color_key, str) else color_key
        
        try:
            text_width = draw.textbbox((0, 0), text, font=font)[2]
        except AttributeError:
            text_width = font.getlength(text)
        
        base_x = layout['x'](width, height)
        if layout['align'] == 'center':
            x = base_x - (text_width // 2)
        elif layout['align'] == 'right':
            x = base_x - text_width
        else:
            x = base_x
        
        y = layout['y'](width, height)

        if template == 'neon':
            glow_color = colors['accent']
            main_color = (255, 255, 255) if key == 'name' else color

            offsets = [-2, 2, -3, 3]
            for offset in offsets:
                draw.text((x+offset, y), text, fill=glow_color, font=font)
                draw.text((x, y+offset), text, fill=glow_color, font=font)

            draw.text((x-1, y), text, fill=main_color, font=font)
            draw.text((x+1, y), text, fill=main_color, font=font)
            draw.text((x, y-1), text, fill=main_color, font=font)
            draw.text((x, y+1), text, fill=main_color, font=font)

            draw.text((x, y), text, fill=main_color, font=font)
        
        else:
            draw.text((x, y), text, fill=color, font=font)

def draw_modern_background(draw, width, height, colors):
    draw.rectangle([0, 0, width, height], fill=colors['light'])
    draw.polygon([(width - 200, 0), (width, 0), (width, 200)], fill=colors['primary'])
    draw.line([(0, height - 100), (width, height)], fill=colors['accent'], width=5)

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

def draw_cute_background(draw, width, height, colors):
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

def draw_retro_background(draw, width, height, colors):
    retro_bg = (245, 222, 179)
    draw.rectangle([0, 0, width, height], fill=retro_bg)
    grid_color = tuple(c - 15 for c in retro_bg)
    for i in range(0, width, 60):
        draw.line([(i, 0), (i, height)], fill=grid_color, width=1)
    for i in range(0, height, 60):
        draw.line([(0, i), (width, i)], fill=grid_color, width=1)
    draw.polygon([(width - 200, height), (width, height - 200), (width, height)], fill=colors['primary'])
    draw.polygon([(width - 150, height), (width, height - 150), (width, height)], fill=colors['accent'])
    for i in range(5):
        draw.rectangle([10+i*2, 10+i*2, width-10-i*2, height-10-i*2], outline=colors['primary'], width=2)

def draw_galaxy_background(draw, width, height, colors):
    draw.rectangle([0, 0, width, height], fill=(10, 10, 30))
    
    for i in range(150):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.choice([1] * 80 + [2] * 15 + [3] * 5) 
        brightness = random.randint(100, 255)
        if size == 1:
            draw.point((x, y), fill=(brightness, brightness, brightness))
        else:
            draw.ellipse([x, y, x + size, y + size], fill=(brightness, brightness, brightness))

def draw_minimalist_background(draw, width, height, colors):
    draw.rectangle([0, 0, width, height], fill=(255, 255, 255))
    border_color = (220, 220, 220)
    draw.rectangle([0, 0, width, 10], fill=border_color)
    draw.rectangle([0, height - 10, width, height], fill=border_color)

    line_y = height * 2 // 3
    line_width = width // 5
    line_start_x = (width - line_width) // 2
    draw.line([(line_start_x, line_y), (line_start_x + line_width, line_y)], fill=colors['secondary'], width=2)

def draw_neon_background(draw, width, height, colors):
    draw.rectangle([0, 0, width, height], fill=(20, 20, 20))

    neon_color = colors['primary']
    for thickness in range(8, 0, -1):
        draw.rectangle([60-thickness, 60-thickness, width-60+thickness, height-60+thickness], outline=neon_color, width=thickness)

def draw_grunge_background(draw, width, height, colors):
    base_color = tuple(max(0, c-30) for c in colors['primary'])
    draw.rectangle([0, 0, width, height], fill=base_color)
    accent_rgb = colors['accent']
    secondary_rgb = colors['secondary']
    for i in range(100):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(1, 5)
        fill_color = random.choice([base_color] * 3 + [accent_rgb] * 5 + [secondary_rgb] * 2)
        draw.ellipse([x, y, x+size, y+size], fill=fill_color)
    for i in range(20):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill=colors['accent'], width=random.randint(1,3))

BACKGROUND_DRAWERS = {
    'modern': draw_modern_background,
    'cute': draw_cute_background,
    'retro': draw_retro_background,
    'galaxy': draw_galaxy_background,
    'minimalist': draw_minimalist_background,
    'neon' : draw_neon_background,
    'grunge' : draw_grunge_background,
}

def create_business_card(user_data):
    template = random.choice(TEMPLATES)
    available_themes = COLOR_THEMES.copy()
    if template == 'neon':
        if 'pastel' in available_themes:
            available_themes.remove('pastel')
    elif template == 'minimalist':
        if 'complementary' in available_themes:
            available_themes.remove('complementary')

    theme = random.choice(available_themes)
    colors = generate_color_palette(user_data['favorite_color'], theme)
    width, height = 800, 500
    img = Image.new('RGB', (width, height), colors['light'])
    draw = ImageDraw.Draw(img)

    if template == 'neon':
        draw_neon_background(draw, width, height, colors)
    elif template == 'grunge':
        draw_grunge_background(draw, width, height, colors)
    else:
        if template in BACKGROUND_DRAWERS:
            BACKGROUND_DRAWERS[template](draw, width, height, colors)

    draw_common_text_layout(draw, width, height, template, colors, user_data)

    return img, template


def generate_qr_code(download_url):
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