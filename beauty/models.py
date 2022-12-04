from tortoise import Model, fields

from beauty.enums import Origin


class User(Model):
    openid = fields.CharField(max_length=200, unique=True)
    avatar = fields.CharField(
        max_length=500,
        default="https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0",
    )
    nickname = fields.CharField(max_length=200, default="微信用户")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class Picture(Model):
    url = fields.CharField(max_length=500, unique=True)
    origin = fields.CharEnumField(Origin)
    description = fields.TextField(null=True)
    collection: fields.ForeignKeyRelation["Collection"] = fields.ForeignKeyField(
        "models.Collection", null=True
    )
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    favorites: fields.ReverseRelation["Favorite"]
    ratings: fields.ReverseRelation["Rating"]


class Favorite(Model):
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField("models.User")
    picture: fields.ForeignKeyRelation[Picture] = fields.ForeignKeyField(
        "models.Picture"
    )
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "picture")]


class Collection(Model):
    title = fields.CharField(max_length=200)
    description = fields.CharField(max_length=500)
    origin = fields.CharEnumField(Origin)
    pictures: fields.ReverseRelation[Picture]

    class Meta:
        unique_together = [("title", "origin")]


class Rating(Model):
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField("models.User")
    rating = fields.IntField()
    picture: fields.ForeignKeyRelation[Picture] = fields.ForeignKeyField(
        "models.Picture"
    )
    comment = fields.CharField(max_length=500, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        unique_together = [("user", "picture")]
