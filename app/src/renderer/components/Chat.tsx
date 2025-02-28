/**
 * Agent Assembly Line
 * License Apache-2.0
 * See the LICENSE file in the root directory for details.
 */

import React, { useEffect, useRef } from 'react';
import { FixedSizeList as List } from 'react-window';
import MarkdownRenderer from './MarkdownRenderer';
import { Box, Typography, Paper } from '@mui/material';

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
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [messages]);

  const renderRow = ({ index, style }: { index: number; style: React.CSSProperties }) => {
    const message = messages[index];
    return (
      <Box style={style} key={index} p={1} borderBottom="1px solid #ccc">
        <Typography variant="body2" color={message.sender === 'user' ? 'primary' : message.sender === 'llm' ? 'secondary' : 'textSecondary'}>
          {message.sender === 'user' ? 'You' : message.sender === 'llm' ? 'AI' : 'System'}
        </Typography>
        <MarkdownRenderer content={message.text} />
      </Box>
    );
  };

  return (
    <Box p={2} height="100%" display="flex" flexDirection="column" justifyContent="flex-end">
      {messages.map((message, index) => (
        <Paper
          key={index}
          style={{
            padding: message.sender === 'system' ? '2px' : '10px',
            marginBottom: '10px',
            alignSelf: message.sender === 'user' ? 'flex-end' : 'flex-start',
            backgroundColor: message.sender === 'user' ? 'white' : message.sender === 'llm' ? '#FAFAFA' : '#EFEFEF',
            borderRadius: message.sender === 'system' ? '5px' : '4px',
            fontSize: message.sender === 'system' ? '0.5rem' : '1rem',
            color: message.sender === 'system' ? '#999' : 'inherit',
            boxShadow: message.sender === 'system' ? 'none' : undefined,
          }}
        >
          <MarkdownRenderer content={message.text} />
        </Paper>
      ))}
    </Box>
  );
};

export default Chat;