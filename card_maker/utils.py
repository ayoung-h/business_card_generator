from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import colorsys
import os
from django.conf import settings
import qrcode
import math

# ========== 사용자 선택 가능한 스타일 ==========
USER_STYLES = [
    'space',       # 우주 → galaxy 템플릿
    'cute',        # 귀여운 → cute 템플릿
    'neon',        # 네온 → neon 템플릿
    'retro',       # 레트로 → retro 템플릿
    'vintage',     # 빈티지 → grunge 템플릿
    'nature',      # 자연 → 베이스 + 테마
    'engineering', # 공학 → 베이스 + 테마
    'art',         # 미술 → 베이스 + 테마
    'sports',      # 스포츠 → 베이스 + 테마
    'music',       # 음악 → 베이스 + 테마
    'education',   # 교육 → 베이스 + 테마
    'business',    # 비즈니스 → 베이스 + 테마
    'medical'      # 의료 → 베이스 + 테마
]

# 스타일 → 템플릿/테마 매핑
STYLE_MAPPING = {
    # 개성 템플릿 (고정 스타일)
    'space': {'type': 'stylized', 'template': 'galaxy'},
    'cute': {'type': 'stylized', 'template': 'cute'},
    'neon': {'type': 'stylized', 'template': 'neon'},
    'retro': {'type': 'stylized', 'template': 'retro'},
    'vintage': {'type': 'stylized', 'template': 'grunge'},
    
    # 베이스 템플릿 + 테마
    'nature': {'type': 'themed', 'theme': 'nature'},
    'engineering': {'type': 'themed', 'theme': 'engineering'},
    'art': {'type': 'themed', 'theme': 'art'},
    'sports': {'type': 'themed', 'theme': 'sports'},
    'music': {'type': 'themed', 'theme': 'music'},
    'education': {'type': 'themed', 'theme': 'education'},
    'business': {'type': 'themed', 'theme': 'business'},
    'medical': {'type': 'themed', 'theme': 'medical'}
}

# 베이스 템플릿 목록
BASE_TEMPLATES = ['modern', 'minimalist']

# 테마별 색상 팔레트
THEME_COLORS = {
    'nature': '#4A7C59',      # 초록
    'engineering': '#2C3E50',  # 진한 회색
    'medical': '#E74C3C',      # 빨강
    'art': '#9B59B6',          # 보라
    'business': '#34495E',     # 네이비
    'education': '#F39C12',    # 주황
    'sports': '#16A085',       # 청록
    'music': '#8E44AD'         # 자주
}

# ========== 유틸리티 함수 ==========

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hsl(rgb):
    r, g, b = [x/255.0 for x in rgb]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return (h, l, s)

def hsl_to_rgb(hsl):
    h, l, s = hsl
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return tuple(int(x * 255) for x in (r, g, b))

def generate_color_palette(base_color_hex, theme='complementary'):
    base_rgb = hex_to_rgb(base_color_hex)
    base_hsl = rgb_to_hsl(base_rgb)
    h, l, s = base_hsl
    
    if theme == 'complementary':
        h_secondary = (h + 0.5) % 1
    elif theme == 'monochrome':
        h_secondary = h
    else:
        h_secondary = (h + 0.3) % 1
    
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
        'retro': os.path.join(font_dir, 'BoldDunggeunmo.ttf'),
        'cute': os.path.join(font_dir, 'Cutefont.ttf'),
        'grunge': os.path.join(font_dir, 'BlackHanSans-Regular.ttf'),
    }

def get_font(size, weight='regular', font_name=None):
    font_paths = get_font_path()
    font_to_use = None

    if font_name and font_name in font_paths:
        font_to_use = font_paths[font_name]
    elif weight == 'bold' and os.path.exists(font_paths.get('bold', '')):
        font_to_use = font_paths['bold']
    elif weight == 'extrabold' and os.path.exists(font_paths.get('extrabold', '')):
        font_to_use = font_paths['extrabold']
    elif os.path.exists(font_paths.get('regular', '')):
        font_to_use = font_paths['regular']

    try:
        if font_to_use and os.path.exists(font_to_use):
            return ImageFont.truetype(font_to_use, size)
        else:
            return ImageFont.load_default()
    except Exception as e:
        print(f"폰트 로드 오류: {e}")
        return ImageFont.load_default()

# ========== 테마 관련 함수 ==========

def get_theme_images(theme):
    """테마에 맞는 이미지 파일 경로 반환"""
    image_dir = os.path.join(settings.BASE_DIR, 'static', 'theme_images', theme)
    
    theme_image_files = {
        'nature': ['leaf.png', 'flower.png', 'mountain.png', 'tree.png'],
        'engineering': ['gear.png', 'circuit.png', 'blueprint.png', 'tool.png'],
        'medical': ['stethoscope.png', 'cross.png', 'heart.png', 'pill.png'],
        'art': ['brush.png', 'palette.png', 'canvas.png', 'pencil.png'],
        'business': ['document.png', 'chart.png', 'briefcase.png', 'handshake.png'],
        'education': ['book.png', 'pencil.png', 'graduate.png', 'apple.png'],
        'sports': ['ball.png', 'dumbbell.png', 'trophy.png', 'shoe.png'],
        'music': ['guitar.png', 'note.png', 'mic.png', 'headphone.png']
    }
    
    files = theme_image_files.get(theme, [])
    return [os.path.join(image_dir, f) for f in files]

def create_themed_background(width, height, theme, colors):
    """테마에 맞는 배경 패턴 생성"""
    img = Image.new('RGB', (width, height), colors['light'])
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    if theme == 'nature':
        # 자연스러운 물결 패턴
        for i in range(5):
            y_offset = i * 100
            points = []
            for x in range(0, width + 50, 50):
                y = y_offset + math.sin(x / 100) * 30
                points.append((x, y))
            if len(points) > 1:
                overlay_draw.line(points, fill=colors['accent'] + (30,), width=2)
        
        # 원형 패턴
        for i in range(15):
            x = random.randint(-50, width + 50)
            y = random.randint(-50, height + 50)
            size = random.randint(30, 80)
            overlay_draw.ellipse([x, y, x + size, y + size], fill=colors['secondary'] + (20,))
    
    elif theme == 'engineering':
        # 격자 패턴
        grid_color = colors['primary'] + (15,)
        for i in range(0, width, 40):
            overlay_draw.line([(i, 0), (i, height)], fill=grid_color, width=1)
        for i in range(0, height, 40):
            overlay_draw.line([(0, i), (width, i)], fill=grid_color, width=1)
        
        # 기하학적 도형
        for i in range(8):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(40, 100)
            overlay_draw.rectangle([x, y, x + size, y + size], 
                                  outline=colors['accent'] + (40,), width=2)
    
    elif theme == 'medical':
        # 십자가 패턴
        cross_color = colors['primary'] + (20,)
        for i in range(10):
            x = random.randint(50, width - 50)
            y = random.randint(50, height - 50)
            size = random.randint(20, 40)
            overlay_draw.rectangle([x - 5, y - size, x + 5, y + size], fill=cross_color)
            overlay_draw.rectangle([x - size, y - 5, x + size, y + 5], fill=cross_color)
    
    elif theme == 'art':
        # 붓 터치 효과
        for i in range(20):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = x1 + random.randint(-100, 100)
            y2 = y1 + random.randint(-100, 100)
            color = random.choice([colors['primary'], colors['accent'], colors['secondary']])
            overlay_draw.line([(x1, y1), (x2, y2)], 
                            fill=color + (30,), width=random.randint(3, 10))
    
    elif theme == 'business':
        # 대각선 스트라이프
        stripe_color = colors['primary'] + (15,)
        for i in range(-height, width + height, 80):
            overlay_draw.polygon([
                (i, 0), (i + 40, 0), (i + 40 - height, height), (i - height, height)
            ], fill=stripe_color)
    
    elif theme == 'education':
        # 점선 노트 패턴
        line_color = colors['primary'] + (25,)
        for i in range(60, height, 40):
            for x in range(0, width, 20):
                overlay_draw.rectangle([x, i, x + 10, i + 1], fill=line_color)
    
    elif theme == 'sports':
        # 다이나믹한 대각선
        for i in range(8):
            x1 = random.randint(-200, 0)
            y1 = random.randint(0, height)
            x2 = x1 + random.randint(200, 400)
            y2 = y1 - random.randint(100, 200)
            overlay_draw.line([(x1, y1), (x2, y2)], 
                            fill=colors['primary'] + (20,), width=random.randint(5, 15))
    
    elif theme == 'music':
        # 오선지 패턴
        staff_color = colors['primary'] + (25,)
        for i in range(5):
            y = 100 + i * 30
            overlay_draw.line([(0, y), (width // 2, y)], fill=staff_color, width=2)
        
        # 음표 모양 원들
        for i in range(10):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(15, 30)
            overlay_draw.ellipse([x, y, x + size, y + size], fill=colors['secondary'] + (30,))
    
    img = img.convert('RGBA')
    img = Image.alpha_composite(img, overlay)
    img = img.filter(ImageFilter.GaussianBlur(radius=8))
    
    return img.convert('RGB')

def add_theme_images_to_card(card_img, theme, template, colors):
    """테마에 맞는 PNG 이미지를 명함에 배치"""
    theme_images = get_theme_images(theme)
    
    if not theme_images:
        return card_img
    
    available_images = [img for img in theme_images if os.path.exists(img)]
    
    if not available_images:
        return card_img
    
    num_images = random.randint(1, min(2, len(available_images)))
    selected_images = random.sample(available_images, num_images)
    
    card_img = card_img.convert('RGBA')
    
    for idx, img_path in enumerate(selected_images):
        try:
            theme_img = Image.open(img_path).convert('RGBA')
            
            if template == 'modern':
                positions = [
                    (50, 50, 100, 100),
                    (50, card_img.height - 150, 100, 100)
                ]
            else:  # minimalist
                positions = [
                    (card_img.width - 150, 50, 80, 80),
                    (50, card_img.height - 130, 80, 80)
                ]
            
            if idx < len(positions):
                x, y, w, h = positions[idx]
                theme_img = theme_img.resize((w, h), Image.Resampling.LANCZOS)
                
                alpha = theme_img.split()[3]
                alpha = alpha.point(lambda p: int(p * 0.4))
                theme_img.putalpha(alpha)
                
                card_img.paste(theme_img, (x, y), theme_img)
        
        except Exception as e:
            print(f"테마 이미지 추가 실패: {e}")
            continue
    
    return card_img

# ========== 개성 템플릿 배경 생성 ==========

def create_galaxy_background(width, height, colors):
    """갤럭시 배경"""
    img = Image.new('RGB', (width, height), (5, 5, 15))
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    nebula_spots = [(random.randint(-200, width), random.randint(-200, height), 
                     random.randint(300, 600)) for _ in range(4)]
    
    nebula_colors = [
        tuple(c // 3 for c in colors['accent']) + (60,),
        tuple(c // 3 for c in colors['secondary']) + (60,),
        tuple(c // 4 for c in colors['primary']) + (40,)
    ]
    
    for (x, y, size), color in zip(nebula_spots, nebula_colors * 2):
        for i in range(5, 0, -1):
            current_size = size * (i / 5)
            alpha = int(60 * (i / 5))
            current_color = color[:3] + (alpha,)
            overlay_draw.ellipse([
                x - current_size // 2, y - current_size // 2,
                x + current_size // 2, y + current_size // 2
            ], fill=current_color)
    
    img = img.convert('RGBA')
    img = Image.alpha_composite(img, overlay)
    img = img.filter(ImageFilter.GaussianBlur(radius=30))
    
    return img.convert('RGB')

def create_cute_background(width, height, colors):
    """큐트 배경"""
    pastel_bg = tuple(min(255, c + 80) for c in colors['primary'])
    img = Image.new('RGB', (width, height), pastel_bg)
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    pastel_colors = [
        colors['accent'] + (30,),
        colors['secondary'] + (30,),
        tuple(min(255, c + 100) for c in colors['primary']) + (40,)
    ]
    
    circles = [
        (-100, -100, 400, 400),
        (width - 400, height - 400, width + 100, height + 100),
        (width // 2 - 200, -150, width // 2 + 200, 250),
    ]
    
    for i, circle in enumerate(circles):
        color = pastel_colors[i % len(pastel_colors)]
        overlay_draw.ellipse(circle, fill=color)
    
    for i in range(50):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(3, 8)
        color = random.choice(pastel_colors)
        overlay_draw.ellipse([x, y, x + size, y + size], fill=color)
    
    img = img.convert('RGBA')
    img = Image.alpha_composite(img, overlay)
    img = img.filter(ImageFilter.GaussianBlur(radius=20))
    
    return img.convert('RGB')

def create_neon_background(width, height, colors):
    """네온 배경"""
    img = Image.new('RGB', (width, height), (10, 10, 20))
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    neon_colors = [
        colors['primary'] + (100,),
        colors['accent'] + (100,),
        colors['secondary'] + (80,)
    ]
    
    for i in range(5):
        y = random.randint(0, height)
        color = random.choice(neon_colors)
        for thickness in range(8, 0, -1):
            alpha = int(100 * (thickness / 8))
            line_color = color[:3] + (alpha,)
            overlay_draw.line([(0, y), (width, y)], fill=line_color, width=thickness)
    
    img = img.convert('RGBA')
    img = Image.alpha_composite(img, overlay)
    img = img.filter(ImageFilter.GaussianBlur(radius=15))
    
    return img.convert('RGB')

def create_retro_background(width, height, colors):
    """레트로 배경"""
    retro_bg = (245, 222, 179)
    img = Image.new('RGB', (width, height), retro_bg)
    draw = ImageDraw.Draw(img)
    
    for i in range(height):
        ratio = i / height
        darkness = int(15 * ratio)
        color = tuple(max(0, c - darkness) for c in retro_bg)
        draw.line([(0, i), (width, i)], fill=color)
    
    grid_color = tuple(c - 20 for c in retro_bg)
    for i in range(0, width, 60):
        draw.line([(i, 0), (i, height)], fill=grid_color, width=1)
    for i in range(0, height, 60):
        draw.line([(0, i), (width, i)], fill=grid_color, width=1)
    
    return img

def create_grunge_background(width, height, colors):
    """그런지 배경"""
    base_color = tuple(max(0, c - 40) for c in colors['primary'])
    img = Image.new('RGB', (width, height), base_color)
    
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    for i in range(20):
        x1 = random.randint(-100, width)
        y1 = random.randint(-100, height)
        x2 = x1 + random.randint(-300, 300)
        y2 = y1 + random.randint(-300, 300)
        
        color_choice = random.choice([colors['accent'], colors['secondary'], base_color])
        stroke_color = tuple(max(0, min(255, c + random.randint(-30, 30))) 
                           for c in color_choice) + (random.randint(20, 60),)
        
        overlay_draw.line([(x1, y1), (x2, y2)], fill=stroke_color, 
                         width=random.randint(50, 150))
    
    img = img.convert('RGBA')
    img = Image.alpha_composite(img, overlay)
    img = img.filter(ImageFilter.GaussianBlur(radius=2))
    
    return img.convert('RGB')

# ========== 메인 명함 생성 함수 ==========

def create_business_card(user_data, style=None):
    """
    명함 이미지 생성
    
    Args:
        user_data: 사용자 정보 (name, school, phone, favorite_color)
        style: 사용자가 선택한 스타일 (None이면 랜덤)
    
    Returns:
        (명함 이미지, 스타일 이름)
    """
    # 스타일 선택
    if style is None or style not in USER_STYLES:
        style = random.choice(USER_STYLES)
    
    style_config = STYLE_MAPPING[style]
    width, height = 800, 500
    
    # 개성 템플릿
    if style_config['type'] == 'stylized':
        template = style_config['template']
        base_color = user_data.get('favorite_color', '#3498db')
        colors = generate_color_palette(base_color, 'complementary')
        
        # 배경 생성
        if template == 'galaxy':
            img = create_galaxy_background(width, height, colors)
        elif template == 'cute':
            img = create_cute_background(width, height, colors)
        elif template == 'neon':
            img = create_neon_background(width, height, colors)
        elif template == 'retro':
            img = create_retro_background(width, height, colors)
        elif template == 'grunge':
            img = create_grunge_background(width, height, colors)
        else:
            img = Image.new('RGB', (width, height), colors['light'])
        
        draw = ImageDraw.Draw(img)
        
        # 템플릿별 컨텐츠 그리기
        if template == 'galaxy':
            draw_galaxy_template(draw, width, height, colors, user_data, 'left_align')
        elif template == 'cute':
            draw_cute_template(draw, width, height, colors, user_data, 'center')
        elif template == 'neon':
            draw_neon_template(draw, width, height, colors, user_data, 'center')
        elif template == 'retro':
            draw_retro_template(draw, width, height, colors, user_data, 'center')
        elif template == 'grunge':
            draw_grunge_template(draw, width, height, colors, user_data, 'center')
    
    # 베이스 템플릿 + 테마
    else:
        theme = style_config['theme']
        template = random.choice(BASE_TEMPLATES)
        
        base_color = THEME_COLORS.get(theme, user_data.get('favorite_color', '#3498db'))
        colors = generate_color_palette(base_color, 'complementary')
        
        # 테마 배경 생성
        img = create_themed_background(width, height, theme, colors)
        draw = ImageDraw.Draw(img)
        
        # 베이스 템플릿 그리기
        if template == 'modern':
            draw_modern_template(draw, width, height, colors, user_data, 'left_align')
        else:
            draw_minimalist_template(draw, width, height, colors, user_data, 'left_align')
        
        # 테마 이미지 추가
        img = add_theme_images_to_card(img, theme, template, colors)
        img = img.convert('RGB')
    
    return img, style

# ========== 템플릿 그리기 함수들 (기존 코드 유지) ==========

def draw_modern_template(draw, width, height, colors, user_data, layout):
    # 배경 제거 (이미 배경 생성됨)
    draw.rectangle([0, 0, width // 4, height], fill=colors['primary'])
    draw.line([(width // 4, 0), (width // 4, height)], fill=colors['accent'], width=3)

    font_large = get_font(48, 'bold')
    font_medium = get_font(32, 'regular')
    font_small = get_font(24, 'regular')
    text_color = colors['dark']

    name_text = user_data['name']
    school_text = user_data['school']
    phone_text = user_data['phone']

    name_width = draw.textbbox((0,0), name_text, font=font_large)[2]
    school_width = draw.textbbox((0,0), school_text, font=font_medium)[2]
    phone_width = draw.textbbox((0,0), phone_text, font=font_small)[2]

    name_x = (width - name_width) // 2
    name_y = 180
    school_x = (width - school_width) // 2
    school_y = 240

    draw.text((name_x, name_y), name_text, fill=text_color, font=font_large)
    draw.text((school_x, school_y), school_text, fill=text_color, font=font_medium)

    phone_x = (width - phone_width) // 2
    phone_y = height - 100

    draw.text((phone_x, phone_y), phone_text, fill=text_color, font=font_small)

def draw_retro_template(draw, width, height, colors, user_data, layout):
    # 배경 레트로 장식
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

    phone_width = draw.textbbox((0,0), phone_text, font=font_small)[2]

    name_x = 120
    name_y = 160
    school_x = 120
    school_y = 220

    draw.text((name_x, name_y), name_text, fill=text_color, font=font_large)
    draw.text((school_x, school_y), school_text, fill=text_color, font=font_medium)

    phone_x = width - phone_width - 120
    phone_y = height - 80

    draw.text((phone_x, phone_y), phone_text, fill=text_color, font=font_small)

def draw_neon_template(draw, width, height, colors, user_data, layout):
    neon_color = colors['primary']
    for thickness in range(8, 0, -1):
        draw.rectangle([60-thickness, 60-thickness, width-60+thickness, height-60+thickness], 
                      outline=neon_color, width=thickness)

    font_large = get_font(46, 'bold')
    font_medium = get_font(32, 'regular')
    font_small = get_font(28, 'regular')

    name_text = user_data['name']
    school_text = user_data['school']
    phone_text = user_data['phone']

    name_width = draw.textbbox((0,0), name_text, font=font_large)[2]
    school_width = draw.textbbox((0,0), school_text, font=font_medium)[2]
    phone_width = draw.textbbox((0,0), phone_text, font=font_small)[2]

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

def draw_galaxy_template(draw, width, height, colors, user_data, layout):
    # 별 추가
    for i in range(100):
        x = random.randint(0, width)
        y = random.randint(0, height)
        brightness = random.randint(150, 255)
        size = random.choice([1] * 90 + [2] * 10)
        if size == 1:
            draw.point((x, y), fill=(brightness, brightness, brightness))
        else:
            draw.ellipse([x-1, y-1, x+1, y+1], fill=(brightness, brightness, brightness))

    font_large = get_font(48, 'bold')
    font_medium = get_font(34, 'regular')
    font_small = get_font(30, 'regular')

    name_text = user_data['name']
    school_text = user_data['school']
    phone_text = user_data['phone']

    phone_width = draw.textbbox((0,0), phone_text, font=font_small)[2]

    name_x = 110
    name_y = 150
    school_x = 110
    school_y = 220

    draw.text((name_x, name_y), name_text, fill=(255, 255, 255), font=font_large)
    draw.text((school_x, school_y), school_text, fill=(200, 200, 255), font=font_medium)

    phone_x = width - phone_width - 110
    phone_y = height - 100

    draw.text((phone_x, phone_y), phone_text, fill=(255, 255, 200), font=font_small)

def draw_minimalist_template(draw, width, height, colors, user_data, layout):
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

    phone_width = draw.textbbox((0, 0), phone_text, font=font_small)[2]
    phone_x = width - phone_width - 120
    phone_y = height - 140

    draw.text((phone_x, phone_y), phone_text, fill=(100, 100, 100), font=font_small)
    
def draw_grunge_template(draw, width, height, colors, user_data, layout):
    accent_rgb = colors['accent']
    secondary_rgb = colors['secondary']
    base_color = tuple(max(0, c-30) for c in colors['primary'])

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

    phone_width = draw.textbbox((0,0), phone_text, font=font_small)[2]

    name_x = 100
    name_y = 160
    school_x = 100
    school_y = 220

    draw.text((name_x, name_y), name_text, fill=text_color, font=font_large)
    draw.text((school_x, school_y), school_text, fill=text_color, font=font_medium)

    phone_x = width - phone_width - 100
    phone_y = height - 100

    draw.text((phone_x, phone_y), phone_text, fill=text_color, font=font_small)

# ========== QR 코드 생성 ==========

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

def draw_cute_template(draw, width, height, colors, user_data, layout):
    # 배경은 이미 생성되어 있으므로 추가 패턴만
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
    phone
    #코드 에러난 듯 일단 git add 해놨으니까 해당본 그대로 다시 클로드 돌리기