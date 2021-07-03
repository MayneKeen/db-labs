# Язык SQL DML

## Цели работы:

Познакомиться с языком создания запросов управления данными SQL-DML.
 
## Программа работы:

1. Самостоятельное изучение SQL-DDL.
2. Создание скрипта БД в соответствии с согласованной схемой. Должны присутствовать первичные и внешние ключи, ограничения на диапазоны значений. Демонстрация скрипта преподавателю.
3. Создание скрипта, заполняющего все таблицы БД данными.
4. Выполнение SQL-запросов, изменяющих схему созданной БД по заданию преподавателя. Демонстрация их работы преподавателю.

## Ход работы:

## Создание стандартных запросов

### 1. Сделать выборку данных из одной таблицы

 - Вывод данных из таблицы **batch**.

​```sql
create view task1_1 as SELECT * FROM batch;
​```

Результат запроса:  
![task1_1](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task1_1.png)

 - Вывод данных из таблицы **buyer**.

​```sql
create view task1_2 as SELECT * FROM buyer;
​```

Результат запроса:  
![task1_2](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task1_2.png)

 - Вывод данных из таблицы **employee**.

​```sql
create view task1_3 as SELECT * FROM employee;
​```

Результат запроса:  
![task1_3](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task1_3.png)

 - Вывод данных из таблицы **manufacturer**.

​```sql
create view task1_4 as SELECT * FROM manufacturer;
​```

Результат запроса:  
![task1_4](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task1_4.png)

 - Вывод данных из таблицы **order**.

​```sql
create view task1_5 as SELECT * FROM "order";
​```

Результат запроса:  
![task1_5](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task1_5.png)

 - Вывод данных из таблицы **ordered_product**.

​```sql
create view task1_6 as SELECT * FROM ordered_product;
​```

Результат запроса:  
![task1_6](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task1_6.png)

 - Вывод данных из таблицы **product**.

​```sql
create view task1_7 as SELECT * FROM product;
​```

Результат запроса:  
![task1_7](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task1_7.png)

 - Вывод данных из таблицы **product_in_batch**.

​```sql
create view task1_8 as SELECT * FROM product_in_batch;
​```

Результат запроса:  
![task1_8](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task1_8.png)

 - Вывод данных из таблицы **product_to_product**.

​```sql
create view task1_9 as SELECT * FROM product_to_product;
​```

Результат запроса:  
![task1_9](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task1_9.png)

 - Вывод данных из таблицы **product_type**.

​```sql
create view task1_10 as SELECT * FROM product_type;
​```

Результат запроса:  
![task1_10](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task1_10.png)

 - Вывод данных из таблицы **review**.

​```sql
create view task1_11 as SELECT * FROM review;
​```

Результат запроса:  
![task1_11](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task1_11.png)

 - Вывод данных из таблицы **shop**.

​```sql
create view task1_12 as SELECT * FROM shop;
​```

Результат запроса:  
![task1_12](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task1_12.png)

 - Вывод данных из таблицы **storage**.

​```sql
create view task1_13 as SELECT * FROM storage;
​```

Результат запроса:  
![task1_13](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task1_3.png)

### 2. Сделать выборку данных из одной таблицы при нескольких условиях, с использованием логических операций, **LIKE**, **BETWEEN**, **IN** 

 - Вывод продуктов, цена на которые лежит в диапазоне от 3000 до 6000.

​```sql
create view task2_1 as SELECT * FROM product WHERE price BETWEEN 3000 AND 6000;
​```
Результат запроса:   
![task2_1](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task2_1.png)

 - Вывод покупателей в имени которых содержится паттерн 'имо'.

​```sql
create view task2_2 as SELECT * FROM buyer WHERE buyer.buyer_name LIKE '%имо%';
​```

Результат запроса:  
![task2_2](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task2_2.png)

 - Вывод сотрудников, даты date_from которых '1939-07-05' и '1926-04-07'.

​```sql
create view task2_3 as SELECT * FROM employee WHERE date_from IN ('1939-07-05', '1926-04-07');
​```

Результат запроса:  
![task2_3](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task2_3.png)

### 3. Создать в запросе вычисляемое поле

 - Запрос рассчитывает количество суток, прошедших между date_to и date_from всех сотрудников.

​```sql
create view task3 as SELECT date_from, date_to, employee_id, abs(extract(epoch FROM date_to::timestamp - date_from::timestamp)/3600/24) AS calc_place FROM employee;
​```

Результат запроса:  
![task3](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task3.png)

### 4. Сделать выборку всех данных с сортировкой по нескольким полям

 - Сортировка данных в таблице product_in_batch по количеству и описанию.

​```sql
create view task4 as SELECT * FROM product_in_batch ORDER BY quantity, description;
​```

Результат запроса:  
![task4](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task4.png)

### 5. Создать запрос, вычисляющий несколько совокупных характеристик таблиц

 - Вывод среднего значения количества продуктов в партии и даты последней созданной записи в этой таблице.

​```sql
create view task5 as SELECT AVG(pb.quantity), MAX(pb.create_date) FROM product_in_batch pb;
​```

Результат запроса:  
![task5](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task5.png)

### 6. Сделать выборку данных из связанных таблиц

 - Вывод продуктов, их цен и типов объединением таблиц product и product_type.

​```sql
create view task6_1 as SELECT p.product_name, p.price, pt.product_type_name FROM product p INNER JOIN product_type pt on p.product_type_id = pt.product_type_id;
​```

Результат запроса:  
![task6_1](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task6_1.png)

 - Вывод столбцов с количеством продуктов в заказе, и датами заказа и поставки с помощью объединения таблиц order и ordered_product.

​```sql
create view task6_2 as SELECT op.quantity, o.order_date_from, o.order_date_to FROM ordered_product op INNER JOIN "order" o on op.order_id = o.order_id;
​```

Результат запроса:  
![task6_2](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task6_2.png)

### 7.Создать запрос, рассчитывающий совокупную характеристику с использованием группировки, наложите ограничение на результат группировки

 - Группировка поставок продуктов по дате их создания, рассчет суммы заказанного количества в определенную дату и числа поставок, вывод только тех строк, где суммарное количество превышает 50.

​```sql
create view task7 as SELECT SUM(pb.quantity), COUNT(pb.quantity) FROM product_in_batch pb GROUP BY pb.create_date HAVING SUM(pb.quantity) > 50;
​```

Результат запроса:  
![task7](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task7.png)

### 8. Придумать и реализовать пример использования вложенного запроса

 - Вложенный запрос, который выводит строку из таблицы сотрудников, у которого покупатель имеет имя 'Шерлок' и телефонный номер '9995976556'.

​```sql
create view task8 as SELECT * FROM employee e WHERE e.buyer_id = (SELECT b.buyer_id FROM buyer b WHERE b.buyer_name LIKE 'Шерлок' AND b.phone LIKE '9995976556');
​```

Результат запроса:  
![task8](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task6_1.png)

### 9. С помощью команды **INSERT** добавить в каждую таблицу по одной записи.

	Заросы с помощью достаточно тривиальной команды **INSERT** в каждую таблицу успешно было добавлено по одной записи. 

 - Добавление данных в таблицу **batch**.

​```sql
CREATE OR REPLACE PROCEDURE insert9_1() LANGUAGE plpgsql AS $$ BEGIN
    INSERT INTO batch VALUES (150, '2000-08-27', '2001-02-07', 'new', 11, 2, 4);
END $$;
CALL task9_1();
​```

 - Добавление данных в таблицу **buyer**.

​```sql
CREATE OR REPLACE PROCEDURE insert9_2() LANGUAGE plpgsql AS $$ BEGIN
    INSERT INTO buyer VALUES (150, 'new_name' , '9887766554', 'laba@mail.ru');
END $$;
CALL task9_2();
​```

 - Добавление данных в таблицу **employee**.

​```sql
CREATE OR REPLACE PROCEDURE insert9_3() LANGUAGE plpgsql AS $$ BEGIN
    INSERT INTO employee VALUES (150, '1994-05-03', '2003-03-06', 6);
END $$;
CALL task9_3();
​```

 - Добавление данных в таблицу **manufacturer**.

​```sql
CREATE OR REPLACE PROCEDURE insert9_4() LANGUAGE plpgsql AS $$ BEGIN
    INSERT INTO manufacturer VALUES (150, 'maxwells');
END $$;
CALL task9_4();
​```

 - Добавление данных в таблицу **order**.

​```sql
CREATE OR REPLACE PROCEDURE insert9_5() LANGUAGE plpgsql AS $$ BEGIN
    INSERT INTO "order" VALUES (150, 19, 3, '1992-05-09', '1979-03-13', 2);
END $$;
CALL task9_5();
​```

 - Добавление данных в таблицу **ordered_product**.

​```sql
CREATE OR REPLACE PROCEDURE insert9_6() LANGUAGE plpgsql AS $$ BEGIN
    INSERT INTO ordered_product VALUES (150, 23, 21);
END $$;
CALL task9_6();
​```

 - Добавление данных в таблицу**product**.

​```sql
CREATE OR REPLACE PROCEDURE insert9_7() LANGUAGE plpgsql AS $$ BEGIN
    INSERT INTO product VALUES (150, 'new', 666666, 4, 'new');
END $$;
CALL task9_7();
​```

 - Добавление данных в таблицу **product_in_batch**.

​```sql
CREATE OR REPLACE PROCEDURE insert9_8() LANGUAGE plpgsql AS $$ BEGIN
    INSERT INTO product_in_batch VALUES (150, 'new', '1931-10-04', 50, 2);
END $$;
CALL task9_8();
​```

 - Добавление данных в таблицу **product_to_product**.

​```sql
CREATE OR REPLACE PROCEDURE insert9_9() LANGUAGE plpgsql AS $$ BEGIN
    INSERT INTO product_to_product VALUES (150, 13, 'new');
END $$;
CALL task9_9();
​```

 - Добавление данных в таблицу **product_type**.

​```sql
CREATE OR REPLACE PROCEDURE insert9_10() LANGUAGE plpgsql AS $$ BEGIN
    INSERT INTO product_type VALUES (150, 'new', 'mechanical_mode');
END $$;
CALL task9_10();
​```

 - Добавление данных в таблицу **review**.

​```sql
CREATE OR REPLACE PROCEDURE insert9_11() LANGUAGE plpgsql AS $$ BEGIN
    INSERT INTO review VALUES (150, 20, 18, 3, 'new');
END $$;
CALL task9_11();
​```

 - Добавление данных в таблицу **shop**.

​```sql
CREATE OR REPLACE PROCEDURE insert9_12() LANGUAGE plpgsql AS $$ BEGIN
    INSERT INTO shop VALUES (150, 'new', 'new');
END $$;
CALL task9_12();
​```

 - Добавление данных в таблицу **storage**.

​```sql
CREATE OR REPLACE PROCEDURE insert9_13() LANGUAGE plpgsql AS $$ BEGIN
    INSERT INTO storage VALUES (150, 150);
END $$;
CALL task9_13();
​```

### 10. С помощью оператора **UPDATE** измените значения нескольких полей у всех записей, отвечающих заданному условию

 - Обновляет цены и описание на продукты с product_type_id = 8.

​```sql
CREATE OR REPLACE PROCEDURE task10() LANGUAGE plpgsql AS $$ BEGIN
UPDATE product p SET price = 15000, description = 'was changed' WHERE product_type_id = 8;
END $$;
CALL task10();
​```

Результат до выполнения запроса:  
![task10_before](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task10_before.png)

Результат после выполнения запроса: 
![task10_after](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task10_after.png)

### 11. С помощью оператора **DELETE** удалить запись, имеющую максимальное (минимальное) значение некоторой совокупной характеристики

 - В данном запросе изначально в таблицу продуктов добавляется запись для удаления с максимальной ценой, а затем соответственно удаляется по критерию максимальной цены.

​```sql
INSERT INTO product VALUES (1000, 'for_del', 250000, 5, 'for_del');
CREATE OR REPLACE PROCEDURE task11() LANGUAGE plpgsql AS $$ BEGIN
    DELETE FROM product WHERE price = (select max(price) from product);
END $$;
CALL task11();
​```

Результат до выполнения запроса:  
![task11_before](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task11_before.png)

Результат после выполнения запроса:  
![task11_after](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task10_after.png)

### 12. С помощью оператора **DELETE** удалить записи в главной таблице, на которые не ссылается подчиненная таблица (используя вложенный запрос)

 - Удаляет строку manufacturer которая нигде не используется в таблице batch.

​```sql
​INSERT INTO manufacturer VALUES (1000, 'default_name');
CREATE OR REPLACE PROCEDURE task12() LANGUAGE plpgsql AS $$ BEGIN
DELETE FROM manufacturer WHERE manufacturer_id NOT IN (SELECT b.manufacturer_id FROM batch b);
END $$;
CALL task12();
​```
 
Результат до выполнения запроса:   
![task12_before](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task12_before.png)

Результат после выполнения запроса:   
![task12_after](https://gitlab.icc.spbstu.ru/maynekeen/vape-shop_PostgreSQL/-/raw/master/lab3/task12_after.png)

## Создание запросов по индивидуальному заданию

TODO()

## Выводы:

В ходе выполнения данной лабораторной работы ознакомился с языком создания запросов управления данными SQL-DML.
 
```
