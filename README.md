# 🥾 Take a hike 🥾

* [Demo video](https://youtu.be/FIYaefWO7AU)
* [Public Github repo](https://github.com/jbrodj/take-a-hike)
* [My website](http://brodieday.com/)

## Setting up for local development 🧑‍💻

### Cloudinary ☁️
* Note that this app uses a `Cloudinary` integration for content management. This requires an API key and secret. To test the application, you can create a free account and drop your secret in the following format into a `.env` file in the project root directory, and it should be good to go. 
`CLOUDINARY_URL=cloudinary://<API_KEY>:<SECRET>`

[Cloudinary documentation](https://cloudinary.com/documentation/python_quickstart)

### Start virtual environment 🐚
* Use `pipenv shell`

### Install dependencies and initialize sql database 📋
* Use `pipenv install`
* Use `pipenv run init_sql`
---- This will initialize sql database and create table schema.

### Run Flask development server 🏃‍➡️
* Use `pipenv run start` 
---- Or run `export FLASK_DEBUG=1 && flask run -h localhost -p 5001` for live reloading
* Find app running at `http://localhost:5001/`

### If you need to access the sqlite3 database 📊
* Use `pipenv run db` or `sqlite3 hikes.db`
* Verify schema with `.schema`
* `.quit` to exit sqlite3 prompt

### To run unit tests on Python files 🧪
* Use `pytest -s <filename>` (ie. `pytest -s utils_test.py`)


## App description & design notes 📝
Take a Hike 🥾 is a social media application for logging and sharing information about hikes!

### App.py
`App.py` houses global configurations and routes for the application. This file is responsible for app configuration, instantiating the Flask Session, loading secrets from the `.env` file, and configuring `cloudinary` (a content management service used to process, store, and serve user-provided image files). 

`App.py` houses several routes that serve the app's functionality:

`'/'` Is a simple splash page with a logo and main navigation.This is the default route for an unauthenticated user. The splash template has some duplicated markup that I'd like to eliminate, but the styling is slightly different from the main layout header, so that hasn't been tackled yet.

`/signup` and `/login` serve similar forms, take user input for username and password, and when submitted make use of utility functions to insert a new user to the `users` table in the database, or authenticate a user by checking for a mathing username and password hash in that table. This uses `wekzeug` to generate hashed passwords. Evidently the `scrypt` method for hashing (which is the default for this package) does not work natiely on MacOS, so the app uses `pbdkf2` for local development. This is a less secure hashing method, and shouldn't be used for production. 
######<mark>TODOs</mark>: 
- Implement rate limiter function for login route to prevent brute forcing of passwords. 
- Update password requirements for security (ie. min 8 chars with upper & lowercase alhpanum + punct). 
- Consider on login - redirect to the referring page would be better UX, rather than redirecting to their user page (ie. if a user is being prompted to log in because they take an action that is wrapped in login-required, they could be redirected to that route to more easily complete that action).

`/logout` Clears the session and redirects to the splash page.

`/users` Serves a simple search form, and when submitted, serves a list of users that 'match' the query string. Initially, I thought to use SQL to loop through the query string to find `LIKE` usernames in the `users` table, but thought that may have poor performance. So instead, we fetch the whole list of users and use python to run a very simple search algorithm on each username:
1. Count for each char in the query that matches a char in the username (minimum of three to be considered a match).
2. Count the proportion of character matches by dividing the count by the length of the username (minimum 50% to be considered a match).
3. Generating the match factor by multiplying these two numbers together. `user-search-results` template is conditionally rendered if there are any results with those results sorted by match factor and displaying an 'exact match' element for an exactly matched username. This view also fetches the image from each hiker's most recent hike (if it exists) and displays that in their user card. This image is scaled down to 100px max width using a`cloudinary` query in the request url.
This isn't a very robust search engine because it will serve some 'false positives' that just happen to match a few letters. If this was a production application with thousands of users, this would need to be fixed. It was fun to think this logic through though, so I've left it as is for now. 

`/users/<username>/feed` and `users/<username>` serve the `feed` template, which conditionally renders a list of hikes for the given user, or a 'feed' of hikes from all hikers that user is 'following.' This data is accessed from the `hikes` table in the sqlite3 database. Images served here are scaled to a max-width of 900px using a `cloudinary` query in the request url. This template also houses the context message functionality in the `context-msg` sub-template. From an html structure perspective, it made more sense to implement this functionality here rather than in the layout template (though, I think design-wise, it would make more sense to put it in the layout so it could be shared by any sub-template). This is a conditionally rendered sub-template that displays context to users after performing certain operations like logging in, creating, editing or deleting hikes. 
######<mark>TODOs</mark>: 
- Add pagination or scrolly loading to the feed template.

`/follow` / `/unfollow` routes are accessed via a UI button when an authenticated user visits another hiker's page. This button conditionally displays the string 'follow' or 'unfollow' depending on whether the current user follows that hiker already. These routes are very similar, and could probably be combined.

`/new_hike` and `edit_hike` and both serve the `hike-form` template (the edit hike route autopopulates the values from that hike's instance in the `hikes` table, while `new_hike` serves a blank form). In the case of `edit_hike`, an edit and delete button are each conditionally rendered on a hike that a user has authorization to edit (ie. their user id matches that hike's user id property). In either case, when this form is submitted, this data is inserted into the `hikes` table in the database, and the image file provided is uploaded to `cloudinary` (and using an optional parameter to generate the 900px version of the image to be used in the 'feed'). When editing an existing hike, the user has the option to cancel, which redirects back to the `users/<username>` route. If they submit the form, those values are used to update that hike in the `hikes` table, and (if provided) a new image will be sent to `cloudinary`. 
######<mark>TODOs</mark>: 
- Better UX design would include a confirmation modal when user deletes a hike. 
- Want to consider deleting cloudinary assets when a hike is deleted for better content management design.

Some routes (`new_hike`, `edit_hike`, `follow`, `unfollow`, `users/<username>/feed`) are wrapped in a decorator function `@login_required` that redirects to the `/login` route if a valid session doesn't exist.

### Utils.py
`Utils.py` houses reusable python functions used in the server. Any logic that was duplicated, or was complex enough to make a route overly messy was factored out into a utility function instead. They're organized into categories by general use-case and for the most part, they do what they say they do. 

### Ready.js
`Ready.js` is run when the main layout template is rendered. These JavaScript functions serve three purposes:
1. `ready()`: Prevents layout shift on render by using CSS to make the body visible only after the markup has been loaded. 
2. `closeContextMsg()`: Provides interactive UI functionality on the context alert message element (using JS to select the element and CSS to hide it when the close button is pressed). 
3. `autofocus()`: To prevent form inputs not autofocusing, the autofocus function runs as a callback inside a setTimeout, selecting the first form label element on the page (if present) and using the .focus JS method to set focus on that element. 
######<mark>TODOs</mark>: 
- Consider adding a timeout to the context alert to have it close automatically after a certain amount of time. 

### Constants.py
As one might expect, `constants.py` contains constants. The sqlite3 database location, and `cloudinary` request urls are stored here. These values should never change, and its cleaner to keep them here instead of in the app file. 

### Content.py
This file contains data used in serving UI content. Primarily, this contains a list of dictionaries containing the HTML attributes for the form elements in the `new_hike/edit_hike` form. This saves on markup repetition in the template file because we can use a loop to generate the inputs and use the data here to provide attr values. This file also contains a dictionary of strings used to serve error messages by the `handle_error` function. This is to save space in the `render_template` call, using the dictionary key instead of the full error string.

### Tables.sql 
This file contains the SQL commands for creating the database's table schema. The original idea for the app was more hike logger, less social media sharing, so some of the tables (`trails`, `areas`) are not actually used to serve any UI yet. I left the in because I might get around to that in the future. In that case, the string values for `trails` and `area_name` in `hikes` table could use the corresponding `id` values in the `trails` and `areas` tables to save on string space. For now though, it was simpler just to use one table to serve the UI, since I wasn't using those tables for anything else. 
######<mark>TODOs</mark>:
- Either make use of the trails and areas tables, or remove them.

### Init_sql.py
This python file is used when setting up local development to create a connection to a new database file, run `tables.sql` to create the table schema, and print status message including a list of tables that have been created. 

### Pipfile / pipfile.lock
This project uses `pipenv` to handle dependencies. 

### .env 
This file houses environment variables.

#### .gitignore
Contains folders, filenames and filetypes to be ignored by git.

#### Pylint.yml
Configuration file for a github workflow action to run `pylint` on push.

### Additional features & design ideas for the future

#### Support multiple images per post
This could include a carousel (ie. kivy) in the feed view. 

#### Maps plugin
Originally the plan for each hike's map link would be a visual element showing the map location, but I haven't looked into a plugin for this yet. 

#### User metrics feature
Data visualization for each user. Could be its own route with information such as distance traveled, number of hikes/locations/etc. Or could be a sub-template with a small amount of info on the users page.

