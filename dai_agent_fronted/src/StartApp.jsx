import logo from './logo.svg';
import './App.css';
import fs from 'fs'
import yaml from 'js-yaml'

import React, { useState, useEffect } from 'react';

/**
 * v0 by Vercel.
 * @see https://v0.dev/t/vWHQ7AzR8lD
 * Documentation: https://v0.dev/docs#integrating-generated-code-into-your-nextjs-app
 */
function StartApp() {
  const config_data = import.meta.env;
  const server_ip = config_data.VITE_server_ip;
  const back_port = config_data.VITE_back_port;
  const front_port2 = config_data.VITE_front_port2;

  const [templates, setTemplates] = useState([]);

  useEffect(() => {
    const fetchTemplates = async () => {
      const envs = await get_envs();
      setTemplates(envs);
    };
    fetchTemplates();
  }, []);

  const get_envs = async () => {
    var url = `http://${server_ip}:${back_port}/list_envs/`;
    try {
      const response = await fetch(url,
        {
          method: 'GET'
        }
      );
      const data = await response.json();
      return data.envs;  // Using 'envs' instead of 'templates' as per the API response
    } catch (error) {
      console.error("Error fetching environments:", error);
      return [];
    }
  };


  const start_sim = async () => {

    var fork_name = document.getElementById("fork_sim").value;
    var new_name = document.getElementById("new_sim").value;
    var model_select = document.getElementById("model");
    var model_select_index = model_select.selectedIndex;
    var model = model_select.options[model_select_index].value;
    const params = new URLSearchParams();
    params.append('fork', fork_name);
    params.append('new', new_name);
    params.append('model', model)
    var url = `http://${server_ip}:${back_port}/start/?${params.toString()}`;
    console.log("Request the url to start simulation: ", url);
    const response = await fetch(url, {
      method: 'GET',
      mode: 'no-cors'
    }).then(
      (data) => {
        console.log("response2: ", data)
      }
    );
    // window.location.href = "/act";
    window.location.href = `/act`;
  };
  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gradient-to-br from-blue-200 to-red-200">
      <div className="flex flex-col items-center justify-center p-10 space-y-6 bg-white rounded-lg shadow-lg w-1/3">
        <div className="w-full max-w-md space-y-6">
          <div className="flex-col space-y-2">
            <label className="text-sm font-medium" htmlFor="model">
              Simulation Type:
            </label>
            <select
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
              id="mode"
            >
              {/* <option>请选择环境</option> */}
              <option>offline</option>
              <option>online</option>
            </select>
          </div>
          <div className="flex flex-col space-y-2">
            <label className="text-sm font-medium" htmlFor="input1">
              Template:
            </label>
            <input
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
              id="fork_sim"
              placeholder=""
              type="text"
            />
          </div>
          <div className="flex flex-col space-y-2">
            <label className="text-sm font-medium" htmlFor="input1">
              Simulation Name:
            </label>
            <input
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
              id="new_sim"
              placeholder=""
              type="text"
            />
          </div>
          <div className="flex flex-col space-y-2">
            <label className="text-sm font-medium" htmlFor="temperature">
              LLM:
            </label>
            <select
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
              id="model"
            >
              <option>vicuna-13b-v1.5</option>
              <option>Qwen/Qwen2-7B-Instruct (32K)</option>
              <option>THUDM/glm-4-9b-chat (32K)</option>
              <option>01-ai/Yi-1.5-9B-Chat-16K (16K)</option>
              <option>gpt-3.5-turbo</option>
            </select>
            {/* <inputh
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
              id="temperature"
              placeholder=""
              type="text"
            /> */}
          </div>
          {/* <div className="flex items-center space-x-2">
            <label className="text-sm font-medium" htmlFor="agent">
              Agent:
            </label>
            <div className="flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm">
              <span className="text-sm">Isabella.docx</span>
              <button className="ml-2 text-indigo-600 hover:text-indigo-900" type="button">
                <XIcon className="h-4 w-4" />
              </button>
            </div>
            <button className="p-2 text-white bg-blue-600 rounded-md hover:bg-blue-700" type="button">
              <PlusIcon className="h-4 w-4" />
            </button>
          </div> */}
          {/* <div className="flex items-center space-x-2">
            <label className="text-sm font-medium" htmlFor="knowledge">
              Knowledge Base:
            </label>
            <div className="flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm">
              <span className="text-sm">knowledge.docx</span>
              <button className="ml-2 text-indigo-600 hover:text-indigo-900" type="button">
                <XIcon className="h-4 w-4" />
              </button>
            </div>
            <button className="p-2 text-white bg-blue-600 rounded-md hover:bg-blue-700" type="button">
              <PlusIcon className="h-4 w-4" />
            </button>
          </div> */}
          
          <button
            className="w-full px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
            type="button"
            onClick={start_sim}
          >
            Start
          </button>

        </div>
      </div>

      <div className="absolute bottom-10 w-full text-center mb-0">
        <h2 className="text-2xl font-bold">Social Simulation Agent</h2>
        <p className="mt-4 text-gray-600">
          Developed by DAI Lab, Zhejiang University.
        </p>
      </div>
    </div>
  )
}

function PlusIcon(props) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M5 12h14" />
      <path d="M12 5v14" />
    </svg>
  )
}


function XIcon(props) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M18 6 6 18" />
      <path d="m6 6 12 12" />
    </svg>
  )
}

export default StartApp;
