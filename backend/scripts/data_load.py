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


NUM_USERS_CLIENTS = 800
NUM_USERS_SELLERS = 150
NUM_USERS_ADMINS = 50
NUM_EQUIPMENT = 1200
NUM_RENTALS = 6000
NUM_PAYMENTS = 5000


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

        self.cur.executemany("""
            INSERT INTO equipment_categories (name, description, parent_id)
            VALUES (%s, %s, %s)
        """, categories)

        self.cur.execute("SELECT id FROM equipment_categories ORDER BY id")
        self.category_ids = [row[0] for row in self.cur.fetchall()]

        self.conn.commit()
        logger.info(f"Добавлено категорий оборудования: {len(categories)}")

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

        self.cur.executemany("""
            INSERT INTO equipment_models (name, brand, rental_price_per_day, deposit_amount, description)
            VALUES (%s, %s, %s, %s, %s)
        """, models)

        self.cur.execute("SELECT id FROM equipment_models ORDER BY id")
        self.model_ids = [row[0] for row in self.cur.fetchall()]

        self.conn.commit()
        logger.info(f"Добавлено моделей оборудования: {len(models)}")

    def fill_users(self):
        users_data = []

        for _ in range(NUM_USERS_CLIENTS):
            name = self.fake.name()
            email = self.fake.unique.email()
            phone = self.fake.phone_number()
            if len(phone) > 25:
                phone = phone[:25]
            users_data.append((name, email, phone, 'Клиент'))

        for i in range(1, NUM_USERS_SELLERS + 1):
            name = f"Продавец {i}"
            email = f"seller{i}@company.com"
            phone = self.fake.phone_number()
            if len(phone) > 25:
                phone = phone[:25]
            users_data.append((name, email, phone, 'Продавец'))

        for i in range(1, NUM_USERS_ADMINS + 1):
            name = f"Админ {i}"
            email = f"admin{i}@company.com"
            phone = self.fake.phone_number()
            if len(phone) > 25:
                phone = phone[:25]
            users_data.append((name, email, phone, 'Админ'))

        self.cur.executemany("""
            INSERT INTO users (name, email, phone, role)
            VALUES (%s, %s, %s, %s)
        """, users_data)

        self.cur.execute("SELECT id, role FROM users ORDER BY id")
        rows = self.cur.fetchall()

        self.client_ids = [row[0] for row in rows if row[1] == 'Клиент']
        self.seller_ids = [row[0] for row in rows if row[1] == 'Продавец']
        self.admin_ids = [row[0] for row in rows if row[1] == 'Админ']

        personal_data = []
        all_user_ids = [row[0] for row in rows]
        for user_id in all_user_ids:
            if random.random() < 0.7:
                personal_data.append((
                    user_id,
                    self.fake.country(),
                    self.fake.city(),
                    self.fake.address(),
                    self.fake.postcode(),
                    self.fake.date_of_birth(minimum_age=18, maximum_age=80)
                ))

        if personal_data:
            self.cur.executemany("""
                INSERT INTO users_personal_data (user_id, country, city, address, postal_code, birth_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, personal_data)

        self.conn.commit()
        total_users = NUM_USERS_CLIENTS + NUM_USERS_SELLERS + NUM_USERS_ADMINS
        logger.info(
            f"Добавлено пользователей: {total_users} (Клиенты: {NUM_USERS_CLIENTS}, Продавцы: {NUM_USERS_SELLERS}, Админы: {NUM_USERS_ADMINS})")

    def fill_equipment(self):
        statuses = ['Доступно'] * 70 + ['В аренде'] * 15 + \
            ['На обслуживании/В ремонте'] * 10 + ['Списано'] * 5
        equipment_data = []

        for i in range(1, NUM_EQUIPMENT + 1):
            category_id = random.choice(self.category_ids)
            model_id = random.choice(self.model_ids)
            inventory_number = f"INV-{i:06d}"
            status = random.choice(statuses)
            equipment_data.append(
                (category_id, model_id, inventory_number, status))

        self.cur.executemany("""
            INSERT INTO equipment (category_id, model_id, inventory_number, status)
            VALUES (%s, %s, %s, %s)
        """, equipment_data)

        self.cur.execute("SELECT id FROM equipment ORDER BY id")
        self.equipment_ids = [row[0] for row in self.cur.fetchall()]

        self.conn.commit()
        logger.info(f"Добавлено единиц оборудования: {NUM_EQUIPMENT}")

    def fill_rentals_and_items(self):
        today = date.today()
        rentals_data = []

        for _ in range(NUM_RENTALS):
            client_id = random.choice(self.client_ids)
            employee_id = random.choice(self.seller_ids)

            start_date = today - timedelta(days=random.randint(0, 730))
            duration = random.randint(3, 30)
            end_date = start_date + timedelta(days=duration)

            return_date = None
            if random.random() < 0.8:
                if random.random() < 0.7:
                    return_date = end_date - \
                        timedelta(days=random.randint(0, 3))
                else:
                    return_date = end_date + \
                        timedelta(days=random.randint(1, 15))

            status_prob = random.random()
            if status_prob < 0.6:
                status = 'Завершён'
            elif status_prob < 0.8:
                status = 'Активен'
            elif status_prob < 0.95:
                status = 'Отменён'
            else:
                status = 'Просрочен срок аренды'

            rentals_data.append(
                (client_id, employee_id, start_date, end_date, return_date, status, None))

        self.cur.executemany("""
            INSERT INTO rentals (user_id, employee_id, start_date, end_date, return_date, status, total_cost)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, rentals_data)

        self.cur.execute(
            "SELECT id FROM rentals ORDER BY id DESC LIMIT %s", (NUM_RENTALS,))

        rental_ids = [row[0] for row in self.cur.fetchall()][::-1]

        rental_items_data = []
        for rental_id in rental_ids:
            num_items = random.randint(1, 4)
            used_in_rental = set()
            for _ in range(num_items):
                available = [
                    eid for eid in self.equipment_ids if eid not in used_in_rental]
                if not available:
                    break
                eq_id = random.choice(available)
                used_in_rental.add(eq_id)

                self.cur.execute("""
                    SELECT rental_price_per_day FROM equipment_models em
                    JOIN equipment e ON em.id = e.model_id
                    WHERE e.id = %s
                """, (eq_id,))
                price_per_day = self.cur.fetchone()[0]

                damage_fee = round(
                    float(price_per_day) * random.uniform(0, 5), 2) if random.random() < 0.1 else 0.0
                rental_items_data.append((rental_id, eq_id, damage_fee))

        if rental_items_data:
            self.cur.executemany("""
                INSERT INTO rental_items (rental_id, equipment_id, damage_fee)
                VALUES (%s, %s, %s)
            """, rental_items_data)

        self.conn.commit()
        logger.info(f"Добавлено аренд: {NUM_RENTALS}")

    def fill_payments(self):
        self.cur.execute(f"""
            SELECT id FROM rentals
            WHERE status = 'Завершён'
            ORDER BY RANDOM()
            LIMIT {NUM_PAYMENTS}
        """)
        rental_ids = [row[0] for row in self.cur.fetchall()]

        methods = ['Наличные', 'Банковской картой', 'Перевод СБП']
        payments_data = []

        for rental_id in rental_ids:
            self.cur.execute(
                "SELECT start_date FROM rentals WHERE id = %s", (rental_id,))
            start_date = self.cur.fetchone()[0]
            method = random.choice(methods)
            payment_date = start_date + timedelta(days=random.randint(0, 5))
            payments_data.append((rental_id, method, payment_date))

        if payments_data:
            self.cur.executemany("""
                INSERT INTO payments (rental_id, payment_method, payment_date)
                VALUES (%s, %s, %s)
            """, payments_data)

        self.conn.commit()
        logger.info(
            f"Добавлено платежей: {len(payments_data)} (планировалось {NUM_PAYMENTS})")

    def fill_damages_and_repairs(self):

        self.cur.execute("""
            SELECT equipment_id, rental_id FROM rental_items
            WHERE damage_fee > 0
            ORDER BY RANDOM()
            LIMIT 1000
        """)
        damage_rows = self.cur.fetchall()

        damages_data = []
        descriptions_damage = ['Царапины на корпусе', 'Поломка крепления',
                               'Потертости и сколы', 'Незначительные деформации', 'Загрязнение']
        for eq_id, rental_id in damage_rows:
            desc = random.choice(descriptions_damage)
            damages_data.append((eq_id, rental_id, desc))

        if damages_data:
            self.cur.executemany("""
                INSERT INTO damages (equipment_id, rental_id, description)
                VALUES (%s, %s, %s)
            """, damages_data)

        self.cur.execute("""
            SELECT id FROM equipment
            ORDER BY RANDOM()
            LIMIT 300
        """)
        repair_eq_ids = [row[0] for row in self.cur.fetchall()]

        repairs_data = []
        descriptions_repair = ['Замена подшипников', 'Ремонт электроники',
                               'Замена щеток', 'Техническое обслуживание', 'Косметический ремонт']
        statuses_repair = ['Завершён'] * 4 + ['В процессе'] * \
            3 + ['Запланирован'] * 2 + ['Отменён'] * 1

        for eq_id in repair_eq_ids:
            start_date = date.today() - timedelta(days=random.randint(0, 365))
            end_date = start_date + \
                timedelta(days=random.randint(1, 14)
                          ) if random.random() < 0.7 else None
            desc = random.choice(descriptions_repair)
            cost = round(500 + random.random() * 4500, 2)
            status = random.choice(statuses_repair)
            repairs_data.append(
                (eq_id, start_date, end_date, desc, cost, status))

        if repairs_data:
            self.cur.executemany("""
                INSERT INTO repairs (equipment_id, start_date, end_date, description, cost, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, repairs_data)

        self.conn.commit()
        logger.info("Добавлена информация о повреждениях и ремонтах")

    def update_equipment_status(self):
        self.cur.execute("""
            UPDATE equipment e
            SET status = 'В аренде'
            WHERE EXISTS (
                SELECT 1 FROM rental_items ri
                JOIN rentals r ON ri.rental_id = r.id
                WHERE ri.equipment_id = e.id
                  AND r.status IN ('Активен', 'Просрочен срок аренды')
            )
        """)

        self.cur.execute("""
            UPDATE equipment e
            SET status = 'На обслуживании/В ремонте'
            WHERE EXISTS (
                SELECT 1 FROM repairs rep
                WHERE rep.equipment_id = e.id
                  AND rep.status IN ('Запланирован', 'В процессе')
            )
        """)

        self.cur.execute("""
            UPDATE equipment e
            SET status = 'Доступно'
            WHERE e.status NOT IN ('В аренде', 'На обслуживании/В ремонте', 'Списано')
        """)

        self.conn.commit()
        logger.info("Статусы оборудования обновлены")

    def fill_all(self):
        logger.info("Начало заполнения базы данных")
        self.fill_equipment_categories()
        self.fill_equipment_models()
        self.fill_users()
        self.fill_equipment()
        self.fill_rentals_and_items()
        self.fill_payments()
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
        logger.info("Скрипт завершён успешно")
    except Exception as e:
        logger.error(f"Ошибка при заполнении: {e}", exc_info=True)
        if filler.conn:
            filler.conn.rollback()
    finally:
        filler.close()
