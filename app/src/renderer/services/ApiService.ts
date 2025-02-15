
/**
 * Agent Assembly Line
 * License Apache-2.0
 * See the LICENSE file in the root directory for details.
 */

export interface Message {
  sender: 'user' | 'llm';
  text: string;
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
  console.log(data.answer);
  return data.answer;
};