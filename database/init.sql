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
  upper_color_bound_hue INT NOT NULL,
  upper_color_bound_saturation INT NOT NULL,
  upper_color_bound_value INT NOT NULL,
  lower_color_bound_hue INT NOT NULL,
  lower_color_bound_saturation INT NOT NULL,
  lower_color_bound_value INT NOT NULL
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
  image_bound_upper DECIMAL NOT NULL,
  image_bound_lower DECIMAL NOT NULL
);

CREATE TABLE height_view (
  view_id BIGINT PRIMARY KEY REFERENCES view(view_id) ON DELETE CASCADE,
  bias_units_m DECIMAL NOT NULL
);

CREATE TABLE width_view (
  view_id BIGINT PRIMARY KEY REFERENCES view(view_id) ON DELETE CASCADE
);

-- make a key from plant_id and measured_at to make it easier to query for the most recent height/width log for a plant

Create unique index height_log_plant_id_measured_at_idx on height_log (plant_id, measured_at);
Create unique index width_log_plant_id_measured_at_idx on width_log (plant_id, measured_at);

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

-- =========================
-- 4) Seed data
-- =========================
INSERT INTO species (
  scientific_name,
  common_name,
  upper_color_bound_hue,
  upper_color_bound_saturation,
  upper_color_bound_value,
  lower_color_bound_hue,
  lower_color_bound_saturation,
  lower_color_bound_value
) VALUES
(
  'Lactuca sativa (Truchas)',
  'Red Lettuce (Truchas)',
  179, 255, 255,
  150, 50, 50
),
(
  'Lactuca sativa (Little Gem)',
  'Mini Romaine Lettuce (Little Gem)',
  80, 255, 255,
  35, 40, 40
),
(
  'Ocimum basilicum',
  'Basil (Italian Genovese)',
  90, 255, 255,
  30, 60, 60
),

INSERT INTO plant (plant_id,species_id) VALUES
-- Truchas (Red Lettuce)
(1,1),
(2,1),

-- Basil
(3,3),
(4,3),

-- Little Gem
(5,2),
(6,2);

INSERT INTO tag (tag_id, scale_units_m) VALUES
-- 7 cm is equal to .07m
(1, 0.07),
(2, 0.07),
(3, 0.07),
(4, 0.07);

INSERT INTO view (tag_id, plant_id, view_type, image_bound_upper, image_bound_lower) VALUES
-- Tag 4 → Truchas (plants 1,2)
(4, 1, 'height', 0.5, 0.0),
(4, 2, 'height', 1.0, 0.5),

-- Tag 3 → Basil (plants 3,4)
(3, 3, 'height', 1.0, 0.5),
(3, 4, 'height', 0.5, 0.0),

-- Tag 2 → Little Gem (plants 5,6)
(2, 5, 'height', 0.5, 0.0),
(2, 6, 'height', 1.0, .50),

-- Tag 1 → Truchas (plants 1,2)
(1, 1, 'height', 1.0, 0.5),
(1, 2, 'height', 1.0, 0.0);

INSERT INTO height_view (view_id, bias_units_m) VALUES
(1, 0.0),
(2, 0.0),
(3, 0.0),
(4, 0.0),
(5, 0.0),
(6, 0.0),
(7, 0.0),
(8, 0.0);

