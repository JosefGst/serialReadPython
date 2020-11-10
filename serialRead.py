import serial                   #to get serial data
import matplotlib.pyplot as plt #for ploting
import numpy as np              #for FFT
from scipy.signal import find_peaks  #find peaks of FFT
import time




#open serial port
ser = serial.Serial(port='COM7', baudrate=115200,timeout=1, bytesize=8, stopbits=1, parity='N')

#check serial connection
if ser.is_open:
    print("connected to serial port, press Button to take measurements")
else: #if not connected, connect now
    print("is now connecting to serial port")
    ser = serial.Serial(port='COM7', baudrate=115200, bytesize=8, stopbits=1, parity='N')
    print("is now connected to serial port")
   
datalist = []
timelist = []
peakIndex = []
duration = 0.0
hertz = 0
threshhold = 2e5

while True: #main infinit loop
    
    while ser.inWaiting() > 0: #reads data only if there's data coming 
        data = ser.readline()
        data = data.replace(' \r\n', '')
        try:
            datalist.append(int(data))
        except:
            print("error at reading")

        print(data)  
        time.sleep(.01)

        if ser.inWaiting() == False: # if no more messages do all the data processing                      
            hertz = datalist.pop()              #the last entry is the frequancy
            duration = float(datalist.pop())    #the second last entry is the duration of all measurments
            n = len(datalist) 
            for i in range(n):  #calculate the time vector
                timeVal = duration * (i+1) / n 
                timelist.append(timeVal)

            #FFT#################################################################
            fhat = np.fft.fft(datalist,n)   #compute FFT
            PSD = fhat * np.conj(fhat) / n
            freq = 1000 / duration * np.arange(n) #1000 because duration is in ms
            L = np.arange(1, np.floor(n/2), dtype = 'int')

            #use PSD to filter out noise ########################################
            indices = PSD > threshhold         #find all freq with large power
            PSDclean = PSD * indices    #zero out all others
            fhat = indices * fhat       #zero out small Fourier coeffs in Y
            ffilt = np.fft.ifft(fhat)   #inverse FFT

            peaks, _ = find_peaks(PSDclean[0:n/2])
            
                

            #plot ###############################################################
            
            fig,axs = plt.subplots(2, 1)
            plt.sca(axs[0])
            plt.title("Time Domain\r\nDuration: " + str(duration) + " [ms], Frequancy: " + str(hertz) + " [Hz]")
            plt.xlabel('Time [ms]')
            plt.ylabel('Acceleration [mg]')
            plt.plot(timelist, datalist, label = 'accel Z')
            plt.plot(timelist, ffilt, label = 'filtered aZ')
            plt.legend()
            plt.grid()

            plt.sca(axs[1])
            plt.title("FFT PSD")
            plt.xlabel('Frequancy [Hz]')
            plt.ylabel('Power [g^2]?')
            plt.plot(freq[L], PSD[L], LineWidth = 3, label = 'PSD')
            plt.plot(freq[L], PSDclean[L], label = 'filtered PSD')
            plt.plot(freq[peaks], PSDclean[peaks], "x")
            plt.legend()
            plt.text(10, 100, '%4.2f' % freq[peaks])
            plt.grid()
            #plt.xscale("log")
            #plt.yscale("log")

            plt.tight_layout()  #prevents the axis label and the title of the subplots to overlap
            plt.show()

            datalist = []
            timelist = []
            duration = 0.0
            hertz = 0
  
    
          


    

    
        