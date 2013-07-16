#!/usr/bin/env python

#This version is created to take the word decription of lateness/earlyness from the Amtrak File
#It will then parse it into a numeric lateness and output it in the format:
# Train No,Date,delay (in minutes)

import matplotlib.pyplot as plt
import numpy as np
import datetime

def movingaverage(interval, window_size):
    window= np.ones(int(window_size))/float(window_size)
    return np.convolve(interval, window, 'same')

def parse_status(word_status):
    if word_status.find('hour') == -1: #no hours
        if word_status[1] == ' ': #single digit status
            number_status = word_status[0]
        else: #two digit status
            number_status = word_status[0:2]
    elif word_status.find('hours') > 0 and word_status[2] == ' ': #10+ hours late/early
        if word_status.find('min') == -1:
            hour = int(word_status[0:3])
            number_status = hour * 60
        elif word_status[14] == ' ': #single digit minutes
            hour = int(word_status[0:3])
            minutes = int(word_status[13])
            number_status = (hour*60) + minutes
        else:
            hour = int(word_status[0:3])
            minutes = int(word_status[13:15])
            number_status = (hour*60) + minutes
    elif word_status.find('hours') > 0: #2-9 digit hours
        if word_status.find('min') == -1:
            hour = int(word_status[0:2])
            number_status = hour * 60
        elif word_status[13] == ' ': #single digit minutes
            hour = int(word_status[0:2])
            minutes = int(word_status[12])
            number_status = (hour*60) + minutes
        else:
            hour = int(word_status[0:2])
            minutes = int(word_status[12:14])
            number_status = (hour*60) + minutes
    else: #1 hour status
        if word_status.find('min') == -1:
            number_status = 60
        elif word_status[2] == ' ': #single digit minutes
            hour = int(word_status[0:2])
            minutes = int(word_status[11])
            number_status = (hour*60) + minutes
        else:
            hour = int(word_status[0:2])
            minutes = int(word_status[11:13])
            number_status = (hour*60) + minutes 
    return number_status

file_error = 0
train_number = '27'
m = 0
delay_times = []
delay_dates = []
date = []

while m <=11:
    m = m + 1
    if m < 10:
        month = '0'+str(m)
    else:
        month = str(m)


    j = 0
    while j <= 30: #j is day counter - will try 31 days for each month - need to figre out how many known file errors will result
        j = j+1
        if j<10: #needed to add leading zero in some file formats
            j_str = '0'+str(j)
            input_file = '27_2012'+month+j_str+'.txt'
            #print(input_file)
            #print(month)
        else:
            j_str = str(j)
            input_file = '27_2012'+month+j_str+'.txt'
            #print(input_file)
        j = int(j)

        try:  #try to open files - if the file open fails, the else increments the file_error and moves on to the next file
            #fout = open('27_PDX_2012.csv', 'a')
            fin = open(input_file, 'r')
        
            data_line = fin.readline()
        
            #print(j)
            date = month+'/'+j_str+'/2012'
        
            i = 0 #skips the 11 header lines to get to the good stuff
            while i < 11:
                data_line = fin.readline()
                i = i + 1
        
            while data_line:
                station = data_line[2:5]
                if station == 'PDX' and len(data_line) > 30 and data_line[0] == '*': #checks to see the line contains valid data and picks the station in question
                    #print(station)
                    if data_line[37] == 'D': #Checks for "Departed:"
                        status = data_line[48:(len(data_line)-3)]
                    else:
                        status = data_line[47:(len(data_line)-3)] #arrived status starts 1 charcter left
                    #print(status)
                    if status[0:2] == 'on': #looking for 'on time'
                        delay = 0
                    else:
                        delay = int(parse_status(status))
                        if status[(len(status)-2):len(status)] == 'rl':
                            delay = delay * -1
                    output = train_number+","+date+","+station+","+str(delay)
                    #fout.write(output)
                    #fout.write('\n')
                    delay_times.append(delay)
                    date = datetime.date(2012, m, j)
                    delay_dates.append(date)
                    print(output)
                data_line = fin.readline()
            fin.close()
            #fout.close()
        except IOError:
            file_error += 1
print('Files Skipped:')
print(file_error)

plt.figure(1)
plt.plot(delay_dates, delay_times, "b.")
delay_times_avg = movingaverage(delay_times, 10)
plt.plot(delay_dates, delay_times_avg, "b", linewidth=5)
plt.xticks(rotation=30)

plt.figure(2)
hist, bins = np.histogram(delay_times,bins = 50)
width = 0.7*(bins[1]-bins[0])
center = (bins[:-1]+bins[1:])/2
plt.bar(center, hist, align = 'center', width = width)
plt.xticks(np.arange(-60, 720, 60.0))
plt.suptitle('Train #27 Delay into PDX')
plt.xlabel('Delay (in minutes)')
plt.ylabel('Number of Occurances')
plt.show()