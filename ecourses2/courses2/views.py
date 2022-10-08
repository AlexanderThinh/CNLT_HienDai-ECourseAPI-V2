from django.shortcuts import render
from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, generics, status, permissions, serializers
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.conf import settings
from django.db.models import F

from .models import *
from .serializers import *
from .paginations import *


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser, ]

    @action(methods=['get'], detail=False, url_path='current-user')
    def get_current_user(self, request):
        return Response(self.serializer_class(request.user, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    def get_permissions(self):
        if self.action == 'get_current_user':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class CategoryViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CourseViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    # queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CoursePagination

    def get_queryset(self):
        courses = Course.objects.filter(active=True)

        q = self.request.query_params.get('q')
        if q:
            courses = courses.filter(name__icontains=q)

        cate_id = self.request.query_params.get('category_id')
        if cate_id:
            courses = courses.filter(category_id=cate_id)

        return courses


    @action(methods=['get'], detail=True, url_path='lessons')
    def get_lessons(self, request, pk):
        course = Course.objects.get(pk=pk)
        lessons = course.lessons.filter(active=True)

        q = self.request.query_params.get('q')
        if q:
            lessons = lessons.filter(name__icontains=q)

        return Response(data=LessonSerializer(lessons, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)

class LessonViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = Lesson.objects.filter(active=True)
    serializer_class = LessonDetailSerializer

    @action(methods=['get'], detail=True, url_path='comments')
    def get_comments(self, request, pk):
        lesson = Lesson.objects.get(pk=pk)
        comment = lesson.comments.select_related('creater').all()

        return Response(data=CommentSerializer(comment, many=True).data,
                        status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='tags')
    def add_tag(self, request, pk):
        lessons = Lesson.objects.get(pk=pk)
        tags = self.request.data.get('tags')
        if tags:
            for tag in tags:
                t, created = Tag.objects.get_or_create(name=tag)
                lessons.tags.add(t)
            lessons.save()

            return Response(data=self.serializer_class(lessons).data,
                            status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(methods=['post'], detail=True, url_path='add-comments')
    def add_comments(self, request, pk):
        lesson = Lesson.objects.get(pk=pk)
        content = request.data.get('content')
        if content:
            c = Comment.objects.create(content=content, lesson=self.get_object(),
                                       creater=request.user)
            lesson.comments.add(c)
            lesson.save()

            return Response(data=CommentSerializer(c).data,
                            status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    # @action(methods=['post'], detail=True, url_path='like')
    # def take_action(self, request, pk):
    #     try:
    #         action_type = int(request.data['type'])
    #     except IndexError | ValueError:
    #         return Response(status=status.HTTP_400_BAD_REQUEST)
    #     else:
    #         action = Action.objects.create(type=action_type, lesson=self.get_object(),
    #                                        creater=request.user)
    #
    #         return Response(data=ActionSerializer(action).data,
    #                         status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='like')
    def like(self, request, pk):
        lesson = Lesson.objects.get(pk=pk)
        user = request.user

        l, created = Like.objects.get_or_create(lesson=lesson, creater=user)
        l.active = not l.active
        l.save()

        return Response(data=LikeSerializer(l).data,
                        status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=True, url_path='rating')
    def rate(self, request, pk):
        # try:
        #     rating = int(request.data['rating'])
        # except IndexError | ValueError:
        #     return Response(status=status.HTTP_400_BAD_REQUEST)
        # else:
        #     r = Rating.objects.create(rate=rating, lesson=self.get_object(),
        #                                    creater=request.user)
        #
        #     return Response(data=RatingSerializer(r).data,
        #                     status=status.HTTP_200_OK)

        if 'rating' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        lesson = self.get_object()
        user = request.user

        r, _ = Rating.objects.get_or_create(lesson=lesson, creater=user)
        r.rate = int(request.data.get('rating'))
        r.save()

        return Response(data=RatingSerializer(r).data,
                        status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=True, url_path='view')
    def increase_view(self, request, pk):
        v, created = LessonView.objects.get_or_create(lesson=self.get_object())
        v.views = F('views') + 1
        v.save()
        v.refresh_from_db()

        return Response(data=LessonViewSerializer(v).data, status=status.HTTP_200_OK)

    def get_permissions(self):
        if self.action in ['add_comments', 'rate']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class CommentViewSet(viewsets.ViewSet, generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        if request.user == self.get_object().creater:
            return super().destroy(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def partial_update(self, request, *args, **kwargs):
        if request.user == self.get_object().creater:
            return super().partial_update(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)


class AuthInfo(APIView):
    def get(self, request):
        return Response(settings.OAUTH2_INFO, status=status.HTTP_200_OK)


def index(request):
    return HttpResponse('Welcome back Alexander Thinh')
