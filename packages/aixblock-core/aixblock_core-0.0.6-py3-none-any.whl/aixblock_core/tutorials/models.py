from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

class TutorialGroup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    order = models.IntegerField(null=True, default=0)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now_add=True)
    
    class Meta:
        db_table = 'tutorial_group'
    
    def has_permission(self, user):
        return self


class TutorialSubGroup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    group_id = models.ForeignKey(
        TutorialGroup, db_column='group_id', 
        on_delete=models.CASCADE, related_name='sub_groups'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now_add=True)

    class Meta:
        db_table = 'tutorial_sub_group'
    
    def has_permission(self, user):
        return self

class TutorialSectionContent(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.TextField(default='')
    url = models.TextField(default='')
    sub_group_id = models.ForeignKey(
        TutorialSubGroup, on_delete=models.CASCADE,
        db_column='sub_group_id', related_name='section_contents'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now_add=True)

    class Meta:
        db_table = 'tutorial_section_content'
    
    def has_permission(self, user):
        return self

class TutorialContent(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.TextField(default='')
    content = models.TextField(null=True)
    section_id = models.OneToOneField(
        TutorialSectionContent, on_delete=models.CASCADE,
        db_column='section_id', related_name='tutorial_content'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now_add=True)

    class Meta:
        db_table = 'tutorial_content'
    
    def has_permission(self, user):
        return self