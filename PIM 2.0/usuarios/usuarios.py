import re
import json
import os
from datetime import datetime
from typing import Dict, Optional



# ========== CONFIGURAÇÕES ==========
ARQUIVO_JSON = "dados_usuarios.json"
ARQUIVO_LOG = "registro_logs.log"
COR_ADM = "\033[1;31m"  # Vermelho
COR_USUARIO = "\033[1;34m"  # Azul
COR_ERRO = "\033[1;33m"  # Amarelo
COR_SUCESSO = "\033[1;32m"  # Verde
COR_LOG = "\033[0;36m"  # Ciano
RESET_COR = "\033[0m"


def get_usuario_logado():
    return usuario_logado

def get_usuarios_cadastrados():
    return usuarios_cadastrados

def registrar_log(acao: str, detalhes: str = ""):
    """Registra ações importantes no arquivo de log"""
    usuario = usuario_logado['nome'] if usuario_logado else 'SISTEMA'
    with open(ARQUIVO_LOG, 'a', encoding='utf-8') as f:
        log_entry = (
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"Usuário: {usuario}\n"
            f"Ação: {acao}\n"
            f"Detalhes: {detalhes}\n"
            f"{'-'*50}\n"
        )
        f.write(log_entry)

# ========== BANCO DE DADOS ==========
def carregar_usuarios() -> Dict:
    """Carrega usuários do JSON ou cria estrutura inicial"""
    if os.path.exists(ARQUIVO_JSON):
        with open(ARQUIVO_JSON, 'r') as f:
            return json.load(f)
    return {
        "admin": {
            "senha": "Admin@123",
            "email": "admin@escola.com",
            "idade": 30,
            "is_admin": True,
            "data_cadastro": datetime.now().isoformat(),
            "cursos": []
        }
    }

def salvar_usuarios():
    """Salva os dados no JSON"""
    with open(ARQUIVO_JSON, 'w') as f:
        json.dump(usuarios_cadastrados, f, indent=4, ensure_ascii=False)


# ========== DADOS GLOBAIS ==========
usuarios_cadastrados = carregar_usuarios()
usuario_logado = None

# ========== VALIDAÇÕES ==========
def validar_email(email: str) -> Optional[str]:
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        return "Email inválido! Formato: usuario@dominio.com"
    return None

def validar_idade(idade: str) -> Optional[str]:
    try:
        if not 5 <= int(idade) <= 120:
            return "Idade deve ser entre 5-120 anos"
    except ValueError:
        return "Digite um número válido"
    return None

def validar_senha(senha: str) -> Optional[str]:
    if len(senha) < 8:
        return "Mínimo 8 caracteres"
    if not any(c.isupper() for c in senha):
        return "Pelo menos 1 letra maiúscula"
    if not any(c.isdigit() for c in senha):
        return "Pelo menos 1 número"
    if not any(c in "!@#$%&*_-+=" for c in senha):
        return "Pelo menos 1 símbolo especial"
    return None

def validar_nome_usuario(nome: str) -> Optional[str]:
    if not re.match(r'^[a-zA-Z0-9_]{4,20}$', nome):
        return "4-20 caracteres (letras, números e _)"
    return None

# ========== OPERAÇÕES DE USUÁRIO ==========
def criar_usuario(is_admin: bool = False):
    """Cadastro completo com validação"""
    global usuarios_cadastrados
    
    tipo = "ADMIN" if is_admin else "ALUNO"
    print(f"\n{COR_ADM if is_admin else COR_USUARIO}=== CADASTRO {tipo} ===")
    
    # Nome de usuário
    while True:
        nome = input("Nome de usuário: ").strip()
        if erro := validar_nome_usuario(nome):
            print(f"{COR_ERRO}❌ {erro}{RESET_COR}")
            continue
        if nome in usuarios_cadastrados:
            print(f"{COR_ERRO}⚠️ Usuário já existe!{RESET_COR}")
            return
        break

    # Email
    while True:
        email = input("Email: ").strip()
        if erro := validar_email(email):
            print(f"{COR_ERRO}❌ {erro}{RESET_COR}")
        else:
            break

    # Idade
    while True:
        idade = input("Idade: ")
        if erro := validar_idade(idade):
            print(f"{COR_ERRO}❌ {erro}{RESET_COR}")
        else:
            idade_int = int(idade)
            break

    # Senha
    while True:
        senha = input("Senha: ")
        if erro := validar_senha(senha):
            print(f"{COR_ERRO}❌ {erro}{RESET_COR}")
        else:
            break

    # Salva dados
    usuarios_cadastrados[nome] = {
        "senha": senha,
        "email": email,
        "idade": idade_int,
        "is_admin": is_admin,
        "data_cadastro": datetime.now().isoformat(),
        "cursos": []
    }
    salvar_usuarios()
    registrar_log(f"Cadastro de {tipo}", f"Usuário: {nome}")
    print(f"{COR_SUCESSO}✅ {tipo} registrado!{RESET_COR}")

def fazer_login() -> bool:
    global usuario_logado, usuarios_cadastrados  # Adiciona a variável global
    usuarios_cadastrados = carregar_usuarios()  # Recarrega antes de validar
    
    print(f"\n{COR_ADM}=== LOGIN ===")
    nome = input("Usuário: ").strip()
    senha = input("Senha: ")

    if nome in usuarios_cadastrados and usuarios_cadastrados[nome]["senha"] == senha:
        usuario_logado = {
            "nome": nome,
            "is_admin": usuarios_cadastrados[nome]["is_admin"]
        }
        registrar_log("Login realizado", f"Usuário: {nome}")
        print(f"\n{COR_SUCESSO}✅ Login bem-sucedido!{RESET_COR}")
        return True
    
    print(f"{COR_ERRO}⚠️ Credenciais inválidas!{RESET_COR}")
    return False

# ========== GERENCIAMENTO DE CONTAS ==========
def deletar_conta():
    """Permite auto-deleção de contas não-administrativas"""
    global usuario_logado, usuarios_cadastrados
    
    if not usuario_logado:
        print(f"{COR_ERRO}⚠️ Nenhum usuário logado!{RESET_COR}")
        return
    
    nome = usuario_logado['nome']
    
    if eh_admin():
        print(f"{COR_ADM}⚠️ ADMs devem usar o menu administrativo{RESET_COR}")
        return
    
    print(f"\n{COR_ERRO}🚨 ATENÇÃO! DELETAR CONTA PERMANENTEMENTE!{RESET_COR}")
    print(f"• Todos os dados de {nome} serão perdidos")
    print(f"• Cursos matriculados: {len(usuarios_cadastrados[nome]['cursos'])}")
    
    confirmacao = input("\nDigite 'DELETAR' para confirmar: ")
    if confirmacao == 'DELETAR':
        usuarios_cadastrados.pop(nome)
        salvar_usuarios()
        registrar_log("Usuário: {nome}")
        logout()
        print(f"{COR_SUCESSO}✅ Conta removida!{RESET_COR}")
    else:
        print(f"{COR_USUARIO}❌ Cancelado{RESET_COR}")

# ========== MENU ADMINISTRATIVO ==========
def menu_admin():
    """Painel completo para administradores"""
    while True:
        print(f"\n{COR_ADM}=== MENU ADMIN ===")
        print("1. 👑 CADASTRAR ADM")
        print("2. 🧑‍🎓 CADASTRAR ALUNO")
        print("3. 📋 LISTAR USUÁRIOS")
        print("4. 🔍 VER DADOS COMPLETOS")
        print("5. 🗑️ DELETAR USUÁRIO")
        print("6. 📜 VER REGISTROS DE LOG")
        print("7. ↩ VOLTAR")
        print("="*25 + RESET_COR)
        
        escolha = input("Escolha: ")

        if escolha == '1':
            criar_usuario(is_admin=True)
        elif escolha == '2':
            criar_usuario(is_admin=False)
        elif escolha == '3':
            listar_usuarios()
        elif escolha == '4':
            visualizar_dados_completos()
        elif escolha == '5':
            deletar_usuario_admin()
        elif escolha == '6':
            visualizar_logs()
        elif escolha == '7':
            break
        else:
            print(f"{COR_ERRO}❌ Opção inválida!{RESET_COR}")

def deletar_usuario_admin():
    """Deleção de usuários por ADMs"""
    print(f"\n{COR_ADM}=== DELETAR USUÁRIO ===")
    listar_usuarios()
    nome = input("\nNome do usuário a deletar: ").strip()
    
    if nome not in usuarios_cadastrados:
        print(f"{COR_ERRO}⚠️ Usuário não encontrado!{RESET_COR}")
        return
    
    if nome == usuario_logado['nome']:
        print(f"{COR_ADM}⚠️ Use a opção de deletar conta no menu principal{RESET_COR}")
        return
    
    print(f"\n{COR_ERRO}🚨 DETALHES DO USUÁRIO:{RESET_COR}")
    print(f"• Email: {usuarios_cadastrados[nome]['email']}")
    print(f"• Idade: {usuarios_cadastrados[nome]['idade']}")
    print(f"• Cursos: {len(usuarios_cadastrados[nome]['cursos'])}")
    
    confirmacao = input("\nConfirmar deleção? (S/N): ").upper()
    if confirmacao == 'S':
        usuarios_cadastrados.pop(nome)
        salvar_usuarios()
        ("Usuário deletado por ADM", f"Usuário: {nome} | Por: {usuario_logado['nome']}")
        print(f"{COR_SUCESSO}✅ Usuário removido!{RESET_COR}")

def visualizar_logs():
    """Exibe os registros de log"""
    if not eh_admin():
        print(f"{COR_ERRO}⚠️ Acesso restrito!{RESET_COR}")
        return
    
    print(f"\n{COR_LOG}=== ÚLTIMOS REGISTROS ===")
    try:
        with open(ARQUIVO_LOG, 'r') as f:
            print(f.read())
    except FileNotFoundError:
        print("Nenhum registro encontrado")
    print("="*50 + RESET_COR)

# ========== FUNÇÕES AUXILIARES ==========
def listar_usuarios():
    """Listagem resumida de usuários"""
    if not eh_admin():
        print(f"{COR_ERRO}⚠️ Acesso restrito!{RESET_COR}")
        return
    
    print(f"\n{COR_ADM}=== USUÁRIOS ===")
    for usuario, dados in usuarios_cadastrados.items():
        tipo = f"{COR_ADM}ADMIN{RESET_COR}" if dados["is_admin"] else f"{COR_USUARIO}ALUNO{RESET_COR}"
        print(f"- {usuario} ({tipo}) | Email: {dados['email']}")
    print("="*25 + RESET_COR)

def visualizar_dados_completos():
    """Exibe todos os dados do JSON"""
    if not eh_admin():
        print(f"{COR_ERRO}⚠️ Acesso restrito!{RESET_COR}")
        return
    
    print(f"\n{COR_ADM}=== DADOS COMPLETOS ===")
    print(json.dumps(usuarios_cadastrados, indent=4, ensure_ascii=False))
    print("="*50 + RESET_COR)

def eh_admin() -> bool:
    return usuario_logado and usuario_logado["is_admin"]

def logout():
    """Encerra a sessão com registro"""
    global usuario_logado
    if usuario_logado:
        registrar_log("Logout", f"Usuário: {usuario_logado['nome']}")
        print(f"\n{COR_ADM}👋 Até logo, {usuario_logado['nome']}!{RESET_COR}")
        usuario_logado = None

# ========== INTERFACE PRINCIPAL ==========
def tela_login_cadastro():
    """Tela adaptável ao status de login"""
    while True:
        print(f"\n{COR_USUARIO}=== {'LOGOUT' if usuario_logado else 'LOGIN'} / CADASTRO ===")
        print(f"1. {'🔓 DESLOGAR' if usuario_logado else '🔑 ENTRAR'}")
        print("2. 📝 CADASTRAR-SE")
        
        if usuario_logado:
            print("3. 👤 VER MEUS DADOS")
            print("4. 💀 DELETAR MINHA CONTA")
            
        print("0. ↩ VOLTAR")
        print("="*25 + RESET_COR)
        
        escolha = input("Escolha: ")

        if escolha == '1':
            if usuario_logado:
                logout()
                break
            else:
                if fazer_login() and eh_admin():
                    menu_admin()
                    break
                    
        elif escolha == '2':
            criar_usuario(is_admin=False)
            
        elif escolha == '3' and usuario_logado:
            mostrar_meus_dados()
            
        elif escolha == '4' and usuario_logado:
            deletar_conta()
            break
            
        elif escolha == '0':
            break
            
        else:
            print(f"{COR_ERRO}❌ Opção inválida!{RESET_COR}")

def mostrar_meus_dados():
    """Exibe dados do usuário logado"""
    if not usuario_logado:
        print(f"{COR_ERRO}⚠️ Nenhum usuário logado!{RESET_COR}")
        return
    
    dados = usuarios_cadastrados[usuario_logado['nome']]
    print(f"\n{COR_USUARIO}=== MEUS DADOS ===")
    print(f"👤 Usuário: {usuario_logado['nome']}")
    print(f"📧 Email: {dados['email']}")
    print(f"🎂 Idade: {dados['idade']}")
    print(f"📅 Cadastro: {dados['data_cadastro'][:10]}")
    print(f"🎓 Cursos: {len(dados['cursos'])} matriculados")
    print("="*25 + RESET_COR)



