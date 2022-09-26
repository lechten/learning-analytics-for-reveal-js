from django.contrib import admin

# Register your models here.
from .models import Student, Module, TimePeriod, Course, SlideSet, Session

# admin.site.register(Student)
admin.site.register(Module)
admin.site.register(TimePeriod)
admin.site.register(Course)
admin.site.register(SlideSet)
admin.site.register(Session)
