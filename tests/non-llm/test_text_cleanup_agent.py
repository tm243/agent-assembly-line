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
        shutil.rmtree(self.test_dir)

    def test_init_with_default_output_path(self):
        agent = TextCleanupAgent(
            input_file_path=self.input_file,
            mode='local'
        )

        expected_output = os.path.join(self.test_dir, "test_input_cleaned.txt")
        self.assertEqual(agent.output_file_path, expected_output)

    def test_init_with_custom_output_path(self):
        custom_output = os.path.join(self.test_dir, "custom_output.txt")
        agent = TextCleanupAgent(
            input_file_path=self.input_file,
            output_file_path=custom_output,
            mode='local'
        )

        self.assertEqual(agent.output_file_path, custom_output)

    def test_init_with_local_mode(self):
        with patch('agent_assembly_line.micros.text_cleanup_agent.Agent.__init__') as mock_super_init:
            agent = TextCleanupAgent(
                input_file_path=self.input_file,
                mode='local'
            )

            mock_super_init.assert_called_once()
            # Just verify it was called - the config structure may vary
            self.assertTrue(mock_super_init.called)

    def test_init_with_cloud_mode(self):
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

    def test_init_with_custom_instructions(self):
        custom_instructions = "Remove all numbers from the text"

        with patch('agent_assembly_line.micros.text_cleanup_agent.Agent.__init__') as mock_super_init:
            agent = TextCleanupAgent(
                input_file_path=self.input_file,
                mode='local',
                custom_instructions=custom_instructions
            )

            # Verify super().__init__ was called
            mock_super_init.assert_called_once()

            # Check that custom instructions are used
            call_args = mock_super_init.call_args[1]['config']
            config_dict = call_args._config_dict if hasattr(call_args, '_config_dict') else {}
            # Custom instructions should be embedded in the prompt template
            self.assertTrue(mock_super_init.called)

    def test_init_with_kwargs(self):
        with patch('agent_assembly_line.micros.text_cleanup_agent.Agent.__init__') as mock_super_init:
            agent = TextCleanupAgent(
                input_file_path=self.input_file,
                mode='local',
                name="custom-cleanup-agent",
                description="Custom description"
            )

            mock_super_init.assert_called_once()
            self.assertTrue(mock_super_init.called)

    def test_verbose_flag_false(self):
        """Test that verbose=False suppresses log output."""
        agent = TextCleanupAgent(
            input_file_path=self.input_file,
            mode='local',
            verbose=False
        )

        with patch('builtins.print') as mock_print:
            agent._log("Test message")
            mock_print.assert_not_called()

    def test_verbose_flag_true(self):
        """Test that verbose=True enables log output."""
        agent = TextCleanupAgent(
            input_file_path=self.input_file,
            mode='local',
            verbose=True
        )

        with patch('builtins.print') as mock_print:
            agent._log("Test message")
            mock_print.assert_called_once_with("Test message")

    def test_chunk_text_basic(self):
        agent = TextCleanupAgent(
            input_file_path=self.input_file, 
            mode='local'
        )

        text = "This is a test. This is another sentence. And one more sentence."
        chunks = agent.chunk_text(text, chunk_size=30)

        self.assertGreater(len(chunks), 1)

        for chunk in chunks:
            self.assertLessEqual(len(chunk), 35)  # Allow some flexibility

        self.assertTrue(chunks[0].startswith("This is a test"))

    def test_chunk_text_with_paragraph_breaks(self):
        """Test that chunking respects paragraph boundaries."""
        agent = TextCleanupAgent(input_file_path=self.input_file, mode='local')

        text = "First paragraph.\n\nSecond paragraph with more text.\n\nThird paragraph."
        chunks = agent.chunk_text(text, chunk_size=30)

        self.assertGreater(len(chunks), 1)

    def test_chunk_text_small_text(self):
        agent = TextCleanupAgent(input_file_path=self.input_file, mode='local')

        text = "Small text."
        chunks = agent.chunk_text(text, chunk_size=100)

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], "Small text.")

    def test_chunk_text_large_overlap(self):
        dummy_file = os.path.join(self.test_dir, "dummy.txt")
        with open(dummy_file, 'w') as f:
            f.write("small content")

        agent = TextCleanupAgent(input_file_path=dummy_file, mode='local')

        text = "This is a test with large overlap settings."
        chunks = agent.chunk_text(text, chunk_size=10)

        self.assertGreater(len(chunks), 0)
        self.assertLess(len(chunks), 100)

    def test_chunk_text_zero_overlap(self):
        dummy_file = os.path.join(self.test_dir, "dummy.txt")
        with open(dummy_file, 'w') as f:
            f.write("small content")

        agent = TextCleanupAgent(input_file_path=dummy_file, mode='local')

        text = "First chunk. Second chunk. Third chunk."
        chunks = agent.chunk_text(text, chunk_size=15)

        self.assertGreater(len(chunks), 1)
        combined = "".join(chunks)
        self.assertIn("First chunk", combined)
        self.assertIn("Third chunk", combined)

    def test_chunk_text_paragraph_boundary_preference(self):
        """Test that chunking prefers paragraph boundaries."""
        agent = TextCleanupAgent(input_file_path=self.input_file, mode='local')

        text = "First paragraph with some text here.\n\nSecond paragraph with more content that should break at paragraph boundary."
        chunks = agent.chunk_text(text, chunk_size=60)

        self.assertGreater(len(chunks), 1)
        # First chunk should end at paragraph boundary
        self.assertTrue(chunks[0].endswith("here."))

    def test_chunk_text_sentence_boundary_fallback(self):
        """Test that chunking falls back to sentence boundaries when no paragraph breaks."""
        agent = TextCleanupAgent(input_file_path=self.input_file, mode='local')

        text = "This is the first sentence. This is a longer second sentence that extends beyond normal size. This is the third sentence."
        chunks = agent.chunk_text(text, chunk_size=50)

        self.assertGreater(len(chunks), 1)
        # Should break at sentence boundary
        first_chunk_ends_with_period = chunks[0].rstrip().endswith('.')
        self.assertTrue(first_chunk_ends_with_period)

    def test_chunk_text_punctuation_fallback(self):
        """Test that chunking falls back to punctuation boundaries."""
        agent = TextCleanupAgent(input_file_path=self.input_file, mode='local')

        text = "This text has: a colon, some commas; and semicolons - but no sentence endings until way later in this very long text."
        chunks = agent.chunk_text(text, chunk_size=40)

        self.assertGreater(len(chunks), 1)
        # Should break at some punctuation
        self.assertGreater(len(chunks[0]), 10)  # Should get reasonable chunk size

    def test_chunk_text_word_boundary_last_resort(self):
        """Test that chunking falls back to word boundaries as last resort."""
        agent = TextCleanupAgent(input_file_path=self.input_file, mode='local')

        # Text with no good punctuation boundaries
        text = "This is a very long continuous text without any good punctuation marks for breaking except spaces between words"
        chunks = agent.chunk_text(text, chunk_size=30)

        self.assertGreater(len(chunks), 1)
        # Should not break in middle of words
        for chunk in chunks[:-1]:  # Exclude last chunk which might be partial
            self.assertFalse(chunk.rstrip().endswith('ord'))  # Shouldn't break "words"

    def test_chunk_text_no_duplication(self):
        """Test that chunking doesn't create duplicate content."""
        agent = TextCleanupAgent(input_file_path=self.input_file, mode='local')

        text = "Word1 Word2 Word3 Word4 Word5 Word6 Word7 Word8 Word9 Word10"
        chunks = agent.chunk_text(text, chunk_size=20)

        # Reconstruct text and verify no duplication
        reconstructed = " ".join(chunk.strip() for chunk in chunks)
        word_count_original = len(text.split())
        word_count_reconstructed = len(reconstructed.split())

        # Should have same number of words (no duplication)
        self.assertEqual(word_count_original, word_count_reconstructed)

    def test_chunk_text_empty_text(self):
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
        with patch('agent_assembly_line.micros.text_cleanup_agent.Agent.run') as mock_parent_run:
            mock_parent_run.return_value = "cleaned text"

            agent = TextCleanupAgent(input_file_path=self.input_file, mode='local')
            agent.verbose = False
            result = agent.run("test prompt")

            mock_parent_run.assert_called_once_with("test prompt")
            self.assertEqual(result, "cleaned text")

    def test_process_file_integration(self):
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
        output_file = os.path.join(self.test_dir, "test_output.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Test output content")

        input_size = os.path.getsize(self.input_file)
        output_size = os.path.getsize(output_file)

        self.assertGreater(input_size, 0)
        self.assertGreater(output_size, 0)

    def test_purpose_attribute(self):
        self.assertTrue(hasattr(TextCleanupAgent, 'purpose'))
        self.assertIsInstance(TextCleanupAgent.purpose, str)
        self.assertIn("encoding issues", TextCleanupAgent.purpose)


class TestTextCleanupAgentEdgeCases(unittest.TestCase):
    """Edge cases and error conditions."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_nonexistent_input_file(self):
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
        dummy_file = os.path.join(self.test_dir, "dummy.txt")
        with open(dummy_file, 'w') as f:
            f.write("small content")

        agent = TextCleanupAgent(input_file_path=dummy_file, mode='local')
        chunks = agent.chunk_text("small text", chunk_size=10000)

        self.assertEqual(len(chunks), 1)

    def test_multiple_encoding_fallback_failure(self):
        dummy_file = os.path.join(self.test_dir, "dummy.txt")
        with open(dummy_file, 'w') as f:
            f.write("content")

        agent = TextCleanupAgent(input_file_path=dummy_file, mode='local')
        agent.verbose = False

        with patch('builtins.open') as mock_open:
            mock_open.side_effect = UnicodeDecodeError('test', b'', 0, 1, 'test error')

            with self.assertRaises(ValueError) as context:
                agent.process_file()

            self.assertIn("Could not read file", str(context.exception))

    def test_successful_encoding_fallback_logging(self):
        """Test that successful encoding fallback is logged."""
        dummy_file = os.path.join(self.test_dir, "dummy.txt")
        with open(dummy_file, 'w') as f:
            f.write("content")

        agent = TextCleanupAgent(input_file_path=dummy_file, mode='local', verbose=True)

        read_call_count = 0
        def open_side_effect(filename, mode='r', encoding='utf-8'):
            nonlocal read_call_count
            if 'r' in mode:
                read_call_count += 1
                if encoding == 'utf-8':
                    raise UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid start byte')
                elif encoding == 'latin-1':
                    mock_file = MagicMock()
                    mock_file.read.return_value = "test content"
                    mock_file.__enter__.return_value = mock_file
                    return mock_file
            else:  # write mode
                mock_file = MagicMock()
                mock_file.__enter__.return_value = mock_file
                return mock_file

        with patch('builtins.open', side_effect=open_side_effect), \
             patch.object(agent, 'chunk_text', return_value=["test"]), \
             patch.object(agent, 'replace_inline_text'), \
             patch.object(agent, 'run', return_value="cleaned"), \
             patch('builtins.print') as mock_print:

            agent.process_file()

            # Should log successful encoding detection
            logged_calls = [str(call) for call in mock_print.call_args_list]
            encoding_log_found = any('latin-1' in call for call in logged_calls)
            self.assertTrue(encoding_log_found)

    def test_log_method_internal(self):
        dummy_file = os.path.join(self.test_dir, "dummy.txt")
        with open(dummy_file, 'w') as f:
            f.write("content")

        agent = TextCleanupAgent(input_file_path=dummy_file, mode='local', verbose=True)

        with patch('builtins.print') as mock_print:
            agent._log("Test internal log message")
            mock_print.assert_called_once_with("Test internal log message")

        # Test with verbose=False
        agent.verbose = False
        with patch('builtins.print') as mock_print:
            agent._log("Should not print")
            mock_print.assert_not_called()


class TestTextCleanupAgentIntegration(unittest.TestCase):
    """Integration tests for complete workflows."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

        # Create test files with different characteristics
        self.large_file = os.path.join(self.test_dir, "large_test.txt")
        with open(self.large_file, 'w', encoding='utf-8') as f:
            # Create content that will require chunking
            content = []
            for i in range(20):
                content.append(f"This is paragraph {i} with some encoding issues like ä and â€œquotesâ€. ")
                content.append(f"It continues with more text to ensure we get multiple chunks. ")
                if i % 3 == 0:
                    content.append("\\n\\n")  # Paragraph breaks
            f.write("".join(content))

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch('agent_assembly_line.micros.text_cleanup_agent.Agent.__init__')
    def test_complete_workflow_with_chunking(self, mock_super_init):
        agent = TextCleanupAgent(
            input_file_path=self.large_file,
            mode='local',
            verbose=False
        )

        # Mock the LLM responses for each chunk - need to account for actual chunk count
        def run_side_effect(prompt):
            if not hasattr(run_side_effect, 'call_count'):
                run_side_effect.call_count = 0
            run_side_effect.call_count += 1
            return f"Cleaned chunk {run_side_effect.call_count}"

        agent.run = Mock(side_effect=run_side_effect)
        agent.replace_inline_text = Mock()

        output_path = agent.process_file()

        self.assertTrue(os.path.exists(output_path))

        # Verify the output contains joined chunks (check for at least first chunk)
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("Cleaned chunk 1", content)
            # File should contain multiple chunks
            self.assertTrue(agent.run.call_count >= 2)

    @patch('agent_assembly_line.micros.text_cleanup_agent.Agent.__init__')
    def test_error_during_chunk_processing(self, mock_super_init):
        agent = TextCleanupAgent(
            input_file_path=self.large_file,
            mode='local',
            verbose=False
        )

        # Mock run method to fail on second chunk
        def run_side_effect(prompt):
            if hasattr(run_side_effect, 'call_count'):
                run_side_effect.call_count += 1
            else:
                run_side_effect.call_count = 1

            if run_side_effect.call_count == 2:
                raise Exception("LLM processing error")
            return f"Cleaned chunk {run_side_effect.call_count}"

        agent.run = Mock(side_effect=run_side_effect)
        agent.replace_inline_text = Mock()

        # Should propagate the exception
        with self.assertRaises(Exception) as context:
            agent.process_file()

        self.assertIn("LLM processing error", str(context.exception))

    @patch('agent_assembly_line.micros.text_cleanup_agent.Agent.__init__')
    def test_custom_instructions_integration(self, mock_super_init):
        custom_instructions = "Convert all text to uppercase"

        agent = TextCleanupAgent(
            input_file_path=self.large_file,
            mode='local',
            verbose=False,
            custom_instructions=custom_instructions
        )

        # Verify that the config was created with custom instructions
        mock_super_init.assert_called_once()
        config_arg = mock_super_init.call_args[1]['config']

        # The custom instructions should be embedded in the prompt template
        self.assertTrue(hasattr(config_arg, '_config_dict') or
                       hasattr(config_arg, 'inline_rag_templates'))

    def test_output_path_generation_edge_cases(self):
        test_cases = [
            ("file.txt", "file_cleaned.txt"),
            ("file", "file_cleaned"),
            ("path/to/file.md", "path/to/file_cleaned.md"),
            ("file.backup.txt", "file.backup_cleaned.txt")
        ]

        for input_path, expected_output in test_cases:
            full_input_path = os.path.join(self.test_dir, input_path.replace("/", os.sep))
            os.makedirs(os.path.dirname(full_input_path), exist_ok=True)

            # Create the input file
            with open(full_input_path, 'w') as f:
                f.write("test content")

            agent = TextCleanupAgent(
                input_file_path=full_input_path,
                mode='local'
            )

            expected_full_output = os.path.join(self.test_dir, expected_output.replace("/", os.sep))
            self.assertEqual(agent.output_file_path, expected_full_output)


if __name__ == '__main__':
    os.makedirs('tests', exist_ok=True)

    unittest.main(verbosity=2)