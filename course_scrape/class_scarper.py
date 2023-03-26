import csv
import pandas as pd 
import requests
from bs4 import BeautifulSoup


cse_win_url = 'https://www.washington.edu/students/timeschd/WIN2023/info.html'
demo_count = 0 

info_dictionary = ['Restr', 'SLN', 'ID', 'Cred', 'Meeting', 'Times', 'Bldg/Rm', 'Instructor', 'Status', 'Enrl/Lim']

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
    
    #trim first header 
    course_infos = course_infos[1:]
    trim_set = []

    print(course_infos[3])
    total_class = len(course_infos)
    for i in range (0, total_class):
        if len(course_infos[i]) == 11:
            trim_set.append(course_infos[i])

    return trim_set

cse_extract = extract_page(cse_win_url)


#
print('start')

def clean_course_info (course_info_set):
    #Step 1: Collect SLN, Restriction 
    SLN =[]
    Restr = []
    #Step 2: SectionId, Credit 
    SectionID = []
    Credit = [] 
    #Step 3: Class days, time and location 
    Class_day =[]
    Class_time = [] 
    Classroom_name = [] 
    Classroom_num = []
    Instructor = [] 

    #Step 4: Status, Enrollment (Seat) 
    Status = []
    Fill = []
    Limit = [] 

    for each_info in course_info_set: 
        if each_info[0].startswith("Res") or each_info[0].startswith("IS"):
            #Handle starting with Restriction
            Restr.append(each_info[0])
            each_info.pop(0)
            SLN.append(each_info[0])

        elif each_info[0].startswith(">"):
            #course starting wth > 
            course_with_arrow = each_info[0]
            course_with_arrow = course_with_arrow[1:]
            Restr.append('Empty')
            SLN.append(course_with_arrow)
        else: 
            #Normal cases
            Restr.append('Empty')
            SLN.append(each_info[0])
        
        SectionID.append(each_info[1])        
        
        #Handle #If Lecture -> note Lecture, if quiz -> section ID 
        if each_info[2] != "QZ":
            Credit.append("Lecture")
        else: 
            Credit.append(each_info[2])     

        #handle "to be arranged"
        if each_info[3] == 'to' and each_info[4] == 'be' and each_info[5] == 'arranged':
            Class_day.append('empty')
            Class_time.append('empty')
            Classroom_name.append('empty')
        else: 
            Class_day.append(each_info[3])
            Class_time.append(each_info[4])
            Classroom_name.append(each_info[5])

        Classroom_num.append(each_info[6])

        #handle null 
        if len(each_info[7]) < 5 :
            Instructor.append("undecided")
        else:
            Instructor.append(each_info[7]) 
        

        #
        Status.append(each_info[8])
        Fill.append(each_info[9])
        Limit.append(each_info[10])

    data_set = [SLN, Restr, SectionID, Credit, Class_day, Class_time, Classroom_name, Classroom_num, Instructor, Status, Fill, Limit]
    return(data_set)


final_output_data = clean_course_info(cse_extract)

print('end')

'''
def assign_class(class_extract): 
    cnt = 0 
    #class_extract[1]: course name, [2]: course_ticker, [3]: other info
    class_infos = class_extract[2]
    for class_info in class_infos:
        #print(class_info[1])
        # Logic: if course is A => apply class name and ticker, update each_class info until next A shows up         
        if(class_info[1] == "A") :
            cnt += 1 
            print(cnt)
            #print(each_info[2]) 
        #print(each_class[0])
        #print(each_class[1])
        #print(each_class[2])
    return(class_extract[0])

assign_class(cse_extract) 
'''

with open('CSE_extract.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(final_output_data)
