/**
 * Agent Assembly Line
 * License Apache-2.0
 * See the LICENSE file in the root directory for details.
 */

import React from 'react';
import { Box } from '@mui/material';
import { keyframes } from '@emotion/react';

const pulse = keyframes`
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.5);
    opacity: 0.5;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
`;

const PulsingDot = () => {
  return (
    <Box
      sx={{
        width: 10,
        height: 10,
        borderRadius: '50%',
        backgroundColor: 'darkgray',
        animation: `${pulse} 1s infinite ease-in-out`,
        display: 'inline-block',
      }}
    />
  );
};

export default PulsingDot;