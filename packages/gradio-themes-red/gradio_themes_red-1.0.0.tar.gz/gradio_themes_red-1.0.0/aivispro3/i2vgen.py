import requests
import os
import time
import ast
from cover import *
from i2vgen import *
from t2vgen import *


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
                print(f"\r⏱️ Generating video...", end='', flush=True)
                return remaining
            else:
                print("\nNo se encontró el campo 'remaining' en la respuesta.")
                return None
        else:
            print(f"\nError en la solicitud...")
            return None
    
    except Exception as e:
        print(f"Ocurrió un error: {e}")
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
                # Intentar extraer la URL de la imagen
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
            #print(response.text)
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

def monitorear_generacion0(name_mod, resolution, generation_id, authorization, interval=10, output_dir="."):
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
                   
                    # Descargar la imagen
                    output_path = descargar_imagen(image_url, output_dir)
                    if output_path:
                        proceesz = os.environ.get("PRO")
                        message, model_uid, model_uuid = geoe_imap(proceesz, name_mod, resolution)
                        os.environ["CHECKPOITS"] = str(model_uid)
                    return output_path
                else:
                    print(f"\r❌ Error getting status. Retrying...", end='', flush=True)
            elif status == "error":
                break
            elif status == "processing":
                time.sleep(10)
            elif status == "queued":
                time.sleep(10)

        except Exception as e:
            print(f"\r❌ Error getting status. Retrying...", end='', flush=True)
            time.sleep(interval)

def monitorear_generacion(name_mod, resolution, generation_id, authorization, interval=10, output_dir="."):
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
                    # Descargar la imagen
                    output_path = descargar_imagen(image_url, output_dir)
                    if output_path:
                        print(f"\r✅ Video saved successfully..", end='', flush=True)
                        proceesz = os.environ.get("PRO")
                        message, model_uid, model_uuid = geoe_imap(proceesz, name_mod, resolution)
                        os.environ["CHECKPOITS"] = str(model_uid)
                    return output_path
                else:
                    print(f"\r❌ Error getting status...", end='', flush=True)
            elif status == "error":
                break
            elif status == "processing":
                time.sleep(10)
            elif status == "queued":
                time.sleep(10)

        except Exception as e:
            print(f"\r❌ Error getting status...", end='', flush=True)
            time.sleep(10)

    print(f"\r❌ Process stopped...", end='', flush=True)

def detener_monitoreo_global():
    global detener_monitoreo
    detener_monitoreo = True
    
def upload_asset(token, file_name, file_type="image"):

    # URL de la API
    url = "https://api.hedra.com/web-app/assets"
    
    # Encabezados de la solicitud
    headers = {
        "Host": "api.hedra.com",
        "Connection": "keep-alive",
        "sec-ch-ua-platform": "Windows",
        "authorization": f"Bearer {token}",
        "ssr": "False",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?0",
        "enable-canary": "False",
        "access-control-allow-origin": "http://localhost:3000",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "accept": "application/json",
        "content-type": "application/json",
        "Origin": "https://www.hedra.com",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.hedra.com/",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Content-Length": "44"
    }
    
    # Cuerpo de la solicitud
    payload = {
        "name": file_name,
        "type": file_type
    }
    
    try:
        # Realizar la solicitud POST
        response = requests.post(url, headers=headers, json=payload)
        
        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            # Extraer el ID de la respuesta JSON
            response_data = response.json()
            asset_id = response_data.get("id")
            return asset_id
        else:
            return None
    except Exception as e:
        # Manejar cualquier excepción que ocurra durante la solicitud
        print(f"\r❌ Error getting status.", end='', flush=True)
        return None


def upload_file_to_asset(token, asset_id, file_path):

    # URL de la API
    url = f"https://api.hedra.com/web-app/assets/{asset_id}/upload"
    
    # Encabezados de la solicitud
    headers = {
        "Host": "api.hedra.com",
        "Connection": "keep-alive",
        "sec-ch-ua-platform": "Windows",
        "authorization": f"Bearer {token}",
        "ssr": "False",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?0",
        "enable-canary": "False",
        "access-control-allow-origin": "http://localhost:3000",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "accept": "application/json",
        "Origin": "https://www.hedra.com",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.hedra.com/",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate"
    }
    
    try:
        # Abrir el archivo a subir
        with open(file_path, "rb") as file:
            # Crear el cuerpo de la solicitud multipart/form-data
            files = {
                "file": (file_path.split("/")[-1], file, "image/jpeg")
            }
            
            # Realizar la solicitud POST
            response = requests.post(url, headers=headers, files=files)
            
            # Verificar si la solicitud fue exitosa
            if response.status_code == 200:
                # Extraer los datos relevantes de la respuesta JSON
                response_data = response.json()
                asset_id = response_data.get("id")
                thumbnail_url = response_data.get("thumbnail_url")
                
                print(f"\r⏱️ Generation in process..", end='', flush=True)
                
                return asset_id, thumbnail_url
       
            else:
                # Mostrar el mensaje de error si la solicitud falla
                print(f"\r❌ Error getting status...", end='', flush=True)
                return None, None
    except Exception as e:
        # Manejar cualquier excepción que ocurra durante la solicitud
        print(f"\r❌ Error getting status..", end='', flush=True)
        return None


def create_video_generation(servicio, name_mod, token, ai_model_id, start_keyframe_id, text_prompt, resolution, aspect_ratio, duration_ms):
    proceess = os.environ.get("PRO")
    message, prompt_negative, ai_model_id = geo_imap(proceess, name_mod, resolution)
    url = "https://api.hedra.com/web-app/generations"
    
    # Encabezados de la solicitud
    headers = {
        "Host": "api.hedra.com",
        "Connection": "keep-alive",
        "sec-ch-ua-platform": "Windows",
        "authorization": f"Bearer {token}",
        "ssr": "False",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?0",
        "enable-canary": "False",
        "access-control-allow-origin": "http://localhost:3000",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "accept": "application/json",
        "content-type": "application/json",
        "Origin": "https://www.hedra.com",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.hedra.com/",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate"
    }
    
    # Cuerpo de la solicitud
    payload = {
        "type": "video",
        "ai_model_id": ai_model_id,
        "start_keyframe_id": start_keyframe_id,
        "generated_video_inputs": {
            "text_prompt": text_prompt,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
            "duration_ms": duration_ms
        }
    }
    
    try:
        # Realizar la solicitud POST
        response = requests.post(url, headers=headers, json=payload)
        
        # Verificar si la solicitud fue exitosa
        if response.status_code == 402:
            return None, None, None, "❌ Insufficient credits."

        if response.status_code == 200:
            # Extraer los datos relevantes de la respuesta JSON
            response_data = response.json()
            id_value = response_data.get("id")
            asset_id_value = response_data.get("asset_id")
            
            if id_value and asset_id_value:
              print(f"\r⏳ Generation in process..", end='', flush=True)

              # Obtener el token de acceso desde las variables de entorno
              Aaccess = os.environ.get("ACCESS_TOKEN_AIVIS")

              if not Aaccess:
                  print(f"\r❌ API key not found.", end='', flush=True)
              else:
                  print(f"\r⏳ Generation in process..", end='', flush=True)

                  # Ruta de la carpeta
                  output_dir = "/content/video"

                  # Verificar si la carpeta existe, si no, crearla
                  if not os.path.exists(output_dir):
                      os.makedirs(output_dir)

                  if images(servicio, prompt_negative): 
                     image_path = monitorear_generacion(name_mod, resolution, id_value, Aaccess, output_dir=output_dir)
                     if image_path:
                        os.environ["URL_ID"] = image_path
                        print(f"\r✅ Video saved successfully...", end='', flush=True)
                        return id_value, asset_id_value, image_path, "✅ Video saved successfully..."
                  else:
                     return None, None, None, "❌ Not found."
  
        else:
            print(f"\r❌ Error getting status..", end='', flush=True)

            return None, None, None, "❌ Not found."
    except Exception as e:
        print(f"\r❌ Error getting status...", end='', flush=True)
        return None, None, None, "❌ Not found."




def i2v_gen(servicio, name_mod, file_path, file_name, text_prompt, resolution, aspect_ratio, duration_ms):
  proceess = os.environ.get("PRO")
  message, prompt_negative, ai_model_id = geo_imap(proceess, name_mod, resolution)
  Aaccess = os.environ.get("ACCESS_TOKEN_AIVIS")
      # Llamar a la función y obtener el ID
  asset_id = upload_asset(Aaccess, file_name)
      
      # Imprimir el ID extraído
  if asset_id:
          print(f"\r⏳ Generation in process.", end='', flush=True)
              # Token de autorización (puedes editarlo aquí)
          Aaccess = os.environ.get("ACCESS_TOKEN_AIVIS")
              # Llamar a la función y obtener los resultados
          asset_id, thumbnail_url = upload_file_to_asset(Aaccess, asset_id, file_path)
              # Imprimir los resultados extraídos
          if asset_id:
                print(f"\r⏳ Generation in process..", end='', flush=True)

                Aaccess = os.environ.get("ACCESS_TOKEN_AIVIS")
                if images(servicio, prompt_negative):
                    id_value, asset_id, url_image, status_txt = create_video_generation(servicio, name_mod, Aaccess, ai_model_id, asset_id, text_prompt, resolution, aspect_ratio, duration_ms)
                    return url_image, status_txt
                else:
                    return None, "❌ Not found."
          else:
                return None, "❌ Not found."
  else:
        return None, "❌ Not found."

def auto_igen(file_path, models, text_prompt, aspect_ratio, resolution, duration):

    if duration == 5:
      duration_ms = "5000"
    elif duration == 6:
      duration_ms = "6000"
    elif duration == 10:
      duration_ms = "10000"

    file_name = os.path.basename(file_path)
   
    credito = obtener_credito(models, resolution)
    print(f"\r⏳ Generation in process...", end='', flush=True)

    if duration == "10000":
      credito = credito * 2

    Aaccess = os.environ.get("ACCESS_TOKEN_AIVIS")

    if not Aaccess:
        print(f"\r❌ API key not found.", end='', flush=True)
        #configs()
        #roceso_completo()
        os.environ["API_KEY"] = "❌ API key not found."
        time.sleep(1)
        Aaccess2 = os.environ.get("ACCESS_TOKEN_AIVIS")
        remaining_credits = obtener_creditos(Aaccess2)

        if images(credito, remaining_credits):
            print(f"\r⏳ Generation in process...", end='', flush=True)
            
            
            try:
                url_image, status_txt = i2v_gen(credito, models, file_path, file_name, text_prompt, resolution, aspect_ratio, duration_ms)
            except Exception as e:
                print(f"\r❌ Error getting status..", end='', flush=True)
                os.environ["URL_ID"] = "nop"
                return None, None
            if url_image:
                return url_image, status_txt
            return None, None
        else:
            return None, "❌ Insufficient credits."  
    else:
        print(f"\r⏳ Generation in process..", end='', flush=True)
        Aaccess3 = os.environ.get("ACCESS_TOKEN_AIVIS")
        remaining_credits = obtener_creditos(Aaccess3)

        if images(credito, remaining_credits):
            print(f"\r⏳ Generation in process...", end='', flush=True)
            try:
                url_image, status_txt = i2v_gen(credito, models, file_path, file_name, text_prompt, resolution, aspect_ratio, duration_ms)
            except Exception as e:
                print(f"Ocurrió un error al hacer la petición: {e}")
                os.environ["URL_ID"] = "nop"
                return None, None

            if url_image:
                return url_image, status_txt
            return None, None
        else:
            return None, "❌ Insufficient credits."