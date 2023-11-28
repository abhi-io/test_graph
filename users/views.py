# -*- coding: utf-8 -*-
import itertools
import uuid
from datetime import datetime
from datetime import timedelta
from threading import Thread

from rest_framework.authentication import SessionAuthentication

from authentication.authentication import JwtTokensAuthentication
from basicauth import decode
from basicauth import encode
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, DateField
from django.db.models.functions import Cast
from django.utils import timezone
from django.views.decorators.cache import cache_control
from django.utils.decorators import method_decorator

from core_viewsets.custom_viewsets import CreateViewSet, ListCreateViewSet, ListViewSet, FetchUpdateViewSets
from jwt_utils.jwt_generator import jwt_generator
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from users.models import LoginLog,Token 
from users.models import UserNotification
from utils.datetime_utils import calculate_time_difference
from utils.datetime_utils import convert_str_date
from utils.datetime_utils import convert_to_str_time
from utils.mail_utils import send_email
from utils.message_utils import get_message
# from utils.otp_utils import send_verification
from utils.pagination import CustomPageNumberPagination
# from utils.upload import upload_file_to_s3
from utils.validation_utils import validate_email, validate_phone
from utils.validation_utils import validate_null_or_empty
from utils.validation_utils import validate_password

from .serializers import EmptySerializer, SharedNoteSerializer
from .serializers import RegisterSerializer, LoginSerializer
from .serializers import ResetPasswordSerializer
from .serializers import UserNotesSerializer
from .serializers import UserNotificationsSerializer
from .serializers import UserSerializer
from video_library.settings import logger, RESET_PASSWORD_LINK, JWT_SECRET, TOKEN_EXPIRY, REFRESH_TOKEN_EXPIRY, \
    BASIC_TEMPLATE_IMAGE_URL, BASIC_IMAGE_URL


# Create your views here.


class RegisterViewSet(CreateViewSet):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = RegisterSerializer
    queryset = get_user_model().objects.all()

    def create(self, request, *args, **kwargs):

        email = request.data.get("email")
        password = request.data.get("password", None)
        phone_number = request.data.get("phone_number")

        # display what are the fields which tent to empty.
        validations = []
        validations = validate_null_or_empty(email, 307, validations)
        validations = validate_null_or_empty(password, 305, validations)
        validations = validate_null_or_empty(phone_number, 301, validations)

        if len(validations) > 0:
            resp = {}
            resp["code"] = 600
            resp["validations"] = validations
            return Response(resp, status=status.HTTP_412_PRECONDITION_FAILED)

        if not validate_email(email):
            return Response(
                {"code": 604, "message": get_message(604)},
                status=status.HTTP_412_PRECONDITION_FAILED,
            )
        if not validate_phone(phone_number):
            return Response({"code": 706, "message": get_message(706)})

        if not validate_password(password):
            return Response(
                {"code": 618, "message": get_message(618)},
                status=status.HTTP_412_PRECONDITION_FAILED,
            )

        user_obj = get_user_model().objects.filter(email=email).exists()
        if user_obj:
            return Response(
                {"code": 621, "message": get_message(621)},
                status=status.HTTP_412_PRECONDITION_FAILED,
            )

        user = get_user_model().objects.create_user(request.data)

        return Response(
            {"code": 200, "message": get_message(200), "user_id": user._get_pk_val()}
        )


class LoginViewSet(CreateViewSet):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = LoginSerializer
    
    def create(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")
        # display what are the fields which tent to empty.
        validations = []
        validations = validate_null_or_empty(email, 307, validations)
        validations = validate_null_or_empty(password, 305, validations)

        if len(validations) > 0:
            resp = {}
            resp["code"] = 600
            resp["validations"] = validations
            return Response(resp, status=status.HTTP_412_PRECONDITION_FAILED)
        try:
            user_obj = get_user_model().objects.get(email=email)
            valid = user_obj.check_password(password)

            if not valid:
                # logger.error({"code": 503, "message": get_message(503)})
                return Response(
                    {"code": 503, "message": get_message(503)},
                    status.HTTP_412_PRECONDITION_FAILED,
                )
            access_token, actual_exp = jwt_generator(
                user_obj.id,
                JWT_SECRET,
                TOKEN_EXPIRY,
                "access",
                user_obj.is_superuser,
            )
            refresh_token, actual_exp_ref = jwt_generator(
                user_obj.id,
                JWT_SECRET,
                REFRESH_TOKEN_EXPIRY,
                "refresh",
                user_obj.is_superuser
            )
            Token.objects.filter(user_id=user_obj).update(is_expired=1)

            Token.objects.update_or_create(
                user_id=user_obj,
                access_token=access_token,
                refresh_token=refresh_token,
                defaults={"updated_at": timezone.now()},
            )
            log_obj, updated_flag = LoginLog.objects.update_or_create(
                user_id=user_obj,
                defaults={
                    "updated_at": timezone.now(),
                    "last_logged_in": timezone.now(),
                },
            )
            log_obj.login_count = log_obj.login_count + 1
            log_obj.save()
            user_obj.last_login = timezone.now()
            check_if_Admin = get_user_model().objects.filter(email=email, is_superuser=True, is_active=True)
            message = get_message(200)
            if check_if_Admin: 
                message = "Ok, With great power comes great responsibility."
            return Response(
                {
                    "code": 200, 
                    "message": message,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user_id": user_obj.pk,
                    "name": user_obj.first_name,
                    "email": user_obj.email,
                    "last_login": user_obj.last_login,
                    "expires_at": actual_exp
                }
            )

        except ObjectDoesNotExist as ex:
            logger.error(ex)
            return Response(
                {"code": 204, "message": get_message(204)},
                status.HTTP_400_BAD_REQUEST,
            )


class UserViewSet(FetchUpdateViewSets):
    authentication_classes = [JwtTokensAuthentication, SessionAuthentication]
    pagination_class = CustomPageNumberPagination
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all().exclude(is_superuser=1)

    def list(self, request, *args, **kwargs):
        email = request.query_params.get("email", None)
        user_id = request.user.get("user_id")
        queryset = self.get_queryset().exclude(pk=user_id)
        if email:
            queryset = queryset.filter(email__icontains=email)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        user_id = request.query_params.get("id")
        try:
            instance = get_user_model().objects.get(pk=user_id, is_verified=True)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        except ObjectDoesNotExist as ex:
            logger.error(ex)
            return Response(
                {"code": 400, "message": get_message(400)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as ex:
            logger.error(ex)
            return Response(
                {"code": 114, "message": get_message(114)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, *args, **kwargs):
        user_id = request.user.get("user_id")
        user_image = request.data.get("image_url")
        image_name = request.data.get("image_name", "")
        try:
            user_obj = get_user_model().objects.get(pk=user_id, is_verified=True)
            user_obj.image_url = user_image
            user_obj.image_name = image_name
            user_obj.updated_at = timezone.now()
            user_obj.save()

            return Response({"code": 200, "message": get_message(200)})
        except Exception as ex:
            logger.error(ex)
            return Response(
                {"code": 114, "message": get_message(114)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LogoutViewSet(CreateViewSet):
    permission_classes = ()
    authentication_classes = [JwtTokensAuthentication]
    serializer_class = EmptySerializer

    def create(self, request, *args, **kwargs):
        user_id = request.user.get("user_id")
        token_id = request.headers.get("Authorization", "")
        try:
            get_user_model().objects.get(pk=user_id, is_verified=True)
        except ObjectDoesNotExist as ex:
            logger.error(ex)
            return Response(
                {"code": 204, "message": get_message(204)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token_obj = Token.objects.get(access_token=token_id, user_id=user_id)
            token_obj.is_expired = 1
            token_obj.save()
            return Response({"code": 200, "message": get_message(200)})
        except Exception as ex:
            logger.error(ex)
            return Response(
                {"code": 114, "message": get_message(114)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ForgotPasswordViewSet(CreateViewSet):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = EmptySerializer

    def create(self, request, *args, **kwargs):

        email_id = request.data.get("email")
        try:
            user_obj = get_user_model().objects.get(email=email_id, is_verified=True)
        except ObjectDoesNotExist as ex:
            logger.error(ex)
            return Response(
                {"code": 204, "message": get_message(204)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            current_time = timezone.now()
            exp_time = current_time + timedelta(milliseconds=1800000)
            exp_at = exp_time.strftime("%Y-%m-%d %H:%M:%S")

            token_url = encode(user_obj.email, exp_at)
            token = token_url.split("Basic ")
            reset_url = RESET_PASSWORD_LINK + "token=" + str(token[1])

            messages = {
                "first_name": user_obj.first_name,
                "last_name": user_obj.last_name,
                "name_email": user_obj.email,
                "name": user_obj.email,
                "image_logo": BASIC_TEMPLATE_IMAGE_URL,
                "font_path": BASIC_IMAGE_URL,
                "html": "users/forgot_password_email.html",
                "reset_url": reset_url,
                "subject": "Reset Password Link",
            }
            # send_email(email_id, messages)
            mail_thread = Thread(target=send_email, args=(email_id, messages))
            mail_thread.start()
            return Response(
                {
                    "code": 200,
                    "message": "A password reset mail is send to the registered email",
                }
            )

        except Exception as ex:
            logger.error(ex)
            return Response(
                {"code": 114, "message": get_message(114)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ResetPasswordViewSet(CreateViewSet):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = ResetPasswordSerializer

    def create(self, request, *args, **kwargs):
        password = request.data.get("password")
        token = request.data.get("token")
        try:
            token = token.replace("%20", "")
            token = "Basic " + token
            email, exp_at = decode(token)
        except Exception as ex:
            logger.error(ex)
            return Response(
                {"code": 114, "message": get_message(114)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:

            user_obj = get_user_model().objects.get(email=email, is_verified=True)
        except ObjectDoesNotExist as ex:
            logger.error(ex)
            return Response(
                {"code": 204, "message": get_message(204)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:

            current_time = timezone.now()
            time_difference = calculate_time_difference(
                exp_at, convert_to_str_time(current_time)
            )

            if time_difference < 0:
                return Response(
                    {"code": 206, "message": get_message(206)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not validate_password(password):
                return Response({"code": 618, "message": get_message(618)})

            valid = user_obj.check_password(password)

            if valid:
                # logger.error({"code": 503, "message": get_message(503)})
                return Response(
                    {"code": 311, "message": get_message(311)},
                    status.HTTP_412_PRECONDITION_FAILED,
                )

            user_obj.set_password(password)
            user_obj.updated_at = timezone.now()
            user_obj.save()
            return Response({"code": 200, "message": get_message(200)})
        except Exception as ex:
            logger.error(ex)
            return Response(
                {"code": 114, "message": get_message(114)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ChangePasswordViewSet(CreateViewSet):
    permission_classes = ()
    authentication_classes = [
        JwtTokensAuthentication,
    ]
    serializer_class = EmptySerializer

    def create(self, request, *args, **kwargs):
        current_password = request.data.get("current_password", "")
        new_password = request.data.get("new_password", "")
        user_id = request.user.get("user_id")
        try:
            user_obj = get_user_model().objects.get(id=user_id, is_verified=True)
        except ObjectDoesNotExist as e:
            logger.error(e)
            return Response(
                {"code": 204, "message": get_message(204)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            if current_password == new_password:
                return Response(
                    {"code": 311, "message": get_message(311)},
                    status.HTTP_412_PRECONDITION_FAILED,
                )

            valid = user_obj.check_password(current_password)
            if not valid:
                return Response(
                    {"code": 619, "message": get_message(619)},
                    status=status.HTTP_412_PRECONDITION_FAILED,
                )

            if not validate_password(new_password):
                return Response(
                    {"code": 618, "message": get_message(618)},
                    status=status.HTTP_412_PRECONDITION_FAILED,
                )

            user_obj.set_password(new_password)
            user_obj.updated_at = timezone.now()
            user_obj.save()

            return Response({"code": 200, "message": get_message(200)})
        except Exception as e:
            logger.error(e)
            print(e)
            return Response(
                {"code": 114, "message": get_message(114)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UploadImageViewSet(CreateViewSet):
    permission_classes = ()
    serializer_class = EmptySerializer
    authentication_classes = [
        JwtTokensAuthentication,
    ]

    def get_queryset(self):
        pass

    def create(self, request, *args, **kwargs):
        try:
            image = request.data.get("name")
            directory_name = "user_images/"
            image_ext = str(image).split(".")[-1]
            image_name = uuid.uuid4().hex
            # name = directory_name + image_name + "." + image_ext
            # path = default_storage.save(name, ContentFile(image.read()))
            # os.path.join(settings.MEDIA_ROOT, path)
            # return Response({"code": 200, "message": get_message(200), "image_url": path})
            s3_image_name = directory_name + image_name + "." + image_ext
            # path = default_storage.save(s3_image_name, ContentFile(image.read()))
            # local_path = os.path.join(settings.MEDIA_ROOT, path)
            upload_url = upload_file_to_s3(s3_image_name, image)
            # upload_url = upload_file_to_s3_in_parts(s3_image_name, local_path)
            logger.info(upload_url)
            if upload_url:
                # os.remove(local_path)
                return Response(
                    {
                        "code": 200,
                        "message": get_message(200),
                        "image_url": upload_url,
                        "image_name": s3_image_name,
                    }
                )
            else:
                return Response(
                    {"code": 313, "message": get_message(313)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            logger.error(e)
            return Response(
                {"code": 114, "message": get_message(114)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AccessCheckViewSet(ListViewSet):
    permission_classes = ()
    serializer_class = UserNotificationsSerializer
    pagination_class = CustomPageNumberPagination
    authentication_classes = [
        JwtTokensAuthentication,
    ]
    # @cache_control(max_age=0)
    def list(self, request, *args, **kwargs):
        return Response(
            {"code": 200, "message": get_message(200),},
            status=status.HTTP_200_OK,
        )














class NotificationsCountViewSet(ListViewSet):
    permission_classes = ()
    serializer_class = UserNotificationsSerializer
    pagination_class = CustomPageNumberPagination
    authentication_classes = [
        JwtTokensAuthentication,
    ]

    @cache_control(max_age=0)
    def list(self, request, *args, **kwargs):
        user_id = self.request.user.get("user_id")
        try:
            get_user_model().objects.get(id=user_id, is_verified=True)
        except ObjectDoesNotExist as e:
            logger.error(e)
            return Response(
                {"code": 204, "message": get_message(204)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        queryset = UserNotification.objects.filter(user_id=user_id, is_read=False)
        return Response(
            {"code": 200, "message": get_message(200), "count": queryset.count()},
            status=status.HTTP_200_OK,
        )


class UserNotificationsViewSet(ListViewSet):
    permission_classes = ()
    serializer_class = UserNotificationsSerializer
    pagination_class = CustomPageNumberPagination
    authentication_classes = [
        JwtTokensAuthentication,
    ]

    @cache_control(max_age=0)
    def list(self, request, *args, **kwargs):
        user_id = self.request.user.get("user_id")
        start_date = self.request.query_params.get("from", None)
        end_date = self.request.query_params.get("to", None)
        notification_text = self.request.query_params.get("notification_text", None)
        try:
            get_user_model().objects.get(id=user_id, is_verified=True)
        except ObjectDoesNotExist as e:
            logger.error(e)
            return Response(
                {"code": 204, "message": get_message(204)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = UserNotification.objects.filter(user_id=user_id).order_by(
            "-created_at"
        )
        queryset.update(is_read=True)

        if notification_text:
            queryset = queryset.filter(notification_text__icontains=notification_text)

        if start_date:
            min_time = datetime.min.time()
            start_date = datetime.combine(convert_str_date(start_date), min_time)
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            max_time = datetime.max.time()
            end_date = datetime.combine(convert_str_date(end_date), max_time)
            queryset = queryset.filter(created_at__lte=end_date)

        queryset = queryset.annotate(search_date=Cast("created_at", DateField()))

        queryset = (
            queryset.order_by("-created_at")
            .values("search_date", "notification_text", "is_read", "id", "created_at")
            .distinct()
        )
        page = self.paginate_queryset(queryset)
        result = []
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            for search_date, search_list in itertools.groupby(
                list(serializer.data), key=lambda x: x["search_date"]
            ):
                search_data = list(search_list)
                search_data = sorted(
                    search_data, key=lambda i: dict(i)["created_at"], reverse=True
                )
                result.append({"date": search_date, "message": search_data})

            return Response(
                {
                    **dict(self.get_paginated_response(result).data),
                    **{"notification_text": notification_text},
                }
            )
            # return dict(self.get_paginated_response(result))

        serializer = self.get_serializer(queryset, many=True)
        for search_date, search_list in itertools.groupby(
            list(serializer.data), key=lambda x: x["search_date"]
        ):
            search_data = list(search_list)
            search_data = sorted(
                search_data, key=lambda i: dict(i)["created_at"], reverse=True
            )
            result.append({"date": search_date, "message": search_data})
        return Response(
            {
                "count": len(result),
                "results": result,
                "notification_text": notification_text,
            }
        )

        # grouped = itertools.groupby(
        #     queryset, lambda record: record.created_at.strftime("%Y-%m-%d")
        # )
        # group_count = [(day, len(list(total_row))) for day, total_row in grouped]
        # temp_dict = {}
        # temp_list = []
        # row_lst = []
        # row_dict = {}
        # if len(queryset) > 0:
        #     cnt = 0
        #     for date in range(len(group_count)):
        #         temp_dict["date"] = datetime.strftime(
        #             queryset[cnt].created_at, "%Y-%m-%d"
        #         )
        #         for message in range(int(group_count[date][1])):
        #             row_dict["notification_text"] = queryset[cnt].notification_text
        #             row_dict["is_read"] = queryset[cnt].is_read
        #             row_dict["created_at"] = datetime.strftime(
        #                 queryset[cnt].created_at, "%Y-%m-%d %H:%M:%S"
        #             )
        #             row_dict["id"] = queryset[cnt].id
        #             row_lst.append(row_dict)
        #             row_dict = {}
        #             cnt += 1
        #         temp_dict["message"] = row_lst
        #         temp_list.append(temp_dict)
        #         temp_dict = {}
        #         row_lst = []
        #
        #     return Response(
        #         {
        #             "code": 200,
        #             "message": get_message(200),
        #             "results": {"notifications": temp_list},
        #         },
        #         status=status.HTTP_200_OK,
        #     )
        # else:
        #     return Response(
        #         {"code": 204, "message": get_message(204)},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )


class NotificationsViewSet(CreateViewSet):
    permission_classes = ()
    serializer_class = UserNotificationsSerializer
    pagination_class = CustomPageNumberPagination
    authentication_classes = ()

    def create(self, request, *args, **kwargs):
        notifications_list = request.data.get("notifications")
        notifications_data = []

        for notifications in notifications_list:
            try:
                user_obj = get_user_model().objects.get(
                    id=notifications.get("user_id", None), is_verified=True
                )
            except ObjectDoesNotExist:
                user_obj = None

            notifications_data.append(
                UserNotification(
                    user_id=user_obj,
                    notification_text=notifications.get("notification_text", ""),
                )
            )

        try:
            UserNotification.objects.bulk_create(notifications_data)
            return Response({"code": 200, "message": get_message(200)})

        except Exception as e:
            logger.error(e)
            return Response(
                {"code": 114, "message": get_message(114)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

