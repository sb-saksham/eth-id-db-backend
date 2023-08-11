from django.urls import path, re_path

from knox import views as knox_views

from .rest_api.views import LoginView, PostIdImageView, UserCreateView, PostWalletImageView, FinalSavePostView, AccountsEmailActivation


app_name = "accounts"

urlpatterns = [
    # Auth Views
    path('login/', LoginView.as_view()),
    path('signup/', UserCreateView.as_view()),
    re_path(r'^user/activate/(?P<key>[0-9A-Za-z]+)/$', AccountsEmailActivation.as_view(), name='email-activation'),
    path('logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('logout/all/', knox_views.LogoutAllView.as_view(), name='knox_logoutall'),

    # Verify Views
    path('id/img/', PostIdImageView.as_view()),
    path('waddr/img/', PostWalletImageView.as_view()),
    path('save/to/db/', FinalSavePostView.as_view()),
]
