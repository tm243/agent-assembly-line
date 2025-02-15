/**
 * Agent Assembly Line
 * License Apache-2.0
 * See the LICENSE file in the root directory for details.
 */

import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { Message } from '../services/ApiService';

interface ChatProps {
  messages: Message[];
}
  
const Chat: React.FC<ChatProps> = ({ messages }) => {
  return (
    <Box p={2} height="100%" display="flex" flexDirection="column" justifyContent="flex-end">
        {messages.map((message, index) => (
        <Paper key={index} style={{ padding: '10px', marginBottom: '10px', alignSelf: message.sender === 'user' ? 'flex-end' : 'flex-start' }}>
            <Typography variant="body1">{message.text}</Typography>
        </Paper>
        ))}
    </Box>
  );
};

export default Chat;