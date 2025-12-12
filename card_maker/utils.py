from PIL import Image, ImageDraw, ImageFont
import random
import colorsys
import os
from django.conf import settings
import qrcode
import logging

logger = logging.getLogger(__name__)

TEMPLATES = [
    'modern', 'cute', 'retro', 'neon', 'galaxy', 'minimalist', 'grunge'
]

COLOR_THEMES = [
    'monochrome', 'gradient', 'complementary', 'pastel', 'vibrant'
]

def hex_to_rgb(hex_color):
    """HEX 색상을 RGB로 변환"""
    try:
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            raise ValueError("Invalid hex color format")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except (ValueError, AttributeError) as e:
        logger.error(f"색상 변환 오류: {hex_color}, {e}")
        return (52, 152, 219)  # 기본 파란색

def rgb_to_hsl(rgb):
    """RGB를 HSL로 변환"""
    r, g, b = [x/255.0 for x in rgb]
    return colorsys.rgb_to_hls(r, g, b)

def hsl_to_rgb(hsl):
    """HSL을 RGB로 변환"""
    h, l, s = hsl
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return tuple(int(x * 255) for x in (r, g, b))

def generate_color_palette(base_color_hex, theme):
    """기본 색상 바탕 팔레트 생성"""
    base_rgb = hex_to_rgb(base_color_hex)
    base_hsl = rgb_to_hsl(base_rgb)
    h, l, s = base_hsl

    # 테마별 보조 색상 생성
    theme_offsets = {
        'complementary': 0.5,
        'monochrome': 0.0,
        'gradient': 0.3,
        'pastel': 0.25,
        'vibrant': 0.4
    }
    h_offset = theme_offsets.get(theme, 0.3)
    h_secondary = (h + h_offset) % 1

    colors = {
        'primary': base_rgb,
        'secondary': hsl_to_rgb((h_secondary, l, s)),
        'accent': hsl_to_rgb((h, min(l + 0.2, 1), s)),
        'light': hsl_to_rgb((h, 0.95, 0.1)),
        'dark': hsl_to_rgb((h, 0.1, s)),
    }
    return colors

def get_font_path():
    """폰트 경로 반환"""
    font_dir = os.path.join(settings.BASE_DIR, 'static', 'fonts')
    return {
        'regular': os.path.join(font_dir, 'NanumGothic.ttf'),
        'bold': os.path.join(font_dir, 'NanumGothicBold.ttf'),
        'extrabold': os.path.join(font_dir, 'NanumGothicExtraBold.ttf'),
        'retro': os.path.join(font_dir, 'BoldDunggeunmo.ttf'),
        'cute': os.path.join(font_dir, 'Cutefont.ttf'),
        'grunge': os.path.join(font_dir, 'BlackHanSans-Regular.ttf'),
        'galaxy': os.path.join(font_dir, 'Hakgyoansim Byeolbichhaneul TTF B.ttf'),
        'neon': os.path.join(font_dir, 'EliceDigitalBaeum_Regular.ttf'),
    }

def get_font(size, weight='regular', font_name=None):
    """폰트 객체 반환 (에러 처리 강화)"""
    font_paths = get_font_path()
    
    # 우선순위: font_name > weight > regular > default
    candidates = []
    if font_name and font_name in font_paths:
        candidates.append(font_paths[font_name])
    if weight in font_paths:
        candidates.append(font_paths[weight])
    candidates.append(font_paths.get('regular'))
    
    for font_path in candidates:
        if font_path and os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception as e:
                logger.warning(f"폰트 로드 실패: {font_path}, {e}")
                continue
    
    logger.error(f"모든 폰트 로드 실패. 기본 폰트 사용: size={size}")
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
        'colors': {
            'name': (255, 255, 255),
            'school': 'light',
            'phone': 'light',
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

def get_text_width(draw, text, font):
    """텍스트 너비 계산 (호환성 개선)"""
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0]
    except AttributeError:
        try:
            return int(font.getlength(text))
        except:
            return len(text) * font.size // 2

def calculate_text_position(text_width, base_x, align):
    """텍스트 정렬에 따른 X 좌표 계산"""
    if align == 'center':
        return base_x - (text_width // 2)
    elif align == 'right':
        return base_x - text_width
    return base_x

def draw_neon_text(draw, x, y, text, font, glow_color, main_color):
    """네온 효과 텍스트 그리기"""
    offsets = [-2, 2, -3, 3]
    for offset in offsets:
        draw.text((x + offset, y), text, fill=glow_color, font=font)
        draw.text((x, y + offset), text, fill=glow_color, font=font)

    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        draw.text((x + dx, y + dy), text, fill=main_color, font=font)

    draw.text((x, y), text, fill=main_color, font=font)

def draw_common_text_layout(draw, width, height, template, colors, user_data):
    """공통 텍스트 레이아웃 그리기 (중복 제거)"""
    config = TEMPLATE_CONFIG.get(template)
    if not config:
        logger.error(f"알 수 없는 템플릿: {template}")
        return
    
    # 폰트 로드
    fonts = {
        size: get_font(**config['fonts'][size])
        for size in ['large', 'medium', 'small']
    }

    # 텍스트 데이터 매핑
    text_mapping = {
        'name': {'text': user_data['name'], 'font': fonts['large']},
        'school': {'text': user_data['school'], 'font': fonts['medium']},
        'phone': {'text': user_data['phone'], 'font': fonts['small']},
    }

    # 각 텍스트 그리기
    for key, data in text_mapping.items():
        text = data['text']
        font = data['font']
        layout = config['layout'][key]
        
        # 색상 결정
        color_key = config['colors'][key]
        color = colors[color_key] if isinstance(color_key, str) else color_key
        
        # 위치 계산
        text_width = get_text_width(draw, text, font)
        base_x = layout['x'](width, height)
        x = calculate_text_position(text_width, base_x, layout['align'])
        y = layout['y'](width, height)

        # 템플릿별 특수 효과
        if template == 'neon':
            main_color = (255, 255, 255) if key == 'name' else color
            draw_neon_text(draw, x, y, text, font, colors['accent'], main_color)
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
    draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=fill)

def draw_cute_background(draw, width, height, colors):
    pastel_bg = random.choice([colors['light'], tuple(min(255, c + 50) for c in colors['primary'])])
    draw.rectangle([0, 0, width, height], fill=pastel_bg)
    
    pattern_color_1 = colors['accent']
    pattern_color_2 = colors['secondary']
    
    for _ in range(25):
        x = random.randint(30, width - 30)
        y = random.randint(30, height - 30)
        size = random.randint(10, 25)
        
        if random.random() < 0.6:
            fill_color = random.choice([pattern_color_1, pattern_color_2, (255, 255, 255)])
            draw_polka_dot(draw, x, y, size, fill_color)
        else:
            fill_color = random.choice([pattern_color_1, (255, 255, 255)])
            draw_cute_sparkle(draw, x, y, size, fill_color)

    draw.rounded_rectangle([40, 40, width - 40, height - 40], radius=20, outline=colors['primary'], width=4)

def draw_retro_background(draw, width, height, colors):
    retro_bg = (245, 222, 179)
    draw.rectangle([0, 0, width, height], fill=retro_bg)
    
    grid_color = tuple(max(0, c - 15) for c in retro_bg)
    for i in range(0, width, 60):
        draw.line([(i, 0), (i, height)], fill=grid_color, width=1)
    for i in range(0, height, 60):
        draw.line([(0, i), (width, i)], fill=grid_color, width=1)
    
    draw.polygon([(width - 200, height), (width, height - 200), (width, height)], fill=colors['primary'])
    draw.polygon([(width - 150, height), (width, height - 150), (width, height)], fill=colors['accent'])
    
    for i in range(5):
        draw.rectangle([10 + i * 2, 10 + i * 2, width - 10 - i * 2, height - 10 - i * 2], 
                      outline=colors['primary'], width=2)

def draw_galaxy_background(draw, width, height, colors):
    draw.rectangle([0, 0, width, height], fill=(10, 10, 30))
    
    for _ in range(150):
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
    draw.line([(line_start_x, line_y), (line_start_x + line_width, line_y)], 
             fill=colors['secondary'], width=2)

def draw_neon_background(draw, width, height, colors):
    draw.rectangle([0, 0, width, height], fill=(20, 20, 20))

    neon_color = colors['primary']
    for thickness in range(8, 0, -1):
        draw.rectangle([60 - thickness, 60 - thickness, width - 60 + thickness, height - 60 + thickness], 
                      outline=neon_color, width=thickness)

def draw_grunge_background(draw, width, height, colors):
    base_color = tuple(max(0, c - 30) for c in colors['primary'])
    draw.rectangle([0, 0, width, height], fill=base_color)
    
    accent_rgb = colors['accent']
    secondary_rgb = colors['secondary']
    
    for _ in range(100):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(1, 5)
        fill_color = random.choice([base_color] * 3 + [accent_rgb] * 5 + [secondary_rgb] * 2)
        draw.ellipse([x, y, x + size, y + size], fill=fill_color)
    
    for _ in range(20):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill=colors['accent'], width=random.randint(1, 3))

BACKGROUND_DRAWERS = {
    'modern': draw_modern_background,
    'cute': draw_cute_background,
    'retro': draw_retro_background,
    'galaxy': draw_galaxy_background,
    'minimalist': draw_minimalist_background,
    'neon': draw_neon_background,
    'grunge': draw_grunge_background,
}

def create_business_card(user_data):
    """명함 생성 (에러 처리 강화)"""
    try:
        # 템플릿 선택
        template = random.choice(TEMPLATES)
        
        # 테마 선택 (템플릿별 제약 적용)
        available_themes = COLOR_THEMES.copy()
        if template == 'neon' and 'pastel' in available_themes:
            available_themes.remove('pastel')
        elif template == 'minimalist' and 'complementary' in available_themes:
            available_themes.remove('complementary')
        
        theme = random.choice(available_themes)
        
        # 색상 팔레트 생성
        colors = generate_color_palette(user_data.get('favorite_color', '#3498db'), theme)
        
        # 이미지 생성
        width, height = 800, 500
        img = Image.new('RGB', (width, height), colors['light'])
        draw = ImageDraw.Draw(img)

        # 배경 그리기
        background_drawer = BACKGROUND_DRAWERS.get(template)
        if background_drawer:
            background_drawer(draw, width, height, colors)
        else:
            logger.warning(f"배경 그리기 함수 없음: {template}")

        # 텍스트 그리기
        draw_common_text_layout(draw, width, height, template, colors, user_data)

        return img, template
    
    except Exception as e:
        logger.error(f"명함 생성 오류: {e}", exc_info=True)
        raise

def generate_qr_code(download_url):
    """QR 코드 생성 (에러 처리 추가)"""
    try:
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
    except Exception as e:
        logger.error(f"QR 코드 생성 오류: {e}", exc_info=True)
        raise