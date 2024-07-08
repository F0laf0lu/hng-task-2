from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import AddUserToOrganisationView, LoginView, OrganizationDetailView, OrganizationListview, RegisterView, UserDetailView

urlpatterns = [
    path("auth/register", RegisterView.as_view(), name="register"),
    path("auth/login", LoginView.as_view(),name="login"),
    path('api/organisations', OrganizationListview.as_view(), name='organisation_list'),
    path("api/organisations/<uuid:orgId>", OrganizationDetailView.as_view(), name="organisation_detail"),
    path('api/organisations/<uuid:orgId>/users', AddUserToOrganisationView.as_view(), name='add_user_to_organisation'),
    path('api/users/<int:pk>', UserDetailView.as_view(), name="user_detail"),
]
