from django.urls import path

from .views import MemberDetailView, MemberListCreateView

urlpatterns = [
    path("members", MemberListCreateView.as_view(), name="member-list"),
    path("members/<int:member_id>", MemberDetailView.as_view(), name="member-detail"),
]
