import tkinter as tk
from tkinter import ttk


def style_themes():
    print(f'Available themes:  {ttk.Style().theme_names()}')

    # Set theme with
    #   ttk.Style().theme_use('winnative')
    # My themes: winnative, clam, alt, default, classic, vista, xpnative
    
    #s.theme_use('clam')
    #s.theme_use('alt')
    #s.theme_use('default')
    #s.theme_use('classic')
    #s.theme_use('vista')
    #s.theme_use('xpnative')



# FROM: Sun Bear https://stackoverflow.com/a/48933106/4381392
def stylename_elements_options(stylename):
    '''Function to expose the options of every element associated to a widget
       stylename.'''
    try:
        # Get widget elements
        style = ttk.Style()
        layout = str(style.layout(stylename))
        print('Stylename = {}'.format(stylename))
        print('Layout    = {}'.format(layout))
        elements=[]
        for n, x in enumerate(layout):
            if x=='(':
                element=""
                for y in layout[n+2:]:
                    if y != ',':
                        element=element+str(y)
                    else:
                        elements.append(element[:-1])
                        break
        print('\nElement(s) = {}\n'.format(elements))

        # Get options of widget elements
        for element in elements:
            print('{0:30} options: {1}'.format(
                element, style.element_options(element)))

    except tk.TclError:
        print('_tkinter.TclError: "{0}" in function'
              'widget_elements_options({0}) is not a regonised stylename.'
              .format(stylename))


# EXAMPLES
# stylename_elements_options('Treeview')
# style_themes()