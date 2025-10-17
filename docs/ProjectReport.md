# Bayesian-Updated File Format

## Senior Design Project Report - 2025/2026
## Michael Brown, Joe Crim, Jacob Rice
## Advised by Dr. Peter Jamieson


# Spatio-Temporal File Format with Python Combining and Interpolating Library
Senior Design Project Report - 2025/2026
Michael Brown, Joe Crim, Jacob Rice
Advised by Dr. Peter Jamieson

## Overview
The Spatio-Temporal File Format is a JSON formatted file structure as outlined in template.json. Different Spatio-Temporal Files (STF moving forward) are used by the Python library to combine into one data set using a variety of methods. Supported methods include: Weighted Arithmetic Mean
After the data sets are combined, points without data can be interpolated in the following supported manners:
Linear Interpolation
## Supported Combinational Methods
### Weighted Arithmetic Mean
#### Implementation
Two STF are considered. At each time shared by the files, the following formula is applied:
	
Where P1 is the total number of points considered to create the data point for STF 1, P2 is the total number of points considered to create the data point for STF 2, C1 is the confidence of the data point from STF 1, C2 is the confidence of the data point from STF 2, D1 is the x or y coordinate of the data point from STF 1, and D2 is the x or y coordinate of the data point from STF 2. This formula is run for each coordinate axis to build a new point.
#### Motivation
	A weighted arithmetic mean keeps a running average of input data points, allowing new data points to easily be weighted and blended together with previous readings. Data points are discarded after being considered, allowing for efficient use of storage. We weight each data point by the confidence and the ratio of points used to the total points between the two data sets. To calculate the new data point, we multiply the weighted result by the total number of points between the two data sets and divide by the average of the confidence. The formula in implementation above is a simplification of this process.

#### Performance

### Weighted Geometric Mean
#### Implementation
Two STF are considered. At each time shared by the files, the following formula is applied:
	
Where P1 is the total number of points considered to create the data point for STF 1, P2 is the total number of points considered to create the data point for STF 2, C1 is the confidence of the data point from STF 1, C2 is the confidence of the data point from STF 2, D1 is the x or y coordinate of the data point from STF 1, and D2 is the x or y coordinate of the data point from STF 2. This formula is run for each coordinate axis to build a new point.
#### Motivation
	A weighted geometric mean keeps a running average of input data points, allowing new data points to easily be weighted and blended together with previous readings. Data points are discarded after being considered, allowing for efficient use of storage. We weight each data point by the confidence and the ratio of points used to the total points between the two data sets. To calculate the new data point, we multiply the weighted result by the total number of points between the two data sets and divide by the average of the confidence. The formula in implementation above is a simplification of this process.

#### Performance
	

## Feature Set

### Feature: apple

### Feature: banana

## Weekly Work Log

### Week 3
Worked on setting up JSON data structure for storing spatio-temporal data as well as confidence levels. Designed structure to be easily updatable and capable of storing metadata for each player, team, and game in the case of game analysis. 

### Week 4
Worked on implementing weighted arithmetic mean, taking weighted average of both location data as well as confidence. We did so by keeping track of total number datapoints logged and using that running total to weigh previous points against new data points every time a new data point is added to the file.

### Week 5
Looking into other methods of calculating running average location and confidence, specifically looking into keeping all data points and confidences for later use, rather than just keeping one weighted average and dumping the individual points as they are added. Worked on breaking the method into two options: Compressed and Uncompressed. Compression makes a new weighted total and confidence level, discarding individual points/confidences, and allows weighted arithmetic average to be taken. Uncompressed keeps all points for calculating things such as weighted geometric average and median, skipping the compression steps that are taken in the compressed option. 


### Week 6
Clarified that our “compressed” format is calculated at the end before data is presented to the user. All calculations are completed in the “uncompressed” format, preserving all of the data for performing the calculations. 

### Week 7
Figuring out how to implement the overall “error” present between all points. We developed a “flawed” data set by purposefully changing some correct values in a perfect data set. We then compared the flawed and perfect datasets to test the file format’s capability to detect errors in the flawed dataset. Decided to divide cumulative differences by the number of points to get the average difference between each point pair of points.  We calculate average error and divide by two, as error is in both the X and Y variables. 

Decided to change how we calculate confidence, instead relying on a process of treating points as vectors and calculating the angle between them to determine similarity. 
Process: If two points are similar (angle is greater than or equal to 0.5), we increase the confidence by 1 + (Similarity in the average). If the points are non-similar, we multiply the average by the similarity. This results in more fluctuation in confidence and will prevent our model from stagnating in a low confidence state.

    Somehow include term that factors in “momentum” into our point calculations (Gradient Descent with Momentum)
    Next week: 
    For the increase in confidence, take the higher confidence and add to it the remaining difference to 1, times the other confidence times the similarity
    Add some form of number of points weighting to the scaling of the confidences

### Week 8
