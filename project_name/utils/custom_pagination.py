# -*- coding:utf-8 -*-
#!/usr/bin/env python
# xiaoz
from collections import OrderedDict

from rest_framework.pagination import BasePagination
from rest_framework.pagination import  _positive_int
from rest_framework.settings import api_settings
from rest_framework.response import Response


def _get_count(queryset):
    """
    Determine an object count, supporting either querysets or regular lists.
    """
    try:
        return queryset.count()
    except (AttributeError, TypeError):
        return len(queryset)


class CustomPagination(BasePagination):
    display_page_controls = False
    page_query_param = "page"
    page_size_query_param = "page_size"
    offset_query_param = "offset"
    show_count_query_param = "show_count"
    show_all_query_param = "show_all"

    page_size = api_settings.PAGE_SIZE
    show_count = True

    def get_page_size(self, request):
        try:
            return _positive_int(
                request.query_params[self.page_size_query_param],
                strict=True,
            )
        except (KeyError, ValueError):
            return self.page_size

    def get_page(self, request):
        try:
            return _positive_int(
                request.query_params[self.page_query_param],
                strict=True
            )
        except (KeyError, ValueError):
            return 1

    def get_offset(self, request):
        try:
            return _positive_int(
                request.query_params[self.offset_query_param],
                strict=True
            )
        except (KeyError, ValueError):
            return 0

    def get_count(self, queryset, request):
        try:
            self.show_count = request.query_params[self.show_count_query_param]
        except (KeyError, ValueError):
            pass
        if self.show_count:
            return _get_count(queryset)
        else:
            return None

    def get_previous_link(self):
        if self.start <= 0:
            return None
        else:
            return True

    def get_next_link(self):
        if self.count and self.count > self.end:
            return True
        else:
            return None

    def paginate_queryset(self, queryset, request, view=None):  # pragma: no cover
        self.page_size = self.get_page_size(request)
        self.count = self.get_count(queryset, request)

        try:
            show_all = request.query_params[self.show_all_query_param]
        except (KeyError, ValueError):
            show_all = False

        if show_all:
            # need to check count
            # if more then 1000, maximum is set to 1000
            self.start = 0
            if not self.count:
                # force to get count
                self.count = _get_count(queryset)
            if self.count > 1000:
                self.end = 1000
            else:
                self.end = self.count
            return queryset[self.start:self.end]

        page = self.get_page(request) - 1
        if page > 0:
            self.start = page * self.page_size
        else:
            self.start = self.get_offset(request)

        self.end = self.start + self.page_size

        if self.count and self.end > self.count:
            self.end = self.count

        return queryset[self.start:self.end]

    def get_paginated_response(self, data):  # pragma: no cover
        meta = {
            "message": "info list",
            "code": 0
        }
        payload = OrderedDict([
            ("count", self.count),
            ('page_size', self.page_size),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ])
        return Response({"meta": meta, "data": payload})


