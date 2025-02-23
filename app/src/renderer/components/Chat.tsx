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
  sender: 'user' | 'llm';
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
        <Typography variant="body2" color={message.sender === 'user' ? 'primary' : 'secondary'}>
          {message.sender === 'user' ? 'You' : 'AI'}
        </Typography>
        <MarkdownRenderer content={message.text} />
      </Box>
    );
  };

  return (
    <Box p={2} height="100%" display="flex" flexDirection="column" justifyContent="flex-end">
        {messages.map((message, index) => (
            <Paper key={index} style={{
                padding: '10px', marginBottom: '10px',
                alignSelf: message.sender === 'user' ? 'flex-end' : 'flex-start',
                backgroundColor: message.sender === 'user' ? 'white' : '#FAFAFA'
            }}
            >
            <MarkdownRenderer content={message.text} />
        </Paper>
        ))}
    </Box>);
};

export default Chat;