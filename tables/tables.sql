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
  area_id INTEGER NOT NULL,
  trailhead TEXT,
  trails_cs TEXT,
  distance FLOAT,
  map_link TEXT,
  other_info TEXT,
  PRIMARY KEY (id)
  FOREIGN KEY (area_id) REFERENCES areas(id)
);