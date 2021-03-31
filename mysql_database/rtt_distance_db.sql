DROP TABLE IF EXISTS `rtt_distance`;

CREATE TABLE `rtt_distance` (
`id` int(15) NOT NULL AUTO_INCREMENT,
`first_location_ip` varchar(15) NULL,
`first_location_name` varchar(132) NULL,
`first_location_coordinates` varchar(132) NULL,
`second_location_ip` varchar(15) NULL,
`second_location_name` varchar(132) NULL,
`second_location_coordinates` varchar(132) NULL,
`rtt` varchar(64) NULL,
`distance` varchar(64) NULL,
PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `rtt_distance` WRITE;

UNLOCK TABLES;


