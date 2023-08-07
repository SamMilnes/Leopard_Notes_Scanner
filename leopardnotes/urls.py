from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from .views import home_view, ocr_view, ocr_results_view, OCRImageDeleteView, segment_image, submit_marked_data,\
    snip_view


urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("allauth.urls")),
    path("", home_view, name="home-view"),
    path("profiles/", include("profiles.urls")),
    path("posts/", include("posts.urls")),
    path("ocr/", ocr_view, name="ocr-view"),
    path('ocr/results/', ocr_results_view, name='ocr-view-results'),
    path('ocr/delete/<int:pk>/', OCRImageDeleteView.as_view(), name='delete-ocr'),
    path('segment-image/', segment_image, name='segment-image'),
    path('submit-marked-data/', submit_marked_data, name='submit-marked-data'),
    path('ocr/snip-image/', snip_view, name='ocr-snip'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
