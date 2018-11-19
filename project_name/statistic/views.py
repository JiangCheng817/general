from datetime import datetime, timedelta
# Create your views here.
from rest_framework.viewsets import ModelViewSet

from project_name.util.custom_response import simple_response
from .import serializers


# @修改为具体名字如，RevenueStatisticView/
class StatisticView(ModelViewSet):
    """
    # 统计通用接口
    """
    # @ 认证部分 根据实际情况来
    # authentication_classes = (JSONWebTokenAuthentication, TokenAuthentication)
    # permission_classes = (IsAuthenticated,)
    serializer_class = serializers.CSerializers

    def get_object(self):
        instance = None
        # 可选参数 ： 类型,比如
        type = self.request.query_params.get("type", None)
        # @ 根据实际情况筛选model
        # 一種方案是將這部分邏輯添加get_object（）裡面
        # if type == 'A':
        #     instance = A.objects.filter()
        # elif type == 'B':
        #     queryset = B.objects.filter()
        # elif type == 'C':
        #     queryset = C.objects.filter()
        # else:
        #     raise ServerError(code=10000, message="missing type params")
        return instance


    def get_queryset(self):
        # @一些默认选项,从7天前到现在
        _INITIAL_DAY = 7
        c_time = datetime.now()

        # 基本参数：初始日期 结束日期
        end_date = self.request.query_params.get("end_date", c_time)
        start_date = self.request.query_params.get("start_date", c_time - timedelta(days=_INITIAL_DAY))

        # 可选参数 ： 年,月,日
        period = self.request.query_params.get("period")

        instance = self.get_object()

        # # @可选参数：device_id
        device_id = self.request.query_params.get("device_id", None)

        # 判断是终端还是web调用
        # owner = self.request.user
        # user = User.objects.filter(username=owner)
        # queryset=instance.filter(create_time__gte=start_date,
        #                          create_time__lte=end_date)


        # if user:
        #     # web端调用
        #     if device_id is not None:
        #         return queryset.filter(device_id=device_id)
        #     else:
        #         return queryset.all()
        #
        # else:
        #     # 比起web端,终端只能看到和自身账户相关的账户
        #     devices = Device.objects.filter(enduserdevice__enduser=owner)
        #     device_list = []
        #     for i in devices:
        #         device_list.append(i.device_id)
        #     queryset = queryset.filter(device_id__in=device_list)

        #     #首页仅仅显示未读消息
        #     home = self.request.query_params.get(1, None)
        #     if home:
        #         return queryset.exclude(flag={user.cellphone: "read"})
        #
        #     return queryset

    def get_serializer_class(self):
        pass
        # @需完善
        # content = self.request.query_params.get("type", None)
        # if content == 'A':
        #     return serializers.ASerializers
        # elif content == 'B':
        #     return serializers.BSerializers
        # else:
        #     return self.serializer_class

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            return result
        serializer = self.get_serializer(queryset, many=True)
        return simple_response(code=0, message="Ok", data=serializer.data)

    def post(self, request):
        # 额外信息，比如user : request.data
        context={}
        # @待定
        serializer = self.serializer_class(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return simple_response(code=0, message="ok", data=serializer.data)
        return simple_response(code=10000, message=serializer.errors)

    def put(self, request):
        # @需要获取的参数
        id = request.data.get("id")
        param_1 = request.data.get("param_1")
        if not id:
            return simple_response(code=10000, message="Missing params")
        try:
            queryset = self.queryset.get(id=id)
        except Exception as e:
            return simple_response(code=50001, message="this feedback does not exist")

        serializer = self.serializer_class(queryset, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return simple_response(code=0, message='ok', data=serializer.data)
        return simple_response(code=10001, message=serializer.errors)

    def delete(self, request):
        id = request.data.get("id")
        if not id:
            return simple_response(code=10000, message="Missing params")
        try:
            self.queryset.filter(id=id).delete()
        except Exception as e:
            return simple_response(code=50001, message="this xxx does not exist")
        return simple_response(code=0, message="ok")
