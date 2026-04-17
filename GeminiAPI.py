import math

import google.generativeai as genai
from dotenv import load_dotenv
import os
import re


load_dotenv()

def setup_gemini():

    current_working_directory = os.getcwd()
    path_to_api = current_working_directory+"/GoogleAPI/Google_api.txt"


    if os.path.exists(path_to_api) == False:
        raise ValueError("Please put your API key in a .txt file named Google_api.txt on the directory : "+current_working_directory+"/Google_api.txt")
    f = open(path_to_api, "r")
    api_key = f.read()

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel('gemini-pro')
    return model


def get_gemini_response(model, prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"


def read_prompt_file(filename='localization_tests/current_prompt.txt'):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt file '{filename}' not found")
    except Exception as e:
        raise Exception(f"Error reading prompt file: {str(e)}")


def save_response(response, filename='current_answer.txt'):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(response)
        print(f"Response saved to {filename}")
    except Exception as e:
        print(f"Error saving response: {str(e)}")


def get_state_vector(filename="localization_tests/current_answer.txt"):
    with open(filename, 'r') as f:
        content = f.read()

    parts = content.split("FINAL ANSWER")
    if len(parts) < 2:
        raise ValueError("No FINAL ANSWER found in file")
    content = parts[1]

    pattern = r'x=([-\d.]+)m,\s*y=([-\d.]+)m,\s*[θθ]=([-\d.]+)°'
    match = re.search(pattern, content)
    if not match:
        raise ValueError("Could not parse state vector from file")

    x, y, theta = map(float, match.groups())
    return (x, y, theta)

def call_gemini(prompt_file='localization_tests/current_prompt.txt', response_file='localization_tests/current_answer.txt'):

    try:
        model = setup_gemini()

        prompt = read_prompt_file(prompt_file)
        print(f"Read prompt: {prompt}")

        response = get_gemini_response(model, prompt)

        save_response(response, response_file)

        return response

    except Exception as e:
        error_message = f"Error in call_gemini: {str(e)}"
        print(error_message)
        return error_message

def generate_prompt(sensor_data):
    robot = sensor_data['robot']
    prompt = f"""You are a localization system estimating robot pose (x, y, θ).  
    Robot movement capabilities:
- w: Forward step of 0.2m in heading direction
- a: Rotate +45° (counter-clockwise)
- d: Rotate -45° (clockwise)

Environment constraints:
- Robot must stay between wall radius ({sensor_data['wall']['radius']}m) and beacon radius ({sensor_data['beacon_radius']}m)
- Central wall: radius {sensor_data['wall']['radius']}m at (0,0)
- 8 static beacons in circle with known absolute positions: radius {sensor_data['beacon_radius']}m
- Beacon positions: 0:(5,0), 1:(3.54,3.54), 2:(0,5), 3:(-3.54,3.54), 4:(-5,0), 5:(-3.54,-3.54), 6:(0,-5), 7:(3.54,-3.54)
- Wall blocks beacon visibility


Action history:"""

    if len(robot.state.actions) > 0:
        for i, action in enumerate(robot.state.actions):
            prompt += f"\nStep {i}:"
            prompt += f"\n- Action: {action}"
            if i > 0 and i - 1 < len(robot.state.gemini_estimates):
                est = robot.state.gemini_estimates[i - 1]
                prompt += f"\n- Previous estimate: x={est[0]:.2f}m, y={est[1]:.2f}m, θ={math.degrees(est[2]):.1f}°"
            readings = robot.state.sensor_readings[i]
            prompt += "\n- Visible beacons:"
            for beacon in readings:
                if beacon['visible']:
                    prompt += f"\n  Beacon {beacon['beacon'].id}: d={beacon['distance']:.2f}m, θ={math.degrees(beacon['angle']):.1f}°"

    # Add current measurements
    prompt += "\n\nCurrent visible beacons:"
    for beacon in sensor_data['visible_beacons']:
        if beacon['visible']:
            prompt += f"\n- Beacon {beacon['beacon'].id}: d={beacon['distance']:.2f}m, θ={math.degrees(beacon['angle']):.1f}°"

    prompt += "\n\n1. Robot must remain in valid operating zone"
    prompt += "\n2. Wall blocks beacon line-of-sight"
    prompt += "\n3. Position estimate must be consistent with sensor data"
    prompt += "\n4. Motion must be physically possible given constraints"

    prompt += """
    In your reasoning, include 
    
    When solving robot localization problems:

Parse key components:


Operating constraints (valid zones, walls)
Robot capabilities (movement commands)
Reference points (beacon positions)
Visibility rules (line-of-sight)
Available sensor data (distances, angles)


Apply systematic validation:


Check position validity (zones, movement physics)
Verify beacon visibility patterns
Ensure sensor data consistency
Cross-validate using:
a) Forward calculation (previous position + movement)
b) Triangulation from beacon measurements
c) Visibility pattern matching
d) Physical constraint verification


Reasoning process:


Use closest beacon measurements first
Each measurement creates a geometric constraint
Multiple measurements narrow possible positions
Previous position + movement adds additional constraint
Final position must explain ALL observations
Cross-check answer satisfies all constraints


Output format - this needs to be followed!! No formatting, no nothing:
FINAL ANSWER: x=<value>m, y=<value>m, θ=<value>°

Remember: True position must simultaneously satisfy geometric constraints (distances/angles), physical constraints (valid movement/zones), and logical constraints (beacon visibility).
    
    """

    prompt += "\n\nProvide pose estimate at the end of your response as: FINAL ANSWER: x=<value>m, y=<value>m, θ=<value>°"

    with open('localization_tests/current_prompt.txt', 'w') as f:
        f.write(prompt)

    return prompt


def main():
    response = call_gemini()
    print("\nGemini Response:")
    print(response)


if __name__ == "__main__":
    main()