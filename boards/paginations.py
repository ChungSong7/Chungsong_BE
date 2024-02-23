from rest_framework.pagination import CursorPagination
from rest_framework.response import Response

class CustomCursorPagination(CursorPagination):
    #count = 3  # 한 페이지에 표시될 항목 수
    ordering = '-created_at'  # 페이지네이션 기준 필드

    def paginate_queryset(self, queryset, request, view=None):
        self.count = queryset.count()
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'results': data
        })