import datetime
import psycopg2
import random
import argparse
import configparser

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

connection = psycopg2.connect(
    dbname=config.get("postgres", "dbname"),
    user=config.get("postgres", "user"),
    password=config.get("postgres", "password"))

cursor = connection.cursor()

digits = '0123456789'
letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
en_letters = 'abcdefghijklmnopqrstuvwxyz'

today = datetime.datetime.today()

shops = ()
buyers = ()
manufacturers = ()
storages = ()
batches = ()
orders = ()
products = ()
productTypes = ()
employees = ()
reviews = ()

names_m = open("names_male.txt", encoding="utf8").readlines()
names_f = open("names_female.txt", encoding="utf8").readlines()
domains = open("email_domains.txt", "r").readlines()
manufacturer_names = open("manufacturers.txt", "r").readlines()
types = open("product_types.txt", "r").readlines()


def generate_data(arguments):
    if arguments.truncate is not None and int(arguments.truncate) == 1:
        truncate_db()

    else:
        if arguments.shops is not None:
            generate_shops(arguments.shops)

        if arguments.buyers is not None:
            generate_buyers(arguments.buyers)

        if arguments.storages is not None:
            generate_storages(arguments.storages)

        generate_employees()

        generate_manufacturers()

        generate_product_types()

        if arguments.batches is not None:
            generate_batches(arguments.batches)

        if arguments.orders is not None:
            generate_orders(arguments.orders)

        if arguments.products is not None:
            generate_products(arguments.products)

        if arguments.reviews is not None:
            generate_reviews(arguments.reviews)

        if arguments.products_in_batches is not None:
            generate_products_in_batches(arguments.products_in_batches)

        if arguments.ordered_products is not None:
            generate_ordered_products(arguments.ordered_products)

        if arguments.product_to_product is not None:
            generate_product_to_product(arguments.product_to_product)


def truncate_db():
    cursor.execute("truncate table ordered_product restart identity cascade;"
                   "truncate table \"order\" restart identity cascade;"
                   "truncate table product_in_batch restart identity cascade;"
                   "truncate table batch restart identity cascade;"
                   "truncate table manufacturer restart identity cascade;"
                   "truncate table \"storage\" restart identity cascade;"
                   "truncate table shop restart identity cascade;"
                   "truncate table product_to_product restart identity cascade;"
                   "truncate table review restart identity cascade;"
                   "truncate table product restart identity cascade;"
                   "truncate table product_type restart identity cascade;"
                   "truncate table employee restart identity cascade;"
                   "truncate table buyer restart identity cascade;")


def generate_shops(amount):
    global shops
    addresses = []
    names = []
    for i in range(int(amount)):
        names.append(random_string(random.randint(1, 100)))
        addresses.append(random_string(random.randint(1, 50)))
    shop_rows = tuple((address, random.choice(names),) for address in addresses)
    query = "INSERT INTO shop (shop_address, shop_name) VALUES (%s, %s)"
    cursor.executemany(query, shop_rows)
    cursor.execute('SELECT shop_id FROM shop')
    shops = cursor.fetchall()


def generate_buyers(amount):
    global buyers
    names = []
    phones = []
    emails = []
    temp = []
    for i in range(int(amount)):
        names.append(random.choice(names_f + names_m).replace("\n", ""))
        phones.append(random_phone_number())
        emails.append(random_email(15))
        temp.append(tuple((names[i], phones[i], emails[i],)))
    buyers_rows = tuple(temp)
    query = "INSERT INTO buyer (buyer_name, phone, email) VALUES (%s, %s, %s)"
    cursor.executemany(query, buyers_rows)
    cursor.execute('SELECT buyer_id FROM buyer')
    buyers = cursor.fetchall()


def generate_manufacturers():
    global manufacturers
    manufacturer_list = []
    for i in range(len(manufacturer_names)):
        manufacturer_list.append(manufacturer_names[i].replace("\n", ""))
    man_rows = tuple((manufacturer,) for manufacturer in manufacturer_list)
    query = "INSERT INTO manufacturer (manufacturer_name) VALUES (%s)"
    cursor.executemany(query, man_rows)
    cursor.execute('SELECT manufacturer_id FROM manufacturer')
    manufacturers = cursor.fetchall()


def generate_storages(amount):
    global storages
    shop_list = []
    for i in range(int(amount)):
        shop_list.append(random.choice(shops))
    shop_rows = tuple(shop_list)
    query = "INSERT INTO \"storage\" (shop_id) VALUES (%s)"
    cursor.executemany(query, shop_rows)
    cursor.execute('SELECT storage_id FROM storage')
    storages = cursor.fetchall()


def generate_employees():
    global employees

    dates_from = []
    dates_to = []

    cursor.execute("SELECT employee.buyer_id FROM employee")
    used = cursor.fetchall()
    list_buyers = []
    not_used = buyers
    t = []
    temp = []

    for i in range(len(not_used)):
        t.append(not_used[i])

    for i in range(len(used)):
        t.remove(used[i])
    not_used = t

    for i in range(int(len(buyers) / 3)):
        dates_from.append(rnd_date(1990, 2020))
        dates_to.append(rnd_date(1990, 2020))
        buyer = random.choice(not_used)
        not_used.remove(buyer)
        list_buyers.append(buyer[0])
        temp.append(tuple((dates_from[i], dates_to[i], list_buyers[i],)))
    employee_rows = tuple(temp)
    query = "INSERT INTO employee(date_from, date_to, buyer_id) VALUES (%s, %s, %s)"
    cursor.executemany(query, employee_rows)
    cursor.execute('SELECT employee_id FROM employee')
    employees = cursor.fetchall()


def generate_product_types():
    global productTypes

    temp = []
    for i in range(len(types)):
        temp.append(tuple((random_string(30), types[i].replace("\n", ""),)))
    types_rows = tuple(temp)
    query = "INSERT INTO product_type(description, product_type_name) VALUES (%s, %s)"
    cursor.executemany(query, types_rows)
    cursor.execute('SELECT product_type_id FROM product_type')
    productTypes = cursor.fetchall()


def generate_batches(amount):
    global batches

    temp = []
    for i in range(int(amount)):
        temp.append(tuple((rnd_date(1990, 2020), rnd_date(1990, 2020), random_string(50),
                           random.choice(manufacturers)[0], random.choice(storages)[0], random.choice(employees)[0],)))
    batches_rows = tuple(temp)
    query = "INSERT INTO batch (batch_date_from, batch_date_to, batch_info, manufacturer_id, storage_id," \
            "employee_id) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.executemany(query, batches_rows)
    cursor.execute('SELECT batch_id FROM batch')
    batches = cursor.fetchall()


def generate_orders(amount):
    global orders
    temp = []
    for i in range(int(amount)):
        temp.append(tuple((random.choice(buyers)[0], random.choice(shops)[0], rnd_date(1990, 2020),
                           rnd_date(1990, 2020), random.choice(employees)[0],)))
    orders_rows = tuple(temp)
    query = "INSERT INTO \"order\"(buyer_id, shop_id, order_date_from, order_date_to, employee_id) VALUES" \
            "(%s, %s, %s, %s, %s)"
    cursor.executemany(query, orders_rows)
    cursor.execute('SELECT order_id FROM \"order\"')
    orders = cursor.fetchall()


def generate_products(amount):
    global products
    temp = []
    for i in range(int(amount)):
        temp.append(tuple((random_string(20), random.randint(50, 8000), random.choice(productTypes)[0],
                           random_string(100),)))
    products_rows = tuple(temp)
    query = "INSERT INTO product (product_name, price, product_type_id, description) VALUES (%s, %s, %s, %s)"
    cursor.executemany(query, products_rows)
    cursor.execute('SELECT product_id FROM product')
    products = cursor.fetchall()


def generate_reviews(amount):
    global reviews
    temp = []
    for i in range(int(amount)):
        temp.append(tuple((random.choice(buyers)[0], random.choice(products)[0], random.randint(0, 5),
                           random_string(200),)))
    reviews_rows = tuple(temp)
    query = "INSERT INTO review (buyer_id, product_id, rating, text) VALUES (%s, %s, %s, %s)"
    cursor.executemany(query, reviews_rows)
    cursor.execute('SELECT review_id FROM review')
    reviews = cursor.fetchall()


def generate_products_in_batches(amount):
    temp = []
    for i in range(int(amount)):
        temp.append(tuple((random.choice(batches)[0], random_string(30), rnd_date(1990, 2020), random.randint(1, 100),
                           random.choice(products)[0],)))
    pib_rows = tuple(temp)
    query = "INSERT INTO product_in_batch(batch_id, description, create_date, quantity, product_id) " \
            "VALUES(%s, %s, %s, %s, %s)"
    cursor.executemany(query, pib_rows)


def generate_ordered_products(amount):
    temp = []
    for i in range(int(amount)):
        temp.append(tuple((random.choice(orders)[0], random.randint(1, 100), random.choice(products)[0],)))
    op_rows = tuple(temp)
    query = "INSERT INTO ordered_product(order_id, quantity, product_id) " \
            "VALUES(%s, %s, %s)"
    cursor.executemany(query, op_rows)


def generate_product_to_product(amount):
    temp = []
    for i in range(int(amount)):
        temp.append(tuple((random.choice(products)[0], random.choice(products)[0], random_string(50),)))
    ptp_rows = tuple(temp)
    query = "INSERT INTO product_to_product(product_id, product_part_id, description) " \
            "VALUES(%s, %s, %s)"
    cursor.executemany(query, ptp_rows)


def rnd_date(start_year, end_year):
    year = random.randint(start_year, end_year)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    date = datetime.date(year, month, day)
    return date


def random_date(start_date, end_date):
    date_delta = end_date - start_date
    days_delta = date_delta.days
    days_random = random.randrange(days_delta)
    r_date = start_date + datetime.timedelta(days=days_random)
    return r_date


def random_email(length):
    email = ""
    for i in range(int(length)):
        email += random.choice(en_letters + digits)
    email += '@'
    email += random.choice(domains)
    email = email.replace("\n", "")
    return email


def random_phone_number():
    phone_number = "9"
    for i in range(9):
        phone_number += random.choice(digits)
    return phone_number


def random_string(length):
    str = ''
    for i in range(int(length)):
        str += random.choice(letters)
    return str


if __name__ == '__main__':
    args = argparse.ArgumentParser(description="Details of data generation")

    args.add_argument('--shops', action="store", dest="shops")
    args.add_argument('--buyers', action="store", dest="buyers")
    args.add_argument('--storages', action="store", dest="storages")
    args.add_argument('--batches', action="store", dest="batches")
    args.add_argument('--orders', action="store", dest="orders")
    args.add_argument('--products', action="store", dest="products")
    args.add_argument('--reviews', action="store", dest="reviews")
    args.add_argument('--products_in_batches', action="store", dest="products_in_batches")
    args.add_argument('--ordered_products', action="store", dest="ordered_products")
    args.add_argument('--product_to_product', action="store", dest="product_to_product")
    args.add_argument('--truncate', action="store", dest="truncate")

    arguments = args.parse_args()

    generate_data(arguments)

    # закрытие соединения
    connection.commit()
    connection.close()
