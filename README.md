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

test_api_returns_expected_data() tests that the API is being called properly by mocking the API call and producing a set of mock weather data. The results from the mocked weather API are then compared to the data output by the real API with the same date range and the API checks that the data is aligned.  

## precipitaton_analysis.py
Contains two methods, one which adds a Rolling Average field to the dataframe and removes temperature fields, and the other which uses this dataframe to calculate maximum and minimum precipitations and the day with most rain and with least rain. 
The window for the rolling averages is determined by the length of the date range selected by the user. So, if the range is less than or equal to 14 days, then a window of 3 days is applied to the calculation. 
Initially when this code was written, the min_periods was not set, which resulted in NA values being produced in the dataset, however setting the min_periods to 1 fixed this issue. This same methodology is applied to date ranges between 14 and 30 days, and greater than 30 days. 

## temp_analysis.py
Contains four functions, one that calculates the descriptive statistics, one that calculates the range in daily temperature, one that calculates extreme hot and cold temperatures, and lastly one that is used to call the other three functions. 

## test_precipitation.py
Contains tests applied to the precipitation analysis code. 

The two tests 

