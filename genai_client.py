import os, io, base64
from PIL import Image
from google import genai
from google.genai import types

class GenAIClient:
    def __init__(self, api_key=None, base_url=None):
        # Reads GEMINI_API_KEY from env if not provided
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.base_url = base_url or os.getenv('GEMINI_BASE_URL')  # optional
        if not self.api_key:
            raise ValueError('GEMINI_API_KEY is not set. Set it as an environment variable or Streamlit secret.')
        # Initialize client
        # genai.Client can accept api_key param or read from env
        self.client = genai.Client(api_key=self.api_key)
    def _extract_images_from_parts(self, parts):
        images = []
        for part in parts:
            # Check if likely an image part
            if getattr(part, 'inline_data', None) is not None:
                # 1. Try SDK's as_image()
                try:
                    img = part.as_image()
                    images.append(img.convert('RGB'))
                    continue
                except Exception:
                    pass
                
                # 2. Try raw bytes (most likely strictly correct if SDK already decoded B64)
                try:
                    data = part.inline_data.data
                    img = Image.open(io.BytesIO(data)).convert('RGB')
                    images.append(img)
                    continue
                except Exception:
                    pass

                # 3. Fallback: Try base64 decode (if data is still b64 encoded bytes/string)
                try:
                    data_b64 = part.inline_data.data
                    img = Image.open(io.BytesIO(base64.b64decode(data_b64))).convert('RGB')
                    images.append(img)
                except Exception:
                    pass
        return images

    def generate_image(self, prompt, negative_prompt=None, model='gemini-3-pro-image-preview',
                       aspect_ratio='16:9', image_size='2K', guidance=7.5, seed=None, num_images=1, input_images=None):
        # Build contents: prompt + optional PIL images
        contents = [prompt]
        if input_images:
            # SDK accepts PIL images inline; append them
            for img in input_images:
                if isinstance(img, Image.Image):
                    contents.append(img)
                else:
                    # try to open path or bytes
                    contents.append(Image.open(img).convert('RGB'))
        # Build config
        image_config = types.ImageConfig(aspect_ratio=aspect_ratio, image_size=image_size)
        gen_config = types.GenerateContentConfig(response_modalities=['TEXT','IMAGE'], image_config=image_config)
        # call generate_content (model-level)
        response = self.client.models.generate_content(model=model, contents=contents, config=gen_config)
        # response.parts is iterable; extract images
        parts = getattr(response, 'parts', []) or []
        images = self._extract_images_from_parts(parts)
        return images
