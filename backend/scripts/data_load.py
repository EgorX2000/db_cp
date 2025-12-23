import psycopg2
from faker import Faker
import random
from datetime import timedelta, date
import time
import logging
import os
import sys
from urllib.parse import urlparse
from dotenv import load_dotenv
from pathlib import Path


LOG_DIR = Path("./app/logs")
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "data_load.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class DatabaseFiller:
    def __init__(self, db_config):
        self.fake = Faker('ru_RU')
        self.db_config = db_config
        self.conn = None
        self.cur = None
        self.category_ids = []
        self.model_ids = []
        self.client_ids = []
        self.seller_ids = []
        self.admin_ids = []
        self.equipment_ids = []

    def connect(self):
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.conn.autocommit = False
            self.cur = self.conn.cursor()
            logger.info("Успешное подключение к БД")
        except Exception as e:
            logger.error(f"Ошибка подключения: {e}", exc_info=True)
            raise

    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        logger.info("Соединение с БД закрыто")

    def fill_equipment_categories(self):
        categories = [
            ('Электроинструменты', 'Аккумуляторные и сетевые электроинструменты', None),
            ('Строительное оборудование', 'Оборудование для строительных работ', None),
            ('Садовый инвентарь', 'Инструменты для работы в саду и на участке', None),
            ('Автоинструмент', 'Инструменты для ремонта автомобилей', None),
            ('Генераторы и компрессоры', 'Источники питания и сжатого воздуха', None),
            ('Дрели и шуруповерты',
             'Аккумуляторные и сетевые дрели, шуруповерты, перфораторы', 1),
            ('Шлифовальные машины',
             'УШМ (болгарки), ленточные и эксцентриковые шлифмашины', 1),
            ('Пилы', 'Циркулярные, сабельные, торцовочные пилы', 1),
            ('Бетономешалки', 'Оборудование для приготовления бетонных смесей', 2),
            ('Строительные пылесосы', 'Промышленные пылесосы для строительства', 2),
            ('Леса и подмости', 'Строительные леса, подмости, вышки-туры', 2),
            ('Газонокосилки', 'Бензиновые и электрические газонокосилки', 3),
            ('Культиваторы', 'Мотокультиваторы и мотоблоки', 3),
            ('Садовые измельчители', 'Измельчители веток и садового мусора', 3),
        ]

        for name, desc, parent_id in categories:
            self.cur.execute("""
                INSERT INTO equipment_categories (name, description, parent_id)
                VALUES (%s, %s, %s) RETURNING id
            """, (name, desc, parent_id))
            cat_id = self.cur.fetchone()[0]
            self.category_ids.append(cat_id)

        self.conn.commit()
        logger.info(f"Добавлено {len(categories)} категорий оборудования")

    def fill_equipment_models(self):
        models = [
            ('DCD 796 D2', 'DeWalt', 350.00, 5000.00,
             'Аккумуляторная дрель-шуруповерт 18В, 2 скорости, быстрозажимной патрон'),
            ('GBH 2-26 DFR', 'Bosch', 550.00, 8000.00,
             'Перфоратор SDS-plus, 800 Вт, энергия удара 2.7 Дж'),
            ('WSG 14-125', 'Makita', 400.00, 6000.00,
             'Угловая шлифмашина 125мм, 1400 Вт, регулировка оборотов'),
            ('TS 55 REQ', 'Festool', 1200.00, 15000.00,
             'Циркулярная пила с направляющей, 1200 Вт, глубина пропила 55мм'),
            ('KM 55 R', 'Stihl', 800.00, 10000.00,
             'Бензиновый культиватор, ширина обработки 55 см, 4.5 л.с.'),
            ('CGW 100', 'Einhell', 1200.00, 15000.00,
             'Бетономешалка 100л, электропривод 550 Вт'),
            ('L Class 26', 'Karcher', 650.00, 9000.00,
             'Строительный пылесос 26л, 1300 Вт, автоматическая очистка фильтра'),
            ('Twin Tub', 'Briggs & Stratton', 900.00, 12000.00,
             'Газонокосилка бензиновая, ширина скашивания 48 см, 4.5 л.с.'),
            ('WG 280 E', 'Stihl', 450.00, 7000.00,
             'Садовый измельчитель, режущая система ножей, 2800 Вт'),
            ('PROM 65-180', 'Fubag', 1500.00, 20000.00,
             'Бензиновый генератор 6.5 кВт, 4-тактный, AVR'),
            ('Impact Wrench 1/2"', 'Ingersoll Rand', 750.00,
             10000.00, 'Пневматический гайковерт 1/2 дюйма, 900 Нм'),
            ('Air Compressor 50L', 'ABAC', 850.00, 12000.00,
             'Воздушный компрессор 50л, 2.2 кВт, 8 бар'),
            ('Ladder 3-section', 'Krause', 150.00, 3000.00,
             'Трехсекционная лестница алюминиевая, высота 6.5 м'),
            ('Telescopic Tower', 'Youngman', 800.00, 15000.00,
             'Вышка-тура алюминиевая 2.0x0.75м, высота до 12м'),
            ('Tile Cutter 600', 'Rubi', 400.00, 6000.00,
             'Плиткорез напольный, длина реза 600мм, алмазное колесо'),
        ]

        for name, brand, price, deposit, desc in models:
            self.cur.execute("""
                INSERT INTO equipment_models (name, brand, rental_price_per_day, deposit_amount, description)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            """, (name, brand, price, deposit, desc))
            model_id = self.cur.fetchone()[0]
            self.model_ids.append(model_id)

        self.conn.commit()
        logger.info(f"Добавлено {len(models)} моделей оборудования")

    def fill_users(self):
        roles = [
            ('Клиент', 800, self.client_ids),
            ('Продавец', 150, self.seller_ids),
            ('Админ', 50, self.admin_ids)
        ]

        for role, count, id_list in roles:
            for i in range(1, count + 1):
                name = f"{role} {i}" if role in [
                    'Продавец', 'Админ'] else self.fake.name()
                email_domain = 'mail.com' if role == 'Клиент' else 'company.com'
                email = f"{role.lower()}{i}@{email_domain}".replace(' ', '')
                phone = self.fake.phone_number()
                if len(phone) > 20:
                    phone = '+7' + ''.join(filter(str.isdigit, phone))[-10:]

                self.cur.execute("""
                    INSERT INTO users (name, email, phone, role)
                    VALUES (%s, %s, %s, %s) RETURNING id
                """, (name, email, phone, role))
                user_id = self.cur.fetchone()[0]
                id_list.append(user_id)

                if random.random() < 0.7:
                    self.cur.execute("""
                        INSERT INTO users_personal_data (user_id, country, city, address, postal_code, birth_date)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        user_id,
                        self.fake.country(),
                        self.fake.city(),
                        self.fake.address(),
                        self.fake.postcode(),
                        self.fake.date_of_birth(minimum_age=18, maximum_age=80)
                    ))

            logger.info(f"Добавлено {count} пользователей с ролью '{role}'")

        self.conn.commit()

    def fill_equipment(self, count=1200):
        statuses = ['Доступно'] * 70 + ['В аренде'] * 15 + \
            ['На обслуживании/В ремонте'] * 10 + ['Списано'] * 5

        for i in range(1, count + 1):
            category_id = random.choice(self.category_ids)
            model_id = random.choice(self.model_ids)
            inventory_number = f"INV-{i:06d}"
            status = random.choice(statuses)

            self.cur.execute("""
                INSERT INTO equipment (category_id, model_id, inventory_number, status)
                VALUES (%s, %s, %s, %s) RETURNING id
            """, (category_id, model_id, inventory_number, status))
            eq_id = self.cur.fetchone()[0]
            self.equipment_ids.append(eq_id)

        self.conn.commit()
        logger.info(f"Добавлено {count} единиц оборудования")

    def fill_rentals_and_items(self, rental_count=6000):
        active_statuses = ['Активен', 'Завершён', 'Просрочен срок аренды']
        today = date.today()

        for _ in range(rental_count):
            client_id = random.choice(self.client_ids)
            employee_id = random.choice(self.seller_ids)

            start_date = today - timedelta(days=random.randint(0, 730))
            duration = random.randint(3, 30)
            end_date = start_date + timedelta(days=duration)

            return_date = None
            if random.random() < 0.8:
                if random.random() < 0.7:
                    early_days = random.randint(0, 3)
                    return_date = end_date - timedelta(days=early_days)
                else:
                    late_days = random.randint(1, 15)
                    return_date = end_date + timedelta(days=late_days)

            status_prob = random.random()
            if status_prob < 0.6:
                status = 'Завершён'
            elif status_prob < 0.8:
                status = 'Активен'
            elif status_prob < 0.95:
                status = 'Отменён'
            else:
                status = 'Просрочен срок аренды'

            self.cur.execute("""
                INSERT INTO rentals (user_id, employee_id, start_date, end_date, return_date, status)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
            """, (client_id, employee_id, start_date, end_date, return_date, status))
            rental_id = self.cur.fetchone()[0]

            num_items = random.randint(1, 4)
            used_equipment = set()

            available_equipment = [
                eid for eid in self.equipment_ids if eid not in used_equipment]

            for _ in range(num_items):
                if not available_equipment:
                    break
                eq_id = random.choice(available_equipment)
                used_equipment.add(eq_id)
                available_equipment.remove(eq_id)

                self.cur.execute("""
                    SELECT rental_price_per_day FROM equipment_models em
                    JOIN equipment e ON em.id = e.model_id
                    WHERE e.id = %s
                """, (eq_id,))
                price_per_day = self.cur.fetchone()[0]

                damage_fee = float(price_per_day) * \
                    random.uniform(0, 5) if random.random() < 0.1 else 0.0

                self.cur.execute("""
                    INSERT INTO rental_items (rental_id, equipment_id, damage_fee)
                    VALUES (%s, %s, %s)
                """, (rental_id, eq_id, round(damage_fee, 2)))

        self.conn.commit()
        logger.info(f"Добавлено {rental_count} аренд и элементов аренды")

    def fill_payments(self, count=5000):
        self.cur.execute("""
            SELECT r.id FROM rentals r
            WHERE r.status = 'Завершён'
              AND EXISTS (SELECT 1 FROM rental_items ri WHERE ri.rental_id = r.id)
            ORDER BY random()
            LIMIT %s
        """, (count,))
        rental_ids = [row[0] for row in self.cur.fetchall()]

        methods = ['Наличные', 'Банковской картой', 'Перевод СБП']

        for rental_id in rental_ids:
            self.cur.execute(
                "SELECT start_date FROM rentals WHERE id = %s", (rental_id,))
            start_date = self.cur.fetchone()[0]

            method = random.choice(methods)
            payment_date = start_date + timedelta(days=random.randint(0, 5))

            self.cur.execute("""
                INSERT INTO payments (rental_id, payment_method, payment_date)
                VALUES (%s,  %s, %s)
            """, (rental_id, method, payment_date))

        self.conn.commit()
        logger.info(f"Добавлено {len(rental_ids)} платежей")

    def fill_damages_and_repairs(self):
        self.cur.execute("""
            SELECT ri.equipment_id, ri.rental_id FROM rental_items ri
            WHERE ri.damage_fee > 0 AND random() < 0.3
            ORDER BY random() LIMIT 1000
        """)
        damage_rows = self.cur.fetchall()

        descriptions = [
            'Царапины на корпусе', 'Поломка крепления', 'Потертости и сколы',
            'Незначительные деформации', 'Загрязнение, требующее чистки', 'Мелкие технические неисправности'
        ]

        for eq_id, rental_id in damage_rows:
            desc = random.choice(descriptions)
            self.cur.execute("""
                INSERT INTO damages (equipment_id, rental_id, description)
                VALUES (%s, %s, %s)
            """, (eq_id, rental_id, desc))

        self.cur.execute("""
            SELECT id FROM equipment
            WHERE status IN ('На обслуживании/В ремонте', 'Списано') OR random() < 0.1
            ORDER BY random() LIMIT 300
        """)
        repair_eq_ids = [row[0] for row in self.cur.fetchall()]

        repair_desc = ['Замена подшипников', 'Ремонт электроники',
                       'Замена щеток', 'Техническое обслуживание', 'Косметический ремонт']
        statuses = ['Завершён'] * 4 + ['В процессе'] * \
            3 + ['Запланирован'] * 2 + ['Отменён'] * 1

        for eq_id in repair_eq_ids:
            start_date = date.today() - timedelta(days=random.randint(0, 365))
            end_date = start_date + \
                timedelta(days=random.randint(1, 14)
                          ) if random.random() < 0.7 else None
            desc = random.choice(repair_desc)
            cost = round(500 + random.random() * 4500, 2)
            status = random.choice(statuses)

            self.cur.execute("""
                INSERT INTO repairs (equipment_id, start_date, end_date, description, cost, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (eq_id, start_date, end_date, desc, cost, status))

        self.conn.commit()
        logger.info("Добавлены повреждения и ремонты")

    def update_equipment_status(self):
        self.cur.execute("""
            UPDATE equipment e
            SET status = 'В аренде'
            WHERE e.id IN (
                SELECT DISTINCT ri.equipment_id
                FROM rental_items ri
                JOIN rentals r ON ri.rental_id = r.id
                WHERE r.status IN ('Активен', 'Просрочен срок аренды')
            )
        """)

        self.cur.execute("""
            UPDATE equipment e
            SET status = 'На обслуживании/В ремонте'
            WHERE e.id IN (
                SELECT DISTINCT equipment_id
                FROM repairs
                WHERE status IN ('Запланирован', 'В процессе')
            )
        """)

        self.cur.execute("""
            UPDATE equipment e
            SET status = 'Доступно'
            WHERE e.status = 'В аренде'
              AND e.id NOT IN (
                  SELECT DISTINCT ri.equipment_id
                  FROM rental_items ri
                  JOIN rentals r ON ri.rental_id = r.id
                  WHERE r.status IN ('Активен', 'Просрочен срок аренды')
              )
              AND e.id NOT IN (
                  SELECT DISTINCT equipment_id FROM repairs
                  WHERE status IN ('Запланирован', 'В процессе')
              )
        """)

        self.conn.commit()
        logger.info("Статусы оборудования обновлены")

    def fill_all(self):
        self.fill_equipment_categories()
        self.fill_equipment_models()
        self.fill_users()
        self.fill_equipment(1200)
        self.fill_rentals_and_items(6000)
        self.fill_payments(5000)
        self.fill_damages_and_repairs()
        self.update_equipment_status()
        logger.info("Заполнение базы данных завершено успешно!")


if __name__ == "__main__":
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL не задан!")

    parsed = urlparse(DATABASE_URL)
    db_config = {
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'database': parsed.path[1:],
        'user': parsed.username,
        'password': parsed.password
    }

    filler = DatabaseFiller(db_config)
    for i in range(20):
        try:
            filler.connect()
            logger.info("Подключение к БД успешно!")
            break
        except Exception as e:
            logger.error(f"Ждём поднятия БД... ({i+1}/20)", exc_info=True)
            time.sleep(3)
    else:
        raise Exception("Не удалось подключиться к базе данных")

    try:
        filler.fill_all()
        logger.info("Заполнение базы завершено!")
    except Exception as e:
        logger.error(f"Ошибка при заполнении: {e}", exc_info=True)
        if filler.conn:
            filler.conn.rollback()
    finally:
        filler.close()
