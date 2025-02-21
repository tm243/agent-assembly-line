/**
 * Agent Assembly Line
 * License Apache-2.0
 * See the LICENSE file in the root directory for details.
 */

import React, { useState, useEffect } from 'react';
import { Box, TextField, Button, Typography } from '@mui/material';
import Chat from './Chat';
import PulsingDot from './PulsingDot';
import { sendMessage, Message, fetchInfo } from '../services/ApiService';

const MainLayout = () => {
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [name, setName] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [llm, setLlm] = useState<string>('');
  const [doc, setDoc] = useState<string>('');

  useEffect(() => {
    const loadInfo = async () => {
      try {
        const fetchedInfo = await fetchInfo();
        const info: { name: string, description: string } = fetchedInfo;
        setName(info.name);
        setDescription(info.description);
        setLlm(fetchedInfo.LLM);
        setDoc(fetchedInfo.doc);
      } catch (error) {
        console.error('Failed to fetch info:', error);
      }
    };

    loadInfo();
  }, []);

  const handleSendMessage = async () => {
    if (inputValue.trim() === '') return;

    const userMessage: Message = { sender: 'user', text: inputValue };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setIsSending(true);

    try {
      setInputValue('');
      const answer = await sendMessage(userMessage);
      const llmMessage: Message = { sender: 'llm', text: answer };
      setMessages((prevMessages) => [...prevMessages, llmMessage]);
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
        <Box flex={1} p={2}>
            <Typography variant="body1">{name}</Typography>
            <Typography variant="body2">{description}</Typography>
            <br />
            <Typography variant="body2" sx={{ fontSize: '0.75rem', color: '#AAA' }}>used LLM: {llm}</Typography>
            <Typography variant="body2" sx={{ fontSize: '0.75rem', color: '#AAA' }}>used doc: {doc}</Typography>
        </Box>

      </Box>
    </Box>
  );
};

export default MainLayout;