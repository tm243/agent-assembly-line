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
  userAddedUrls: string;
}

const API_URL = 'http://localhost:8000/api';

export const fetchMessages = async (): Promise<Message[]> => {
  const response = await fetch(`${API_URL}/messages`);
  if (!response.ok) {
    throw new Error('Failed to fetch messages');
  }
  return response.json();
};

export const sendMessage = async (message: Message): Promise<{ answer: string; shouldUpdate: boolean }> => {
  try {
    const response = await axios.post(`${API_URL}/question`, { prompt: message.text });
    return {
      answer: response.data.answer,
      shouldUpdate: response.data.shouldUpdate || false,
    };
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};

export const streamMessage = (message: Message, onMessage: (data: string) => void,  onComplete: () => void, onError: (error: Event) => void): void => {
  const eventSource = new EventSource(`${API_URL}/stream?prompt=${encodeURIComponent(message.text)}`);

  eventSource.onmessage = (event) => {
    if (event.data === '[DONE]') {
      eventSource.close();
      onComplete();
    } else {
      onMessage(event.data);
    }  };

  eventSource.onerror = (error) => {
    console.error('Error with message stream:', error);
    eventSource.close();
    onError(error);
  };
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

export const fetchAvailableAgents = async (): Promise<string[]> => {
  const response = await fetch(`${API_URL}/agents`);
  if (!response.ok) {
    throw new Error('Failed to fetch available agents');
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