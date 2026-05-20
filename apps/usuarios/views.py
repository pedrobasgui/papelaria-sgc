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
    """POST /api/auth/recuperar-senha/ - solicita recuperacao por e-mail."""
    permission_classes = [AllowAny]

    def post(self, request):
        from django.contrib.auth import get_user_model
        from .reset_token import PasswordResetToken
        from .email_service import enviar_email_recuperacao

        serializer = RecuperarSenhaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        User = get_user_model()
        usuario = User.objects.filter(email=email, is_active=True).first()
        if usuario:
            token_raw, _ = PasswordResetToken.criar_para(usuario)
            enviar_email_recuperacao(email, usuario.username, token_raw)
        return Response({
            "mensagem": "Se o e-mail estiver cadastrado, "
                        "você receberá as instruções em breve."
        })


class RedefinirSenhaView(APIView):
    """POST /api/auth/redefinir-senha/ - confirma token e salva nova senha."""
    permission_classes = [AllowAny]

    def post(self, request):
        from .reset_token import PasswordResetToken
        token_raw = request.data.get("token", "")
        nova_senha = request.data.get("nova_senha", "")
        if not token_raw or not nova_senha:
            return Response(
                {"erro": "Token e nova senha são obrigatórios.",
                 "codigo": "DADOS_INVALIDOS"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(nova_senha) < 6:
            return Response(
                {"erro": "A senha deve ter no mínimo 6 caracteres.",
                 "codigo": "SENHA_CURTA"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        import hashlib
        token_hash = hashlib.sha256(token_raw.encode()).hexdigest()
        token_obj = PasswordResetToken.objects.filter(
            token_hash=token_hash
        ).select_related("usuario").first()
        if not token_obj or not token_obj.is_valido():
            return Response(
                {"erro": "Token inválido ou expirado.",
                 "codigo": "TOKEN_INVALIDO"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        usuario = token_obj.usuario
        usuario.set_password(nova_senha)
        usuario.save()
        token_obj.marcar_usado()
        return Response({"mensagem": "Senha redefinida com sucesso."})

class UsuarioViewSet(viewsets.ModelViewSet):
    """CRUD de usuários (apenas ADMIN)."""
    queryset = User.objects.all()
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.action == "create":
            return UsuarioCreateSerializer
        return UsuarioSerializer
