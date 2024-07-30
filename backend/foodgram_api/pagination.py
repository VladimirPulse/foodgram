from rest_framework.pagination import PageNumberPagination


class MyPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'recipes_limit'
    max_page_size = 10

    def get_paginate_response(self, data):
        return data
