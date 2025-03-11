/**
 * Agent Assembly Line
 * License Apache-2.0
 * See the LICENSE file in the root directory for details.
 */

import React, { useRef } from 'react';
import { IconButton } from '@mui/material';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import { uploadFile, Message } from '../services/ApiService';

interface FileUploadButtonProps {
  onSystemMessage: (message: Message) => void;
}

const FileUploadButton: React.FC<FileUploadButtonProps> = ({ onSystemMessage }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleButtonClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      console.log('Selected file:', file.name);
      try {
        const systemMessage = await uploadFile(file);
        console.log('File uploaded successfully:', systemMessage);
        onSystemMessage(systemMessage);
      } catch (error) {
        console.error('Error uploading file:', error);
      }
    }
  };

  return (
    <>
      <input
        type="file"
        ref={fileInputRef}
        style={{ display: 'none' }}
        accept=".pdf,.md,.txt,.json"
        onChange={handleFileChange}
      />
      <IconButton
        onClick={handleButtonClick}
        color="primary"
        aria-label="upload file"
        component="span"
        sx={{
          backgroundColor: '#ffffff',
          '&:hover': {
            backgroundColor: '#f0f0f0',
          },
          '&:active': {
            backgroundColor: '#e0e0e0',
          },
          borderRadius: '50%',
          width: 40,
          height: 40,
        }}
      >
        <AttachFileIcon sx={{ color: '#4a4a4a' }} />
      </IconButton>
    </>
  );
};

export default FileUploadButton;