#Olivia Creasey
#Bioengineering PhD Candidate; Gartner Lab UCSF
#August/September 2019; edited January 2020
#Edited September 2021 for 147_mini_1
#Edited March 2023 for permutation analysis

"""This module defines classes useful for managing cell-cell and cell-ECM
contact data output by OAC's Contact Calculator XTension. These classes are 
the Tissue class, Contact class, and Component class. This code was made 
specifically for use in OAC's application with 3D confocal images of 
pancreatic islets - some variable names and values
may need to be changed in a different application."""

class Tissue:
    """The Tissue class contains a dictionary contacts_dict that itself
holds Contact objects. The Tissue class also contains a dictionary
components_dict which contains Component objects. The Tissue class also
contains a list cells_list which lists the identifiers of the Component
objects in the components_dict that correspond to cells that are fully
embedded in the 3D image analyzed."""
    def __init__(self, contacts_dict, components_dict, cells_list):
        self.contacts_dict = contacts_dict
        self.components_dict = components_dict
        self.cells_list = cells_list
        self.cell_metrics_dict = dict()
        self.contact_sizes_dict = dict()
        self.contact_types_list = []
        self.beta_beta_contacts_list =[]
        self.voxel_size = float(1)
        
        #added for permutation analysis
        self.p_contact_types_list = [('beta','beta') , ('alpha','beta') , ('beta','delta') , ('beta','capillary') , ('beta','peri')]
        self.beta_contacts_size_p = [[],[],[],[],[]]
        self.beta_contacts_counts_p = [[],[],[],[],[]]
        self.beta_contacts_proportion_p = [[],[],[],[],[]]
        
        """ self.beta_beta_contacts_size_p =[]
        self.beta_alpha_contacts_size_p =[]
        self.beta_delta_contacts_size_p =[]
        self.beta_capillary_contacts_size_p =[]
        self.beta_peri_contacts_size_p =[]
        self.beta_beta_contacts_number_p =[]
        self.beta_alpha_contacts_number_p =[]
        self.beta_delta_contacts_number_p =[]
        self.beta_capillary_contacts_number_p =[]
        self.beta_peri_contacts_number_p =[]
        self.beta_beta_contacts_proportion_p =[]
        self.beta_alpha_contacts_proportion_p =[]
        self.beta_delta_contacts_proportion_p =[]
        self.beta_capillary_contacts_proportion_p =[]
        self.beta_peri_contacts_proportion_p =[]"""
        
        
        
        
    def new_contact(self, contact):
        """Takes a Contact object and adds it to the Tissue's dictionary of Contacts"""
        self.contacts_dict[contact.identifier] = contact

    def new_component(self, component):
        """Takes a Component object and adds it to the Tissue's dictionary of Components"""
        self.components_dict[component.identifier] = component

    def find_cells(self):
        """Identifies the Component objects in the Tissue that are both fully inside the image 
        and that are either labeled cells or are touching labeled cells,
creating the Cells_List. It also returns a sorted list of all of the Contact types in the tissue."""
        
        working_contact_types_set = set()
        for component_name, component_object in self.components_dict.items(): #loop through the dictionary of Components

                touching_endocrine = 0

                for contact_name in component_object.contact_list: #loop through all contacts for each Component
                    #create a set listing all of the contact types in the tissue 
                    working_contact_types_set.add(self.contacts_dict[contact_name].contact_type)
                    
                    #Test whether the Component is involved in any endocrine-contacting Contacts
                    if 'alpha' in self.contacts_dict[contact_name].contact_type: 
                        touching_endocrine = 1
                    elif 'delta' in self.contacts_dict[contact_name].contact_type:
                        touching_endocrine = 1
                    elif 'beta' in self.contacts_dict[contact_name].contact_type:
                        touching_endocrine = 1

            
                if touching_endocrine == 1 and component_object.distance_to_edge > 0.2 :
                    self.cells_list.append(component_name)
  
        self.contact_types_list = sorted(working_contact_types_set)


            

    def compile_cells_and_contacts(self):
        """This method runs through all of the data stored in the Component and Contact objects and creates lists of Contact size by type
and of various Component parameters by Component type, for all of the Components in the Cells_List and associated Contacts"""
        working_contacts_set = set()
            
        for cell in self.cells_list: #Loops through all Cells and measures the number of each type of Contact for each cell
            #and the number of surface voxels involved in each type of contact (summed)
            working_contacts_counts = [0]*len(self.contact_types_list)
            working_contacts_area = [0]*len(self.contact_types_list)
            working_cell = self.components_dict[cell]
            for item in working_cell.contact_list:
                working_contact = self.contacts_dict[item]
                """"2023-04-10 to avoid contacts so small that they were only measured once"""
                if len(working_contact.number_of_voxels)!=2:
                    continue
                
                for i in range(len(self.contact_types_list)):
                    if working_contact.contact_type == self.contact_types_list[i]:
                        working_contacts_counts[i] = working_contacts_counts[i] + 1
                        working_contacts_area[i] = working_contacts_area[i] + working_contact.get_size()
                    
                if item not in working_contacts_set:
                    working_contacts_set.add(item)
                    try:
                        self.contact_sizes_dict[working_contact.contact_type].append(working_contact.get_size())
                    except KeyError:
                        self.contact_sizes_dict[working_contact.contact_type]=[working_contact.get_size()]

                
            try:#Add Cells to the cell_metrics_dict by component type.
                #Basically a dictionary of lists containing all of the information for each cell, separated by type
                self.cell_metrics_dict[working_cell.component_type].append((working_cell.identifier, working_cell.surface_area,
                                                                               working_cell.volume, working_cell.sphericity,
                                                                               working_cell.bounding_box, working_cell.ellipticity_p,
                                                                               working_cell.ellipticity_o, working_cell.surface_voxels,
                                                                            working_contacts_counts, working_contacts_area))
            except KeyError:
                self.cell_metrics_dict[working_cell.component_type]=[(working_cell.identifier, working_cell.surface_area,
                                                                               working_cell.volume, working_cell.sphericity,
                                                                               working_cell.bounding_box, working_cell.ellipticity_p,
                                                                               working_cell.ellipticity_o, working_cell.surface_voxels,
                                                                       working_contacts_counts, working_contacts_area)]
                

            self.voxel_size = working_cell.voxel_size 
            
            
    def compile_beta_beta_contacts(self):
        """This method written for the first time January 2020; Compiles all beta-beta contacts and their
        sizes (regardless of whether or not associated cells are fully embedded) so that the information can
        later be used for graph theory analyses"""
        """"Edited April 10, 2023 to avoid contacts so small that they were only measured once"""
        for identifier, contact in self.contacts_dict.items():
            if contact.contact_type == ('beta','beta') and len(contact.number_of_voxels)==2:
                self.beta_beta_contacts_list.append((identifier[0],identifier[1],contact.get_size()))
                
    
    def compile_permutation_beta_contacts(self):
        """"For the permutation analysis 2023-03-19"""
        #working_types_list = [('beta','beta') , ('alpha','beta') , ('beta','delta') , ('beta','capillary') , ('beta','peri')]

        """for identifier, contact in self.contacts_dict.items():
            if contact.contact_type == ('beta','beta'):
                self.beta_beta_contacts_size_p.append(contact.get_size())
            elif contact.contact_type == ('alpha','beta'):
                self.beta_alpha_contacts_size_p.append(contact.get_size())
            elif contact.contact_type == ('beta','delta'):
                self.beta_delta_contacts_size_p.append(contact.get_size())
            elif contact.contact_type == ('beta','capillary'):
                self.beta_capillary_contacts_size_p.append(contact.get_size())
            elif contact.contact_type == ('beta','peri'):
                self.beta_peri_contacts_size_p.append(contact.get_size())"""
        
        contacts_set = set()
        
        for component_name, component_object in self.components_dict.items():
            if component_object.component_type == 'beta':
                
                working_contacts_counts = [0, 0, 0, 0, 0]
                working_contacts_size = [0, 0, 0, 0, 0]
               # contact_already_counted = 0
                
                for contact in component_object.contact_list:
                 #   if contact in contacts_set:
                  #      contact_already_counted = 1
                
                    
                    working_contact = self.contacts_dict[contact]
                    """"2023-04-10 to avoid contacts so small that they were only measured once"""
                    if len(working_contact.number_of_voxels)!=2:
                        continue
                    
                    #contacts_set.add(contact)

                    i = 0
                    for p_type in self.p_contact_types_list:
                        if working_contact.contact_type == p_type:
                            working_contacts_counts[i] = working_contacts_counts[i] + 1
                            working_contacts_size[i] = working_contacts_size[i] + working_contact.get_size()
                            """"If statement added April 11 2023 because previously contacts had been skipped for contact count and contact proportion"""
                            if contact not in contacts_set:
                                self.beta_contacts_size_p[i].append(working_contact.get_size()*component_object.voxel_size)
                                contacts_set.add(contact)
                            break
                        i = i+1
                
                working_contacts_proportion = [x/component_object.surface_voxels for x in working_contacts_size]

                
                
                for j in range(len(self.p_contact_types_list)):
                    self.beta_contacts_counts_p[j].append(working_contacts_counts[j])
                    self.beta_contacts_proportion_p[j].append(working_contacts_proportion[j])
                    
                    """if contact.contact_type == ('beta','beta'):
                        working_contacts_counts[0] = working_contacts_counts[0] + 1
                        working_contacts_size[0] = working_contacts_size[0] + contact.get_size()
                        self.beta_beta_contacts_size_p.append(contact.get_size())
                        
                    elif contact.contact_type == ('alpha','beta'):
                        working_contacts_counts[1] = working_contacts_counts[1] + 1
                        working_contacts_size[1] = working_contacts_size[1] + contact.get_size()
                        self.beta_alpha_contacts_size_p.append(contact.get_size())
                        
                    elif contact.contact_type == ('beta','delta'):
                        working_contacts_counts[2] = working_contacts_counts[2] + 1
                        working_contacts_size[2] = working_contacts_size[2] + contact.get_size()
                        self.beta_delta_contacts_size_p.append(contact.get_size())
                        
                    elif contact.contact_type == ('beta','capillary'):
                        working_contacts_counts[3] = working_contacts_counts[3] + 1
                        working_contacts_size[3] = working_contacts_size[3] + contact.get_size()
                        self.beta_capillary_contacts_size_p.append(contact.get_size())
                        
                    elif contact.contact_type == ('beta','peri'):
                        working_contacts_counts[4] = working_contacts_counts[4] + 1
                        working_contacts_size[4] = working_contacts_size[4] + contact.get_size()
                        self.beta_peri_contacts_size_p.append(contact.get_size())"""
                    
                
            
        


class Contact:
    """Contact class objects contain the information about individual cell-cell
and cell-ECM contacts in the 3D image. Each Contact object has an identifier,
a contact_type, and a size (number of voxels)."""
    def __init__(self, component1, component2, voxels_measurement):
        self.identifier = tuple(sorted([component1.identifier, component2.identifier]))

        self.number_of_voxels = []
        self.number_of_voxels.append(voxels_measurement)
        self.contact_type = tuple(sorted([component1.component_type, component2.component_type]))


    def add_replicate_measurement(self, voxels_measurement):
        """Each Contact may be measured twice (as a part of each of two Components) - both measurements
are stored in number_of_voxels, which is a list"""
        self.number_of_voxels.append(voxels_measurement)

    def get_size(self):
        """Returns the average of all voxels measurements in the contact's number_of_voxels list"""
        average = sum(self.number_of_voxels)/len(self.number_of_voxels)
        return average
    
    def update_type(self, component1_ptype, component2_ptype):
        """"For the permutation analysis 2023-03-19"""
        self.contact_type = tuple(sorted([component1_ptype, component2_ptype]))
        



class Component:
    """Component class objects contain the information about individual
tissue components (cells and ECM structures like capillaries) found within
the 3D image. Each Component object has an identifier, a component_type, volume, surface
area, sphericity, bounding box, ellipticity prolate and ellipticity oblate, 
and a list containing the identifiers for the
Contact objects associated with that Component."""
    def __init__(self, name, component_type):
        self.identifier = name
        self.component_type = component_type
        self.contact_list = []

    def add_component_features(self, surface_area, volume, sphericity, bounding_box, ellipticity_p, ellipticity_o, surface_voxels, distance_to_edge, voxel_size):
        """Adds features to an existing Component Object"""
        self.surface_area = surface_area
        self.volume = volume
        self.sphericity = sphericity
        self.bounding_box = bounding_box
        self.ellipticity_p = ellipticity_p
        self.ellipticity_o = ellipticity_o
        self.surface_voxels = surface_voxels
        self.distance_to_edge = distance_to_edge
        self.voxel_size = voxel_size

    def add_contact(self, contact):
        """Adds a single Contact identifier to the list of Contacts associated with a Component"""
        self.contact_list.append(contact.identifier)
        
    def update_type(self, ptype):
        """"For the permutation analysis 2023-03-19"""
        self.component_type = ptype
        


            
        

if __name__ == '__main__':
    current_tissue = Tissue(dict(), dict(), [])

    component1 = Component('Cell 100', 'beta')
    component2 = Component('Cell4', 'matrix')

    contact_name = tuple(sorted([component2.identifier,component1.identifier]))

    contact1 = Contact(component1, component2, 143)

    print(component1.identifier)
    print(component1.component_type)
    print()
    print(component2.identifier)
    print(component2.component_type)
    print()
    print(contact1.identifier)
    print(contact1.number_of_voxels)
    print(contact1.contact_type)
    contact1.add_replicate_measurement(155)
    print(contact1.number_of_voxels)
    print(contact1.get_size())
    print()
    current_tissue.new_contact(contact1)
    current_tissue.new_component(component1)
    current_tissue.new_component(component2)
    print(current_tissue.contacts_dict)
    print(current_tissue.components_dict)
    print(current_tissue.cells_list)
    component1.add_contact(contact1)
    print(component1.contact_list)


