/**
 * Agent Assembly Line
 * License Apache-2.0
 * See the LICENSE file in the root directory for details.
 */

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
      <Markdown options={{ forceBlock: true, wrapper: 'article' }}>{content}</Markdown>
    </Box>
  );
};

export default MarkdownRenderer;