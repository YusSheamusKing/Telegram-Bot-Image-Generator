import os
import base64
import requests
from PIL import Image, ImageEnhance
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('.env')

class Helper:
    def __init__(self):
        self.allowed_users = os.getenv('USER_ID').split(',')
        self.allowed_admins = os.getenv('ADMIN_ID').split(',')

    def is_user(self, user_id):
        """
        Check if a user is authorized (based on user ID).
        Returns True if the user ID is in the allowed list or if '*' is present (wildcard for all users >:)).
        """
        return '*' in self.allowed_users or str(user_id) in self.allowed_users

    def is_admin(self, user_id):
        """
       Check if a user has admin privileges (based on user ID).
       Returns True if the user ID is in the admin list or if '*' is present (wildcard for all admins  MUAHAHAHA).
       """
        return '*' in self.allowed_admins or str(user_id) in self.allowed_admins

class ImageGen: # You  are still reading all comments?
    """
    A class for handling image generation and processing, including watermarking and API interaction.
    """
    def add_watermark(self, input_image_path, output_image_path, watermark_image_path, transparency=25):
        if watermark_image_path is None or not os.path.exists(watermark_image_path): #adds watermark for image
            original_image = Image.open(input_image_path)
            original_image.save(output_image_path)
            return # Save the original image without changes if no watermark is provided

        try:
            original_image = Image.open(input_image_path)
            watermark = Image.open(watermark_image_path)

            # Resize the watermark to fit the original image (14% of the smallest dimension)
            min_dimension = min(original_image.width, original_image.height)
            watermark_size = (int(min_dimension * 0.14), int(min_dimension * 0.14))
            watermark = watermark.resize(watermark_size)

            # Ensure the watermark image has an RGBA mode (for transparency)
            if watermark.mode != 'RGBA':
                watermark = watermark.convert('RGBA')

            # Copy the original image to add the watermark
            image_with_watermark = original_image.copy()
            position = (0, original_image.size[1] - watermark.size[1]) #goes to bottom left
            image_with_watermark.paste(watermark, position, watermark)
            #Adjust transparency
            alpha = watermark.split()[3] # Get the alpha channel (transparency)
            alpha = ImageEnhance.Brightness(alpha).enhance(transparency / 100.0)
            watermark.putalpha(alpha)
            image_with_watermark.save(output_image_path)
        except Exception as e:
            # Log any errors and save the original image without changes
            print(f"Error adding watermark: {e}")
            original_image.save(output_image_path)

    def generate_image(self, prompt, style="None", size="square"):
        api_key = os.getenv('STABILITY_API_KEY')
        # Define the common parameters for the API request
        common_params = {
            "samples": 1,
            "steps": 50,
            "cfg_scale": 5.5,
            "text_prompts": [
                {
                    # Main prompt with a weight of 1
                    "text"  : prompt, 
                    "weight": 1
                },
                {  # Positive reinforcement text with a lower weight
                    "text"  :   "The artwork showcases excellent anatomy with a clear, complete, and appealing "
                                "depiction. It has well-proportioned and polished details, presenting a unique "
                                "and balanced composition. The high-resolution image is undamaged and well-formed, "
                                "conveying a healthy and natural appearance without mutations or blemishes. The "
                                "positive aspect of the artwork is highlighted by its skillful framing and realistic "
                                "features, including a well-drawn face and hands. The absence of signatures contributes "
                                "to its seamless and authentic quality, and the depiction of straight fingers adds to "
                                "its overall attractiveness.",
                    "weight": 0.3
                },
                # Negative reinforcement text to avoid undesired artifacts(yet I will still check images)
                {
                    "text"  :   "2 faces, 2 heads, bad anatomy, blurry, cloned face, cropped image, cut-off, deformed hands, "
                                "disconnected limbs, disgusting, disfigured, draft, duplicate artifact, extra fingers, extra limb, "
                                "floating limbs, gloss proportions, grain, gross proportions, long body, long neck, low-res, mangled, "
                                "malformed, malformed hands, missing arms, missing limb, morbid, mutation, mutated, mutated hands, "
                                "mutilated, mutilated hands, multiple heads, negative aspect, out of frame, poorly drawn, poorly drawn "
                                "face, poorly drawn hands, signatures, surreal, tiling, twisted fingers, ugly",
                    "weight": -1
                },
            ],
        }
        # Map size keywords to specific dimensions
        size_mapping = {
            "square-p": (1152, 896),
            "portrait": (1216, 832),
            "highscreen": (1344, 768),
            "panorama-p": (1536, 640),
            "square": (1024, 1024),
            "panorama": (640, 1536),
            "square-l": (896, 1152),
            "landscape": (832, 1216),
            "widescreen": (768, 1344),
        }
        # Assign dimensions based on the provided size
        if size in size_mapping:
            common_params["height"], common_params["width"] = size_mapping[size]
            # Add style preset if a style is specified
        if style != "None":
            common_params["style_preset"] = style
        body = common_params.copy()

        try:
            # Send a POST request to the Stability AI API
            response = requests.post(
                "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                json=body,
            )
            # Check for non-200 responses
            if response.status_code != 200:
                raise Exception("Non-200 response: " + str(response.text))
            # Parse the response and save the generated image
            data = response.json()
            output_directory = "./image"
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
            generated_image_path = f'{output_directory}/txt2img_{data["artifacts"][0]["seed"]}.png'
            with open(generated_image_path, "wb") as f:
                f.write(base64.b64decode(data["artifacts"][0]["base64"]))

            # Apply a watermark to the generated image the logo one in update 2.0.1 aka biggest update
            watermark_image_path = 'logo.png'
            output_with_watermark_path = generated_image_path
            self.add_watermark(generated_image_path, output_with_watermark_path, watermark_image_path, transparency=25)
            # Return the path to the final image
            return generated_image_path
        except Exception as e:
            # Log errors and return None in case of failure
            print(f"Error in generate_image: {e}")
            return None

helper_code = Helper()
image_gen = ImageGen()
