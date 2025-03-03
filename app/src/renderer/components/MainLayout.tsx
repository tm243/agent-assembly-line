/**
 * Agent Assembly Line
 * License Apache-2.0
 * See the LICENSE file in the root directory for details.
 */

import React, { useState, useEffect } from 'react';
import { Box, TextField, Button, Typography, MenuItem, Select, FormControl, InputLabel, SelectChangeEvent } from '@mui/material';
import Chat from './Chat';
import PulsingDot from './PulsingDot';
import { sendMessage, Message, fetchInfo, selectAgent, fetchDataSources, fetchHistory } from '../services/ApiService';
import MemoryDisplay from './MemoryDisplay';
import FileUploadButton from './FileUploadButton';

const defaultAgent = "chat-demo";

const MainLayout = () => {
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [name, setName] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [llm, setLlm] = useState<string>('');
  const [doc, setDoc] = useState<string>('');
  const [availableDataSources, setAvailableDataSources] = useState<string[]>([]);
  const [selectedDataSource, setSelectedDataSource] = useState<string>('');

  const handleSystemMessage = (message: Message) => {
    setMessages((prevMessages) => [...prevMessages, message]);
  };

  useEffect(() => {
    const loadDefaultAgent = async () => {
        try {
          setSelectedDataSource(defaultAgent);
          await selectAgent(defaultAgent);
          loadInfo();
          loadHistory();
        } catch (error) {
          console.error('Failed to select agent:', error);
        }
    };

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

    const loadAvailableDataSources = async () => {
        try {
          const sources = await fetchDataSources();
          setAvailableDataSources(sources);
        } catch (error) {
          console.error('Failed to fetch data sources:', error);
        }
      };

    const loadHistory = async () => {
      try {
        const history = await fetchHistory();
        setMessages(history);
      } catch (error) {
        console.error('Failed to load history:', error);
      }
    };

    loadDefaultAgent();
    loadAvailableDataSources();
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
      setMessages((prevMessages) => [...prevMessages, userMessage, llmMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsSending(false);
    }
  };

  const handleDataSourceChange = async (event: SelectChangeEvent<string>) => {
    const newDataSource = event.target.value as string;
    setSelectedDataSource(newDataSource);
    try {
      await selectAgent(newDataSource);
      const fetchedInfo = await fetchInfo();
      setName(fetchedInfo.name);
      setDescription(fetchedInfo.description);
      setDoc(fetchedInfo.doc);
      const history = await fetchHistory();
      setMessages(history);
    } catch (error) {
      console.error('Failed to select agent:', error);
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
                size='small'
                onKeyDown={(e) => {if(e.key === 'Enter') {handleSendMessage();}}}
                onChange={(e) => setInputValue(e.target.value)}
            />
            <FileUploadButton onSystemMessage={handleSystemMessage} />
            <Button variant="contained" color="primary" onClick={handleSendMessage}>
                Send
            </Button>
        </Box>
      </Box>
      <Box flex={1} display="flex" flexDirection="column" borderRight="1px solid #ccc">
          <Box flex={1} p={2}>
            <FormControl fullWidth size='small'>
                <InputLabel>Data Source</InputLabel>
                <Select
                    value={selectedDataSource}
                    onChange={handleDataSourceChange}
                >
                    {availableDataSources.map((source) => (
                    <MenuItem key={source} value={source}>
                        {source}
                    </MenuItem>
                    ))}
                </Select>
            </FormControl>
            <Typography variant="body1">{name}</Typography>
            <Typography variant="body2">{description}</Typography>
            <br />
            <Typography variant="body2" sx={{ fontSize: '0.75rem', color: '#AAA' }}>used LLM: {llm}</Typography>
            <Typography variant="body2" sx={{ fontSize: '0.75rem', color: '#AAA' }}>used doc: {doc}</Typography>
          </Box>
          <Box sx={{flexShrink: 0, py: 2, height: "40%", backgroundColor: "#f8f9fa", borderTop: "1px solid #ccc", width: "100%"}}>
            <Typography variant="body2" sx={{ fontSize: "0.75rem", color: "#AAA", marginLeft: 1 }} align="left">
              Memory
            </Typography>
            <MemoryDisplay />
          </Box>
        </Box>
      </Box>
  );
};

export default MainLayout;