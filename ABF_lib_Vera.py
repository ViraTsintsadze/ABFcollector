import pyabf as pa               # package for loading abf data
import numpy as np               # for numpy array objects

import scipy.signal as ss

import matplotlib.pyplot as plt

#from tkinter import *
from os import listdir

##############################################################################
#, plots each sweep in subplot with sweep numbers,  
#print message: what to exclude? type separated by comas
#gets: filename (string), range for plotting in secs
# returns N of sweeps
def file_sweep_plot(filename, pl_range):  #giving in points already
    
    #plot range to points fo 50 kmsec sampling
    st_t = pl_range[0]
    end_t = pl_range[1]
    data_file = abf_file_opener (filename)
    # plotting all sweeps
    for sw in range (1, data_file.sweepCount):   #for each sweep
        data_file.setSweep(sw)
        trace = data_file.sweepY[st_t:end_t:5]
        time_ax = data_file.sweepX[st_t:end_t:5]*4
        plt.subplot (3,4,sw)  #subplot always 4X3
        plt.title = filename
        plt.plot(time_ax,trace)
        plt.legend([sw])
        plt.savefig(filename+"resp.png")            
    return data_file.sweepCount

##############################################################################
#opens abf file, reads how many sweeps
def abf_file_opener (filename):
    #check, if there is no '.abf' in filename, add it
    if '.abf' in filename:
        filename=filename
    else:
        filename=filename+'.abf'

    #opening abf file and plotting all sweeps
    data_file = pa.ABF(filename)
    return data_file 

#########################################################################
def lattency (data, diff_tr, minimum_range, sweep): #giving in points already
    drop_index =0
    piece = data[minimum_range[0]:minimum_range[1]]
    filtered = filtering(data, 50, 1000)
    filtered_piece = filtered[minimum_range[0]:minimum_range[1]]
    diff_filtered_piece=np.diff(filtered_piece)
    drop_index_array=np.where(diff_filtered_piece<=diff_tr)   
    if (len(drop_index_array[0])>0):
        drop_index = drop_index_array[0][0]
    plt.subplot (3,4,sweep+1)
    plt.plot(piece, color='k')
    plt.axvline(drop_index , color='r')
    plt.legend([sweep])
    plt.grid()
    
    return drop_index  #in points, from beginning of minimum_range
    
   


 # aver baseline - minimum response, filtered by 200low-pass
def resp_ampl(data, baseline_range, minimum_range): #giving in points already
    bl = data[baseline_range[0]:baseline_range[1]]    
    resp = data[minimum_range[0]:minimum_range[1]]
    amp = np.mean(bl)-np.min(resp) 
    return amp
    

###############################################################
def peak_finder(data, threshold, Sampl_in_mkrsec):   
    #easy peak finding and thresholding those peaks
    #time_ax = 
    Peaks=[]
    filtered_data = filtering(data, Sampl_in_mkrsec, 200)
    (argrelmin_res,) = ss.argrelmin(filtered_data)
    argrelmin_res  = list(argrelmin_res)
    Peaks_tr=[]
    for peak in argrelmin_res:
        if filtered_data[peak]<=threshold:
            Peaks_tr.append(peak)
    plt.plot(data, color='gray')
    plt.plot(filtered_data, color='black')
    plt.plot(argrelmin_res, color='red', marker='.')
    plt.plot(Peaks_tr, color='yellow', marker='*')
    #plt.show()
    plt.savefig("peaks.png")
    return Peaks_tr  #peak indexes, list


def frequency (data, threshold, Sampl_in_mkrsec):
    #using peak_finder(data, threshold, Sampl_in_mkrsec)
    fr = len(peak_finder(data, threshold, Sampl_in_mkrsec))/(len(data)*Sampl_in_mkrsec/1000000)
    return fr


def filtering(data, Sampl_in_mkrsec, lowpass_freq):
    Sampl =1/Sampl_in_mkrsec/1e-6
    Wn = lowpass_freq / (Sampl/2)
    b, a = ss.iirfilter(1, Wn, ftype='butter', btype='low')
    filtered_data = ss.filtfilt(b, a, data)    
    return filtered_data


##################################################################################
def from_secs_to_points(time_in_sec, Sampl_in_mkrsec): #usual is 50
    Sampl =1/Sampl_in_mkrsec/1e-6
    time_in_points = int(round(time_in_sec*Sampl))
    return time_in_points

def from_points_to_secs(time_in_points, Sampl_in_mkrsec):
    Sampl =1/Sampl_in_mkrsec/1e-6
    time_in_sec = time_in_points/Sampl
    return time_in_sec
    


#############################################################################
def abf_files_in_Directory(Directory):  #Directory - string with path
    #choosing abf files, returns list of abf files  
    ABF_files_list=[]
    for files in listdir(Directory):
        if '.abf' in files:
            ABF_files_list.append(Directory+'/'+files)         
    if ABF_files_list==[]:
        messagebox.showinfo("There's no ABF files", "There's no ABF files in the folder")
    ABF_files_list.append(Directory)   #directory is the last in list ABF_files_list
    return (ABF_files_list)



##############################################################################    
def cutter_appender (data, Start,End, Cutoff_from, Cutoff_to): #gets Start,End, Cutoff_from, Cutoff_to in points, not in seconds
    #takes array and cut and append
    new_data = []
    new_data.extend (data[Start:Cutoff_from])
    new_data.extend (data[Cutoff_to:End])
    return (new_data)

################################################################################
def append_files_sweeps(ABF_files_list, Start,End, Cutoff_from, Cutoff_to, wanna_txt):   #gets Start,End, Cutoff_from, Cutoff_to in points, not in seconds
    #append data from files and sweeps and save in txt file
    Big_final_trace=[]
    #check, were directory  window picked
    if ABF_files_list==[]:
        messagebox.showinfo("There's no ABF files", "Please define a directory with ABF files (Directory button)") 
 
    # for every file and sweep, call cutter_appender f-n, extend everything in one Big_final_trace               
    for files in range (len(ABF_files_list)-1):   #for each file, "files" is index
        app_data_file =[]
        data_file = pa.ABF(ABF_files_list[files]) #file open
        
        for sw in range (1, data_file.sweepCount):   #for each sweep
            data_file.setSweep(sw)
            app_data_file.extend (cutter_appender(list(data_file.sweepY),Start,End,Cutoff_from,Cutoff_to))
        Big_final_trace.extend(app_data_file)        
    
    #and save in txt file
    if wanna_txt:
        Big_final_trace_str = "\n".join(str(x) for x in Big_final_trace) #to str separated with tabs
        save_path = ABF_files_list[-1]+'/Big_final_trace.txt'
        ftxt= open(save_path,"w+")
        ftxt.write(Big_final_trace_str)
        ftxt.close()   
    
    return Big_final_trace
    
#####################################################################################
# function separated letters and digits, for filename indexing
def base_n_digit(base_and_digit):  #takes string
    base_part=''
    digit_part=''
    for c in range (len(base_and_digit)):
        if base_and_digit[c].isdigit():
            digit_part=digit_part+base_and_digit[c]
        else:
            base_part=base_part+base_and_digit[c] 
    
    return base_part,digit_part   #returns tuple

#####################################################################################
#function for making list of filenames based on ['from'] and ['to'] collumns, given as strings
def from_to_filenames (from_file, to_file):
    from_file_base, from_file_digit = base_n_digit(from_file)
    to_file_base, to_file_digit = base_n_digit(to_file)
    if from_file_base==to_file_base:
        #make a digit progr
        file_list = []
        how_m_files = int(to_file_digit) - int(from_file_digit) #how many files
        
        for i in range(how_m_files+1):
            new_name_to_append_digit_int = int(from_file_digit)+i
            new_name_to_append_digit_str = str(new_name_to_append_digit_int)
            char_num = len(new_name_to_append_digit_str) #how long in the new number
            new_name_to_append_d = '0'*len(to_file_digit)  #zeros as far
            new_name_to_append_d = new_name_to_append_d [:-char_num]+new_name_to_append_digit_str #substitude zeros with numbers
            file_list.append(from_file_base+new_name_to_append_d) 
            
    else:
        print (from_file, '-->',to_file, "Impossible to define the file sequence")
        
    return file_list #type - list of strings


##################################################################################
def resp_peak_min(data, filt_fr, BaselineBorders, PeakBorders):
    
    returns(peak_ampl,peak_time) #in points 
    