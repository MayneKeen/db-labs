INSERT INTO public.manufacturer (manufacturer_name)
			VALUES
			('manufacturer 1'),
			('manufacturer 2'),
			('manufacturer 3');

INSERT INTO public.shop (shop_address, shop_name)
			VALUES
			('shop_address 1', 'shop_name 1'),
			('shop_address 2', 'shop_name 2'),
			('shop_address 3', 'shop_name 3');

INSERT INTO public.buyer (buyer_name, phone, email)
			VALUES
			('Vladimir Pooteen', '11-00-11', 'pooteen@government.ru'),
			('Vitaliy Milonov', '555', 'milonov@brain.net'),
			('Lebowski', '88005553535','thedude@yahoo.com');

INSERT INTO public.order (buyer_id, shop_id, order_date_to, order_date_from)
			VALUES
			(1, 1, '2019-01-01', '2019-01-30'),
			(2, 3, '2020-02-01', '2020-09-01'),
			(3, 2, '1966-10-31', '1966-11-01');


INSERT INTO public.product_type (description, product_type_name)
            VALUES
            ('description_1', 'device'),
            ('description_2', 'component_part'),
            ('description_3', 'liquid');

INSERT INTO public.product (product_name, price, product_type_id, description)
            VALUES
            ('device', 4000, 1, 'description_1'),
            ('component_part', 500, 2, 'description_2'),
            ('liquid', 1000, 3, 'description_3');

INSERT INTO public.product_to_product(product_id, product_part_id, description)
            VALUES
            (1, 2, 'description_1');

INSERT INTO public.ordered_product (order_id, quantity, product_id)
			VALUES
			(1, 1, 1),
			(1, 2, 2),
			(2, 1, 3);


INSERT INTO public.storage (shop_id)
			VALUES
			(1),
			(2),
			(3);

INSERT INTO public.batch (batch_date_to, batch_date_from, batch_info, manufacturer_id, storage_id)
			VALUES
			('1944-06-06', '1944-06-05', 'D Day', 1, 1),
			('1099-12-31', '1096-01-01', '1st crusade', 2, 2),
			('1969-06-20', '1961-06-16', 'Apollo 11', 3, 3);

INSERT INTO public.product_in_batch (batch_id, description, create_date, quantity, product_id)
			VALUES
			(1, 'batch 1 device', '1337-08-02', 8800, 1),
			(2, 'batch 2 liquid', '2001-08-02', 555, 1),
			(2, 'batch 2 device', '2020-09-01', 3535, 3);