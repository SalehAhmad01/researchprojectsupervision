from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('projects/', include('projects.urls')),
    path('drafts/', include('drafts.urls')),
    path('feedbacks/', include('feedbacks.urls')),
    path('notifications/', include('notifications.urls')),
    path('', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
