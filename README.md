# triangulator
A web app to use measurements of multiple listeners in order to triangulate a (misbehaving) radio station

* consists of a web app (using phonegap or a browser) and a web service (using flask)
* allows users to send measurements including their location and a bearing
* combines these measurements to display a google map with all the current measurements plotted
* requires registration and login
* allows users to start a new search or select a current search
* a search consists of a frequency, a start time and a short description

## API
/api/searches/
* GET: list of searches
* POST(/PUT): create new search
  returns: ID of new search

/api/searches/x
* GET: current map of search
* PUT(/POST): send new measurement
  headers:
    - own location
    - bearing
    - strenght

/api/users/
* POST: register as new user
  headers:
    - email address
    - password
    - location

All calls except api/users require basic auth.
