from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import os
import uuid
from .utils import create_business_card, generate_qr_code

def index(request): #메인페이지
    return render(request, 'card_maker/index.html')

@csrf_exempt
def generate_card(request): #명함 생성
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            user_data = {
                'name': data.get('name', ''),
                'school': data.get('school', ''),
                'phone': data.get('phone', ''),
                'favorite_color': data.get('favorite_color', '#3498db'),
            }

            card_img, template = create_business_card(user_data)

            filename = f"card_{uuid.uuid4().hex[:8]}.png"
            filepath = os.path.join(settings.MEDIA_ROOT, 'cards', filename)

            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            card_img.save(filepath)

            server_ip = request.get_host()
            download_url = f'http://{server_ip}/download/{filename}/'
            qr_img = generate_qr_code(download_url)

            qr_filename = f"qr_{uuid.uuid4().hex[:8]}.png"
            qr_filepath = os.path.join(settings.MEDIA_ROOT, 'qrcodes', qr_filename)

            os.makedirs(os.path.dirname(qr_filepath), exist_ok=True)

            qr_img.save(qr_filepath)

            return JsonResponse({
                'success': True,
                'card_url': f'/media/cards/{filename}',
                'qr_url': f'/media/qrcodes/{qr_filename}',
                'download_url': download_url,
                'template': template,
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
        
    return JsonResponse({'success': False, 'error': 'POST method required'})

def download_card(request, filename): #명함 다운로드
    filepath = os.path.join(settings.MEDIA_ROOT, 'cards', filename)

    if not os.path.exists(filepath):
        raise Http404("파일을 찾을 수 없습니다.")
    
    with open(filepath, 'rb') as f:
        response = HttpResponse(f.read(), content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response