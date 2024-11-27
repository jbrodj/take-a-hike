# hike-logger

### Setting up for local development

#### Install dependencies
* Run `npm install`
* Run `pip install Flask`

#### Initialize sql database and generate schema 
* Use `npm run initSql` 
---- This will run `/init_sql.py` to create the tables
 
#### Run development server with live reloading 
* Use `npm run dev`
--- This runs `export FLASK_DEBUG=1 && flask run -h localhost -p 5001`
* Find app running at `http://localhost:5001/`

#### To access the sqlite3 database
* Use `npm run db` or `sqlite3 hikes.db`
* Verify schema with `.schema`
* `.quit` to exit sqlite3 prompt