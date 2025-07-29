from django.db.models import Q
from comments.models import Comment
from comments.serializers import CommentSerializer
from core.permissions import ViewClassPermission, all_permissions
from rest_framework import generics
from rest_framework.response import Response
from tasks.models import Annotation


class CommentAPI(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_required = ViewClassPermission(
        GET=all_permissions.annotations_view,
        POST=all_permissions.annotations_view,
    )

    def get_queryset(self):
        task_pk = self.request.query_params.get('task')
        ordering = self.request.query_params.get('ordering')

        filters = Q(
            Q(
                Q(task__isnull=False)
                & Q(task=task_pk)
            )
            | Q(annotation__in=Annotation.objects.filter(task_id=task_pk).values_list('id', flat=True))
        )

        return Comment.objects.filter(filters).order_by(ordering)

    def get(self, request, *args, **kwargs):
        return super(CommentAPI, self).get(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def post(self, request, *args, **kwargs):
        return super(CommentAPI, self).post(request, *args, **kwargs)


class CommentResolveAPI(generics.UpdateAPIView):
    permission_required = ViewClassPermission(
        PATCH=all_permissions.annotations_view,
    )

    def get_queryset(self):
        return Comment.objects

    def patch(self, request, *args, **kwargs):
        comment = self.get_object()

        if comment is not None:
            comment.is_resolved = request.data.get('is_resolved')
            comment.save(update_fields=frozenset(['is_resolved']))
            return Response(CommentSerializer(comment).data)

        return Response(status=403)
