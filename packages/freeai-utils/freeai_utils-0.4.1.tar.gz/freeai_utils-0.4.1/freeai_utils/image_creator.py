import torch
from diffusers import AutoPipelineForText2Image
import os
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
    def __init__(self, preferred_device : str = None ,support_model : str = None ,output_dir : str = "generated_image", model_path : str = None, scheduler : str = "default"):
        #model path is to check whether get from lib or get from running folder
        #support_model is for use or not
        #schedule is for sample
        pass
    
    def generate_images(self,
                        positive_prompt : str = None, 
                        negative_prompt : str = None,
                        filename : str = None, 
                        width : int = 512, 
                        height : int = 512, 
                        steps : int = 24, 
                        guidance_scale : float = 7.5, 
                        number_of_images : int = 2, 
                        seed : int = None) -> None:
        pass
    
    def _help_config(self) -> None:
        pass
    
if __name__ == "__main__":
    imagegenerator = SDXL_TurboImage(device="cpu")
    imagegenerator.generate_images(prompt= "Create an image of an blue hair anime girl", image_name="generated_image", output_dir="images")