-- AureaTech migration for PBKDF2 seed passwords, extra demo users,
-- plate normalization, and app-owned rule actuator actions.
-- Run this on an existing database. Fresh installs should use docs/db.sql.

START TRANSACTION;

-- Store and compare plates without spaces.
UPDATE allowed_plate
SET plate = UPPER(REPLACE(plate, ' ', ''));

UPDATE camera_event
SET detected_plate = UPPER(REPLACE(detected_plate, ' ', ''));

-- Ensure each community can expose a garage door actuator. Plate recognition opens this actuator.
INSERT INTO actuator (community_id, actuator_type, location, current_state, created_at, last_changed_at)
SELECT 1, 'SERVOMOTOR', 'Garage Door 1A', 'CLOSED', NOW(), NOW()
WHERE NOT EXISTS (
  SELECT 1 FROM actuator
  WHERE community_id = 1 AND actuator_type = 'SERVOMOTOR'
);

-- Existing seeded users: move from legacy SHA-256 to app PBKDF2 hashes.
UPDATE user
SET password_hash = CASE email
  WHEN 'admin@test.com' THEN 'pbkdf2_sha256$260000$e95ebd623fa6a2dfade14ac2559bfc38$bf4202343c08be1bfcbd0bfdcd9c1f7c61a6d07bba236e1b5736a72e1533c4cc'
  WHEN 'tech1@test.com' THEN 'pbkdf2_sha256$260000$944e6581c97cfd9e1e5dded537130597$d565ede687d7105d80b6e657379400d4cbdc0af735ed560eb8b287a18cf56c21'
  WHEN 'tech2@test.com' THEN 'pbkdf2_sha256$260000$faf0e19f7ea10fb712214de276369da6$73943db8a2c80e91f3c89c7f511d6dfd94845921a3cdee862085dec8cb237abd'
  WHEN 'aurea@tech.com' THEN 'pbkdf2_sha256$260000$5c9e2bc05ee0028ce8472c37b75ea98b$1addff5dc1fb569b9e6acd7636e59c025113a273142e5149debc2ec1cdb1f805'
  WHEN 'juan@juan.com' THEN 'pbkdf2_sha256$260000$f4817f8cff4e6aabf9e1e7c7fd9930f7$f75dd958ccd186ac6dfb187c19540e8aaa976b4343c5c1dbebcae1ea8dbb6b6c'
  WHEN 'pepe@perez.com' THEN 'pbkdf2_sha256$260000$2457c5fd8f6dd196cf61c016a5c40d8f$f44b8e7576fb3ff266fc095813f793f7265924b2906cbbd5b38e8bd3ce35c08b'
  ELSE password_hash
END
WHERE email IN (
  'admin@test.com',
  'tech1@test.com',
  'tech2@test.com',
  'aurea@tech.com',
  'juan@juan.com',
  'pepe@perez.com'
);

-- Extra demo users: totals become 5 admins, 5 technicians, 9 neighbors.
INSERT IGNORE INTO user (
  community_id,
  full_name,
  email,
  password_hash,
  role,
  date_of_birth,
  picture_path,
  picture_url
) VALUES
(NULL, 'Admin Norte', 'admin2@test.com',
 'pbkdf2_sha256$260000$315a9e0f8e76c96971eaf9168b0e4da1$03c2b83db25a807343b05165151aed5038103c41738174251fd66b40cba2f0fc',
 'ADMIN', NULL, '', NULL),
(NULL, 'Admin Sur', 'admin3@test.com',
 'pbkdf2_sha256$260000$055cdc8f095c478f746eb33d17f04950$76582d829d4f608b8ea5d035db0a903fceb9dc3948f632308c67a1b1d299521a',
 'ADMIN', NULL, '', NULL),
(NULL, 'Admin Operaciones', 'admin4@test.com',
 'pbkdf2_sha256$260000$2ff6f4abb2022c1c9f3ecc518fae0f07$4069c8d43bb33391d7a844fb0133b5cec7269718c7ee21fb2ec74cf44b749db4',
 'ADMIN', NULL, '', NULL),
(NULL, 'Admin Seguridad', 'admin5@test.com',
 'pbkdf2_sha256$260000$a71deca0953817c607c5a0e62a640aef$7c811cff3feb2a2725400bb971711aaf0744ec2b8b83ce475ea9e428512df6a0',
 'ADMIN', NULL, '', NULL),
(1, 'Tech Support Comunidad 1B', 'tech3@test.com',
 'pbkdf2_sha256$260000$6d77d7276abff901aa8ebe7e997c0543$d4f8aa3a4b5accc534412fde6536428684178fa796bce85c476bc245a12740b7',
 'TECHNICIAN', NULL, '', NULL),
(2, 'Tech Support Comunidad 2B', 'tech4@test.com',
 'pbkdf2_sha256$260000$f571268d1efb57f6ca577ab5a0c1d76a$3f187aa7d768bf46a8e85108606bb5b5e1d10c3a2294d0fa68b63d9c8d1269f9',
 'TECHNICIAN', NULL, '', NULL),
(1, 'Tech Support Guardia', 'tech5@test.com',
 'pbkdf2_sha256$260000$5e610de8f5f23deacff688432acdf7b7$556fc16fc763d6cb178b862b155d00e7041434a3d79d0cee432bfa49f5cecee8',
 'TECHNICIAN', NULL, '', NULL),
(1, 'Lucia Martin', 'lucia@test.com',
 'pbkdf2_sha256$260000$be39e33ec015bc2f7a58852e79a0e084$b08a5209aa30d453c0d320357856e48bd4af801d285ff0823d4593bb8bf85f7d',
 'NEIGHBOR', NULL, '', NULL),
(1, 'Carlos Ruiz', 'carlos@test.com',
 'pbkdf2_sha256$260000$5032c583d73039f65fd196a2e1e2698a$5e8403c181a2d580e3d0fc84573d6741bfd3a0a8f6731e1e904f20dafbb449a9',
 'NEIGHBOR', NULL, '', NULL),
(1, 'Elena Sanz', 'elena@test.com',
 'pbkdf2_sha256$260000$d4eecaad6d82a14b71895ff519b61d7b$2133b4d6282aa7e1ef364aad742e725ba3a96a9ab9118916c855f368d6cfbd07',
 'NEIGHBOR', NULL, '', NULL),
(2, 'Miguel Torres', 'miguel@test.com',
 'pbkdf2_sha256$260000$66c37add68ac7f5b9db9cacef17a01a7$f5ffc296e000c431db8e74fa82b1dce9e70eaf8fa3ec2a0a6daccada7ea3c5d9',
 'NEIGHBOR', NULL, '', NULL),
(2, 'Sofia Leon', 'sofia@test.com',
 'pbkdf2_sha256$260000$6d753d5067246787a904df140358de1d$3e15151ca229c5dba11b65add68bc519f8d41a4e0b846a39c63120f0c25e2115',
 'NEIGHBOR', NULL, '', NULL),
(2, 'Pablo Vega', 'pablo@test.com',
 'pbkdf2_sha256$260000$60d28dff240a88afe328c59f38eab38e$6ccd63701d7a2a73c527486de797091bfefc1328441d406eab5bb10799573b43',
 'NEIGHBOR', NULL, '', NULL);

-- Demo admin plate. Admin-owned active plates are valid in every community.
INSERT INTO allowed_plate (community_id, user_id, plate, is_active, created_at)
SELECT 1, 1, '0000ADM', 1, NOW()
WHERE NOT EXISTS (
  SELECT 1 FROM allowed_plate WHERE plate = '0000ADM'
);

-- App-owned actuator actions for the existing seeded rules.
INSERT INTO rule_actuator_action (rule_id, actuator_id, command_type, target_state)
SELECT 1, 5, 'SET', 'ON'
WHERE NOT EXISTS (SELECT 1 FROM rule_actuator_action WHERE rule_id = 1 AND actuator_id = 5 AND command_type = 'SET');

INSERT INTO rule_actuator_action (rule_id, actuator_id, command_type, target_state)
SELECT 2, 1, 'SET', 'ON'
WHERE NOT EXISTS (SELECT 1 FROM rule_actuator_action WHERE rule_id = 2 AND actuator_id = 1 AND command_type = 'SET');

INSERT INTO rule_actuator_action (rule_id, actuator_id, command_type, target_state)
SELECT 2, 2, 'SET', 'ON'
WHERE NOT EXISTS (SELECT 1 FROM rule_actuator_action WHERE rule_id = 2 AND actuator_id = 2 AND command_type = 'SET');

INSERT INTO rule_actuator_action (rule_id, actuator_id, command_type, target_state)
SELECT 3, 5, 'SET', 'ON'
WHERE NOT EXISTS (SELECT 1 FROM rule_actuator_action WHERE rule_id = 3 AND actuator_id = 5 AND command_type = 'SET');

COMMIT;
