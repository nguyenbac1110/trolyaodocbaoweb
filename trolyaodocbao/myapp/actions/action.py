import requests
from bs4 import BeautifulSoup
import random
import webbrowser
class XuLyTinTuc:
    def __init__(self):
        self.duongdan = "https://vnexpress.net/"
        self.luutrutintuc = []
        self.baibao_hientai = None  

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
                    mota = phan_mota.text.strip()
                    link = phan_link['href']
                    if not link.startswith('http'):
                        link = 'https://vnexpress.net' + link
                    
                    tin_moi = {
                        'tieude': tieude,
                        'mota': mota,
                        'link': link
                    }
                    self.luutrutintuc.append(tin_moi)
                    danhsach_tieude.append(f"Tiêu đề: {tieude}")
            
            if not self.luutrutintuc:
                return ["Không thể tải tin tức. Vui lòng thử lại sau."]
            
            return danhsach_tieude
            
        except requests.RequestException as e:
            return ["Không thể kết nối đến VnExpress. Vui lòng kiểm tra kết nối mạng."]
        except Exception as e:
            return ["Đã xảy ra lỗi khi tải tin tức. Vui lòng thử lại sau."]

    def lay_chitiet_baibao(self, tieude_timkiem):
        if not self.luutrutintuc:
            return "Vui lòng xem tin tức mới nhất trước khi đọc chi tiết"
        
        tukhoa_loaibo = [
            'đọc bài', 'đọc chi tiết', 'xem bài', 'bài', 'đọc', 
            'xem', 'nội dung', 'chi tiết', 'cho tôi xem'
        ]
        
        tu_timkiem = tieude_timkiem.lower()
        for tu in tukhoa_loaibo:
            tu_timkiem = tu_timkiem.replace(tu, '').strip()
        
        if not tu_timkiem:
            return "Vui lòng nói rõ tiêu đề bài báo bạn muốn đọc"
        
        tin_phuhop = None
        tile_phuhop_max = 0
        
        for tin in self.luutrutintuc:
            tieude = tin['tieude'].lower()
            
            danhsach_tu_tim = [tu for tu in tu_timkiem.split() if len(tu) > 1]
            danhsach_tu_tieude = tieude.split()
            
            so_tu_trung = sum(1 for tu in danhsach_tu_tim if any(tu in tu_tieude for tu_tieude in danhsach_tu_tieude))
            
            if so_tu_trung > 0:
                tile_phuhop = so_tu_trung / len(danhsach_tu_tim)
                if tile_phuhop > tile_phuhop_max:
                    tile_phuhop_max = tile_phuhop
                    tin_phuhop = tin
        
        if tin_phuhop and tile_phuhop_max >= 0.3:
            try:
                phanhoi = requests.get(tin_phuhop['link'])
                phanhoi.raise_for_status()
                soup = BeautifulSoup(phanhoi.content, 'html.parser')
                
                description = soup.find('p', class_='description')
                
                article_content = soup.find('article', class_='fck_detail')
                if article_content:
                    noidung_baibao = article_content.find_all('p', class_='Normal')
                else:
                    noidung_baibao = soup.find_all('p', class_='Normal')
                
                noidung_parts = []
                if description:
                    noidung_parts.append(description.text.strip())
                if noidung_baibao:
                    noidung_parts.extend([p.text.strip() for p in noidung_baibao])
                
                noidung_daydu = ' '.join(noidung_parts)
                
                self.baibao_hientai = {
                    'tieude': tin_phuhop['tieude'],
                    'noidung': noidung_daydu if noidung_daydu else tin_phuhop['mota']
                }
                
                return self.baibao_hientai
            except Exception as e:
                return "Không thể tải nội dung chi tiết. Vui lòng thử lại sau."
            
        return "Không tìm thấy bài báo với tiêu đề này. Vui lòng nói rõ tiêu đề bài báo bạn muốn đọc."

    def gioi_thieu_bot(self):
        return "Xin chào! Tôi là trợ lý đọc báo thông minh. Tôi có thể giúp bạn:\n- Đọc tin tức mới nhất từ VnExpress\n- Đọc chi tiết nội dung bài báo bạn quan tâm\n- Tóm tắt nội dung bài báo\nBạn có thể nói 'xem tin mới nhất' hoặc 'đọc bài' kèm theo tiêu đề bài báo bạn muốn đọc."

    def xuly_yeucau(self, intent, text):
        if intent == 'latest_news':
            return self.laytin_moinhat()
        elif intent == 'search_news':
            return self.lay_chitiet_baibao(text)
        elif intent == 'category_news' and text:
            return self.lay_tin_theloai(text)
        elif intent == 'intro_bot':
            return "Tôi là trợ lý đọc báo thông minh. Tôi có thể giúp bạn đọc tin tức mới nhất, tìm kiếm các bài báo cụ thể và đọc tin tức theo chuyên mục từ VnExpress."
        else:
            return "Xin lỗi, tôi không hiểu yêu cầu của bạn."
    def lay_tin_theloai(self, text):
        danhmuc_chuyenmuc = {
            'thời sự': '/thoi-su',
            'thế giới': '/the-gioi',
            'kinh doanh': '/kinh-doanh',
            'khoa học': '/khoa-hoc',
            'giải trí': '/giai-tri',
            'thể thao': '/the-thao',
            'pháp luật': '/phap-luat',
            'giáo dục': '/giao-duc',
            'sức khỏe': '/suc-khoe',
            'đời sống': '/doi-song',
            'du lịch': '/du-lich',
            'xe': '/oto-xe-may',
            'công nghệ': '/so-hoa',
            'góc nhìn': '/goc-nhin',
            'podcasts': '/podcast',
            'video': '/video',
            'bất động sản': '/bat-dong-san',
            'ý kiến': '/y-kien'
        }
        
        noidung_timkiem = text.lower()
        chuyenmuc_duocchon = None
        
        for chuyenmuc, duongdan in danhmuc_chuyenmuc.items():
            if chuyenmuc in noidung_timkiem:
                chuyenmuc_duocchon = duongdan
                break
        
        if not chuyenmuc_duocchon:
            return "Không tìm thấy chuyên mục này. Vui lòng thử lại với chuyên mục khác."
            
        try:
            duongdan_url = f"https://vnexpress.net{chuyenmuc_duocchon}"
            self.duongdan = duongdan_url
            return self.laytin_moinhat()
            
        except Exception as e:
            return "Không thể tải tin tức cho chuyên mục này. Vui lòng thử lại sau."