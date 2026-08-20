from rest_framework import generics

from .models import Member
from .serializers import MemberSerializer


class MemberListCreateView(generics.ListCreateAPIView):
    serializer_class = MemberSerializer

    def get_queryset(self):
        queryset = Member.objects.all()
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(full_name__icontains=search)
        return queryset


class MemberDetailView(generics.RetrieveAPIView):
    serializer_class = MemberSerializer
    queryset = Member.objects.all()
    lookup_url_kwarg = "member_id"
