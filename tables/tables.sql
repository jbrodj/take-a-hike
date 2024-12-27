CREATE TABLE IF NOT EXISTS users (
  id INTEGER NOT NULL,
  username TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS areas (
  id INTEGER NOT NULL,
  area_name TEXT NOT NULL UNIQUE,
  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS trails (
  id INTEGER NOT NULL,
  area_id INTEGER NOT NULL,
  trail_name TEXT NOT NULL UNIQUE,
  PRIMARY KEY (id),
  FOREIGN KEY (area_id) REFERENCES areas(id)
);

CREATE TABLE IF NOT EXISTS hikes (
  id INTEGER NOT NULL,
  hike_date DATE NOT NULL,
  user_id TEXT NOT NULL,
  area_id INTEGER NOT NULL,
  area_name TEXT NOT NULL,
  trailhead TEXT,
  trails_cs TEXT,
  distance_km FLOAT,
  image_url TEXT,
  image_alt TEXT,
  map_link TEXT,
  other_info TEXT,
  PRIMARY KEY (id)
  FOREIGN KEY (area_id) REFERENCES areas(id)
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS follows (
  follower_id INTEGER NOT NULL,
  followee_id INTEGER NOT NULL,
  PRIMARY KEY (follower_id, followee_id)
  FOREIGN KEY (follower_id) REFERENCES users(id)
  FOREIGN KEY (followee_id) REFERENCES users(id)
);