#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  6 10:23:40 2022

@author: changruiquan
"""

import os
import string

os.chdir(r'/Users/changruiquan/Documents/GitHub')

def readtxt():
    f = open('2005proposal_clean.pdf.txt')
    data ="msa,base,action,mil_out,civ_out,mil_in,civ_in,mil_net,civ_net,net_contr,direct,indirect,total,ea_emp,ch_as_perc"
    f1 = open('question2.csv','a')
    f1.write(data)
    line1 = ''
    line2 = ''
    str = ''
    m = n = 0
    pointer = 0    # check if the format looks like the first row
    line = f.readline()
    while line:
        i = len(line)
        if line[i-2] == '%':            # if the last character of the line is %
            s = line.replace(' ','\n')  # substitute with \n
            s = s.replace(',', '')      # delete ',' between the numbers
            list = s.splitlines()       # split words and numbers
            if (list[1].find('(')!=-1 or list[1].isnumeric()) and list[1].strip('()').isnumeric() and list[0] != 'Total':    
                # if the second word has '(' and the first word is not 'Total', then the first word of the line should be 'action'
                pointer = 1   
                k = len(list)
                if n==0:
                    str = str0.replace(',', '') + "," + str3.replace(',', '')
                else:
                    str = str0.replace(',', '') + "," + str1.replace(',', '')     # str0 - 'msa', str1 - 'base'
                for i in range(k):
                    str = str + "," + list[i]
                f1.write('\n' + str)
                m = 0
                n = 1
            elif (list[1].find('(')!=-1 or list[1].isnumeric()) and list[0] == 'Total':      
                # if the second word has '(' and the first word is 'Total'，then omit this line and go to next two lines
                str0 = f.readline().strip('\n')    # next line should be 'msa'
                table_end_line = str0.replace(' ', '\n')  
                table_end_line = table_end_line.replace(',', '')
                list_tel = table_end_line.splitlines()
                if list_tel[0] == "This":
                    m=1
                    str0 = line2.replace(',',' ')
                    str1 = line1.replace(',', ' ')
                else:
                    str0 = str0.replace(',',' ')
                    str1 = f.readline().strip('\n')     # next line should be 'base'
                    str1 = str1.replace(',', '')
                    i=len(str1)
                    if str1[i-1]  == '%':
                        s = str1.replace(' ', '\n')
                        s = s.replace(',', '') 
                        list = s.splitlines()  
                        for i in range(len(list)):
                            if list[i].find('(') != -1 or list[i].isnumeric():
                                j = i - 1
                                break
                        for i in range(len(list)):
                            if i == 0:
                                str = str0 + "," + list[i]
                            elif i < j:
                                str = str + " " + list[i]
                            else:
                                str = str + "," + list[i]
                        f1.write('\n' + str)
                    str3 = str1
            elif pointer == 0:    # when pointer = 0
                for i in range(len(list)):
                    if list[i].find('(') != -1 or list[i].isnumeric():
                        j = i - 1
                        break
                for i in range(len(list)):
                    if i == 0:
                        str = str0 + "," + list[i]
                    elif i < j:
                        str = str + " " + list[i]
                    else:
                        str = str + "," + list[i]
                f1.write('\n' + str)
                pointer = 1
            else:    # if 'base' has multiple words, e.g. 'Kirtland Air Force Base'
                for i in range(len(list)):
                    if list[i].find('(') != -1 or list[i].isnumeric():
                        if list[i].strip('()').isnumeric():
                            j=i-1
                            break
                if m == 0:
                    for i in range(len(list)):
                        if i==0:
                            str = str0 + "," + list[i]
                        elif i<j:
                            str = str + " " + list[i]
                        else:
                            str = str + "," + list[i]
                    f1.write('\n' + str)
                elif m == 1:
                    str0 = line1.replace(',', '')
                    for i in range(len(list)):
                        if i==0:
                            str = str0 + "," + list[i]
                        elif i<j:
                            str = str + " " + list[i]
                        else:
                            str = str + "," + list[i]
                    f1.write('\n' + str)
                    m = 2
                else:
                    for i in range(len(list)):
                        if i==0:
                            str = str0 + "," + list[i]
                        elif i<j:
                            str = str + " " + list[i]
                        else:
                            str = str + "," + list[i]
                    f1.write('\n' + str)
        else:
            str1 = line.strip('\n')
        line2 = line1.strip('\n')
        line1 = line.strip('\n')
        if m==1:
            str0 = line2.replace(',', ' ')
            str1 = line1.replace(',', ' ')
        if pointer==0:
            str0 = line1.replace(',', ' ')
        line = f.readline()
    f.close()
    f1.close()

def cleanfile():    # some lines in the original txt file doesn't have blank lines
    f = open('2005proposal.pdf.txt')
    f1 = open('2005proposal_clean.pdf.txt','a')
    line = f.readline()
    while line:
        data = line.replace('% ', '%\n')     # add a blank line after all '%' (end of a row)
        f1.write(data)
        line = f.readline()
    f.close()
    f1.close()


if __name__ == '__main__':
    cleanfile()
    readtxt()

