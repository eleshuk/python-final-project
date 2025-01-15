# Python weather analyser
This project uses a user's IP address to obtain historical weather based on the area that they are in, using the Open-Meteo weather API. 
Once data is loaded, the data is analyzed in various ways, as outlined in the following Python files. 

## project.py
project.py contains the main function, a function to get the user's information, including a start date to start the date range to get weather data. The end date is date.today() and so no input is required from the user. It also contains a class to get the location data from GEO API, which returns the municipality the user is in. 
The file contains a class and methods to get historical weather data from the Open-Meteo API, and gives the user the option to output this weather data as a CSV. The option to export the data as a CSV is presented as an argument in the export_weather_data() function, located within the main function. If the argument to export is True, then the user will be prompted to select a destination for their CSV file via a GUI which runs with tkinter. 
*Issues*
One user had some trouble with running tkinter in a virtual environment, so if this issue persists for the user, then this argument should be set to False and the user has set their intended filepath within the code. 

The main function calls functions in project.py as well as several precipitation and temperature analysis functions in their respective files. These were put in their own files to reduce the size of project.py, and increase the ease of readability of each file. 

Several methods print information, including the municipality, temperature analysis, and precipitation analysis. These results output into the user's terminal, allowing them to view quick statistics about temperature and precipitation througout the duration of their selected date range. This code does not currently output the processed data, only the data summaries. Therefore for future work, the team could build in additional features to export all data in a folder, for example. This would give users more freedom to analyze their data according to their needs. 

## test_project.py
Contains all of the test cases for project.py, which were tested with pytest.

## precipitaton_analysis.py
Contains two methods, one which adds a Rolling Average field to the dataframe and removes temperature fields, and the other which uses this dataframe to calculate maximum and minimum precipitations and the day with most rain and with least rain. 


## temperature_analysis.py

