from rest_framework.routers import DefaultRouter
from .views import BookViewset

router = DefaultRouter()
router.register(r'', BookViewset, basename='books')

urlpatterns = router.urls