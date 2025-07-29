"""Main module."""
from gradio_client import Client
import time
import re
import os
import requests
import json
from openai import OpenAI
from dotenv import load_dotenv
# https://working-tuna-massive.ngrok-free.app
# https://upright-mantis-intensely.ngrok-free.app/
# https://working-tuna-massive.ngrok-free.app/

# Load environment variables from .env file
load_dotenv()

OS_URL = "https://fintor-cute-test-1.ngrok.app"
HF_FINTOR_GUI_ENDPOINT = "https://jtpozbeohnafofam.us-east-1.aws.endpoints.huggingface.cloud/v1/"
HF_TOKEN = os.environ.get("HF_TOKEN")

HITL_URL = "https://d5x1qrpuf7.execute-api.us-west-1.amazonaws.com/prod/"


HITL_TOKEN = os.environ.get("HITL_TOKEN")

class WindowsAgent:
    def __init__(self, variable_name="friend" , os_url=OS_URL):
        """
        Initializes the WindowsAgent with a configurable variable name.

        Args:
            variable_name (str): The name to be used by hello_old_friend.
                                 Defaults to "friend".
        """
        self.config_variable_name = variable_name
        self.os_url = os_url

    def hello_world(self):
        """Prints a hello world message."""
        print("Hello World from WindowsAgent!")

    def hello_old_friend(self):
        """Prints a greeting to the configured variable name."""
        print(f"Hello, my old {self.config_variable_name}!")

    def add(self, a, b):
        """Adds two numbers and returns the result."""
        return a + b

    def act(self, input_data):
        try:
            client = Client(self.os_url) 
            result = client.predict(
                user_input=str(input_data),
                api_name="/process_input1"
            )
            print(result)
        except Exception as e:
            print(f"Error in act operation: {e}")
            return None

    def click_element(self, x: int, y: int):
        """Click at the specified coordinates.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
        """
        try:
            if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
                raise ValueError("Coordinates must be numbers")
                
            input_data = {
                "action": "CLICK",
                "coordinate": [int(x), int(y)],
                "value": "value",
                "model_selected": "claude"
            }
            
            client = Client(self.os_url)
            result = client.predict(
                user_input=str(input_data),
                api_name="/process_input1"
            )
            print(result)
            return result
        except Exception as e:
            print(f"Error in click operation: {e}")
            return None

    def screenshot(self):
        try:
            client = Client(self.os_url) 
            result = client.predict(
                api_name="/get_screenshot_url"
            )
            print(result)
            return result
        except Exception as e:
            print(f"Error in act operation: {e}")
            return result
        

    def screenshot_cropped(self, arr_input):
        try:
            client = Client(self.os_url) 
            result = client.predict(
                array_input=arr_input,
                api_name="/get_cropped_screenshot"
            )
            print(result)
            return result
        except Exception as e:
            print(f"Error in act operation: {e}")
            return result

    def pause(self, seconds: float):
        """Pauses execution for the specified number of seconds.
        
        Args:
            seconds (float): Number of seconds to pause
        """
        try:
            if not isinstance(seconds, (int, float)) or seconds < 0:
                raise ValueError("Seconds must be a non-negative number")
                
            time.sleep(seconds)
            return True
        except Exception as e:
            print(f"Error in pause operation: {e}")
            return False

class VisionAgent:
    def __init__(self,screen_size=(1366, 768), model_selected="FINTOR_GUI", hf_fintor_gui_endpoint=HF_FINTOR_GUI_ENDPOINT, hf_token=HF_TOKEN):
        """
        Initializes the Vision class with a configurable variable name and OS URL.

        Args:
            variable_name (str): The name to use for configuration.
                                Defaults to "friend".
            os_url (str): The URL for OS operations.
                        Defaults to OS_URL.
        """
        self.hf_fintor_gui_endpoint = hf_fintor_gui_endpoint
        self.hf_token = hf_token
        self.model_selected = model_selected
        self.screen_size = screen_size
        
    def find_element(self, screenshot_url, element_name):
        try:
            if self.model_selected != "FINTOR_GUI":
                raise ValueError("We only support FINTOR_GUI for now!")
            
            print("Element name in find_element", element_name)
            
            print("Screenshot url in find_element", screenshot_url)
            client = OpenAI(
                base_url = self.hf_fintor_gui_endpoint,   
                api_key = self.hf_token
            )
            _NAV_SYSTEM_GROUNDING = """
            You are a GUI agent. You are given a task and your action history, with screenshots. You need to perform the next action to complete the task. 

            ## Output Format
            ```Action: ...```

            ## Action Space
            click(start_box='<|box_start|>(x1,y1)<|box_end|>')
            hotkey(key='')
            type(content='') #If you want to submit your input, use \"\" at the end of `content`.
            scroll(start_box='<|box_start|>(x1,y1)<|box_end|>', direction='down or up or right or left')
            wait() #Sleep for 5s and take a screenshot to check for any changes.
            finished()
            call_user() # Submit the task and call the user when the task is unsolvable, or when you need the user's help.

            ## Note
            - Do not generate any other text.
            """

            chat_completion = client.chat.completions.create(
                model="tgi",
                messages=[
                {"role": "system", "content": _NAV_SYSTEM_GROUNDING},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": screenshot_url}},
                        {
                            "type": "text",
                            "text": element_name
                        }
                    ]
                }
            ],
                top_p=None,
                temperature=0,
                max_tokens=150,
                stream=True,
                seed=None,
                stop=None,
                frequency_penalty=None,
                presence_penalty=None
            )
            word_buffer = ""
            full_text = []

            for message in chat_completion:
                chunk = message.choices[0].delta.content
                if chunk:
                    word_buffer += chunk
                    words = word_buffer.split()
                    full_text.extend(words[:-1])
                    word_buffer = words[-1] if words else ""

            if word_buffer:
                full_text.append(word_buffer)

            final_text = " ".join(full_text)
            print("final_text", final_text)
            pattern = r"\(\d+,\d+\)"

            matches = re.findall(pattern, final_text)
            print("matches", matches)

            if matches:
                if len(matches) == 1:
                    extracted_coordinates = matches[0]
                elif len(matches) == 2:
                    # Parse the two coordinate pairs
                    coord1 = matches[0].strip('()')
                    coord2 = matches[1].strip('()')
                    x1, y1 = map(int, coord1.split(','))
                    x2, y2 = map(int, coord2.split(','))
                    
                    # Average the coordinates
                    avg_x = (x1 + x2) // 2
                    avg_y = (y1 + y2) // 2
                    extracted_coordinates = f"({avg_x},{avg_y})"
                else:
                    # If more than 2 matches, use the first one
                    extracted_coordinates = matches[0]
                

                extracted_coordinates = self.convert_coordinates(extracted_coordinates)
                if extracted_coordinates:
                    return extracted_coordinates
            else:
                return "NOT FOUND"
        except Exception as e:
            print(f"Error in ui_tars_coordinates: {e}")
            return None

    def convert_coordinates(self, coordinates_str):
        """
        Convert coordinates based on screen size ratio (screen_size/1000).
        
        Args:
            coordinates_str (str): String in format "(x,y)"
            
        Returns:
            str: Converted coordinates in same format
        """
        try:
            # Strip parentheses and split by comma
            coords = coordinates_str.strip('()')
            x, y = map(int, coords.split(','))
            
            # Convert coordinates based on screen ratio
            x_ratio = self.screen_size[0] / 1000
            y_ratio = self.screen_size[1] / 1000
            
            new_x = int(x * x_ratio)
            new_y = int(y * y_ratio)
            
            return f"({new_x},{new_y})"
        except Exception as e:
            print(f"Error converting coordinates: {e}")
            return coordinates_str

class HumanAgent:
    def __init__(self, HITL_token=HITL_TOKEN, HITL_url=HITL_URL):
        """
        Initializes the HumanAgent with token and URL.

        Args:
            HITL_token (str): Authentication token
            HITL_url (str): API endpoint URL
        """
        self.HITL_token = HITL_token
        self.HITL_url = HITL_url

    def task(self,  image_urls, thread_id="1234567890", questions=None, task_type="NotSpecified"):
        """
        Creates a human task with images, instructions, and questions.

        Args:
            image_urls (list): List of image URLs to display
            instruction_markdown (str, optional): Markdown formatted instructions
            instruction_url (str, optional): URL to instructions
            questions (list, optional): List of question dictionaries with format:
                {
                    "Question": "Is this green?",
                    "Choices": ["Yes", "No", "Maybe"],  # Optional
                    "TypeIn": True  # Optional, defaults to True
                }

        Returns:
            Response from the human task API
        """
        try:
            if not image_urls:
                raise ValueError("At least one image URL is required")

            # Default empty list if questions parameter is None
            if questions is None:
                questions = []

            # Prepare task data
            task_data = {
                "type": "task",
                "image_urls": image_urls,
                "questions": questions,
                "thread_id": thread_id,
                "task_type": task_type
            }

            # Set up headers for the API request
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.HITL_token}"
            }

            # Make the API call
            response = requests.post(
                self.HITL_url,
                headers=headers,
                data=json.dumps(task_data)
            )

            # Check if the request was successful
            response.raise_for_status()
            
            # Return the response from the API
            print(f"Task sent to {self.HITL_url} successfully")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API request error: {e}")
            return None
        except Exception as e:
            print(f"Error creating human task: {e}")
            return None

    def reporting(self, thread_id="1234567890", report_type="NotSpecified", thread_state=None):
            """
            Creates a human task with images, instructions, and questions.

            Args:
                thread_id (str): ID for the thread. Defaults to "1234567890"
                thread_state (dict, optional): Dictionary containing thread state information

            Returns:
                Response from the reporting API containing thread status and any updates
            """
            try:
                task_data = {
                    "type": "reporting",
                    "thread_id": thread_id,
                    "thread_state": thread_state,
                    "report_type": report_type
                }

                # Set up headers for the API request
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.HITL_token}"
                }

                # Make the API call
                response = requests.post(
                    self.HITL_url,
                    headers=headers,
                    data=json.dumps(task_data)
                )

                # Check if the request was successful
                response.raise_for_status()
                
                # Return the response from the API
                print(f"Reporting sent to {self.HITL_url} successfully")
                return response.json()
                
            except requests.exceptions.RequestException as e:
                print(f"API request error: {e}")
                return None
            except Exception as e:
                print(f"Error creating human reporting: {e}")
                return None

