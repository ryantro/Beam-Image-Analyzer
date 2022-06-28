# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 11:00:43 2022

@author: ryan.robinson
"""

import tkinter as tk

import DataParser as dp






class Application:
    def __init__(self, master):
        """
        CREATE THE PROGRAM GUI
        """
        self.master = master
        
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # BOX CONFIGURE
        self.master.title('BIS - Burn In Station')
        
        # DEFINE RUNFRAME
        self.runframe = tk.Frame(self.master)
        self.runframe.rowconfigure([0, 1, 2, 3, 4, 5], minsize=30, weight=1)
        self.runframe.columnconfigure([0, 1, 2, 3, 4, 5, 6, 7, 8], minsize=25, weight=1)




    
    def on_closing(self):
        """
        EXIT THE APPLICATION
        """
        # PROMPT DIALOG BOX
        if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
            
            # DESTROY APPLICATION
            self.master.destroy()
            
        return
































def main():
    
    # CREATE ROOT TKINTER OBJECT
    root = tk.Tk()
    
    # CREATE APPLICATION
    app = Application(root)
    
    # RUN MAINLOOP
    root.mainloop()
    
    return



if __name__=="__main__":
    main()