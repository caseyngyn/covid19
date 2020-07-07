'''
Casey Nguyen
CIS 41b
front end of lab 3 using sql tables form lab3 backend

'''

#cur.execute('''SELECT * FROM CovidDB WHERE Country NOT IN
#               ("North America","South America","Europe","Asia", "Africa","Oceania","World") ''')


import matplotlib
matplotlib.use('TkAgg')               # tell matplotlib to work with Tkinter
import tkinter as tk                    # normal import of tkinter for GUI
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Canvas widget
import matplotlib.pyplot as plt         # normal import of pyplot to plot
import os
from os import path
import tkinter.messagebox as tkmb
import sys
import sqlite3
import numpy as np

class MainWindow(tk.Tk):
    def __init__(self,*filenames):
        super().__init__()
        self.continents = ["North America","South America","Europe","Asia", "Africa","Oceania","World"]
        self.title('Covid-19 Cases')
        self.geometry("500x200")
        conn = sqlite3.connect('covid.db')
        self.cur = conn.cursor()

        #L1
        self.cur.execute('''SELECT COUNT(*) FROM CovidDB
                            WHERE Country NOT IN (?,?,?,?,?,?,?)''',self.continents)
        country_num = int(self.cur.fetchone()[0])
        str1 = tk.StringVar()
        str1.set("Worldwide: "+str(country_num)+" countries")
        L1 = tk.Label(textvariable = str1)
        L1.grid(row=0,column = 0,sticky = 'w')

        #L2
        str2 = tk.StringVar()
        self.cur.execute('SELECT TotCasesPer1Mpop FROM CovidDB WHERE country = "World"')
        str2.set("Worldwide: "+str(self.cur.fetchone()[0])+" cases per 1M people")
        L2 = tk.Label(textvariable = str2)
        L2.grid(row= 1,column = 0,columnspan = 2,sticky = 'w')

        #L3
        str3 = tk.StringVar()
        self.cur.execute('SELECT DeathPer1Mpop FROM CovidDB WHERE country = "World"')
        str3.set("Worldwide: "+str(self.cur.fetchone()[0])+" deaths per 1M people")
        L3 = tk.Label(textvariable = str3)
        L3.grid(row= 2,column = 0,columnspan = 2,sticky = 'w')
        
        self.make_buttons()
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

    def on_exit(self):
        '''
        This function opens a message box asking if the user wants to quit
        Then quits out of the program if the user clicks yes
        '''
        if tkmb.askyesno("Exit", "Do you want to quit the application?"):
            self.quit()

    def make_buttons(self):
        '''
        function makes buttons
        '''
        self.rowconfigure(1, weight=0)      # column where the widget is
        self.button_frame = tk.Frame(self)
        self.button_frame.grid(row = 3, column = 0,padx = 10,pady = 10)

        #button 1
        self.new_cases = tk.Button(self.button_frame,text = 'New Cases',command = self.show_new_cases)
        self.new_cases.grid(row=3, column=0, padx=15, pady=10)

        #button 2
        self.top_twenty = tk.Button(self.button_frame,text = 'Top 20 Cases',command = self.show_top_twenty)
        self.top_twenty.grid(row=3, column=1, padx=15, pady=10)

        #button 3
        self.cmp_countries = tk.Button(self.button_frame,text = 'Compare Countries',command = self.show_countries)
        self.cmp_countries.grid(row=3, column=2, padx=15, pady=10)

    def show_new_cases(self):
        ''' button 1 logic '''
        header = [('Country','New Cases','New Deaths')]
        self.cur.execute("""SELECT Country, NewCases FROM CovidDB WHERE Country NOT IN ("World")
                            ORDER By NewCases DESC""")
        highest_continent = self.cur.fetchall()[0]
        self.cur.execute("""SELECT Country, NewCases, NewDeaths FROM CovidDB
                            WHERE Country NOT IN (?,?,?,?,?,?,?) AND NewCases != 0
                            ORDER BY NewCases DESC """, self.continents)
        case_list = header + self.cur.fetchall()
        print(case_list)
        DisplayWin(self,1,case_list,highest_continent)
        
    def show_top_twenty(self):
        '''button 2 logic'''
        header = [('Country','Cases / 1 million people','New Deaths','Deaths / 1 million people','Tests / 1 million people')]
        self.cur.execute("""SELECT Country, TotCasesPer1Mpop, DeathPer1mPop,TestsPer1mPop FROM CovidDB
                    WHERE Country NOT IN (?,?,?,?,?,?,?)
                    ORDER BY TotalCases DESC """, self.continents)
        top_twenty = self.cur.fetchall()
        top_twenty = top_twenty[0:20]
        top_twenty = header + top_twenty
        DisplayWin(self,2,top_twenty)
    
    def show_countries(self):
        '''button 3 logic'''
        self.cur.execute("SELECT Country FROM CovidDB ORDER BY Country ")
        country = self.cur.fetchall()
        dwin = DialogWin(self,country)
        self.wait_window(dwin)
        choices_idx = dwin.get_choices()
        if choices_idx:
            chosen_country_name = []
            chosen_country_case = []
            for i in choices_idx:
                chosen_country_name.append(str(country[i]).strip('(,\')'))
                temp = []
                temp.append(str(country[i]).strip('(,\')'))
                self.cur.execute("""SELECT TotCasesPer1Mpop 
                        FROM CovidDB WHERE Country IN (?) ORDER BY Country""",temp)
                case = self.cur.fetchone()[0]
                chosen_country_case.append(case)

            PlotWin(chosen_country_name, chosen_country_case)



class PlotWin(tk.Toplevel):
    def __init__(self,x,y):
        super().__init__()
        self.fig = plt.figure(figsize=(8,8))
        self.focus_set()
        self.x_axis = x
        self.y_axis = y
        self.plot()
        canvas = FigureCanvasTkAgg(self.fig, master=self)
        canvas.get_tk_widget().grid()
        canvas.draw() 

    def plot(self):
        ''' plot points'''
        plt.bar(np.arange(0,len(self.x_axis)),np.array(self.y_axis))
        plt.title('Number of Cases for Chosen Countries')
        plt.xlabel('Countries')
        plt.ylabel('Number of Cases per 1M People')
        plt.xticks(np.arange(0,len(self.x_axis)),np.array(self.x_axis))
        plt.tick_params(axis = 'x', rotation = 45, labelsize = 7)



class DisplayWin(tk.Toplevel):
    def __init__(self,master,button_no,*args):
        super().__init__(master)
        #self.focus_set()     # comment this out to see the effect
        #self.grab_set()      # comment this out to see the effect
        self.transient(master)    # comment this out to see the effect (on Windows system)
        if button_no == 1:
            self.display_new_cases(*args)
        elif button_no ==2:
            self.display_top_twenty(*args)

    def display_new_cases(self,*args):
        '''show all countries with new cases'''
        option_frame = tk.Frame(self)
        self.title('New Cases')
        S = tk.Scrollbar(option_frame,orient = "vertical")
        self.Lb = tk.Listbox(option_frame,height = 10,width = 50, selectmode = "multiple",yscrollcommand = S.set)
        S.pack(side = "right",fill = "y")
        self.Lb.pack()
        S.config(command = self.Lb.yview)
       
        self.Lb.insert(tk.END,*args[0])

        option_frame.pack()
        self.protocol("WM_DELETE_WINDOW",self.delete)
        str1 = tk.StringVar()
        str1.set("Highest "+str(args[1][1])+" new cases in "+args[1][0])
        tk.Label(self,textvariable = str1).pack()

    def display_top_twenty(self,*args):
        '''
        Show top 20 countries
        '''
        self.title('Top Twenty')
        option_frame = tk.Frame(self)
        self.Lb1 = tk.Listbox(option_frame,height = 21,width = 100, selectmode = "multiple")
        self.Lb1.pack()
        self.Lb1.insert(tk.END,*args[0])
        option_frame.pack()
        self.protocol("WM_DELETE_WINDOW",self.delete)       

    def delete(self):
        ''' exits the window'''
        self.destroy()

class DialogWin(tk.Toplevel):
    def __init__(self,master,country_list):
        super().__init__(master)
        self.cursor = () #have to have so no error if user don't select anything
        self.title('Choose Countries')
        self.focus_set()     # comment this out to see the effect
        self.grab_set()      # comment this out to see the effect
        self.transient(master)    # comment this out to see the effect (on Windows system)
        option_frame = tk.Frame(self)
        S = tk.Scrollbar(option_frame,orient = "vertical")
        self.Lb = tk.Listbox(option_frame,height = 10,width = 50, selectmode = "multiple",yscrollcommand = S.set)
        S.pack(side = "right",fill = "y")
        self.Lb.pack()
        S.config(command = self.Lb.yview)
       
        self.Lb.insert(tk.END,*country_list)
        self.Lb.bind("<<ListboxSelect>>",self.poll)

        option_frame.pack()
        tk.Button(self,text = "OK", command = self.destroy).pack()

        self.protocol("WM_DELETE_WINDOW",self.delete)

    def poll(self,*args):
        '''get cursor selection'''
        self.cursor = self.Lb.curselection()

    def delete(self):
        '''exits the window '''
        self.cursor = ()
        self.selected = None
        self.destroy()

    def get_choices(self):
        '''returns index of college names to the Main Win'''
        return self.cursor

def main():
    app = MainWindow()
    app.mainloop()
main()