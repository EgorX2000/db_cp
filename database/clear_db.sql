do $$ 
declare 
    r record;
begin
    for r in (select tablename from pg_tables where schemaname = 'public') loop
        execute 'TRUNCATE TABLE ' || quote_ident(r.tablename) || ' RESTART IDENTITY CASCADE';
    end loop;
end $$;