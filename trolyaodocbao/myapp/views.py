from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .train_model import IntentClassifier
import requests
from bs4 import BeautifulSoup, Tag
from typing import List, Optional, Dict, Union
import os
import joblib
import re
import random

# Initialize intent classifier
intent_classifier = IntentClassifier()
model_path = os.path.join('myapp', 'models', 'intent_model.joblib')
try:
    intent_classifier.load_model(model_path)
except:
    # If model doesn't exist or can't be loaded, train a new one
    intent_classifier.train('myapp/data/intent_data.csv')
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    intent_classifier.save_model(model_path)

class XuLyTinTuc:
    def __init__(self):
        self.duongdan = "https://nhandan.vn/"
        self.luutrutintuc = []
        self.baibao_hientai = None
        self.trangbao_hientai = "Nhân Dân"
        
        # Định nghĩa các chuyên mục cơ bản của báo Nhân Dân
        self.danhmuc_chung = {
            'chính trị': 'chinhtri',
            'kinh tế': 'kinhte',
            'văn hóa': 'vanhoa',
            'xã hội': 'xahoi',
            'pháp luật': 'phapluat',
            'du lịch': 'du-lich',
            'thế giới': 'thegioi',
            'thể thao': 'thethao',
            'giáo dục': 'giaoduc',
            'y tế': 'y-te',
            'khoa học công nghệ': 'khoahoc-congnghe',
            'môi trường': 'moi-truong',
            'bạn đọc': 'bandoc'
        }
        
        # Cấu hình chi tiết cho Báo Nhân Dân
        self.danhsach_trangbao = {
            "nhandan": {
                "ten": "Nhân Dân",
                "url": "https://nhandan.vn/",
                "mota": "Cơ quan Trung ương của Đảng Cộng sản Việt Nam",
                "danhmuc": {
                    **self.danhmuc_chung,
                    'xã luận': 'xa-luan',
                    'bình luận phê phán': 'binh-luan-phe-phan',
                    'xây dựng đảng': 'xay-dung-dang',
                    'tài chính chứng khoán': 'chungkhoan',
                    'thông tin hàng hóa': 'thong-tin-hang-hoa',
                    'bhxh và cuộc sống': 'bhxh-va-cuoc-song',
                    'người tốt việc tốt': 'nguoi-tot-viec-tot',
                    'bình luận quốc tế': 'binh-luan-quoc-te',
                    'asean': 'asean',
                    'châu phi': 'chau-phi',
                    'châu mỹ': 'chau-my',
                    'châu âu': 'chau-au',
                    'trung đông': 'trung-dong',
                    'châu á-tbd': 'chau-a-tbd',
                    'góc tư vấn': 'goc-tu-van',
                    'đường dây nóng': 'duong-day-nong',
                    'kiểm chứng thông tin': 'factcheck'
                },
                "prefix": "/",
                "suffix": "/"
            }
        }

        # Cấu hình các bộ chọn (selectors) HTML cho Báo Nhân Dân
        self.trangbao_selectors = {
            "nhandan": {
                "category": {
                    "article": ['article.story', 'div.rank-1', 'div.rank-2', 'div.rank-3'],
                    "title": ['h2.story__heading', 'h3.story__heading'],
                    "description": ['div.story__summary'],
                    "link": 'a.cms-link'
                }
            }
        }
    
    def la_bai_da_phuong_tien(self, tieude):
        """Kiểm tra xem tiêu đề có bắt đầu bằng [Video] hoặc [Ảnh] hay không"""
        return tieude.startswith('[Video]') or tieude.startswith('[Ảnh]')
    
    def loc_bai_da_phuong_tien(self, danhsach_bai):
        """Lọc bỏ tất cả bài viết có tiêu đề bắt đầu bằng [Video] hoặc [Ảnh]"""
        return [bai for bai in danhsach_bai if not self.la_bai_da_phuong_tien(bai['tieude'])]

    def laytin_moinhat(self):
        """Lấy tin mới nhất từ trang báo Nhân Dân"""
        try:
            response = requests.get(self.duongdan)
            soup = BeautifulSoup(response.content, 'html.parser')
            danhsachtin = []
            ketqua = []
            
            # Set để lưu trữ URL đã thu thập để tránh trùng lặp
            url_dadanhsach = set()
            
            # Xác định xem URL hiện tại có phải là trang chủ hay không
            is_homepage = self.duongdan.rstrip('/') == self.danhsach_trangbao["nhandan"]["url"].rstrip('/')
            
            # Nếu là trang chủ, quét cả các phần rank và bài viết nổi bật
            if is_homepage:
                # 1. Quét các phần rank trước (vì đây là các bài viết nổi bật nhất)
                rank_divs = soup.find_all('div', class_=['rank-1', 'rank-2', 'rank-3'])
                for div in rank_divs:
                    rank_articles = div.find_all('article', class_='story')
                    for article in rank_articles:
                        heading = article.find(['h2', 'h3'], class_='story__heading')
                        if heading:
                            link = heading.find('a', class_='cms-link')
                            if link:
                                tieude = link.get('title', '') or link.text.strip()
                                url = link.get('href', '')
                                if tieude and url and url not in url_dadanhsach:
                                    url_dadanhsach.add(url)
                                    danhsachtin.append({
                                        'tieude': tieude,
                                        'url': url
                                    })
            
                # 2. Quét các bài viết chính khác
                main_articles = soup.find_all('article', class_='story')
                for article in main_articles:
                    # Bỏ qua các bài viết đã nằm trong phần rank
                    if article.parent and article.parent.get('class') and any(cls in ['rank-1', 'rank-2', 'rank-3'] for cls in article.parent.get('class')):
                        continue
                        
                    heading = article.find(['h2', 'h3'], class_='story__heading')
                    if heading:
                        link = heading.find('a', class_='cms-link')
                        if link:
                            tieude = link.get('title', '') or link.text.strip()
                            url = link.get('href', '')
                            if tieude and url and url not in url_dadanhsach:
                                url_dadanhsach.add(url)
                                danhsachtin.append({
                                    'tieude': tieude,
                                    'url': url
                                })
            else:
                # Nếu là trang chuyên mục, tìm tất cả bài viết
                articles = soup.find_all('article', class_='story')
                
                for article in articles:
                    heading = article.find(['h2', 'h3'], class_='story__heading')
                    if heading:
                        link = heading.find('a', class_='cms-link')
                        if link:
                            tieude = link.get('title', '') or link.text.strip()
                            url = link.get('href', '')
                            if tieude and url and url not in url_dadanhsach:
                                url_dadanhsach.add(url)
                                danhsachtin.append({
                                    'tieude': tieude,
                                    'url': url
                                })

            # Lọc bỏ tất cả bài viết video và ảnh
            danhsachtin_loc = self.loc_bai_da_phuong_tien(danhsachtin)
            
            # Tạo danh sách kết quả hiển thị
            ketqua = [f"Tiêu đề: {tin['tieude']}" for tin in danhsachtin_loc[:10]]
            
            # Lưu danh sách tin đã lọc bỏ video và ảnh
            self.luutrutintuc = danhsachtin_loc[:10]
            
            # Trả về 10 tin đầu tiên đã lọc, mỗi tin một dòng
            return ketqua

        except Exception as e:
            print(f"Lỗi khi lấy tin mới nhất: {str(e)}")
            return ["Đã xảy ra lỗi khi tải tin tức. Vui lòng thử lại sau."]

    def lay_chitiet_baibao(self, tieude_timkiem) -> Union[Dict[str, str], str, List[str]]:
        if not self.luutrutintuc:
            return ["Vui lòng xem tin tức mới nhất trước khi đọc chi tiết bài báo"]
        
        tukhoa_loaibo = [
            'đọc bài', 'đọc chi tiết', 'xem bài', 'bài', 'đọc', 
            'xem', 'nội dung', 'chi tiết', 'cho tôi xem'
        ]
        
        tu_timkiem = tieude_timkiem.lower()
        for tu in tukhoa_loaibo:
            tu_timkiem = tu_timkiem.replace(tu, '').strip()
        
        if not tu_timkiem:
            return ["Vui lòng nói rõ tiêu đề bài báo bạn muốn đọc"]
        
        tin_phuhop = None
        tile_phuhop_max = 0
        
        for tin in self.luutrutintuc:
            tieude = tin['tieude'].lower()
            
            danhsach_tu_tim = [tu for tu in tu_timkiem.split() if len(tu) > 1]
            danhsach_tu_tieude = tieude.split()
            
            so_tu_trung = sum(1 for tu in danhsach_tu_tim if any(tu in tu_tieude for tu_tieude in danhsach_tu_tieude))
            
            if so_tu_trung > 0:
                tile_phuhop = so_tu_trung / len(danhsach_tu_tim) if danhsach_tu_tim else 0
                if tile_phuhop > tile_phuhop_max:
                    tile_phuhop_max = tile_phuhop
                    tin_phuhop = tin
        
        if tin_phuhop and tile_phuhop_max >= 0.3:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5'
                }
                
                phanhoi = requests.get(tin_phuhop['url'], headers=headers, timeout=10)
                phanhoi.raise_for_status()
                soup = BeautifulSoup(phanhoi.content, 'html.parser')
                
                noidung_parts = []
                
                # Xử lý cho Báo Nhân Dân
                # Lấy tiêu đề
                article_title = soup.find('h1', class_='article__title')
                if article_title:
                    noidung_parts.append(article_title.text.strip())
                
                # Lấy tóm tắt (sapo)
                article_sapo = soup.find('div', class_='article__sapo')
                if article_sapo:
                    noidung_parts.append(article_sapo.text.strip())
                
                # Lấy nội dung chính - tìm tất cả thẻ p trong bài viết
                article_content = soup.find_all('p')
                if article_content:
                    for p in article_content:
                        # Loại bỏ các caption ảnh và thành phần không phải nội dung chính
                        if not p.find('figure') and p.text.strip():
                            noidung_parts.append(p.text.strip())
                
                # Nếu không tìm thấy nội dung, thử phương pháp khác
                if len(noidung_parts) <= 2:  # Nếu chỉ có tiêu đề và sapo
                    article_body = soup.find('div', class_='article-body')
                    if article_body:
                        paragraphs = article_body.find_all(['p', 'h2', 'h3'])
                        for p in paragraphs:
                            if p.text.strip() and not p.find('figure'):
                                noidung_parts.append(p.text.strip())
                
                # Loại bỏ các đoạn trùng lặp
                noidung_parts = list(dict.fromkeys(noidung_parts))
                
                if not noidung_parts:
                    return ["Không thể đọc nội dung bài viết này."]
                
                self.baibao_hientai = {
                    'tieude': tin_phuhop['tieude'],
                    'noidung': '\n\n'.join(noidung_parts)
                }
                
                return noidung_parts
                
            except Exception as e:
                print(f"Lỗi khi tải nội dung: {str(e)}")
                return ["Không thể tải nội dung chi tiết."]
        
        return ["Không tìm thấy bài báo với tiêu đề này. Vui lòng nói rõ tiêu đề bài báo bạn muốn đọc."]

    def gioi_thieu_bot(self):
        gioi_thieu = ["Xin chào! Tôi là trợ lý đọc báo Nhân Dân. Tôi có thể giúp bạn đọc tin tức mới nhất từ báo Nhân Dân, đọc tin tức theo chuyên mục bạn quan tâm, và đọc chi tiết nội dung bài báo. Bạn muốn đọc tin tức về chủ đề nào? Ví dụ: chính trị, kinh tế, văn hóa, xã hội..."]
        return gioi_thieu

    def chao_hoi(self):
        # Danh sách các lời chào ngẫu nhiên
        danh_sach_chao = [
            "Xin chào! Tôi là trợ lý đọc báo Nhân Dân. Bạn muốn đọc tin về chủ đề gì hôm nay?",
            "Chào bạn! Rất vui được gặp bạn. Tôi có thể đọc tin tức về chủ đề nào cho bạn?",
            "Xin chào! Hôm nay bạn muốn nghe tin tức về chủ đề gì?",
            "Chào bạn! Tôi là trợ lý đọc báo Nhân Dân. Bạn quan tâm đến tin tức gì?"
        ]
        # Chọn một lời chào ngẫu nhiên
        return [random.choice(danh_sach_chao)]

    def lay_tin_theloai(self, text):
        noidung_timkiem = text.lower()
        chuyenmuc_duocchon = None
        
        # Lấy thông tin trang báo hiện tại (Nhân Dân)
        trangbao = self.danhsach_trangbao["nhandan"]
        
        # Xử lý đặc biệt cho "trang chủ"
        if "trang chủ" in noidung_timkiem:
            self.duongdan = trangbao["url"]
            return self.laytin_moinhat()
        
        # Tìm chuyên mục phù hợp
        for chuyenmuc, duongdan in trangbao["danhmuc"].items():
            if chuyenmuc in noidung_timkiem:
                chuyenmuc_duocchon = duongdan
                break
        
        if not chuyenmuc_duocchon:
            return [f"Chuyên mục này không có trên báo Nhân Dân hoặc chưa được hỗ trợ. Vui lòng thử chuyên mục khác như: {', '.join(list(trangbao['danhmuc'].keys())[:5])}..."]
        
        try:
            # Tạo URL đầy đủ cho chuyên mục
            duongdan_url = f"{trangbao['url'].rstrip('/')}{trangbao['prefix']}{chuyenmuc_duocchon}{trangbao['suffix']}"
            
            # Thêm header để tránh bị chặn như một bot
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
                'Referer': self.duongdan
            }
            
            phanhoi = requests.get(duongdan_url, headers=headers, timeout=10)
            
            # Kiểm tra mã trạng thái HTTP
            if phanhoi.status_code == 403:
                return [f"Trang báo Nhân Dân đã chặn truy cập đến chuyên mục này."]
            elif phanhoi.status_code != 200:
                return [f"Không thể tải tin tức cho chuyên mục này."]
            
            phanhoi.raise_for_status()
            
            # Kiểm tra nội dung có chứa thông báo lỗi hoặc từ chối truy cập
            if "access denied" in phanhoi.text.lower() or "blocked" in phanhoi.text.lower() or "403 forbidden" in phanhoi.text.lower():
                return [f"Trang báo Nhân Dân đã chặn truy cập đến chuyên mục này."]
            
            # Lưu URL hiện tại để truy cập bài viết
            self.duongdan = duongdan_url
            
            ketqua = [f"Đã chọn chuyên mục {chuyenmuc} của báo Nhân Dân. Đang tải tin tức..."]
            # Lấy danh sách tin mới nhất cho chuyên mục
            tin_moi = self.laytin_moinhat()
            return ketqua + tin_moi
            
        except requests.Timeout:
            return [f"Không thể tải tin tức cho chuyên mục này do quá thời gian chờ."]
        except requests.RequestException as e:
            return [f"Không thể kết nối đến chuyên mục này."]
        except Exception as e:
            return [f"Đã xảy ra lỗi khi tải tin tức cho chuyên mục này."]

    def xuly_yeucau(self, intent, text):
        # Danh sách từ khóa để nhận diện yêu cầu giới thiệu
        gioi_thieu_keywords = [
            "giới thiệu", "bạn là ai", "bạn có thể làm gì", "chức năng", 
            "khả năng", "làm được gì", "giúp được gì", "hỗ trợ gì", 
            "có thể làm", "bạn làm được gì", "bạn giúp được gì"
        ]
        
        greeting_keywords = ['chào', 'xin chào', 'hello', 'hi', 'hey', 'chào bạn']
        
        text_lower = text.lower()
        
        # Kiểm tra intent và từ khóa giới thiệu trước
        if (intent == 'intro_bot' or 
            any(keyword in text_lower for keyword in gioi_thieu_keywords)):
            return self.gioi_thieu_bot()
        
        elif intent == 'greeting' or any(keyword in text_lower for keyword in greeting_keywords):
            return self.chao_hoi()
        
        elif intent == 'latest_news':
            return self.laytin_moinhat()
        
        elif intent == 'search_news':
            result = self.lay_chitiet_baibao(text)
            if isinstance(result, dict):
                return [result['noidung']]  # Trả về nội dung bài báo dưới dạng list
            return result
        
        elif intent == 'category_news' and text:
            return self.lay_tin_theloai(text)
        
        else:
            # Thông báo lỗi ngắn gọn hơn
            return ["Xin lỗi, tôi không hiểu yêu cầu. Bạn có thể đọc tin mới nhất, tin theo chuyên mục, hoặc đọc chi tiết bài báo. Hãy thử lại."]

# Khởi tạo đối tượng xử lý tin tức toàn cục để lưu trữ giữa các request
xu_ly_chung = XuLyTinTuc()

# Tạo một compact text để đọc dễ dàng hơn
def format_for_tts(text_list):
    # Nếu chỉ có một mục, trả về nguyên mục đó
    if len(text_list) == 1:
        return text_list[0]
    
    # Nối các mục lại với nhau, nhưng giữ nguyên các đầu mục
    result = ""
    for item in text_list:
        if item.startswith("Tiêu đề:") or item.startswith("-"):
            # Với các danh sách tin, thêm dấu xuống dòng
            result += item + ". "
        else:
            # Với các đoạn văn thông thường, nối lại
            result += item + " "
    
    # Xử lý một số trường hợp đặc biệt để làm gọn
    result = re.sub(r'\s+', ' ', result)  # Loại bỏ khoảng trắng thừa
    result = re.sub(r'\.+', '.', result)  # Loại bỏ dấu chấm thừa
    result = re.sub(r'\s+\.', '.', result)  # Xử lý khoảng trắng trước dấu chấm
    
    print(f"TTS text formatted: {result[:100]}...")  # In ra 100 ký tự đầu tiên của văn bản TTS
    return result

@csrf_exempt
def process_input(request):
    if request.method == 'POST':
        try:
            text = request.POST.get('text', '').lower().strip()
            if not text:
                return JsonResponse({
                    'status': 'success',
                    'response': ['Xin lỗi, tôi không nghe rõ bạn nói gì. Bạn có thể nhắc lại được không?'],
                    'tts_text': 'Xin lỗi, tôi không nghe rõ bạn nói gì. Bạn có thể nhắc lại được không?'
                })

            # Phát hiện intent
            intent = intent_classifier.predict(text)
            print(f"Detected intent: {intent} for text: {text}")  # Ghi log để debug
            
            # Xử lý trường hợp greeting đơn giản trước
            greeting_keywords = ['chào', 'xin chào', 'hello', 'hi', 'hey', 'chào bạn']
            if any(keyword in text for keyword in greeting_keywords) or intent == 'greeting':
                response = ["Xin chào! Tôi là trợ lý đọc báo Nhân Dân. Bạn muốn đọc tin về chủ đề gì hôm nay?"]
                return JsonResponse({
                    'status': 'success',
                    'response': response,
                    'tts_text': response[0]
                })
            
            # Gọi phương thức xử lý yêu cầu từ lớp XuLyTinTuc
            response = xu_ly_chung.xuly_yeucau(intent, text)
            
            print(f"Response from xuly_yeucau: {response[:2] if isinstance(response, list) else 'Not a list'}")
            
            # Format text cho TTS
            tts_text = format_for_tts(response)
            
            # Kiểm tra và đảm bảo tts_text không rỗng
            if not tts_text or tts_text.strip() == '':
                print("Warning: Empty TTS text after formatting, using default")
                tts_text = "Xin lỗi, tôi không thể đọc nội dung này."
            
            print(f"Final TTS text length: {len(tts_text)}")
            
            return JsonResponse({
                'status': 'success', 
                'response': response,
                'tts_text': tts_text
            })
            
        except Exception as e:
            print(f"Error: {str(e)}")  # For debugging
            error_message = 'Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau.'
            return JsonResponse({
                'status': 'success',
                'response': [error_message],
                'tts_text': error_message
            })

    return JsonResponse({
        'status': 'success',
        'response': ['Xin lỗi, tôi không thể xử lý yêu cầu này.'],
        'tts_text': 'Xin lỗi, tôi không thể xử lý yêu cầu này.'
    })


def chat_view(request):
    """
    Render the chat interface
    """
    return render(request, 'myapp/chat.html', {
        'title': 'Trợ lý đọc báo Nhân Dân'
    })