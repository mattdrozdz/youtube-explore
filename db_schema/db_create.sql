SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

CREATE SCHEMA IF NOT EXISTS `youtube` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
USE `youtube` ;

-- -----------------------------------------------------
-- Table `youtube`.`channel`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `youtube`.`channel` ;

CREATE TABLE IF NOT EXISTS `youtube`.`channel` (
  `channel_id` VARCHAR(100) NOT NULL,
  `title` VARCHAR(160) NULL,
  `description` TEXT NULL,
  `published_at` TIMESTAMP NULL,
  `country` VARCHAR(45) NULL,
  `traversed` TINYINT NULL DEFAULT 0,
  `parent_id` VARCHAR(100) NULL,
  PRIMARY KEY (`channel_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `youtube`.`video`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `youtube`.`video` ;

CREATE TABLE IF NOT EXISTS `youtube`.`video` (
  `video_id` VARCHAR(100) NOT NULL,
  `channel_id` VARCHAR(100) NOT NULL,
  `title` VARCHAR(160) NULL,
  `published_at` TIMESTAMP NULL,
  `description` TEXT NULL,
  `category_id` VARCHAR(100) NULL,
  PRIMARY KEY (`video_id`),
  INDEX `fk_video_channel1_idx` (`channel_id` ASC),
  CONSTRAINT `fk_video_channel1`
    FOREIGN KEY (`channel_id`)
    REFERENCES `youtube`.`channel` (`channel_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `youtube`.`comment`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `youtube`.`comment` ;

CREATE TABLE IF NOT EXISTS `youtube`.`comment` (
  `comment_id` VARCHAR(100) NOT NULL,
  `author_channel_id` VARCHAR(100) NULL,
  `channel_id` VARCHAR(100) NOT NULL COMMENT 'channel_id comment refers to',
  `video_id` VARCHAR(100) NOT NULL,
  `reply_to` VARCHAR(100) NULL,
  `text` TEXT NULL,
  `total_reply_count` INT NULL,
  `like_count` INT NULL,
  `published_at` VARCHAR(45) NULL,
  PRIMARY KEY (`comment_id`),
  INDEX `fk_comment_video_idx` (`video_id` ASC),
  INDEX `fk_comment_channel1_idx` (`channel_id` ASC),
  INDEX `fk_comment_channel2_idx` (`author_channel_id` ASC),
  INDEX `fk_comment_comment1_idx` (`reply_to` ASC),
  CONSTRAINT `fk_comment_video`
    FOREIGN KEY (`video_id`)
    REFERENCES `youtube`.`video` (`video_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_comment_channel1`
    FOREIGN KEY (`channel_id`)
    REFERENCES `youtube`.`channel` (`channel_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_comment_channel2`
    FOREIGN KEY (`author_channel_id`)
    REFERENCES `youtube`.`channel` (`channel_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_comment_comment1`
    FOREIGN KEY (`reply_to`)
    REFERENCES `youtube`.`comment` (`comment_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `youtube`.`channel_statistics`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `youtube`.`channel_statistics` ;

CREATE TABLE IF NOT EXISTS `youtube`.`channel_statistics` (
  `channel_id` VARCHAR(100) NOT NULL,
  `view_count` INT NULL,
  `comment_count` INT NULL,
  `subscriber_count` INT NULL,
  `hidden_subscriber_count` TINYINT(1) NULL,
  `video_count` INT NULL,
  INDEX `fk_channel_statistics_channel1_idx` (`channel_id` ASC),
  CONSTRAINT `fk_channel_statistics_channel1`
    FOREIGN KEY (`channel_id`)
    REFERENCES `youtube`.`channel` (`channel_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `youtube`.`video_statistics`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `youtube`.`video_statistics` ;

CREATE TABLE IF NOT EXISTS `youtube`.`video_statistics` (
  `video_id` VARCHAR(100) NOT NULL,
  `view_count` INT NULL,
  `like_count` INT NULL,
  `dislike_count` INT NULL,
  `favourite_count` INT NULL,
  `comment_count` INT NULL,
  INDEX `fk_video_statistics_video1_idx` (`video_id` ASC),
  CONSTRAINT `fk_video_statistics_video1`
    FOREIGN KEY (`video_id`)
    REFERENCES `youtube`.`video` (`video_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
