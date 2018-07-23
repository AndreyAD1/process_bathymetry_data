# Bathymetry data processing
This script gets sonar data and water elevation data and returns
`*.csv` file with coordinates and bottom elevation.

Generally, this script gets water depths and water elevations, 
interpolates them spatially and temporally and converts every measured water depth
into bottom elevation.

# Project Goal
We wanted to simplify processing of bathymetry data collected in tidal river
estuary.

Surveying river estuary we deployed several loggers measuring water elevation
along estuary. While loggers were working, we provided bathymetry observations
using sonar. Finally, we got sonar data (points with coordinates, depth and measurement time)
and logger data (temporal variation of water elevation along river estuary). 

We decided to make this program to convert automatically every observed depth into a bottom 
elevation.

# Getting Started
 
## How to Install
Python v3.5 should be already installed. Moreover, you should use `pip` to install 
third-party Python modules which this script uses (dependencies).
The console command to install dependencies:
```bash
pip install -r requirements.txt # alternatively try pip3
```
It is recommended to use virtual environment for better isolation.

## Quick Start

1. Download the file `data_processing.py` from this repository.
2. Put these files in the script`s directory (see file formats in **Input File Formats**):
    1. `fairway_points.csv` - file with coordinates of points located along 
    river fairway; 
    2. `logger_points.csv` - file with loggers` coordinates;
    3. `logger_data.xlsx` - file with time series of water elevation;
3. Create folder `bathymetry/` in the script\`s directory ;
4. Put files containing bathymetry data in the folder `bathymetry/` `*.csv` .

To run script on Linux enter the command:
```bash
$ python3 data_processing.py
```

Windows usage is the same.

# Detailed Description

## Input File Formats

Developed to solve the specific task this script requires very specific and 
even strange formats of input files.

### Fairway Coordinates

This `*.csv` file contains information about points located along
fairway line of an estuary. Each file line contains four values separated 
by semicolons:
- longitude, 
- latitude, 
- useless value, 
- distance from a seashore (metres).

Coordinates are in decimal geographical format: DD.DDD.

Example: `37.9876550297;63.9347729125;1;25`

### Loggers` coordinates

This `*.csv` file contains information about logger locations. 
Each file line contains three values: 
- longitude, 
- latitude,
- logger name.

Coordinates are in decimal geographical format: DD.DDD. 
Logger names coincide with sheet names in `*.xlsx` logger data file.

Example: `38.0392161806;63.9261588182;first_logger`

### Logger Data

This `*.xlsx` file contains information about logger locations.
Data collected by each logger mentioned in loggers\` coordinates `*.csv` file 
is located on separate sheet. Sheet names coincide with names in
the file containing loggers` coordinates.

Each sheet contains water elevation time series:

 Datetime   | H, m 
------------| ----
 01.01.2000 |  5       
 02.01.2000 |  4.95    

### Bathymetry Data

By default `*.csv` files containing bathymetry data are located in 
the folder `/bathymetry_data`.
Each file line contains seven values:
- longitude, 
- latitude,
- depth (metres),
- useless value,
- useless value, 
- useless value, 
- measurement datetime.

Coordinates are in decimal geographical format: DD.DDD.
The first datetime value is a day.

Example: `38.28673531901094;63.82725462860046;2,5;107;0;0:00;08.08.2017 10:50;`

## Script Parameters

This item is in progress.

## Output File Format

This item is in progress.
 

