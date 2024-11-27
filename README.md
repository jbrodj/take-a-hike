# hike-logger

### Setting up for local development

#### Install dependencies and initialize sql database
* Run `npm run init`
---- This will install npm packages, install Flask with pip, and initialize sql database and create table schema.
 
#### Run Flask development server with live reloading 
* Use `npm run dev`
* Find app running at `http://localhost:5001/`

#### If you need to access the sqlite3 database
* Use `npm run db` or `sqlite3 hikes.db`
* Verify schema with `.schema`
* `.quit` to exit sqlite3 prompt