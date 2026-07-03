import asyncio
import aiosqlite
from database import Database

TEST_PHONES = [
    # Apple
    ('iPhone 15 Pro Max', 'Apple', '1400 USD', '256GB', '8GB', '48MP', '4441 mAh', 'available'),
    ('iPhone 15', 'Apple', '850 USD', '128GB', '6GB', '48MP', '3349 mAh', 'available'),
    ('iPhone 13', 'Apple', '650 USD', '128GB', '4GB', '12MP', '3227 mAh', 'available'),
    
    # Samsung
    ('Galaxy S24 Ultra', 'Samsung', '1300 USD', '512GB', '12GB', '200MP', '5000 mAh', 'available'),
    ('Galaxy A55 5G', 'Samsung', '420 USD', '128GB', '8GB', '50MP', '5000 mAh', 'available'),
    ('Galaxy A15', 'Samsung', '180 USD', '128GB', '4GB', '50MP', '5000 mAh', 'available'),
    
    # Xiaomi / Poco
    ('Xiaomi 14 Ultra', 'Xiaomi', '1100 USD', '512GB', '16GB', '50MP', '5000 mAh', 'available'),
    ('Redmi Note 13 Pro 5G', 'Xiaomi', '320 USD', '256GB', '8GB', '200MP', '5100 mAh', 'available'),
    ('Poco X6 Pro', 'Xiaomi', '350 USD', '256GB', '8GB', '64MP', '5000 mAh', 'available'),
    
    # Honor & Realme
    ('Honor 200 Pro', 'Honor', '600 USD', '512GB', '12GB', '50MP', '5200 mAh', 'available'),
    ('Realme GT 6', 'Realme', '550 USD', '256GB', '12GB', '50MP', '5500 mAh', 'available')
]

async def seed_database():
    db_manager = Database()
    
    await db_manager.create_tables()
    
    print("Bazaga ma'lumotlar yozilmoqda...")
    
    async with aiosqlite.connect(db_manager.db_path) as db:
        await db.execute("DELETE FROM smartphones")
        
        await db.executemany("""
            INSERT INTO smartphones (model, brand, price, storage, ram, camera, battery, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, TEST_PHONES)
        
        await db.commit()
        
    print(f"Muvaffaqiyatli yakunlandi! {len(TEST_PHONES)} ta telefon bazaga qo'shildi.")

if __name__ == "__main__":
    asyncio.run(seed_database())