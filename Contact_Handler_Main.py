#Olivia Creasey
#Bioengineering PhD Candidate; Gartner Lab UCSF
#August/September 2019; edits January 2020
#edits September 2021 for 147_mini_1

"""This is the main program for managing the cell-cell and cell-ECM contact
data output by the OAC Contact Calculator Xtension."""

import Contact_Handler_IO as IO
import Contact_Handler_definitions as Definitions
import Contact_Handler_component_type as Component_Type
import Contact_Handler_graphs as Graphs

#Find the files and load in the list of tissue components and the type for each component
file_list = sorted(IO.get_file_list('.'))
#The channel intensity file should be the first one in the folder
component_channels_dict = IO.get_component_channels(file_list[-1])
#This assumes that the channels are in a file labeled "intensity" and the components are
#in files labeled "downsampled" - may need to change this for different labeling conventions

Component_Type.component_type_histograms(component_channels_dict)
#Graphs.make_intensities_plot(component_channels_dict)
component_types_dict = Component_Type.component_type_calculator(component_channels_dict)
#
#
current_tissue = Definitions.Tissue(dict(), dict(), [])
##Initialize all of the components in the tissue
for component_name, component_type in component_types_dict.items():
    c = Definitions.Component(component_name, component_type)
    current_tissue.new_component(c)

#Go through the remaining files and read in the contact-specific and component-specific spatial information
#This assumes that the channels are in a file labeled "zzzChannel" and the components are
#in files labeled pretty much anything else - may need to change this for different labeling conventions
    #The "zzzChannel" thing is kind of cheating, but I don't care
for i in range(len(file_list)-1):
    (name, surface_area, volume, sphericity, bounding_box, ellipticity_p, ellipticity_o, s_voxels, distance_to_edge, voxel_size, contacts_list) = IO.get_component_info(file_list[i])
    working_component = current_tissue.components_dict[name]
    working_component.add_component_features(surface_area, volume, sphericity, bounding_box, ellipticity_p, ellipticity_o, s_voxels, distance_to_edge, voxel_size)

    
    for j,k in contacts_list:
        contact_name = tuple(sorted([name, j]))
        if contact_name in current_tissue.contacts_dict.keys():
            current_tissue.contacts_dict[contact_name].add_replicate_measurement(k)
        else:
            current_tissue.contacts_dict[contact_name]=Definitions.Contact(working_component, current_tissue.components_dict[j], k)

        working_component.add_contact(current_tissue.contacts_dict[contact_name])


#decide which components are "cells" - i.e. entirely within the image and involved in an endocrine-labeled contact
current_tissue.find_cells()
#print(current_tissue.cells_list)
#crunch the data to put it in lists that are more useable
current_tissue.compile_cells_and_contacts()
current_tissue.compile_beta_beta_contacts()#Added January 2020
#print(current_tissue.contact_sizes_dict.keys())
#export data to an Excel spreadsheet
IO.export_to_excel(current_tissue.contact_sizes_dict, current_tissue.contact_types_list,
                   current_tissue.cell_metrics_dict, current_tissue.voxel_size, current_tissue.beta_beta_contacts_list)

