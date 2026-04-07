-- =========================
-- 0) (Optional) Database
-- =========================
-- NOTE: CREATE DATABASE cannot run inside a transaction block and is usually run separately.
-- CREATE DATABASE test_greenhouse;

-- After creating it, connect:
-- \c test_greenhouse


-- =========================
-- 1) Drop existing objects
-- =========================
-- see if table exists before dropping to avoid errors when running this script multiple times
DROP TABLE IF EXISTS height_view CASCADE;
DROP TABLE IF EXISTS width_view CASCADE;
DROP TABLE IF EXISTS plant_view CASCADE;
DROP TABLE IF EXISTS view CASCADE;
DROP TABLE IF EXISTS tag CASCADE;
DROP TABLE IF EXISTS plant CASCADE;
DROP TABLE IF EXISTS species CASCADE;
DROP TABLE IF EXISTS height_log CASCADE;
DROP TABLE IF EXISTS width_log CASCADE;
DROP TYPE IF EXISTS view_type_enum CASCADE;


-- =========================
-- 2) Types
-- =========================
CREATE TYPE view_type_enum AS ENUM ('height', 'width');


-- =========================
-- 3) Tables
-- =========================
CREATE TABLE species (
  species_id SERIAL PRIMARY KEY,
  scientific_name VARCHAR(128) NOT NULL UNIQUE,
  common_name VARCHAR(128),
  upper_hsv INTEGER[3] NOT NULL,
  lower_hsv INTEGER[3] NOT NULL
);

CREATE TABLE camera (
  camera_id SERIAL PRIMARY KEY,
  ip_address VARCHAR(64) NOT NULL UNIQUE,
  width INT NOT NULL DEFAULT 1024,
  height INT NOT NULL DEFAULT 768,
  focal_length_mm DECIMAL NOT NULL DEFAULT 3.6,
  sensor_height_mm DECIMAL NOT NULL DEFAULT 2.2684,
  sensor_width_mm DECIMAL NOT NULL DEFAULT 3.590
);

CREATE TABLE plant (
  plant_id SERIAL PRIMARY KEY,
  species_id INT NOT NULL REFERENCES species(species_id) ON DELETE RESTRICT
);

CREATE TABLE tag (
  tag_id INT PRIMARY KEY,
  scale_units_m DECIMAL DEFAULT 0.70
);

-- Renamed from "view" to avoid keyword friction
CREATE TABLE view (
  view_id BIGSERIAL PRIMARY KEY,
  tag_id INT REFERENCES tag(tag_id) ON DELETE CASCADE,
  plant_id INT REFERENCES plant(plant_id) ON DELETE CASCADE,
  view_type view_type_enum NOT NULL,
  image_bound_x_high DECIMAL NOT NULL,
  image_bound_x_low DECIMAL NOT NULL,
  image_bound_y_high DECIMAL NOT NULL DEFAULT 1.0,
  image_bound_y_low DECIMAL NOT NULL DEFAULT 0.0,
  minimum_area_pixels INT NOT NULL DEFAULT 200,
  upper_hsv INTEGER[3] default NULL,
  lower_hsv INTEGER[3] default NULL,
  current boolean default true
);

CREATE TABLE height_view (
  view_id BIGINT PRIMARY KEY REFERENCES view(view_id) ON DELETE CASCADE,
  bias_units_m DECIMAL NOT NULL
);

CREATE TABLE width_view (
  view_id BIGINT PRIMARY KEY REFERENCES view(view_id) ON DELETE CASCADE
);

-- make a key from plant_id and measured_at to make it easier to query for the most recent height/width log for a plant

Create table height_log (
  height_log_id BIGSERIAL PRIMARY KEY,
  plant_id INT NOT NULL REFERENCES plant(plant_id) ON DELETE CASCADE,
  height_units_m Decimal not null check (height_units_m >= 0),
  raw_file_path TEXT NOT NULL,
  processed_file_path TEXT NOT NULL,
  measured_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

Create table width_log (
  width_log_id BIGSERIAL PRIMARY KEY,
  plant_id INT NOT NULL REFERENCES plant(plant_id) ON DELETE CASCADE,
  width_units_m Decimal not null check (width_units_m >= 0),
  raw_file_path TEXT NOT NULL,
  processed_file_path TEXT NOT NULL,
  measured_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE FUNCTION update_height_view()
RETURNS trigger AS $$
BEGIN
  INSERT INTO height_view (view_id, bias_units_m)
  VALUES (NEW.view_id, 0.0)
  ON CONFLICT (view_id) DO NOTHING;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trigger_update_height_view
AFTER INSERT ON view
FOR EACH ROW
WHEN (NEW.view_type = 'height')
EXECUTE FUNCTION update_height_view();

CREATE FUNCTION update_width_view()
RETURNS trigger AS $$
BEGIN
  INSERT INTO width_view (view_id)
  VALUES (NEW.view_id)
  ON CONFLICT (view_id) DO NOTHING;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_width_view
AFTER INSERT ON view
FOR EACH ROW
WHEN (NEW.view_type = 'width')
EXECUTE FUNCTION update_width_view();


--- there is an error here

--Create unique index height_log_plant_id_measured_at_idx on height_log (plant_id, measured_at);
--Create unique index width_log_plant_id_measured_at_idx on width_log (plant_id, measured_at);


-- =========================
-- 4) Seed data
-- =========================
INSERT INTO camera (
  ip_address, 
  width, height, 
  focal_length_mm, 
  sensor_height_mm, 
  sensor_width_mm
) VALUES
(
  '192.168.1.11', 
  1024, 
  768, 3.6, 
  2.2684, 
  3.590
);

INSERT INTO species (
  scientific_name,
  common_name,
  upper_hsv,
  lower_hsv
) VALUES
(
  'Lactuca sativa (Truchas)',
  'Red Lettuce (Truchas)',
  ARRAY[179, 255, 255],
  ARRAY[150, 50, 50]
),
(
  'Lactuca sativa (Little Gem)',
  'Mini Romaine Lettuce (Little Gem)',
  ARRAY[80, 255, 255],
  ARRAY[35, 40, 40]
),
(
  'Ocimum basilicum',
  'Basil (Italian Genovese)',
  ARRAY[90, 255, 255],
  ARRAY[30, 60, 60]
),
(
  'Mentha spicata',
  'Mint (Common)',
  ARRAY[90, 255, 255],
  ARRAY[30, 60, 60]
);

INSERT INTO plant (plant_id,species_id) VALUES
-- Truchas (Red Lettuce)
(1,1),
(2,1),

-- Basil
(3,3),
(4,3),

-- Little Gem
(5,2),
(6,2),

-- Mint
(7,4),
(8,4); 

INSERT INTO tag (tag_id, scale_units_m) VALUES
-- 7 cm is equal to .07m
(1, 0.07),
(2, 0.07),
(3, 0.07),
(4, 0.07),
(5, 0.07),
(6, 0.07),
(7, 0.07),
(8, 0.07);

INSERT INTO view (tag_id, plant_id, view_type, image_bound_x_high, image_bound_x_low) VALUES
-- Tag 4 → Truchas (plants 1,2)
(4, 1, 'height', 0.5, 0.0),
(4, 2, 'height', 1.0, 0.5),

-- Tag 3 → Basil (plants 3,4)
(3, 3, 'height', 1.0, 0.5),
(3, 4, 'height', 0.5, 0.0),

-- Tag 2 → Little Gem (plants 5,6)
(2, 5, 'height', 0.5, 0.0),
(2, 6, 'height', 1.0, .50),

-- Tag 1 → Lettuce (plants 1,2)
(1, 1, 'height', 1.0, 0.5),
(1, 2, 'height', 1.0, 0.0);

--change image_bound_low to image_bound_x_low

Insert Into view (tag_id, plant_id, view_type, image_bound_x_high, image_bound_x_low, minimum_area_pixels) VALUES

-- Tag  2 -> Little Gem (plants 5,6)
(2, 5, 'width', 0.5, 0.0, 300),
(2, 6, 'width', 1.0, .50, 300);

