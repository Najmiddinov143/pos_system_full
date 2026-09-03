# utils/image_fetcher.py - Placeholder bilan
from PIL import Image, ImageDraw, ImageFont
import requests
import urllib.parse
import os
import re
import time
import shutil

class ImageFetcher:
    def __init__(self):
        self.cache_dir = "assets/product_images"
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def search_image(self, product_name):
        """Mahsulot nomi bo'yicha rasm qidirish"""
        try:
            query = product_name.strip()
            
            # DuckDuckGo (ko'pincha ishlaydi)
            url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}+moy&iax=images&ia=images"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            images = re.findall(r'data-src="(https://[^"]+\.(?:jpg|jpeg|png|webp))"', response.text)
            for img in images:
                if 'google' not in img and 'gstatic' not in img and 'encrypted' not in img:
                    return img
            return None
            
        except Exception as e:
            print(f"Rasm qidirishda xatolik: {e}")
            return None
    
    def create_placeholder(self, product_name, product_id):
        """Agar rasm topilmasa, placeholder rasm yaratish"""
        try:
            safe_name = re.sub(r'[^a-zA-Z0-9]', '_', product_name)
            file_path = f"{self.cache_dir}/{product_id}_{safe_name}_placeholder.png"
            
            # Rasm yaratish
            img = Image.new('RGB', (200, 200), color='#1a1a2e')
            draw = ImageDraw.Draw(img)
            
            # Matn yozish
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()
            
            # Mahsulot nomini yozish
            text = product_name[:15]
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (200 - text_width) // 2
            y = (200 - text_height) // 2 - 20
            
            draw.text((x, y), text, fill='white', font=font)
            draw.text((x, y + 30), "🖼️ Rasm yo'q", fill='#a0a0b8', font=font)
            
            img.save(file_path)
            return file_path
            
        except Exception as e:
            print(f"Placeholder yaratishda xatolik: {e}")
            return None
    
    def download_image(self, product_name, product_id):
        """Rasmni yuklab olish yoki placeholder yaratish"""
        try:
            safe_name = re.sub(r'[^a-zA-Z0-9]', '_', product_name)
            cache_path = f"{self.cache_dir}/{safe_name}.jpg"
            
            if os.path.exists(cache_path):
                return cache_path
            
            # Rasm qidirish
            image_url = self.search_image(product_name)
            
            if image_url:
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    response = requests.get(image_url, headers=headers, timeout=15)
                    
                    if response.status_code == 200:
                        file_path = f"{self.cache_dir}/{product_id}_{safe_name}.jpg"
                        with open(file_path, 'wb') as f:
                            f.write(response.content)
                        return file_path
                except:
                    pass
            
            # Rasm topilmasa placeholder yaratish
            return self.create_placeholder(product_name, product_id)
            
        except Exception as e:
            print(f"Rasm yuklab olishda xatolik: {e}")
            return self.create_placeholder(product_name, product_id)