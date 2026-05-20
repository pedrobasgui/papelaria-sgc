"""Testes de autenticação JWT."""
import pytest

@pytest.mark.django_db
class TestAuth:

    def test_login_sucesso(self, api_client, admin_user):
        r = api_client.post("/api/auth/login/", {
            "username": "admin", "password": "senha123"
        }, format="json")
        assert r.status_code == 200
        data = r.json()
        assert "access" in data and "refresh" in data
        assert data["usuario"]["perfil"] == "ADMIN"

    def test_login_credencial_invalida(self, api_client, admin_user):
        r = api_client.post("/api/auth/login/", {
            "username": "admin", "password": "errada"
        }, format="json")
        assert r.status_code == 401

    def test_endpoint_protegido_sem_token(self, api_client):
        r = api_client.get("/api/clientes/")
        assert r.status_code == 401

    def test_endpoint_protegido_com_token(self, api_client, admin_user):
        login = api_client.post("/api/auth/login/", {
            "username": "admin", "password": "senha123"
        }, format="json").json()
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {login["access"]}')
        r = api_client.get("/api/clientes/")
        assert r.status_code == 200

    def test_me_retorna_dados_usuario(self, admin_client):
        r = admin_client.get("/api/auth/me/")
        assert r.status_code == 200
        assert r.json()["username"] == "admin"

@pytest.mark.django_db
class TestRecuperacaoSenha:

    def test_solicitar_recuperacao_email_valido(self, api_client, admin_user):
        r = api_client.post("/api/auth/recuperar-senha/",
                            {"email": admin_user.email}, format="json")
        assert r.status_code == 200
        assert "mensagem" in r.json()

    def test_solicitar_recuperacao_email_inexistente(self, api_client):
        r = api_client.post("/api/auth/recuperar-senha/",
                            {"email": "naoexiste@email.com"}, format="json")
        assert r.status_code == 200

    def test_redefinir_senha_token_invalido(self, api_client):
        r = api_client.post("/api/auth/redefinir-senha/",
                            {"token": "tokenfalso", "nova_senha": "nova123"},
                            format="json")
        assert r.status_code == 400
        assert r.json()["codigo"] == "TOKEN_INVALIDO"

    def test_redefinir_senha_fluxo_completo(self, api_client, admin_user):
        from apps.usuarios.reset_token import PasswordResetToken
        token_raw, _ = PasswordResetToken.criar_para(admin_user)
        r = api_client.post("/api/auth/redefinir-senha/",
                            {"token": token_raw, "nova_senha": "novasenha123"},
                            format="json")
        assert r.status_code == 200
        admin_user.refresh_from_db()
        assert admin_user.check_password("novasenha123")

    def test_token_expira_apos_uso(self, api_client, admin_user):
        from apps.usuarios.reset_token import PasswordResetToken
        token_raw, _ = PasswordResetToken.criar_para(admin_user)
        api_client.post("/api/auth/redefinir-senha/",
                        {"token": token_raw, "nova_senha": "senha111"},
                        format="json")
        r = api_client.post("/api/auth/redefinir-senha/",
                            {"token": token_raw, "nova_senha": "senha222"},
                            format="json")
        assert r.status_code == 400
