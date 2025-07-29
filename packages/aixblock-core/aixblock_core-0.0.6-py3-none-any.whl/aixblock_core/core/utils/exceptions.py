"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
from rest_framework.exceptions import APIException, ValidationError
from rest_framework import status
from lxml.etree import XMLSyntaxError


class AIxBlockError(Exception):
    pass


class AIxBlockAPIException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Unknown error'


class AIxBlockDatabaseException(AIxBlockAPIException):
    default_detail = 'Error executing database query'


class AIxBlockDatabaseLockedException(AIxBlockAPIException):
    default_detail = "Sqlite <a href='https://docs.djangoproject.com/en/3.1/ref/databases/#database-is-locked-errors'>doesn't operate well</a> on multiple transactions. \
    Please be patient and try update your pages, or ping us on Slack to  get more about production-ready db"


class ProjectExistException(AIxBlockAPIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = 'Project with the same title already exists'


class AIxBlockErrorSentryIgnored(Exception):
    pass


class AIxBlockAPIExceptionSentryIgnored(AIxBlockAPIException):
    pass


class AIxBlockValidationErrorSentryIgnored(ValidationError):
    pass


class AIxBlockXMLSyntaxErrorSentryIgnored(Exception):
    pass


class ImportFromLocalIPError(AIxBlockAPIException):
    default_detail = 'Importing from local IP is not allowed'
    status_code = status.HTTP_403_FORBIDDEN


class MLModelLocalIPError(AIxBlockAPIException):
    default_detail = 'Adding models with local IP is not allowed'
    status_code = status.HTTP_403_FORBIDDEN
