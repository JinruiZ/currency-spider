import pymysql

from urllib import request
from bs4 import BeautifulSoup


class currency_item(object):
    def __init__(self, code, num_code, currency_name, region):
        self.code = code
        self.num_code = num_code
        self.currency_name = currency_name
        self.region = region


class html_parser(object):
    def __init__(self, url):
        self.url = url

    def parser(self):
        response = request.urlopen(self.url)

        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')

        currency_items = []

        find_body = soup.find('tbody')
        for item in find_body.children:
            try:
                elements = []
                for content in item.children:
                    if content != '\n':
                        for attr in content.children:
                            elements.append(' '.join(attr.string.split()))
            except:
                continue

            if len(elements) == 4:
                currency_items.append(
                    currency_item(code=elements[2],
                                  num_code=elements[3],
                                  currency_name=elements[1],
                                  region=elements[0]))

        return currency_items


def main():
    url = "https://www.iban.com/currency-codes"

    cur_parser = html_parser(url)
    currency_items = cur_parser.parser()

    conn = pymysql.connect(host='host',
                           port='port',
                           user='username',
                           passwd='passwd',
                           db='db')
    cur = conn.cursor()

    insert_currency = 'insert into currency (code, numericCode, currencyName, region) values(%s,%s,%s,%s)'
    get_currency = (
        'select * from currency where '
        'code = %s and numericCode = %s and currencyName = %s and region = %s')

    for item in currency_items:
        try:
            res = cur.execute(
                get_currency,
                (item.code, item.num_code, item.currency_name, item.region))
            if res is None:
                cur.execute(insert_currency, (item.code, item.num_code,
                                              item.currency_name, item.region))
        except Exception as e:
            print(e)

    conn.commit()
    cur.close()
    conn.close()


main()