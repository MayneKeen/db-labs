--находим месяц и год старта продаж магазина
WITH temptable(sid, oid, mindate, yyyy, mm) AS (
	SELECT "order".shop_id, "order".order_id, MIN("order".order_date_from), EXTRACT (YEAR FROM "order".order_date_from) AS date_year, 
	EXTRACT (MONTH FROM "order".order_date_from) AS date_month 
	FROM "order"
	JOIN "order" AS order2 ON order2.shop_id = "order".shop_id
	GROUP BY "order".shop_id, EXTRACT (YEAR FROM "order".order_date_from), EXTRACT (MONTH FROM "order".order_date_from), "order".order_id
	HAVING EXTRACT(YEAR FROM "order".order_date_from) = EXTRACT (YEAR FROM MIN(order2.order_date_from)) 
		AND EXTRACT (MONTH FROM "order".order_date_from) = EXTRACT (MONTH FROM MIN(order2.order_date_from)) 
	ORDER BY shop_id
)
--выводим вместе с количеством заказов в первый месяц работы магазина
SELECT temptable.sid, temptable.yyyy, temptable.mm, COUNT(*) FROM  temptable
JOIN "order" ON "order".shop_id = temptable.sid AND temptable.oid = "order".order_id
WHERE EXTRACT (YEAR FROM "order".order_date_from) = temptable.yyyy AND EXTRACT (MONTH FROM "order".order_date_from) = temptable.mm
GROUP BY temptable.sid, temptable.yyyy, temptable.mm
ORDER BY COUNT DESC
LIMIT 10;
