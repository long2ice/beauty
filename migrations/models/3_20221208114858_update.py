from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `picture` ADD `origin_url` VARCHAR(500)  UNIQUE;
        UPDATE `picture` SET `origin_url` = `url`;
        UPDATE `picture` SET `url` = NULL;
        ALTER TABLE `picture` MODIFY COLUMN `url` VARCHAR(500);
        ALTER TABLE `picture` MODIFY COLUMN `origin_url` VARCHAR(500) NOT NULL ;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `picture` DROP INDEX `idx_picture_origin__d36072`;
        ALTER TABLE `picture` DROP COLUMN `origin_url`;
        ALTER TABLE `picture` MODIFY COLUMN `url` VARCHAR(500) NOT NULL;"""
