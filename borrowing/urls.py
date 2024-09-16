from rest_framework import routers

from borrowing.views import (
    BorrowingViewSet,
)

app_name = "borrowing"

router = routers.DefaultRouter()
router.register("borrowing", BorrowingViewSet)

urlpatterns = router.urls
