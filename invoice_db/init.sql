create table invoice_table (
    id_invoice serial not null primary key,
    nama varchar not null,
    email varchar not null,
    phone varchar null,
    apparel_package varchar not null,
    apparel_size varchar not null,
    qty numeric not null,
    "address" varchar not null,
    shipping_cost numeric not null,
    due_date date not null, 
    total_price numeric not null,
    is_paid boolean not null DEFAULT FALSE,
    created_at timestamp not null default now()
)