from __future__ import print_function
import sys
import csv
import os
from selenium.common.exceptions import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

ADDRESS_BOOK = 'sample.csv'
RECORD_BOOK = 'records.csv'

addresses = []
record_collection = []
console = {
    'total_addresses': 0,
    'addresses_searched': 0,
    'no_results': 0,
    'total_records': 0,
}


def update_console(field):
    console[field] += 1
    sys.stdout.flush()
    print('Addresses Searched: ' + str(console['addresses_searched']) 
            + '/' + str(console['total_addresses']) + ', '
            + 'No Records: ' + str(console['no_results']) + ', '
            + 'Total Records: ' + str(console['total_records']), end='\r')


def expand_records(address):
    # select all addresses
    while True:
        try:
            table = driver.find_element_by_id('grdIdisResult')
        except NoSuchElementException:
            update_console('no_results')
            break

        # Parse through table and append results to record_collection
        rows = table.find_elements_by_tag_name('tr')

        for row in rows[1:]:
            record = [address]
            elems = row.find_elements_by_tag_name('td')

            for elem in elems[1:]:
                record.append(elem.text)

            record_collection.append(record)
            update_console('total_records')

        try:
            indexes = driver.find_element_by_id('pnlNavigate')
            current_index = int(indexes.find_element_by_css_selector('font').text)
            if current_index % 10 != 0:
                driver.execute_script("goPage('" + str(current_index+1) + "')")
            else:
                driver.execute_script("goPage('" + str(current_index+1) + "N')")
        # Reached the end of the loop
        except NoSuchElementException:
            break    


# Read filenames if none use defaults
input_file = raw_input('Please enter an input filename (.csv): ')
output_file = raw_input('Please enter an output filename (.csv): ')
if '.csv' in input_file:
    ADDRESS_BOOK = input_file
else:
    print('Using default input file - ', str(ADDRESS_BOOK))
if '.csv' in output_file:
    RECORD_BOOK = output_file
else:
    print('Using default output file - ', str(RECORD_BOOK))

# Fill list with addresses from .csv file (will start at index 0)
with open(ADDRESS_BOOK, 'rb') as address_book:
    reader = csv.reader(address_book)
    for row in reader:
        addresses.append(row[0])
console['total_addresses'] = len(addresses)
        
# Initiate browser
driver = webdriver.Chrome(os.getcwd()+'/chromedriver')

for address in addresses:
    # Go to website
    driver.get('http://ladbsdoc.lacity.org/IDISPublic_Records/idis/DefaultCustom.aspx')

    # Go to address search, repeatedly try if session failure
    elem = driver.find_element_by_id('lnkBtnAddress').click()

    # put this into a function
    while ('Document Search' not in driver.title):
        driver.get('http://ladbsdoc.lacity.org/IDISPublic_Records/idis/DefaultCustom.aspx')
        elem = driver.find_element_by_id('lnkBtnAddress')
        elem.click()

    # Search for address in DB
    elem = driver.find_element_by_name('Address$txtAddress')
    elem.send_keys(str(address))
    elem.send_keys(Keys.RETURN)
    update_console('addresses_searched')

    # Look for table of docs on page, if none then address has no search results
    # if driver.find_element_by_id == dgAddress1, need to parse further
    try:
        table = driver.find_element_by_id('dgAddress1')
        checkbox = driver.find_element_by_name('chkAddress1All').click()
        continue_button = driver.find_element_by_name('btnNext3').click()
        expand_records(address) 
    except NoSuchElementException:
        expand_records(address)
    except UnexpectedAlertPresentException:
        alert = driver.switch_to.alert
        alert.accept()
        update_console('no_results')
        continue

# Close web browser
driver.close()

# Write records into new .csv file
with open(RECORD_BOOK, 'wb') as record_book:
    writer = csv.writer(record_book)
    for rec in record_collection:
        writer.writerow(rec)

print('Addresses Searched: ' + str(console['addresses_searched']) 
            + '/' + str(console['total_addresses']) + ', '
            + 'No Records: ' + str(console['no_results']) + ', '
            + 'Total Records: ' + str(console['total_records']))
