
import matplotlib.pyplot as plt
import matplotlib.ticker as tckr

def annoplot(x, y, text, z='', style='ko', mark_size=10,
             xoff=10, yoff=-7, text_size=10, coords=True, 
             cur_plot=plt.subplot(111)):
    plt.plot(x,y,style,markersize=mark_size)
    
    if (coords):
        text = text + '\n(' + str(x) + ', ' + str(y) + ' |' + z +')'
    plt.annotate(text,xy=(x,y),xytext=(xoff,yoff), textcoords='offset points', size=text_size)


# Get references to the default figure and subplot
fig = plt.figure(1)
ax = plt.subplot(1,1,1)
#fig.set_size_inches(10, 10)  # CHANGE

# Setup the axes, grid, and legend
ax.set_aspect('equal')#, adjustable="box-forced")  # CHANGE
#plt.axis('equal')
#plt.gca().set_aspect('equal', adjustable='box')

plt.gca().xaxis.set_major_locator(tckr.MultipleLocator(500)) # Set x axis intervals
plt.gca().xaxis.set_minor_locator(tckr.MultipleLocator(100)) # Set x axis intervals
plt.gca().yaxis.set_major_locator(tckr.MultipleLocator(500)) # Set y axis intervals
plt.gca().yaxis.set_minor_locator(tckr.MultipleLocator(100)) # Set y axis intervals

# Rotate the text in the x-axis legend by 45 degrees so it doesn't overlap
for tick in ax.get_xticklabels():
    tick.set_rotation(45)

plt.axis([-3500,3500,-3500,3500])  # sets min and max values for x and y axes
plt.gca().invert_yaxis()
plt.grid(True)  # display a grid using the ticks

# Mirror the axes with the same limits
ax1 = ax.twinx()
ax1.set_ylim(ax.get_ylim())
ax1.set_aspect('equal')  # CHANGE
ax2 = ax.twiny()
ax2.set_xlim(ax.get_xlim())
ax2.set_aspect('equal')  # CHANGE

# Plot a point with a corresponding circle to show radius
#plt.scatter(0, 0, s=2000, c='red', alpha=0.5)
#plt.plot(0, 0, 'ko')
circle = plt.Circle((0, 0), 500, color='red', fill=True, alpha=0.5)  # CHANGE
plt.gca().add_artist(circle)  # CHANGE

# Show the figure, then clear it from memory
plt.show()
plt.close(fig)
