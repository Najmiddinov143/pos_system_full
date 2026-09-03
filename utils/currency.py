# utils/currency.py - VALYUTA KURSINI AVTOMATIK OLISH

import requests
import json
from datetime import datetime
import os
import logging

# Logging sozlamalari (xatoliklarni kuzatish uchun)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_usd_rate():
    """
    Real vaqtda USD kursini olish (cbu.uz dan)
    Agar internet bo'lmasa, oxirgi saqlangan qiymatni qaytaradi
    """
    # 1. API dan kurs olish
    try:
        response = requests.get(
            "https://cbu.uz/oz/arkhiv-kursov-valyut/json/",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            for item in data:
                if item.get('Ccy') == 'USD':
                    # Rate string holatida keladi, float ga o'tkazamiz
                    rate = float(item.get('Rate', 0))
                    if rate > 0:
                        _save_rate_to_cache(rate)
                        logger.info(f"Yangi kurs olindi: 1$ = {rate:,.2f} so'm")
                        return rate
    except requests.exceptions.RequestException as e:
        logger.warning(f"API dan kurs olishda xatolik: {e}")
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        logger.warning(f"API javobini tahlil qilishda xatolik: {e}")
    
    # 2. Keshdan o'qish
    cached_rate = _get_rate_from_cache()
    if cached_rate:
        logger.info(f"Keshdan kurs olindi: 1$ = {cached_rate:,.2f} so'm")
        return cached_rate
    
    # 3. Agar hech narsa bo'lmasa, DEFAULT (so'nggi ma'lum kurs)
    DEFAULT_RATE = 12118.95  # 2026-07-13 dagi haqiqiy kurs
    logger.warning(f"Default kurs ishlatilmoqda: 1$ = {DEFAULT_RATE:,.2f} so'm")
    return DEFAULT_RATE

def _get_rate_from_cache():
    """Keshdan kursni o'qish (1 soatlik)"""
    try:
        cache_file = "assets/currency_cache.json"
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 1 soat ichida olingan bo'lsa
                if datetime.now().timestamp() - data.get('timestamp', 0) < 3600:
                    return data.get('rate', 0)
                else:
                    logger.info("Kesh eskirgan, yangilash kerak")
    except (json.JSONDecodeError, KeyError, OSError) as e:
        logger.warning(f"Keshni o'qishda xatolik: {e}")
    return None

def _save_rate_to_cache(rate):
    """Kursni keshlash"""
    try:
        os.makedirs("assets", exist_ok=True)
        cache_file = "assets/currency_cache.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({
                'rate': rate,
                'timestamp': datetime.now().timestamp(),
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, f, ensure_ascii=False, indent=2)
        logger.info(f"Kurs keshlandi: {rate:,.2f}")
    except OSError as e:
        logger.warning(f"Keshni saqlashda xatolik: {e}")

def get_currency_display(rate=None):
    """Kursni formatlab ko'rsatish"""
    if rate is None:
        rate = get_usd_rate()
    return f"1$ = {rate:,.2f} so'm"

# Qulaylik uchun: agar bu fayl to'g'ridan-to'g'ri ishga tushirilsa, kursni chiqaradi
if __name__ == "__main__":
    rate = get_usd_rate()
    print(get_currency_display(rate))