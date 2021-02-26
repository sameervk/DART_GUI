import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.widgets import Slider, RadioButtons
from matplotlib.collections import LineCollection
from matplotlib.ticker import AutoMinorLocator, LogLocator
from matplotlib.artist import Artist

from numpy import absolute, real, array, float16, column_stack, full, arange, round
import sys

from loading_data_v2 import load_data

"""
From v2. For data with no thicknesses.
"""

class Plotting:
    
    """
    Plots absolute value of delrho as a function of thickness for a maximum of 6 figures.
    Slider is used to change the thickness value.
    Left plot of a row plots only 1 line at the corresponding thickness.
    Right plot of a row plots this line and all the previous ones starting at 1 nm.
    The code can be improved by parallelizing the update of the plots when thickness is changed.
    
    version 2: Flattening the axes array
    
    """
    
    
    def __init__(self, diffdata_list = [], sample_list = [], time_step = 1, max_slider_val = 50):
    
        # Initializing matplotlib properties
        self.cmap = cm.hsv_r # colormap
        self.minorlocator = AutoMinorLocator()
        self.logminorlocator = LogLocator(base=10.0, subs=arange(0.1, 1, 0.05), numticks=4)
        
        self.diffdata_list = diffdata_list
        # self.thickness_list = thickness_list
        self.time_list = [diffdata_list[i].index.to_numpy() for i in range(len(diffdata_list))]
        self.sample_names = sample_list
        
        self.time_step = time_step
        self.max_slider_val = max_slider_val
        self.no_of_plots = len(sample_list)
        
        # self.sizelist = [len(i) for i in self.thickness_list]
        self.sizelist = [len(i) for i in self.time_list]
        # captures the different lengths of each sample's dataframe
        
        if self.no_of_plots > 3:
            
            sys.exit("Max number allowed is 3 plots. Exiting...")
        
        else:
            ncols = 2
            nrows = self.no_of_plots
        

        
        self.energy_ev = array(diffdata_list[0].columns).astype(float16)
        self.x_lim = (self.energy_ev.min(), self.energy_ev.max())
        self.y_lim = []
        
        self.fig, self.ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(16,16))
        self.ax = self.ax.flatten()
        # tight_layout = True, constrained_layout =True: cant use these with subplots_adjust
        self.fig.subplots_adjust(left=0.1, bottom=0.2)
        self.fig.suptitle('DART results of ' + str(self.sample_names[0]), fontsize = 16, fontweight='bold', x=0.5, y=0.94)
        self.data_segments = []
        self.axis_collections = []
        self.textvar =  self.fig.text(x = 0.3, y = 0.7, s = '')
        

        index = 0
        for i, diff_rpp_rss, in zip(range(self.no_of_plots), diffdata_list):
        
        
            y_lim = (0.00001, absolute(diff_rpp_rss.values).flatten().max())
            # y_lim = (real(diff_rpp_rss.values).flatten().min(), real(diff_rpp_rss.values).flatten().max())
            self.y_lim.append(y_lim)
            
            for j in range(2):
                self.ax[index].set_xlim(auto=True, xmin=self.x_lim[0], xmax=self.x_lim[1])
                self.ax[index].set_ylim(auto=True, ymin=y_lim[0], ymax=y_lim[1])
                self.ax[index].xaxis.set_label_text('Wavelength (nm)', fontweight='bold', fontsize=14)
                self.ax[index].set_ylabel(r'|$\delta \rho$|', fontweight='bold', fontsize=14)
                self.ax[index].xaxis.set_tick_params(which='minor', width=1, length=5)
                self.ax[index].xaxis.set_tick_params(which='major', width=1, length=10)
                
                self.init_segments = [column_stack([self.energy_ev, full(shape=len(self.energy_ev), fill_value=1,
                                                                     dtype=float16)])]
                lincoll = LineCollection(segments=self.init_segments, linewidths=1.5, linestyles='solid',
                                                         cmap=cm.get_cmap(self.cmap))
                self.data_segments.append(lincoll)
                
                self.axis_collections.append(self.ax[index].add_collection(self.data_segments[index]))
                index = index+1
        
        # Setting titles for the single line plots only
        # [self.ax[j].set_title(self.sample_names[i], y = 0.9,) for i,j in enumerate(range(0, self.no_of_plots*2,2))]
        
        # Colorbar for multiple line plots only
        [self.data_segments[j].set_array(self.diffdata_list[i].index.to_numpy()[::self.time_step]) for i,j in
         enumerate(range(1, self.no_of_plots*2, 2))]
        # [self.data_segments[j].set_array(self.thickness_list[i].iloc[:,1].values[::self.thickness_step]) for i,j in
        #  enumerate(range(1, self.no_of_plots*2, 2))]

        
        self.cbar = [self.fig.colorbar(self.data_segments[i], ax = self.ax[i], label = 'time (min)') for i in
                     range(1, self.no_of_plots*2, 2)]
        
        # Adding slider
        axcolor = 'lightgoldenrodyellow'
        # axthickness = self.fig.add_axes([0.2, 0.05, 0.65, 0.03], facecolor=axcolor)
        axtime = self.fig.add_axes([0.2, 0.05, 0.65, 0.03], facecolor=axcolor)



        self.time_slider = Slider(axtime, label='', valmin=0, valmax=max_slider_val,
          valinit=0, valfmt='%d', valstep=self.time_step)
        
        
        self.draw_data()
        self.time_slider.on_changed(self.draw_data)
        

        # Adding radio buttons
        rax = self.fig.add_axes([0.025, 0.05, 0.15, 0.1], facecolor=axcolor)
        self.radiobutton = RadioButtons(rax, ('Linear', 'SemiLogY', 'SemiLogX', 'LogLog'), active=0)
        self.radiobutton.on_clicked(self.axes_func)
        
        print(self.radiobutton.value_selected)

    def draw_data(self, slider_value='1'):
        rows = int(slider_value)
        if rows == 0 or rows == -1:
            [i.set_segments(self.init_segments) for i in self.data_segments]
            # reset all graphs
            
        else:
            idx = 0
            for i in range(self.no_of_plots):
               
                multiplesegments = [column_stack([self.energy_ev, absolute(row)]) for row in
                            self.diffdata_list[i].iloc[:rows:self.time_step].values]
                self.data_segments[idx+1].set_segments(multiplesegments)
                
                if rows > self.sizelist[i]:
                    # if rows is greater than the len of the dataframe, plotting single
                    # lines throws an error
                    singlesegments = [
                        column_stack([self.energy_ev, absolute(self.diffdata_list[i].iloc[self.sizelist[i] - 1].values)])]
                    self.data_segments[idx].set_segments(singlesegments)
                    idx = idx + 2
                
                else:
                    singlesegments = [column_stack([self.energy_ev, absolute(self.diffdata_list[i].iloc[rows-1].values)])]
                    self.data_segments[idx].set_segments(singlesegments)
                    idx = idx+2
                    Artist.remove(self.textvar)
                    self.textvar = self.fig.text(x = 0.3, y = 0.85, s = 't = %0.2f min'%(self.time_list[i][rows-1]), fontsize = 15)

        
            # For confirming sync between diff_rpp_rss, thickness and Slider value
            # Checking using the values of the last sample set
            # print(self.diffdata_list[self.no_of_plots-1].index.to_numpy()[:rows:self.thickness_step][-1],
            #       round(self.thickness_list[self.no_of_plots-1].iloc[:, 0].values[:rows:self.thickness_step][-1], 3),
            #       round(self.thickness_list[self.no_of_plots-1].iloc[:, 1].values[:rows:self.thickness_step][-1], 1))

            
    
    
    
    def axes_func(self, label='Linear'):
        if label == 'SemiLogY':
            print(self.radiobutton.value_selected)
            
            [i.remove() for i in self.axis_collections]
            self.axis_collections.clear()
            [self.axis_collections.append(self.ax[i].add_collection(self.data_segments[i])) for i in range(
                self.no_of_plots*2)]
            
            self.axes_properties(scale=label)
            self.fig.canvas.draw_idle()
            # If this is not used, then the plot is not update until the slider value is changed
    
        elif label == 'SemiLogX':
            print(self.radiobutton.value_selected)
            
            [i.remove() for i in self.axis_collections]
            self.axis_collections.clear()
            [self.axis_collections.append(self.ax[i].add_collection(self.data_segments[i])) for i in range(
                self.no_of_plots * 2)]
            
            self.axes_properties(scale=label)
            self.fig.canvas.draw_idle()
    
    
        elif label == 'LogLog':
            print(self.radiobutton.value_selected)
            
            [i.remove() for i in self.axis_collections]
            self.axis_collections.clear()
            [self.axis_collections.append(self.ax[i].add_collection(self.data_segments[i])) for i in range(
                self.no_of_plots * 2)]
            
            self.axes_properties(scale=label)
            self.fig.canvas.draw_idle()
    
        else:
            print(self.radiobutton.value_selected)
            
            [i.remove() for i in self.axis_collections]
            self.axis_collections.clear()
            [self.axis_collections.append(self.ax[i].add_collection(self.data_segments[i])) for i in range(
                self.no_of_plots * 2)]
            
            self.axes_properties(scale=label)
            self.fig.canvas.draw_idle()

    def axes_properties(self, scale='Linear'):
    
        if scale == 'Linear':
            [i.set_xscale(value='linear') for i in self.ax]
            [i.set_yscale(value='linear') for i in self.ax]
            [i.xaxis.set_minor_locator(self.minorlocator) for i in self.ax]
            self.set_ax_limits()
    
        elif scale == 'SemiLogX' or scale == 'LogLog':
            # ax.cla()
            [i.set_xscale(value='log') for i in self.ax]
        
            if scale == 'LogLog':
                [i.set_yscale(value='log') for i in self.ax]
            else:
                [i.set_yscale(value='linear') for i in self.ax]
            [i.xaxis.set_minor_locator(self.logminorlocator) for i in self.ax]
            self.set_ax_limits()
    
    
        else:
            [i.set_xscale(value='linear') for i in self.ax]
            [i.set_yscale(value='log') for i in self.ax]
            [i.xaxis.set_minor_locator(self.minorlocator) for i in self.ax]
            self.set_ax_limits()

    def set_ax_limits(self):
        [i.set_xlim(auto=True, xmin=self.x_lim[0], xmax=self.x_lim[1]) for i in self.ax]
        
        idx=0
        for i in range(self.no_of_plots):
            self.ax[idx].set_ylim(auto=True, ymin=self.y_lim[i][0], ymax=self.y_lim[i][1])
            self.ax[idx+1].set_ylim(auto=True, ymin=self.y_lim[i][0], ymax=self.y_lim[i][1])
            idx = idx+2


            



if __name__=='__main__':
    
    AnisoOrg =  ['/home/sameer/Ellipsometer_data/Data/Sameer/Sameer/RDA/Woollam_simulations/Aniso_Organic/']
    
    IsoOrg =  ['/home/sameer/Ellipsometer_data/Data/Sameer/Sameer/RDA/Woollam_simulations/Iso_Organic/']

  
    
    SiN = ['/home/sameer/Ellipsometer_data/Data/Sameer/Sameer/RDA/Woollam_simulations/Si3N4/']

    AlGaAs = ['/home/sameer/Ellipsometer_data/Data/Sameer/Sameer/RDA/Woollam_simulations/AlGaAs/']
    
    test_folders = IsoOrg

    diffdata_list, sample_list, max_slider_val = load_data(choice='selected_',directories=test_folders)

    time_step = 1
    
    plot_object = Plotting(diffdata_list, sample_list, time_step, max_slider_val)

    
    # self.figure.show() # this opens and closes the self.figure in the blink of an eye.
    # plt.tight_layout(rect=(0,0,0.8,0.8))
    plt.show()
        