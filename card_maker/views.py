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