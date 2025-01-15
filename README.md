# Python weather analyser
This project uses the users ip address location to determine the weather of the area that that IP address is in. 

## project.py
project.py contains the main function, a function to get the user's information, including a start date to start the date range to get weather data. The end date is date.today() and so no input is sought from the user. 
It also contains a class and methods to get weather data from the open meteo API, and the option to output this weather data as a CSV. 
Finally it contains a class to get the location data from GEO API, which returns the municipality the user is in

The main function calls functions in project.py as well as several precipitation and temperature analysis functions in their respective files. These were put in their own files to reduce the size of project.py, and increase the ease of readability of each file

Several methods print information, including the municipality, temperature analysis, and precipitation analysis

## test_project.py
Contains all of the test cases for project.py, which were tested with pytest

## precipitaton_analysis.py
Contains two methods, one which adds a Rolling Average field to the dataframe and removes temperature fields, and the other which uses this dataframe to calculate maximum and minimum precipitations and the day with most rain, and with least rain

## temperature_analysis.py
