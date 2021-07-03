import psycopg2
# import random
# import argparse
import configparser
import datetime

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

connection = psycopg2.connect(
    dbname=config.get("postgres", "dbname"),
    user=config.get("postgres", "user"),
    password=config.get("postgres", "password"))

cursor = connection.cursor()
connection.autocommit = True

digits = '0123456789'
letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
en_letters = 'abcdefghijklmnopqrstuvwxyz'

today = datetime.datetime.today()
types = ()
type_names_list = []
buyers = ()


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


def get_manufacturers():
    query = "SELECT manufacturer_name FROM manufacturer"
    cursor.execute(query)
    manufacturers_t = cursor.fetchall()
    manufacturers = list(sum(manufacturers_t, ()))
    manufacturers_str = ""
    for man in manufacturers:
        manufacturers_str += man
        manufacturers_str += '\n'
    return manufacturers_str


def get_products():
    query = "SELECT product_name, price, product_type_name FROM product JOIN product_type ON product.product_type_id = " \
            "product_type.product_type_id GROUP BY product_name, price, product_type_name"
    cursor.execute(query)
    products_t = cursor.fetchall()
    products = list(sum(products_t, ()))
    products_str = format_products_price(products)
    return products_str


def format_products(products):
    products_str = ""
    i = 0
    for prod in products:
        if i == 0:
            products_str += "name: "
            products_str += str(prod)
            products_str += ' '
            i += 1
            continue
        elif i == 1:
            products_str += "price: "
            products_str += str(prod)
            products_str += ' '
            products_str += '\n'
            i = 0
            continue

    return products_str


def format_products_price(products):
    products_str = ""
    i = 0
    for prod in products:
        if i == 0:
            products_str += "name: "
            products_str += str(prod)
            products_str += ' '
            i += 1
            continue
        elif i == 1:
            products_str += "price: "
            products_str += str(prod)
            products_str += ' '
            i += 1
            continue
        elif i == 2:
            products_str += "type: "
            products_str += str(prod)
            products_str += '\n'
            i = 0
            continue
    return products_str


def get_products_by_type(prod_type):
    global types
    get_types()
    type = get_type_by_name(prod_type)

    query = "SELECT product_name, price FROM product JOIN product_type ON product.product_type_id = " \
            "product_type.product_type_id WHERE product.product_type_id = (%s) GROUP BY product_name, price" # LIMIT 30 "
    cursor.execute(query, str(type))
    products_t = cursor.fetchall()
    products = list(sum(products_t, ()))
    products_str = format_products(products)

    return products_str


def get_products_by_price(lower):
    if lower:
        query = "SELECT product_name, price, product_type_name FROM product JOIN product_type ON product.product_type_id = " \
                "product_type.product_type_id GROUP BY product_name, price, product_type_name ORDER BY price ASC" # LIMIT 30 "
        cursor.execute(query)
        products_t = cursor.fetchall()
        products = list(sum(products_t, ()))
        products_str = format_products_price(products)
        return products_str
    else:
        query = "SELECT product_name, price, product_type_name FROM product JOIN product_type ON product.product_type_id = " \
                "product_type.product_type_id GROUP BY product_name, price, product_type_name ORDER BY price DESC" # LIMIT 30 "
        cursor.execute(query)
        products_t = cursor.fetchall()
        products = list(sum(products_t, ()))
        products_str = format_products_price(products)
        return products_str


def get_type_by_name(name):
    global types
    get_types()
    type = 0
    for pair in types:
        print(pair[0], pair[1])
        if pair[1] == name:
            type = pair[0]
            break
    if not type:
        print("Couldn't find type")
        return None
    return type


def get_prod_id_by_name(name):
    name_row = tuple((name,))
    query = "SELECT product_id FROM product WHERE product_name = (%s)"
    cursor.execute(query, name_row)

    temp = cursor.fetchall()
    if not temp:
        return 1

    prod_id = temp[0]
    return prod_id


def get_emails():
    global emails
    query = "SELECT email FROM buyer"
    cursor.execute(query)
    emails = list(sum(cursor.fetchall(), ()))
    return emails


def get_buyer_id_by_email(email):
    email_row = tuple((email,))

    query = "SELECT buyer_id FROM buyer WHERE email = (%s)"
    # print(email_row)
    cursor.execute(query, email_row)
    buyer_id = cursor.fetchall()[0]
    return buyer_id


def get_types():
    global types
    cursor.execute("SELECT product_type_id, product_type_name FROM product_type")
    types = cursor.fetchall()


def get_type_names():
    global type_names_list
    cursor.execute("SELECT product_type_name FROM product_type")
    type_names = cursor.fetchall()
    type_names_list = list(sum(type_names, ()))
    # print(str(type_names_list))
    return type_names_list


def add_product(name, price, type, desc):
    global types
    get_types()
    prod_type = get_type_by_name(type)
    if not prod_type:
        return None
    prod_row = tuple((name, price, prod_type, desc), )
    query = "INSERT INTO product (product_name, price, product_type_id, description) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, prod_row)
    return 1


def add_review(bid, pid, rate, text):
    review_row = tuple((bid, pid, rate, text), )
    query = "INSERT INTO review (buyer_id, product_id, rating, text) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, review_row)
    return 1


def find_product_by_name(prod_name):
    prod_id = ""
    return prod_id


def update_buyers():
    global buyers
    cursor.execute("SELECT * FROM buyer")
    buyers = cursor.fetchall()


def get_reviews(email):
    buyer_id = get_buyer_id_by_email(email)
    # buyer_row = tuple((email,))
    query = "SELECT review_id, review.product_id, product_name, price FROM review JOIN product ON product.product_id =" \
            "review.product_id WHERE review.buyer_id = (%s)"
    cursor.execute(query, buyer_id)

    result = cursor.fetchall()

    if result:
        return result
    else:
        return -1


def get_review_ids(email):
    buyer_id = get_buyer_id_by_email(email)
    # buyer_row = tuple((email,))
    query = "SELECT review_id FROM review WHERE review.buyer_id = (%s)"
    cursor.execute(query, buyer_id)

    result = cursor.fetchall()

    if result:
        return result
    else:
        return -1


def get_review_ids_list(email):
    reviews = get_review_ids(email)

    if reviews == -1:
        return -1
    reviews_list = list(sum(reviews, ()))

    return reviews_list


def get_reviews_format(email):
    reviews = get_reviews(email)

    if reviews == -1:
        return -1
    reviews_list = list(sum(reviews, ()))
    # 0 1 2 3
    reviews_str = ""
    i = 0
    for review in reviews_list:
        if i == 0:
            reviews_str += "id: "
            reviews_str += str(review)
            reviews_str += '; '
            i += 1
            continue

        elif i == 1:
            reviews_str += "product id: "
            reviews_str += str(review)
            reviews_str += '; '
            i += 1
            continue

        elif i == 2:
            reviews_str += "product name: "
            reviews_str += str(review)
            reviews_str += '; '
            i += 1
            continue

        elif i == 3:
            reviews_str += "price: "
            reviews_str += str(review)
            reviews_str += ' '
            reviews_str += '\n'
            i = 0
            continue
    return reviews_str


def delete_review(review_id):
    rid_row = tuple((review_id,))
    query = "DELETE FROM review WHERE review_id = (%s)"
    cursor.execute(query, rid_row)


def refactor_product(pid, name, price, desc):
    query_no_desc = "UPDATE product SET product_name = (%s), price = (%s) WHERE product_id = (%s)"
    query_desc = "UPDATE product SET product_name = (%s), price = (%s), description = (%s) WHERE product_id = (%s)"

    if not desc:
        prod_row = tuple((name, price, pid), )
        cursor.execute(query_no_desc, prod_row)

    else:
        prod_row = tuple((name, price, desc, pid), )
        cursor.execute(query_desc, prod_row)
    return


def check_phone(phone):
    phone_row = tuple((phone,))
    query = "SELECT buyer_id FROM buyer WHERE phone = (%s)"
    cursor.execute(query, phone_row)
    result = cursor.fetchall()
    if result:
        return result
    else:
        return 1


def check_mail(email):
    email_row = tuple((email,))
    query = "SELECT buyer_id FROM buyer WHERE email = (%s)"
    cursor.execute(query, email_row)
    result = cursor.fetchall()
    if result:
        return result
    else:
        return 1


def add_buyer(name, phone, email):
    buyer_row = tuple((name, phone, email), )
    query = "INSERT INTO buyer (buyer_name, phone, email) VALUES (%s, %s, %s)"
    cursor.execute(query, buyer_row)
    return


def add_employee(name, phone, email, date_from, date_to):
    buyer_row = tuple((name, phone, email), )
    query1 = "SELECT buyer_id FROM buyer WHERE buyer_name = (%s) AND phone = (%s) AND email = (%s)"
    cursor.execute(query1, buyer_row)
    buyer = cursor.fetchall()
    buyer_id = 0
    if not buyer:
        query2 = "INSERT INTO buyer (buyer_name, phone, email) VALUES (%s, %s, %s)"
        cursor.execute(query2, buyer_row)
        cursor.execute(query1, buyer_row)
        buyer_id = cursor.fetchall()[0]
    else:
        buyer_id = buyer[0]

    employee_row = tuple((date_from, date_to, buyer_id), )
    query3 = "INSERT INTO employee (date_from, date_to, buyer_id) VALUES (%s, %s, %s)"
    cursor.execute(query3, employee_row)
    return
