create or replace function calculate_late_fee(p_rental_id int, p_daily_fee decimal(10,2) default 500.00, p_fixed_fee decimal(10,2) default 1000.00)
returns decimal(10,2)
language plpgsql
as $$
declare
    late_days int;
    late_fee decimal(10,2) default 0;
begin
    select current_date - end_date
    into late_days
    from rentals 
    where id = p_rental_id and status = 'Просрочен срок аренды';
    
    if (late_days > 0) then
        late_fee := p_fixed_fee + (late_days * p_daily_fee);
    end if;
    
    return late_fee;
end;
$$;

create or replace function get_avg_rental_days(p_equipment_id int)
returns decimal(5,1)
language plpgsql
as $$
declare
    avg_days decimal(5,1);
begin
    select coalesce(avg(r.end_date - r.start_date + 1), 0) into avg_days
    from rental_items ri
    join rentals r on ri.rental_id = r.id
    where ri.equipment_id = p_equipment_id
      and r.status = 'Завершён';
    
    return avg_days;
end;
$$;


create or replace function get_rentals_period_report(p_start_date date, p_end_date date)
returns table (
    rental_id int,
    client_name varchar(100),
    start_date date,
    end_date date,
    status varchar(20),
    total_cost decimal(10,2),
    equipment_count int
)
language plpgsql
as $$
begin
    return query
    select 
        r.id,
        u.name,
        r.start_date,
        r.end_date,
        r.status,
        r.total_cost,
        count(ri.id)::int as equipment_count
    from rentals r
    join users u on r.user_id = u.id
    left join rental_items ri on r.id = ri.rental_id
    where r.start_date between p_start_date and p_end_date
    group by r.id, u.name
    order by r.start_date;
end;
$$;


create or replace function get_rentals_ending_soon(p_days_left int default 2)
returns table (
    rental_id int,
    client_name varchar(100),
    client_phone varchar(20),
    end_date date,
    equipment_count int,
    employee varchar(100)
)
language plpgsql
as $$
begin
    return query
    select 
        r.id,
        u.name,
        u.phone,
        r.end_date,
        count(ri.id)::int,
        e.name as employee
    from rentals r
    join users u on r.user_id = u.id
    join users e on r.employee_id = e.id
    left join rental_items ri on r.id = ri.rental_id
    where r.status = 'Активен' and r.end_date between current_date and current_date + p_days_left
    group by r.id, u.name, u.phone, e.name
    order by r.end_date;
end;
$$;
