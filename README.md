# simple_gps_simulator

## *Simple GPS Simulator based on vector spatial data*

Vehicle motion simulator based on LineString and MultiLineString data. Using the `random` library, it selects a starting position (coordinates), initial velocity, and direction. Then, the coordinates move along the line ("straight simulation"), taking into account the velocity and elapsed time (using the `datetime` library).  
If the vehicle's position reaches the end of the line, it selects the next line (from neighboring lines for the current "road"), choosing the closest line.  
   
The data (with .geojson extension) must be in a coordinate system with meter units (not degrees!)


### **Requirements**
```
geopy==2.3.0
numpy==1.24.3
pyproj==3.5.0
shapely==2.0.1
```

### **Usage**
To use your own layer, generate GeoJSON in QGIS and save it in the 'roads_data' folder.
```
python3 simulator.py generate 5 'example_poznan_2180.geojson' 'output' --results 10 --min_speed 1 --max_speed 50
```
The results will be saved in the 'results' folder.

### **License**
MIT