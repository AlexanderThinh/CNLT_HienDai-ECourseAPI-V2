from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import *


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class CourseSerializer(ModelSerializer):
    image = SerializerMethodField()

    def get_image(self, course):
        request = self.context['request']

        name = course.image.name

        if name.startswith('static/'):
            path = '/%s' % name
        else:
            path = '/static/%s' % name
        return request.build_absolute_uri(path)

    class Meta:
        model = Course
        fields = ['id', 'name', 'image', 'created_date', 'updated_date', 'category']

class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class LessonSerializer(ModelSerializer):
    image = SerializerMethodField()

    def get_image(self, lesson):
        request = self.context['request']

        name = lesson.image.name

        if name.startswith('static/'):
            path = '/%s' % name
        else:
            path = '/static/%s' % name
        return request.build_absolute_uri(path)

    class Meta:
        model = Lesson
        fields = ['id', 'name', 'image', 'created_date', 'updated_date', 'course']


class LessonDetailSerializer(LessonSerializer):
    tags = TagSerializer(many=True)
    rate = SerializerMethodField()
    image = SerializerMethodField()

    def get_image(self, lesson):
        request = self.context['request']

        name = lesson.image.name

        if name.startswith('static/'):
            path = '/%s' % name
        else:
            path = '/static/%s' % name
        return request.build_absolute_uri(path)

    def get_rate(self, lesson):
        request = self.context['request']
        if request and request.user.is_authenticated:
            r = lesson.rating_set.filter(creater=request.user).first()
            if r:
                return r.rate

        return -1

    class Meta:
        model = LessonSerializer.Meta.model
        fields = LessonSerializer.Meta.fields + ['content', 'tags', 'rate']


class UserSerializer(ModelSerializer):
    avatar = SerializerMethodField()
    def get_avatar(self, user):
        request = self.context['request']

        name = user.avatar.name

        if name.startswith('static/'):
            path = '/%s' % name
        else:
            path = '/static/%s' % name
        return request.build_absolute_uri(path)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'password', 'email', 'avatar', 'date_joined']
        # Khong do DL password ra ngoai
        extra_kwargs = {
            'password': {'write_only': 'true'}
        }

    # To Bam Password
    def create(self, validated_data):
        data = validated_data.copy()
        user = User(**data)
        user.set_password(validated_data['password'])
        user.save()

        return user


class CommentSerializer(ModelSerializer):
    creater = UserSerializer()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_date', 'updated_date', 'creater']


class ActionSerializer(ModelSerializer):
    class Meta:
        model = Action
        fields = ['id', 'type', 'created_date']


class RatingSerializer(ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'rate', 'created_date']


class LikeSerializer(ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'active', 'creater', 'lesson']


class LessonViewSerializer(ModelSerializer):
    class Meta:
        model = LessonView
        fields = ['id', 'views', 'lesson']


