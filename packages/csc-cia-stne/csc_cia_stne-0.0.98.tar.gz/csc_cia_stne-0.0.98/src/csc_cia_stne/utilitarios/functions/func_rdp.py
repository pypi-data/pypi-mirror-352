# import platform
# import subprocess
# import time
# import pyautogui
# import psutil
# import pygetwindow as gw
# import logging
# pyautogui.USE_MOUSEINFO = False
# log = logging.getLogger('__main__')

# def obter_ip_conexao_rdp():
#     """Retorna o ip da conexão RDP

#     Returns:
#         str: ip
#     """
    
#     for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    
#         if proc.info['name'] == 'mstsc.exe' and proc.info['cmdline']:
    
#             for arg in proc.info['cmdline']:
    
#                 if arg.startswith("/v:"):  # O argumento '/v:' contém o IP
    
#                     return arg.replace("/v:", "").strip()
    
#     return None

# def verificar_sessao_rdp()->bool:
#     """Verifica se a sessão RDP está ativa"""
#     # Verifica se o processo mstsc.exe está rodando
#     for proc in psutil.process_iter(['name']):
#         if proc.info['name'] == 'mstsc.exe':
#             #return True
    
#             # Verifica se a janela da Área de Trabalho Remota está aberta
#             for window in gw.getAllTitles():
#                 if "Área de Trabalho Remota" in window or "Remote Desktop" in window:
#                     return True
    
#     return False

# def conectar_rdp(host:str, usuario:str, senha:str)->bool:
#     """Conecta via RDP em uma máquina remota
    
#     Args:
    
#             host (str): ip/host destino
#         usuario (str): usuário
#         senha (str): senha
    
#     Returns:
#         bool: True/False
#     """
    
#     sistema = platform.system()

#     if sistema == "Windows":

#         try:
            
#             def criar_arquivo_rdp(host, usuario, caminho_rdp="conexao.rdp")->str:
#                 """Cria um arquivo .rdp para conexão RDP
#                 Args:
#                     host (str): host do computador remoto
#                     usuario (str): Usuário
#                     caminho_rdp (str): Caminho do arquivo .rdp
#                 Returns:
#                     str: Caminho do arquivo .rdp
#                 """
#                 conteudo_rdp = f"""
#                 screen mode id:i:2
#                 desktopwidth:i:1920
#                 desktopheight:i:1080
#                 session bpp:i:32
#                 winposstr:s:0,1,0,0,800,600
#                 full address:s:{host}
#                 username:s:{usuario}
#                 """
#                 with open(caminho_rdp, "w") as arquivo:
#                     arquivo.write(conteudo_rdp.strip())
                
#                 return caminho_rdp

#             caminho_rdp = criar_arquivo_rdp(host, usuario)
#             subprocess.run(f"start mstsc {caminho_rdp}", shell=True)
#             # Espera a conexão ser feita e confirma que realmente quer fazer a conexão com o computador remoto de forma insegura (certificado)
#             time.sleep(10)
#             pyautogui.press('left')
#             pyautogui.press('enter')
#             # Espera 3 segundos para digitar a senha e dar enter
#             time.sleep(3)
#             pyautogui.write(senha)
#             pyautogui.press('enter')
#             # Espera 5 segundos para aparecer a tela sobre o certificado e aceitar a conexão de forma insegura (certificado)
#             time.sleep(5)
#             pyautogui.press('left')
#             pyautogui.press('enter')
#             # Aguarda 5 segundos e verifica se a conexão foi feita com sucesso
#             time.sleep(5)
#             return verificar_sessao_rdp()
        
#         except Exception as e:

#             log.error(f"Erro ao conectar à área de trabalho remota:\n{e}")
#             return False
    
#     elif sistema == "Linux":
        
#         # Comando para executar a conexao com o xfreerdp
#         # Para instalar: sudo apt install freerdp2-x11
#         comando_rdp = f"""xfreerdp /u:{usuario} /p:{senha} /v:{host} /size:1920x1080"""

#         # Executar o comando e capturar saída
#         try:
            
#             processo_rdp = subprocess.Popen(
#                 comando_rdp,
#                 shell=True,
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE,
#                 text=True
#             )
        
#         except Exception as e:
        
#             raise Exception(f"Falha ao executar o comando de conexão RDP no Linux. Você possui o xfreerdp instalado? (sudo apt install freerdp2-x11)\nErro: {str(e)}")
        
#         # Aguarda 10 segundos, para aparecer o banner azul
#         time.sleep(10)

#         # Se a conexão foi bem-sucedida, retornar True
#         if processo_rdp.poll() is None:
            
#             # Clica no 'enter', no banner azul
#             pyautogui.press('enter')
#             return True

#         else:

#             return False
        
#     else:

#         raise Exception("Sistema operacional não suportado (Somente 'Windows' ou 'Linux').")

