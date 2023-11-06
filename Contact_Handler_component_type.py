#Olivia Creasey
#Bioengineering PhD Candidate; Gartner Lab UCSF
#August/September 2019, edits for Ms1H_mini_1 in September 2021

"""This is a simple method for categorizing component_type. It will likely
need to be updated to handle data more effectively."""

def component_type_calculator(component_channels_dict):
    """This function categorizes different components within the current tissue
based on the mean intensity of labeling. This is a very simple method of 
classifying components by type. It requires significant user attention."""
    component_type_dict = dict()
    for component, channels in component_channels_dict.items():
        if 'peri' in component.lower():
            component_type = 'peri'
        elif 'cap' in component.lower():
            component_type = 'capillary'
        elif 'exo' in component.lower():
            component_type = 'exocrine'
        elif channels[3][1]> 7000: #ch4 is 405
            component_type = 'alpha'
        elif channels[0][1]/channels[2][1]> 2.4: #ch1 is 647, ch3 is 488
            component_type = 'delta'
        elif channels[2][1]/channels[1][1]> 0.6: #ch3 is 488
            component_type = 'beta'
        else:
            component_type = 'unlabeled'

        component_type_dict[component] = component_type

    return component_type_dict
    
def component_type_histograms(component_channels_dict):
    """This function prints out the mean and median intensity values for each channel
for each component into an Excel spreadsheet, so that the values can be graphed
or otherwise inspected."""
    import xlsxwriter

    wb = xlsxwriter.Workbook('Channels.xlsx')

    sheet1 = wb.add_worksheet('Channels')
    items = sorted(component_channels_dict.keys())
    sheet1.write(0,1,'Ch1_mean')
    sheet1.write(0,2,'Ch2_mean')
    sheet1.write(0,3,'Ch3_mean')
    sheet1.write(0,4,'Ch4_mean')
    sheet1.write(0,5,'Ch1_median')
    sheet1.write(0,6,'Ch2_median')
    sheet1.write(0,7,'Ch3_median')
    sheet1.write(0,8,'Ch4_median')
    for i in range(len(items)):
        sheet1.write(i+1, 0, items[i])
        sheet1.write(i+1, 1, component_channels_dict[items[i]][0][1])
        sheet1.write(i+1, 2, component_channels_dict[items[i]][1][1])
        sheet1.write(i+1, 3, component_channels_dict[items[i]][2][1])
        sheet1.write(i+1, 4, component_channels_dict[items[i]][3][1])
        sheet1.write(i+1, 5, component_channels_dict[items[i]][0][0])
        sheet1.write(i+1, 6, component_channels_dict[items[i]][1][0])
        sheet1.write(i+1, 7, component_channels_dict[items[i]][2][0])
        sheet1.write(i+1, 8, component_channels_dict[items[i]][3][0])

    wb.close()
