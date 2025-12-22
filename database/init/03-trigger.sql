create or replace function log_audit_func()
returns trigger
language plpgsql
as $$
begin
    if (tg_op = 'INSERT') then
        insert into audit_log (table_name, record_id, operation, old_data, new_data)
        values (tg_table_name, new.id, 'INSERT', null, row_to_json(new));
        return new;
    elsif (tg_op = 'UPDATE') then
        insert into audit_log (table_name, record_id, operation, old_data, new_data)
        values (tg_table_name, new.id, 'UPDATE', row_to_json(old), row_to_json(new));
        return new;
    elsif (tg_op = 'DELETE') then
        insert into audit_log (table_name, record_id, operation, old_data, new_data)
        values (tg_table_name, old.id, 'DELETE', row_to_json(old), null);
        return old;
    end if;
    return null;
end;
$$;

create or replace trigger log_audit_users_trigger
after insert or update or delete on users
for each row
execute function log_audit_func();

create or replace trigger log_audit_equipment_trigger
after insert or update or delete on equipment
for each row
execute function log_audit_func();

create or replace trigger log_audit_rentals_trigger
after insert or update or delete on rentals
for each row
execute function log_audit_func();

create or replace trigger log_audit_payments_trigger
after insert or update or delete on payments
for each row
execute function log_audit_func();

create or replace trigger log_audit_repairs_trigger
after insert or update or delete on repairs
for each row
execute function log_audit_func();


create or replace function calculate_rental_total_cost_func()
returns trigger
language plpgsql
as $$
declare
    target_rental_id int;
    actual_days int;
    new_total decimal(10,2);
begin
    if tg_table_name = 'rental_items' then
        if tg_op = 'DELETE' then
            target_rental_id := old.rental_id;
        else
            target_rental_id := new.rental_id;
        end if;
    else
        target_rental_id := new.id;
    end if;

    select 
        case 
            when r.return_date is not null and r.return_date >= r.start_date then 
				r.return_date - r.start_date + 1
            else 
                r.end_date - r.start_date + 1
        end
    into actual_days
    from rentals r
    where r.id = target_rental_id;

    if actual_days is null or actual_days < 1 then
        actual_days := 0;
    end if;

    select coalesce(sum(em.rental_price_per_day * actual_days + ri.damage_fee), 0)
    into new_total
    from rental_items ri
    join equipment e on ri.equipment_id = e.id
    join equipment_models em on e.model_id = em.id
    where ri.rental_id = target_rental_id;

    update rentals
    set total_cost = new_total
    where id = target_rental_id;

    return null;
end;
$$;

create or replace trigger calculate_rental_total_cost_items_trigger
after insert or update or delete on rental_items
for each row
execute function calculate_rental_total_cost_func();

create or replace trigger calculate_rental_total_cost_date_trigger
after update of start_date, end_date, return_date on rentals
for each row
execute function calculate_rental_total_cost_func();

create or replace trigger calculate_rental_total_cost_insert_trigger
after insert on rentals
for each row
execute function calculate_rental_total_cost_func();


create or replace function updated_at_timestamp_func()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = current_timestamp;
    return new;
end;
$$;

create or replace trigger updated_at_timestamp_trigger
before update on rentals
for each row
execute function updated_at_timestamp_func();


create or replace function copy_total_cost_to_payment()
returns trigger
language plpgsql
as $$
declare
    rental_total decimal(10,2);
begin
    select total_cost into rental_total
    from rentals
    where id = new.rental_id;

    if rental_total is null then
        rental_total := 0.00;
    end if;

    new.amount := rental_total;

    return new;
end;
$$;

create trigger trg_copy_amount_from_rental_insert
before insert on payments
for each row
execute function copy_total_cost_to_payment();


create or replace function update_equipment_status_rental_update_func()
returns trigger
language plpgsql
as $$
begin
    if (new.status = 'Активен' and old.status != 'Активен') then
        update equipment 
        set status = 'В аренде'
        where id in (
            select equipment_id 
            from rental_items 
            where rental_id = new.id
        );
    elsif (new.status in ('Завершён', 'Отменён') 
        and old.status not in ('Завершён', 'Отменён')) then
        update equipment 
        set status = 'Доступно'
        where id in (
            select equipment_id 
            from rental_items 
            where rental_id = new.id and damage_fee = 0
        );
        update equipment
        set status = 'На обслуживании/В ремонте'
        where id in (
            select equipment_id 
            from rental_items 
            where rental_id = new.id and damage_fee > 0
        );
    end if;
    
    return new;
end;
$$;

create or replace trigger update_equipment_status_rental_update_trigger
after update of status on rentals
for each row
execute function update_equipment_status_rental_update_func();


create or replace function update_equipment_status_rental_insert_func()
returns trigger
language plpgsql
as $$
begin
    if exists (
        select 1 from rentals 
        where id = new.rental_id 
        and status = 'Активен'
    ) then
        update equipment 
        set status = 'В аренде'
        where id = new.equipment_id;
    end if;
    
    return new;
end;
$$;

create or replace trigger update_equipment_status_rental_insert_trigger
after insert on rental_items
for each row execute function update_equipment_status_rental_insert_func();


create or replace function update_equipment_status_repair_func()
returns trigger
language plpgsql
as $$
begin
    if (tg_op = 'INSERT' and new.status in ('В процессе', 'Запланирован')) then
        update equipment 
        set status = 'На обслуживании/В ремонте'
        where id = new.equipment_id;
    elsif (tg_op = 'UPDATE' and new.status != old.status) then
        if (new.status in ('В процессе', 'Запланирован')) then
            update equipment 
            set status = 'На обслуживании/В ремонте'
            where id = new.equipment_id;
        
        elsif (new.status in ('Завершён', 'Отменён')) then
            if not exists (
                select 1 
                from rental_items ri
                join rentals r on ri.rental_id = r.id
                where ri.equipment_id = new.equipment_id
                  and r.status = 'Активен'
            ) then
                update equipment 
                set status = 'Доступно'
                where id = new.equipment_id;
            end if;
        end if;
    end if;
    
    return new;
end;
$$;

create or replace trigger update_equipment_status_repair_trigger
after insert or update of status on repairs
for each row
execute function update_equipment_status_repair_func();


create or replace function update_overdue_rentals_func()
returns trigger
language plpgsql
as $$
begin
    if (new.end_date < current_date 
        and new.status = 'Активен'
        and new.return_date is null) then
        new.status := 'Просрочен срок аренды';
    end if;
    
    return new;
end;
$$;

create or replace trigger update_overdue_rentals_trigger
before insert or update on rentals
for each row
execute function update_overdue_rentals_func();