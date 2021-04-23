# WindroseDash

Given a csv with the velocities and the wind headings of a meteorological station, the app will plot the wind rose.

## Install
To use the app you must have Python 3 installed with the packages presented in *requirements.txt*. Use the following commands to create a virtual environment and install the required packages:

```
cd WindroseDash
virtualenv venv
source venv/bin/activate

pip install dash

pip install pandas
```

The app is also available in Heroku ([App link](https://windrose-dash.herokuapp.com/))

## Use

To use the application one should have a csv file similar to the *wind_data_example.csv* given as an example. The first line must be the header line and at least to columns must be given: one for the wind velocity and the other for the wind direction. On the app there are numeric inputs to point to each column.

The wind heading must be a value between 0º and 360º. The convention adopted is:

* North: 0.0º
* East: 90.0º
* South: 180º
* West: 270º

The *velocity breaks* entry refers to the velocity interval, must be started with a value grater than zero and must be semicolon separated. For example, if the string 1;3;5 is given than the intervals computed are 0 <= V < 1.0, 1.0 <= V < 3.0, 3.0 <= V < 5.0 and V >= 5.0. 

The wind velocity module can be given in four distinct units: m/s, km/h, mph and knots. Conversion between than is provided in the *From*, *To* entries.

Finally, the *Frequency considering only valid measurements* entry indicates if one should use all data for frequency calculations or if only the non NA data should be applied. Nevertheless the NA percentual is shown.

## Considerations

This app is being developed. In the future other functionalities might be added. Any suggestions are appreciated. Feel free to help on the development!

