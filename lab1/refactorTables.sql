create table if not exists review
(
	review_id serial not null
		constraint review_pk
			primary key,
	buyer_id serial not null
		constraint review_buyer_buyer_id_fk
			references buyer,
	product_id serial not null
		constraint review_product_product_id_fk
			references product
				on delete cascade,
	rating integer not null,
	text varchar(200)
);

create unique index if not exists review_review_id_uindex
	on review (review_id);

create table if not exists employee
(
	employee_id serial not null
		constraint employee_pk
			primary key,
	date_from date not null,
	date_to date not null,
	buyer_id integer not null
		constraint employee_buyer_buyer_id_fk
			references buyer	
				on delete cascade
);

alter table batch add column if not exists employee_id integer not null 
			constraint batch_employee_employee_id_fk
				references employee
					on delete cascade;
							
alter table "order" add column if not exists employee_id integer not null 
			constraint order_employee_employee_id_fk
				references employee
					on delete cascade;


create unique index if not exists employee_buyer_id_uindex
	on employee (buyer_id);

create unique index if not exists employee_employee_id_uindex
	on employee (employee_id);

