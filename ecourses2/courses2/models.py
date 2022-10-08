from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    avatar = models.ImageField(upload_to='uploads/%Y/%m', default=None)


class Category(models.Model):
    name = models.CharField(max_length=50, null=False, unique=True)

    def __str__(self):
        return self.name

class ItemBase(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=100, null=False)
    image = models.ImageField(upload_to='courses/%Y/%m', default=None)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Course(ItemBase):
    class Meta:
        unique_together = ('name', 'category')

    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')

class Lesson(ItemBase):
    class Meta:
        unique_together = ('name', 'course')

    content = models.TextField(null=True, blank=True)
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag', related_name='lessons', blank=True, null=True)

class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Comment(models.Model):
    content = models.TextField()
    lesson = models.ForeignKey(Lesson, related_name='comments', on_delete=models.CASCADE)
    creater = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content


class BaseAction(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    creater = models.ForeignKey(User, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        unique_together = ('creater', 'lesson')


class Like(BaseAction):
    active = models.BooleanField(default=False)


class Rating(BaseAction):
    rate = models.PositiveSmallIntegerField(default=0)


class Action(BaseAction):
    LIKE, HAHA, HEART = range(3)  # ~ LIKE=0, HAHA=1, HEART=2
    ACTIONS = [
        (LIKE, 'like'),
        (HAHA, 'haha'),
        (HEART, 'heart')
    ]
    type = models.PositiveSmallIntegerField(choices=ACTIONS, default=LIKE)


class LessonView(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)
    lesson = models.OneToOneField(Lesson, related_name='views', on_delete=models.CASCADE)

