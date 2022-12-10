from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `collection` ADD `category` VARCHAR(2) NOT NULL  COMMENT 'beauty: 美女\nscenery: 风景' DEFAULT '美女';
        ALTER TABLE `picture` ADD `category` VARCHAR(2) NOT NULL  COMMENT 'beauty: 美女\nscenery: 风景' DEFAULT '美女';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `picture` DROP COLUMN `category`;
        ALTER TABLE `collection` DROP COLUMN `category`;"""
