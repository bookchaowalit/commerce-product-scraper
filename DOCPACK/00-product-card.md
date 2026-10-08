---
title: Book Ecommerce Scraping — Product Card
doc_id: CARD-book-ecommerce-scraping
doc_type: product-card
verdict: archive
version: 0.1
date: 2026-10-08
status: ร่างเพื่อพิจารณา
owner: Product owner (Book Dev)
---

# Book Ecommerce Scraping — Product Card

## 1. สรุปคุณค่าในหนึ่งประโยค

เก็บประกาศขายสาธารณะจาก Kaidee (สูงสุด 5 หน้า / 200 แถวต่อรอบ) ลง CSV ในเครื่อง — ยังไม่มีใครหรือระบบใดใช้ข้อมูลนี้

## 2. ปัญหาและผู้ใช้เป้าหมาย

- ปัญหาที่ตั้งใจ: ติดตามราคาสินค้ามือสองในตลาดไทย
- ผู้ใช้: ไม่ระบุใน repo **[ต้องยืนยัน]**

## 3. สิ่งที่ทำได้จริงตอนนี้

- `scripts/run_marketplace.py` → `ecommerce/kaidee_scraper.py` (collector เดียว)
- HTTP แบบสุภาพ: User-Agent ระบุตัว, timeout 30 s, retry เฉพาะ 429/5xx, เขียนไฟล์ atomic
- scraper Shopee/Lazada เดิมถูกลบในรอบ 2026-09 เพราะไม่ใช่ของจริงและรันไม่ได้
- cron ทุก 6 ชั่วโมงแบบ optional; ไม่มี lake ingest หรือ API

## 4. หลักฐานสถานะ

| รายการ | ค่า (ตรวจจาก repository) |
|---|---|
| Stack | Python |
| Commits | 17 (แรก 2026-07-09 → ล่าสุด 2026-10-01) |
| Source | 10 ไฟล์ / 1,111 บรรทัด |
| Tests | 6 ไฟล์ |
| CI | 1 workflow |
| Deploy config | ไม่มี |
| Live URL | ไม่มี |
| README | 87 บรรทัด (`book-ecommerce-scraping`) |
| โครงสร้างซ้ำ (template family) | 1 repo ที่มี structure signature เดียวกัน |

## 5. คุณค่าและจุดต่าง

- โค้ดเป็นระเบียบ มี test และเป็นตัวอย่าง polite scraping แต่รูปแบบเดียวกันมีอยู่แล้วใน `book-restaurant-scraping` และ `book-news-scraping`
- ไม่มีมุมรายได้ที่มีหลักฐาน

## 6. ช่องว่างสำคัญ

- แหล่งเดียว, ไม่มี consumer, ไม่มี data contract/lake
- การ scrape marketplace มีความเสี่ยงด้าน ToS **[ต้องยืนยัน]**

## 7. คำตัดสิน

**`archive`** — ไม่มีผู้ใช้ ไม่มี consumer และไม่มีจุดต่างจาก repo scraping อื่น จึงเสนอ archive หลังเจ้าของอนุมัติ จะมีค่าก็ต่อเมื่อมีคำถามธุรกิจชัด (เช่น ตั้งราคาขายของมือสอง) และมี consumer อ่านข้อมูลเป็นประจำ

## 8. ขั้นต่อไป

1. ยืนยันว่าไม่มี cron/ระบบใดอ่าน `data/exported/` ของ repo นี้
2. archive หลังอนุมัติ

## การอนุมัติ

| บทบาท | สถานะ | วันที่ | ลงนาม |
|---|---|---|---|
| Product owner (Book Dev) | รอพิจารณา | — | ________ |

## แหล่งข้อมูล

- `README.md`
- `PRODUCT.md`
- `ecommerce/kaidee_scraper.py`
- `ecommerce/http.py`
