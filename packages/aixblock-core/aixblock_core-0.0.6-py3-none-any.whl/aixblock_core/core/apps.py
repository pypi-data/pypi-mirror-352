from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'core'

    def ready(self):
        from django.contrib import admin
        from django.contrib.auth.models import Group
        from rest_framework.authtoken.models import TokenProxy
        import oauth2_provider.models as oauth2Models
        import signals
        admin.site.unregister(Group)
        admin.site.unregister(TokenProxy)
        admin.site.unregister(oauth2Models.Application)
        admin.site.unregister(oauth2Models.AccessToken)
        admin.site.unregister(oauth2Models.Grant)
        admin.site.unregister(oauth2Models.IDToken)
        admin.site.unregister(oauth2Models.RefreshToken)

        # for cls in list(admin.site._registry):
        #     print(cls)
            # if cls is not SomeName:
            #     admin.site.unregister(cls)

        return super().ready()
