from datetime import datetime
# Create your views here.
from rest_framework.generics import ListAPIView
from rest_framework.parsers import MultiPartParser, FormParser

from project_name.util.custom_response import simple_response
from .serializers import SupportSerializer, FeedbackSerializer
from .models import Support, Feedback


class SupportView(ListAPIView):
    """
    认证类 看情况而定
    """
    # @认证类需补充完整
    # permission_classes =(IsAuthenticatedOrReadOnly,)
    # authentication_classes = (TokenAuthentication,)
    serializer_class = SupportSerializer
    queryset = Support.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            return result
        serializer = self.get_serializer(queryset, many=True)
        # 这里封装了django framework的response
        return simple_response(code=0, message="ok", data=serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return simple_response(code=0, message="ok", data=serializer.data)
        return simple_response(code=10000, message=serializer.errors)

    def put(self, request):
        support_id = request.data.get("id")
        if not support_id:
            return simple_response(code=10000, message="Missing params")
        try:
            support = self.queryset.get(id=support_id)
        except Support.DoesNotExist:
            return simple_response(code=41001, message="this support does not exist")

        serializer = self.serializer_class(support, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return simple_response(code=0, message='ok', data=serializer.data)
        return simple_response(code=10001, message=serializer.errors)

    def delete(self, request):
        help_id = request.data.get("id")
        if not help_id:
            return simple_response(code=10000, message="Missing params")
        try:
            self.queryset.filter(id=help_id).delete()
        except Support.DoesNotExist:
            return simple_response(code=41001, message="this support does not exist")
        return simple_response(code=0, message="ok")


class FeedbackView(ListAPIView):
    """
        认证类 看情况而定
    """
    # @认证类需补充完整
    # permission_classes = (IsAuthenticated,)
    # authentication_classes = (TokenAuthentication, JSONWebTokenAuthentication)
    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()

    def get_parsers(self):
        if self.request.method == "POST":
            return [parser() for parser in [MultiPartParser]]
        else:
            return [parser() for parser in [FormParser]]

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            return result
        serializer = self.get_serializer(queryset, many=True)
        return simple_response(code=0, message="Ok", data=serializer.data)

    def post(self, request):
        image_path = None
        # @图像逻辑需补充完整
        # # 处理图像,一般数据库存储的是图像地址
        # # 下面这个例子使用的是阿里oss服务,根据实际情况更换
        # image_file = request.data.get("file")
        # if image_file:
        #     file_suffix = image_file.name.split(".")[1]
        #     cellphone=request.user.cellphone
        #     timestamp = datetime.now().strftime("%Y%m%d%M%H%S")
        #     image_name = "anxin_feeback_collections/{0}-{1}.{2}".format(cellphone, timestamp,file_suffix)
        #     image = bucket.put_object(image_name, image_file.chunks())
        #     image_path = None
        #     if image.status == 200:
        #         image_path =settings.OSS_DOWNLOAD_URL + image_name
        context = {
            "user": request.user,
            "image": image_path
        }
        serializer = self.serializer_class(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return simple_response(code=0, message="ok", data=serializer.data)
        return simple_response(code=10000, message=serializer.errors)

    def put(self, request):
        feedback_id = request.data.get("id")
        if not feedback_id:
            return simple_response(code=10000, message="Missing params")
        try:
            feedback = self.queryset.get(id=feedback_id)
        except Feedback.DoesNotExist:
            return simple_response(code=41000, message="this feedback does not exist")

        serializer = self.serializer_class(feedback, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return simple_response(code=0, message='ok', data=serializer.data)
        return simple_response(code=10001, message=serializer.errors)

    def delete(self, request):
        feedback = request.data.get("id")
        if not feedback:
            return simple_response(code=10000, message="Missing params")
        try:
            self.queryset.filter(id=feedback).delete()
        except Feedback.DoesNotExist:
            return simple_response(code=41000, message="this feedback does not exist")
        return simple_response(code=0, message="ok")