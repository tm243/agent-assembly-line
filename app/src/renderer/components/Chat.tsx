/**
 * Agent Assembly Line
 * License Apache-2.0
 * See the LICENSE file in the root directory for details.
 */

import React, { useEffect, useRef } from 'react';
import { Box, Typography, Paper } from '@mui/material';
import MarkdownRenderer from './MarkdownRenderer';

interface Message {
  sender: 'user' | 'llm' | 'system';
  text: string;
}

interface ChatProps {
  messages: Message[];
}

const Chat: React.FC<ChatProps> = ({ messages }) => {
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight + 40;
    }
  }, [messages]);

  const renderRow = (message: Message, index: number) => (
    <Paper
      key={index}
      elevation={0} // Remove shadows
      style={{
        padding: message.sender === 'system' ? '2px' : '10px',
        marginBottom: '10px',
        alignSelf: message.sender === 'user' ? 'flex-end' : 'flex-start',
        backgroundColor: message.sender === 'user' ? '#EFEFEF' : message.sender === 'llm' ? 'white' : '#FAFAFA',
        borderRadius: message.sender === 'system' ? '5px' : '4px',
        fontSize: message.sender === 'system' ? '0.5rem' : '1rem',
        color: message.sender === 'system' ? '#999' : 'inherit',
        maxWidth: message.sender === 'user' ? '60%' : '100%',
        marginLeft: message.sender === 'user' ? 'auto' : '0',
        marginRight: message.sender === 'llm' ? 'auto' : '0',
      }}
    >
      <Typography style={{ fontSize: '8px' }} variant="body2" color={message.sender === 'user' ? 'primary' : message.sender === 'llm' ? 'secondary' : 'textSecondary'}>
        {message.sender === 'user' ? 'You' : message.sender === 'llm' ? 'AI' : 'System'}
      </Typography>
      <MarkdownRenderer content={message.text} />
    </Paper>
  );

  return (
    <Box p={2} height="100%" display="flex" flexDirection="column" justifyContent="flex-end">
      <div ref={listRef} style={{ overflowY: 'auto', maxHeight: '100%' }}>
        {messages.map((message, index) => renderRow(message, index))}
      </div>
    </Box>
  );
};

export default Chat;