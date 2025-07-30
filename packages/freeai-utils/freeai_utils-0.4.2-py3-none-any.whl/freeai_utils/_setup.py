import gc
import os
import requests
from tqdm import tqdm
import re

def install_model(target : str):
    
    target =target.strip().upper() if target is str else target
    if target is None or target == "A" or target == "":
        install_default_model()  # Installs all default models (excluding image generation)
    elif target == "S":
        print("Downloading default models for speech-to-text")
        download_transcription()
    elif target == "D":
        print("Downloading default models for document processing")
        download_document_related()
    elif target == "I":
        print("Downloading default models for OCR and image captioning")
        download_image_related()
    elif target == "T":
        print("Downloading default models for translation")
        download_translation()
    elif target == "L":
        print("Downloading default models for local LLMs")
        download_LLM()
    elif target == "ICF":
        print("Downloading all models for image creating")
        print("*" * 100)
        print("Recommend to use AUTOMATIC 1111 instead for better speed and UI")
        print("*" * 100)
        download_image_creation_related()
        download_from_civitai()
    else:
        print("No cmd found, please try again")
        
def install_default_model():
    decision = input(
        "This function will download all default models used by this library.\n"
        "The process can take a significant amount of time, so feel free to take a break.\n"
        "Would you like to proceed with the download? (Y/n): ").strip().lower()
        
    if decision != "y":
        print("Download cancelled.")
        return
        
    download_transcription()
    download_document_related()
    download_image_related()
    download_translation()

def download_transcription():
    from .audio_to_text_vn import VN_Whisper
    from .audio_to_text_whisper import OpenAIWhisper
     
    _download_and_purge(VN_Whisper)
    _download_and_purge(OpenAIWhisper)


def download_document_related():
    from .decider import DecisionMaker
    from .document_filter import DocumentFilter
     
    _download_and_purge(DecisionMaker)
    _download_and_purge(DocumentFilter, auto_init=False)


def download_image_related():
    from .image_to_text import ImageCaptioner
    from .text_from_image_easyocr import Text_Extractor_EasyOCR
    
    _download_and_purge(ImageCaptioner)
    _download_and_purge(Text_Extractor_EasyOCR)


def download_translation():
    from .language_detection import MBartTranslator, M2M100Translator
    
    _download_and_purge(MBartTranslator)
    _download_and_purge(M2M100Translator)

def _download_and_purge(cls, *args, **kwargs):
    inst = cls(*args, **kwargs)
    del inst
    gc.collect()

def download_LLM():
    from .localLLM import LocalLLM
    _download_and_purge(LocalLLM)

def download_image_creation_related():
    from .image_creator import SDXL_TurboImage, SD15_Image
    _download_and_purge(SDXL_TurboImage)
    _download_and_purge(SD15_Image)

def download_from_civitai():#download some popular models
    #https://civitai.com/models/23521/anime-pastel-dream
    _url_download_from_civitai(civitai_api_download_url="https://civitai.com/api/download/models/28100?type=Model&format=SafeTensor&size=full&fp=fp16",
                        model_name="anime_pastal_dream",
                        download_name="anime_pastal_dream"
                        )

    _url_download_from_civitai(civitai_api_download_url="https://civitai.com/api/download/models/108289?type=Model&format=SafeTensor&size=pruned&fp=fp16",
                        model_name="meinapastel",
                        download_name="meinapastel"
                        )

    #https://civitai.com/models/81458/absolutereality
    _url_download_from_civitai(civitai_api_download_url="https://civitai.com/api/download/models/132760?type=Model&format=SafeTensor&size=pruned&fp=fp16",
                        model_name="reality",
                        download_name="reality"
                        )

    #https://civitai.com/models/23900?modelVersionId=304817
    _url_download_from_civitai(civitai_api_download_url="https://civitai.com/api/download/models/304817?type=Model&format=SafeTensor&size=pruned&fp=fp16",
                        model_name="annylora_checkpoint",
                        download_name="annylora_checkpoint"
                        )
    
    #https://civitai.com/models/7808?modelVersionId=9208
    _url_download_from_civitai(civitai_api_download_url="https://civitai.com/api/download/models/9208?type=Model&format=SafeTensor&size=full&fp=fp16",
                        model_name="easynegative",
                        download_name="easynegative"
                        )
    
    #https://civitai.com/models/56519/negativehand-negative-embedding
    _url_download_from_civitai(civitai_api_download_url="https://civitai.com/api/download/models/60938?type=Negative&format=Other",
                        model_name="negative_hand",
                        download_name="negative_hand"
                        )
    
    #https://civitai.com/models/55700/badprompt-negative-embedding
    _url_download_from_civitai(civitai_api_download_url="https://civitai.com/api/download/models/60095?type=Negative&format=Other",
                        model_name="bad_prompt",
                        download_name="bad_prompt"
                        )
    
#only support .safetensors and .pt
def _url_download_from_civitai(civitai_api_download_url : str = "", model_name : str = None, download_name : str = None, download_dir : str = None): #only support for '.safetensors' and '.pt'
    #model_name -> this to help know what model is being downloaded
    #downloaded_name -> this will check the name when download to own computer
    #download_dir -> where it would be downloaded
    
    if download_dir is None:
        download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloaded_models") #temp
    os.makedirs(download_dir, exist_ok=True)
    
    if download_name is None:
        raise TypeError("download_name can not be None")
    
    if model_name is None:
        model_name = download_name #use the downloaded name as the model name
    
    direct_download_url = None
    final_filename = None
    
    try:
        print(f"Fetching direct download URL for model: {model_name}...")
        response = requests.head(civitai_api_download_url, allow_redirects=False)
        response.raise_for_status()

        if response.status_code in [301, 302, 303, 307, 308]: # Check for redirect status codes
            direct_download_url = response.headers['Location']
            print(f"Found direct download URL: {direct_download_url}")

            if "Content-Disposition" in response.headers:
                cd = response.headers['Content-Disposition']
                filename_match = re.search(r'filename\*?=(?:UTF-8\'\')?([^;]+)', cd, re.IGNORECASE)
                if filename_match:
                    final_filename = filename_match.group(1).strip('\"\'')
            
            if not final_filename:
                final_filename = os.path.basename(direct_download_url.split('?')[0])
                if not final_filename.endswith(('.safetensors', '.pt')):
                    raise RuntimeError("File not end with .safetensors or .pt") #fall back if file is not in these type
                    
        else:
            print(f"Unexpected status code {response.status_code}. Not a redirect. Assuming direct download.")
            direct_download_url = civitai_api_download_url # Use the original URL if no redirect
            if "Content-Disposition" in response.headers:
                cd = response.headers['Content-Disposition']
                filename_match = re.search(r'filename\*?=(?:UTF-8\'\')?([^;]+)', cd, re.IGNORECASE)
                if filename_match:
                    final_filename = filename_match.group(1).strip('\"\'')
            if not final_filename:
                final_filename = f"{model_name}.safetensors"
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching direct download URL: {e}")
        return
        
    if not direct_download_url:
        print("Could not determine the direct download URL. Exiting.")
        return
        
    #filename for the downloaded
    filepath = os.path.join(download_dir, f"{download_name}.{final_filename.split(".")[-1]}")
    
    headers = {}
    download_start_byte = 0
    total_size_in_bytes = 0
    resume_possible = False
    
    if os.path.exists(filepath):
        download_start_byte = os.path.getsize(filepath)
        # Check existing file size matches
        try:
            head_response_for_size = requests.head(direct_download_url, allow_redirects=True)
            head_response_for_size.raise_for_status()
            expected_full_size = int(head_response_for_size.headers.get('content-length', 0))
            if expected_full_size > 0 and download_start_byte == expected_full_size:
                print(f"File {final_filename} already fully downloaded. Size: {download_start_byte} bytes.")
                while True:
                    user_choice = input(f"'{final_filename}' already exists and is complete.\nDo you want to redownload it [R], or exit? [E]  Choice(R/E): ").strip().lower()
                    if user_choice == 'r':
                        print("Initiating full re-download.")
                        os.remove(filepath) # Delete the existing file
                        download_start_byte = 0 # Reset to start new download
                        break
                    elif user_choice == 'e':
                        print("Exiting as requested.")
                        return
                    else:
                        print("Invalid choice. Please enter 'R' or 'E'.")

            if expected_full_size > download_start_byte:
                while True:
                    user_choice = input(f"Partial file '{final_filename}' found ({download_start_byte} bytes).\nDo you want to resume [R], or start [S] a new download from scratch? (R/S): ").strip().lower()
                    if user_choice == 'r':
                        headers["Range"] = f"bytes={download_start_byte}-"
                        resume_possible = True
                        print(f"Resuming download from byte {download_start_byte} for {final_filename}")
                        break
                    elif user_choice == 's':
                        print("Starting a new download from scratch.")
                        os.remove(filepath) # Delete the existing partial file
                        download_start_byte = 0 # Reset to start new download
                        break
                    else:
                        print("Invalid choice. Please enter 'R' or 'S'.")
            elif download_start_byte > 0 and expected_full_size <= download_start_byte:
                print(f"Partial file {final_filename} exists, but it's larger or equal to expected size {expected_full_size}. Possibly corrupted or full.")
                print("Starting a new download. If this is incorrect, delete the partial file manually.")
                download_start_byte = 0 # force new download
                
        except requests.exceptions.RequestException as e:
            while True:
                user_choice = input(f"Could not verify full file size from server. Partial file '{final_filename}' found ({download_start_byte} bytes).\nDo you want to resume [R], or start [S] a new download from scratch? (R/S): ").strip().lower()
                if user_choice == 'r':
                    headers["Range"] = f"bytes={download_start_byte}-"
                    resume_possible = True
                    print(f"Attempting resume from byte {download_start_byte} for {final_filename} without full size check.")
                    break
                elif user_choice == 's':
                    print("Starting a new download from scratch.")
                    if os.path.exists(filepath):
                        os.remove(filepath) # Delete the existing partial file
                    download_start_byte = 0 # Reset to start new download
                    break
                else:
                    print("Invalid choice. Please enter 'R' or 'S'.")
    else:
        print(f"Starting new download for {final_filename}.")
    
    try:
        with requests.get(direct_download_url, headers=headers, stream=True, allow_redirects=True) as r:
            r.raise_for_status() # HTTPError for bad responses 
            
            # Confirm the actual total size from the response
            if r.status_code == 206 and 'Content-Range' in r.headers:
                try:
                    range_header = r.headers['Content-Range']
                    total_size_in_bytes = int(range_header.split('/')[1])
                    print(f"Server responded with 206 Partial Content. Total file size: {total_size_in_bytes} bytes.")
                except (IndexError, ValueError):
                    total_size_in_bytes = int(r.headers.get('content-length', 0)) 
                    print("Warning: Could not parse Content-Range header. Progress bar might be inaccurate.")
            elif r.status_code == 200:
                if resume_possible:
                    print("Server did not return 206 Partial Content for resume. Starting new download from scratch.")
                    download_start_byte = 0 # Reset if server didn't resume
                total_size_in_bytes = int(r.headers.get('content-length', 0))
                print(f"Server responded with 200 OK. Total file size: {total_size_in_bytes} bytes.")
            
            if total_size_in_bytes == 0:
                print("Warning: Could not determine total file size. Progress bar will not be accurate.")
            block_size = 1024 # 1 Kibibyte (1KB)
            
            # Open file in append-binary mode ('ab') for resuming, or write-binary ('wb') for new
            mode = 'ab' if download_start_byte > 0 and r.status_code == 206 else 'wb'
            
            print(f"Downloading to: {filepath}")
            with tqdm(
                initial=download_start_byte,
                total=total_size_in_bytes,
                unit='iB',
                unit_scale=True,
                desc=final_filename
            ) as progress_bar:
                with open(filepath, mode) as f:
                    for chunk in r.iter_content(chunk_size=block_size):
                        progress_bar.update(len(chunk))
                        f.write(chunk)
        
        print(f"Successfully downloaded {final_filename} to {download_dir}")
    
    except requests.exceptions.RequestException as e:
        status_code = getattr(e.response, 'status_code', None)
        if status_code == 416:
            print("File already full, exiting...")
            return
        
        # Fallback for any other network/HTTP errors
        print(f"An HTTP or network error occurred during download: {e}")
        print("Please check your internet connection and the direct download URL.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    download_from_civitai()