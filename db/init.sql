CREATE DATABASE IF NOT EXISTS `avqf1`;
USE `avqf1`;

CREATE TABLE IF NOT EXISTS `bets` (
  `UserID` int NOT NULL,
  `GPID` int NOT NULL,
  `DriverID` int NOT NULL,
  `Pos` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

CREATE TABLE IF NOT EXISTS `driver` (
  `DriverID` int NOT NULL AUTO_INCREMENT,
  `TeamID` int NOT NULL DEFAULT '0',
  `Abv` char(3) NOT NULL,
  `DriverName` char(50) NOT NULL,
  `img` char(50) NOT NULL,
  PRIMARY KEY (`DriverID`) USING BTREE,
  UNIQUE KEY `Abv` (`Abv`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

CREATE TABLE IF NOT EXISTS `driverpos` (
  `GPNum` int NOT NULL,
  `DriverID` int NOT NULL,
  `Pos` int NOT NULL,
  `Status` char(50) NOT NULL DEFAULT '',
  `Points` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

CREATE TABLE IF NOT EXISTS `fastlaptime` (
  `GPNum` int NOT NULL,
  `DriverID` int NOT NULL,
  `LapNum` int NOT NULL,
  `LapTime` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

CREATE TABLE IF NOT EXISTS `gp` (
  `GPID` int NOT NULL,
  `GPName` char(100) NOT NULL,
  `GPFormat` char(50) NOT NULL,
  `GPDate` char(50) NOT NULL DEFAULT '',
  `Cimg` char(50) NOT NULL,
  `Flagimg` char(50) NOT NULL,
  `Country` char(50) NOT NULL,
  `Location` char(50) NOT NULL,
  `Timezone` char(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

CREATE TABLE IF NOT EXISTS `team` (
  `TeamID` int NOT NULL AUTO_INCREMENT,
  `TeamName` char(100) NOT NULL,
  `TeamColor` char(10) NOT NULL,
  `img` char(50) NOT NULL,
  PRIMARY KEY (`TeamID`),
  UNIQUE KEY `TeamName` (`TeamName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

CREATE TABLE IF NOT EXISTS `user` (
  `UserID` int unsigned NOT NULL AUTO_INCREMENT,
  `UserName` char(50) NOT NULL,
  `UserEMail` char(100) NOT NULL,
  `UserPassword` char(102) NOT NULL,
  `UserGender` char(10) NOT NULL DEFAULT 'other',
  `UserPoints` int unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`UserID`),
  UNIQUE KEY `UserEMail` (`UserEMail`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

