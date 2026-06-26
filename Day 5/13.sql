CREATE SCHEMA IF NOT EXISTS `cinema` DEFAULT CHARACTER SET utf8 ;
USE `cinema` ;
-- -----------------------------------------------------
-- Table `cinema`.`Movies`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cinema`.`Movies` (
  `id_film` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(150) NOT NULL,
  `director` VARCHAR(100) NOT NULL,
  `duration_min` INT NOT NULL,
  `age_rating` VARCHAR(10) NOT NULL,
  PRIMARY KEY (`id_film`))
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `cinema`.`Armchairs`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cinema`.`Armchairs` (
  `id_armchairs` INT NOT NULL AUTO_INCREMENT,
  `row` INT NOT NULL,
  `place` INT NOT NULL,
  PRIMARY KEY (`id_armchairs`))
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `cinema`.`Halls`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cinema`.`Halls` (
  `id_hall` INT NOT NULL AUTO_INCREMENT,
  `number` INT NOT NULL,
  `capacity` INT NOT NULL,
  `type` VARCHAR(20) NULL,
  `id_armchairs` INT NULL,
  PRIMARY KEY (`id_hall`),
  UNIQUE INDEX `number_UNIQUE` (`number` ASC) VISIBLE,
  INDEX `id_armchairs_idx` (`id_armchairs` ASC) VISIBLE,
  CONSTRAINT `id_armchairs`
    FOREIGN KEY (`id_armchairs`)
    REFERENCES `cinema`.`Armchairs` (`id_armchairs`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `cinema`.`Sessions`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cinema`.`Sessions` (
  `id_session` INT NOT NULL AUTO_INCREMENT,
  `date` DATE NOT NULL,
  `time` TIME NOT NULL,
  `price` DECIMAL(10,2) NOT NULL,
  `id_film` INT NULL,
  `id_hall` INT NULL,
  PRIMARY KEY (`id_session`),
  INDEX `id_session_idx` (`id_hall` ASC) VISIBLE,
  INDEX `id_film_idx` (`id_film` ASC) VISIBLE,
  CONSTRAINT `id_hall`
    FOREIGN KEY (`id_hall`)
    REFERENCES `cinema`.`Halls` (`id_hall`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `id_film`
    FOREIGN KEY (`id_film`)
    REFERENCES `cinema`.`Movies` (`id_film`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `cinema`.`Buyers`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cinema`.`Buyers` (
  `id_buyer` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NULL,
  `telephone` VARCHAR(20) NULL,
  PRIMARY KEY (`id_buyer`))
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `cinema`.`Tickets`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Tickets` (
    `id_ticket` INT NOT NULL AUTO_INCREMENT,
    `status` VARCHAR(20) NOT NULL DEFAULT 'free',
    `id_session` INT NULL,
    `id_armchairs` INT NULL,
    `id_buyer` INT NULL,
    PRIMARY KEY (`id_ticket`),
    INDEX `id_buyer_idx` (`id_buyer` ASC),
    INDEX `id_armchairs_idx` (`id_armchairs` ASC),
    INDEX `id_session_idx` (`id_session` ASC),
    CONSTRAINT `fk_tickets_buyer`
        FOREIGN KEY (`id_buyer`)
        REFERENCES `Buyers` (`id_buyer`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT `fk_tickets_armchairs`
        FOREIGN KEY (`id_armchairs`)
        REFERENCES `Armchairs` (`id_armchairs`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT `fk_tickets_session`
        FOREIGN KEY (`id_session`)
        REFERENCES `Sessions` (`id_session`)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;