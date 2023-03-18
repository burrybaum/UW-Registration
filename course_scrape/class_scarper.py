import csv
import pandas as pd 
import requests
from bs4 import BeautifulSoup


cse_win_url = 'https://www.washington.edu/students/timeschd/WIN2023/cse.html'
demo_count = 0 

#The function intakes the course schedule from UW and extracts (returns) all the text information 
def extract_page(page_url):
    ticker_response = requests.get(page_url)
    soup = BeautifulSoup(ticker_response.text, 'html.parser')

    #set return values
    course_names = [] 
    course_tickers = []
    course_infos = [] 

    all_cell = soup.find_all('tr')
    for each_tr in all_cell:
        each_tr = each_tr.find('td')
        
        if each_tr.find('pre') is not None:
            each_pre = each_tr.find('pre')
            
            course_info = each_pre.get_text()
            course_infos.append(course_info.split())

        else :
            header_info = each_tr.find_all(['a']) 

            # filter that only contains header info 
            if len(header_info) > 1: 
                course_ticker = header_info[0].get_text()
                course_name = header_info[1].get_text()
                course_tickers.append(course_ticker) 
                course_names.append(course_name)

        '''
        demo_count += 1 
        if demo_count > 25: 
            print('success')  
            break 
        ''' 
    #trim first header  
    course_infos = course_infos[1:]
    return ([course_names, course_tickers, course_infos])

cse_extract = extract_page(cse_win_url)

def assign_class (class_extract): 
    #print(class_extract[0])
    #print(class_extract[1])
    #print(class_extract[2].head(5))
    return(class_extract[0])

assign_class(cse_extract) 

'''
with open('output.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(cse_extract)
''' 