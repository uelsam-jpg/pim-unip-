# certificados.py
from fpdf import FPDF
import hashlib
from datetime import datetime
import os

# ========== CONFIGURAÇÕES DE CORES ==========
COR_TITULO = "\033[1;35m"  # Roxo
COR_MENU = "\033[1;36m"    # Azul claro
COR_SUCESSO = "\033[1;32m" # Verde
COR_ERRO = "\033[1;31m"    # Vermelho
COR_ALERTA = "\033[1;33m"  # Amarelo
COR_USUARIO = "\033[1;34m" # Azul
RESET_COR = "\033[0m"

# ========== CONFIGURAÇÕES DE PASTAS ==========
PASTA_CERTIFICADOS = "certificados"
os.makedirs(PASTA_CERTIFICADOS, exist_ok=True)

# ========== FUNÇÕES DE ACESSO SEGURO ==========
def get_usuario_logado():
    """Obtém o estado ATUAL do usuário logado"""
    from usuarios.usuarios import usuario_logado
    return usuario_logado

def get_usuarios_cadastrados():
    """Obtém os dados ATUALIZADOS dos usuários (agora com reload)"""
    from usuarios.usuarios import carregar_usuarios  # Importa a função de carregar
    return carregar_usuarios()  # Retorna dados frescos do JSON

def get_cursos_disponiveis():
    """Obtém os cursos atualizados"""
    from cursos.cursos import cursos_disponiveis
    return cursos_disponiveis

def registrar_log(acao: str, detalhes: str = ""):
    """Registra log usando a função original"""
    from usuarios.usuarios import registrar_log as original_registrar_log
    usuario = get_usuario_logado()
    original_registrar_log(acao, f"{detalhes} | Usuário: {usuario['nome'] if usuario else 'SISTEMA'}")

# ========== CLASSE CERTIFICADO ==========
class Certificado:
    def __init__(self):
        self.codigo = None
        self.caminho = None

    def gerar(self, nome_aluno: str, nome_curso: str, carga_horaria: str):
        """Gera um certificado em PDF"""
        self._gerar_codigo(nome_aluno, nome_curso)
        self.caminho = f"{PASTA_CERTIFICADOS}/{self.codigo}.pdf"

        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_font("Arial", size=24)
        pdf.set_text_color(10, 50, 150)
        pdf.cell(0, 40, txt="CERTIFICADO", ln=True, align='C')
        pdf.ln(20)
        
        pdf.set_font("Arial", size=16)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 10, 
            f"Certificamos que {nome_aluno} concluiu com êxito o curso "
            f"'{nome_curso}' com carga horária de {carga_horaria}.\n\n"
            f"Data de emissão: {datetime.now().strftime('%d/%m/%Y')}\n\n"
            f"Código de validação: {self.codigo}",
            align='C')
        
        pdf.set_y(-30)
        pdf.set_font("Arial", style='I', size=12)
        pdf.cell(0, 10, txt="Este certificado pode ser validado em nossa plataforma", ln=True, align='C')
        
        pdf.output(self.caminho)
        return self.caminho

    def _gerar_codigo(self, nome_aluno: str, nome_curso: str):
        """Cria um código único baseado em hash"""
        base = f"{nome_aluno}{nome_curso}{datetime.now()}"
        self.codigo = "CERT-" + hashlib.sha256(base.encode()).hexdigest()[:12].upper()

# ========== FUNÇÕES PRINCIPAIS ==========
def tela_certificados():
    """Menu principal de certificados"""
    usuario = get_usuario_logado()
    if not usuario:
        print(f"\n{COR_ERRO}⚠️ VOCÊ PRECISA ESTAR LOGADO!{RESET_COR}")
        return

    while True:
        print(f"\n{COR_TITULO}=== MEUS CERTIFICADOS ===")
        print(f"{COR_MENU}1. 🖨️ Gerar certificado")
        print("2. 📂 Ver meus certificados")
        print(f"0. ↩ Voltar{RESET_COR}")
        print("="*40)
        
        escolha = input("Escolha: ")

        if escolha == '1':
            gerar_certificado_menu()
        elif escolha == '2':
            listar_certificados()
        elif escolha == '0':
            break
        else:
            print(f"{COR_ERRO}❌ Opção inválida!{RESET_COR}")

def gerar_certificado_menu():
    """Interface para gerar certificado"""
    usuario = get_usuario_logado()
    if not usuario:
        print(f"{COR_ERRO}⚠️ Você precisa estar logado!{RESET_COR}")
        return
    
    dados = get_usuarios_cadastrados()
    usuario_data = dados[usuario['nome']]
    
    if not usuario_data.get('cursos', []):
        print(f"{COR_ALERTA}⚠️ Você não está matriculado em nenhum curso!{RESET_COR}")
        return
    
    cursos = get_cursos_disponiveis()
    
    print(f"\n{COR_TITULO}=== GERAR CERTIFICADO ===")
    print(f"{COR_MENU}Cursos disponíveis para certificação:{RESET_COR}")
    
    for curso_id in usuario_data['cursos']:
        if curso_id in cursos:
            print(f"- {curso_id}: {cursos[curso_id]['nome']} ({cursos[curso_id]['carga_horaria']})")
    
    id_curso = input("\nDigite o ID do curso: ").strip()
    
    if id_curso not in cursos:
        print(f"{COR_ERRO}❌ Curso inválido!{RESET_COR}")
        return
    
    if not verificar_conclusao(usuario['nome'], id_curso):
        print(f"{COR_ERRO}❌ Você não concluiu este curso!{RESET_COR}")
        return
    
    try:
        cert = Certificado()
        caminho = cert.gerar(
            nome_aluno=usuario['nome'],
            nome_curso=cursos[id_curso]['nome'],
            carga_horaria=cursos[id_curso]['carga_horaria']
        )
        
        if 'certificados' not in usuario_data:
            usuario_data['certificados'] = []
            
        usuario_data['certificados'].append({
            'curso': id_curso,
            'codigo': cert.codigo,
            'data': datetime.now().isoformat(),
            'caminho': caminho
        })
        
        # Atualiza no arquivo JSON
        from usuarios.usuarios import salvar_usuarios
        salvar_usuarios()
        
        registrar_log("Certificado emitido", f"Curso: {id_curso}")
        print(f"\n{COR_SUCESSO}✅ Certificado gerado com sucesso!{RESET_COR}")
        print(f"{COR_MENU}Caminho: {caminho}{RESET_COR}")
        
    except Exception as e:
        print(f"{COR_ERRO}❌ Erro ao gerar certificado: {e}{RESET_COR}")

def listar_certificados():
    """Lista todos os certificados do usuário"""
    usuario = get_usuario_logado()
    if not usuario:
        print(f"{COR_ERRO}⚠️ Você precisa estar logado!{RESET_COR}")
        return
    
    dados = get_usuarios_cadastrados()
    usuario_data = dados[usuario['nome']]
    
    if not usuario_data.get('certificados', []):
        print(f"{COR_ALERTA}⚠️ Nenhum certificado encontrado!{RESET_COR}")
        return
    
    cursos = get_cursos_disponiveis()
    
    print(f"\n{COR_TITULO}=== MEUS CERTIFICADOS ===")
    for idx, cert in enumerate(usuario_data['certificados'], 1):
        curso_nome = cursos[cert['curso']]['nome'] if cert['curso'] in cursos else "Curso Removido"
        print(f"{COR_MENU}{idx}. {curso_nome}")
        print(f"{COR_USUARIO}   Código: {cert['codigo']}")
        print(f"   Data: {cert['data'][:10]}{RESET_COR}")
    print("="*50)

# ========== FUNÇÃO AUXILIAR ==========
def verificar_conclusao(id_aluno: str, id_curso: str) -> bool:
    """Verifica se o aluno concluiu o curso (IMPLEMENTE SUA LÓGICA AQUI)"""
    # Exemplo simplificado - adapte para seu sistema
    dados = get_usuarios_cadastrados()
    cursos = get_cursos_disponiveis()
    
    if id_aluno not in dados or id_curso not in cursos:
        return False
    
    # Verifica se completou todos os módulos
    modulos_concluidos = dados[id_aluno].get('modulos_concluidos', {}).get(id_curso, [])
    return len(modulos_concluidos) == len(cursos[id_curso].get('modulos', []))