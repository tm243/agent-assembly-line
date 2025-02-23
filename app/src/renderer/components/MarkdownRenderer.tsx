import React from 'react';
import Markdown from 'markdown-to-jsx';
import { Box } from '@mui/material';
import './MarkdownRenderer.css';

interface MarkdownRendererProps {
  content: string;
}

const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  return (
    <Box className="markdown-content">
      <Markdown>{content}</Markdown>
    </Box>
  );
};

export default MarkdownRenderer;