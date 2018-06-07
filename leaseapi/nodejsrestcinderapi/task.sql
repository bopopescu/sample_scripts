-- Vivek SQL Dump
-- version 4.0.4
-- http://www.google.com
--
-- Host: localhost
-- Generation Time: April 16, 2018 at 01:23 PM
-- Server version: 5.6.12-log

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: 'testVivek'
--

-- --------------------------------------------------------

--
-- Table structure for table `task`
--
use database testVivek;

CREATE TABLE IF NOT EXISTS `task` (
  `Id` varchar(50) NOT NULL,
  `Title` varchar(500) DEFAULT NULL,
  `Status` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `task`
--

INSERT INTO `task` (`Id`, `Title`, `Status`) VALUES
('1', 'Go to Market tomorrow', 'done'),
('2', 'Email to manager', 'pending'),
('3', 'Push code to GitHub', 'done'),
('4', 'Go For Running', 'done'),
('5', 'Go to Movie', 'pending');

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
