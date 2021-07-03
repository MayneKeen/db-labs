--нужна для подсчета количества уникальных посещенных магазинов по каждому покупателю as quantity
WITH shop_count(bid, quantity) AS (SELECT "order".buyer_id, COUNT(DISTINCT "order".shop_id) FROM "order"
GROUP BY "order".buyer_id
ORDER BY "order".buyer_id),

--промежуточная конструкция, служит для вычисления суммарной стоимости продуктов в заказе as mul
summary(order_id, product_id, mul) AS (
	SELECT op.order_id, op.product_id, (op.quantity*product.price) as mul FROM ordered_product AS op
	JOIN product ON op.product_id = product.product_id 
	GROUP BY op.order_id, op.product_id, product.price, op.quantity
	ORDER BY op.order_id),

--здесь для каждого заказа_ид лежит суммарная стоимость продуктов в нем 
ordsum(order_id, s) AS (
	SELECT "order".order_id, SUM(summary.mul) AS s FROM "order"
	JOIN summary ON summary.order_id = "order".order_id
	GROUP BY "order".order_id
	ORDER BY "order".order_id
)

--quantity - количество магазинов, в которых покупал человек 
SELECT "order".buyer_id, "order".shop_id, COUNT(*) AS orders, shop_count.quantity, SUM(ordsum.s) AS sum_cost FROM "order"
JOIN shop_count ON shop_count.bid = "order".buyer_id
JOIN ordsum ON ordsum.order_id = "order".order_id
GROUP BY "order".buyer_id, "order".shop_id, shop_count.quantity
	HAVING (SELECT COUNT(shop.shop_id) FROM shop) - shop_count.quantity > 3
ORDER BY shop_count.quantity