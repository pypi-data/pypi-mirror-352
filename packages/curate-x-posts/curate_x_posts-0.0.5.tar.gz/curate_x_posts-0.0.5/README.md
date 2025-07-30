# ```scrape-x```

1. Install
  ```
  pip install curate-x-posts
  ```

2. Create a ```json``` file that contains your login credentials for the X social platform

3. Change below ```88``` and ```99``` to the appropriate values for the latitude and longitude of the location you would like to query and run the command:
  ```
  python twix.py --lat 88 --lon 99 
  ```    
  Above will scrape with default parameters.
  
  Explore with other attributes, e.g.: 
  ```
  python twix.py --lat 88 --lon 99 --radius-km 10  --query "foodpoison,stomachbug" --start-date 2025-04-01 --days 7
  ```


## ```json``` file

[See example](tests/example_x_login.json)
