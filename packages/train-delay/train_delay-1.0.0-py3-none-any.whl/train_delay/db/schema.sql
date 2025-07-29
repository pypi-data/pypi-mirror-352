
CREATE DATABASE IF NOT EXISTS `{database_name}`;
USE `{database_name}`;

CREATE TABLE IF NOT EXISTS `trains` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `line` varchar(50) NOT NULL,
  `train_id` varchar(50) NOT NULL,
  `first_station` varchar(50) NOT NULL,
  `last_station` varchar(50) NOT NULL,
  `planned_departure` datetime NOT NULL,
  `current_departure` datetime DEFAULT NULL,
  `track` varchar(50) NOT NULL,
  `messages` varchar(50) NOT NULL,
  `train_station` varchar(2000) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `train_id` (`train_id`,`planned_departure`,`current_departure`)
) ENGINE=InnoDB AUTO_INCREMENT=818 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
