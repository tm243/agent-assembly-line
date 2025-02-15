/**
 * Agent Assembly Line
 * License Apache-2.0
 * See the LICENSE file in the root directory for details.
 */

import React, { useState } from 'react';
import { Box, TextField, Button } from '@mui/material';
import Chat from './Chat';
import PulsingDot from './PulsingDot';
import { sendMessage, Message } from '../services/ApiService';

const MainLayout = () => {
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isSending, setIsSending] = useState(false);

  const handleSendMessage = async () => {
    if (inputValue.trim() === '') return;

    const userMessage: Message = { sender: 'user', text: inputValue };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setIsSending(true);

    try {
      const answer = await sendMessage(userMessage);
      const llmMessage: Message = { sender: 'llm', text: answer };
      setMessages((prevMessages) => [...prevMessages, llmMessage]);
      setInputValue('');
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <Box display="flex" height="100vh">
      <Box flex={2} display="flex" flexDirection="column" borderRight="1px solid #ccc">
        <Box flex={1} overflow="auto">
          <Chat messages={messages} />
        </Box>
        <Box p={2} display="flex" alignItems="center">
            <Box sx={{ visibility: isSending ? 'visible' : 'hidden', marginRight: 2 }}>
                <PulsingDot />
            </Box>
            <TextField
                fullWidth
                placeholder="Type something..."
                variant="outlined"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
            />
            <Button variant="contained" color="primary" onClick={handleSendMessage}>
                Send
            </Button>
        </Box>
      </Box>
      <Box flex={1} p={2}>
        {/* Content for the right panel */}
      </Box>
    </Box>
  );
};

export default MainLayout;