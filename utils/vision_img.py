import base64
import requests
import pandas as pd

class API_calling:
    def __init__(self):
        self.payload = None
        self.prompt = "From a set of images, please extract the title, authors, date of invention, and city of invention from the image with detailed description on the patent and only tell me the information in such format: Title: [title]\n Authors: [authors]\n Invention_Date: [date]\n City: [city]\n Once you identified the first page of the patent document (not image) give me information above, stopping immediately."
        self.prompt_test = "From a set of images, please extract the title, authors, date of invention, and city of invention from the image with detailed description on the patent and only tell me the information in such format: Title: [title]\n Authors: [authors]\n Invention_Date: [date]\n City: [city]\n. Once you identified the first page of the patent document (not image) give me information above, stopping immediately and tell me the page index that you stopped at."

    def encode_image(self, image_path):
        '''
        encodes the image in base64
        
        Args:
            image_path (str): The path to the image to be processed
            
        Returns:
            str: The base64 encoded image   
        '''
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def get_info(self, image_path_list, headers):
        '''
        queries the API for the title & author information in the image
        
        Args:
            image_path_list (str list): The path to the image to be processed
        
        Returns:
            json: The response from the API
        '''
        try:
            self.payload = self.create_payload(image_path_list)
            
            print("api calling...")
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=self.payload)
            return response.json()
        except Exception as e:
            print(f"An error occurred: {e}")
    
    def create_payload(self, image_paths):
        '''
        defines the payload information

        Args:
            image_paths (list): A list of paths to the images to be processed

        Returns:
            dict: payload information
        '''
        base64_images = [self.encode_image(image_path) for image_path in image_paths]

        content = [
            {
                "type": "text",
                "text": self.prompt,
            }
        ]

        for base64_image in base64_images:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ],
            "max_tokens": 300
        }

        return payload
    
    def create_payload_test(self, image_paths):
        '''
        defines the payload information

        Args:
            image_paths (list): A list of paths to the images to be processed

        Returns:
            dict: payload information
        '''
        base64_images = [self.encode_image(image_path) for image_path in image_paths]

        content = [
            {
                "type": "text",
                "text": self.prompt_test,
            }
        ]

        for base64_image in base64_images:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ],
            "max_tokens": 300
        }

        return payload

if __name__ == "__main__":
    test = API_calling()
    api_key = open("/Users/pattoyin/code/gptapi/apikey.txt", "r").read().strip('\n')
    image_path_list = ["images/13.tif", "images/14.tif", "images/15.tif"]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    response = test.get_info(image_path_list, headers)
    print(response)
    print(response['choices'][0]['message']['content'])