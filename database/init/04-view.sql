create view v_active_rentals as
select 
    r.id as rental_id,
    r.start_date,
    r.end_date,
    u.name as client_name,
    u.phone as client_phone,
    e.name as employee_name,
    count(ri.equipment_id) as equipment_count
from rentals r
join users u on r.user_id = u.id
join users e on r.employee_id = e.id
left join rental_items ri on r.id = ri.rental_id
where r.status = 'Активен'
group by r.id, u.name, u.phone, e.name
order by r.end_date;


create view v_overdue_rentals as
select 
    r.id as rental_id,
    r.end_date,
    u.name as client_name,
    u.phone as client_phone,
    u.email as client_email,
    (current_date - r.end_date) as days_overdue,
    count(ri.equipment_id) as equipment_count
from rentals r
join users u on r.user_id = u.id
left join rental_items ri on r.id = ri.rental_id
where r.status = 'Просрочен срок аренды'
group by r.id, u.name, u.phone, u.email
order by days_overdue desc;


create view v_client_stats as
select 
    u.id as client_id,
    u.name,
    u.email,
    u.phone,
    count(distinct r.id) as total_rentals,
    min(r.start_date) as first_rental,
    max(r.start_date) as last_rental
from users u
left join rentals r on u.id = r.user_id
where u.role = 'Клиент'
group by u.id, u.name, u.email, u.phone
order by total_rentals desc;


create view v_monthly_revenue as
select 
    date_trunc('month', r.start_date) as month,
    count(distinct r.id) as rental_count,
    count(distinct ri.equipment_id) as equipment_count,
    sum(r.total_cost) as total_revenue,
    sum(ri.damage_fee) as damage_fees
from rentals r
left join rental_items ri on r.id = ri.rental_id
where r.status = 'Завершён'
group by date_trunc('month', r.start_date)
order by month desc;