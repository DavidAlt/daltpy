# Minimum blocks between nether portals: 1024 / 128

import logging
logging.basicConfig(level=logging.CRITICAL, format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('treeview')
log.setLevel(logging.DEBUG)

import matplotlib.pyplot as plt
import matplotlib.ticker as tckr
import numpy as np


class AnnoPlot():

    def __init__(self, title=''):
        
        self.title = title

        # Setup the points
        # TODO: load plots from collection
        # TODO: load plots from csv
        self.plot_predefined()
        
        # Get references to the default figure and subplot
        self.fig = plt.figure(1)
        self.axes = plt.subplot(1,1,1)

        plt.title(self.title + '\n\n')
        self.fig.set_size_inches(12, 12)

        self.setup_axes()

        # Show the figure, then clear it from memory
        plt.show()
        plt.close(self.fig)


    def setup_axes(self):
        # Setup axes
        plt.gca().xaxis.set_major_locator(tckr.MultipleLocator(500)) # Set x axis intervals
        plt.gca().xaxis.set_minor_locator(tckr.MultipleLocator(100)) # Set x axis intervals
        plt.gca().yaxis.set_major_locator(tckr.MultipleLocator(500)) # Set y axis intervals
        plt.gca().yaxis.set_minor_locator(tckr.MultipleLocator(100)) # Set y axis intervals

        # Rotate the text in the x-axis legend by 45 degrees so it doesn't overlap
        for tick in self.axes.get_xticklabels():
            tick.set_rotation(45)
        plt.axis([-3500,3500,-3500,3500])  # sets min and max values for x and y axes
        plt.gca().invert_yaxis() # Invert the y axis
        plt.grid(True)  # display a grid using the ticks
        
        # Creates a mirrored x axis and copies the same limits
        ax1 = self.axes.twinx()
        ax1.set_ylim(self.axes.get_ylim())

        # Creates a mirrored y axis and copies the same limits
        ax2 = self.axes.twiny()
        ax2.set_xlim(self.axes.get_xlim())


    def plot_predefined(self):
        #self.annoplot(0,0,'Origin')
        #rng = np.random.RandomState(0)
        #x = rng.randn(100)
        #y = rng.randn(100)
        #colors = rng.rand(100)
        #sizes = 1000 * rng.rand(100)

        #plt.scatter(x, y, c=colors, s=sizes, alpha=0.3, cmap='viridis')
                    
        #plt.colorbar();  # show color scale

        x = 0
        y = 0
        size = 100

        #plt.scatter(0,0, c='red', s=50000, alpha=0.3)#, cmap='viridis')
        plt.scatter(x, y, s=20, c=x, cmap="Blues", alpha=0.4, edgecolors="grey", linewidth=2)


    def annoplot(self, x, y, text, z='', style='ko', mark_size=10,
                xoff=10, yoff=-7, text_size=10, coords=True, 
                cur_plot=plt.subplot(111)):
        plt.plot(x,y,style,markersize=mark_size)
        
        if (coords) and z == '':
            text = text + '\n(' + str(x) + ', ' + str(y) +')'
        elif (coords) and z != '':
            text = text + '\n(' + str(x) + ', ' + str(y) + ' |' + z +')'
        plt.annotate(text,xy=(x,y),xytext=(xoff,yoff), textcoords='offset points', size=text_size)




if __name__ == '__main__':
    map = AnnoPlot('Portal Radius')