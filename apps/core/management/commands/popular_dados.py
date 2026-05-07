"""
python manage.py popular_dados
Cria dados iniciais para desenvolvimento e demonstração.
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.clientes.models import Cliente
from apps.produtos.models import Produto

User = get_user_model()

class Command(BaseCommand):
    help = "Popula o banco com dados iniciais (Papelaria Mundo Letrado)."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Populando dados iniciais...\n")

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin", email="admin@mundoletrado.com.br",
                password="admin123", perfil="ADMIN"
            )
            self.stdout.write(self.style.SUCCESS(
                " - admin criado (admin / admin123)"
            ))

        for u in [("joao.silva",  "joao@mundoletrado.com.br",  "FUNCIONARIO"),
                  ("maria.santos","maria@mundoletrado.com.br", "FUNCIONARIO")]:
            if not User.objects.filter(username=u[0]).exists():
                User.objects.create_user(
                    username=u[0], email=u[1], password="senha123", perfil=u[2]
                )
                self.stdout.write(f" - usuário {u[0]} criado")

        clientes = [
            ("Ana Beatriz Souza",   "529.982.247-25", "ana@email.com",     "(61) 99876-5432", "Q 401 Norte, Brasília/DF"),
            ("Carlos Eduardo Lima", "248.438.034-80", "carlos@email.com",  "(61) 99123-4567", "Lago Sul, Brasília/DF"),
            ("Fernanda Oliveira",   "863.715.706-19", "fernanda@email.com","(61) 98555-1122", "Asa Sul 308, Brasília/DF"),
            ("João Pedro Castro",   "390.533.447-05", "joaop@email.com",   "(61) 99888-3344", "Taguatinga Norte, DF"),
        ]
        for nome, cpf, email, tel, end in clientes:
            if not Cliente.objects.filter(cpf=cpf).exists():
                Cliente.objects.create(
                    nome=nome, cpf=cpf, email=email,
                    telefone=tel, endereco=end
                )
        self.stdout.write(f" - {len(clientes)} clientes garantidos")

        produtos = [
            ("Caderno Universitário 200 folhas", "Caderno espiral, 200 folhas, capa dura",      "24.90",  60, 10),
            ("Caneta Esferográfica Azul",        "Caneta esferográfica BIC azul",                "2.50", 200, 30),
            ("Caneta Esferográfica Preta",       "Caneta esferográfica BIC preta",               "2.50", 180, 30),
            ("Lápis HB",                         "Lápis grafite preto HB com borracha",          "1.80", 250, 40),
            ("Borracha Branca",                  "Borracha branca tamanho médio",                "1.20", 150, 20),
            ("Apontador com Depósito",           "Apontador com depósito de plástico",           "3.50",  90, 15),
            ("Mochila Escolar",                  "Mochila escolar 20L com bolsos laterais",    "149.90",  20,  3),
            ("Estojo Triplo",                    "Estojo escolar triplo",                       "45.00",  35,  5),
            ("Tinta Guache 6 Cores",             "Conjunto de tinta guache 6 cores 15ml",       "12.90",  40,  8),
            ("Lápis de Cor 24 Cores",            "Caixa com 24 lápis de cor",                   "29.90",  45,  8),
            ("Cola Branca 90g",                  "Cola escolar branca lavável 90g",              "4.90", 100, 15),
            ("Tesoura sem Ponta",                "Tesoura escolar sem ponta",                    "8.50",  60, 10),
            ("Marcador de Texto Amarelo",        "Marca-texto fluorescente amarelo",             "4.20", 110, 20),
            ("Papel Sulfite A4 (resma)",         "Resma com 500 folhas A4 75g",                 "29.90",  25,  5),
            ("Pasta Catálogo 50 plásticos",      "Pasta tipo catálogo com 50 plásticos",        "18.90",  30,  5),
        ]
        for nome, desc, preco, est, est_min in produtos:
            if not Produto.objects.filter(nome=nome).exists():
                Produto.objects.create(
                    nome=nome, descricao=desc,
                    preco=Decimal(preco), estoque=est,
                    estoque_minimo=est_min,
                )
        self.stdout.write(f" - {len(produtos)} produtos garantidos")

        self.stdout.write(self.style.SUCCESS("\n✓ Dados iniciais OK!"))
        self.stdout.write("Login: admin / admin123\n")
