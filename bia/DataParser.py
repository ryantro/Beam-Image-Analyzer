# -*- coding: utf-8 -*-
"""
Created on Mon Sep 27 08:25:40 2021

@author: ryan.robinson

Purpose:
    Analyze ascii data from CCD camera
    Fucntions:
    - Subtract noise from data
    - Generate color plot of data
    - Generate single axis and knife edge plots
    - Generate enclosed power vs solid angle plot (work in progress)
"""

import numpy as np
import matplotlib.pyplot as plt
import sys

def main():
    
    ########################### FILENAME #####################################
    
    # FAR FIELD DATA
        # IQA
    #filename = r'N:\TEST DATA\HBL-100\Dolby Customer Unit\BeamGage\IQA Fixture\1000019_Full Module_100%_FF_0001.ascii.csv'
        # COLLIMATOR DATA
    #filename = r'N:\TEST DATA\HBL-100\Dolby Customer Unit\BeamGage\1000019_Collimator_All Lens_FF_100%_3_0001.ascii.csv'
    #filename = r'N:\TEST DATA\HBL-100\Dolby Customer Unit\BeamGage\1000019_Collimator_All Lens_FF_100%_4A2_0001.ascii.csv'
    
    # NEAR FIELD DATA
        # IQA DATA
    #filename = r'N:\TEST DATA\HBL-100\Dolby Customer Unit\BeamGage\IQA Fixture\1000019_Full Module_100%_NF_0001.ascii.csv'
        # COLLIMATOR DATA
    #filename = r'N:\TEST DATA\HBL-100\Dolby Customer Unit\BeamGage\1000019_Collimator_All Lens_NF_100%_0001.ascii.csv'
    
    
    #filename = r'N:/TEST DATA/HBL-100/Module 22/BeamGage Data/M1000022_Full_Module_100%_NF_0001.ascii.csv'
    filename = r'N:\TEST DATA\HBL-100\Module 22\BeamGage Data/M1000022_Full_Module_100%_FF_paper_beamblock_0001.ascii.csv'
    filename = r'C:\Users\ryan.robinson\Downloads\AI-75 IQA TESTING\Beam Gage\AI-75 50% CW FF 2_0001.ascii.csv'
    
    # filename = r'C:\Users\ryan.robinson\Downloads\AI-75 IQA TESTING\Beam Gage\AI-75 50% CW NF 2_0001.ascii.csv'
    ########################## DETECTOR SETTINGS #############################
    
    
    # PARSE DETECTOR SIZE AND MULTIPLIER

    px = 4.4        # Pixel Spacing
    mult = 1/0.59   # Magnification Multiplier

    
    # ZOOM SET TO +/- 100UM
    zoom = 300
    
    if('FF' in filename):
        # FAR FIELD FILE
        FF = True       # FAR FIELD
        mult = 1        # MULTIPLIER - Used to convert image to object, set to 1 for Far Field Analysis
        flen = 80.0     # FOCAL LENGTH
        titleMod = 'AI-75 Far Field '
        zoomed = True
    elif('NF' in filename):
        # NEAR FIELD FILE
        FF = False      # FAR FIELD
        flen = 80.0     # FOCAL LENGTH
        titleMod = 'AI-75 Near Field '
        zoomed = False
    else:
        print(r'Error: Neither \'NF\' or \'FF\' found in data title.')
        sys.exit(0)
    
    ######################### PRINT SETTINGS #################################    
    
    printb()
    print('File: '+filename)
    print('Pixel Size Used: {}'.format(px))
    print('Measurement: '+titleMod)
    print('Lens focal length: {}'.format(flen))
    print('Size multiplier: {}'.format(mult))
    printb()  
        
    # PARSE ASCII FILE
    B = parseAscii(filename)
    
    # CHANGE ROTATE TO TRUE TO ROTATE DATA
    rotate = False
    if(rotate):
        B = np.rot90(B)
    
    # FIND DETECTOR SIZE GIVEN PIXEL SIZE
    xsize = px*len(B[0,:]) # length of a single row times pixel size
    ysize = px*len(B[:,0]) # length of a single column times pixel size
    
    
    ########################### PLOTTING #####################################
    
    mult = 0.59
    # CREATE DATA OBJECT
    # BP = BeamProfileFarField(B,xsize,ysize, lens = 80.0) # Create beam profile object
    BP = BeamProfileFarField(B,xsize,ysize, 80.0)
    
    BP.X.removeEndPoints(0)
    BP.X.removeStartPoints(1)    
    
    
    BP.Y.removeEndPoints(1)
    BP.Y.removeStartPoints(1) 
    
    # BP.X.center()
    # BP.Y.center()
    
    BP.X.removeNoise(3500, 2)
    BP.Y.removeNoise(800, 2)
    
    # BP.X.center()
    # BP.Y.center()
    # DATA MANIPULATION
    #BP.centerData(0)
    
    # DATA PLOTTING
    BP.colorPlot(title=titleMod+'Color Plot') # Create color plot
    BP.knifeEdgePlot(title=titleMod+'Knife Edge Plot') # Create knife edge plot
    BP.singleAxisPlot(title=titleMod+'Single Axis Plot') # Create single axis plot (Knife Edge Derivative)
    
    return


def parseAscii(filename):
    """
    Input:
        - (str) filename
    Purpose:
        Extract out a Numpy Array from an Ascii file generated by an LBP2-HR-VIS2 Laser Beam Profiler
    """
    slens = []
    A = []
    with open(filename) as f:
        for rows in f:
            s = rows.split(',')
            slens.append(len(s))
        maxlen = max(slens)
        #print(maxlen)
    
    with open(filename) as f:
        for rows in f:
            s1 = rows.strip('\n')
            s = s1.split(',')
            for i in range(0,maxlen):
                if (i >= len(s)):
                    s.append(0.0)
                elif (s[i] == ''):
                    s[i] = 0.0
                else:
                    s[i] = float(s[i])
                i = i+1
            A.append(s)
    B = np.array(A)
    return B

def parseAsciiOld(filename):
    """Parses an ascii file for a nicely formatted file"""
    A = np.genfromtxt(filename,delimiter=',')
    lenX = len(A[1][:])
    B = A[:,:lenX-1] # Remove last NaN column
    return B

class SingleAxisBeamProfile:
    def __init__(self,flux,axis_size):
        
        # Generate normalized single axis 1D array
        self.f = flux
        
        # Detector size
        self.axis_size = axis_size # Detector size in x (um)
        
        # DETECTOR SIZE IN PIXELS
        self.axis_len = len(self.f) # Detector size in x (pixels)
        
        # GENERATE AXIS IN UM    
        self.m = np.linspace(-self.axis_size/2, self.axis_size/2, self.axis_len)
        
        # GENERATE AXIS IN PIXELS
        self.p = np.linspace(1,self.axis_len,self.axis_len)
            
        # PIXEL SIZE
        self.pixel_size = self.axis_size/self.axis_len
        
        # CALCULATE REMAINING BEAM PARAMETERS
        self.calc()
        
        return
        
    def calc(self):
        # GENERATE KNIFE EDGE DATA
        self.kE = self.knifeEdge(self.f)

        # FIND CENTER INDEX BASED ON 50% KNIFE EDGE
        self.center_index, self.center_point = self.findPoint(self.kE,0.5)
        
        # CENTER POINT
        #self.center_point = self.m[self.center_index]

        k1 = 0.05
        k2 = 0.95
        
        self.p1, self.m1 = self.findPoint(self.kE,k1)
        self.p2, self.m2 = self.findPoint(self.kE,k2)
        
        
        self.width = self.m2 - self.m1
        
        return
    
    def removeEndPoints(self,n):
        # Generate normalized single axis 1D array
        self.f = self.f[:self.axis_len - n - 1]
        self.f = self.f / np.sum(self.f)
        
        # Detector size
        self.axis_size = self.axis_size - (n * self.pixel_size) # Detector size in x (um)
        
        # DETECTOR SIZE IN PIXELS
        self.axis_len = len(self.f) # Detector size in x (pixels)
        
        # GENERATE AXIS IN UM    
        self.m = np.linspace(-self.axis_size/2, self.axis_size/2, self.axis_len)
        
        # GENERATE AXIS IN PIXELS
        self.p = np.linspace(1,self.axis_len,self.axis_len)
        
        # CALCULATE REMAINING BEAM PARAMETERS
        self.calc()
        return

    def removeStartPoints(self,n):
        # Generate normalized single axis 1D array
        self.f = self.f[n:]
        self.f = self.f / np.sum(self.f)
        
        # Detector size
        self.axis_size = self.axis_size - (n * self.pixel_size) # Detector size in x (um)
        
        # DETECTOR SIZE IN PIXELS
        self.axis_len = len(self.f) # Detector size in x (pixels)
        
        # GENERATE AXIS IN UM    
        self.m = np.linspace(-self.axis_size/2, self.axis_size/2, self.axis_len)
        
        # GENERATE AXIS IN PIXELS
        self.p = np.linspace(1,self.axis_len,self.axis_len)
        
        # CALCULATE REMAINING BEAM PARAMETERS
        self.calc()
        return

    def center(self):
        """
        Shifts the beam 50% Knife Edge point to the 0 coordinate

        Returns
        -------
        None.

        """
        self.m = self.m - self.center_point
        self.p = self.p - self.p[self.center_index]
        self.center_point = 0
        return

    def knifeEdge(self,X):
        """
        Parameters
        ----------
        X : 1D NUMPY ARRAY
            INTENSITY ALONG 1 AXIS.

        Returns
        -------
        R : 1D NUMPY ARRAY
            KNIFE EDGE OF INPUT.

        """
        l = len(X)
        R = np.zeros(l)
        for x in range(1,l,1):
            R[x] = R[x-1] + X[x]
        return R

    def findPoint(self,KE,pmin = 0.5):
        """
        Finds the index that the pmin crosses over.

        Parameters
        ----------
        KE : 1D NUMPY ARRAY
            KNIFE EDGE ARRAY.
        pmin : FLOAT, optional
            Crossing value. The default is 0.5.

        Returns
        -------
        a : INT
            Index at crossing value.
        b : FLOAT
            Coordinate at crossing value

        """
        a = 0
        b = 0
        l = len(KE)        
        for j in range(0,l,1):
            if(KE[j] >= pmin):
                a = j
                break
        
        # To get better than pixel precision
        rise = KE[a] - KE[a-1]
        run = self.m[a] - self.m[a-1]
        slope = rise/run
        
        deltaY = pmin - KE[a-1]
        
        deltaX = deltaY/slope
        
        b = deltaX + self.m[a-1]
        
        return a, b

    def removeNoise(self, gap, deg, noisePlot = True, title = 'Noise Curves'):
        """
        Remove the noise from the data.

        Parameters
        ----------
        xgap : FLOAT
            Y gap size to ignore in noise fit.
        ygap : FLOAT
            X gap size to ignore in noise fit.
        deg : INT
            Polynomial degree fit too.
        noisePlot : BOOL, optional
            Toggle noise plotting on or off. Default is True.
        title : STR, optional
            Plot title for noise fit. Default is Noise Curves.
        Returns
        -------
        None

        """
        
        
        printb()
        print("Fitting noise as a {} degree polynomial.".format(deg))
        
        ######################################################################
        # REMOVE NOISE FROM X DATA
        xOff = int(gap / self.pixel_size / 2)
        
        # Indexes to mark ignored gap
        xL = int(self.center_index - xOff)
        xH = int(self.center_index + xOff)
        # print("X Data: Ignoring {:.2f} um gap from {} um to {} um".format(-self.m[xL]+self.m[xH],self.m[xL],self.m[xH]))
        
        # Remove the center of the data
        x = np.concatenate((self.p[:xL],self.p[xH:]), axis = None)
        y = np.concatenate((self.f[:xL],self.f[xH:]), axis = None)
        
        # Fit to a linear curve
        z = np.polyfit(x,y,deg)
        
        # Turn fit into a function
        yFit = np.poly1d(z)
        print('X noise fit: '+str(yFit))
        # Apply the fuction to generate fit
        yPolyFit = yFit(self.p)
        
        # PLOT X NOISE FIT
        if(noisePlot):
            plt.figure(title+' X')
            plt.title(title+' X')
            plt.xlabel('Pixel position (pixels)')
            plt.ylabel('Normalized Intensity (W/W)')
            plt.plot(self.m[:xL],self.f[:xL],color='k',linewidth=0.1,label='Noise')
            plt.plot(self.m[xH:],self.f[xH:],color='k',linewidth=0.1)
            plt.plot(self.m,yPolyFit,label='Fit')
            plt.legend()
        xNew = self.f - yPolyFit
        self.f = xNew/np.sum(xNew)
        
        ######################################################################
        
        # GENERATE KNIFE EDGE DATA
        self.calc()
        
        printb()
        return



class BeamProfile:
    def __init__(self,array,xsize,ysize):
        """
        Initiator for beam profile data object

        Parameters
        ----------
        array : 2D NUMPY ARRAY
            Intensity data.
        xsize : FLOAT
            X size of detector in um.
        ysize : FLOAT
            Y size of detector in um.
        
        Returns
        -------
        None.

        """
        
        # Detector data
        self.A = array
        self.A = self.A / np.sum(self.A) # Normalize
        
        # Detector size
        x_size = xsize # Detector size in x (um)
        y_size = ysize # Detector size in y (um)
        
        # Generate normalized single axis 1D array
        X = np.sum(self.A, axis = 0)  # Detector summed along Y axis
        Y = np.sum(self.A, axis = 1)  # Detector summed along X axis
        
        # Generate 1D beam profile objects
        self.X = SingleAxisBeamProfile(X, x_size)
        self.Y = SingleAxisBeamProfile(Y, y_size)
        
        return
    
    def colorPlot(self,title='Color Plot'):
        """
        Produces a color plot of the data.

        Parameters
        ----------
        title : STR, optional
            Title for the plot produced. The default is 'Color Plot'.

        Returns
        -------
        None.

        """
        
        plt.figure(title)
        plt.title(title)
        
        x1 = min(self.X.m)
        x2 = max(self.X.m)
        y1 = min(self.Y.m)
        y2 = max(self.Y.m)

        self.A = self.A-np.min(self.A)
        self.A = self.A/np.sum(self.A)

        plt.imshow(np.flipud(self.A), cmap='jet', extent=[x1, x2, y1, y2])
        plt.xlabel('x (um)')
        plt.ylabel('y (um)')
        
        plt.text(x1*0.9,y1*0.9,"X Width: {:.2f} um\nY Width: {:.2f} um\n".format(self.X.width,self.Y.width), color = 'white')
        # plt.text(x1*0.9,y2*0.5,"X Center: {:.2f} um\nY Center: {:.2f} um\n".format(self.X.center_point,self.Y.center_point), color = 'white')
        return
    
    def singleAxisPlot(self,title='Single Axis Plot'):        
        """
        Parameters
        ----------
        title : STR, optional
            Title for the plot produced. The default is 'Single Axis Plot'.
        zoomed : BOOL, optional
            Zoomed plot on or off. The default is False.

        Returns
        -------
        None.

        """
        # PLOT BEAM INTENSITY ALONG X AND Y
        plt.figure(title)
        plt.plot(self.X.m,self.X.f) # Plot X intensity
        plt.figure(title)
        plt.plot(self.Y.m,self.Y.f) # plot Y intensity
        
        
        # PLOT FORMATTING
        plt.title(title)
        plt.grid()
        plt.xlabel('x (um)')
        plt.ylabel('Normalized Intensity (W/W)')
        plt.legend(["Intensity Along X","Intensity Along Y"])
        return
    
    def knifeEdgePlot(self,title='Beam Width Plot'):
        """
        Plot the knife edge data.

        Parameters
        ----------
        title : STR, optional
            Title for the plot produced. The default is 'Beam Width Plot'.
        zoomed : BOOL, optional
            Zoomed plot on or off. The default is False.

        Returns
        -------
        None.

        """
        
        # Plotting
        plt.figure(title)
        plt.plot(self.X.m, self.X.kE, markevery=[self.X.p1,self.X.p2], marker="o")
        plt.figure(title)
        plt.plot(self.Y.m, self.Y.kE, markevery=[self.Y.p1,self.Y.p2], marker="o")
        
        # PLOT FORMATTING
        textPos = min([min(self.X.m),min(self.Y.m)])

        # Adding labels to plots
        plt.title(title)
        plt.xlabel('Knife Position (um)')
        plt.ylabel('Fractional Power (W/W)')

        # Adding text to plots
        if(self.X.width >= 1000 and self.Y.width >= 1000):
            plt.text(textPos,0.6,"5% - 95% Width:\n   X : {:.3f} mm\n   Y : {:.3f} mm\n".format(self.X.width/1000,self.Y.width/1000))
        else:
            plt.text(textPos,0.6,"5% - 95% Width:\n   X : {:.2f} um\n   Y : {:.2f} um\n".format(self.X.width,self.Y.width))
        plt.legend(["X","Y"])
        return
                

class BeamProfileNearField(BeamProfile):
    def __init__(self, array, xsize, ysize, mag = 1,):
        
        # CREATE SUBCLASS
        BeamProfile.__init__(self, array, xsize / mag, ysize / mag)
        
        return

class BeamProfileFarField(BeamProfile):
    def __init__(self, array, xsize, ysize, lens = 80):
        
        # CREATE SUBCLASS
        BeamProfile.__init__(self, array, xsize, ysize)
        
        self.lens = lens
        
        return
    
    def colorPlot(self,title='Color Plot'):
        """
        Produces a color plot of the data.

        Parameters
        ----------
        title : STR, optional
            Title for the plot produced. The default is 'Color Plot'.

        Returns
        -------
        None.

        """
        
        plt.figure(title)
        plt.title(title)
        
        x1 = min(self.X.m)
        x2 = max(self.X.m)
        y1 = min(self.Y.m)
        y2 = max(self.Y.m)

        plt.imshow(np.flipud(self.A), cmap='jet', extent=[x1, x2, y1, y2])
        plt.xlabel('x (um)')
        plt.ylabel('y (um)')
        
        plt.text(x1*0.9,y1*0.9,"X Divergence: {:.2f} mrad\nY Divergence: {:.2f} mrad\n".format(self.X.width / self.lens,self.Y.width / self.lens), color = 'white')
        plt.text(x1*0.9,y2*0.5,"X Center: {:.2f} um\nY Center: {:.2f} um\n".format(self.X.center_point,self.Y.center_point), color = 'white')
        return
    
    def singleAxisPlot(self,title='Single Axis Plot'):        
        """
        Parameters
        ----------
        title : STR, optional
            Title for the plot produced. The default is 'Single Axis Plot'.
        zoomed : BOOL, optional
            Zoomed plot on or off. The default is False.

        Returns
        -------
        None.

        """
        # PLOT BEAM INTENSITY ALONG X AND Y
        plt.figure(title)
        plt.plot(self.X.m,self.X.f) # Plot X intensity
        plt.figure(title)
        plt.plot(self.Y.m,self.Y.f) # plot Y intensity
        
        
        # PLOT FORMATTING
        plt.title(title)
        plt.grid()
        plt.xlabel('x (um)')
        plt.ylabel('Normalized Single Axis Intensity (W/W m)')
        plt.legend(["Intensity Along X","Intensity Along Y"])
        return
    
    def knifeEdgePlot(self,title='Beam Width Plot'):
        """
        Plot the knife edge data.

        Parameters
        ----------
        title : STR, optional
            Title for the plot produced. The default is 'Beam Width Plot'.
        zoomed : BOOL, optional
            Zoomed plot on or off. The default is False.

        Returns
        -------
        None.

        """
        
        # Plotting
        plt.figure(title)
        plt.plot(self.X.m, self.X.kE, markevery=[self.X.p1,self.X.p2], marker="o")
        plt.figure(title)
        plt.plot(self.Y.m, self.Y.kE, markevery=[self.Y.p1,self.Y.p2], marker="o")
        
        # PLOT FORMATTING
        textPos = min([min(self.X.m),min(self.Y.m)])

        # Adding labels to plots
        plt.title(title)
        plt.xlabel('Knife Position (um)')
        plt.ylabel('Fractional Power (W/W)')

        # Adding text to plots
        plt.text(textPos,0.6,"5% - 95% Width:\n   X : {:.3f} mrad\n   Y : {:.3f} mrad\n".format(self.X.width / self.lens, self.Y.width / self.lens))
        plt.legend(["X","Y"])
        return

def printb():
    """
    Prints a line to make console output more legible.

    Returns
    -------
    None.

    """
    print('-----------------------------------------------------------------')
    return
























if __name__=="__main__":
    main()