from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import os
import uuid
import logging
from .utils import create_business_card, generate_qr_code

logger = logging.getLogger(__name__)

def index(request):
    """메인페이지"""
    return render(request, 'card_maker/index.html')

def validate_user_data(data):
    """사용자 입력 데이터 검증"""
    errors = []
    
    name = data.get('name', '').strip()
    school = data.get('school', '').strip()
    phone = data.get('phone', '').strip()
    favorite_color = data.get('favorite_color', '#3498db').strip()
    
    # 필수 항목 검증
    if not name:
        errors.append('이름을 입력해주세요.')
    elif len(name) > 50:
        errors.append('이름은 50자 이내로 입력해주세요.')
    
    if not school:
        errors.append('학교를 입력해주세요.')
    elif len(school) > 100:
        errors.append('학교명은 100자 이내로 입력해주세요.')
    
    if not phone:
        errors.append('전화번호를 입력해주세요.')
    elif len(phone) > 20:
        errors.append('전화번호는 20자 이내로 입력해주세요.')
    
    # 색상 코드 검증
    if not favorite_color.startswith('#') or len(favorite_color) != 7:
        logger.warning(f"잘못된 색상 코드: {favorite_color}, 기본값 사용")
        favorite_color = '#3498db'
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'data': {
            'name': name,
            'school': school,
            'phone': phone,
            'favorite_color': favorite_color,
        }
    }

def ensure_directory_exists(directory):
    """디렉토리 존재 확인 및 생성"""
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except OSError as e:
        logger.error(f"디렉토리 생성 실패: {directory}, {e}")
        return False

def save_image_safely(image, filepath):
    """이미지 안전하게 저장"""
    try:
        directory = os.path.dirname(filepath)
        if not ensure_directory_exists(directory):
            raise IOError(f"디렉토리 생성 실패: {directory}")
        
        image.save(filepath)
        
        # 파일 저장 확인
        if not os.path.exists(filepath):
            raise IOError(f"파일 저장 실패: {filepath}")
        
        return True
    except Exception as e:
        logger.error(f"이미지 저장 오류: {filepath}, {e}")
        raise

@csrf_exempt
def generate_card(request):
    """명함 생성 (에러 처리 강화)"""
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'POST 메서드만 허용됩니다.'
        }, status=405)
    
    try:
        # JSON 데이터 파싱
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {e}")
            return JsonResponse({
                'success': False,
                'error': '잘못된 JSON 형식입니다.'
            }, status=400)
        
        # 데이터 검증
        validation = validate_user_data(data)
        if not validation['valid']:
            return JsonResponse({
                'success': False,
                'error': ', '.join(validation['errors'])
            }, status=400)
        
        user_data = validation['data']
        
        # 명함 이미지 생성
        try:
            card_img, template = create_business_card(user_data)
        except Exception as e:
            logger.error(f"명함 생성 오류: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': '명함 생성 중 오류가 발생했습니다.'
            }, status=500)
        
        # 명함 이미지 저장
        filename = f"card_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(settings.MEDIA_ROOT, 'cards', filename)
        
        try:
            save_image_safely(card_img, filepath)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': '명함 이미지 저장 중 오류가 발생했습니다.'
            }, status=500)
        
        # QR 코드 생성
        server_ip = request.get_host()
        download_url = f'http://{server_ip}/download/{filename}/'
        
        try:
            qr_img = generate_qr_code(download_url)
        except Exception as e:
            logger.error(f"QR 코드 생성 오류: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': 'QR 코드 생성 중 오류가 발생했습니다.'
            }, status=500)
        
        # QR 코드 저장
        qr_filename = f"qr_{uuid.uuid4().hex[:8]}.png"
        qr_filepath = os.path.join(settings.MEDIA_ROOT, 'qrcodes', qr_filename)
        
        try:
            save_image_safely(qr_img, qr_filepath)
        except Exception as e:
            # QR 저장 실패해도 명함은 제공
            logger.error(f"QR 코드 저장 오류: {e}", exc_info=True)
            return JsonResponse({
                'success': True,
                'card_url': f'/media/cards/{filename}',
                'qr_url': None,
                'download_url': download_url,
                'template': template,
                'warning': 'QR 코드 생성은 실패했지만 명함은 정상적으로 생성되었습니다.'
            })
        
        # 성공 응답
        return JsonResponse({
            'success': True,
            'card_url': f'/media/cards/{filename}',
            'qr_url': f'/media/qrcodes/{qr_filename}',
            'download_url': download_url,
            'template': template,
        })
    
    except Exception as e:
        logger.error(f"예기치 않은 오류: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'
        }, status=500)

def download_card(request, filename):
    """명함 다운로드 (보안 강화)"""
    # 파일명 검증 (경로 탐색 공격 방지)
    if '..' in filename or '/' in filename or '\\' in filename:
        logger.warning(f"잘못된 파일명 접근 시도: {filename}")
        raise Http404("잘못된 파일 요청입니다.")
    
    # 확장자 검증
    if not filename.lower().endswith('.png'):
        logger.warning(f"잘못된 파일 형식: {filename}")
        raise Http404("PNG 파일만 다운로드 가능합니다.")
    
    # 파일 경로 생성
    filepath = os.path.join(settings.MEDIA_ROOT, 'cards', filename)
    
    # 파일 존재 확인
    if not os.path.exists(filepath):
        logger.info(f"파일을 찾을 수 없음: {filepath}")
        raise Http404("파일을 찾을 수 없습니다.")
    
    # 파일이 실제로 media/cards 디렉토리 안에 있는지 확인
    real_path = os.path.realpath(filepath)
    cards_dir = os.path.realpath(os.path.join(settings.MEDIA_ROOT, 'cards'))
    if not real_path.startswith(cards_dir):
        logger.warning(f"디렉토리 외부 파일 접근 시도: {real_path}")
        raise Http404("잘못된 파일 요청입니다.")
    
    # 파일 읽기 및 응답
    try:
        with open(filepath, 'rb') as f:
            response = HttpResponse(f.read(), content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    except IOError as e:
        logger.error(f"파일 읽기 오류: {filepath}, {e}")
        raise Http404("파일을 읽을 수 없습니다.")
    #클로드야 싸우자.................................