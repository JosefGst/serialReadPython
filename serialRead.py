import serial                   #to get serial data
import matplotlib.pyplot as plt #for ploting
import numpy as np              #for FFT
from scipy.signal import find_peaks  #find peaks of FFT
from datetime import datetime
import os                       #to create a folder
import pandas as pd             #create csv file

# CONFIGURATION:
SAVING = 1
filename = 'JOSEF_TOURQUE_0040_TEST'

#open serial port
ser = serial.Serial(port='COM17', baudrate=115200, bytesize=8, stopbits=1, parity='N')

#check serial connection
if ser.is_open:
    print("connected to serial port")
else: #if not connected, connect now
    print("is now connecting to serial port")
    ser = serial.Serial(port='COM17', baudrate=115200, bytesize=8, stopbits=1, parity='N')
    print("is now connected to serial port")
   
datalist = []
timelist = []
peakIndex = []
duration = 0.0
hertz = 0
counter = 0

print('Press Button to take measurements!\n')
while True: #main infinit loop   
    if counter%1000 == 1:
        print("please wait!")
    data = ser.readline() #waits until data is to read
    data = data.replace(' \r\n', '')
    if not ("this is the end" in data): #if "this is the end" has not reached, continue appending & reading the data
        datalist.append(float(data))
        counter += 1
        #print(data)                  
    else:     #if 'this is the end' messages arrives, do all the data processing                 
        hertz = datalist.pop()              #the last entry is the frequancy
        duration = float(datalist.pop())/1000    #the second last entry is the duration of all measurments
        nEntries = len(datalist) 
        for i in range(nEntries):  #calculate the time vector
            timeVal = duration * (i+1) / nEntries 
            timelist.append(timeVal)

        #FFT#################################################################
        fhat = np.fft.fft(datalist,nEntries)   #compute FFT
        PSD = fhat * np.conj(fhat) / nEntries
        freq = 1 / duration * np.arange(nEntries) #1000 because duration is in ms
        L = np.arange(1, np.floor(nEntries/2), dtype = 'int')

        #use PSD to filter out noise ########################################
        threshhold = max(PSD[1:])/2
        indices = PSD > threshhold         #find all freq with large power
        PSDclean = PSD * indices    #zero out all others
        fhat = indices * fhat       #zero out small Fourier coeffs in Y
        ffilt = np.fft.ifft(fhat)   #inverse FFT

        peaks, _ = find_peaks(PSDclean[0:nEntries/2])      # get peaks of the filtered PSD
            

        #plot ###############################################################
        
        fig,axs = plt.subplots(2, 1)
        plt.sca(axs[0])
        plt.title("Time Domain\nDuration: " + str(duration) + " [s], Frequancy: " + str(hertz) + " [Hz]")
        plt.xlabel('Time [s]')
        plt.ylabel('Acceleration [mg]')
        plt.plot(timelist, datalist, label = 'accel Z')
        #plt.plot(timelist, ffilt, label = 'filtered aZ')
        plt.legend()
        plt.grid()

        plt.sca(axs[1])
        plt.title("FFT PSD")
        plt.xlabel('Frequancy [Hz]')
        plt.ylabel('Power [g^2]?')
        plt.plot(freq[L], PSD[L], LineWidth = 3, label = 'PSD')
        #plt.plot(freq[L], PSDclean[L], label = 'filtered PSD')
        plt.plot(freq[peaks], PSDclean.real[peaks], "x" )
        for x, y in zip(freq[peaks], PSDclean.real[peaks]): #plot the nuvalues to the peaks
            plt.text(x, y, " %.2f Hz" % x)
        plt.legend()
        plt.grid()
        #plt.xscale("log")
        #plt.yscale("log")
        plt.tight_layout()  #prevents the axis label and the title of the subplots to overlap
        

        if SAVING is 1:   
            now = datetime.now()
            directory_filename = "D:\\RA_PROJECT\\" + now.strftime('%Y_%m\\%d') #create '<month>/<day>' folder
            # check wether the folder exists
            if not os.path.exists(directory_filename):
                os.mkdir(directory_filename)  
            i = 1
            while(i > 0):
                if not os.path.isfile(directory_filename + '\\' + filename + '{}.png'.format(i)):
                    # save the plot
                    plt.savefig(directory_filename + '\\' + filename + '{}.png'.format(i), dpi=300)
                    print(directory_filename + '\\' + filename + '{}.png'.format(i))
                    print('Plot file saved')

                    #save Excel
                    df1 = pd.DataFrame({'datapoints [mg]': datalist, 'Time [s]': timelist})
                    df2 = pd.DataFrame({'PSD [Power]': PSD.real[L], 'Freq [Hz]': freq[L]})
                    #print (df1, df2)
                    with pd.ExcelWriter(directory_filename + '\\' + filename + '{}.xlsx'.format(i)) as writer: #write each dataframe to another sheet
                        df1.to_excel (writer, sheet_name='Time Domain')
                        df2.to_excel (writer, sheet_name='PSD')
                    print(directory_filename + '\\' + filename + '{}.xlsx'.format(i))
                    print('Excle file saved')
                    i = 0 # ends the while loop
                else:
                    i += 1
            
            
            
                
        plt.show()
        datalist = []
        timelist = []
        duration = 0.0
        hertz = 0
        counter = 0
        print('Press Button to take new measurements!\n')
                
  
    
          


    

    
        