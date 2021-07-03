create table if not exists manufacturer
(
	manufacturer_id serial not null
		constraint manufacturer_pk
			primary key,
	manufacturer_name varchar default ''::character varying not null
);

create unique index if not exists manufacturer_manufacturer_id_uindex
	on manufacturer (manufacturer_id);

create table if not exists shop
(
	shop_id serial not null
		constraint shop_pk
			primary key,
	shop_address varchar default ''::character varying not null,
	shop_name varchar default ''::character varying not null
);

create unique index if not exists shop_shop_id_uindex
	on shop (shop_id);

create table if not exists buyer
(
	buyer_id serial not null
		constraint buyer_pk
			primary key,
	buyer_name varchar default ''::character varying not null,
	phone varchar(20) not null,
	email varchar default ''::character varying not null
);

create table if not exists "order"
(
	order_id serial not null
		constraint order_pk
			primary key,
	buyer_id integer not null
		constraint order_buyer_buyer_id_fk
			references buyer,
	shop_id integer
		constraint order_shop_shop_id_fk
			references shop,
	order_date_to date not null,
	order_date_from date not null
);

create unique index if not exists order_order_id_uindex
	on "order" (order_id);

create unique index if not exists buyer_buyer_id_uindex
	on buyer (buyer_id);

create table if not exists storage
(
	storage_id serial not null
		constraint storage_pk
			primary key,
	shop_id integer not null
		constraint storage_shop_shop_id_fk
			references shop
				on delete cascade
);

create table if not exists batch
(
	batch_id serial not null
		constraint batch_pk
			primary key,
	batch_date_to date not null,
	batch_date_from date not null,
	batch_info varchar,
	manufacturer_id integer not null
		constraint batch_manufacturer_manufacturer_id_fk
			references manufacturer,
	storage_id integer not null
		constraint batch_storage_storage_id_fk
			references storage
				on delete cascade
);

create unique index if not exists batch_batch_id_uindex
	on batch (batch_id);

create unique index if not exists storage_storage_id_uindex
	on storage (storage_id);

create table if not exists product_type
(
	product_type_id serial not null
		constraint product_type_pk
			primary key,
	description varchar default ''::character varying not null,
	product_type_name varchar default ''::character varying not null
);

create table if not exists product
(
	product_id serial not null
		constraint device_pk
			primary key,
	product_name varchar default ''::character varying not null,
	price integer not null,
	product_type_id integer not null
		constraint product_product_type_product_type_id_fk
			references product_type
				on delete cascade,
	description varchar default ''::character varying not null
);

create unique index if not exists device_device_id_uindex
	on product (product_id);

create table if not exists ordered_product
(
	order_id integer not null
		constraint product_in_order_order_order_id_fk
			references "order"
				on delete cascade,
	quantity integer not null,
	product_id integer not null
		constraint ordered_product_product_product_id_fk
			references product
				on delete cascade
);

create table if not exists product_in_batch
(
	batch_id integer not null
		constraint product_in_batch_batch_batch_id_fk
			references batch
				on delete cascade,
	description varchar default ''::character varying not null,
	create_date date not null,
	quantity integer not null,
	product_id integer not null
		constraint product_in_batch_product_product_id_fk
			references product
);

create unique index if not exists product_type_product_type_id_uindex
	on product_type (product_type_id);

create table if not exists product_to_product
(
	product_id integer not null
		constraint product_to_product_product_product_id_fk
			references product
				on delete cascade,
	product_part_id integer not null
		constraint product_to_product_product_product_id_fk_2
			references product
				on delete cascade,
	description varchar default ''::character varying not null
);
