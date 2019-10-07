# -*- coding: utf-8 -*-
"""
Crowning Glory Realm
@author: David Alt

ToDo: 
    plot by thing, i.e. town(-210,343,'Name'), pyramid(-483,238,'Name')
    each associated with own symbol so it doesn't need to be configured
    
    zoomable map
    
    clickable filters
    
    nether calculator

"""
import matplotlib.pyplot as plt
import matplotlib.ticker as tckr

def annoplot(x, y, text, z='', style='ko', mark_size=10,
             xoff=10, yoff=-7, text_size=10, coords=True, 
             cur_plot=plt.subplot(111)):
    plt.plot(x,y,style,markersize=mark_size)
    
    if (coords):
        text = text + '\n(' + str(x) + ', ' + str(y) + ' |' + z +')'
    plt.annotate(text,xy=(x,y),xytext=(xoff,yoff), textcoords='offset points', size=text_size)
    #plt.annotate(str(k),xy=(k[0],k[1]), xytext=(6,-5), textcoords='offset points', size=8)


# Player Bases
annoplot(-951,432,'Main Base')
annoplot(-1086,353,'Underground Garden',z='12')
annoplot(505,-590,'Stronghold Base')
annoplot(-165,179,'Hut at Desert Edge')
annoplot(-339,194,'Humble Beginnings')
annoplot(-431,52,'Overchasm')
annoplot(-712,403,'Jungle Overlook')
annoplot(-1150,292,'Overchasm')
annoplot(-1282,459,'Gopher Hut')
annoplot(-302,-473,'Gopher Hut')
annoplot(-105,-130,'Chasm Edge')
annoplot(530,-610,'Underdark',z='28')


# Gates
annoplot(-327,714,'G',z='63')
annoplot(-1066,356,'G-Underground Garden',z='11')
annoplot(-321,712,'G-Desert Seaside',z='59')
#annoplot(-49,96,'NG-Desert Seaside',z='55')
annoplot(-409,58,'G-Overchasm',z='71')
#annoplot(-47,13,'NG-Overchasm',z='56')
annoplot(1216,-1392,'G-Desert Town',z='70')
#annoplot(105,-130,'NG-Desert Town',z='85')
annoplot(861,-1036,'G-Ice Spikes',z='87')
annoplot(495,-585,'G-Stronghold',z='63')
annoplot(433,-632,'G-Stronghold_lower',z='31')
#annoplot(61,-73,'NG-Stronghold',z='68')


# Towns
annoplot(-216,1110,'DTown')
annoplot(-201,36,'Well')
annoplot(1240,-1388,'DTown')
annoplot(1040,770,'DTown')
annoplot(860,715,'DTown_Pyramid')

# Water Temples (WT), Pyramids (P), Jungle Temples (JT), Mineshafts (MS), Stronghold (S)
annoplot(2230,-1295,'JT')
annoplot(2390,-223,'JT')
annoplot(295,1630,'JT')
annoplot(-970,405,'MS',z='23')
annoplot(-262,618,'P')
annoplot(-438,1210,'P')
annoplot(860,715,'P')
annoplot(-857,839,'WT', style='bs')
annoplot(-376,728,'WT', style='bs')
annoplot(-1240,1255,'WT', style='bs')
annoplot(-680,1210,'WT', style='bs')
annoplot(55,1720,'WT-Harbor', style='bs') # Fantastic access, bordered by swamp, jungle, and frost
annoplot(435,-633,'S',z='30')

# Dungeons
annoplot(-982,405,'Cave Spiders',z='23')
annoplot(-984,425,'Cave Spiders',z='13')
annoplot(-1079,370,'Cave Spiders',z='29')
annoplot(-1137,363,'Cave Spiders',z='35')
annoplot(-1123,361,'Cave Spiders',z='36')
annoplot(-1143,371,'Zombies',z='34')
annoplot(-287,-431,'Spawner',z='61')

# Biomes (UG=underground)
annoplot(-304,268,'Chasm')
annoplot(-427,64,'Chasm')
annoplot(-117,-136,'Chasm')
annoplot(-1153,287,'Chasm-UG',z='12')
annoplot(621,-546,'Chasm-UG',z='24')
annoplot(1275,-2240,'Chasm')
annoplot(1640,-60,'Chasm-IceSpikes')
annoplot(1365,-105,'Chasm-NearIceSpikes')
annoplot(870,1035,'Chasm-OceanEdge')
annoplot(-1435,-265,'Flower Forest')
annoplot(1430,-2500,'Flower Mountain')
annoplot(-300,-1500,'Gravel Plains')
annoplot(1570,-83,'Ice Spikes) # fantastic spot to build city')
annoplot(-777,270,'Jungle')
annoplot(990,-1650,'Mesa')
annoplot(1035,960,'Mesa Mountain')
annoplot(-72,0,'Mooshroom')

# Interesting Features
annoplot(-1340,168,'Caldera')
annoplot(-1532,-114,'Gravel Peninsula')
annoplot(635,0,'Hollow Mountain')











# Get references to the default figure and subplot
fig = plt.figure(1)
ax = plt.subplot(1,1,1)


# Customize legend, axes
plt.title('Crowning Glory Overworld\n')
plt.gca().xaxis.set_major_locator(tckr.MultipleLocator(500)) # Set x axis intervals
plt.gca().xaxis.set_minor_locator(tckr.MultipleLocator(100)) # Set x axis intervals
plt.gca().yaxis.set_major_locator(tckr.MultipleLocator(500)) # Set y axis intervals
plt.gca().yaxis.set_minor_locator(tckr.MultipleLocator(100)) # Set y axis intervals


# Rotate the text in the x-axis legend by 45 degrees so it doesn't overlap
for tick in ax.get_xticklabels():
    tick.set_rotation(45)

plt.axis([-3500,3500,-3500,3500])  # sets min and max values for x and y axes
plt.gca().invert_yaxis() # Invert the y axis
plt.grid(True)  # display a grid using the ticks
fig.set_size_inches(12, 12)


# Creates a mirrored x axis and copies the same limits
ax1 = ax.twinx()
ax1.set_ylim(ax.get_ylim())

# Creates a mirrored y axis and copies the same limits
ax2 = ax.twiny()
ax2.set_xlim(ax.get_xlim())


# Show the figure, then clear it from memory
plt.show()
plt.close(fig)
