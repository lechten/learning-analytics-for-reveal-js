from django.db import models


class Module(models.Model):
    name = models.CharField(max_length=100, default='default_Module')
    description = models.CharField(max_length=500, default='', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class TimePeriod(models.Model):
    name = models.CharField(max_length=100, default='default_TimePeriod')
    description = models.CharField(max_length=500, default='', blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=100, default='default_course')
    description = models.CharField(max_length=500, default='',
                                   blank=True)
    module = models.ForeignKey(Module,
                               on_delete=models.CASCADE)
    time_period = models.ForeignKey(TimePeriod,
                                    on_delete=models.CASCADE)
    participants = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class SlideSet(models.Model):
    base_url = models.CharField(primary_key=True, max_length=500)
    name = models.CharField(max_length=100, default='default_name')
    description = models.CharField(max_length=500, default='', blank=True)
    courses = models.ManyToManyField(Course, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.base_url

    def __str__(self):
        return self.name + " (" + self.base_url + ")"


class Student(models.Model):
    user_token = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.user_token


class Session(models.Model):
    session_token = models.UUIDField(primary_key=True)
    slide_set = models.ForeignKey(SlideSet, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    total_slides = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.session_token


class Event(models.Model):
    type = models.CharField(max_length=500, default='default_event')
    timestamp = models.DateTimeField()
    absolute_url = models.CharField(max_length=500)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name


class SlideTransition(Event):
    horizontal_transition = models.IntegerField(null=True)
    vertical_transition = models.IntegerField(null=True)

    def __unicode__(self):
        return self.name


class DwellTime(Event):
    dwell_time = models.TimeField()

    def __unicode__(self):
        return self.name


class Quiz(Event):
    quiz_type = models.CharField(max_length=500, default='default_quiz_event')
    percentage = models.IntegerField(null=True)

    def __unicode__(self):
        return self.name


class Link(Event):
    link_type = models.CharField(max_length=500, default='default_link_event')
    href = models.CharField(max_length=500, null=True)
    link_text = models.CharField(max_length=500, null=True)

    def __unicode__(self):
        return self.name


class Media(Event):
    media_type = models.CharField(max_length=500, default='default_media_type')
    media_event = models.CharField(max_length=500, default='default_media_event')
    media_source = models.CharField(max_length=500, null=True)

    def __unicode__(self):
        return self.name


class Shortcut(Event):
    short_cut = models.CharField(max_length=100, default='default_shortcut')

    def __unicode__(self):
        return self.name
