from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from application_tracking import views  # ✅ Import the module, not a single view

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 👇 Root URL — loads your home page (landing page or job listings based on auth)
    path('', views.home, name='home'),
    
    # Browse jobs page
    path('jobs/', views.list_adverts, name='browse_jobs'),
    
    # Other apps
    path('auth/', include('accounts.urls')),
    path('', include('application_tracking.urls')),
]

# ✅ Add static/media file serving (for development)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
