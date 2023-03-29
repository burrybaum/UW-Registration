import csv
import pandas as pd 
import requests
import numpy as np 
from bs4 import BeautifulSoup

course_win_url = 'https://www.washington.edu/students/timeschd/WIN2023/info.html'

data_dictionary = ['SLN', 'Course_Name', 'Section', 'Required Section Amount', 'Limit', 'Class day', 'Class Time']
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

#Step 1. extract each row from web 
#Step 2. loop over each row, fetch [SLN, SectionID, ClassType, Class_day, Class_time]
#Step 3. iterate each rows and fetch total class seats 
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
        
        #Handle Class types
        #If ClassType -> note Lecture, if quiz -> section ID 
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
    target_set = [SLN, SectionID, Limit, Class_day, Class_time]
    #print(len(SLN), len(SectionID), len(ClassType), len(Class_day), len(Limit))
    return(target_set)

#Run to add customized columns for NFT mint 
#Returns dataset(lists) with updated course name and required amount of section 
def customize_for_contract(course_pair, filter_data): 
    #Add [Course Name, Required Section Amount']
    section_Amount = [] 
    update_course_name = [] 
    update_course_ticker = [] 

    #split input parameters 
    all_sectionID = filter_data[1]
    course_tickers = course_pair[0]
    course_names = course_pair[1]

    class_cnt = len(all_sectionID)

    pair_cnt = 0 
    for i in range(class_cnt):  
        #binding
        #Fill same course untill the next class shows up 
        if all_sectionID[i] == "A": 
            #Update course name, ticker 
            pair_cnt += 1
            update_course_ticker.append(course_tickers[(pair_cnt - 1)].replace("\xa0","" ).replace(" ", ""))   
            #Since the first value is always a Lecture
            update_course_name.append(course_names[(pair_cnt - 1)])
        else: 
            update_course_ticker.append(course_tickers[(pair_cnt - 1)].replace("\xa0","" ).replace(" ", ""))
            update_course_name.append(course_names[(pair_cnt - 1)])

        #Fill same course untill the next class shows up 
        #If one digit and the following is not, then does not have a section 
        if len(all_sectionID[i]) == 1 and i+1 < class_cnt and len(all_sectionID[i+1]) == 1:
            section_Amount.append('0')
        #if the class has the lab, quiz, or seminar, indicate the number 
        else:
            section_Amount.append('1')
        
        if len(all_sectionID[-1]) == 1: 
            section_Amount[-1] = 0

        #filter ">"
        all_sln = filter_data[0]
        filter_data[0] = [each_sln.replace('>', '') for each_sln in all_sln]

        #Filter "E"
        all_limit = filter_data[2]
        filter_data[2] = [each_limit.replace('E', '') for each_limit in all_limit]
        

    #print(len(update_course_name), len(update_course_ticker), len(all_sectionID), len(section_Amount))
    combine_dataset = filter_data + [update_course_ticker] + [update_course_name] + [section_Amount]
    return combine_dataset
         
#The function intakes the filtered file, and convert into data frame, with a target order 
def frame_data(final_data):
    df = pd.DataFrame({'SLN': final_data[0], 
                       'Course Name': final_data[6],
                       'Course Ticker': final_data[5], 
                       'Section': final_data[1],
                       'Required Section Amount': final_data[7], 
                       'Limit': final_data[2], 
                       'Class Day': final_data[3], 
                       'Class Time': final_data[4]
                       })
    return df


#Collect samples 
sample_major_list = ['cse', 'info', 'econ', 'phil']
time_periods = ['WIN2023', 'SPR2023']

for sample_major in sample_major_list: 
    
    for each_period in time_periods: 
        course_url = 'https://www.washington.edu/students/timeschd/' + each_period + '/' + sample_major  +'.html'
        #Run functions 
        web_extract = extract_catalog(course_url)
        #Collect the target information (descriped in the above data dictionary)
        filter_data = clean_course_info(web_extract[0])
        #Customize the filtered data to fit the NFT contract 
        final_data = customize_for_contract(web_extract[1], filter_data)
        #Convert to csv file format
        final_dataframe = frame_data(final_data)
        #Log in csv 
        final_dataframe.to_csv('course_scrape/sample_csv/' + sample_major + '_' + each_period + '.csv', index=False)

