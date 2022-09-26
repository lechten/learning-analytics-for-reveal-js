from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import EventSerializer, StudentSerializer, SessionSerializer, DwellTimeSerializer, \
    SlideTransitionSerializer, ShortcutSerializer, QuizSerializer, LinkSerializer, MediaSerializer
from Dashboard.models import Event, Student, Session, SlideSet
import logging
import uuid
import json
from urllib.parse import urlsplit, urlunsplit


"""
    Validate UUID format
"""
def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


"""
    Validate user token exists in DB
"""
def validate_user_token(token):
    all_tokens = Student.objects.all()

    if is_valid_uuid(token) and all_tokens.filter(pk=token).exists():
        return token
    else:
        return create_new_user_token()


"""
    Validate session token exists and is related to given user token
"""
def validate_session_token(token, user_token="", absolute_url="", total_slides=0):
    all_tokens = Session.objects.all()
    split_url = urlsplit(absolute_url)
    base_url = split_url.scheme + "://" + split_url.netloc + split_url.path
    if is_valid_uuid(token) and all_tokens.filter(pk=token, slide_set_id=base_url, total_slides=total_slides).exists():
        return token, all_tokens.filter(pk=token).first().student.user_token
    else:
        return create_new_session_token(user_token, absolute_url=absolute_url, total_slides=total_slides)


"""
    Creates new session token (and user token if not provided)
"""
def create_new_session_token(user_token="", absolute_url="", total_slides=0):
    if user_token == "" or not is_valid_uuid(user_token):
        user_token = create_new_user_token()

    all_session_tokens = Session.objects.all()
    session_token = uuid.uuid4()
    while all_session_tokens.filter(pk=session_token).exists():
        session_token = uuid.uuid4()

    split_url = urlsplit(absolute_url)
    base_url = split_url.scheme + "://" + split_url.netloc + split_url.path
    slide_set, created = SlideSet.objects.get_or_create(base_url=base_url)

    serializer = SessionSerializer(data={"session_token": session_token, "student": user_token,
                                         "slide_set": slide_set.pk,
                                         "total_slides": total_slides})

    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return session_token, user_token
    else:
        return serializer.errors


"""
    Creates new user token
"""
def create_new_user_token():
    all_user_tokens = Student.objects.all()

    user_token = uuid.uuid4()
    while all_user_tokens.filter(pk=user_token).exists():
        user_token = uuid.uuid4()

    serializer = StudentSerializer(data={"user_token": user_token})
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return user_token
    else:
        return False


"""
    API endpoint to validate user token
"""
class UserTokenValidationViews(APIView):
    def post(self, request):
        try:
            user_token = validate_user_token(token=request.data["user_token"])
            return Response({"status": "success", "user_token": user_token}, status=status.HTTP_200_OK)
        except Exception as ex:
            logging.warning(ex)
            return Response({"status": "error", "message": "Unable to validate user token"},
                            status=status.HTTP_400_BAD_REQUEST)


"""
    API endpoint to create user token
"""
class UserTokenCreationViews(APIView):
    def post(self, request):
        try:
            user_token = create_new_user_token()
            return Response({"status": "success", "user_token": user_token}, status=status.HTTP_200_OK)
        except Exception as ex:
            logging.warning(ex)
            return Response({"status": "error", "message": "Unable to create new user token"},
                            status=status.HTTP_400_BAD_REQUEST)


"""
    API endpoint to validate session token
"""
class SessionTokenValidationViews(APIView):
    def post(self, request):
        try:
            if "user_token" in request.data:
                session_token, user_token = validate_session_token(token=request.data["session_token"],
                                                                   user_token=request.data["user_token"],
                                                                   absolute_url=request.data["absolute_url"],
                                                                   total_slides=request.data["total_slides"])
            else:
                session_token, user_token = validate_session_token(token=request.data["session_token"],
                                                                   absolute_url=request.data["absolute_url"],
                                                                   total_slides=request.data["total_slides"])
            return Response({"status": "success", "user_token": user_token, "session_token": session_token},
                            status=status.HTTP_200_OK)
        except Exception as ex:
            logging.warning(ex)
            return Response({"status": "error", "message": "Unable to validate sessions token"},
                            status=status.HTTP_400_BAD_REQUEST)


"""
    API endpoint to create session token
"""
class SessionTokenCreationViews(APIView):
    def post(self, request):
        try:
            if "user_token" in request.data:
                session_token, user_token = create_new_session_token(user_token=request.data["user_token"],
                                                                     absolute_url=request.data["absolute_url"],
                                                                     total_slides=request.data["total_slides"])
            else:
                session_token, user_token = create_new_session_token(absolute_url=request.data["absolute_url"],
                                                                     total_slides=request.data["total_slides"])


            return Response({"status": "success", "user_token": user_token, "session_token": session_token},
                            status=status.HTTP_200_OK)
        except Exception as ex:
            logging.warning(ex)
            return Response({"status": "error", "message": "Unable to create new session token"},
                            status=status.HTTP_400_BAD_REQUEST)


"""
    Tracking API endpoint saving events to database
"""
class EventViews(APIView):
    def post(self, request):
        try:
            # transform JSON to dictionaries
            data_json = json.loads(request.data["data"])
            events = data_json["timeline"]

            # iterate over all given events
            for event in events:
                # generate specialization
                if event["type"] == "slideTransition":
                    event["session"] = data_json["sessionToken"]
                    event["horizontal_transition"] = \
                        event["transitionDetails"]["horizontal"]
                    event["vertical_transition"] = \
                        event["transitionDetails"]["vertical"]

                    serializer = SlideTransitionSerializer(data=event)

                # generate specialization
                elif event["type"] == "dwellTimePerSlide":
                    event["session"] = data_json["sessionToken"]

                    serializer = DwellTimeSerializer(data=event)

                elif event["type"] == "shortcut":
                    event["session"] = data_json["sessionToken"]

                    serializer = ShortcutSerializer(data=event)

                elif event["type"] == "quiz":
                    if "score" in event:
                        quiz_score = int(event["score"] / event["metadata"]["numberOfQuestions"]*100)
                    else:
                        quiz_score = 0

                    event["session"] = data_json["sessionToken"]
                    event["percentage"] = quiz_score

                    serializer = QuizSerializer(data=event)

                elif event["type"] == "link":

                    event["session"] = data_json["sessionToken"]
                    event["href"] = event["metadata"]["href"]
                    event["link_text"] = event["metadata"]["linkText"]

                    serializer = LinkSerializer(data=event)

                elif event["type"] == "media":
                    if "finished" in event and event["finished"]:
                        event["mediaEvent"] = "finished"
                    event["session"] = data_json["sessionToken"]
                    event["media_source"] = event["metadata"]["mediaSource"]

                    serializer = MediaSerializer(data=event)

                if serializer.is_valid(raise_exception=True):
                    serializer.save()

            return Response({"status": "success"}, status=status.HTTP_200_OK)
        except Exception as x:
            logging.error(x)
            return Response({"status": "error"}, status=status.HTTP_400_BAD_REQUEST)
