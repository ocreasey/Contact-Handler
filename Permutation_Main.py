#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 19 14:08:21 2023

@author: oliviacreasey
"""

#Olivia Creasey
#2023-03-19
#Permutation analysis for Contact Handler - MAIN

import Contact_Handler_IO as IO
import Contact_Handler_definitions as Definitions
import Contact_Handler_component_type as Component_Type
import Contact_Handler_graphs as Graphs

import copy
import random

#Find the files and load in the list of tissue components and the type for each component
file_list = sorted(IO.get_file_list('.'))
#The channel intensity file should be the first one in the folder
component_channels_dict = IO.get_component_channels(file_list[-1])
#This assumes that the channels are in a file labeled "intensity" and the components are
#in files labeled "downsampled" - may need to change this for different labeling conventions

#Compile the dictionary of each component's type, as defined by the data
component_types_dict = Component_Type.component_type_calculator(component_channels_dict)

#Create a tissue object
current_tissue = Definitions.Tissue(dict(), dict(), [])
##Initialize all of the components in the tissue
#and count how many alpha, beta, and delta cells
n_beta = 0
#n_alpha = 0
#n_delta = 0
components_endocrine = []
for component_name, component_type in component_types_dict.items():
    c = Definitions.Component(component_name, component_type)
    current_tissue.new_component(c)
    if component_type == 'beta':
            n_beta = n_beta + 1
            components_endocrine.append(component_name)
    #elif component_type == 'alpha':
    #        n_alpha = n_alpha + 1
    #       components_endocrine.append(component_name)
    #elif component_type == 'delta':
    #        n_delta = n_delta + 1
    #        components_endocrine.append(component_name)
    
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
        
#start the permutation analysis
p_current_tissue = copy.deepcopy(current_tissue)

for perm in range (1000):
    random.shuffle(components_endocrine)
    for b in range(n_beta):
        p_current_tissue.components_dict[components_endocrine[b]].update_type('beta')
    """for a in range(n_alpha):
        p_current_tissue.components_dict[components_endocrine[a+b+1]].update_type('alpha')
    for d in range(n_delta):
        p_current_tissue.components_dict[components_endocrine[a+b+d+2]].update_type('delta')"""
    #for d in range(n_delta):
    #    p_current_tissue.components_dict[components_endocrine[b+d+1]].update_type('delta')    
        
    for identifier, contact in p_current_tissue.contacts_dict.items():
        contact.update_type(p_current_tissue.components_dict[identifier[0]].component_type,p_current_tissue.components_dict[identifier[1]].component_type)

    p_current_tissue.compile_permutation_beta_contacts()

IO.export_permutation_beta(p_current_tissue.p_contact_types_list, p_current_tissue.beta_contacts_size_p, p_current_tissue.beta_contacts_counts_p, p_current_tissue.beta_contacts_proportion_p)





