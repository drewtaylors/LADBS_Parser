from __future__ import print_function
import sys
import csv
import os
from selenium.common.exceptions import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from multiprocessing import Pool, cpu_count

def run_parallel_selenium_processes(datalist, selenium_func):
    pool = Pool()

    # max number of parallel process
    ITERATION_COUNT = cpu_count()-1

    count_per_iteration = len(datalist) / float(ITERATION_COUNT)

    for i in range(0, ITERATION_COUNT):
        list_start = int(count_per_iteration * i)
        list_end = int(count_per_iteration * (i+1))
        pool.apply_async(selenium_func, [datalist[list_start:list_end]])

class LADBS_Parser:

    # Class variables
    addresses = []
    record_collection = []
    total_addresses = 0
    addresses_searched = 0
    no_results = 0
    total_records = 0

    def __init__(self, address_book='sample.csv', 
                    record_book='records.csv', 
                    multiprocess=False):
        if '.csv' in address_book:
            self.address_book = address_book
        else:
            print('Please enter a valid input file (.csv)')
        if '.csv' in record_book:
            self.record_book = record_book
        else:
            print('Please enter a valid output file (.csv')
        self.multiprocess =  multiprocess

        # Fill list with addresses from .csv file (will start at index 0)
        with open(self.address_book, 'rb') as ab:
            reader = csv.reader(ab)
            for row in reader:
                self.addresses.append(row[0])
        self.total_addresses = len(self.addresses)
        
    def start(self):
        if self.multiprocess:
            self.record_collection.append(self.multiprocess_parse())
        else:
            self.record_collection = self.singleprocess_parse(self.addresses)

        # Write records into new .csv file
        with open(self.record_book, 'wb') as rb:
            writer = csv.writer(rb)
            for rec in self.record_collection:
                writer.writerow(rec)

        print('Addresses Searched: ' + str(addresses_searched) 
                + '/' + str(total_addresses) + ', '
                + 'No Records: ' + str(no_results) + ', '
                + 'Total Records: ' + str(total_records))

    def singleprocess_parse(self, addresses):
        # Initiate browser
        driver = webdriver.Chrome(os.getcwd()+'/chromedriver')
        records = []

        for address in addresses:
            # Go to website
            driver.get('http://ladbsdoc.lacity.org/IDISPublic_Records/idis/DefaultCustom.aspx')

            # Go to address search, repeatedly try if session failure
            elem = driver.find_element_by_id('lnkBtnAddress').click()

            # put this into a function
            while ('Document Search' not in driver.title):
                driver.get('http://ladbsdoc.lacity.org/IDISPublic_Records/idis/DefaultCustom.aspx')
                elem = driver.find_element_by_id('lnkBtnAddress').click()

            # Search for address in DB
            elem = driver.find_element_by_name('Address$txtAddress')
            elem.send_keys(str(address))
            elem.send_keys(Keys.RETURN)
            self.update_record_data(self.addresses_searched)

            # Look for table of docs on page, if none then address has no search results
            # if driver.find_element_by_id == dgAddress1, need to parse further
            try:
                table = driver.find_element_by_id('dgAddress1')
                driver.find_element_by_name('chkAddress1All').click()
                driver.find_element_by_name('btnNext3').click()
                self.expand_records(driver, records, address) 
            except NoSuchElementException:
                self.expand_records(driver, records, address)
            except UnexpectedAlertPresentException:
                alert = driver.switch_to.alert
                alert.accept()
                self.update_record_data(self.no_results)
                continue

        # Close web browser
        driver.close()

        return records

    def multiprocess_parse(self):
        print('hi')
        return 0

    def update_record_data(self, field):
        field += 1
        sys.stdout.flush()
        print('Addresses Searched: ' + str(self.addresses_searched) 
                + '/' + str(self.total_addresses) + ', '
                + 'No Records: ' + str(self.no_results) + ', '
                + 'Total Records: ' + str(self.total_records), end='\r')

    def expand_records(self, driver, records, address):
        # select all addresses
        while True:
            table = driver.find_element_by_id('grdIdisResult')

            # Parse through table and append results to record_collection
            rows = table.find_elements_by_tag_name('tr')

            for row in rows[1:]:
                record = [address]
                elems = row.find_elements_by_tag_name('td')

                for elem in elems[1:]:
                    record.append(elem.text)

                records.append(record)
                self.update_record_data(self.total_records)

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

if __name__ == '__main__':

    # Read filenames for input and output files
    input_file = raw_input('Please enter an input filename (.csv): ')
    output_file = raw_input('Please enter an output filename (.csv): ')

    if input_file == '' and output_file == '':
        parser = LADBS_Parser()
    elif input_file == '' and output_file:
        parser = LADBS_Parser(record_book=output_file)
    elif input_file and output_file == '':
        parser = LADBS_Parser(address_book=input_file)
    else:
        parser = LADBS_Parser(input_file, output_file)
    
    parser.start()
