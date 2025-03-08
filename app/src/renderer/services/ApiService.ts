/**
 * Agent Assembly Line
 * License Apache-2.0
 * See the LICENSE file in the root directory for details.
 */

import axios from 'axios';

export interface Message {
  sender: 'user' | 'llm' | 'system';
  text: string;
}

export interface Info {
  name: string;
  description: string;
  LLM: string;
  doc: string;
  memoryStrategy: string;
  savingInterval: number;
  autoSaveMessageCount: number;
  memoryPrompt: string;
  userUploadedFiles: string;
  userUploadedUrls: string;
}

const API_URL = 'http://localhost:8000/api';

export const fetchMessages = async (): Promise<Message[]> => {
  const response = await fetch(`${API_URL}/messages`);
  if (!response.ok) {
    throw new Error('Failed to fetch messages');
  }
  return response.json();
};

export const sendMessage = async (message: Message): Promise<string> => {
  const response = await fetch(`${API_URL}/question`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ prompt: message.text }),
  });
  if (!response.ok) {
    throw new Error('Failed to send message');
  }
  const data = await response.json();
  return data.answer;
};

export const selectAgent = async (agent: string): Promise<void> => {
  const response = await fetch(`${API_URL}/select-agent`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ agent: agent }),
  });
  if (!response.ok) {
    throw new Error('Failed to select agent');
  }
};

export const fetchInfo = async (): Promise<Info> => {
  const response = await fetch(`${API_URL}/info`);
  if (!response.ok) {
    throw new Error('Failed to fetch information');
  }
  const data = await response.json();
  return data;
};

export const fetchDataSources = async (): Promise<string[]> => {
  const response = await fetch(`${API_URL}/data-sources`);
  if (!response.ok) {
    throw new Error('Failed to fetch data sources');
  }
  const data = await response.json();
  return data;
};

export const fetchMemory = async (): Promise<string> => {
  const response = await fetch(`${API_URL}/memory`);
  if (!response.ok) {
    throw new Error('Failed to fetch memory');
  }
  const data = await response.json();
  return data.memory;
};

export const fetchHistory = async (): Promise<Message[]> => {
  const response = await fetch(`${API_URL}/load-history`);
  if (!response.ok) {
    throw new Error('Failed to fetch history');
  }
  const data = await response.json();
  return data.messages || [];
};

export const uploadFile = async (file: File): Promise<Message> => {
  const formData = new FormData();
  formData.append('file', file);
  try {
    const response = await axios.post(`${API_URL}/upload-file`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return {
      sender: 'system',
      text: response.data.message || `File "${file.name}" uploaded successfully.`,
    };
  } catch (error) {
    console.error('Error uploading file:', error);
    return {
      sender: 'system',
      text: (error as any).response?.data?.message || `File "${file.name}" not added. Error: ${(error as any).message}`,
    };
  }
};