from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `collection` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `title` VARCHAR(200) NOT NULL,
    `description` VARCHAR(500) NOT NULL,
    `origin` VARCHAR(15) NOT NULL  COMMENT 'netbian: www.netbian.com\nwin3000: www.win3000.com',
    UNIQUE KEY `uid_collection_title_02772d` (`title`, `origin`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `picture` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `url` VARCHAR(500)  UNIQUE,
    `origin_url` VARCHAR(500) NOT NULL UNIQUE,
    `origin` VARCHAR(15) NOT NULL  COMMENT 'netbian: www.netbian.com\nwin3000: www.win3000.com',
    `description` LONGTEXT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `collection_id` INT,
    CONSTRAINT `fk_picture_collecti_2ef08cfd` FOREIGN KEY (`collection_id`) REFERENCES `collection` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `user` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `openid` VARCHAR(200) NOT NULL UNIQUE,
    `avatar` VARCHAR(500) NOT NULL  DEFAULT 'https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0',
    `nickname` VARCHAR(200) NOT NULL  DEFAULT '微信用户',
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `favorite` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `picture_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    UNIQUE KEY `uid_favorite_user_id_6c3c64` (`user_id`, `picture_id`),
    CONSTRAINT `fk_favorite_picture_d14e685c` FOREIGN KEY (`picture_id`) REFERENCES `picture` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_favorite_user_babde07c` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `feedback` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `content` LONGTEXT NOT NULL,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `user_id` INT NOT NULL,
    CONSTRAINT `fk_feedback_user_3669089f` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `like` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `picture_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    UNIQUE KEY `uid_like_user_id_b96668` (`user_id`, `picture_id`),
    CONSTRAINT `fk_like_picture_6e94692b` FOREIGN KEY (`picture_id`) REFERENCES `picture` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_like_user_e8643edc` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
