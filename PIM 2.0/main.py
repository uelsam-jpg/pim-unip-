import os
import cursos.cursos
import modulos.modulos
import security.security
from usuarios.usuarios import (
    get_usuario_logado, tela_login_cadastro,
    eh_admin, menu_admin, logout,
    usuarios_cadastrados, registrar_log
)


# ========== CONFIGURAÇÕES VISUAIS ==========
COR_TITULO = "\033[1;35m"  # Roxo
COR_MENU = "\033[1;36m"    # Azul claro
COR_ADM = "\033[1;31m"     # Vermelho
COR_USUARIO = "\033[1;34m" # Azul
COR_ALERTA = "\033[1;33m"  # Amarelo
COR_SUCESSO = "\033[1;32m" # Verde
COR_ERRO = "\033[1;31m"    # Vermelho
RESET_COR = "\033[0m"

# ========== MENU PRINCIPAL ==========
def mostrar_menu_principal():
    print(f"\n{COR_TITULO}=== PLATAFORMA EDUCAÇÃO DIGITAL ==={RESET_COR}")
    
    if get_usuario_logado():
        cor_status = COR_ADM if eh_admin() else COR_USUARIO
        tipo = "ADMIN" if eh_admin() else "USUÁRIO"
        print(f"{cor_status}👉 Logado como: {get_usuario_logado()['nome']} ({tipo}){RESET_COR}")
    
    print(f"\n{COR_MENU}=== MENU PRINCIPAL ===")
    print("1. 🔐 Login/Cadastro")
    print("2. 🎓 Cursos")
    print("3. 🔒 Segurança")
    print("4. 📚 Módulos")
    print("5. 📜 Certificados")
    print("6. 🚪 Sair")
    
    if eh_admin():
        print(f"{COR_ADM}99. ⚡ Menu ADM{RESET_COR}")
    
    print("=" * 35 + RESET_COR)
    return input("Escolha uma opção: ")

def main():
    while True:
        escolha = mostrar_menu_principal()

        # Opção 1: Login/Cadastro
        if escolha == '1':
            tela_login_cadastro()

        # Opção 2: Cursos
        elif escolha == '2':
            if get_usuario_logado():
                cursos.cursos.tela_cursos()
            else:
                print(f"\n{COR_ALERTA}⚠️ Você precisa fazer login primeiro!{RESET_COR}")
                input("Pressione Enter para voltar...")

        # Opção 3: Segurança
        elif escolha == '3':
            security.security.tela_seguranca()

        # Opção 4: Módulos (Versão corrigida)
        elif escolha == '4':
            if not get_usuario_logado():
                print(f"\n{COR_ALERTA}⚠️ Você precisa fazer login primeiro!{RESET_COR}")
                input("Pressione Enter para voltar...")
            else:
                if eh_admin():
                    try:
                        from modulos.modulos import tela_modulos
                        tela_modulos()
                    except ImportError as e:
                        print(f"\n{COR_ERRO}❌ Erro ao carregar módulo: {e}{RESET_COR}")
                        registrar_log("Erro de importação", f"Módulos: {str(e)}")
                else:
                    print(f"\n{COR_ERRO}🚫 ACESSO NEGADO!{RESET_COR}")
                    print(f"{COR_ALERTA}👉 Esta função é restrita a administradores{RESET_COR}")
                input("Pressione Enter para voltar...")

        # Opção 5: Certificados
        elif escolha == '5':
            if get_usuario_logado():
                try:
                    from certificados.certificados import tela_certificados
                    tela_certificados()
                except ImportError as e:
                    print(f"\n{COR_ERRO}❌ Erro ao carregar módulo: {e}{RESET_COR}")
                    input("Pressione Enter para voltar...")
            else:
                print(f"\n{COR_ALERTA}⚠️ Você precisa fazer login primeiro!{RESET_COR}")
                input("Pressione Enter para voltar...")

        # Opção 6: Sair
        elif escolha == '6':
            print(f"\n{COR_SUCESSO}✅ Até logo!{RESET_COR}")
            if get_usuario_logado():
                logout()
            break

        # Opção 99: Menu ADM
        elif escolha == '99' and eh_admin():
            menu_admin()

        else:
            print(f"\n{COR_ERRO}❌ Opção inválida!{RESET_COR}")
            input("Pressione Enter para voltar...")

if __name__ == "__main__":
    main()