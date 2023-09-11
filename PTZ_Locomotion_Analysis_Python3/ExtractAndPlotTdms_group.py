# This code was adapted by Khwa Zhong Xuan, February 2021.
# Original code writted by Li Hankun, 2017.

#######################
###     Imports     ###
#######################

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
from nptdms import TdmsFile
import os, sys, string, math, openpyxl, shutil, csv
import pandas as pd

# Set Values
JITTER_THRESHOLD = 2
PAUSE_LEN = 3
FPS = 1000

##############################
###    Helper Functions    ###
##############################

def count_samples(tdms):
    min_sample = np.inf
    max_sample = 0
    for channel in tdms["Tracker"].channels():
        try:
            sample_no = int(channel.name[-3:])
        except:
            continue
        if sample_no < min_sample:
            min_sample = sample_no
        if sample_no > max_sample:
            max_sample = sample_no
    return min_sample, max_sample


##############################
###    files gouping Functions    ###
##############################


def groupfile():
    
    from nptdms import TdmsFile
    import os, shutil, re, csv
    import pandas as pd
    import numpy as np
    fullpath = os.getcwd()
    fileall = os.listdir(fullpath)
    if 'groupfile.xlsx' in fileall:
        os.remove('groupfile.xlsx')
        print('remove previous groupfile.xlsx')
    _nsre = re.compile('([0-9]+)')
    def natural_sort_key(s):
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split(_nsre, s)]
    pau_file = [os.path.join(root, name) for root, dirs, files in os.walk(fullpath) for name in files if name == 'PauseSummary.csv']
    pau_file.sort(key=natural_sort_key)

    v_file = [os.path.join(root, name) for root, dirs, files in os.walk(fullpath) for name in files if name == 'V_category.csv']
    v_file.sort(key=natural_sort_key)

    dis_file = [os.path.join(root, name) for root, dirs, files in os.walk(fullpath) for name in files if name == 'TotalDistance.csv']
    dis_file.sort(key=natural_sort_key)
    with pd.ExcelWriter('groupfile.xlsx', engine = 'xlsxwriter') as writer:
        i=j=k=0
        for file in pau_file:
            tmp = pd.read_csv(file)
            tmp = pd.DataFrame(tmp)
            if i==0:
                pause_dt = tmp
            else:
                tmp = tmp.drop(columns='Sample') 
                #pause_dt = pd.merge(pause_dt,tmp,on = 'Sample')
                pause_dt = pd.concat([pause_dt,tmp],axis = 1)
            i+=1

        for file in v_file:
            tmp = pd.read_csv(file)
            tmp = pd.DataFrame(tmp)
            if j==0:
                vel_dt = tmp
            else:
                vel_dt = pd.concat([vel_dt,tmp],axis = 1)
            j+=1    

        for file in dis_file:
            tmp = pd.read_csv(file)
            tmp = pd.DataFrame(tmp)
            if k==0:
                dis_dt = tmp
            else:
                dis_dt = pd.concat([dis_dt,tmp],axis = 1)
            k+=1 

        pause_dt.to_excel(writer,sheet_name = 'PauseSummary',index = False)
        vel_dt.to_excel(writer,sheet_name = 'V_Category',index = False)
        dis_dt.to_excel(writer,sheet_name = 'TotalDistance',index = False)

##############################
###    Main Program Begins ###
##############################

# Check Arguments to determine run type
args = sys.argv
files = []
if len(args) == 1:
    # Search current working directory for .tdms files.
    print("No file specified, searching current directory for all .tdms files.")
    for name in os.listdir(os.getcwd()):
        if name.endswith(".tdms"):
            files.append(name)
elif len(args) == 2:
    # Run program for specific file.
    if not args[1].endswith(".tdms"):
        print("Specified file is not a .tdms file. Aborting.")
        exit(1)
    files.append(args[1])

# Loop through .tdms files
while files:
    filename = files.pop()
    print("--------------")
    print("NOW WORKING ON: %s" % filename)

    # Checking and creating folder for tdms files.
    dirname = filename.rstrip('.tdms') + '/'
    if os.path.exists(dirname):
        print("%s already exist, removing original and rewriting." % dirname)
        shutil.rmtree(dirname)
    os.makedirs(dirname + 'RawData/')
    os.makedirs(dirname + 'Velocity/')
    os.makedirs(dirname + 'Pause/')
    os.makedirs(dirname + 'Figures/')

    # Read .tdms file
    tdms_file = TdmsFile.read(filename)
    min_sample, max_sample = count_samples(tdms_file)
    no_sample = max_sample - min_sample + 1

    # Channel Names
    xpix_str = 'cXpix'
    ypix_str = 'cYpix'
    distance_str = 'distance_mm'

    # For Speed Stage and Pause Summaries
    SSdata = {
        'No Speed' : [],
        'Low' : [],
        'Intermediate' : [],
        'High' : []
    }
    Distdata = {'mm' : []}
    PauseSummary = {
        'Sample' : [],
        'Total pause numbers' : [],
        'Total pause time' : []
    }

    # For plotting purposes
    xpix_min, xpix_max = np.inf, 0
    ypix_min, ypix_max = np.inf, 0
    xpix_dict = {}
    ypix_dict = {}
    cols_dict = {}

    for i in range(no_sample):
        num_str = f'{(i+min_sample):03}'

        # Read Channels from "Tracker" group of tdms file
        xpix = tdms_file["Tracker"][xpix_str+num_str].data
        ypix = tdms_file["Tracker"][ypix_str+num_str].data
        distance = tdms_file["Tracker"][distance_str+num_str].data
        frames = tdms_file["Tracker"]["FrameStamp"].data
        time = tdms_file["Tracker"][ "Timestamp"].data

        data = {}
        data['FrameStamp'] = frames
        data['Timestamp'] = time
        data['Xpix'] = xpix
        data['Ypix'] = ypix
        data['distance'] = distance

        # Export .csv files
        df = pd.DataFrame(data)
        csvname = num_str + '.csv'
        df.to_csv(dirname + 'RawData/' + csvname, float_format='%.12f',
                  index=False)

        # Frame Calculation
        if min(xpix) < xpix_min:
            xpix_min = min(xpix)
        if max(xpix) > xpix_max:
            xpix_max = max(xpix)
        if min(ypix) < ypix_min:
            ypix_min = min(ypix)
        if max(ypix) > ypix_max:
            ypix_max = max(ypix)

        xpix_dict.update({num_str : xpix})
        ypix_dict.update({num_str : ypix})

        # Calculating Velocity
        totalrow = len(df)
        timestart = int(time[0])
        timeflow = []
        timeflow.append(time[0])
        i, n, totalsec = 0, 0, 0
        auxlist, velocity = {}, {}

        # Timestamps per 1 second
        while timestart < int(time[totalrow-1]):
            timestart=timestart+FPS
            timeflow.append(timestart)
            i+=1

        for x in range(0,len(timeflow)-1):
            nlist=[]
            while n < totalrow:
                if time[n]<=timeflow[x+1] and time[n]>=timeflow[x]:
                    nlist.append(n)
                    n+=1
                else:
                    x+=1
                    nlist=[]
                    continue
                auxlist[x]=nlist

        for x in auxlist.keys():
            vsum=0
            for m in auxlist[x]:
                if m>0 and distance[m]!=0:
                    if abs(float(xpix[m])-float(xpix[m-1])) > JITTER_THRESHOLD or \
                       abs(float(ypix[m])-float(ypix[m-1])) > JITTER_THRESHOLD:
                        try:
                            dtime=float(time[max(auxlist[x])]-time[max(auxlist[x-1])])
                        except:
                            dtime=float(time[max(auxlist[x])]-time[min(auxlist[x])])
                        vsum+=float(distance[m]/dtime)*FPS
            velocity[x]= vsum

        vps = pd.DataFrame(velocity,index=['mm/s'])
        vps=vps.T
        vps.to_csv(dirname+'Velocity/v'+num_str+'.csv',float_format= '%.4f')

        # Speed Stage Calculation
        s0, s1, s2, s3 = 0, 0, 0, 0
        velocity = vps['mm/s']
        totalsecs = len(velocity)
        cols = []

        # velocity categories: 0 <= Velocity < 8, 8 <= Velocity < 16, 16 <= Velocity
        for i in range(totalsecs):
            if velocity[i] == 0:
                s0 += 1
                cols.append(0)
            if velocity[i] > 0 and velocity[i] <= 8:
                s1 += 1
                cols.append(1)
            if velocity[i] > 8 and velocity[i] <= 16:
                s2 += 1
                cols.append(2)
            if velocity[i] > 16:
                s3 += 1
                cols.append(3)

        # Determining colour for print
        cols_full = []
        for i in range(totalrow):
            cols_full.append(cols[int((time[i]-time[0])/FPS)])
        cols_dict.update({num_str : cols_full})

        SSdata['No Speed'].append(s0)
        SSdata['Low'].append(s1)
        SSdata['Intermediate'].append(s2)
        SSdata['High'].append(s3)

        # Calculate total distances
        distsum = 0
        for i in range(1, totalrow):
            if abs(xpix[i]-xpix[i-1]) > JITTER_THRESHOLD or \
               abs(ypix[i]-ypix[i-1]) > JITTER_THRESHOLD:
                distsum += distance[i]
        Distdata['mm'].append(distsum)

        # Pause Analysis
        Pausedata = {
            'Pause point' : [],
            'Pause duration' : []
        }

        start = None
        length = 0

        for i in range(totalsecs):
            if velocity[i] == 0:
                # Paused
                if start == None:
                    # Pause has just begun
                    start = i
                length += 1 # Increase Pause Length
            else:
                # Not Paused
                if start == None:
                    # Was not paused before
                    continue
                else:
                    # Was paused, just unpaused.
                    if length >= PAUSE_LEN:
                        # Pause was long enough
                        Pausedata['Pause point'].append(start)
                        Pausedata['Pause duration'].append(length)
                    # Reset
                    start = None
                    length = 0
        # Check if ended on pause
        if start != None:
            if length >= PAUSE_LEN:
                Pausedata['Pause point'].append(start)
                Pausedata['Pause duration'].append(length)
            start = None
            length = 0

        # Export Pause to csv
        pause_str = 'pv' + num_str
        pps = pd.DataFrame(Pausedata)
        pps.to_csv(dirname+'Pause/'+pause_str+'.csv', index=False)

        # Pause Summary
        PauseSummary['Sample'].append(pause_str)
        PauseSummary['Total pause numbers'].append(len(Pausedata['Pause point']))
        PauseSummary['Total pause time'].append(sum(Pausedata['Pause duration']))


    # Output File-wide CSVs
    v_category = pd.DataFrame(SSdata)
    v_category.to_csv(dirname+'Velocity/V_category.csv', index=False)

    total = pd.DataFrame(Distdata)
    total.to_csv(dirname+'Velocity/TotalDistance.csv', index=False)

    ps = pd.DataFrame(PauseSummary)
    ps.to_csv(dirname+'Pause/PauseSummary.csv', index=False)

    ##################
    ## Figure Plots ##
    ##################

    print("Plotting Figures.")

    # V Category
    v_cat_plot_data = v_category.divide(v_category.sum(axis=1), axis=0) * 100
    v_cat_plot_data.plot(kind='bar', stacked=True, color=['#7986CB','#4DB6AC','#D4E157','#FF7043'])
    plt.xticks(range(-1, no_sample+1))
    plt.ylabel('%')
    plt.savefig(dirname+'Figures/V_category.png')
    plt.clf()

    # Total Distance
    x_pos = np.arange(1, no_sample+1)
    plt.bar(x_pos, total['mm'])
    plt.xticks(range(1, no_sample+1))
    plt.xlim(left=0)
    plt.ylabel('mm')
    plt.savefig(dirname+'Figures/TotalDistance.png')
    plt.clf()

    # Pause Times
    plt.bar(x_pos, PauseSummary['Total pause time'])
    plt.xticks(range(1, no_sample+1))
    plt.xlim(left=0)
    plt.ylabel('sec')
    plt.savefig(dirname+'Figures/Pausetime.png')
    plt.clf()

    # Pause Number
    plt.bar(x_pos, PauseSummary['Total pause numbers'])
    plt.xticks(range(1, no_sample+1))
    plt.xlim(left=0)
    plt.ylabel('times')
    plt.savefig(dirname+'Figures/Pausenumber.png')
    plt.clf()

    # Path plots
    plt.figure(figsize=(5,5))

    xgap = int((xpix_max - xpix_min)/10)
    ygap = int((ypix_max - ypix_min)/10)
    xpix_min -= xgap
    xpix_max += xgap
    ypix_min -= ygap
    ypix_max += ygap

    cmap = ListedColormap(['#7986CB','#4DB6AC','#D4E157','#FF7043'])
    norm = BoundaryNorm([-0.5, 0.5, 1.5, 2.5, 3.5], cmap.N)

    for i in range(no_sample):
        num_str = f'{(i+min_sample):03}'
        xlist = xpix_dict[num_str]
        ylist = ypix_dict[num_str]
        cols = np.array(cols_dict[num_str][:-1])
        points = np.array([xlist, ylist]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        lc = LineCollection(segments, cmap=cmap, norm=norm)
        lc.set_array(cols)
        lc.set_linewidth(2)
        plt.gca().add_collection(lc)
        plt.gca().invert_yaxis()
        plt.xlim(xpix_min, xpix_max)
        plt.ylim(ypix_min, ypix_max)
        plt.savefig(dirname+'Figures/%s.png' % num_str)
        plt.clf()

        
groupfile()