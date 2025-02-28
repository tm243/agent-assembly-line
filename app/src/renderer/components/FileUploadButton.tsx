import React, { useRef } from 'react';
import { IconButton } from '@mui/material';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import { uploadFile } from '../services/ApiService';

const FileUploadButton: React.FC = () => {
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
        const response = await uploadFile(file);
        console.log('File uploaded successfully:', response);
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