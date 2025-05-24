import json
import os
from datetime import datetime
from usuarios.usuarios import get_usuario_logado, eh_admin, registrar_log
from cursos.cursos import cursos_disponiveis, salvar_cursos


# ========== CONFIGURAÇÕES ==========
COR_SUCESSO = "\033[1;32m"
COR_ERRO = "\033[1;31m"
COR_TITULO = "\033[1;36m"
COR_ALERTA = "\033[1;33m"
RESET_COR = "\033[0m"

# ========== CONSTANTES DE ERRO ==========
ERRO_PERMISSAO = f"{COR_ERRO}🚫 Acesso restrito a administradores!{RESET_COR}"
ERRO_CURSO_NAO_ENCONTRADO = f"{COR_ERRO}❌ Curso não encontrado!{RESET_COR}"
ERRO_MODULO_NAO_ENCONTRADO = f"{COR_ERRO}❌ Módulo não encontrado!{RESET_COR}"


# ========== FUNÇÕES PRINCIPAIS ==========
def tela_modulos():
    """Menu principal de módulos"""
    if not get_usuario_logado:
        print(f"{COR_ERRO}⚠️ Faça login primeiro!{RESET_COR}")
        input("Pressione Enter para voltar...")
        return
    
    if not eh_admin():
        print(ERRO_PERMISSAO)
        input("Pressione Enter para voltar...")
        return

    while True:
        print(f"\n{COR_TITULO}=== GERENCIAMENTO DE MÓDULOS ===")
        print("1. 📋 Listar módulos por curso")
        print("2. ➕ Adicionar módulo")
        print("3. ✏️ Editar módulo")
        print("4. 🗑️ Remover módulo")
        print("0. ↩ Voltar")
        print("="*40 + RESET_COR)
        
        escolha = input("Escolha: ").strip()

        if escolha == '1':
            listar_modulos_por_curso()
        elif escolha == '2':
            adicionar_modulo()
        elif escolha == '3':
            editar_modulo()
        elif escolha == '4':
            remover_modulo()
        elif escolha == '0':
            break
        else:
            print(f"{COR_ERRO}❌ Opção inválida!{RESET_COR}")
            input("Pressione Enter para continuar...")

# ========== OPERAÇÕES DE MÓDULOS ==========
def adicionar_modulo():
    """Adiciona novo módulo a um curso existente"""
    print(f"\n{COR_TITULO}=== ADICIONAR MÓDULO ===")
    
    from cursos.cursos import listar_cursos
    listar_cursos()
    
    id_curso = input("\nID do curso: ").strip()
    if id_curso not in cursos_disponiveis:
        print(ERRO_CURSO_NAO_ENCONTRADO)
        input("Pressione Enter para voltar...")
        return
    
    nome_modulo = input("Nome do módulo: ").strip()
    if not nome_modulo:
        print(f"{COR_ERRO}❌ Nome não pode ser vazio!{RESET_COR}")
        input("Pressione Enter para voltar...")
        return
    
    try:
        novo_modulo = {
            "nome": nome_modulo,
            "criado_por": get_usuario_logado["nome"],
            "data_criacao": datetime.now().isoformat(),
            "aulas": []
        }
        
        cursos_disponiveis[id_curso]["modulos"].append(novo_modulo)
        salvar_cursos()
        
        registrar_log("Módulo adicionado", 
                     f"Curso: {cursos_disponiveis[id_curso]['nome']} | Módulo: {nome_modulo}")
        print(f"\n{COR_SUCESSO}✅ Módulo adicionado com sucesso!{RESET_COR}")
    except Exception as e:
        print(f"{COR_ERRO}❌ Erro ao adicionar módulo: {e}{RESET_COR}")
    finally:
        input("Pressione Enter para voltar...")

def editar_modulo():
    """Edita um módulo existente"""
    print(f"\n{COR_TITULO}=== EDITAR MÓDULO ===")
    
    id_curso, idx_modulo = selecionar_modulo()
    if id_curso is None:
        return
    
    try:
        modulo = cursos_disponiveis[id_curso]["modulos"][idx_modulo]
        print(f"\nEditando: {modulo['nome']}")
        print("Deixe em branco para manter o valor atual\n")
        
        novo_nome = input(f"Novo nome [{modulo['nome']}]: ").strip()
        
        if novo_nome:
            cursos_disponiveis[id_curso]["modulos"][idx_modulo]["nome"] = novo_nome
            cursos_disponiveis[id_curso]["modulos"][idx_modulo]["ultima_edicao"] = {
                "por": get_usuario_logado["nome"],
                "em": datetime.now().isoformat()
            }
            salvar_cursos()
            registrar_log()("Módulo editado", f"ID Curso: {id_curso} | Novo nome: {novo_nome}")
            print(f"\n{COR_SUCESSO}✅ Módulo atualizado!{RESET_COR}")
        else:
            print(f"{COR_ALERTA}⚠️ Nenhuma alteração realizada.{RESET_COR}")
    except Exception as e:
        print(f"{COR_ERRO}❌ Erro ao editar módulo: {e}{RESET_COR}")
    finally:
        input("Pressione Enter para voltar...")

def remover_modulo():
    """Remove um módulo de um curso"""
    print(f"\n{COR_TITULO}=== REMOVER MÓDULO ===")
    
    id_curso, idx_modulo = selecionar_modulo()
    if id_curso is None:
        return
    
    try:
        modulo = cursos_disponiveis[id_curso]["modulos"][idx_modulo]
        confirmacao = input(f"\nTem certeza que deseja remover '{modulo['nome']}'? (S/N): ").upper()
        
        if confirmacao == 'S':
            modulo_removido = cursos_disponiveis[id_curso]["modulos"].pop(idx_modulo)
            salvar_cursos()
            registrar_log()("Módulo removido", 
                         f"Curso: {cursos_disponiveis[id_curso]['nome']} | Módulo: {modulo_removido['nome']}")
            print(f"\n{COR_SUCESSO}✅ Módulo removido com sucesso!{RESET_COR}")
        else:
            print(f"{COR_ALERTA}❌ Operação cancelada.{RESET_COR}")
    except Exception as e:
        print(f"{COR_ERRO}❌ Erro ao remover módulo: {e}{RESET_COR}")
    finally:
        input("Pressione Enter para voltar...")

# ========== FUNÇÕES AUXILIARES ==========
def listar_modulos_por_curso():
    """Lista todos os módulos organizados por curso"""
    try:
        print(f"\n{COR_TITULO}=== MÓDULOS POR CURSO ===")
        for id_curso, curso in cursos_disponiveis.items():
            print(f"\n📚 {curso['nome']} ({len(curso['modulos'])} módulos):")
            for idx, modulo in enumerate(curso["modulos"], 1):
                print(f"   {idx}. {modulo['nome']}")
                print(f"      Criado por: {modulo['criado_por']}")
                print(f"      Data: {modulo['data_criacao'][:10]}")
        print("="*50 + RESET_COR)
    except Exception as e:
        print(f"{COR_ERRO}❌ Erro ao listar módulos: {e}{RESET_COR}")
    finally:
        input("\nPressione Enter para continuar...")

def selecionar_modulo():
    """Seleciona um módulo específico com validação reforçada"""
    from cursos.cursos import listar_cursos
    
    try:
        listar_cursos()
        id_curso = input("\nID do curso: ").strip()
        
        if id_curso not in cursos_disponiveis:
            print(ERRO_CURSO_NAO_ENCONTRADO)
            return None, None
        
        if not cursos_disponiveis[id_curso]["modulos"]:
            print(ERRO_MODULO_NAO_ENCONTRADO)
            return None, None
        
        print(f"\nMódulos disponíveis em {cursos_disponiveis[id_curso]['nome']}:")
        for idx, modulo in enumerate(cursos_disponiveis[id_curso]["modulos"], 1):
            print(f"{idx}. {modulo['nome']}")
        
        idx_modulo = int(input("\nNúmero do módulo: ")) - 1
        if idx_modulo < 0 or idx_modulo >= len(cursos_disponiveis[id_curso]["modulos"]):
            raise ValueError("Índice inválido")
            
        return id_curso, idx_modulo
        
    except ValueError:
        print(f"{COR_ERRO}❌ Digite um número válido da lista!{RESET_COR}")
        return None, None
    except Exception as e:
        print(f"{COR_ERRO}❌ Erro ao selecionar módulo: {e}{RESET_COR}")
        return None, None