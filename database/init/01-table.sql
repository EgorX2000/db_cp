create table users (
    id serial primary key,
    name varchar(100) not null,
    email varchar(100) unique not null,
    phone varchar(25),
    role varchar(25) not null check (role in ('Клиент', 'Продавец', 'Админ'))
);

create table equipment_categories (
    id serial primary key,
    name varchar(100) not null,
    description text,
    parent_id int default null,
    created_at timestamp default current_timestamp,
    foreign key (parent_id) references equipment_categories(id) on update cascade on delete set null
);

create table equipment_models (
    id serial primary key,
    name varchar(100) not null,
    description text,
    brand varchar(100),
    rental_price_per_day decimal(10, 2) not null check (rental_price_per_day >= 0),
    deposit_amount decimal(10, 2) default 0 check (deposit_amount >= 0)
);

create table equipment (
    id serial primary key,
    category_id int not null,
    model_id int not null,
    inventory_number varchar(50) unique not null,
    status varchar(25) not null default 'Доступно' 
        check (status in ('Доступно', 'В аренде', 'На обслуживании/В ремонте', 'Списано')),
    foreign key (category_id) references equipment_categories(id) on update cascade on delete restrict,
    foreign key (model_id) references equipment_models(id) on update cascade on delete restrict
);

create table rentals (
    id serial primary key,
    user_id int not null,
    employee_id int not null,
    start_date date not null,
    end_date date not null,
    check (end_date >= start_date),
    return_date date default null,
    check (return_date >= start_date or return_date is null),
    status varchar(25) not null default 'Активен' 
        check (status in ('Активен', 'Завершён', 'Отменён', 'Просрочен срок аренды')),
    total_cost decimal(10, 2) check (total_cost >= 0),
    created_at timestamp default current_timestamp,
    updated_at timestamp default current_timestamp,
    foreign key (user_id) references users(id) on update cascade on delete restrict,
    foreign key (employee_id) references users(id) on update cascade on delete restrict
);

create table rental_items (
    id serial primary key,
    rental_id int not null,
    equipment_id int not null,
    damage_fee decimal(10, 2) default 0 check (damage_fee >= 0),
    created_at timestamp default current_timestamp,
    foreign key (rental_id) references rentals(id) on update cascade on delete cascade,
    foreign key (equipment_id) references equipment(id) on update cascade on delete restrict,
    unique (rental_id, equipment_id) 
);

create table payments (
    id serial primary key,
    rental_id int not null,
    amount decimal(10, 2) not null check (amount > 0),
    payment_method varchar(25) not null check (payment_method in ('Наличные', 'Банковской картой', 'Перевод СБП')),
    payment_date timestamp default current_timestamp,
    foreign key (rental_id) references rentals(id) on update cascade on delete cascade
);

create table damages (
    id serial primary key,
    equipment_id int not null,
    rental_id int not null,
    description text not null,
    created_at timestamp default current_timestamp,
    foreign key (equipment_id) references equipment(id) on update cascade on delete restrict,
    foreign key (rental_id) references rentals(id) on update cascade on delete cascade
);

create table repairs (
    id serial primary key,
    equipment_id int not null,
    start_date date not null,
    end_date date,
    description text not null,
    cost decimal(10, 2) check (cost >= 0),
    status varchar(25) default 'В процессе' check (status in ('Запланирован', 'В процессе', 'Завершён', 'Отменён')),
    foreign key (equipment_id) references equipment(id) on update cascade on delete restrict,
    check (end_date >= start_date or end_date is null)
);

create table audit_log (
    id serial primary key,
    table_name varchar(50) not null,
    record_id int not null,
    operation varchar(10) not null check (operation in ('INSERT', 'UPDATE', 'DELETE')),
    old_data jsonb,
    new_data jsonb,
    changed_at timestamp default current_timestamp
);
