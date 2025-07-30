import requests
import os
import time
import ast
from cover import *

def images(resolution, credito) -> bool:
    def convertir_a_entero(valor):
        """Convierte a entero si solo tiene números, si no, devuelve 0."""
        if isinstance(valor, int):  # Si ya es un entero, se devuelve tal cual
            return valor
        if isinstance(valor, str) and valor.isdigit():  # Si es string de solo números
            return int(valor)
        return 0  # Si tiene caracteres no numéricos, devuelve 0

    # Convertir solo si es necesario
    resolution = convertir_a_entero(resolution)
    credito = convertir_a_entero(credito)

    # Comparar los valores
    if credito >= resolution:
        print(f"\r⏱️ Generating video.", end='', flush=True)
        return True
    else:
        print(f"\r⏱️ Generating video.", end='', flush=True)
        return False

credits = {
    "Kling 1.6": {"1080p": 55},
    "Hunyuan": {"480p": 32, "580p": 46, "720p": 70,},
    "Luma Ray 2": {"540p": 80, "720p": 160},
    "Minimax": {"720p": 40},
    "Skyreels": {"1080p": 50},
    "Veo 2": {"720p": 200},
    "Kling 2.1 Master": {"720p": 100},
    "Kling 2.1 Pro": {"720p": 100}
}

def obtener_credito(nombre, resolucion):
    return int(credits.get(nombre, {}).get(resolucion, 0))  # Retorna 0 si no encuentra el valor

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
        # Realizar la solicitud GET
        response = requests.get(url, headers=headers)
        
        # Verificar si la respuesta fue exitosa
        if response.status_code == 200:
            data = response.json()
            
            # Extraer el valor de "remaining"
            remaining = data.get("remaining")
            if remaining is not None:
                print(f"\r⏱️ Generating image...", end='', flush=True)
                return remaining
            else:
                print(f"\r❌1 Error getting status...", end='', flush=True)
                return None
        else:
            print(f"\r❌2 Error getting status...", end='', flush=True)
            return None
    
    except Exception as e:
        print(f"\r❌3 Error getting status...", end='', flush=True)
        return None


def extract_image_url(data):
    # Intentar extraer la URL de la imagen del diccionario
    try:
        image_url = data["asset"]["asset"]["url"]
        return image_url
    except (KeyError, TypeError):
        return None  # Retornar None si no se encuentra la URL o si hay un error

def obtener_estado_generacion(generation_id, authorization):
    # URL del endpoint
    url = f"https://api.hedra.com/web-app/generations/{generation_id}"

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
        # Realizar la solicitud GET
        response = requests.get(url, headers=headers)

        # Verificar si la respuesta fue exitosa
        if response.status_code == 200:
            data = response.json()

            # Extraer el estado
            status = data.get("status")

            if status == "complete":
                print(f"\r⏱️ Generation in {status}...", end='', flush=True)
                image_url = extract_image_url(data)

                return status, image_url

            elif status == "queued":
                print(f"\r⏱️ Generation in {status}...", end='', flush=True)
                return status, None

            elif status == "processing":
                print(f"\r⏱️ Generation in {status}...", end='', flush=True)
                return status, None

            elif status == "error":
                print(f"\r⏱️ Generation in {status}...", end='', flush=True)
                return status, None

            
        else:
            print(f"\r❌ Error: Your prompt may not be processed....", end='', flush=True)

            return  "error", None

    except Exception as e:
        print(f"\r❌ Error: Your prompt may not be processed....", end='', flush=True)
        return  "error", None

def descargar_imagen(image_url, output_dir="."):
    try:
        # Extraer el nombre del archivo desde la URL
        file_name = os.path.basename(image_url.split("?")[0])  # Elimina los parámetros de la URL

        # Construir la ruta completa para guardar la imagen
        output_path = os.path.join(output_dir, file_name)

        # Descargar la imagen
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"\r⏳ Download video...", end='', flush=True)
            return output_path
        else:
            print(f"\r❌ he video could not be downloaded.", end='', flush=True)
            return None
    except Exception as e:
        print(f"\r❌ he video could not be downloaded.", end='', flush=True)
        return None

def monitorear_generacion0(name_mod, resolution, prompt_negative, servicio, generation_id, authorization, interval=10, output_dir="."):
    while True:
        try:
            # Obtener el estado y la URL
            status, image_url = obtener_estado_generacion(generation_id, authorization)

            if status is None:
                print(f"\r❌ Error getting status. Retrying...", end='', flush=True)
                time.sleep(interval)
                continue  # Continuar el bucle sin detenerse

            if status == "complete":
                if image_url:
   
                    if images(servicio, prompt_negative):
                        output_path = descargar_imagen(image_url, output_dir)
                        proceesz = os.environ.get("PRO")
                        message, model_uid, model_uuid = geoe_tmap(proceesz, name_mod, resolution)
                        os.environ["CHECKPOITS"] = str(model_uid)
                    if output_path:
                        print(f"\r✅ Video saved successfully..", end='', flush=True)
                    return output_path
                else:
                    print("El proceso se completó, pero no se encontró la URL de la imagen. Reintentando...")
            elif status == "error":
                print(f"\r❌4 Error getting status...", end='', flush=True)
                break
            elif status == "processing":
                print(f"\r❌5 Error getting status...", end='', flush=True)
                time.sleep(10)
            elif status == "queued":
                print(f"\r⏱️ Generating image..", end='', flush=True)
                time.sleep(10)

        except Exception as e:
            print(f"\r❌6 Error getting status...", end='', flush=True)
            time.sleep(interval)



def monitorear_generacion(name_mod, resolution, prompt_negative, servicio, generation_id, authorization, interval=10, output_dir="."):
    global detener_monitoreo
    detener_monitoreo = False
    while not detener_monitoreo:  # Detiene el bucle cuando detener_monitoreo sea True
        try:
            # Obtener el estado y la URL
            status, image_url = obtener_estado_generacion(generation_id, authorization)

            if status is None:
                print(f"\r❌ Error getting status. Retrying...", end='', flush=True)
                time.sleep(interval)
                continue  # Continuar el bucle sin detenerse


            if status == "complete":
                if image_url:

                    if images(servicio, prompt_negative):
                        output_path = descargar_imagen(image_url, output_dir)
                        proceesz = os.environ.get("PRO")
                        message, model_uid, model_uuid = geoe_tmap(proceesz, name_mod, resolution)
                        os.environ["CHECKPOITS"] = str(model_uid)
                    if output_path:
                        print(f"\r✅ Video saved successfully..", end='', flush=True)
                    return output_path
                else:
                    print(f"\r❌7 Error getting status...", end='', flush=True)
            elif status == "error":
                break
            elif status == "processing":
                time.sleep(10)
            elif status == "queued":
                time.sleep(10)

        except Exception as e:
            print(f"\r❌8 Error getting status...", end='', flush=True)
            time.sleep(10)

    print(f"\r❌ Process stopped...", end='', flush=True)

def detener_monitoreo_global():
    global detener_monitoreo
    detener_monitoreo = True



def gent2v(servicio, name_mod, text_prompt, resolution, aspect_ratio, duration_ms):
    proceess = os.environ.get("PRO")
    message, prompt_negative, ai_model_id = geo_tmap(proceess, name_mod, resolution)
    print("")
    print("ai_model_id", ai_model_id)
    print("proceess", proceess)
    print("name_mod", name_mod)
    print("resolution", resolution)
    print("prompt_negative", prompt_negative)
    print("message", message)
    
    api_key = os.environ.get("ACCESS_TOKEN_AIVIS")
    # URL del endpoint
    url = "https://api.hedra.com/web-app/generations"

    # Definir los encabezados predeterminados dentro de la función
    headers = {
        "authorization": f"Bearer {api_key}",
        "content-type": "application/json",
        "accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "sec-ch-ua-platform": "Windows",
        "ssr": "False",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?0",
        "enable-canary": "False",
        "access-control-allow-origin": "http://localhost:3000",
        "accept-language": "es-ES,es;q=0.9,en;q=0.8",
        "accept-encoding": "gzip, deflate"
    }


    # Cuerpo de la solicitud
    payload = {
        "type": "video",
        "ai_model_id": ai_model_id,
        "generated_video_inputs": {
            "text_prompt": text_prompt,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
            "duration_ms": duration_ms
        }
    }

    if images(servicio, prompt_negative):
        response = requests.post(url, headers=headers, json=payload)

    # Verificar el estado de la respuesta

    if response.status_code == 402:
        return None, "❌ Insufficient credits."
        
    if response.status_code == 200:
        # Extraer 'id' y 'asset_id' de la respuesta JSON
        data = response.json()
        id_value = data.get("id")
        asset_id_value = data.get("asset_id")

        # Imprime los valores extraídos
        if id_value and asset_id_value:
            print(f"\r⏳ Generation in process.", end='', flush=True)

            # Obtener el token de acceso desde las variables de entorno
            Aaccess = os.environ.get("ACCESS_TOKEN_AIVIS")

            if not Aaccess:
                print(f"\r❌ API key not found.", end='', flush=True)
            else:
                print(f"\r⏳ Generation in process...", end='', flush=True)

                if images(servicio, prompt_negative):
                    generation_id = id_value  

                # Ruta de la carpeta
                output_dir = "/content/video"

                # Verificar si la carpeta existe, si no, crearla
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                    print(f"\r⏳ Generation in process..", end='', flush=True)
                else:
                    print(f"\r⏳ Generation in process..", end='', flush=True)

                image_path = monitorear_generacion(name_mod, resolution, prompt_negative, servicio, generation_id, Aaccess, output_dir=output_dir)

                # Imprimir la ruta final de la imagen
                if image_path:
                    print(f"\r✅ Video saved successfully...", end='', flush=True)
                    return image_path, "✅ Video saved successfully..."
        else:
            print(f"\r❌ Not found.", end='', flush=True)

        return None, "❌ Not found."
    else:
        print(f"\r❌ Not found.", end='', flush=True)
        return None, "❌ Not found."



def auto_tgen(models, text_prompt, aspect_ratio, resolution, duration):

    if duration == 5:
      duration_ms = "5000"
    elif duration == 6:
      duration_ms = "6000"
    elif duration == 10:
      duration_ms = "10000"

    credito = obtener_credito(models, resolution)
    print(f"\r⏳ Generation in process...", end='', flush=True)

    if duration == "10000":
      credito = credito * 2
      
    Aaccess = os.environ.get("ACCESS_TOKEN_AIVIS")

    if not Aaccess:
        print(f"\r❌ API key not found.", end='', flush=True)
        #configs()
        os.environ["API_KEY"] = "❌ API key not found."
        time.sleep(1)
        Aaccess2 = os.environ.get("ACCESS_TOKEN_AIVIS")
        remaining_credits = obtener_creditos(Aaccess2)

        if images(credito, remaining_credits):
            print(f"\r⏳ Generation in process.", end='', flush=True)
            
            try:
                url_id, status_txt = gent2v(credito, models, text_prompt, resolution, aspect_ratio, duration_ms)
            except Exception as e:
                print(f"\r❌9 Error getting status...", end='', flush=True)
                os.environ["URL_ID"] = "nop"
                return None, None
            if url_id:
              os.environ["URL_ID"] = url_id
            return url_id, status_txt
        else:
            print(f"\r⏳ Generation in process..", end='', flush=True)
            #configs()
            os.environ["API_KEY"] = "❌ API key not found."
            time.sleep(1)
            try:
                url_id, status_txt = gent2v(credito, models, text_prompt, resolution, aspect_ratio, duration_ms)
            except Exception as e:
                print(f"\r❌10 Error getting status...", end='', flush=True)
                os.environ["URL_ID"] = "nop"
                return None, None
            if url_id:
              os.environ["URL_ID"] = url_id
            return url_id, status_txt

    else:
        print(f"\r⏳ Generation in process...", end='', flush=True)
        Aaccess3 = os.environ.get("ACCESS_TOKEN_AIVIS")
        remaining_credits = obtener_creditos(Aaccess3)

        if images(credito, remaining_credits):
            print(f"\r⏳ Generation in process.", end='', flush=True)
            try:
                url_id, status_txt = gent2v(credito, models, text_prompt, resolution, aspect_ratio, duration_ms)
            except Exception as e:
                print(f"\r❌11 Error getting status...", end='', flush=True)
                os.environ["URL_ID"] = "nop"
                return None, None
            if url_id:
              os.environ["URL_ID"] = url_id
            return url_id, status_txt
        else:
            print(f"\r⏳ Generation in process..", end='', flush=True)
            #configs()
            os.environ["API_KEY"] = "❌ API key not found."
            time.sleep(1)
            try:
                url_id, status_txt = gent2v(credito, models, text_prompt, resolution, aspect_ratio, duration_ms)
            except Exception as e:
                print(f"\r❌12 Error getting status...", end='', flush=True)
                os.environ["URL_ID"] = "nop"
                return None, None
            if url_id:
              os.environ["URL_ID"] = url_id
            return url_id, status_txt
