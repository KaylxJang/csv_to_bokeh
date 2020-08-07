import math
import numpy as np
from numpy import genfromtxt
from bokeh.plotting import figure, output_file, show
from bokeh.models.markers import X


# Bare with me.  This code is ugly, but hey, it works
# x and y relative data is commented out and not fully implemented bc it is not used

# data slicing / refining portion
data_no_header = np.genfromtxt(data_path, delimiter='\t', skip_header=True)

# with no header, chop off datetime and index
data_no_header_datetime = np.delete(data_no_header, 0, 1) # delete (arr, obj, axis) datetime
data_n_hd = data_no_header_datetime

data_no_header_datetime_index = np.delete(data_no_header_datetime, 0, 1) # delete index
data_n_hdi = data_no_header_datetime_index
#print(data_no_header_datetime)
#print(data_no_header_datetime_index)

# from index column, find max index value
index_list = data_n_hd[:,0]
index_max = int(index_list.max(axis=0)) # vs using np.amax(data_only_numbers, axis=0)

# calculate number of samples and passes
samples = np.ma.size(index_list) # size of array, careful 'np.ma.size' is all elements, here is fine
passes = int(samples / index_max)
#print(passes)

# with coordinate data in index order, create four 1 column arrays from the 4 coordinate columns values (0-3)
x_global = data_n_hdi[:,0]
y_global = data_n_hdi[:,1]
x_relative = data_n_hdi[:,2]
y_relative = data_n_hdi[:,3]
#print(x_global)
#print(y_global)

# create sample vs site array by reshaping the above 1 column arrays into ('passes' # of rows, 'index_max' # of columns)
# this emulates the original Google Sheets process for error checking this process
x_global_sample_vs_site = x_global.reshape(passes, index_max)
y_global_sample_vs_site = y_global.reshape(passes, index_max)
x_relative_sample_vs_site = x_relative.reshape(passes, index_max)
y_relative_sample_vs_site = y_relative.reshape(passes, index_max)
#print(y_global_sample_vs_site)

# renaming so you're not looking at a wall of text
x_global_svs = x_global_sample_vs_site
y_global_svs = y_global_sample_vs_site
x_relative_svs = x_relative_sample_vs_site
y_relative_svs = y_relative_sample_vs_site

#print(x_global_svs)
#print(x_global_svs)
#print(x_relative_svs)

# wall of text removing rows with any '0' element bc theoutputs zeroes if system can't ID feature
# also it's very unlikely that relative positions output all zeros
x_global_sample_vs_site_no_zeros = x_global_svs[np.all(x_global_svs != 0, axis=1)]
y_global_sample_vs_site_no_zeros = y_global_svs[np.all(y_global_svs != 0, axis=1)]
x_relative_sample_vs_site_no_zeros = x_relative_svs[np.all(x_relative_svs != 0, axis=1)]
y_relative_sample_vs_site_no_zeros = x_relative_svs[np.all(y_relative_svs != 0, axis=1)]
#print(x_global_sample_vs_site_no_zeros)

#print(x_global_sample_vs_site_no_zeros.shape)
print(x_global_sample_vs_site_no_zeros.shape)
#print(x_relative_sample_vs_site_no_zeros.shape)
#print(y_relative_sample_vs_site_no_zeros.shape)


# create and append sample vs delta array, using a list for calculations is faster
# use same 'a = []' list to save memory
# insert (index_max, global sample_vs_site_no_zeros)
def gen_sample_vs_delta_no_zeros(id, x):
    a = []
    for i in range(0, id-1):
        a.append(x[:,i+1] - x[:,i])
    a = np.asarray(a)
    global_sample_vs_delta_no_zeros = np.transpose(a)
    return global_sample_vs_delta_no_zeros

# use method to generate data
x_global_sample_vs_delta_no_zeros = gen_sample_vs_delta_no_zeros(index_max, x_global_sample_vs_site_no_zeros)
y_global_sample_vs_delta_no_zeros = gen_sample_vs_delta_no_zeros(index_max, y_global_sample_vs_site_no_zeros)
#x_relative_sample_vs_delta_no_zeros = gen_sample_vs_delta_no_zeros(index_max, x_relative_sample_vs_site_no_zeros)
#y_relative_sample_vs_delta_no_zeros = gen_sample_vs_delta_no_zeros(index_max, y_relative_sample_vs_site_no_zeros)
print(x_global_sample_vs_delta_no_zeros)
print(y_global_sample_vs_delta_no_zeros)
#print(x_relative_sample_vs_delta_no_zeros)
#print(y_relative_sample_vs_delta_no_zeros)



# make one set of the lowest to highest index
delta_site_number = y_global_sample_vs_delta_no_zeros.shape[1]
delta_site_sequence_short = range(1, delta_site_number+1)
#print(delta_site_number)
#print(delta_site_sequence_short)

y_global_sample_vs_delta_no_zeros_ravel = y_global_sample_vs_delta_no_zeros.ravel() # ravel is a view, flatten is a copy
x_global_sample_vs_delta_no_zeros_ravel = x_global_sample_vs_delta_no_zeros.ravel() # ravel is a view, flatten is a copy
#print(y_global_sample_vs_delta_no_zeros_ravel)

passes_no_zeros = y_global_sample_vs_delta_no_zeros.shape[0]

delta_sites_passes = np.empty([0])

delta_site_sequence_long = np.tile(delta_site_sequence_short, y_global_sample_vs_delta_no_zeros.shape[0])
#print(t)



class stats_generator:
    def __init__(self, data):
        self.data = data

    def mean(self):
        return np.mean(self.data, axis=0)

    def mean_of_means(self):
        a = np.mean(self.data, axis=0)
        return np.mean(a, axis=0)

    def sem_pos(self):
        # sem calc
        sem = np.std(self.data, axis=0) / math.sqrt(self.data.shape[0])
        mean = np.mean(self.data, axis=0)
        return mean + sem

    def sem_neg(self):
        # sem calc
        sem = np.std(self.data, axis=0) / math.sqrt(self.data.shape[0])
        mean = np.mean(self.data, axis=0)
        return mean - sem

    def sd1_pos(self):
        mean = np.mean(self.data, axis=0)
        std = np.std(self.data, axis=0)
        return mean + 1*std

    def sd1_neg(self):
        mean = np.mean(self.data, axis=0)
        std = np.std(self.data, axis=0)
        return mean - 1*std

    def sd2_pos(self):
        mean = np.mean(self.data, axis=0)
        std = np.std(self.data, axis=0)
        return mean + 2*std

    def sd2_neg(self):
        mean = np.mean(self.data, axis=0)
        std = np.std(self.data, axis=0)
        return mean - 2*std

    def sd3_pos(self):
        mean = np.mean(self.data, axis=0)
        std = np.std(self.data, axis=0)
        return mean + 3*std

    def sd3_neg(self):
        mean = np.mean(self.data, axis=0)
        std = np.std(self.data, axis=0)
        return mean - 3*std

# create object for stats method
y_stats = stats_generator(y_global_sample_vs_delta_no_zeros)
x_stats = stats_generator(x_global_sample_vs_delta_no_zeros)
#print(y_stats.mean())
#print(y_stats.mean_of_means())
#print(y_stats.sd())
#print(y_stats.sem())




# bokeh starts here


output_file("lol.html")

# figure
p = figure(title='Distance Between Two Features (um) vs Feature Delta Number', y_range=(y_global_sample_vs_delta_no_zeros.min(), y_global_sample_vs_delta_no_zeros.max()*1.002), x_axis_label='Feature Delta Number', y_axis_label='Feature Distance Apart (um)')

# figure style
p.title.text_font_style = 'bold'
p.title.text_font_size = '12pt'
p.xaxis.axis_label_text_font_size = '12pt'
p.yaxis.axis_label_text_font_size = '12pt'
p.xaxis.major_label_text_font_size = '20pt'
p.yaxis.major_label_text_font_size = '20pt'

# data to plot
p.scatter(delta_site_sequence_long, y_global_sample_vs_delta_no_zeros_ravel, radius=0.02, legend='Site Samples')
p.circle(delta_site_sequence_short, y_stats.mean(), radius=0.1, color='red', legend='Site Mean') # mean of delta group

# sd markers
p.rect(delta_site_sequence_short, y_stats.sd1_neg(), 0.4, 0.0004, line_color="black", fill_color="black", legend='Site SD1').visible = False
p.rect(delta_site_sequence_short, y_stats.sd1_pos(), 0.4, 0.0004, line_color="black", fill_color="black", legend='Site SD1').visible = False
p.rect(delta_site_sequence_short, y_stats.sd2_neg(), 0.4, 0.0004, line_color="black", fill_color="black", legend='Site SD2').visible = False
p.rect(delta_site_sequence_short, y_stats.sd2_pos(), 0.4, 0.0004, line_color="black", fill_color="black", legend='Site SD2').visible = False
# sd stem
p.segment(delta_site_sequence_short, y_stats.sd1_neg(), delta_site_sequence_short, y_stats.sd1_pos(), line_color="gray", line_width=1, legend='Site SD1').visible = False
p.segment(delta_site_sequence_short, y_stats.sd2_neg(), delta_site_sequence_short, y_stats.sd2_pos(), line_color="lightgray", line_width=1, legend='Site SD2').visible = False

# sem markers
p.rect(delta_site_sequence_short, y_stats.sem_pos(), 0.4, 0.0004, line_color="black", fill_color="black", legend='Site SEM')
p.rect(delta_site_sequence_short, y_stats.sem_neg(), 0.4, 0.0004, line_color="black", fill_color="black", legend='Site SEM')
# sem stem
p.segment(delta_site_sequence_short, y_stats.sem_pos(), delta_site_sequence_short, y_stats.sem_neg(), line_color="black", line_width=1, legend='Site SEM')

# linear fit generator and graphing
par = np.polyfit(delta_site_sequence_long, y_global_sample_vs_delta_no_zeros_ravel, 1, full=True)
slope = par[0][0]
intercept = par[0][1]
y_predicted = [slope*i + intercept  for i in delta_site_sequence_long]
print('slope: {}'.format(slope))

p.line(delta_site_sequence_long, y_predicted, color='red', legend='y='+str(round(slope, 2))+'x+'+str(round(intercept, 2)))


# legend interactivity
p.legend.location = 'top_right'
p.legend.click_policy = "hide"

show(p)