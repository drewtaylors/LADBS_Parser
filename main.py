import csv
import time
from selenium.common.exceptions import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

ADDRESS_BOOK = 'sample.csv'
RECORD_BOOK = 'records.csv'

addresses = []
record_collection = []

with open(ADDRESS_BOOK, 'rb') as address_book:
    reader = csv.reader(address_book)
    for row in reader:
        addresses.append(row[0])

driver = webdriver.Chrome()

for address in addresses:

    driver.get('http://ladbsdoc.lacity.org/IDISPublic_Records/idis/DefaultCustom.aspx')
    assert 'Document Search Selection' in driver.title

    elem = driver.find_element_by_id('lnkBtnAddress')
    elem.click()
    while ('Document Search' not in driver.title):
        driver.get('http://ladbsdoc.lacity.org/IDISPublic_Records/idis/DefaultCustom.aspx')
        elem = driver.find_element_by_id('lnkBtnAddress')
        elem.click()

    elem = driver.find_element_by_name('Address$txtAddress')
    elem.send_keys(address)
    elem.send_keys(Keys.RETURN)

    try:
        table = driver.find_element_by_id('dgAddress1')
        print('dgAddress1')
    except NoSuchElementException:
        table = driver.find_element_by_id('grdIdisResult')
        print('grdIdisResult')
    except UnexpectedAlertPresentException:
        print('no records found')
        alert = driver.switch_to.alert
        alert.accept()
        continue

    rows = table.find_elements_by_tag_name('tr')

    for row in rows[1:]:
        record = [address]
        elems = row.find_elements_by_tag_name('td')

        for elem in elems[1:]:
            record.append(elem.text)

        record_collection.append(record)

with open(RECORD_BOOK, 'wb') as record_book:
    writer = csv.writer(record_book)
    for i in record_collection:
        print i
        writer.writerow(i)

driver.close()



