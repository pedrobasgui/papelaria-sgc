"""
Serializers do app usuarios.

Inclui:
- LoginSerializer (custom): retorna token + dados do usuário
- UsuarioSerializer: leitura do perfil
- UsuarioCreateSerializer: cadastro (somente ADMIN)
- TrocarSenhaSerializer
- RecuperarSenhaSerializer (placeholder para Entrega 3)
"""
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UsuarioSerializer(serializers.ModelSerializer):
    """Representação pública de um usuário."""
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "perfil", "is_active", "criado_em",
        ]
        read_only_fields = ["id", "criado_em"]

class UsuarioCreateSerializer(serializers.ModelSerializer):
    """Cria usuário - hash da senha automático via set_password."""
    password = serializers.CharField(
        write_only=True, required=True, min_length=6,
        style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "perfil", "password"
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)   # hash PBKDF2
        user.save()
        return user

class LoginSerializer(TokenObtainPairSerializer):
    """
    Serializer custom de login. Inclui dados do usuário no response
    para evitar uma requisição adicional pelo frontend.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Claims customizadas
        token["username"] = user.username
        token["perfil"]   = user.perfil
        token["email"]    = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["usuario"] = UsuarioSerializer(self.user).data
        return data

class TrocarSenhaSerializer(serializers.Serializer):
    """Troca a senha do usuário autenticado."""
    senha_atual = serializers.CharField(required=True, write_only=True)
    senha_nova  = serializers.CharField(
        required=True, write_only=True, min_length=6
    )

    def validate_senha_atual(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Senha atual incorreta.")
        return value

class RecuperarSenhaSerializer(serializers.Serializer):
    """
    Solicita recuperação por e-mail (Entrega 3).
    Por enquanto apenas valida o e-mail.
    """
    email = serializers.EmailField()
