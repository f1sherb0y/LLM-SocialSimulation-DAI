"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: gpt_structure.py
Description: Wrapper functions for calling OpenAI APIs.
"""

import json
import random
from openai import OpenAI
import time

from utils import openai_api_base, openai_api_key, default_model

client = OpenAI(api_key=openai_api_key, base_url=openai_api_base)


def gpt_completion_single_request(prompt, gpt_parameters):
    """
    Make a single GPT completion request using provided parameters.

    ARGS:
      prompt: A string prompt for the GPT model.
      gpt_parameters: A dictionary with keys for parameter names and values
                      for parameter values.

    RETURNS:
      A string containing the GPT response.
    """

    # Set the model to use
    model = gpt_parameters["engine"] if not default_model else default_model

    try:
        response = client.completions.create(
            model=model,
            prompt=prompt,
            temperature=gpt_parameters["temperature"],
            max_tokens=gpt_parameters["max_tokens"],
            top_p=gpt_parameters["top_p"],
            frequency_penalty=gpt_parameters["frequency_penalty"],
            presence_penalty=gpt_parameters["presence_penalty"],
            stream=gpt_parameters["stream"],
            stop=gpt_parameters["stop"],
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error during GPT request: {e}")
        return "An error occurred during the request."


def gpt_completion_request(prompt, gpt_parameters, max_retries=3, timeout=10):
    """
    Make a single GPT completion request with retries and timeout handling.

    ARGS:
      prompt: A string prompt for the GPT model.
      gpt_parameters: A dictionary with keys for parameter names and values
                      for parameter values.
      max_retries: Maximum number of retry attempts.
      timeout: Maximum time in seconds to wait for a successful response.

    RETURNS:
      A string containing the GPT response, or an error message if unsuccessful.
    """
    start_time = time.time()
    tries = 0

    while tries < max_retries:
        elapsed_time = time.time() - start_time
        if elapsed_time > timeout:
            return "Request timed out."

        response = gpt_completion_single_request(prompt, gpt_parameters)

        if response:
            return response

        tries += 1
        time.sleep(0.1)  # Optional: Wait before retrying

    return "Request failed after maximum retries."


def gpt_chat_single_request(user_prompt, gpt_parameters, system_prompt=""):
    """
    Make a single GPT chat request using provided parameters.

    ARGS:
      prompt: A string prompt for the GPT model.
      gpt_parameters: A dictionary with keys for parameter names and values
                      for parameter values.

    RETURNS:
      A string containing the GPT chat response.
    """

    # Set the model to use
    model = gpt_parameters["engine"] if not default_model else default_model

    try:
        # Prepare the messages as a chat input
        messages = []
        if system_prompt is not None and system_prompt != "":
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=gpt_parameters["temperature"],
            max_tokens=gpt_parameters["max_tokens"],
            top_p=gpt_parameters["top_p"],
            frequency_penalty=gpt_parameters["frequency_penalty"],
            presence_penalty=gpt_parameters["presence_penalty"],
            stream=gpt_parameters["stream"],
            stop=gpt_parameters["stop"],
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        print(f"Error during GPT chat request: {e}")
        return None


def gpt_chat_request(
    prompt, gpt_parameters, system_prompt="", max_retries=3, timeout=10
):
    """
    Make a single GPT chat request with retries and timeout handling, including a system prompt.

    ARGS:
      prompt: A string prompt for the GPT model.
      gpt_parameters: A dictionary with keys for parameter names and values
                      for parameter values.
      system_prompt: A string prompt to set the system's initial instructions or context.
      max_retries: Maximum number of retry attempts.
      timeout: Maximum time in seconds to wait for a successful response.

    RETURNS:
      A string containing the GPT chat response, or an error message if unsuccessful.
    """
    start_time = time.time()
    tries = 0

    while tries < max_retries:
        elapsed_time = time.time() - start_time
        if elapsed_time > timeout:
            return "Request timed out."

        response = gpt_chat_single_request(prompt, gpt_parameters, system_prompt)

        if response:
            return response

        tries += 1
        time.sleep(0.1)  # Optional: Wait before retrying

    return "Request failed after maximum retries."


def GPT4_safe_generate_response(
    prompt,
    example_output,
    special_instruction,
    repeat=3,
    fail_safe_response="error",
    func_validate=None,
    func_clean_up=None,
    verbose=False,
):
    prompt = 'GPT-3 Prompt:\n"""\n' + prompt + '\n"""\n'
    prompt += (
        f"Output the response to the prompt above in json. {special_instruction}\n"
    )
    prompt += "Example output json:\n"
    prompt += '{"output": "' + str(example_output) + '"}'

    if verbose:
        print("CHAT GPT PROMPT")
        print(prompt)

    for i in range(repeat):

        try:
            curr_gpt_response = gpt_chat_request(prompt).strip()
            end_index = curr_gpt_response.rfind("}") + 1
            curr_gpt_response = curr_gpt_response[:end_index]
            curr_gpt_response = json.loads(curr_gpt_response)["output"]

            if func_validate(curr_gpt_response, prompt=prompt):
                return func_clean_up(curr_gpt_response, prompt=prompt)

            if verbose:
                print("---- repeat count: \n", i, curr_gpt_response)
                print(curr_gpt_response)
                print("~~~~")

        except:
            pass

    return False


def ChatGPT_safe_generate_response(
    prompt,
    example_output,
    special_instruction,
    repeat=3,
    fail_safe_response="error",
    func_validate=None,
    func_clean_up=None,
    verbose=False,
):
    # prompt = 'GPT-3 Prompt:\n"""\n' + prompt + '\n"""\n'
    prompt = '"""\n' + prompt + '\n"""\n'
    prompt += (
        f"Output the response to the prompt above in json. {special_instruction}\n"
    )
    prompt += "Example output json:\n"
    prompt += '{"output": "' + str(example_output) + '"}'

    if verbose:
        print("CHAT GPT PROMPT")
        print(prompt)
    print("lg: start")  #
    for i in range(repeat):

        try:
            print("lg: try")  #
            curr_gpt_response = gpt_completion_request(prompt)
            print("lg")  #
            print(curr_gpt_response)  #
            print("lg")  #
            curr_gpt_response = curr_gpt_response.strip()
            end_index = curr_gpt_response.rfind("}") + 1
            ###
            begin_index = curr_gpt_response.find("{")  #
            curr_gpt_response = curr_gpt_response[begin_index:end_index]  #
            ###
            # curr_gpt_response = curr_gpt_response[:end_index]

            curr_gpt_response = json.loads(curr_gpt_response)["output"]
            print("lg: happy")  #

            # curr_gpt_response = curr_gpt_response + ""#lg
            curr_gpt_response = str(curr_gpt_response)  # lg

            # print ("---ashdfaf")
            # print (curr_gpt_response)
            # print ("000asdfhia")

            if func_validate(curr_gpt_response, prompt=prompt):
                return func_clean_up(curr_gpt_response, prompt=prompt)

            if verbose:
                print("---- repeat count: \n", i, curr_gpt_response)
                print(curr_gpt_response)
                print("~~~~")

        except:
            pass
    print("lg: fail")  #
    return False


# tyn
def ChatGPT_safe_generate_response_new(
    prompt,
    example_output,
    special_instruction,
    repeat=3,
    fail_safe_response="error",
    func_validate=None,
    func_clean_up=None,
    verbose=False,
):
    # prompt = 'GPT-3 Prompt:\n"""\n' + prompt + '\n"""\n'
    prompt = '"""\n' + prompt + '\n"""\n'
    prompt += f"Please output the response to the prompt above in json. {special_instruction}\n"
    prompt += "Example output json:\n"
    prompt += '{"output": ' + str(example_output) + "}"

    if verbose:
        print("CHAT GPT PROMPT")
        print(prompt)
    print("lg: start")  #
    for i in range(repeat):

        try:
            print("lg: try")  #
            curr_gpt_response = gpt_completion_request(prompt)
            print("lg")  #
            print(curr_gpt_response)  #
            print("lg")  #
            curr_gpt_response = curr_gpt_response.strip()
            end_index = curr_gpt_response.rfind("}") + 1
            ###
            begin_index = curr_gpt_response.find("{")  #
            curr_gpt_response = curr_gpt_response[begin_index:end_index]  #
            ###
            # curr_gpt_response = curr_gpt_response[:end_index]

            curr_gpt_response = json.loads(curr_gpt_response)["output"]
            print("lg: happy")  #

            # curr_gpt_response = curr_gpt_response + ""#lg
            curr_gpt_response = str(curr_gpt_response)  # lg

            # print ("---ashdfaf")
            # print (curr_gpt_response)
            # print ("000asdfhia")

            if func_validate(curr_gpt_response, prompt=prompt):
                return func_clean_up(curr_gpt_response, prompt=prompt)

            if verbose:
                print("---- repeat count: \n", i, curr_gpt_response)
                print(curr_gpt_response)
                print("~~~~")

        except:
            pass
    print("lg: fail")  #
    return False


def generate_prompt(curr_input, prompt_lib_file):
    """
    Takes in the current input (e.g. comment that you want to classifiy) and
    the path to a prompt file. The prompt file contains the raw str prompt that
    will be used, which contains the following substr: !<INPUT>! -- this
    function replaces this substr with the actual curr_input to produce the
    final promopt that will be sent to the GPT3 server.
    ARGS:
      curr_input: the input we want to feed in (IF THERE ARE MORE THAN ONE
                  INPUT, THIS CAN BE A LIST.)
      prompt_lib_file: the path to the promopt file.
    RETURNS:
      a str prompt that will be sent to OpenAI's GPT server.
    """
    if type(curr_input) == type("string"):
        curr_input = [curr_input]
    curr_input = [str(i) for i in curr_input]

    f = open(prompt_lib_file, "r")
    prompt = f.read()
    f.close()
    for count, i in enumerate(curr_input):
        prompt = prompt.replace(f"!<INPUT {count}>!", i)
    if "<commentblockmarker>###</commentblockmarker>" in prompt:
        prompt = prompt.split("<commentblockmarker>###</commentblockmarker>")[1]
    return prompt.strip()


def safe_generate_response(
    prompt,
    gpt_parameter,
    repeat=5,
    fail_safe_response="error",
    func_validate=None,
    func_clean_up=None,
    verbose=False,
):
    if verbose:
        print(prompt)

    for i in range(repeat):
        curr_gpt_response = gpt_completion_request(prompt, gpt_parameter)
        if func_validate(curr_gpt_response, prompt=prompt):
            return func_clean_up(curr_gpt_response, prompt=prompt)
        if verbose:
            print("---- repeat count: ", i, curr_gpt_response)
            print(curr_gpt_response)
            print("~~~~")
    return fail_safe_response


def get_embedding(text, model="text-embedding-ada-002"):

    model = model if not default_model else default_model

    text = text.replace("\n", " ")
    if not text:
        text = "this is blank"
    return client.embeddings.create(input=[text], model=model)["data"][0]["embedding"]


if __name__ == "__main__":
    gpt_parameter = {
        "engine": "text-davinci-003",
        "max_tokens": 50,
        "temperature": 0,
        "top_p": 1,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": ['"'],
    }
    curr_input = ["driving to a friend's house"]
    prompt_lib_file = "prompt_template/test_prompt_July5.txt"
    prompt = generate_prompt(curr_input, prompt_lib_file)

    def __func_validate(gpt_response):
        if len(gpt_response.strip()) <= 1:
            return False
        if len(gpt_response.strip().split(" ")) > 1:
            return False
        return True

    def __func_clean_up(gpt_response):
        cleaned_response = gpt_response.strip()
        return cleaned_response

    output = safe_generate_response(
        prompt, gpt_parameter, 5, "rest", __func_validate, __func_clean_up, True
    )

    print(output)
