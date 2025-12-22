create index if not exists idx_rentals_active_end_date on rentals(end_date)
where status = 'Активен';
explain analyze
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
where r.status = 'Активен' and r.end_date between current_date and current_date + 3
group by r.id, u.name, u.phone, e.name
order by r.end_date;


create index if not exists idx_rentals_overdue_end_date on rentals(end_date)
where status = 'Просрочен срок аренды';
explain analyze
select * from v_overdue_rentals;


create index if not exists idx_rentals_start_date on rentals (start_date);
explain analyze
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
where r.start_date between '2024-01-01' and '2024-12-31'
group by r.id, u.name
order by r.start_date;


create index if not exists idx_rentals_overdue_status on rentals (status, end_date)
where status = 'Просрочен срок аренды';
explain analyze
select calculate_late_fee(123);


create index if not exists idx_rental_items_rental_id on rental_items (rental_id);
explain analyze
select * from v_active_rentals 
limit 20
offset 10;


drop index if exists idx_rentals_active_end_date;
drop index if exists idx_rentals_overdue_end_date;
drop index if exists idx_rentals_start_date;
drop index if exists idx_rentals_overdue_status;
drop index if exists idx_rental_items_rental_id;
