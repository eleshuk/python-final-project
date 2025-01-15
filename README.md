# Python weather analyser
This project uses a user's IP address to obtain historical weather based on the area that they are in, using the Open-Meteo weather API. 
Once data is loaded, the data is analyzed in various ways, as outlined in the following Python files. 

## project.py
### main()
project.py contains the **main()** function, which initiates the process of getting a user's information. This includes a start date to start the date range to get weather data. The end date is date.today(), so no further input is required from the user. This limits the user inputs requirements, making the code easier and more efficient to run.  

All functions in this project are called from the **main()** function to ensure consistency and organization throughout the project. The main function calls functions in project.py as well as several temperature analysis functions in their respective files. These were put in their own files to reduce the size of project.py, and increase the ease of readability of each file.  

Several functions throughout this project print information, including the municipality, temperature analysis, and precipitation analysis. These results output into the user's terminal, allowing them to view quick statistics about temperature and precipitation througout the duration of their selected date range. 

### Getting Farm Inputs
**get_farm_input()** obtains a user's latitude and longitude using the GEO API, which returns the municipality the user is in.

### Weather data analysis
The file contains a class and methods to get historical weather data from the Open-Meteo API, and gives the user the option to output this weather data as a CSV. The option to export the data as a CSV is presented as an argument in the **export_weather_data()** function, called within the main function. If the argument to export is *True*, then the user will be prompted to select a destination for their CSV file via a GUI which runs with tkinter. If *False* this feature is skipped. 

### Precipitation Data
The precipitation data is handled by two functions, **precipitation_data_avg()** which takes the weather data as an input and adds a Rolling Average field to the dataframe and removes temperature fields, and **precipitation_quick_stats()** which uses the output from **precipitation_data_avg()** to calculate maximum and minimum precipitation as well as the day within the date range with most rain and with least rain.  

The window for the rolling averages is determined by the length of the date range selected by the user. So, if the range is less than or equal to 14 days, then a window of 3 days is applied to the calculation. This same methodology is applied to date ranges between 14 and 30 days, and greater than 30 days, but with different window sizes. Initially when this code was written, the "min_periods" (which just does the rolling average calculation with less datapoints) was not set, which resulted in NA values being produced in the dataset, however setting the min_periods to 1 fixed this issue.

### Functionality and Future Work
This code does not currently output the processed data, only the data summaries. Therefore for future work, the team could build in additional features to export all data in a folder, for example. This would give users more freedom to analyze their data according to their needs. Additional future work would include the ability to output a PDF report with all of the results presented neatly.  

*Potential Issues*  
One user had some trouble with running tkinter in a virtual environment, which prevents the GUI for selecting a destination for the data export from **export_weather_data()** from popping up. If this issue persists for the user, then this argument should be set to *False* and the user has set their intended filepath within the code. 

## test_project.py
Contains all of the test cases for project.py, which were tested with pytest.

### Tests
#### Test user inputs
**default_values()**, **test_valid_input()**, **test_invalid_date_format()**, and **test_boundary_coordinates()** test that the user inputed dates being acquired and handled correctly, and that latitude and longitude obtained from the GEO API is within the defined boundaries.

#### Test that coordinates are being obtained correctly
**test_geocoder_failure()** and **test_boundary_coordinates()** check that geocoder successfully able to get a user's coordinates. 

#### Test that API returns expected data
**test_api_returns_expected_data()** tests that the API is being called properly by mocking the API call and producing a set of mock weather data. The results from the mocked weather API are then compared to the data output by the real API with the same date range and the API checks that the data is aligned.

#### Test data cleaning
**test_data_cleaning()** checks that the data returned by the **get_weather_data()** function is properly formatted and matches the expected layout. 

## precipitaton_analysis.py

## temp_analysis.py
Contains four functions, one that calculates the descriptive statistics, one that calculates the range in daily temperature, one that calculates extreme hot and cold temperatures, and lastly one that is used to call the other three functions.

## test_precipitation.py
Contains one test that is applied to the precipitation analysis code. 




