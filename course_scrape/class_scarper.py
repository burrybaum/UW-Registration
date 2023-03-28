import csv
import pandas as pd 
import requests
import numpy as np 
from bs4 import BeautifulSoup


course_win_url = 'https://www.washington.edu/students/timeschd/WIN2023/info.html'

data_dictionary = ['SLN', 'Course_Name', 'Section', 'Limit', 'Class day', 'Class Time', 'Prereq', 'Required Section Amount']
#Prereq is not includes in this version

#The function intakes the course schedule from UW and extracts (returns) all the text information 
def extract_catalog(page_url):
    ticker_response = requests.get(page_url)
    soup = BeautifulSoup(ticker_response.text, 'html.parser')

    #Scrape course ticker, name and information for all listed courses
    course_tickers = []
    course_names = [] 
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
    #Course Pair 
    course_pair = [course_tickers, course_names]    
    #trim first header 
    course_infos = course_infos[1:]
    return (course_infos, course_pair) 

web_extract = extract_catalog(course_win_url)

#Step 1. extract each row from web 
#Step 2. loop over each row, fetch [SLN, SectionID, ClassType, Class_day, Class_time]
#Step 3. iterate each rows and fetch total class seats 

print('start')

def clean_course_info(web_extract):
    all_information = web_extract

    #Step 1: Collect SLN (Restriction for exception handle) 
    SLN =[]
    Restr = []
    #Step 2: SectionId, ClassType 
    SectionID = []
    ClassType = [] 
    #Step 3: Class days, Class time 
    Class_day =[]
    Class_time = [] 
    #Step 4: Total Seat 
    Limit = []

    for each_info in all_information: 
        if each_info[0].startswith("Res") or each_info[0].startswith("IS"):
            #Handle starting with Restriction
            Restr.append(each_info[0])
            each_info.pop(0)
            SLN.append(each_info[0])

        elif each_info[0].startswith(">"):
            #course starting wth '>' 
            course_with_arrow = each_info[0]
            course_with_arrow = course_with_arrow[1:]
            Restr.append('Empty')
            SLN.append(course_with_arrow)
        else: 
            #Normal cases
            Restr.append('Empty')
            SLN.append(each_info[0])
        
        SectionID.append(each_info[1])        
        
        #Handle #If ClassType -> note Lecture, if quiz -> section ID 
        print(each_info[2])
        if each_info[2] == "QZ":
            ClassType.append(each_info[2])
        elif each_info[2] == "LB":
            ClassType.append(each_info[2])
        elif each_info[2] == "SM":
            ClassType.append(each_info[2])
        else: 
            ClassType.append("Lecture")     

        #handle "to be arranged"
        if each_info[3] == 'to' and each_info[4] == 'be' and each_info[5] == 'arranged':
            Class_day.append('empty')
            Class_time.append('empty')
        else: 
            Class_day.append(each_info[3])
            Class_time.append(each_info[4])

        #Collect seat by iterating each_info 
        each_info_length = len(each_info)
        for i in range(each_info_length-1): 
            if '/' in each_info[i][-1]:
                Limit.append(each_info[i+1])
    
    target_set = [SLN, SectionID, ClassType, Class_day, Class_time, Limit]
    print(ClassType)
    print(len(SLN), len(SectionID), len(ClassType), len(Class_day), len(Limit))
    return(target_set)

#Collect the target information (descriped in the above data dictionary)
filter_data = clean_course_info(web_extract[0])

#Run to add customized columns for NFT mint 
def customize_for_contract(course_pair, filter_data): 
    #Add [Course Name, Required Section Amount']
    Course_Name = [] 
    all_sectionID = filter_data[1]
    
    #print(filter_data[2])
    course_pair_cnt = 0 
    for each_sectionID in all_sectionID: 
        '''
        if each_sectionID == "A":
            Course_Name.append(course_pair[course_pair_cnt])
            course_pair_cnt += 1
            print(course_pair_cnt)
        '''
    Section_Amount = [] 

    combine_data = np.concatenate((filter_data, Course_Name , Section_Amount))
    return combine_data 

print('end')

final_data = customize_for_contract(web_extract[1], filter_data)

with open('CSE_extract.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(final_data)
