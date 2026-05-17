-- --------------------------------------------------------
-- AureaTech relational schema aligned with logicdiagram.txt
-- Source of truth: logical ER model (PlantUML)
-- Target: MariaDB / MySQL-compatible DDL
-- Notes:
--   * Table names changed to singular, as requested.
--   * Order of creation follows FK dependencies.
--   * Existing seed data was removed because it no longer matches the new schema.
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

DROP DATABASE IF EXISTS `pii26_aureatech`;
CREATE DATABASE IF NOT EXISTS `pii26_aureatech`
  /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;
USE `pii26_aureatech`;

-- ========================================================
-- Base entities
-- ========================================================

DROP TABLE IF EXISTS `chat_message`;
DROP TABLE IF EXISTS `chat_thread`;
DROP TABLE IF EXISTS `user_alert`;
DROP TABLE IF EXISTS `alert`;
DROP TABLE IF EXISTS `rule_alert_action`;
DROP TABLE IF EXISTS `rule_actuator_action`;
DROP TABLE IF EXISTS `audit_log`;
DROP TABLE IF EXISTS `faq`;
DROP TABLE IF EXISTS `error_event`;
DROP TABLE IF EXISTS `automation_rule`;
DROP TABLE IF EXISTS `reading`;
DROP TABLE IF EXISTS `actuator`;
DROP TABLE IF EXISTS `sensor`;
DROP TABLE IF EXISTS `user`;
DROP TABLE IF EXISTS `community`;

CREATE TABLE IF NOT EXISTS `community` (
  `community_id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(150) NOT NULL,
  `address` VARCHAR(255) DEFAULT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`community_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `user` (
  `user_id` INT NOT NULL AUTO_INCREMENT,
  `community_id` INT NULL,
  `full_name` VARCHAR(150) NOT NULL,
  `email` VARCHAR(180) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `role` VARCHAR(50) NOT NULL,
  `date_of_birth` DATE DEFAULT NULL,
  `picture_path` VARCHAR(255) DEFAULT NULL,
  `picture_url` VARCHAR(255) DEFAULT NULL,
  `is_active` TINYINT(1) NOT NULL DEFAULT 1,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `uq_user_email` (`email`),
  KEY `idx_user_community` (`community_id`),
  CONSTRAINT `fk_user_community`
    FOREIGN KEY (`community_id`) REFERENCES `community` (`community_id`)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `sensor` (
  `sensor_id` INT NOT NULL AUTO_INCREMENT,
  `community_id` INT NOT NULL,
  `sensor_type` VARCHAR(100) NOT NULL,
  `location` VARCHAR(150) DEFAULT NULL,
  `is_enabled` TINYINT(1) NOT NULL DEFAULT 1,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`sensor_id`),
  KEY `idx_sensor_community` (`community_id`),
  CONSTRAINT `fk_sensor_community`
    FOREIGN KEY (`community_id`) REFERENCES `community` (`community_id`)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `actuator` (
  `actuator_id` INT NOT NULL AUTO_INCREMENT,
  `community_id` INT NOT NULL,
  `actuator_type` VARCHAR(100) NOT NULL,
  `location` VARCHAR(150) DEFAULT NULL,
  `current_state` VARCHAR(100) NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `last_changed_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`actuator_id`),
  KEY `idx_actuator_community` (`community_id`),
  CONSTRAINT `fk_actuator_community`
    FOREIGN KEY (`community_id`) REFERENCES `community` (`community_id`)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `reading` (
  `reading_id` INT NOT NULL AUTO_INCREMENT,
  `sensor_id` INT NOT NULL,
  `reading_value` DECIMAL(10,2) NOT NULL,
  `unit` VARCHAR(20) NOT NULL,
  `recorded_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`reading_id`),
  KEY `idx_reading_sensor` (`sensor_id`),
  KEY `idx_reading_recorded_at` (`recorded_at`),
  CONSTRAINT `fk_reading_sensor`
    FOREIGN KEY (`sensor_id`) REFERENCES `sensor` (`sensor_id`)
    ON UPDATE CASCADE
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `automation_rule` (
  `rule_id` INT NOT NULL AUTO_INCREMENT,
  `sensor_id` INT NOT NULL,
  `rule_name` VARCHAR(150) NOT NULL,
  `metric_key` VARCHAR(100) NOT NULL,
  `comparison_operator` VARCHAR(20) NOT NULL,
  `threshold_value` DECIMAL(10,2) NOT NULL,
  `is_enabled` TINYINT(1) NOT NULL DEFAULT 1,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`rule_id`),
  KEY `idx_automation_rule_sensor` (`sensor_id`),
  CONSTRAINT `fk_automation_rule_sensor`
    FOREIGN KEY (`sensor_id`) REFERENCES `sensor` (`sensor_id`)
    ON UPDATE CASCADE
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `error_event` (
  `error_id` INT NOT NULL AUTO_INCREMENT,
  `exception_type` VARCHAR(150) NOT NULL,
  `severity` VARCHAR(50) NOT NULL,
  `message` TEXT NOT NULL,
  `source_layer` VARCHAR(100) NOT NULL,
  `stacktrace` TEXT DEFAULT NULL,
  `user_id` INT NULL,
  `community_id` INT NULL,
  `target_entity_type` VARCHAR(100) DEFAULT NULL,
  `target_entity_id` INT DEFAULT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`error_id`),
  KEY `idx_error_event_created_at` (`created_at`),
  KEY `idx_error_event_scope` (`created_at`, `severity`, `source_layer`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `faq` (
  `faq_id` INT NOT NULL AUTO_INCREMENT,
  `community_id` INT NOT NULL,
  `question` TEXT NOT NULL,
  `answer` TEXT NOT NULL,
  `tags` VARCHAR(255) DEFAULT NULL,
  `is_active` TINYINT(1) NOT NULL DEFAULT 1,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`faq_id`),
  KEY `idx_faq_community` (`community_id`),
  CONSTRAINT `fk_faq_community`
    FOREIGN KEY (`community_id`) REFERENCES `community` (`community_id`)
    ON UPDATE CASCADE
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `audit_log` (
  `log_id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `community_id` INT NULL,
  `actor_role` VARCHAR(50) NOT NULL,
  `category` VARCHAR(100) NOT NULL,
  `action` VARCHAR(100) NOT NULL,
  `target_entity_type` VARCHAR(100) DEFAULT NULL,
  `target_entity_id` INT DEFAULT NULL,
  `details` TEXT DEFAULT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`log_id`),
  KEY `idx_audit_log_user` (`user_id`),
  KEY `idx_audit_log_created_at` (`created_at`),
  KEY `idx_audit_log_scope` (`created_at`, `category`, `community_id`),
  KEY `idx_audit_log_actor_action` (`actor_role`, `action`),
  CONSTRAINT `fk_audit_log_user`
    FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ========================================================
-- Allowed plates per community / optional user ownership
-- ========================================================

CREATE TABLE IF NOT EXISTS `allowed_plate` (
  `allowed_plate_id` INT NOT NULL AUTO_INCREMENT,
  `community_id` INT NOT NULL,
  `user_id` INT DEFAULT NULL,
  `plate` VARCHAR(20) NOT NULL,
  `is_active` TINYINT(1) NOT NULL DEFAULT 1,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`allowed_plate_id`),
  UNIQUE KEY `uq_allowed_plate_plate` (`plate`),
  KEY `idx_allowed_plate_community` (`community_id`),
  KEY `idx_allowed_plate_user` (`user_id`),
  CONSTRAINT `fk_allowed_plate_community`
    FOREIGN KEY (`community_id`) REFERENCES `community` (`community_id`)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT `fk_allowed_plate_user`
    FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`)
    ON UPDATE CASCADE
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ========================================================
-- Camera recognition events
-- ========================================================

CREATE TABLE IF NOT EXISTS `camera_event` (
  `camera_event_id` INT NOT NULL AUTO_INCREMENT,
  `sensor_id` INT NOT NULL,
  `detected_plate` VARCHAR(20) NOT NULL,
  `is_allowed` TINYINT(1) DEFAULT NULL,
  `detected_at` DATETIME NOT NULL,
  `image_path` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`camera_event_id`),
  KEY `idx_camera_event_sensor` (`sensor_id`),
  KEY `idx_camera_event_plate` (`detected_plate`),
  KEY `idx_camera_event_detected_at` (`detected_at`),
  CONSTRAINT `fk_camera_event_sensor`
    FOREIGN KEY (`sensor_id`) REFERENCES `sensor` (`sensor_id`)
    ON UPDATE CASCADE
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ========================================================
-- Rule actions and alerts
-- ========================================================

CREATE TABLE IF NOT EXISTS `rule_actuator_action` (
  `rule_actuator_action_id` INT NOT NULL AUTO_INCREMENT,
  `rule_id` INT NOT NULL,
  `actuator_id` INT NOT NULL,
  `command_type` VARCHAR(100) NOT NULL,
  `target_state` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`rule_actuator_action_id`),
  KEY `idx_rule_actuator_action_rule` (`rule_id`),
  KEY `idx_rule_actuator_action_actuator` (`actuator_id`),
  CONSTRAINT `fk_rule_actuator_action_rule`
    FOREIGN KEY (`rule_id`) REFERENCES `automation_rule` (`rule_id`)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT `fk_rule_actuator_action_actuator`
    FOREIGN KEY (`actuator_id`) REFERENCES `actuator` (`actuator_id`)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `rule_alert_action` (
  `rule_alert_action_id` INT NOT NULL AUTO_INCREMENT,
  `rule_id` INT NOT NULL,
  `alert_type` VARCHAR(100) NOT NULL,
  `severity` VARCHAR(50) NOT NULL,
  `message_template` TEXT NOT NULL,
  PRIMARY KEY (`rule_alert_action_id`),
  KEY `idx_rule_alert_action_rule` (`rule_id`),
  CONSTRAINT `fk_rule_alert_action_rule`
    FOREIGN KEY (`rule_id`) REFERENCES `automation_rule` (`rule_id`)
    ON UPDATE CASCADE
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `alert` (
  `alert_id` INT NOT NULL AUTO_INCREMENT,
  `community_id` INT NOT NULL,
  `rule_alert_action_id` INT NOT NULL,
  `alert_type` VARCHAR(100) NOT NULL,
  `severity` VARCHAR(50) NOT NULL,
  `message` TEXT NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`alert_id`),
  KEY `idx_alert_community` (`community_id`),
  KEY `idx_alert_rule_alert_action` (`rule_alert_action_id`),
  KEY `idx_alert_created_at` (`created_at`),
  CONSTRAINT `fk_alert_community`
    FOREIGN KEY (`community_id`) REFERENCES `community` (`community_id`)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,
  CONSTRAINT `fk_alert_rule_alert_action`
    FOREIGN KEY (`rule_alert_action_id`) REFERENCES `rule_alert_action` (`rule_alert_action_id`)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `user_alert` (
  `user_alert_id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `alert_id` INT NOT NULL,
  `read_status` TINYINT(1) NOT NULL DEFAULT 0,
  `read_at` DATETIME DEFAULT NULL,
  PRIMARY KEY (`user_alert_id`),
  UNIQUE KEY `uq_user_alert_user_alert` (`user_id`, `alert_id`),
  KEY `idx_user_alert_alert` (`alert_id`),
  CONSTRAINT `fk_user_alert_user`
    FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT `fk_user_alert_alert`
    FOREIGN KEY (`alert_id`) REFERENCES `alert` (`alert_id`)
    ON UPDATE CASCADE
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ========================================================
-- Internal messaging
-- ========================================================

CREATE TABLE IF NOT EXISTS `chat_thread` (
  `thread_id` INT NOT NULL AUTO_INCREMENT,
  `community_id` INT NOT NULL,
  `created_by_user_id` INT NOT NULL,
  `assigned_user_id` INT DEFAULT NULL,
  `subject` VARCHAR(200) NOT NULL,
  `status` VARCHAR(50) NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `closed_at` DATETIME DEFAULT NULL,
  PRIMARY KEY (`thread_id`),
  KEY `idx_chat_thread_community` (`community_id`),
  KEY `idx_chat_thread_created_by` (`created_by_user_id`),
  KEY `idx_chat_thread_assigned_user` (`assigned_user_id`),
  CONSTRAINT `fk_chat_thread_community`
    FOREIGN KEY (`community_id`) REFERENCES `community` (`community_id`)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,
  CONSTRAINT `fk_chat_thread_created_by_user`
    FOREIGN KEY (`created_by_user_id`) REFERENCES `user` (`user_id`)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,
  CONSTRAINT `fk_chat_thread_assigned_user`
    FOREIGN KEY (`assigned_user_id`) REFERENCES `user` (`user_id`)
    ON UPDATE CASCADE
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `chat_message` (
  `message_id` INT NOT NULL AUTO_INCREMENT,
  `thread_id` INT NOT NULL,
  `sender_user_id` INT NOT NULL,
  `content` TEXT NOT NULL,
  `message_type` VARCHAR(50) NOT NULL,
  `sent_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`message_id`),
  KEY `idx_chat_message_thread` (`thread_id`),
  KEY `idx_chat_message_sender` (`sender_user_id`),
  KEY `idx_chat_message_sent_at` (`sent_at`),
  CONSTRAINT `fk_chat_message_thread`
    FOREIGN KEY (`thread_id`) REFERENCES `chat_thread` (`thread_id`)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT `fk_chat_message_sender_user`
    FOREIGN KEY (`sender_user_id`) REFERENCES `user` (`user_id`)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;

-- Communities
INSERT INTO community (community_id, name, address, created_at) VALUES
(1, 'Los Ãlamos', 'Avenida de Castilla 37, Las Rozas - Madrid', NOW()),
(2, 'Villa Romana', 'Calle los Farolillos s/n, Agulo, La Gomera - Islas Canarias', NOW());

-- Users
INSERT INTO user (
    community_id,
    full_name,
    email,
    password_hash,
    role,
    date_of_birth,
    picture_path,
    picture_url
) VALUES

(null, 'MarÃ­a Esperanza', 'admin@test.com',
 'pbkdf2_sha256$260000$e95ebd623fa6a2dfade14ac2559bfc38$bf4202343c08be1bfcbd0bfdcd9c1f7c61a6d07bba236e1b5736a72e1533c4cc',
 'ADMIN', NULL, '', 'https://images.pexels.com/photos/1130626/pexels-photo-1130626.jpeg'),

(1, 'Tech Support Comunidad 1', 'tech1@test.com',
 'pbkdf2_sha256$260000$944e6581c97cfd9e1e5dded537130597$d565ede687d7105d80b6e657379400d4cbdc0af735ed560eb8b287a18cf56c21',
 'TECHNICIAN', NULL, '', 'https://images.pexels.com/photos/346529/pexels-photo-346529.jpeg'),

(2, 'Tech Support Comunidad 2', 'tech2@test.com',
 'pbkdf2_sha256$260000$faf0e19f7ea10fb712214de276369da6$73943db8a2c80e91f3c89c7f511d6dfd94845921a3cdee862085dec8cb237abd',
 'TECHNICIAN', NULL, '', 'https://images.pexels.com/photos/346529/pexels-photo-346529.jpeg'),

(1, 'AureaTech', 'aurea@tech.com',
 'pbkdf2_sha256$260000$5c9e2bc05ee0028ce8472c37b75ea98b$1addff5dc1fb569b9e6acd7636e59c025113a273142e5149debc2ec1cdb1f805',
 'NEIGHBOR', NULL, '', 'https://images.pexels.com/photos/1542085/pexels-photo-1542085.jpeg'),

(2, 'Juan', 'juan@juan.com',
 'pbkdf2_sha256$260000$f4817f8cff4e6aabf9e1e7c7fd9930f7$f75dd958ccd186ac6dfb187c19540e8aaa976b4343c5c1dbebcae1ea8dbb6b6c',
 'NEIGHBOR', NULL, '', 'https://images.pexels.com/photos/1819483/pexels-photo-1819483.jpeg'),

(2, 'Pepe PÃ©rez', 'pepe@perez.com',
 'pbkdf2_sha256$260000$2457c5fd8f6dd196cf61c016a5c40d8f$f44b8e7576fb3ff266fc095813f793f7265924b2906cbbd5b38e8bd3ce35c08b',
 'NEIGHBOR', STR_TO_DATE('14/12/2003','%d/%m/%Y'), NULL, NULL),

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
 
-- Sensors
INSERT INTO sensor (
    community_id,
    sensor_type,
    location,
    is_enabled,
    created_at
) VALUES
(1, 'TEMPERATURE', 'Zona Residencial', 1, NOW()),
(1, 'HUMIDITY',    'Zona Residencial', 1, NOW()),
(2, 'TEMPERATURE', 'Zona Residencial', 1, NOW()),
(2, 'HUMIDITY',    'Zona Residencial', 1, NOW()),
(1, 'LIGHT',       'Zona Residencial', 1, NOW()),
(1, 'DISTANCE',    'Zona Residencial', 1, NOW()),
(2, 'LIGHT',       'Zona Residencial', 1, NOW()),
(2, 'DISTANCE',    'Zona Residencial', 1, NOW()),
(1, 'SMOKE',       'Zona Residencial', 1, NOW()),
(1, 'WIND',        'Zona Residencial', 1, NOW()),
(2, 'SMOKE',       'Zona Residencial', 1, NOW()),
(2, 'WIND',        'Zona Residencial', 1, NOW()),
(1, 'CAMERA',      'Zona Residencial', 1, NOW()), 
(2, 'CAMERA',      'Zona Residencial', 1, NOW()); 
 
-- Actuators
INSERT INTO actuator (
    community_id,
    actuator_type,
    location,
    current_state,
    created_at,
    last_changed_at
) VALUES
(1, 'LED',        'Streetlight 1A', 'ON',     NOW(), '2025-12-14 20:51:37'),
(1, 'LED',        'Streetlight 1B', 'OFF',    NOW(), '2025-12-14 21:15:57'),
(2, 'LED',        'Streetlight 2A', 'ON',     NOW(), '2025-12-14 16:22:34'),
(2, 'LED',        'Streetlight 2B', 'OFF',    NOW(), '2025-12-14 21:25:43'),
(1, 'BUZZER',     'Fire Alarm 1A',  'OFF',    NOW(), '2025-12-14 15:45:45'),
(1, 'SERVOMOTOR', 'Garage Door 1A', 'CLOSED', NOW(), '2025-12-14 16:22:54'),
(2, 'SERVOMOTOR', 'Garage Door 2A', 'OPEN',   NOW(), '2025-12-14 16:22:54');

-- Sensor readings
INSERT INTO reading (
    sensor_id,
    reading_value,
    unit,
    recorded_at
) VALUES
(1, 17.40, 'C',     '2026-03-22 08:00:00'),
(2, 49.20, '%',     '2026-03-22 08:00:00'),
(5, 120.00, 'lux',  '2026-03-22 08:00:00'),
(6, 85.00,  'cm',   '2026-03-22 08:00:00'),
(3, 16.80, 'C',     '2026-03-23 09:30:00'),
(4, 52.40, '%',     '2026-03-23 09:30:00'),
(7, 340.00,'lux',   '2026-03-23 09:30:00'),
(8, 210.00,'cm',    '2026-03-23 09:30:00'),
(9, 14.00, 'ppm',   '2026-03-24 18:45:00'),
(10, 9.80, 'km/h',  '2026-03-24 18:45:00'),
(11, 18.50,'ppm',   '2026-03-25 19:15:00'),
(12, 12.60,'km/h',  '2026-03-25 19:15:00'),
(1, 21.30, 'C',     '2026-03-26 13:10:00'),
(2, 43.70, '%',     '2026-03-26 13:10:00'),
(5, 910.00,'lux',   '2026-03-26 13:10:00'),
(3, 19.90, 'C',     '2026-03-27 14:20:00'),
(4, 46.10, '%',     '2026-03-27 14:20:00'),
(7, 870.00,'lux',   '2026-03-27 14:20:00');

-- Car plates
INSERT INTO `allowed_plate` (
  `community_id`,
  `user_id`,
  `plate`,
  `is_active`,
  `created_at`
) VALUES
(1, 4, '9172VCW', 1, NOW()),
(1, 4, '0620SBW', 1, NOW()),
(1, 2, '5013XVX', 1, NOW()),
(1, 2, '1113YBY', 1, NOW()),
(1, 1, '0000ADM', 1, NOW()),

(2, 5, '0879LPM', 1, NOW()),
(2, 5, '8488KDG', 1, NOW()),
(2, 6, '9315DSN', 1, NOW()),
(2, 6, '1731KJJ', 1, NOW());

-- Audit logs
INSERT INTO audit_log (
  user_id,
  actor_role,
  category,
  action,
  details,
  created_at
) VALUES
(1, 'ADMIN', 'AUTH', 'login_ok', 'admin@test.com', '2025-12-14 23:01:42'),
(1, 'ADMIN', 'AUTH', 'login_ok', 'admin@test.com', '2025-12-14 23:01:24'),
(1, 'ADMIN', 'AUTH', 'login_ok', 'ADMIN@TEST.COM', '2025-12-14 22:57:11'),
(1, 'ADMIN', 'AUTH', 'login_ok', 'admin@test.com', '2025-12-14 22:56:05'),
(1, 'ADMIN', 'AUTH', 'login_ok', 'admin@test.com', '2025-12-14 22:47:51'),
(1, 'ADMIN', 'AUTH', 'login_ok', 'admin@test.com', '2025-12-14 22:43:36'),
(1, 'ADMIN', 'AUTH', 'login_ok', 'admin@test.com', '2025-12-14 22:40:42'),
(3, 'TECHNICIAN', 'ACTUATOR', 'TOGGLE',
 'Actuator set to ON (community 2)', '2025-12-14 21:10:26'),
(3, 'TECHNICIAN', 'ACTUATOR', 'TOGGLE',
 'Actuator set to OFF (community 2)', '2025-12-14 21:10:20'),
(3, 'TECHNICIAN', 'AUTH', 'login_ok',
 'tech2@test.com', '2025-12-14 21:10:01');

-- FAQs
INSERT INTO faq (
  community_id,
  question,
  answer,
  tags,
  is_active,
  created_at
) VALUES

(1, 'Why is the street light not turning on?',
 'Street lights only turn on at night and when presence is detected nearby.',
 'lights,street,presence', 1, NOW()),

(1, 'What should I do if temperature readings seem wrong?',
 'Please wait for the next refresh cycle. If the issue persists, open a chat with support.',
 'temperature,sensor,dht22', 1, NOW()),

(1, 'Why is humidity always high?',
 'Humidity sensors may be affected by environmental conditions. Ensure proper placement.',
 'humidity,sensor', 1, NOW()),

(2, 'Why does the garage not open?',
 'Check if your license plate is registered in the system.',
 'garage,access,plate', 1, NOW()),

(2, 'What happens if smoke is detected?',
 'An alert is triggered and the alarm system is activated automatically.',
 'smoke,alarm,safety', 1, NOW()),

(2, 'Why are street lights on during the day?',
 'They may be under maintenance or manual override by technicians.',
 'lights,override', 1, NOW());

-- Chats
INSERT INTO chat_thread (
  community_id,
  created_by_user_id,
  assigned_user_id,
  subject,
  status,
  created_at,
  closed_at
) VALUES
(1, 4, 2, 'Street light issue', 'OPEN', '2026-03-16 18:00:00', NULL),
(2, 5, 3, 'Garage not opening', 'OPEN', '2026-03-20 10:15:00', NULL),
(1, 4, 2, 'Temperature sensor issue', 'CLOSED', '2026-03-18 12:00:00', '2026-03-18 14:30:00'),
(2, 6, 3, 'Smoke alert triggered', 'CLOSED', '2026-03-21 19:00:00', '2026-03-21 19:20:00');

-- Messages
INSERT INTO chat_message (
  thread_id,
  sender_user_id,
  content,
  message_type,
  sent_at
) VALUES

-- Thread 1
(1, 4, 'Hi, the street light is not turning on.', 'TEXT', '2026-03-16 18:01:00'),
(1, 2, 'Hello, we are checking the issue.', 'TEXT', '2026-03-16 18:05:00'),

-- Thread 2
(2, 5, 'My garage is not opening.', 'TEXT', '2026-03-20 10:16:00'),
(2, 3, 'Please confirm your plate is registered.', 'TEXT', '2026-03-20 10:18:00'),

-- Thread 3
(3, 4, 'Temperature values look wrong.', 'TEXT', '2026-03-18 12:01:00'),
(3, 2, 'Sensor recalibrated, please check again.', 'TEXT', '2026-03-18 14:00:00'),

-- Thread 4
(4, 6, 'Smoke alarm triggered unexpectedly.', 'TEXT', '2026-03-21 19:01:00'),
(4, 3, 'False alarm confirmed, system reset.', 'TEXT', '2026-03-21 19:15:00');

-- Minimal automation rules for alert seeding
INSERT INTO automation_rule (
  sensor_id,
  rule_name,
  metric_key,
  comparison_operator,
  threshold_value,
  is_enabled,
  created_at
) VALUES
(1,  'High temperature critical rule', 'temperature', '>', 38.00, 1, NOW()),
(5,  'Low light info rule',            'light',       '<', 50.00, 1, NOW()),
(9,  'Poor air quality warning rule',  'smoke',       '>', 180.00, 1, NOW());

-- Rule alert action
INSERT INTO rule_alert_action (
  rule_id,
  alert_type,
  severity,
  message_template
) VALUES
(1, 'high_temperature', 'CRIT', 'Temperatura crÃ­tica detectada'),
(2, 'low_light',        'INFO', 'Nivel de luz bajo'),
(3, 'poor_air_quality', 'WARN', 'Calidad del aire deficiente');

-- Rule actuator actions used by the app-side rule engine
INSERT INTO rule_actuator_action (
  rule_id,
  actuator_id,
  command_type,
  target_state
) VALUES
(1, 5, 'SET', 'ON'),
(2, 1, 'SET', 'ON'),
(2, 2, 'SET', 'ON'),
(3, 5, 'SET', 'ON');

-- Alerts
INSERT INTO alert (
  community_id,
  rule_alert_action_id,
  alert_type,
  severity,
  message,
  created_at
) VALUES
(1, 1, 'high_temperature', 'CRIT',
 'Temperatura crÃ­tica detectada: 38.4Â°C',
 '2025-12-14 18:05:00'),

(1, 2, 'low_light', 'INFO',
 'Nivel de luz bajo: 42 lux',
 '2025-12-14 17:52:00'),

(1, 3, 'poor_air_quality', 'WARN',
 'Calidad del aire deficiente: 182 ppm',
 '2025-12-14 17:30:00');

-- User alerts
INSERT INTO user_alert (
  user_id,
  alert_id,
  read_status,
  read_at
) VALUES
(1, 1, 0, NULL),
(2, 2, 0, NULL),
(4, 1, 0, NULL),
(2, 1, 0, NULL),
(4, 2, 0, NULL),
(3, 2, 0, NULL),
(3, 3, 1, '2026-02-14 8:10:00'),
(5, 2, 0, NULL),
(5, 3, 1, '2025-12-14 18:10:00'),
(6, 2, 0, NULL),
(6, 3, 1, '2026-02-27 13:30:00');

-- Camera events
INSERT INTO camera_event (
  sensor_id,
  detected_plate,
  is_allowed,
  detected_at,
  image_path
) VALUES
(13, '9172VCW', 1, '2026-03-24 18:45:00', NULL),
(13, '5983CPR', 0, '2026-03-27 21:00:00', NULL),
(14, '8488KDG', 1, '2026-03-24 19:15:00', NULL),
(14, '9999ZZZ', 0, '2026-03-28 22:15:00', NULL);

