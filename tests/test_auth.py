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
