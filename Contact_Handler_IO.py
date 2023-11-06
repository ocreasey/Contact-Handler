#Olivia Creasey
#Bioengineering PhD Candidate; Gartner Lab UCSF
#August/September 2019; edits January 2020
#Edited September 2021 for Ms1H_mini_1

"""This module provides I/O functions for managing the cell-cell and cell-ECM
contact data output by the OAC Contact Calculator Xtension."""

def get_component_channels(filename):
    """Creates the list of components in the tissue and reads in the intensity
for all 4 channels for each component. Returns a dictionary with keys that are
component names and values in the form of (ch1, ch2, ch3, ch4).
Each ch value is itself a list of 6 numbers: Median intensity, mean intensity, 
intensity sum, min intensity, max intensity, and intensity stdev. """
    f = open(filename, 'r')
    component_channels_dict = {}

    for line in f:
        if line[0:3] == 'Cap' or line[0:4] == 'Surf' or line [0:4] == 'Peri' or line[0:3] == 'Exo':
            ch1 = []
            ch2 = []
            ch3 = []
            ch4 = []
            component_name = line.strip().replace(' ', '_')
            f.readline()
            for i in range(3):
                #for i=0, median; for i=1, mean; for i=2, Intensity Sum
                #for 1=3, min; for i=4, max; for i=5, stdev
                ch1.append(float(f.readline().split('\t')[1]))
                ch2.append(float(f.readline().split('\t')[1]))
                ch3.append(float(f.readline().split('\t')[1]))
                ch4.append(float(f.readline().split('\t')[1]))

            f.readline()

            component_channels_dict[component_name] = (ch1, ch2, ch3, ch4)

    f.close()
    return component_channels_dict

def get_component_info(filename):
    """This function takes a filename(containing data for a component) and
pulls out all of the quantitative spatial information in the file, returning a tuple
(identifier, surface_area, volume, sphericity, bounding_box(tuple of 3), s_voxels (calculated surface
voxels), voxel_size, and a list of contacts (really a list of tuples: (name of contacting component, number of voxels)"""
    f = open(filename, 'r')
    #print(filename)
    identifier = f.readline().strip()
    surface_area = float(f.readline().split('\t')[1])
    volume = float(f.readline().split('\t')[1])
    sphericity = float(f.readline().split('\t')[1])
    bb = f.readline().split('\t')
    bounding_box = (float(bb[1]), float(bb[2]), float(bb[3]))
    ellipticity_p = float(f.readline().split('\t')[1])
    ellipticity_o = float(f.readline().split('\t')[1])
    s_voxels = float(f.readline().split('\t')[1])
    distance_to_edge = float(f.readline().split('\t')[1])
    voxel_size = float(f.readline().split('\t')[2])


    contacts_list = []
    contact_voxels = 0

    line = f.readline()
    line = f.readline()

    while line != '':
        if line[0:4]=='Cell' or line[0:4] == 'Surf' or line[0:3]== 'Cap' or line[0:4]=='Peri' or line[0:3]=='Exo':
            name = line.strip()
        elif line == '\n':
            contacts_list.append((name, contact_voxels))
            contact_voxels = 0
        else:
            contact_voxels = contact_voxels + float(line.strip())
        line = f.readline()

    if line == '':
        contacts_list.append((name, contact_voxels))

    f.close()
    return (identifier, surface_area, volume, sphericity, bounding_box, ellipticity_p, ellipticity_o, s_voxels, distance_to_edge, voxel_size, contacts_list)
    
def get_file_list(path):
    """Finds all of the .txt files in the folder defined by path and saves their names to a list, which it returns"""
    import os
    file_list = []

    for item in os.listdir(path):
        (root, ext) = os.path.splitext(item)
        if ext == '.txt':
            file_list.append(item)

    return file_list

def export_to_excel(contact_sizes_dict, contact_types_list, cell_metrics_dict, voxel_size, beta_beta_contacts_list):
    import xlsxwriter
    """Writes the quantitative information about the components and the contacts to an Excel spreadsheet
saved in the same folder - compiles the data for easy downstream analysis"""
    
    wb = xlsxwriter.Workbook('Results.xlsx')
    
    sheet1 = wb.add_worksheet('Contact Sizes (voxels)')
    sheet2 = wb.add_worksheet('Contact Sizes (um^2)')

    for i in range(len(contact_types_list)):
        if contact_types_list[i] != ('capillary','peri') and contact_types_list[i] != ('capillary','capillary') and contact_types_list[i] != ('peri','peri') and contact_types_list[i] !=('exocrine', 'peri') and contact_types_list[i] !=('exocrine', 'capillary') and contact_types_list[i] !=('exocrine', 'exocrine') :
            sheet1.write(0, i, str(contact_types_list[i]))
            sheet2.write(0, i, str(contact_types_list[i]))
            for j in range(len(contact_sizes_dict[contact_types_list[i]])):
                sheet1.write(j+1, i, contact_sizes_dict[contact_types_list[i]][j])
                sheet2.write(j+1, i, contact_sizes_dict[contact_types_list[i]][j]*voxel_size)

            

    cell_type_list = sorted(cell_metrics_dict.keys())

    for k in range(len(cell_type_list)):
        working_cell_list = cell_metrics_dict[cell_type_list[k]]
        working_sheet = wb.add_worksheet(str(cell_type_list[k]))
        working_sheet.write(0,0, 'Identifier')
        working_sheet.write(0,1, 'Surface Area')
        working_sheet.write(0,2, 'Volume')
        working_sheet.write(0,3, 'Sphericity')
        working_sheet.write(0,4, 'Bounding Box 1')
        working_sheet.write(0,5, 'Bounding Box 2')
        working_sheet.write(0,6, 'Bounding Box 3')
        working_sheet.write(0,7, 'Ellipticity Prolate')
        working_sheet.write(0,8, 'Ellipticity Oblate')
        working_sheet.write(0,9, 'Surface Voxels')
        working_sheet.write(0,10, 'Calculated Surface Area')
        for p in range(len(contact_types_list)):
            working_sheet.write(0, 11+p, str(contact_types_list[p])+' Count')
            working_sheet.write(0, 11+p+len(contact_types_list), str(contact_types_list[p])+ ' Proportion')

        for m in range(len(working_cell_list)):
            working_sheet.write(m+1, 0, working_cell_list[m][0])
            working_sheet.write(m+1, 1, working_cell_list[m][1])
            working_sheet.write(m+1, 2, working_cell_list[m][2])
            working_sheet.write(m+1, 3, working_cell_list[m][3])
            working_sheet.write(m+1, 4, working_cell_list[m][4][0])
            working_sheet.write(m+1, 5, working_cell_list[m][4][1])
            working_sheet.write(m+1, 6, working_cell_list[m][4][2])
            working_sheet.write(m+1, 7, working_cell_list[m][5])
            working_sheet.write(m+1, 8, working_cell_list[m][6])
            working_sheet.write(m+1, 9, working_cell_list[m][7])
            working_sheet.write(m+1, 10, working_cell_list[m][7]*voxel_size)
            for n in range(len(contact_types_list)):
                working_sheet.write(m+1, 11+n, working_cell_list[m][8][n])
                working_sheet.write(m+1, 11+n+len(contact_types_list), working_cell_list[m][9][n]/working_cell_list[m][7])

    #This part added January 2020 - information for beta cell graph theory connectivity analysis
    last_sheet = wb.add_worksheet('Beta-Beta Contacts')
    beta_cell_list = cell_metrics_dict['beta']
    last_sheet.write(0,0,'Fully embedded Beta Cells')
    for q in range(len(beta_cell_list)):
        last_sheet.write(q+1, 0, beta_cell_list[q][0])
        
    last_sheet.write(0,2,'Vertex 1')
    last_sheet.write(0,3,'Vertex 2')
    last_sheet.write(0,4,'Edge Weight')
    for s in range(len(beta_beta_contacts_list)):
        last_sheet.write(s+1,2, beta_beta_contacts_list[s][0])
        last_sheet.write(s+1,3, beta_beta_contacts_list[s][1])
        last_sheet.write(s+1,4, beta_beta_contacts_list[s][2])
    
    wb.close()
    


#Added 2023-03-19
def export_permutation_beta(p_contact_types_list, beta_contacts_size_p, beta_contacts_counts_p, beta_contacts_proportion_p):
    import xlsxwriter
    
    """#Writes the information from the permutation analysis to an Excel spreadsheet
#saved in the same folder - compiles the data for easy downstream analysis
"""
    
    wb = xlsxwriter.Workbook('Results_permute.xlsx')
    sheet1 = wb.add_worksheet('Contact Type Sizes (um^2)')
    sheet2 = wb.add_worksheet('Contact Type Counts')
    sheet3 = wb.add_worksheet('Contact Type Proportions')
    
    for i in range(len(p_contact_types_list)):
        sheet1.write(0, i, str(p_contact_types_list[i]))
        sheet2.write(0, i, str(p_contact_types_list[i]))
        sheet3.write(0, i, str(p_contact_types_list[i]))
        
        for j in range(len(beta_contacts_size_p[i])):
            sheet1.write(j+1,i,beta_contacts_size_p[i][j])
            
        for k in range(len(beta_contacts_counts_p[i])):
            sheet2.write(k+1,i,beta_contacts_counts_p[i][k])
            sheet3.write(k+1,i,beta_contacts_proportion_p[i][k])
    
    wb.close()
        

    

if __name__ == '__main__':
    #component_channels_dict = get_component_info('XT_OAC_SurfaceSurfaceContactArea_v12_Channel_Intensities.txt')
    #print(component_channels_dict)
    #(name, surface_area, volume, sphericity, bounding_box, s_voxels, voxel_size, contacts_list) = get_component_info('XT_OAC_SurfaceSurfaceContactArea_v12_Cells_1_Cell_Export_[4].txt')
    #print(name)
    #print(surface_area)
    #print(volume)
    #print(sphericity)
    #print(bounding_box)
    #print(s_voxels)
    #print(voxel_size)
    #print(contacts_list)
    print(get_file_list('.'))
