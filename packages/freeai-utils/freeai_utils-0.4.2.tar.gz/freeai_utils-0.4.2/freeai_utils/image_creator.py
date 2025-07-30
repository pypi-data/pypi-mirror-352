import torch
from diffusers import AutoPipelineForText2Image #for sdxl_turbo
import os
from diffusers import StableDiffusionPipeline #for sd1.5
from transformers import CLIPTokenizer #for sd1.5
from freeai_utils.log_set_up import setup_logging
import logging

class SDXL_TurboImage:
    
    __slots__ = ("_model", "_device", "logger", "_initialized")
    
    _model: AutoPipelineForText2Image
    _device: str
    logger: logging.Logger
    _initialized: bool
    
    def __init__(self, model_name : str = "stabilityai/sdxl-turbo", device : str = None):
        #check type
        self.__enforce_type(model_name, str, "model_name")
        self.__enforce_type(device, str, "device")
        
        #init
        super().__setattr__("_initialized", False)
        
        self.logger = setup_logging(self.__class__.__name__)
        #init the var to hold device available
        preferred_devices = []
        self._model = None
        #try input first
        if device is not None:
            self.__enforce_type(device, str, "device")
            preferred_devices.append(device)
        
        # try cuda second 
        if torch.cuda.is_available() and "cuda" not in preferred_devices:
            preferred_devices.append("cuda")
        
        # fall back to CPU if not already there
        if "cpu" not in preferred_devices:
            preferred_devices.append("cpu")
        
        for dev in preferred_devices:
            dtype = torch.float32 if dev == "cpu" else torch.float16
            try:
                self.logger.info(f"Loading '{model_name}' on {dev}")
                self._model = AutoPipelineForText2Image.from_pretrained(model_name, torch_dtype=dtype,).to(dev)
                self._device = dev
                self.logger.info(f"Successfully loaded on {dev}")
                break
            except Exception as e:
                self.logger.error(f"Failed to load on {dev}: {e}")
                
        if self._model is None:
            raise RuntimeError(f"Cannot load '{model_name}' on any of: {preferred_devices}")
        
        #lock
        super().__setattr__("_initialized", True)
        
        self.logger.info("Fast image generator, sacrifice quality for speed")

    @property
    def device(self):
        return self._device
    
    @property
    def model(self):
        return self._model

    def generate_images(self, prompt : str = None, 
                    negative_prompt : str = """lowres, text, error, missing fingers, extra digit, missing libs, cropped, bad mouth, bad lips
                                                worst quality, lowres, (bad anatomy), (bad hands), text, missing finger, 
                                                extra digits, 2 eyes color, blurry, bad eyes, low quality, 3d, sepia, painting, 
                                                cartoons, sketch, signature, watermark, username""", 
                    steps : int = 2,
                    number_of_images : int = 2,
                    image_name : str = "generated_image",
                    output_dir : str = "") -> None:
        
        #check type
        self.__enforce_type(prompt, str, "prompt")
        self.__enforce_type(negative_prompt, str, "negative_prompt")
        self.__enforce_type(steps, int, "steps")
        self.__enforce_type(number_of_images, int, "number_of_images")
        self.__enforce_type(image_name, str, "image_name")
        self.__enforce_type(output_dir, str, "output_dir")
        
        output = self._model(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=steps,
            guidance_scale=0.0,
            num_images_per_prompt=number_of_images
        )
        images = output.images  # a list of PIL images
        os.makedirs(output_dir, exist_ok=True)
        
        for i, img in enumerate(images):
            img.save(f"{output_dir}\\{image_name}{i}.png") #will add time later to not be overload
        print(f"Saved {len(images)} images.")

    def __setattr__(self, name, value):
        # once initialized, block these core attributes
        if getattr(self, "_initialized", False) and name in ("_model", "_device"):
            raise AttributeError(f"Cannot reassign '{name}' after initialization")
        super().__setattr__(name, value)
        
    def __enforce_type(self, value, expected_type, arg_name):
        if not isinstance(value, expected_type):
            raise TypeError(f"Argument '{arg_name}' must be of type {expected_type.__name__}, but received {type(value).__name__}")

class SD15_Image:
    
    logger : logging.Logger
    output_dir: str
    _model : StableDiffusionPipeline
    _tokenizer : CLIPTokenizer
    
    def __init__(self, preferred_device : str = None ,support_model : str = "meinapastel.safetensors" ,output_dir : str = "generated_image", model_path : str = None, scheduler : str = "default"):
        #model path is to check whether get from lib or get from running folder
        #support_model is for use or not
        #schedule is for sample
        self.logger = setup_logging(self.__class__.__name__)
        self.logger.info("Init...")
        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = os.path.join(os.getcwd(), output_dir) #make valid output dir

        if model_path is None:
            model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloaded_models")
        
        if preferred_device == "cuda": #temp set to cuda, will modify later
                torch_dtype = torch.float16
        else: torch_dtype = torch.float32
        self.device = preferred_device 
        # --- Load tokenizer (we’ll still use the SD-v1.5 vocab) ---
        self._tokenizer = CLIPTokenizer.from_pretrained(
            "stable-diffusion-v1-5/stable-diffusion-v1-5",
            subfolder="tokenizer"
        )

        path = os.path.join(model_path, support_model) #init the path to correct model
        self._model = StableDiffusionPipeline.from_single_file( #init model
            path,
            tokenizer=self._tokenizer,
            torch_dtype=torch_dtype,
            safety_checker=None,
        ).to(preferred_device)
        
        self._model.enable_attention_slicing() #reduce size
        
        #schedule type
        if scheduler == "Karras":
            from diffusers import DPMSolverSinglestepScheduler
            # build the DPM++ SDE Karras scheduler
            sde_karras = DPMSolverSinglestepScheduler.from_config( #this requires number of step to be even
                self._model.scheduler.config,
                use_karras_sigmas=True,
                lower_order_final = True
            )
            self._model.scheduler = sde_karras
         
        else: #default euler
            from diffusers import EulerDiscreteScheduler
            self._model.scheduler = EulerDiscreteScheduler.from_config(self._model.scheduler.config)
            
        #embeded support
        embedding_paths = {
            "easynegative": os.path.join(model_path, "easynegative.safetensors"),
            "badprompt": os.path.join(model_path, "bad_prompt.pt"),
            "negativehand": os.path.join(model_path, "negative_hand.pt")
        }
        
        for token_name, epath in embedding_paths.items(): #load embeded path to model
            self._model.load_textual_inversion(epath, token=token_name)
            
        self.logger.info("Successfully")
    
    def generate_images(self,
                        positive_prompt : str = None, 
                        negative_prompt : str = "<easynegative:0.8>, <negativehand:2.1>, <badprompt:1.4>",
                        image_name : str = "generated_image", 
                        width : int = 512, 
                        height : int = 512, 
                        steps : int = 24, 
                        guidance_scale : float = 7.5, 
                        number_of_images : int = 2, 
                        seed : int = 123456789) -> None:
        
        generator = torch.Generator(self.device).manual_seed(seed)
        
        with torch.inference_mode():
            output = self._model(
                prompt= positive_prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                num_inference_steps= steps, 
                guidance_scale= guidance_scale,
                num_images_per_prompt= number_of_images,
                generator=generator,
            )
            
        for i, img in enumerate(output.images):
            img.save(f"{self.output_dir}\\{image_name}{i}.png") #will add time later to not be overload
            print(f"Saved {len(output.images)} images.")
    
    def _help_config(self) -> None:
        pass
    
if __name__ == "__main__":
    imagegenerator = SDXL_TurboImage(device="cuda")
    img2 = SD15_Image(preferred_device="cpu")
    img2.generate_images("A beautiful backgrounnd screen")
    # imagegenerator.generate_images(prompt= "Create an image of an blue hair anime girl", image_name="generated_image", output_dir="images")