from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Contract
from .serializers import ContractCreateSerializer, ContractSerializer
from .services import ContractError, create_contract

TRUTHY = {"true", "1", "yes"}


class ContractListCreateView(generics.ListCreateAPIView):
    serializer_class = ContractSerializer

    def get_queryset(self):
        queryset = Contract.objects.select_related("member", "unit", "unit__property")

        params = self.request.query_params
        active = params.get("active")
        if active is not None:
            if active.lower() in TRUTHY:
                queryset = queryset.active()
            else:
                queryset = queryset.exclude(pk__in=Contract.objects.active().values("pk"))

        for param, field in (
            ("unit_id", "unit_id"),
            ("member_id", "member_id"),
            ("property_id", "unit__property_id"),
        ):
            if params.get(param):
                queryset = queryset.filter(**{field: params[param]})

        return queryset

    def create(self, request, *args, **kwargs):
        payload = ContractCreateSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        data = payload.validated_data

        try:
            contract = create_contract(
                member=data["member"],
                unit_id=data["unit"].pk,
                start_date=data["start_date"],
                end_date=data["end_date"],
                monthly_rent=data.get("monthly_rent"),
                created_by=request.user,
            )
        except ContractError as exc:
            raise ValidationError({"detail": str(exc)})

        return Response(ContractSerializer(contract).data, status=status.HTTP_201_CREATED)


class ContractDetailView(generics.RetrieveAPIView):
    serializer_class = ContractSerializer
    lookup_url_kwarg = "contract_id"
    queryset = Contract.objects.select_related("member", "unit", "unit__property")
