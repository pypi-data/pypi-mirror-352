# ```curate-x-posts [by geolocations]```

1. Install
  ```
  pip install curate-x-posts
  ```

2. Create a ```json``` file that contains your login credentials for the X social platform

3. Change below ```88``` and ```99``` to the appropriate values for the latitude and longitude of the location you would like to query and run the command:
 
  ```
  python -m curate-x-posts --lat 88 --lon 99 --radius-km 10
          --query "foodpoison,stomachbug"
          --start-date 2025-04-01 --days 7
          --email my_x@gmail.com --username my_x_username --password my_x_password
          --cookie-path my_cookies.json
  ```
  Above will save the cookie data into a file my_cookies.json

  Once created, you could refer to the cookie file and drop the credential data
  ```
  python -m curate-x-posts -q "vancouver foodpoison" --start-date 2025-04-01 --days 7 -c my_cookies.json
  ```

## ```json``` file

[See example](tests/example_x_login.json)


## Misc tools

- [Query builder](https://developer.x.com/apitools/query?query=SFBWIC1JOlJU)
- [Google Earth]( https://earth.google.com/web/search/Gaza+Strip/@31.41024584,34.38869278,59.29678965a,63493.72275582d,35y,0h,0t,0r/data=CnkaSxJFCiUweDE0ZmQ4NDQxMDRiMjU4YTk6MHhmZGRjYjE0YjE5NGJlOGU3GZEq5RDMWj9AId5VD5iHJ0FAKgpHYXphIFN0cmlwGAIgASImCiQJn0hATpYzNEARnUhATpYzNMAZi2JLAa5CSUAhtZBRkQGXScBCAggBOgMKATBCAggASg0I____________ARAA)
