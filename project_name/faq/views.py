from datetime import datetime
# Create your views here.
from rest_framework import mixins
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from project_name.core import error_code
from project_name.core.authentication import TokenAuthentication
from project_name.utils.custom_exception import ServerError
from project_name.utils.custom_pagination import CustomPagination
from project_name.utils.custom_response import simple_response
from .serializers import SupportSerializer, FeedbackSerializer
from .models import Support, Feedback


class SupportsView(ListCreateAPIView):
    """
    认证类 看情况而定
    """
    # @认证类需补充完整
    permission_classes = (AllowAny,)
    serializer_class = SupportSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return Support.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return simple_response(code=error_code.SUCCESS,
                               message='successfully created support')


class SupportView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    authentication_classes = (TokenAuthentication,)
    serializer_class = SupportSerializer

    def get_object(self):
        try:
            instance = Support.objects.get(id=self.kwargs['support_id'])
        except Support.DoesNotExist:
            raise ServerError(*error_code.ERR_SUPPORT_NOT_EXIST)
        return instance

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return simple_response(code=error_code.SUCCESS,
                               message="update support_id=%s ok" %(instance.id), data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return simple_response(code=error_code.SUCCESS,
                               message="delete support_id=%s ok" % (instance.id))

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return simple_response(code=error_code.SUCCESS,
                               message="get support_id=%s ok" % (instance.id), data=serializer.data)


class FeedbacksView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, JSONWebTokenAuthentication)
    pagination_class = CustomPagination
    serializer_class = FeedbackSerializer

    # def get_parsers(self):
    #     if self.request.method == "POST":
    #         return [parser() for parser in [MultiPartParser]]
    #     else:
    #         return [parser() for parser in [FormParser]]

    def get_queryset(self):
        # 条件筛选在这里做
        return Feedback.objects.all()

    def create(self, request, *args, **kwargs):
        image_url = None
        image = self.request.data.get('file')
        # 将文件存储并记录访问地址
        #
        # if image:
        #     file_suffix = image.name.split(".")[1]
        #     cellphone=request.user.cellphone
        #     timestamp = datetime.now().strftime("%Y%m%d%M%H%S")
        #     image_name = "anxin_feeback_collections/{0}-{1}.{2}".format(cellphone, timestamp,file_suffix)
        #     image = bucket.put_object(image_name, image.chunks())
        #     if image.status == 200:
        #         image_url =settings.OSS_DOWNLOAD_URL + image_name

        context = {
            "user": self.request.user,
            "image": image_url
        }
        serializer = self.get_serializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return simple_response(code=error_code.SUCCESS,
                               message='successfully created support')


class FeedbackView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    serializer_class = FeedbackSerializer

    def get_object(self):
        #
        try:
            instance = Feedback.objects.get(id=self.kwargs['feedback_id'])
        except Feedback.DoesNotExist:
            raise ServerError(*error_code.ERR_FEEDBACK_NOT_EXIST)
        return instance

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return simple_response(code=error_code.SUCCESS,
                               message="update feedback_id=%s ok" % instance.id, data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return simple_response(code=error_code.SUCCESS,
                               message="delete feedback_id=%s ok" % instance.id)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return simple_response(code=error_code.SUCCESS,
                               message="get feedback_id=%s ok" % instance.id, data=serializer.data)