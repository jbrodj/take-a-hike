CREATE TABLE areas (
  id INTEGER NOT NULL,
  area_name TEXT NOT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE trails (
  id INTEGER NOT NULL,
  area_id INTEGER NOT NULL,
  trail_name TEXT NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (area_id) REFERENCES areas(id)
);

CREATE TABLE hikes (
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