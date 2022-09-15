# -*- coding = utf-8 -*-
# @Time : 2022/8/10 9:49
# @Auther : Ruiquan
# @Fuke : readexcel.py
# @Software: PyCharm

import xlrd
import xlwt
import os
import PySimpleGUI as sg
import pandas as pd
import codecs
import time


# GUI page
def main():
    flag = login()
    if flag:
        layout = [
            [sg.Text('Please input keywords')],
            [sg.Text('Keyword1', size=(15, 1)), sg.InputText()],
            [sg.Text('Keyword2', size=(15, 1)), sg.InputText()],
            [sg.Text('Keyword3', size=(15, 1)), sg.InputText()],
            [sg.Text('Type', size=(15,1)), sg.Combo(['All','ACABQ','Secretary General'],default_value='All')],
            [sg.Text('Symbol', size=(15,1)), sg.Combo(['All','A/76/613','A/76/782','A/77/6'],default_value='All')],
            [sg.Text('Date', size=(15,1)), sg.Combo(['All','2/7/2022','2/11/2022','2/17/2022','2/23/2022',
                                                     '2/28/2022','3/18/2022','3/21/2022','3/9/2022',
                                                     '3/10/2022','6/24/2022'],default_value='All')],
            [sg.Submit()]
        ]
        window = sg.Window('File Retrieval System Demo', layout)
        while True:
            button, values = window.read()
            if button == sg.WIN_CLOSED or button == 'Bye!': # program shutdown
                break
            if button:  # click 'submit' button
                inter_xls_file = "database.xls"  # source data file
                result_xls_file = "result3.xls"  # keywords search result file
                result_xls_file1 = "result.xls"  # condition filter result file
                if values[3] == "All" : # if 'All', no limitations
                    values[3] = ""
                if values[4] == "All" :
                    values[4] = ""
                if values[5] == "All" :
                    values[5] = ""
                if len(values[3]) + len(values[4]) + len(values[5]) == 0:
                    my_search = search_kw(values[0], values[1], values[2], inter_xls_file, result_xls_file1, 0)
                else:
                    my_search = search_kw(values[0], values[1], values[2], inter_xls_file, result_xls_file, 0)
                    search_kw(values[3], values[4], values[5], result_xls_file, result_xls_file1, 1)
                if my_search == 0:
                    sg.popup("Please enter your search terms")
                    continue
                str = result_presentation(values[0],values[1],values[2])
                if str == 0: # if no string, pop up window
                    sg.popup("The keyword was not found",title="Not retrieved")
            if os.path.exists('result.html'):   # open the file when it exists
                kw1 = values[0].casefold()
                kw2 = values[1].casefold()
                kw3 = values[2].casefold()
                font_color(kw1,kw2,kw3)
                remove_n() # delete \r\n in the html file
                os.system(r'start result.html')
            if os.path.exists("result.xls"):
                os.remove("result.xls")  # delete temp file
            if os.path.exists("result3.xls"):
                os.remove("result3.xls")
            if os.path.exists('result.html'):
                time.sleep(1)
                #os.remove('result.html')  
        window.close()


# one keyword filter: retrieve results with specific kewords from inter_xls, and output to dest_xls
def read_excel(kw,inter_xls,dest_xls,col_num):
    if col_num == 0:
        col_num = 9 # retrieve the 9th column 'question'
    workbook = xlrd.open_workbook(inter_xls)   # read intermediate file "inter.xls"
    result_xls = xlwt.Workbook(encoding="ascii")    
    wsheet = result_xls.add_sheet('search results')
    sheetnum = workbook.nsheets
    kw1 = kw.casefold() # transfer to lower cases
    y = 0      
    for m in range(0,sheetnum):
        sheet = workbook.sheet_by_index(m)  
        nrowsnum = sheet.nrows 
        for i in range(0,nrowsnum):
            data = sheet.row(i)      
            for n in range(0,len(data)):
                data_column = str(data[col_num])     
                lower_case_data_column = data_column.casefold()  
                if lower_case_data_column.find(kw1)>0:  # keywords filter: yes then 1, no then 0
                    y = y+1
                    for j in range(len(data)):
                        wsheet.write(y,j,sheet.cell_value(i,j))
                break   
        result_xls.save(dest_xls)


# multiple keywords filter: retrieve all the three keywords in source file and create result file
def search_kw(kw1,kw2,kw3,inter_xls_file,result_xls_file,col_num):
    temp_xls_file1 = "result1.xls"
    temp_xls_file2 = "result2.xls"
    if len(kw3) == 0:
        if len(kw2) == 0:
            if len(kw1) == 0:  # no kws
                return 0
            else:
                read_excel(kw1, inter_xls_file, result_xls_file,col_num*3)  # kw1
        elif len(kw1) != 0:  # kw1 & kw2
            read_excel(kw2, inter_xls_file, temp_xls_file1,col_num*1)
            read_excel(kw1, temp_xls_file1, result_xls_file,col_num*3)
        else:
            read_excel(kw2, inter_xls_file, result_xls_file,col_num*1)  # kw2
    elif (len(kw2) != 0) and (len(kw1) != 0):  # kw1 & kw2 & kw3
        read_excel(kw3, inter_xls_file, temp_xls_file2,col_num*5)
        read_excel(kw2, temp_xls_file2, temp_xls_file1,col_num*1)
        read_excel(kw1, temp_xls_file1, result_xls_file,col_num*3)
    elif len(kw2) != 0 and len(kw1) == 0:  # kw2 & kw3
        read_excel(kw3, inter_xls_file, temp_xls_file2,col_num*5)
        read_excel(kw2, temp_xls_file2, result_xls_file,col_num*1)
    elif len(kw1) != 0 and len(kw2) == 0:  # kw1 & kw3
        read_excel(kw3, inter_xls_file, temp_xls_file2,col_num*5)
        read_excel(kw1, temp_xls_file2, result_xls_file,col_num*3)
    else:  # kw3
        read_excel(kw3, inter_xls_file, result_xls_file,col_num*5)
    if os.path.exists(temp_xls_file1):
        os.remove(temp_xls_file1)
    if os.path.exists(temp_xls_file2):
        os.remove(temp_xls_file2)


# create html page
def result_presentation(kw1,kw2,kw3):
    xd = pd.ExcelFile('result.xls')
    df = xd.parse()
    #print("3333", df)
    col = ["ID","Symbol","Reference","Type","Subject","Date","Year","Number","Category","Question","Answer","Attachments"]  #列名，最大12列
    if not df.empty:    # if not empty, open the browser
        col_num = df.shape[1]   
        df.columns = col[0:col_num] 
        html_str = df.to_html(header=True, index=False, col_space=60)
        # display style
        style = '''
        <style>
            table{
                border-spacing:0;  
            }
            th{
                text-align:center;vertical-align:middle;
            }
            td{
                text-align:justify;vertical-align:middle;
            }
        </style>
        
        '''
        # add title
        if len(kw1) !=0 and len(kw2) !=0 and len(kw3) !=0:  #123
            keywd01 = "(" + kw1 + ")(" + kw2 + ")(" + kw3 + ")"
            title_kw01 =  "(ZZZ" + kw1 + ")(ZZZ" + kw2 + ")(ZZZ" + kw3 + ")"
        elif len(kw1) !=0 and len(kw2) !=0 and len(kw3) ==0:    #12
            keywd01 = "(" + kw1 + ")(" + kw2 + ")"
            title_kw01 = "(ZZZ" + kw1 + ")(ZZZ" + kw2 + ")" 
        elif len(kw1) !=0 and len(kw2) ==0 and len(kw3) !=0:    #13
            keywd01 = "(" + kw1 + ")(" + kw3 + ")"
            title_kw01 = "(ZZZ" + kw1 + ")(ZZZ" + kw3 + ")" 
        elif len(kw1) ==0 and len(kw2) !=0 and len(kw3) !=0:    #23
            keywd01 = "(" + kw2 + ")(" + kw3 + ")"
            title_kw01 = "(ZZZ" + kw2 + ")(ZZZ" + kw3 + ")" 
        elif len(kw1) !=0 and len(kw2) ==0 and len(kw3) ==0:    #1
            keywd01 = kw1
            title_kw01 = "(ZZZ" + kw1 + ")" 
        elif len(kw1) ==0 and len(kw2) !=0 and len(kw3) ==0:    #2
            keywd01 = kw2
            title_kw01 = "(ZZZ" + kw2 + ")" 
        else:
            keywd01 = kw3
            title_kw01 = "(ZZZ" + kw3 + ")" 
        keywd = keywd01.casefold()
        my_title = f'<title>{title_kw01}</title>  <h1>Search Results for keyword: <font color="red">{keywd}</font></h1>'
        html_str = style + my_title + html_str
        html_str = style + html_str
        with codecs.open('result.html', 'w', 'utf-8') as html_file:
            html_file.write(html_str)
        return keywd
    else:
        return 0


# keywords highlight for html page
def font_color(kw1,kw2,kw3):
    if len(kw1) != 0:
        kw11 = " "+kw1
        replace_kw(kw1,kw11,"red")
        kw11 = " " + kw1.capitalize()
        replace_kw(kw1, kw11, "red")
        kw11 = " " + kw1.upper()
        replace_kw(kw1, kw11, "red")
    if len(kw2) != 0:
        kw22 = " " + kw2
        replace_kw(kw2,kw22,"green")
        kw22 = " " + kw2.capitalize()
        replace_kw(kw2, kw22, "green")
        kw22 = " " + kw2.upper()
        replace_kw(kw2, kw22, "green")
    if len(kw3) != 0:
        kw33 = " " + kw3
        replace_kw(kw3,kw33,"blue")
        kw33 = " " + kw3.capitalize()
        replace_kw(kw3, kw33, "blue")
        kw33 = " " + kw3.upper()
        replace_kw(kw3, kw33, "blue")


# explaination sentance for html page
def replace_kw(title_kw,kw,kwcolor):
    replace_text = fr"<mark> <b> <font color = {kwcolor}>" + kw +"</font></b></mark>"
    with open(r'result.html', 'r', encoding='UTF-8') as file:
        data = file.read()
        data = data.replace(kw, replace_text)
        title_kw1 = "ZZZ"+title_kw
        data = data.replace(title_kw1, title_kw)    
    with open(r'result.html', 'w', encoding='UTF-8') as file:
        file.write(data)


# delete \r\n in htmla page and set column width/height
def remove_n():
    with open(r'result.html', 'r', encoding='UTF-8') as file:
        data = file.read()
        data = data.replace(r"\r\n","<br/>")
        data = data.replace(r"•\t", "  ")
        data = data.replace(r"• \t", "  ")
        data = data.replace(r"\t", "  ")
        data = data.replace(r"\n• ", "<br/>")
        data = data.replace(r"\n", "<br/>")
        str1 = "<th style=\"min-width: 60px;\">Reference</th>"
        str2 = "<th style=\"min-width: 160px;\">Reference</th>"
        data = data.replace(str1, str2) 
        str1 = "<th style=\"min-width: 60px;\">Subject</th>"
        str2 = "<th style=\"min-width: 250px;\">Subject</th>"
        data = data.replace(str1, str2)
        str1 = "<th style=\"min-width: 60px;\">Number</th>"
        str2 = "<th style=\"min-width: 100px;\">Number</th>"
        data = data.replace(str1, str2)  
        str1 ="<th style=\"min-width: 60px;\">Question</th>"
        str2 = "<th style=\"min-width: 400px;\">Question</th>"
        data = data.replace(str1,str2)  
        str1 = "<th style=\"min-width: 60px;\">Answer</th>"
        str2 = "<th style=\"min-width: 500px;\">Answer</th>"
        data = data.replace(str1, str2) 
    with open(r'result.html', 'w', encoding='UTF-8') as file:
        file.write(data)


# login form: main page
def login():
    # login page
    sg.theme_button_color("red")
    sg.theme_text_element_background_color("white")
    sg.theme_background_color("gray")
    sg.theme_text_color("black")
    layout = [
        [sg.Txt("Create account")],
        [sg.Txt("Username", size=(8, 1)), sg.InputText("", key="-user-")],
        [sg.Txt("Password", size=(8, 1)), sg.InputText("", tooltip="Enter a password", password_char="*", key="-pwd-")],
        [sg.Button("Log in"), sg.Button("Join"), sg.Button("Forgot password"), sg.Button("Exit")],
    ]
    # show login window
    window = sg.Window("Login", layout)
    while True:
        flag = False
        # read user information
        event, values = window.read()
        if event == "Log in":
            with open("upd.txt", 'r', encoding='utf-8') as f:
                user = f.readline()
                while len(user) != 0:
                    user_id, user_passwd = user.split()
                    if user_id == values['-user-'] and values['-pwd-'] == user_passwd:
                        # if password corret, allow login
                        flag = True
                        msg = "正在登录中，请稍后！"
                        lst = [[sg.Txt(msg)]]
                        window.close()
                        return [user_id, user_passwd]
                    else:
                        user = f.readline()
                if flag == False:
                    # if password incorrect, pop up window
                    lst = [[sg.Txt("Incorrect username or password entered. Please try again！")], [sg.Button("Submit")]]
                    msg_window = sg.Window("Please try again", lst)
                    event, values = msg_window.read()
                    if event == "Submit":
                        msg_window.close()
                        continue
        if event == "Join":
            # sign in page
            Enroll()
        if event == 'Forgot password':
            # find password page
            Recall_passwd()
        if event == 'Exit' or event == None:
            return 0
            break
    window.close()


# login form: reset password
def Reset_passwd(user_name, user_passwd):
    with open("upd.txt", 'r', encoding='utf-8') as f:
        # read all the users' information
        lines = f.readlines()
    with open("upd.txt", 'w', encoding='utf-8') as f:
        # rewrite
        for l in lines:
            if user_name == l[:len(user_name)]:
                f.write(user_name + ' ' + user_passwd + '\n')
            else:
                f.write(l)
    return


# login form: recall password
def Recall_passwd():
    layout = [[sg.Txt("Please input username："), sg.InputText('', key='name')],
              [sg.Button('Submit')]]
    re_window = sg.Window('Retrieve password', layout)
    event, values = re_window.read()
    if event == 'Submit':
        user_name = values['name']
        with open("upd.txt", 'r', encoding='utf-8') as f:
            user = f.readline()
            while len(user) != 0:
                user_id, user_passwd = user.split()
                if user_id == user_name:
                    # find password through user name
                    re_window.close()
                    lst = [[sg.Txt("Please input password", size=(15, 1)), sg.InputText("", tooltip="Please input password", key="-pwd-")],
                           [sg.Txt("Confirm password", size=(16, 1)),
                           sg.InputText("", tooltip="Confirm password", password_char="*", key="-pwds-")],
                            [sg.Button("Submit"), sg.Button('Exit')]]
                     # if pass the second level password, show recall page
                    reset_window = sg.Window('Reset password', lst)
                    while True:
                        event, values = reset_window.read()
                        if event == "Submit":
                            user_passwd = values["-pwd-"]
                            user_passwds = values["-pwds-"]
                            if user_passwd == user_passwds:
                                f.close()
                                Reset_passwd(user_name, user_passwd)
                                reset_window.close()
                                return
                            else:
                                # make sure to enter the same password twice
                                sg.popup_auto_close('The passwords you entered do not match！', auto_close_duration=2)
                else:
                    user = f.readline()
            f.close()


# login form: sign in page
def Enroll():
    screen = [
        [sg.Txt("Please input username", size=(18, 1)), sg.InputText("", tooltip="Please input username", key="-user_id-")],
        [sg.Txt("Enter a password", size=(18, 1)), sg.InputText("", tooltip="Enter a password", key="-pwd-")],
        [sg.Txt("Confirm password", size=(18, 1)), sg.InputText("", tooltip="Confirm password", key="-pwds-")],
        [sg.Button("Submit"), sg.Button('Exit')]
    ]
    enroll_window = sg.Window("Joining", screen)
    pdno_window_active = False
    while True:
        event, values = enroll_window.read()
        if event == "Submit":
            user_id = values['-user_id-']
            user_passwd = values["-pwd-"]
            user_passwds = values["-pwds-"]
            if user_passwd == user_passwds:
                with open("upd.txt", 'a', encoding='utf-8') as f:
                    f.write(user_id + ' ' + user_passwd + '\n')
                    f.close()
                enroll_window.close()
                break
            elif not pdno_window_active:
                pdno_window_active = True
                lst = [
                    [sg.Txt("The passwords you entered do not match！")],
                    [sg.Button("OK")]
                ]
                pdno_window = sg.Window("Please input again", lst)
                event, values = pdno_window.read()
                if event == "OK":
                    pdno_window_active = False
                    pdno_window.close()
        if event == 'Exit' or event == None:
            enroll_window.close()
            break


if __name__ == "__main__":
    main()


