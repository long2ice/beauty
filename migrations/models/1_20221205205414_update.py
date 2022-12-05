from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `like` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `picture_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    UNIQUE KEY `uid_like_user_id_b96668` (`user_id`, `picture_id`),
    CONSTRAINT `fk_like_picture_6e94692b` FOREIGN KEY (`picture_id`) REFERENCES `picture` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_like_user_e8643edc` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
        DROP TABLE IF EXISTS `rating`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `like`;"""
