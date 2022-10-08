from django.contrib import admin
from django.urls import path, re_path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(prefix='categories', viewset=views.CategoryViewSet)
router.register(prefix='courses', viewset=views.CourseViewSet, basename='course')
router.register(prefix='lessons', viewset=views.LessonViewSet, basename='lesson')
router.register(prefix='users', viewset=views.UserViewSet, basename='user')
router.register(prefix='comments', viewset=views.CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
    path('home/', views.index), 
    path('oauth2-info/', views.AuthInfo.as_view())
]