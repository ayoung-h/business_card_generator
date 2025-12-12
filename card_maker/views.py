from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import os
import uuid
from .utils import create_business_card, generate_qr_code, USER_STYLES

def index(request):
    """메인페이지 - 스타일 선택지 포함"""
    context = {
        'user_styles': USER_STYLES
    }
    return render(request, 'card_maker/index.html', context)

@csrf_exempt
def generate_card(request):
    """명함 생성 - 스타일 파라미터 지원"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            user_data = {
                'name': data.get('name', ''),
                'school': data.get('school', ''),
                'phone': data.get('phone', ''),
                'favorite_color': data.get('favorite_color', '#3498db'),
            }

            # 사용자가 선택한 스타일 (선택 안하면 None -> 랜덤)
            style = data.get('style', None)

            # 명함 생성
            card_img, used_style = create_business_card(user_data, style=style)

            # 파일명 생성 및 저장
            filename = f"card_{uuid.uuid4().hex[:8]}.png"
            filepath = os.path.join(settings.MEDIA_ROOT, 'cards', filename)

            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            card_img.save(filepath)

            # QR 코드 생성
            server_ip = request.get_host()
            download_url = f'http://{server_ip}/download/{filename}/'
            qr_img = generate_qr_code(download_url)

            qr_filename = f"qr_{uuid.uuid4().hex[:8]}.png"
            qr_filepath = os.path.join(settings.MEDIA_ROOT, 'qrcodes', qr_filename)

            os.makedirs(os.path.dirname(qr_filepath), exist_ok=True)
            qr_img.save(qr_filepath)

            # 스타일 이름을 한글로 변환
            style_names = {
                'space': '우주',
                'cute': '귀여운',
                'neon': '네온',
                'retro': '레트로',
                'vintage': '빈티지',
                'nature': '자연',
                'engineering': '공학',
                'art': '미술',
                'sports': '스포츠',
                'music': '음악',
                'education': '교육',
                'business': '비즈니스',
                'medical': '의료'
            }

            return JsonResponse({
                'success': True,
                'card_url': f'/media/cards/{filename}',
                'qr_url': f'/media/qrcodes/{qr_filename}',
                'download_url': download_url,
                'style': used_style,
                'style_name': style_names.get(used_style, used_style),
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
        
    return JsonResponse({'success': False, 'error': 'POST method required'})

def download_card(request, filename):
    """명함 다운로드"""
    filepath = os.path.join(settings.MEDIA_ROOT, 'cards', filename)

    if not os.path.exists(filepath):
        raise Http404("파일을 찾을 수 없습니다.")
    
    with open(filepath, 'rb') as f:
        response = HttpResponse(f.read(), content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response