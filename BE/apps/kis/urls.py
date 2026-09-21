from django.urls import path

from .views import (
    KisAgentSearchView,
    KisDatasetAssetView,
    KisSearchInspectView,
    KisSearchView,
    KisVideoUploadView,
)


urlpatterns = [
    path("agent/search/", KisAgentSearchView.as_view(), name="kis-agent-search"),
    path("search/", KisSearchView.as_view(), name="kis-search"),
    path(
        "search/inspect/",
        KisSearchInspectView.as_view(),
        name="kis-search-inspect",
    ),
    path(
        "videos/upload/",
        KisVideoUploadView.as_view(),
        name="kis-video-upload",
    ),
    path(
        "assets/<path:asset_path>",
        KisDatasetAssetView.as_view(),
        name="kis-dataset-asset",
    ),
]
