from rest_framework import serializers
from Dashboard.models import Event, Session, Student, DwellTime, SlideTransition, Shortcut, Quiz, Link, Media


"""
    Serializers for each data model
"""
class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class SlideTransitionSerializer(serializers.ModelSerializer):
    dateTime = serializers.DateTimeField(source='timestamp')

    class Meta:
        model = SlideTransition
        fields = ('type', 'dateTime', 'absolute_url', 'session',
                  'horizontal_transition', 'vertical_transition')


class DwellTimeSerializer(serializers.ModelSerializer):
    dateTime = serializers.DateTimeField(source='timestamp')
    dwellTime = serializers.CharField(source='dwell_time')

    class Meta:
        model = DwellTime
        fields = ('type', 'dateTime', 'absolute_url', 'session', 'dwellTime')


class ShortcutSerializer(serializers.ModelSerializer):
    dateTime = serializers.DateTimeField(source='timestamp')
    shortcut = serializers.CharField(source='short_cut')

    class Meta:
        model = Shortcut
        fields = ('type', 'dateTime', 'absolute_url', 'session', 'shortcut')


class QuizSerializer(serializers.ModelSerializer):
    dateTime = serializers.DateTimeField(source='timestamp')
    quizEvent = serializers.CharField(source='quiz_type')

    class Meta:
        model = Quiz
        fields = ('type', 'dateTime', 'absolute_url', 'session', 'quizEvent', 'percentage')


class LinkSerializer(serializers.ModelSerializer):
    dateTime = serializers.DateTimeField(source='timestamp')
    linkType = serializers.CharField(source='link_type')

    class Meta:
        model = Link
        fields = ('type', 'dateTime', 'absolute_url', 'session', 'linkType', 'href', 'link_text')


class MediaSerializer(serializers.ModelSerializer):
    dateTime = serializers.DateTimeField(source='timestamp')
    mediaType = serializers.CharField(source='media_type')
    mediaEvent = serializers.CharField(source='media_event')

    class Meta:
        model = Media
        fields = ('type', 'dateTime', 'absolute_url', 'session', 'mediaType', 'mediaEvent', 'media_source')