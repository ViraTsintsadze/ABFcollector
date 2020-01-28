import pyabf as pa               # package for loading abf data
import numpy as np               # for numpy array objects
from pyabf.abfWriter import writeABF1
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import filedialog
from os import listdir


window = Tk()
window.title("Appending files and sweeps")


def cust_checked():
    Cust_from.configure(state="normal")
    Cust_from.update()
    Cust_to.configure(state="normal")
    Cust_to.update()
    Cust_cut_from.configure(state="normal")
    Cust_cut_from.update()
    Cust_cut_to.configure(state="normal")
    Cust_cut_to.update()
    return

def cust_unchecked():
    Cust_from.configure(state=DISABLED)
    Cust_from.update()
    Cust_to.configure(state=DISABLED)
    Cust_to.update()
    Cust_cut_from.configure(state=DISABLED)
    Cust_cut_from.update()
    Cust_cut_to.configure(state=DISABLED)
    Cust_cut_to.update()
    return


def make_ABF_files_list():
    ABF_files_list =  list(filedialog.askopenfilenames(filetypes=[("ABF Files",".abf")]))
    #get directory part
    rev = ABF_files_list[0][::-1] #revers path
    sl = rev.find('/') #find first slash
    revDir = rev[sl :] #takes path from slash
    Directory = revDir[::-1] #reverse back to normal
    ABF_files_list.append(Directory)   #directory is the last in list ABF_files_list
    return (ABF_files_list)

    
def cutter_appender (data, Start,End, Cutoff_from, Cutoff_to):
    #takes array and cut and append
    new_data = []
    if (Cutoff_from>0 or Cutoff_from>0):
        new_data.extend (data[Start:Cutoff_from])
        new_data.extend (data[Cutoff_to:End])
    else:
        new_data.extend (data[Start:End])
    for i in range (len(new_data)-1):
        new_data[i]= new_data[i].astype(int)
    return (new_data)


def Times_point(L):
    Times_points = []
    if selected.get() == 1:
        cust_unchecked()
        Start_End = [0,1.0] #first second, in samples
        Start = int(round(Start_End[0]*Sampl))
        Times_points.append(Start)
        End = int(round(Start_End[1]*Sampl))
        Times_points.append(End)
        Cutoff_piece=[0,0]
        Cutoff_from = int(round(Cutoff_piece[0]*Sampl))
        Times_points.append(Cutoff_from)
        Cutoff_to = int(round(Cutoff_piece[1]*Sampl))
        Times_points.append(Cutoff_to)
    elif selected.get() == 2:
        cust_unchecked()
        Start_End = [1.2,2.2] #after stimulation, sr measurement cut off, in samples 
        Start = int(round(Start_End[0]*Sampl))
        End = int(round(Start_End[1]*Sampl))
        Cutoff_piece = [0,0] 
        Cutoff_from = int(round(Cutoff_piece[0]*Sampl))
        Cutoff_to = int(round(Cutoff_piece[1]*Sampl))
        Times_points.append(Start)
        Times_points.append(End)
        Times_points.append(Cutoff_from)
        Times_points.append(Cutoff_to)
    elif selected.get() == 3:  #custom
        Start = int(round(float(Cust_from.get())*Sampl))
        End = int(round(float(Cust_to.get())*Sampl))
        Cutoff_from = int(round(float(Cust_cut_from.get())*Sampl))
        Cutoff_to = int(round(float(Cust_cut_to.get())*Sampl))
        Times_points.append(Start)
        Times_points.append(End)
        Times_points.append(Cutoff_from)
        Times_points.append(Cutoff_to)
    elif selected.get() == 4: #whole file
        Times_points = [0,L-1,0,0]
    return Times_points


def btn_append_clicked():
    #append data from files and sweeps and save in txt file
    textDone.set(" ")
    global Sampl
    Sampl =int(1000000/float(Sampling_var.get()))
    print("Sampl= ", Sampl)
    ABF_files_list = make_ABF_files_list()
    Big_final_trace=[]
    # for every file and sweep, call cutter_appender f-n, extend everything in one Big_final_trace               
    #Times_points = Times_point()
    for files in range (len(ABF_files_list)-1):   #for each file, "files" is index
        app_data_file =[]
        data_file = pa.ABF(ABF_files_list[files]) #file open
        for sw in range (0, data_file.sweepCount):   #for each sweep
            data_file.setSweep(sw)
            Times_points = Times_point(L=len(data_file.sweepY))
            #Times_points = Times_point(int(len(data_file.sweepY)))
            app_data_file.extend (cutter_appender(list(data_file.sweepY),Times_points[0],Times_points[1],Times_points[2],Times_points[3]))
        Big_final_trace.extend(app_data_file)        
        #save in abf
        
    outp_f_n='from'+str(Times_points[0])+'to'+str(Times_points[1])
    print(ABF_files_list)
    #getting folder name 
    str1 = ABF_files_list[len(ABF_files_list)-1]
    pos =str1[:-1:][::-1].find('/')
    foldn = str1[-pos-1:-1]
    writeABF1(np.array([Big_final_trace ]), ABF_files_list[files+1]+foldn+outp_f_n+'.abf', units='pA')
    
    textDone.set("Done!")
    return 

#ABF_files_list=[]

textDone=StringVar()
textDone.set("")
LabelDone = Label(window, textvariable= textDone)
LabelDone.grid(column=0, row=8, columnspan=4)    

#button to make the append heppend
btn_append = Button(window, text="Append", command=btn_append_clicked)
btn_append.grid(column=0, row=3, columnspan=2)

Label(window, text="Sampling").grid(column=0, row=6, columnspan=2, sticky="W")
Sampling_var = StringVar(window, value='50')
Sampling_en = Entry(window, textvariable=Sampling_var, width=5)
Sampling_en.grid(column=0, row=7)
Label(window, text="mks").grid(column=1, row=7, sticky="W")
Sampl =int(1000000/float(Sampling_var.get()))

#radiobuttons 
selected=IntVar()
Spon = Radiobutton(window, text="Spontaneous-first second", value=1, variable=selected) 
Post = Radiobutton(window, text="Post-stimulation", value=2, variable=selected, command=cust_unchecked)
Cust = Radiobutton(window, text="Custom", value=3, variable=selected, command=cust_checked)
Wholef = Radiobutton(window, text="Entire file", value=4, variable=selected, command=cust_unchecked)

Spon.grid(column=2, row=1,sticky="W",columnspan=2)
Post.grid(column=2, row=2,sticky="W",columnspan=2)
Cust.grid(column=2, row=3,sticky="W",columnspan=2)
Wholef.grid(column=2, row=4,sticky="W",columnspan=2)

Label(window, text="From").grid(column=3, row=4,sticky="E")
Label(window, text="To").grid(column=3, row=5,sticky="E")
Label(window, text="Cut from ").grid(column=3, row=6,sticky="E")
Label(window, text="Cut to ").grid(column=3, row=7,sticky="E")

Zerro_var_f = StringVar(window, value='0')
Zerro_var_cf = StringVar(window, value='0')
Zerro_var_t = StringVar(window, value='0')
Zerro_var_ct = StringVar(window, value='0')
Cust_from = Entry(window,state=DISABLED, width=10, textvariable=Zerro_var_f)
Cust_to =Entry(window,state=DISABLED, width=10, textvariable=Zerro_var_t)
Cust_cut_from =Entry(window,state=DISABLED, width=10, textvariable=Zerro_var_cf)
Cust_cut_to =Entry(window,state=DISABLED, width=10, textvariable=Zerro_var_ct)

Cust_from.grid(column=4, row=4,sticky="E")
Cust_to.grid(column=4, row=5,sticky="E")
Cust_cut_from.grid(column=4, row=6)
Cust_cut_to.grid(column=4, row=7)

Spon.invoke()

window.mainloop()
