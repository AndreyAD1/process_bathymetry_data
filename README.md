# Bathymetry data processing
This script gets sonar data and water elevation data and returns
`*.csv` file with bottom elevation and coordinates.

Generally, this script gets water depths and water elevations, 
interpolates them spatially and temporally and converts every measured water depth
into bottom elevation.

# Table of Contents

1. [Project Goal](#project_goal)
2. [Getting Started](#getting_started)
    1. [How to Install](#how_to_install)
    2. [Quick Start](#quick_start)
3. [Detailed Description](#detailed_description)
    1. [Input File Formats](#input_file_formats)
        1. [Fairway Coordinates](#fairway_coordinates)
        2. [Logger Coordinates](#logger_coordinates)
        3. [Logger Data](#logger_data)
        4. [Bathymetry Data](#bathymetry_data)
    2. [Script Parameters](#script_parameters)
    3. [Output File Format](#output_file_format)

# Project Goal <a name='project_goal'></a>
We want to simplify processing of bathymetry data collected in tidal river
estuary.

Surveying river estuary we deployed several loggers measuring water elevation
along estuary. While loggers were working, we provided bathymetry observations
using sonar. Finally, we got sonar data (points with coordinates, depth and measurement time)
and logger data (temporal variation of water elevation along river estuary). 

We decided to make this program to convert automatically every observed depth into a bottom 
elevation.

# Getting Started <a name='getting_started'></a>
 
## How to Install <a name='how_to_install'></a>
Python v3.5 should be already installed. Moreover, you should use `pip` to install 
third-party Python modules (dependencies) which this script uses.
The console command to install dependencies:
```bash
pip install -r requirements.txt # alternatively try pip3
```
It is recommended to use virtual environment for better isolation.

## Quick Start <a name='quick_start'></a>

1. Download the file `data_processing.py` from this repository.
2. Put these files in the script`s directory (see file formats 
in [Input File Formats](##input_file_formats)):
    1. `fairway_points.csv` - file with coordinates of points located along 
    river fairway; 
    2. `logger_points.csv` - file with loggers` coordinates;
    3. `logger_data.xlsx` - file with time series of water elevation;
3. Create a folder `bathymetry_data/` in the script`s directory ;
4. Put `*.csv` files containing bathymetry data in the folder `bathymetry_data/`.

To run script on Linux enter the command:
```bash
$ python3 data_processing.py
```

Windows usage is the same.

Having completed calculations the script creates the file `output.csv`
containing bottom elevations and its coordinates.

User can specify paths and names of all input and output files (see [Script Parameters](#script_parameters)).

# Detailed Description <a name='detailed_description'></a>

## Input File Formats <a name='input_file_formats'></a>

Developed to solve the specific task this script requires input files with quite specific and 
even strange formats.

### Fairway Coordinates <a name='fairway_coordinates'></a>

This `*.csv` file contains information about points located along
fairway line of an estuary. Each file line contains four values separated 
by semicolons:
- longitude, 
- latitude, 
- ignored value, 
- distance from a seashore (metres).

Coordinates are in decimal geographical format: DD.DDD.

Example row: `37.9876550297;63.9347729125;1;25`. 
See [example file](https://github.com/AndreyAD1/process_bathymetry_data/blob/master/fairway_points.csv).

### Logger Coordinates <a name='logger_coordinates'></a>

This `*.csv` file contains information about logger locations. 
Each file line contains three values separated by semicolons: 
- longitude, 
- latitude,
- logger name.

Coordinates are in decimal geographical format: DD.DDD. 
Logger names coincide with sheet names in `*.xlsx` logger data file.

Example row: `38.0392161806;63.9261588182;first_logger`.
See [example file](https://github.com/AndreyAD1/process_bathymetry_data/blob/master/logger_points.csv).

### Logger Data <a name='logger_data'></a>

This `*.xlsx` file contains information about logger locations.
Data collected by each logger mentioned in loggers\` coordinates `*.csv` file 
is located on separate sheet. Sheet names should coincide with names mentioned in
the file containing loggers` coordinates.

Each sheet contains column headers and water elevation time series:

 Datetime   | H, m 
------------| ----
 01.01.2000 |  5       
 02.01.2000 |  4.95    
 
 See [example file](https://github.com/AndreyAD1/process_bathymetry_data/blob/master/logger_data.xlsx).

### Bathymetry Data <a name='bathymetry_data'></a>

By default `*.csv` files containing bathymetry data are located in 
the folder `/bathymetry_data`.
Each file line contains seven values separated by semicolons:
- longitude, 
- latitude,
- depth (metres),
- ignored value,
- ignored value, 
- ignored value, 
- measurement datetime.

Coordinates are in decimal geographical format: DD.DDD.
The first value in a datetime is a day.

Example row: `38.28673531901094;63.82725462860046;2,5;107;0;0:00;15.08.2017 10:50`.
See [example file](https://github.com/AndreyAD1/process_bathymetry_data/blob/master/bathymetry_data/Sonar0000_out_t.csv)

## Script Parameters <a name='script_parameters'></a>

The script has five optional parameters: 
1. `-b`, `--bathymetry_directory` - path of directory containing `*.csv` 
files with sonar data. By default: `bathymetry_data/`;
2. `-f`, `--fairway_points_filepath` - path of `*.csv` file containing coordinates 
of points located along river fairway. By default: `fairway_points.csv`;
3. `-l`, `--logger_points_filepath` - path of `*.csv` file containing 
loggers\` coordinates. By default: `logger_points.csv`;
4. `-x`, `--logger_data_filepath` - path of `*.xlsx` file containing 
time series of water elevation. By default: `logger_data.xlsx`;
5. `-o`, `--output_filepath` - path of output `*.csv` file.
By default: `output.csv`.

## Output File Format <a name='output_file_format'></a>

The script outputs result in a `*.csv` file.
Each file line contains eight values separated by semicolons:
- longitude (UTM),
- latitude (UTM),
- bottom elevation,
- measurement time,
- water elevation,
- depth,
- distance from a seashore,
- path of bathymetry file containing this measurement point.

Example row: `451190.7;7090276.6;-4.6;07.08.17 21:58;1.09;5.7;625.0;bathymetry_data/Sonar01.csv`.


 

