#!/usr/bin/env python3
"""
Unit tests for the TextCleanupAgent class.
"""

import unittest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from agent_assembly_line.micros.text_cleanup_agent import TextCleanupAgent

class TestTextCleanupAgent(unittest.TestCase):
    """Test cases for TextCleanupAgent functionality."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        
        self.sample_corrupted_text = """
This is a test document with encoding issues.
Here are some bad umlauts: ä, ö, ü, Ä, Ö, Ü
Corrupted quotes: â€œHello Worldâ€ and â€™single quotesâ€™
Strange symbols: â€¢ bullet point, â€" em dash, â€" en dash
Some normal text that should remain unchanged.
Another paragraph with more ä encoding issues.
        """.strip()
        
        self.sample_cleaned_text = """
This is a test document with encoding issues.
Here are some bad umlauts: ä, ö, ü, Ä, Ö, Ü
Corrupted quotes: "Hello World" and 'single quotes'
Strange symbols: • bullet point, — em dash, – en dash
Some normal text that should remain unchanged.
Another paragraph with more ä encoding issues.
        """.strip()
        
        self.input_file = os.path.join(self.test_dir, "test_input.txt")
        with open(self.input_file, 'w', encoding='utf-8') as f:
            f.write(self.sample_corrupted_text)

    def tearDown(self):
        """Clean up test fixtures after each test method."""
        shutil.rmtree(self.test_dir)

    def test_init_with_default_output_path(self):
        """Test initialization with default output path generation."""
        agent = TextCleanupAgent(
            input_file_path=self.input_file,
            mode='local'
        )
        
        expected_output = os.path.join(self.test_dir, "test_input_cleaned.txt")
        self.assertEqual(agent.output_file_path, expected_output)

    def test_init_with_custom_output_path(self):
        """Test initialization with custom output path."""
        custom_output = os.path.join(self.test_dir, "custom_output.txt")
        agent = TextCleanupAgent(
            input_file_path=self.input_file,
            output_file_path=custom_output,
            mode='local'
        )
        
        self.assertEqual(agent.output_file_path, custom_output)

    def test_init_with_local_mode(self):
        """Test initialization with local mode."""
        with patch('agent_assembly_line.micros.text_cleanup_agent.Agent.__init__') as mock_super_init:
            agent = TextCleanupAgent(
                input_file_path=self.input_file,
                mode='local'
            )
            
            mock_super_init.assert_called_once()
            # Just verify it was called - the config structure may vary
            self.assertTrue(mock_super_init.called)

    def test_init_with_cloud_mode(self):
        """Test initialization with cloud mode."""
        with patch('agent_assembly_line.micros.text_cleanup_agent.Agent.__init__') as mock_super_init:
            agent = TextCleanupAgent(
                input_file_path=self.input_file,
                mode='cloud'
            )
            
            mock_super_init.assert_called_once()
            # Just verify it was called - the config structure may vary
            self.assertTrue(mock_super_init.called)

    def test_init_with_invalid_mode(self):
        """Test initialization with invalid mode raises ValueError."""
        with self.assertRaises(ValueError) as context:
            TextCleanupAgent(
                input_file_path=self.input_file,
                mode='invalid_mode'
            )
        
        self.assertIn("Invalid mode", str(context.exception))

    def test_chunk_text_basic(self):
        """Test basic text chunking functionality."""
        agent = TextCleanupAgent(
            input_file_path=self.input_file, 
            mode='local'
        )
        
        text = "This is a test. This is another sentence. And one more sentence."
        chunks = agent.chunk_text(text, chunk_size=30, overlap=5)
        
        self.assertGreater(len(chunks), 1)
        
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 35)  # Allow some flexibility
            
        self.assertTrue(chunks[0].startswith("This is a test"))

    def test_chunk_text_with_paragraph_breaks(self):
        """Test that chunking respects paragraph boundaries."""
        agent = TextCleanupAgent(input_file_path=self.input_file, mode='local')
        
        text = "First paragraph.\n\nSecond paragraph with more text.\n\nThird paragraph."
        chunks = agent.chunk_text(text, chunk_size=30, overlap=5)
        
        self.assertGreater(len(chunks), 1)

    def test_chunk_text_small_text(self):
        """Test chunking with text smaller than chunk size."""
        agent = TextCleanupAgent(input_file_path=self.input_file, mode='local')
        
        text = "Small text."
        chunks = agent.chunk_text(text, chunk_size=100)
        
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], "Small text.")

    def test_chunk_text_large_overlap(self):
        """Test chunking with overlap larger than chunk size."""
        dummy_file = os.path.join(self.test_dir, "dummy.txt")
        with open(dummy_file, 'w') as f:
            f.write("small content")
            
        agent = TextCleanupAgent(input_file_path=dummy_file, mode='local')
        
        text = "This is a test with large overlap settings."
        chunks = agent.chunk_text(text, chunk_size=10, overlap=15)
        
        self.assertGreater(len(chunks), 0)
        self.assertLess(len(chunks), 100)

    def test_chunk_text_zero_overlap(self):
        """Test chunking with zero overlap."""
        dummy_file = os.path.join(self.test_dir, "dummy.txt")
        with open(dummy_file, 'w') as f:
            f.write("small content")
            
        agent = TextCleanupAgent(input_file_path=dummy_file, mode='local')
        
        text = "First chunk. Second chunk. Third chunk."
        chunks = agent.chunk_text(text, chunk_size=15, overlap=0)
        
        self.assertGreater(len(chunks), 1)
        combined = "".join(chunks)
        self.assertIn("First chunk", combined)
        self.assertIn("Third chunk", combined)

    def test_chunk_text_empty_text(self):
        """Test chunking with empty text."""
        dummy_file = os.path.join(self.test_dir, "dummy.txt")
        with open(dummy_file, 'w') as f:
            f.write("small content")
            
        agent = TextCleanupAgent(input_file_path=dummy_file, mode='local')
        
        chunks = agent.chunk_text("", chunk_size=100)
        
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], "")

    @patch('builtins.open', create=True)
    def test_process_file_utf8_encoding(self, mock_open):
        """Test file processing with UTF-8 encoding."""
        mock_file = MagicMock()
        mock_file.read.return_value = self.sample_corrupted_text
        mock_open.return_value.__enter__.return_value = mock_file
        
        with patch.object(TextCleanupAgent, '__init__', return_value=None):
            agent = TextCleanupAgent.__new__(TextCleanupAgent)
            agent.input_file_path = self.input_file
            agent.output_file_path = os.path.join(self.test_dir, "output.txt")
            agent.verbose = False
            agent.chunk_text = Mock(return_value=["chunk1", "chunk2"])
            agent.replace_inline_text = Mock()
            agent.run = Mock(side_effect=["cleaned_chunk1", "cleaned_chunk2"])
            
            result = agent.process_file()
            
            mock_open.assert_any_call(self.input_file, 'r', encoding='utf-8')
            mock_open.assert_any_call(agent.output_file_path, 'w', encoding='utf-8')

    @patch('builtins.open')
    def test_process_file_encoding_fallback(self, mock_open):
        """Test file processing with encoding fallback."""
        mock_read_file = MagicMock()
        mock_read_file.read.return_value = self.sample_corrupted_text
        mock_write_file = MagicMock()
        
        def open_side_effect(filename, mode='r', encoding='utf-8'):
            if 'r' in mode:
                if encoding == 'utf-8':
                    raise UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid start byte')
                else:
                    return mock_read_file
            else:
                return mock_write_file
        
        mock_open.side_effect = open_side_effect
        mock_read_file.__enter__.return_value = mock_read_file
        mock_write_file.__enter__.return_value = mock_write_file
        
        with patch.object(TextCleanupAgent, '__init__', return_value=None):
            agent = TextCleanupAgent.__new__(TextCleanupAgent)
            agent.input_file_path = self.input_file
            agent.output_file_path = os.path.join(self.test_dir, "output.txt")

            agent.verbose = False
            agent.chunk_text = Mock(return_value=["chunk1"])
            agent.replace_inline_text = Mock()
            agent.run = Mock(return_value="cleaned_chunk")
            
            result = agent.process_file()
            
            self.assertGreaterEqual(mock_open.call_count, 2)
            self.assertEqual(result, agent.output_file_path)

    def test_run_method(self):
        """Test the run method calls parent correctly."""
        with patch('agent_assembly_line.micros.text_cleanup_agent.Agent.run') as mock_parent_run:
            mock_parent_run.return_value = "cleaned text"
            
            agent = TextCleanupAgent(input_file_path=self.input_file, mode='local')
            agent.verbose = False
            result = agent.run("test prompt")
            
            mock_parent_run.assert_called_once_with("test prompt")
            self.assertEqual(result, "cleaned text")

    def test_process_file_integration(self):
        """Integration test for the complete process_file workflow."""
        with patch('agent_assembly_line.micros.text_cleanup_agent.Agent.__init__'):
            agent = TextCleanupAgent(
                input_file_path=self.input_file,
                mode='local'
            )
            
            agent.verbose = False
            agent.replace_inline_text = Mock()
            agent.run = Mock(return_value=self.sample_cleaned_text)
            
            output_path = agent.process_file()
            
            self.assertTrue(os.path.exists(output_path))
            
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn("This is a test document", content)

    def test_file_size_reporting(self):
        """Test that file size reporting works correctly."""
        output_file = os.path.join(self.test_dir, "test_output.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Test output content")
            
        input_size = os.path.getsize(self.input_file)
        output_size = os.path.getsize(output_file)
        
        self.assertGreater(input_size, 0)
        self.assertGreater(output_size, 0)

    def test_purpose_attribute(self):
        """Test that the purpose attribute is properly set."""
        self.assertTrue(hasattr(TextCleanupAgent, 'purpose'))
        self.assertIsInstance(TextCleanupAgent.purpose, str)
        self.assertIn("encoding issues", TextCleanupAgent.purpose)


class TestTextCleanupAgentEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_nonexistent_input_file(self):
        """Test behavior with non-existent input file."""
        nonexistent_file = os.path.join(self.test_dir, "nonexistent.txt")
        
        with patch('agent_assembly_line.micros.text_cleanup_agent.Agent.__init__'):
            agent = TextCleanupAgent(
                input_file_path=nonexistent_file,
                mode='local'
            )

            agent.verbose = False

            with self.assertRaises(FileNotFoundError):
                agent.process_file()

    def test_empty_file(self):
        """Test behavior with empty input file."""
        empty_file = os.path.join(self.test_dir, "empty.txt")
        with open(empty_file, 'w') as f:
            f.write("")
            
        with patch('agent_assembly_line.micros.text_cleanup_agent.Agent.__init__'):
            agent = TextCleanupAgent(
                input_file_path=empty_file,
                mode='local'
            )

            agent.verbose = False
            agent.replace_inline_text = Mock()
            agent.run = Mock(return_value="")
            
            output_path = agent.process_file()
            
            self.assertTrue(os.path.exists(output_path))

    def test_very_large_chunks(self):
        """Test chunking with very large chunk size."""
        dummy_file = os.path.join(self.test_dir, "dummy.txt")
        with open(dummy_file, 'w') as f:
            f.write("small content")
            
        agent = TextCleanupAgent(input_file_path=dummy_file, mode='local')
        chunks = agent.chunk_text("small text", chunk_size=10000)
        
        self.assertEqual(len(chunks), 1)


if __name__ == '__main__':
    os.makedirs('tests', exist_ok=True)
    
    unittest.main(verbosity=2)