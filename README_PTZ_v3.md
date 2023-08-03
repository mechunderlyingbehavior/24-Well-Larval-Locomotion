README 
Done by Saoirse Therese Lightbourne @02/06/2022
Python v3.9.7, npTDMS v1.4.0, Pandas v1.3.4, Matplotlib v3.4.3, NumPy v1.20.3

This python package adapted by Khwa Zhong Xuan in February 2021, combines the following python files, 
originally created by  Li Hankun in December 2017, into one script:

1. TdmsExtractorToCSV.py:
Extracts useful information from .tdms file and puts in new .csv files.

2. VelocityPerSec.py:
Calculates the velocity at each second during recording. 

3. SpeedStage.py:
Analyses the velocity at each second and divides the velocity into three different stages, 
and calculates the total distance each fish travelled during recording. 


4. PauseAnalysis.py:
Analyses the pause events (3 sec without movement) in each fish.


5. FigureCreator.py:
Creates the figures for:
	1. velocity category:
		Figures for the percentages of seconds in different velocity categories of each fish.
		Figure will be stored in "(filename)/Figures/" and named V_category.png
		
	2. total distance of the fish:
		Figures for the total distance each fish travelled.
		Figure will be stored in "(filename)/Figures/" and named TotalDistance.png
		
	3. pause numbers and total pause time of the fish:
		Figures for the pause numbers and pause duration of each fish
		Figures will be stored in "(filename)/Figures/" and named Pausenumber.png and Pausetime.png
		
	4. the movement of each fish:
		Figures illustrating fish movement during recording
		Figures will be stored in "(filename)/Figures/" and named after each fish number as "001.png"
		

  
Running instructions: 

Before running the `ExtractAndPlotTdms.py` make sure the following python modules have been installed:

- npTDMS 1.4.0
- Pandas 1.3.4
- Matplotlib 3.4.3
- NumPy 1.20.3

Modules can be installed using the pip command : pip install module_name. To install specific module versions use '==' version.
E.g.
```
pip install npTDMS == 1.4.0

```

'ExtractAndPlotTdms.py' is made to run from the command line, from a directory
containing the .tdms files to be extracted and plotted. To run the script first move working directory to location 
where the script and tdms files are located. To move working directory use the cd command followed by the full path name of the folder.
E.g.
```
cd C:\Users\ASMLabUser1\Desktop\PTZ_Locomotion_Analysis_Py3

```

There are 2 main options when running the script. If you provide the `.tdms` file that you want to
extract, it will run the script only for that file. E.g.

```
python ExtractAndPlotTdms.py tdmsfile.tdms
```

If no file is given, the program instead searches the current working directory
for all `.tdms` files in the directory, and runs the code for all the files.
E.g.

```
python ExtractAndPlotTdms.py
```

The python program also allows for changing universal values, mainly the jitter
threshold, pause length, and fps. This should be changed directly in the
`ExtractAndPlotTdms.py` file before running on command line.
