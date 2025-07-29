from rest_framework import status

from core.utils.exceptions import AIxBlockAPIException


class LabelBulkUpdateError(AIxBlockAPIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
