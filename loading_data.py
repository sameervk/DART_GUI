import numpy as np
import pandas as pd
from datafile_destinations import filepath


def load_data(choice = 'selected_', directories = ['folder']):
    
    # list containing the data as pandas DataFrame
    diffdata_list = []
    
    # list containing the corresponding thickness list
    thickness_list = []
    
    # list containing the corresponding sample details
    sample_name_list = []
    
    # object for holder the maximum slider value
    max_slider_val = 0
    
    for folder in directories:
        npz_file = np.load(folder + choice + 'diff_rpp_rss.npz', allow_pickle=True)
        print('Files in npz:', npz_file.files)

        diff_rpp_rss = pd.DataFrame(data=npz_file['values'], index=npz_file['index'], columns=npz_file['col_names'])
        diff_rpp_rss.index.name = npz_file['index_name']
        
        print('Sample: ', npz_file['meta_data'])
        sample_name_list.append(npz_file['meta_data'])

        times_thicknesses = pd.read_csv(folder + choice + 'times_thickness.csv')
        # dropping the 1st and the last to keep the derivative calc consistent,
        # i.e. removing the calculations at the boundaries: 1st and the last point.
        # times_thicknesses = times_thicknesses.iloc[1:-1]
        # times_thicknesses.reset_index(inplace=True, drop=True)
        thickness_list.append(times_thicknesses)
        
        # Setting the maximum value of the slider
        max_slider_val = times_thicknesses.iloc[:,1].values[-1] if times_thicknesses.iloc[:,1].values[-1] > \
                                                                   max_slider_val else max_slider_val

        # diff_rpp_rss = diff_rpp_rss.iloc[1:-1]  # dropping the 1st and last
        diffdata_list.append(diff_rpp_rss)
        
    return diffdata_list, thickness_list, sample_name_list, max_slider_val
            
    
if __name__=='__main__':
    
    
    filepath_list = filepath(no=2)
    
    data_for_plotting = load_data(directories=filepath_list)
        
        
        
    
    
    