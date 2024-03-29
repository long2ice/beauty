from tortoise import Model, fields

from beauty.enums import Origin, PictureCategory


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
    url = fields.CharField(max_length=500, unique=True, null=True)
    origin_url = fields.CharField(max_length=500, unique=True)
    origin = fields.CharEnumField(Origin)
    description = fields.TextField(null=True)
    collection: fields.ForeignKeyRelation["Collection"] = fields.ForeignKeyField(
        "models.Collection", null=True
    )
    category = fields.CharEnumField(PictureCategory, default=PictureCategory.beauty)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    favorites: fields.ReverseRelation["Favorite"]
    likes: fields.ReverseRelation["Like"]


class Favorite(Model):
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField("models.User")
    picture: fields.ForeignKeyRelation[Picture] = fields.ForeignKeyField("models.Picture")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "picture")]


class Collection(Model):
    title = fields.CharField(max_length=200)
    description = fields.CharField(max_length=500)
    category = fields.CharEnumField(PictureCategory, default=PictureCategory.beauty)
    origin = fields.CharEnumField(Origin)
    pictures: fields.ReverseRelation[Picture]

    class Meta:
        unique_together = [("title", "origin")]


class Like(Model):
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField("models.User")
    picture: fields.ForeignKeyRelation[Picture] = fields.ForeignKeyField("models.Picture")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "picture")]


class Feedback(Model):
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField("models.User")
    content = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
