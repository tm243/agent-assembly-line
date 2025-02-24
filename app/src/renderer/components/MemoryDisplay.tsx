import React, { useState, useEffect } from 'react';
import { Box, TextareaAutosize } from '@mui/material';
import { fetchMemory } from '../services/ApiService';
import "./MemoryDisplay.css";

const MemoryDisplay: React.FC = () => {
  const [memory, setMemory] = useState<string>('');

  useEffect(() => {
    const loadMemory = async () => {
      try {
        const fetchedMemory = await fetchMemory();
        setMemory(fetchedMemory);
      } catch (error) {
        console.error('Failed to fetch memory:', error);
      }
    };

    loadMemory();
    const intervalId = setInterval(loadMemory, 5000);

    return () => clearInterval(intervalId);
  }, []);

  return (
    <Box
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',

        backgroundColor: '#333',
        color: '#ccc',
        padding: 0,
        overflowY: 'auto',
      }}
    >
      {/* <TextareaAutosize
        className='memory-display'
        value={memory}
        readOnly
        style={{
          width: '100%',
          height: '88%'
        }}
      /> */}
            <textarea
        className="memory-display"
        value={memory}
        readOnly
      />
    </Box>
  );
};

export default MemoryDisplay;