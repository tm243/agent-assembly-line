/**
 * Agent Assembly Line
 * License Apache-2.0
 * See the LICENSE file in the root directory for details.
 */

import React, { useState, useEffect } from 'react';
import { Box, TextField, Button, Typography, MenuItem, Select, FormControl, InputLabel, SelectChangeEvent } from '@mui/material';
import Chat from './Chat';
import PulsingDot from './PulsingDot';
import { sendMessage, Message, fetchInfo, selectAgent, fetchAvailableAgents, fetchHistory, streamMessage } from '../services/ApiService';
import MemoryDisplay from './MemoryDisplay';
import FileUploadButton from './FileUploadButton';

const defaultAgent = "chat-demo";

const MainLayout = () => {
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [streamingMessageId, setStreamingMessageId] = useState<number | null>(null);
  const [name, setName] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [llm, setLlm] = useState<string>('');
  const [doc, setDoc] = useState<string>('');
  const [memoryStrategy, setMemoryStrategy] = useState<string>('');
  const [savingInterval, setSavingInterval] = useState<number>(0);
  const [autoSaveMessageCount, setAutoSaveMessageCount] = useState<number>(0);
  const [memoryPrompt, setMemoryPrompt] = useState<string>('');
  const [availableAgents, setAvailableAgents] = useState<string[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<string>('');
  const [userUploadedFiles, setUserUploadedFiles] = useState<string>('');
  const [userAddedUrls, setUserAddedUrls] = useState<string>('');

  const handleSystemMessage = (message: Message) => {
    setMessages((prevMessages) => [...prevMessages, message]);
    loadInfo();
  };

  const loadInfo = async () => {
    try {
      const fetchedInfo = await fetchInfo();
      const info: { name: string, description: string } = fetchedInfo;
      setName(info.name);
      setDescription(info.description);
      setLlm(fetchedInfo.LLM);
      setDoc(fetchedInfo.doc);
      setMemoryStrategy(fetchedInfo.memoryStrategy);
      setSavingInterval(fetchedInfo.savingInterval);
      setAutoSaveMessageCount(fetchedInfo.autoSaveMessageCount);
      setMemoryPrompt(fetchedInfo.memoryPrompt);
      setUserUploadedFiles(fetchedInfo.userUploadedFiles);
      setUserAddedUrls(fetchedInfo.userAddedUrls);
    } catch (error) {
      console.error('Failed to fetch info:', error);
    }
  };

  useEffect(() => {
    const loadDefaultAgent = async () => {
        try {
          setSelectedAgent(defaultAgent);
          await selectAgent(defaultAgent);
          loadInfo();
          loadHistory();
        } catch (error) {
          console.error('Failed to select agent:', error);
        }
    };

    const loadAvailableAgents = async () => {
        try {
          const agents = await fetchAvailableAgents();
          setAvailableAgents(agents);
        } catch (error) {
          console.error('Failed to fetch agents:', error);
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
    loadAvailableAgents();
  }, []);

  const handleSendMessage = async () => {
    if (inputValue.trim() === '') return;

    const userMessage: Message = { sender: 'user', text: inputValue };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setIsSending(true);

    try {
      setInputValue('');
      const { answer, shouldUpdate } = await sendMessage(userMessage);
      const llmMessage: Message = { sender: 'llm', text: answer };
      setMessages((prevMessages) => [...prevMessages, llmMessage]);

      if (shouldUpdate) {
        loadInfo();
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsSending(false);
    }
  };

  const handleStreamMessage = async () => {
    if (inputValue.trim() === '') return;

    const userMessage: Message = { sender: 'user', text: inputValue };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setIsSending(true);

    try {
      setInputValue('');
      const tempMessage: Message = { sender: 'llm', text: '' };
      setMessages((prevMessages) => [...prevMessages, tempMessage]);
      const tempMessageId = messages.length+1;

      streamMessage(
        userMessage,
        (data: string) => {
          let safeData = data.trim() === '' ? '\n' : data;
          setMessages((prevMessages) => {
            const updatedMessages = [...prevMessages];
            const prevText = updatedMessages[tempMessageId].text;

            // Avoid double newlines: Don't add if previous text already ends with '\n'
            if (safeData === '\n' && prevText.endsWith('\n')) {
              return updatedMessages;
            }

            updatedMessages[tempMessageId] = { ...updatedMessages[tempMessageId], text: prevText + safeData };
            return updatedMessages;
          });
        },
        () => {
          setStreamingMessageId(null);
          setIsSending(false);
        },
        (error) => {
          console.error('Failed to stream message:', error);
          setStreamingMessageId(null);
          setIsSending(false);
        }
      );
    } catch (error) {
      console.error('Failed to stream message:', error);
      setIsSending(false);
    }
  };

  const handleAgentChange = async (event: SelectChangeEvent<string>) => {
    const newAgent = event.target.value as string;

    setName('');
    setDescription('');
    setLlm('');
    setDoc('');
    setMessages([]);
    setUserUploadedFiles('');
    setUserAddedUrls('');

    setSelectedAgent(newAgent);
    try {
      await selectAgent(newAgent);
      const fetchedInfo = await fetchInfo();
      setName(fetchedInfo.name);
      setDescription(fetchedInfo.description);
      setDoc(fetchedInfo.doc);
      setAutoSaveMessageCount(fetchedInfo.autoSaveMessageCount);
      setMemoryPrompt(fetchedInfo.memoryPrompt);
      setMemoryStrategy(fetchedInfo.memoryStrategy);
      setSavingInterval(fetchedInfo.savingInterval);
      setUserUploadedFiles(fetchedInfo.userUploadedFiles);
      setUserAddedUrls(fetchedInfo.userAddedUrls);
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
                onKeyDown={(e) => {if(e.key === 'Enter') {handleStreamMessage();}}}
                onChange={(e) => setInputValue(e.target.value)}
            />
            <FileUploadButton onSystemMessage={handleSystemMessage} />
            <Button variant="contained" color="primary" onClick={handleStreamMessage}>
                Send
            </Button>
        </Box>
      </Box>
      <Box flex={1} display="flex" flexDirection="column" borderRight="1px solid #ccc">
          <Box flex={1} p={2}>
            <FormControl fullWidth size='small'>
                <InputLabel>Agent</InputLabel>
                <Select
                    value={selectedAgent}
                    onChange={handleAgentChange}
                >
                    {availableAgents.map((agent) => (
                    <MenuItem key={agent} value={agent}>
                        {agent}
                    </MenuItem>
                    ))}
                </Select>
            </FormControl>
            <Typography variant="body1">{name}</Typography>
            <Typography variant="body2">{description}</Typography>
            <br />
            <Typography variant="body2" sx={{ fontSize: '0.75rem', color: '#AAA' }}>LLM: {llm}</Typography>
            <Typography variant="body2" sx={{ fontSize: '0.75rem', color: '#AAA' }}>RAG: {doc}</Typography>
            <Typography variant="body2" sx={{ fontSize: '0.75rem', color: '#AAA' }}>Memory Strategy: {memoryStrategy}</Typography>
            <Typography variant="body2" sx={{ fontSize: '0.75rem', color: '#AAA' }}>saving interval: {savingInterval}</Typography>
            <Typography variant="body2" sx={{ fontSize: '0.75rem', color: '#AAA' }}>autoSave message count: {autoSaveMessageCount}</Typography>
            {/* <Typography variant="body2" sx={{ fontSize: '0.75rem', color: '#AAA' }}>memory prompt: {memoryPrompt}</Typography> */}
            <Typography variant="body2" sx={{ fontSize: '0.75rem', color: '#AAA' }}>files: {userUploadedFiles}</Typography>
            <Typography variant="body2" sx={{ fontSize: '0.75rem', color: '#AAA' }}>urls: {userAddedUrls}</Typography>

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