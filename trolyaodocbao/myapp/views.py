from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .train_model import IntentClassifier
import requests
from bs4 import BeautifulSoup

class XuLyTinTuc:
    def __init__(self):
        self.duongdan = "https://vnexpress.net/"
        self.luutrutintuc = []

    def laytin_moinhat(self):
        try:
            phanhoi = requests.get(self.duongdan)
            phanhoi.raise_for_status()
            
            soup = BeautifulSoup(phanhoi.content, 'html.parser')
            danhsachtin = soup.find_all('article', {'class': ['item-news', 'item-news-common', 'article-item']})
            
            self.luutrutintuc = []
            danhsach_tieude = []
            for baibao in danhsachtin[:10]:
                phan_tieude = baibao.find(['h3', 'h2'], recursive=True)
                if phan_tieude:
                    phan_link = phan_tieude.find('a', href=True)
                else:
                    continue
                    
                phan_mota = baibao.find(['p', 'div'], class_=['description', 'description-news'])
                
                if phan_tieude and phan_mota and phan_link:
                    tieude = phan_tieude.text.strip()
                    danhsach_tieude.append(f"Tiêu đề: {tieude}")
            
            if not danhsach_tieude:
                return ["Không thể tải tin tức. Vui lòng thử lại sau."]
            
            return danhsach_tieude
            
        except requests.RequestException:
            return ["Không thể kết nối đến VnExpress. Vui lòng kiểm tra kết nối mạng."]
        except Exception:
            return ["Đã xảy ra lỗi khi tải tin tức. Vui lòng thử lại sau."]

xu_ly_tin_tuc = XuLyTinTuc()
intent_classifier = IntentClassifier()
model_path = 'd:/Trolyaodocbaoweb/trolyaodocbao/myapp/models/intent_model.joblib'
intent_classifier.load_model(model_path)

def chat_view(request):
    return render(request, 'myapp/chat.html')

@csrf_exempt
def process_input(request):
    if request.method == 'POST':
        try:
            text = request.POST.get('text')
            if not text:
                return JsonResponse({'error': 'No text provided'})

            intent = intent_classifier.predict(text.lower())
            
            if intent == 'latest_news':
                news_list = xu_ly_tin_tuc.laytin_moinhat()
                if news_list:
                    return JsonResponse({
                        'status': 'success',
                        'response': news_list
                    })
            else:
                response = "Xin lỗi, tôi không hiểu yêu cầu của bạn."
                return JsonResponse({'response': response})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'error': 'Invalid request'})