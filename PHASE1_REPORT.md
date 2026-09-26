# گزارش Phase 1: تایید و بررسی ساختار داده‌ها

## خلاصه پروژه

**عنوان پروژه:** شناسایی اکانت‌های اسپم در شبکه‌های اجتماعی با استفاده از Machine Learning تفسیرپذیر (SHAP)

**هدف:** ایجاد یک پوتکال یادگیری ماشینی چند مدالیتی (multimodal) برای شناسایی اکانت‌های اسپم و ارائه توضیح‌های قابل‌فهم برای تصمیمات مدل.

---

## معماری پروژه

### سه لایه اصلی:

```
داده Cresci-2017
        ↓
┌─────────────────────────────────────┐
│ Phase 1: تایید و بررسی ساختار    │ ← شما اینجا هستید
│ - کشف فایل‌ها                     │
│ - تشخیص ستون‌ها                   │
│ - بررسی برچسب‌ها                  │
└─────────────────────────────────────┘
        ↓
┌─────────────────────────────────────┐
│ Phase 2-8: استخراج ویژگی‌ها      │
│ - ویژگی‌های رفتاری               │
│ - بردار متنی (BERT)              │
│ - نمایش گراف (GraphSAGE/GAT)      │
└─────────────────────────────────────┘
        ↓
┌─────────────────────────────────────┐
│ Phase 9-11: تفسیرپذیری و ارزیابی  │
│ - TreeSHAP                         │
│ - ابلیشن‌های                     │
│ - اندازه‌گیری کیفیت توضیح         │
└─────────────────────────────────────┘
```

---

## Phase 1: توضیح کد

### فایل‌های اصلی:

#### 1. **`src/data/validator.py`** - تایید ساختار داده
```python
class DatasetValidator:
    - discover_files()          # پیدا کردن فایل‌های CSV/JSON
    - inspect_csv()             # خواندن ساختار CSV
    - inspect_json()            # خواندن ساختار JSON
    - detect_schema()           # تشخیص ستون‌های مهم
    - check_missing_values()    # بررسی مقادیر خالی
    - check_duplicates()        # بررسی آی‌دی‌های تکراری
    - validate()                # بررسی نهایی
```

**کار:** این کلاس به صورت خودکار:
- فایل‌های داده را در پوشه `data/raw/cresci2017/` پیدا می‌کند
- ستون‌های account_id، tweet_id، text، timestamp، label را تشخیص می‌دهد
- مقادیر خالی و تکراری را برای کنترل کیفیت بررسی می‌کند

#### 2. **`src/data/label_mapper.py`** - نقشه‌برداری برچسب‌ها
```python
class LabelMapper:
    genuine_accounts      → 0  (اکانت‌های اصلی)
    traditional_spambots  → 1  (اسپم‌بات‌های سنتی)
    social_spambots       → 1  (اسپم‌بات‌های اجتماعی)
    fake_followers        → exclude  (حذف شده)
```

**کار:** تمام دسته‌بندی‌ها را به یک برچسب دودویی تبدیل می‌کند و تعداد هر کلاس را گزارش می‌دهد.

#### 3. **`scripts/01_validate_data.py`** - نقطه ورود اصلی
```python
def main():
    1. بارگذاری config.yaml
    2. ایجاد logger
    3. اجرای validator روی داده
    4. ذخیره گزارش در JSON
```

---

## نحوه اجرا

### مرحله 1: نصب وابستگی‌ها
```bash
pip install -r requirements.txt
```

### مرحله 2: ایجاد داده نمونه (برای تست)
```bash
python scripts/create_sample_data.py
```

**خروجی:**
```
✓ Created: data/raw/cresci2017/genuine_accounts/users.csv
✓ Created: data/raw/cresci2017/traditional_spambots_1/users.csv
✓ Created: data/raw/cresci2017/social_spambots_1/users.csv
✓ Created: data/raw/cresci2017/fake_followers/users.csv

Sample data created successfully!
Total accounts: 9
  - Genuine: 3
  - Traditional spambots: 2
  - Social spambots: 2
  - Fake followers: 2 (will be excluded)
```

### مرحله 3: اجرای Phase 1
```bash
python scripts/01_validate_data.py
```

**خروجی (مثال):**
```
2026-09-26 22:45:26,600 - spam_xai - INFO - ============================================================
2026-09-26 22:45:26,607 - spam_xai - INFO - PHASE 1: DATASET VALIDATION
============================================================

Discovered files:
  - genuine_accounts/users.csv
  - traditional_spambots_1/users.csv
  - social_spambots_1/users.csv
  - fake_followers/users.csv

Detected candidate columns:
  account_id candidates: ['user_id']
  tweet_id candidates: []
  text candidates: ['text']
  timestamp candidates: ['created_at']
  label candidates: []

SELECTED SCHEMA
  Account ID: user_id
  Tweet ID: None
  Text: text
  Timestamp: created_at
  Label: None

Label summary:
  genuine accounts: 3
  spam accounts: 4
  excluded accounts: 2
  class ratio: 0.57

✓ Phase 1 completed successfully!
```

### مرحله 4: مشاهده گزارش
```bash
cat data/interim/schema_report.json
```

---

## خروجی Phase 1

فایل `data/interim/schema_report.json` شامل:

```json
{
  "status": "success",
  "schema": {
    "account_id_column": "user_id",
    "tweet_id_column": null,
    "text_column": "text",
    "timestamp_column": "created_at",
    "label_column": null,
    "profile_columns": ["followers_count", "statuses_count", "verified"],
    "files_found": 4,
    "duplicate_account_ids": 0,
    "duplicate_tweet_ids": 0,
    "detected_categories": {
      "genuine": 3,
      "traditional_spambots": 2,
      "social_spambots": 2,
      "fake_followers": 2
    }
  },
  "missing_values": {},
  "category_distribution": {...}
}
```

---

## اصول تحقیقی Phase 1

### 1. **عدم فرض پیشین (No Assumptions)**
- کد از قبل فرض نمی‌کند که ستون‌ها کدام هستند
- داده را بررسی می‌کند و خود ستون‌ها را کشف می‌کند

### 2. **کنترل کیفیت (Quality Checks)**
- تکراری‌ها را شناسایی می‌کند
- مقادیر خالی را گزارش می‌کند
- توزیع کلاس را نمایش می‌دهد

### 3. **انتقال واضح (Clear Reporting)**
- اگر یک فیلد مورد نیاز پیدا نشود، پیام خطا واضحی ارائه می‌دهد
- هرگز بدون اطلاع ادامه نمی‌دهد

### 4. **Reproducibility**
- تمام seed‌ها قابل‌تنظیم هستند
- تمام مسیر‌ها از `config.yaml` می‌آیند
- نتایج قابل تکرار هستند

---

## ساختار دایرکتوری

```
spam-xai-research/
├── configs/
│   └── config.yaml                    # تنظیمات پروژه
├── data/
│   ├── raw/
│   │   └── cresci2017/               # داده خام
│   ├── interim/
│   │   └── schema_report.json         # خروجی Phase 1
│   └── processed/                     # برای فاز‌های بعدی
├── src/
│   ├── data/
│   │   ├── validator.py              # کشف ساختار
│   │   └── label_mapper.py           # نقشه برچسب
│   └── utils/
│       ├── config.py                 # بارگذاری config
│       └── logging.py                # ثبت‌گیری
├── scripts/
│   ├── create_sample_data.py         # ایجاد داده نمونه
│   └── 01_validate_data.py           # اجرای Phase 1
├── tests/                             # تست‌های واحد
├── outputs/                           # نتایج و گزارش‌ها
├── requirements.txt                   # وابستگی‌ها
└── README.md                          # مستندات
```

---

## نتایج Phase 1

✅ **مکمل شده:**
- [x] کشف فایل‌های داده
- [x] بررسی ساختار CSV/JSON
- [x] تشخیص ستون‌های مهم
- [x] نقشه‌برداری برچسب‌ها
- [x] بررسی کیفیت (تکراری، خالی)
- [x] تولید گزارش JSON

📋 **فاز‌های بعدی:**
- [ ] Phase 2: تجمیع سطح اکانت (Account-level aggregation)
- [ ] Phase 3: استخراج ویژگی‌های رفتاری
- [ ] Phase 4: بردارهای متنی (BERT)
- [ ] Phase 5-8: مدل‌های فوژن (Fusion)
- [ ] Phase 9-11: تفسیرپذیری (SHAP) و ارزیابی

---

## نکات مهم

### برای داده واقعی:
1. داده Cresci-2017 از https://mib.projects.iit.cnr.it/dataset.html درخواست کنید
2. فایل‌های ZIP را در `data/raw/cresci2017/` استخراج کنید
3. دستور `python scripts/01_validate_data.py` را اجرا کنید
4. کد خودکار ساختار را تشخیص می‌دهد

### برای داده نمونه (تست):
1. `python scripts/create_sample_data.py` را اجرا کنید
2. داده‌های ساختگی در `data/raw/cresci2017/` ایجاد می‌شود
3. Phase 1 را اجرا کنید

---

## مراجع

- **Cresci et al. (2017):** "The Paradigm-Shift of Social Spambots" - WWW '17 Companion
- **MIB Datasets:** https://mib.projects.iit.cnr.it/dataset.html
- **Repository:** https://github.com/raaees/spam-xai-research

---

## نتیجه‌گیری

Phase 1 یک بنیاد محکم برای پروژه فراهم می‌کند:
- **تایید شده:** ساختار داده واضح و معتبر است
- **اسناد‌شده:** تمام فرآیند گزارش می‌شود
- **تکرارپذیر:** کد همیشه یکی نتیجه می‌دهد
- **آماده برای بعد:** داده برای Phase 2 آماده است

