import psycopg2
import random
import threading
import time
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import datetime
import argparse

import configparser

parser = argparse.ArgumentParser(description='Database load modeling application')
parser.add_argument('--operating_mode', '-m', default=0, type=int,
                    help='''operating mode, 1 for database answer time / queries per second relation 
                    0 for database answer time / threads number relation''')
parser.add_argument('--minimum_threads', '-t_min', default=1, type=int,
                    help='threads number at which modeling with threads will start')
parser.add_argument('--maximum_threads', '-t_max', default=10, type=int,
                    help='threads number at which modeling with threads will end')
parser.add_argument('--constant_threads', '-t_con', default=1, type=int,
                    help='threads number at which modeling with queries per second will run')
parser.add_argument('--minimum_queries', '-q_min', default=10, type=int,
                    help='queries number at which modeling with queries per second will start')
parser.add_argument('--maximum_queries', '-q_max', default=150, type=int,
                    help='queries number at which modeling with queries per second will end')
parser.add_argument('--constant_queries', '-q_con', default=100, type=int,
                    help='queries number at which modeling with threads will run')
parser.add_argument('--seconds', '-s', default=20, type=int, help='seconds for modeling with queries per second')
p_args = parser.parse_args()
work_flag = p_args.operating_mode
threads_min = p_args.minimum_threads
threads_max = p_args.maximum_threads
const_threads = p_args.constant_threads
queries_min = p_args.minimum_queries
queries_max = p_args.maximum_queries
const_queries = p_args.constant_queries
seconds = p_args.seconds

# con = psycopg2.connect(**params)  # открыть соединение, чтобы прочитать данные, необходимые для запросов
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

con = psycopg2.connect(
    dbname=config.get("postgres", "dbname"),
    user=config.get("postgres", "user"),
    password=config.get("postgres", "password"))
cur = con.cursor()

# cur.execute('SELECT name FROM countries;')  # список стран для запросов
# countries = cur.fetchall()
# cur.execute('SELECT name FROM artists;')  # список артистов для запросов
# artists = cur.fetchall()


def rnd_date(start_year, end_year):
    year = random.randint(start_year, end_year)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    date = datetime.date(year, month, day)
    return date


manufacturers = open("manufacturers.txt", "r").readlines()


def random_manufacturer():
    manufacturer = random.choice(manufacturers)
    manufacturer = manufacturer.replace("\n", "")
    return manufacturer


con.close()

# dates = pd.date_range('2020-01-01', datetime.now(), freq='D')  # даты для запросов

threads = []
results = []  # общие результаты работы для всех потоков

prepare = False

queries = {
    #
    1: '''SELECT buyer.buyer_id, buyer_name, phone, email, employee.date_from, employee.date_to,
          \"order\".order_id, \"order\".shop_id FROM buyer 
          JOIN employee as employee ON employee.buyer_id = buyer.buyer_id 
          JOIN \"order\" ON \"order\".employee_id = employee.employee_id 
          WHERE \"order\".order_date_to = (%s);''',
    #
    2: '''SELECT product.product_id, product.product_name, product.price, product.product_type_id, product.description
          , pt.product_type_name, pt.description, ptp.product_id, ptp.product_part_id, prod.price, prod.product_type_id,
          prod.description FROM product
          JOIN product_type as pt ON product.product_type_id = pt.product_type_id
          JOIN product_to_product as ptp ON ptp.product_id = product.product_id
          JOIN product as prod ON ptp.product_part_id = prod.product_id
          WHERE product.price = (%s);''',
    # #
    # 3: '''SELECT manufacturer.manufacturer_id, manufacturer_name, batch_date_to, batch_date_from, batch_info,
    #       b.storage_id, buyer.buyer_name, buyer.phone FROM manufacturer
    #       JOIN batch as b ON b.manufacturer_id = manufacturer.manufacturer_id
    #       JOIN employee ON b.employee_id = employee.employee_id
    #       JOIN buyer ON employee.buyer_id = buyer.buyer_id
    #       WHERE manufacturer.manufacturer_name = (%s);''',
    # #
    # 4: '''SELECT review.buyer_id, review.product_id, product_name, price, product_type_name, review.rating,
    #       review.text, buyer_name  FROM review
    #       JOIN buyer ON review.buyer_id = buyer.buyer_id
    #       JOIN product ON review.product_id = product.product_id
    #       JOIN product_type AS pt ON product.product_type_id = pt.product_type_id
    #       WHERE rating = (%s);''',
    #
    # 5: '''SELECT \"storage\".storage_id, batch_date_to, employee.employee_id, buyer_name as employee_name,
    #        batch_info, manufacturer_name, product_name, quantity, price, create_date FROM \"storage\"
    #        JOIN batch ON batch.storage_id = \"storage\".storage_id
    #        JOIN employee ON batch.employee_id = employee.employee_id
    #        JOIN buyer ON employee.buyer_id = buyer.buyer_id
    #        JOIN manufacturer ON batch.manufacturer_id = manufacturer.manufacturer_id
    #        JOIN product_in_batch as pib ON pib.batch_id = batch.batch_id
    #        JOIN product ON pib.product_id=product.product_id
    #        WHERE quantity = (%s);'''
}

queries_prepared = {
    1: "EXECUTE query1 (%s);",
    2: "EXECUTE query2 (%s);",
    3: "EXECUTE query3 (%s);",
    4: "EXECUTE query4 (%s);",
    # 5: "EXECUTE query5 (%s);"
}


def optimize_create_indices():
    ind_con = psycopg2.connect(dbname=config.get("postgres", "dbname"),
                               user=config.get("postgres", "user"),
                               password=config.get("postgres", "password"))  # открыть соединение, чтобы создать индексы
    ind_cur = ind_con.cursor()
    ind_cur.execute("CREATE INDEX IF NOT EXISTS i1 ON \"order\"(order_date_to);")
    ind_cur.execute("CREATE INDEX IF NOT EXISTS i2 ON product(price);")
    ind_cur.execute("CREATE INDEX IF NOT EXISTS i3 ON manufacturer(manufacturer_name);")
    ind_cur.execute("CREATE INDEX IF NOT EXISTS i4 ON review(rating);")
    ind_cur.execute("CREATE INDEX IF NOT EXISTS i5 ON product_in_batch(quantity);")

    ind_con.commit()
    print('indices created')
    ind_con.close()


def prepare_queries(thread_cursor):
    thread_cursor.execute('''PREPARE query1 (date) AS SELECT buyer.buyer_id, buyer_name, phone, email, employee.date_from, employee.date_to,
          \"order\".order_id, \"order\".shop_id FROM buyer 
          JOIN employee as employee ON employee.buyer_id = buyer.buyer_id 
          JOIN \"order\" ON \"order\".employee_id = employee.employee_id 
          WHERE \"order\".order_date_to = $1;''')
    thread_cursor.execute('''PREPARE query2 (integer) AS SELECT product.product_id, product.product_name, product.price, product.product_type_id, product.description
          , pt.product_type_name, pt.description, ptp.product_id, ptp.product_part_id, prod.price, prod.product_type_id,
          prod.description FROM product
          JOIN product_type as pt ON product.product_type_id = pt.product_type_id
          JOIN product_to_product as ptp ON ptp.product_id = product.product_id
          JOIN product as prod ON ptp.product_part_id = prod.product_id
          WHERE product.price = $1;''')
    # thread_cursor.execute('''PREPARE query3 (varchar(50)) AS SELECT manufacturer.manufacturer_id, manufacturer_name, batch_date_to, batch_date_from, batch_info,
    #       b.storage_id, buyer.buyer_name, buyer.phone FROM manufacturer
    #       JOIN batch as b ON b.manufacturer_id = manufacturer.manufacturer_id
    #       JOIN employee ON b.employee_id = employee.employee_id
    #       JOIN buyer ON employee.buyer_id = buyer.buyer_id
    #       WHERE manufacturer.manufacturer_name = $1;''')
    # thread_cursor.execute('''PREPARE query4 (integer) AS SELECT review.buyer_id, review.product_id, product_name, price, product_type_name, review.rating,
    #       review.text, buyer_name  FROM review
    #       JOIN buyer ON review.buyer_id = buyer.buyer_id
    #       JOIN product ON review.product_id = product.product_id
    #       JOIN product_type AS pt ON product.product_type_id = pt.product_type_id
    #       WHERE rating = $1;''')
    # thread_cursor.execute('''PREPARE query5 (integer) AS SELECT \"storage\".storage_id, batch_date_to, employee.employee_id, buyer_name as employee_name,
    #        batch_info, manufacturer_name, product_name, quantity, price, create_date FROM \"storage\"
    #        JOIN batch ON batch.storage_id = \"storage\".storage_id
    #        JOIN employee ON batch.employee_id = employee.employee_id
    #        JOIN buyer ON employee.buyer_id = buyer.buyer_id
    #        JOIN manufacturer ON batch.manufacturer_id = manufacturer.manufacturer_id
    #        JOIN product_in_batch as pib ON pib.batch_id = batch.batch_id
    #        JOIN product ON pib.product_id=product.product_id
    #        WHERE quantity = $1;''')
    print('queries prepared')


def drop_indices():
    ind_con = psycopg2.connect(dbname=config.get("postgres", "dbname"),
                               user=config.get("postgres", "user"),
                               password=config.get("postgres", "password"))  # открыть соединение, чтобы дропнуть индексы
    ind_cur = ind_con.cursor()
    ind_cur.execute("DROP INDEX IF EXISTS i1;")
    ind_cur.execute("DROP INDEX IF EXISTS i2;")
    ind_cur.execute("DROP INDEX IF EXISTS i3;")
    ind_cur.execute("DROP INDEX IF EXISTS i4;")
    ind_cur.execute("DROP INDEX IF EXISTS i5;")
    ind_con.commit()
    print('indices dropped')
    ind_con.close()


def execute_random_query(thread_cursor):
    """Выполняет случайный запрос к базе данных, используя курсор соединения, открытого потоком"""
    global prepare

    # query = random.randint(1, len(queries))
    #
    # if query == query_1:
    #     thread_cursor.execute("EXPLAIN ANALYZE " + query_1, {"date": rnd_date(1990, 2020)})
    # elif query == query_2:
    #     thread_cursor.execute("EXPLAIN ANALYZE " + query_2, {"price": random.randint(1, 5000)})
    # elif query == query_3:
    #     thread_cursor.execute("EXPLAIN ANALYZE " + query_3, {"man": random_manufacturer()})
    # elif query == query_4:
    #     thread_cursor.execute("EXPLAIN ANALYZE " + query_4, {"rating": random.randint(0, 5)})
    # elif query == query_5:
    #     thread_cursor.execute("EXPLAIN ANALYZE " + query_5, {"quantity": random.randint(1, 100)})

    query_number = random.randint(1, len(queries))
    if query_number == 1:
        args = (rnd_date(1990, 2020),)
    elif query_number == 2:
        args = (random.randint(1, 5000),)
    # elif query_number == 3:
    #     args = (random_manufacturer(),)
    # elif query_number == 4:
    #     args = (random.randint(1, 5),)
    # elif query_number == 5:
    #     args = (random.randint(1, 100),)
    else:
        print('wrong query number')
        return

    if prepare:
        thread_cursor.execute("EXPLAIN ANALYSE " + queries_prepared[query_number], args)
    else:
        thread_cursor.execute("EXPLAIN ANALYSE " + queries[query_number], args)

    query_result = thread_cursor.fetchall()
    exec_time = float(query_result[-1][0].split()[2]) + float(query_result[-2][0].split()[2])

    return exec_time


def run_modeling_with_queries(x, y):
    for thread in range(const_threads):
        new_thread = ConstantQueryThread(queries_min, queries_max, seconds)
        new_thread.start()
        threads.append(new_thread)

    for t in threads:
        t.join()

    threads.clear()

    print('RESULTS', results)

    for second in range(seconds):
        queries_sum = 0
        threads_sum = 0
        avg_time_sum = 0
        for element in results:
            if element[0] == second:
                queries_sum += element[1]
                threads_sum += 1
                avg_time_sum += element[2]
        # Проверка, чтобы график не "скакал" туда-обратно, когда потоки достигнут физического максимума
        # выполнения запросов в секунду
        if len(x) == 0 or queries_sum > x[-1]:
            x.append(queries_sum)
            y.append(avg_time_sum / threads_sum)

    results.clear()

    print('x:', x)
    print('y:', y)


def run_modeling_with_threads(x, y):
    for step in range(threads_min, threads_max + 1):
        for thread in range(step):
            new_thread = DynamicQueryThread(const_queries)
            new_thread.start()
            threads.append(new_thread)

        for t in threads:
            t.join()

        threads.clear()

        print('RESULTS', results)

        x.append(len(results))
        y.append(sum(results) / len(results))

        results.clear()

    print('x:', x)
    print('y:', y)


def build_answer_queries_relation():
    """Строит график зависимости времени ответа базы данных от количества запросов к ней в секунду.
    Работает с постоянным количеством потоков. Каждый поток имеет физический максимум обращений
    к базе данных за секунду. Поэтому реальное количество обращений может отличаться от заданного максимума."""

    global prepare

    # моделирование нагрузки без оптимизации
    drop_indices()
    x1 = []
    y1 = []
    run_modeling_with_queries(x1, y1)

    # моделирование нагрузки с отимизацией в виде создания индексов
    optimize_create_indices()
    x2 = []
    y2 = []
    run_modeling_with_queries(x2, y2)

    # моделирование нагрузки с потимизацией в виде создание подготовленных операторов (с уже созданными индексами)
    prepare = True
    x3 = []
    y3 = []
    run_modeling_with_queries(x3, y3)

    fig, ax = plt.subplots()
    ax.plot(x1, y1, label='non-optimized')
    ax.plot(x2, y2, label='optimized with indices')
    ax.plot(x3, y3, label='optimized with indices + prepared queries')
    ax.grid(which='major', linewidth=0.5, color='k')
    ax.legend()
    plt.xlabel('Суммарно запросов в секунду со всех потоков')
    plt.ylabel('Среднее время ответа на один запрос, мс')
    plt.title(f'''Зависимость времени ответа БД от кол-ва запросов в секунду
    Количество потоков: {const_threads}''')
    plt.show()


def build_answer_threads_relation():
    """Строит график зависимости времени ответа базы данных от количества потоков, обращающихся к ней.
    Работает с постоянным количеством запросов от каждого потока."""

    global prepare

    # моделирование нагрузки без оптимизации
    drop_indices()
    x1 = []
    y1 = []
    run_modeling_with_threads(x1, y1)

    # моделирование нагрузки с отимизацией в виде создания индексов
    optimize_create_indices()
    x2 = []
    y2 = []
    run_modeling_with_threads(x2, y2)

    # моделирование нагрузки с потимизацией в виде создание подготовленных операторов (с уже созданными индексами)
    prepare = True
    x3 = []
    y3 = []
    run_modeling_with_threads(x3, y3)

    fig, ax = plt.subplots()
    ax.plot(x1, y1, label='non-optimized')
    ax.plot(x2, y2, label='optimized with indices')
    ax.plot(x3, y3, label='optimized with indices + prepared queries')
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.minorticks_on()
    ax.grid(which='major', linewidth=0.5, color='k')
    ax.legend()
    plt.xlabel('Количество потоков')
    plt.ylabel('Среднее время ответа на один запрос, мс')
    plt.title('Зависимость времени ответа БД от кол-ва потоков')
    plt.show()


class ConstantQueryThread(threading.Thread):
    """Поток, выполняющийся заданное время и старающийся выполнить переданное ему количество запросов в секунду"""

    def __init__(self, q_min, q_max, work_seconds):
        super().__init__()
        self.work_seconds = work_seconds
        self.queries_min = q_min
        self.queries_max = q_max
        self.query_con = psycopg2.connect(dbname=config.get("postgres", "dbname"),
                                          user=config.get("postgres", "user"),
                                          password=config.get("postgres", "password"))
        self.query_cur = self.query_con.cursor()

    def run(self):
        global prepare
        print(f'\nDatabase connection OPENED successfully in thread {threading.current_thread().ident}')
        if prepare:
            prepare_queries(self.query_cur)
            self.query_con.commit()
        step_length = (self.queries_max - self.queries_min) // (seconds - 1)
        for second, curr_q_num in enumerate(range(self.queries_min, self.queries_max + 1, step_length)):
            thread_results = []
            start_time = time.time()
            for query in range(curr_q_num):
                thread_results.append(execute_random_query(self.query_cur))
                if time.time() - start_time >= 1:  # если секунда вышла - перестаём делать запросы
                    break

            if time.time() - start_time <= 1:  # ждём остаток секунды, если она ещё не вышла, а цикл закончился
                time.sleep(1 - (time.time() - start_time))

            queries_amount = len(thread_results)
            avg_time = sum(thread_results) / queries_amount  # среднее время выполнения запроса
            print(f'''\nresults for thread {threading.current_thread().ident}:
            number of queries: {queries_amount}
            average query planning + execution time: {avg_time}''')

            results.append((second, queries_amount, avg_time))

        self.query_con.close()
        print(f'Database connection CLOSED successfully in thread {threading.current_thread().ident}')


class DynamicQueryThread(threading.Thread):
    """Поток, выполняющий заданное количество запросов к базе данных"""

    def __init__(self, q_amount):
        super().__init__()
        self.queries_amount = q_amount
        self.query_con = psycopg2.connect(dbname=config.get("postgres", "dbname"),
                                          user=config.get("postgres", "user"),
                                          password=config.get("postgres", "password"))
        self.query_cur = self.query_con.cursor()

    def run(self):
        global prepare
        print(f'\nDatabase connection OPENED successfully in thread {threading.current_thread().ident}')
        if prepare:
            prepare_queries(self.query_cur)
            self.query_con.commit()
        thread_results = []
        for query in range(self.queries_amount):
            thread_results.append(execute_random_query(self.query_cur))

        queries_amount = len(thread_results)
        avg_time = sum(thread_results) / queries_amount  # среднее время выполнения запроса
        print(f'''\nresults for thread {threading.current_thread().ident}:
        number of queries: {queries_amount}
        average query planning + execution time: {avg_time}''')

        results.append(avg_time)

        self.query_con.close()
        print(f'Database connection CLOSED successfully in thread {threading.current_thread().ident}')


if work_flag:
    build_answer_queries_relation()
else:
    build_answer_threads_relation()
