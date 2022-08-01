# Fadal 4th Axis Post Processor
A utility to post process the gcode output of Fusion360/HSMworks so it works on an older Fadal with 4th axis

## Explanation
Post process code generated with HSMWorks/Fusion360 using the 'Haas with A axis' post so it's usable with a Fadal with A axis.

The fadal post built into HSMworks refuses to generate if you have a 4th axis operation. The "Haas with A-axis" post will not generate the correct coordinates for the A-axis according to what the Fadal is expecting. On a Fadal, the A-axis doesn't rotate the direction that would be the shortest distance from the current coordinate to the desired coordinate as one may expect. Instead the negative sign doesn't mean a negative coordinate, instead it means rotate the chuck clockwise and a positive number after the A means rotate the chuck counter-clockwise. This script will go through every A callout and see if it needs to be positive or negative or not.

## Usage
Generate codes you want in Solidworks with HSMworks installed or Fusion360 and then use the "Haas with A Axis" post to make the input nc codes.

Put the nc codes you want converted in the same folder as this script. Open a terminal, nagivate to the folder and run the following:
```console
python Fadal_post_process.py input.nc
```
This will generate input_fd.nc as the output in the same directory as input.nc.
```console
python Fadal_post_process.py input.nc --directory an_output_folder_name_or_path_to_output_folder
```
Will instead put the output in another folder specified.
```console
python Fadal_post_process.py input.nc --fnames output_name.nc
```
Will let you select a different output name.

Can also process multiple files at once:
```console
python Fadal_post_process.py operation1.nc operation2.nc operation3.nc
```
```console
python Fadal_post_process.py operation1.nc operation2.nc operation3.nc --fnames out1.nc out2.nc out3.nc
```
Note that order of supplied names matters in the above line.
You can also use a wild card operator to select all nc codes in the directory and process them all:
```console
python Fadal_post_process.py *.nc
```
Note that this isn't evaluated by the shell so it only supports that exact pattern. Eg. you _can't_ have it only select files with a prefix that end with nc like `jobname_*.nc`

See built in help with:

```console
python Fadal_post_process.py -h
```
