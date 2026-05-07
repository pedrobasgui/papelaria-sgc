"""
Views da API de autenticação e usuários.

Endpoints:
    POST /api/auth/login/       - login (retorna access + refresh)
    POST /api/auth/refresh/     - renova access token
    POST /api/auth/logout/      - blacklist do refresh token
    GET  /api/auth/me/          - dados do usuário logado
    POST /api/auth/trocar-senha/
    POST /api/auth/recuperar-senha/   (placeholder - Entrega 3)
    GET/POST /api/auth/usuarios/   - listar/criar usuários (ADMIN)
"""
from django.contrib.auth import get_user_model
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView
)
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.permissions import IsAdmin
from .serializers import (
    LoginSerializer, UsuarioSerializer, UsuarioCreateSerializer,
    TrocarSenhaSerializer, RecuperarSenhaSerializer,
)

User = get_user_model()

class LoginView(TokenObtainPairView):
    """POST /api/auth/login/ - autentica e devolve tokens + perfil."""
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

class LogoutView(APIView):
    """POST /api/auth/logout/ - invalida o refresh token."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh = request.data.get("refresh")
            if refresh:
                token = RefreshToken(refresh)
                token.blacklist()
            return Response(
                {"mensagem": "Logout realizado com sucesso."},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"erro": "Token inválido.", "codigo": "TOKEN_INVALIDO"},
                status=status.HTTP_400_BAD_REQUEST,
            )

class MeView(generics.RetrieveAPIView):
    """GET /api/auth/me/ - retorna dados do usuário logado."""
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class TrocarSenhaView(APIView):
    """POST /api/auth/trocar-senha/"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TrocarSenhaSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data["senha_nova"])
        user.save()
        return Response({"mensagem": "Senha alterada com sucesso."})

class RecuperarSenhaView(APIView):
    """
    POST /api/auth/recuperar-senha/
    Stub para Entrega 3: apenas valida e-mail por enquanto.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RecuperarSenhaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # TODO Entrega 3: gerar token, enviar e-mail
        return Response({
            "mensagem": "Se o e-mail estiver cadastrado, "
                        "instruções de recuperação serão enviadas.",
            "obs": "Funcionalidade completa será implementada na Entrega 3.",
        })

class UsuarioViewSet(viewsets.ModelViewSet):
    """CRUD de usuários (apenas ADMIN)."""
    queryset = User.objects.all()
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.action == "create":
            return UsuarioCreateSerializer
        return UsuarioSerializer
