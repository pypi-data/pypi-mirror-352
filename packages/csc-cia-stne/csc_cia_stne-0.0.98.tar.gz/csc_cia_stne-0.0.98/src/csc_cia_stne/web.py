# Selenium
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select,WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# Botcity
from botcity.web import WebBot, Browser
from botcity.web.util import element_as_select

# Externa
import requests

# Validador
from pydantic import ValidationError

# Validadores de parametros
from .utilitarios.validations.web_validator import InitParamsValidator,ClickOnScreenValidator,InputValueValidator,SelectValueValidator,VerifyServerValueValidator,NavigateValidator


class web_screen():


    def __init__(self,model:str="selenium",timeout:int=60,headless:bool=True,disable_gpu:bool=True,no_sandbox:bool=True,security:bool=True):
        """
        Inicializa a instância da classe Web.
        Parâmetros:
        - model (str): O modelo a ser utilizado, pode ser "selenium" ou outro modelo suportado.
        - timeout (int): O tempo limite em segundos para aguardar a resposta do navegador.
        - headless (bool): Define se o navegador será executado em modo headless (sem interface gráfica).
        - disable_gpu (bool): Define se a aceleração de hardware do GPU será desabilitada.
        - no_sandbox (bool): Define se o sandbox do navegador será desabilitado.
        - security (bool): Define se a segurança do navegador será habilitada.
        Raises:
        - ValueError: Se ocorrer um erro na validação dos dados de entrada da inicialização da instância.
        """
        
        self.model = model
        self.timeout = timeout
        self.security = security

        try:
        
            InitParamsValidator(model=model,timeout=timeout, headless=headless, disable_gpu=disable_gpu, no_sandbox=no_sandbox, security=security)

        except ValidationError as e:
        
            raise ValueError("Erro na validação dos dados de input da inicialização da instância:", e.errors())

        if self.model.upper() == "SELENIUM":

            try:

                chrome_options = Options()

                if headless:
                    chrome_options.add_argument('--headless')
                if disable_gpu:
                    chrome_options.add_argument('--disable-gpu')
                if no_sandbox:
                    chrome_options.add_argument('--no-sandbox')

                # Criação do drive para selenium
                service = ChromeService(executable_path=ChromeDriverManager().install())

                self.web_bot = webdriver.Chrome(service=service, options=chrome_options)
            
            except Exception as e:

                raise ValueError("Erro na inicialização da classe:", e)
        
        else:

            try:

                # Criação do drive para botcity

                self.web_bot = WebBot()
            
                # Configurar o navegador (por exemplo, Chrome)
                self.web_bot.browser = Browser.CHROME

                self.web_bot.driver_path = ChromeDriverManager().install()

                # Configurar as opções do Chrome
                self.web_bot.headless = headless
                self.web_bot.disable_gpu = disable_gpu
                self.web_bot.no_sandbox = no_sandbox
            
            except Exception as e:

                    raise ValueError("Erro na inicialização da classe:", e)


    def get_bot(self):
        """
        Retorna o objeto web_bot associado a esta instância.
        """

        return self.web_bot


    def verify_server(self,url:str):
        """
        Verifica se o servidor está ativo e acessível.
        Args:
            url (str): A URL do servidor a ser verificado.
        Returns:
            bool: True se o servidor estiver ativo e acessível, False caso contrário.
        """

        try:

            VerifyServerValueValidator(url=url)

        except ValidationError as e:

            raise ValueError("Erro na validação dos dados de input:", e.errors())

        try:

            reply = requests.get(url, verify=self.security)

        except:

            return False
        
        if reply.status_code == 200:

            return True
        
        return False


    def navigate(self,url:str):
        """
        Navega para a URL especificada.
        Args:
            url (str): A URL para navegar.
        Returns:
            dict: Um dicionário contendo informações sobre o sucesso da navegação.
                - 'success' (bool): Indica se a navegação foi bem-sucedida.
                - 'details' (str): Detalhes adicionais sobre a navegação, caso haja algum erro.
                - 'error' (Exception): A exceção ocorrida durante a navegação, caso haja algum erro.
        """

        try:

            NavigateValidator(url=url)

        except ValidationError as e:

            raise ValueError("Erro na validação dos dados de input:", e.errors())

        if not self.verify_server(url):

            return {
                'success': False,
                'details': f"Não foi possível acessar o endereço {url}."
            }
        
        if self.model.upper() == "SELENIUM":

            try:

                self.bot.get(url)

                return {
                        "success": True,
                        "error": None
                    }
                        
            except Exception as e:

                return {
                    "success": False,
                    "details":None,
                    "error": e
                }

        else:

            try:

                self.bot.browse(url)

                return {
                        "success": True,
                        "error": None
                    }
                        
            except Exception as e:

                return {
                    "success": False,
                    "details":None,
                    "error": e
                }


    def click_on_screen(self, target:str):
        """
        Clica em um elemento na tela.
        Parâmetros:
        - target (str): O elemento alvo a ser clicado.
        Retorna:
        Um dicionário com as seguintes chaves:
        - success (bool): Indica se o clique foi realizado com sucesso.
        - details (str): Detalhes adicionais em caso de erro.
        - error (Exception): A exceção ocorrida, se houver.
        Raises:
        Nenhum.
        """

        try:
        
            ClickOnScreenValidator(target=target)

        except ValidationError as e:
        
            raise ValueError("Erro na validação dos dados de input para o click na tela:", e.errors())


        if self.model.upper() == "SELENIUM":

            try:

                WebDriverWait(self.web_bot, self.timeout).until(EC.element_to_be_clickable((By.XPATH, target))).click()

                return {
                    "success": True,
                    "error": None
                }
            
            except EC.NoSuchElementException:

                return {
                    "success": False,
                    "details": f"Elemento {target} não encontrado.",
                    "error": None
                }
            
            except EC.TimeoutException:

                return {
                    "success": False,
                    "details": f"O elemento {target} não foi encontrado dentro do tempo definido",
                    "error": None
                }

            except Exception as e:

                return {
                    "success": False,
                    "details":None,
                    "error": e
                }
            
        else:

            try:

                element_click = self.web_bot.find_element(target, By.XPATH)

                self.web_bot.wait_for_stale_element(
                    element=element_click,
                    timeout=self.timeout
                )

                element_click.click()

                return {
                    "success": True,
                    "error": None
                }
            
            except Exception as e:

                return {
                    "success": False,
                    "details": None,
                    "error": e
                }
            
    
    def input_value(self, target:str, value, clear:bool=True):
        """
        Insere um valor em um elemento de entrada na página web.
        Parâmetros:
        - target (str): O XPath do elemento de entrada.
        - value: O valor a ser inserido no elemento de entrada.
        - clear (bool): Indica se o elemento de entrada deve ser limpo antes de inserir o valor (padrão: True).
        Retorna:
        Um dicionário com as seguintes chaves:
        - "success" (bool): Indica se a operação foi bem-sucedida.
        - "details" (str): Detalhes adicionais sobre o resultado da operação.
        - "error" (Exception): A exceção ocorrida, se houver.
        """

        try:
        
            InputValueValidator(target=target,clear=clear)

        except ValidationError as e:
        
            raise ValueError("Erro na validação dos dados de input para realizar o input na tela:", e.errors())

        if self.model.upper() == "SELENIUM":

            try:

                element_input = WebDriverWait(self.web_bot, self.timeout).until(EC.EC.visibility_of_element_located(By.XPATH,target))

                if clear:

                    element_input.clear()

                element_input.send_keys(value)

            except EC.NoSuchElementException:

                return {
                    "success": False,
                    "details": f"Elemento {target} não encontrado.",
                    "error": None
                }
            
            except EC.TimeoutException:

                return {
                    "success": False,
                    "details": f"O elemento {target} não foi encontrado dentro do tempo definido",
                    "error": None
                }

            except Exception as e:

                return {
                    "success": False,
                    "details":None,
                    "error": e
                }
            
        else:

            try:

                element_input = self.web_bot.find_element(target, By.XPATH)

                self.web_bot.wait_for_stale_element(
                    element=element_input,
                    timeout=self.timeout
                )

                if clear:

                    element_input.clear()

                element_input.send_keys(value)

            except Exception as e:

                return {
                    "success": False,
                    "details":None,
                    "error": e
                }
            

    def select_value(self, target:str, value):
        """
        Seleciona um valor em um elemento de seleção (select) na página web.
        Args:
            target (str): O seletor XPath do elemento de seleção.
            value: O valor a ser selecionado.
        Returns:
            dict: Um dicionário com as seguintes chaves:
                - "success" (bool): Indica se a seleção foi bem-sucedida.
                - "details" (str): Detalhes adicionais sobre o resultado da seleção.
                - "error" (Exception): A exceção ocorrida, se houver.
        Raises:
            ValueError: Se ocorrer um erro na validação dos dados para realizar o select na tela.
        Note:
            - Se o modelo for "SELENIUM", o método usará a biblioteca Selenium para realizar a seleção.
            - Caso contrário, o método usará a biblioteca web_bot para realizar a seleção.
        """

        try:
        
            SelectValueValidator(target=target)

        except ValidationError as e:
        
            raise ValueError("Erro na validação dos dados para realizar o select na tela:", e.errors())

        if self.model.upper() == "SELENIUM":

            try:

                element_select = WebDriverWait(self.web_bot, self.timeout).until(EC.element_to_be_clickable((By.XPATH, target)))

                element_select = Select(element_select)

                element_select.select_by_value(value)

            except EC.NoSuchElementException:

                return {
                    "success": False,
                    "details": f"Elemento {target} não encontrado.",
                    "error": None
                }
            
            except EC.TimeoutException:

                return {
                    "success": False,
                    "details": f"O elemento {target} não foi encontrado dentro do tempo definido",
                    "error": None
                }

            except Exception as e:

                return {
                    "success": False,
                    "details":None,
                    "error": e
                }
            
        else:

            try:

                element_select = self.web_bot.find_element(target, By.XPATH)

                self.web_bot.wait_for_stale_element(
                    element=element_select,
                    timeout=self.timeout
                )

                element_select = element_as_select(element_select)

                element_select.select_by_value(value)

            except Exception as e:

                return {
                    "success": False,
                    "details":None,
                    "error": e
                }
            
    
    def close(self):
        """
        Fecha o navegador web.
        Retorna um dicionário com as seguintes chaves:
        - 'success': Indica se o fechamento foi bem-sucedido (True) ou não (False).
        - 'details': Detalhes adicionais, caso ocorra algum erro durante o fechamento.
        - 'error': Exceção ocorrida durante o fechamento, caso haja.
        Se o modelo for 'SELENIUM', o método utiliza o método 'quit()' do objeto 'web_bot' para fechar o navegador.
        Caso contrário, utiliza o método 'stop_browser()'.
        Exemplo de retorno em caso de sucesso:
        {
            'success': True,
            'error': None
        Exemplo de retorno em caso de erro:
        {
            'success': False,
            'details': None,
            'error': Exception
        """

        if self.model.upper() == "SELENIUM":

            try:

                self.web_bot.quit()

                return {
                    "success": True,
                    "error": None
                }
            
            except Exception as e:

                return {
                    "success": False,
                    "details": None,
                    "error": e
                }
            
        else:

            try:

                self.web_bot.stop_browser()

                return {
                    "success": True,
                    "error": None
                }
            
            except Exception as e:

                return {
                    "success": False,
                    "details": None,
                    "error": e
                }