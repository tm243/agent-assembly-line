"""
Non-LLM tests for Proof Refutation Machine logic
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from flows.proof_refutation_machine import ProofRefutationMachine, EvaluationResult, load_hypothesis_from_file


class TestProofRefutationMachineLogic(unittest.TestCase):
    """Test non-LLM logic components of the proof refutation machine"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        """Clean up test environment"""
        self.temp_dir.cleanup()

    def test_evaluation_result_creation(self):
        """Test EvaluationResult dataclass creation"""
        result = EvaluationResult(
            hypothesis="Test hypothesis",
            formalized_statement="Formalized test",
            derived_consequences="Test consequences",
            falsification_attempts="Test falsification",
            evidence_assessment="Test evidence",
            final_verdict="Test verdict",
            confidence_level="High",
            processing_time=1.5,
            timestamp=1234567890.0
        )

        self.assertEqual(result.hypothesis, "Test hypothesis")
        self.assertEqual(result.confidence_level, "High")
        self.assertEqual(result.processing_time, 1.5)
        self.assertIsInstance(result.timestamp, float)

    def test_confidence_level_extraction_patterns(self):
        """Test various patterns for confidence level extraction"""
        with patch('agent_assembly_line.llm_factory.LLMFactory.create_llm_and_embeddings') as mock_create:
            mock_create.return_value = (MagicMock(), MagicMock())
            machine = ProofRefutationMachine(mode='local', debug=False)

        test_cases = [
            ("Confidence level: 85%", "85%"),
            ("3. Confidence level: High", "High"),
            ("Confidence: Medium uncertainty", "Medium uncertainty"),
            ("CONFIDENCE LEVEL: 90%", "90%"),
            ("confidence: low", "low"),
            ("1. Verdict: True\n2. Justification: Strong\n3. Confidence level: Very High\n4. Conditions: None", "Very High"),
            ("Confidence level:\nHigh (95% certain)", "High (95% certain)"),
            ("No confidence mentioned here", "Not specified"),
            ("", "Not specified"),
            ("Confident but no level specified", "Not specified"),
            ("Confidence level:", "Not specified"),
        ]

        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = machine._extract_confidence_level(input_text)
                self.assertEqual(result, expected, f"Failed for input: {input_text}")

    def test_mode_validation(self):
        """Test that mode validation works correctly"""
        with patch('agent_assembly_line.llm_factory.LLMFactory.create_llm_and_embeddings') as mock_create:
            mock_create.return_value = (MagicMock(), MagicMock())

            try:
                machine_local = ProofRefutationMachine(mode='local')
                self.assertEqual(machine_local.mode, 'local')

                machine_cloud = ProofRefutationMachine(mode='cloud')
                self.assertEqual(machine_cloud.mode, 'cloud')
            except Exception as e:
                self.fail(f"Valid modes should not raise exceptions: {e}")

        with self.assertRaises(ValueError) as context:
            ProofRefutationMachine(mode='invalid')
        self.assertIn("Invalid mode 'invalid'", str(context.exception))
        self.assertIn("Choose either 'local' or 'cloud'", str(context.exception))

    def test_prompt_formatting_content(self):
        """Test that prompt formatting includes expected content"""
        with patch('agent_assembly_line.llm_factory.LLMFactory.create_llm_and_embeddings') as mock_create:
            mock_create.return_value = (MagicMock(), MagicMock())
            machine = ProofRefutationMachine(mode='local', debug=False)

        hypothesis = "Test scientific hypothesis"
        formalized = "Formalized: Test hypothesis with clear parameters"
        consequences = "Derived consequences: 1. Prediction A, 2. Prediction B"
        evidence = "Supporting evidence: Experiment X shows Y"
        falsification = "Falsification attempts: Counter-example Z"

        # Test interpreter prompt
        interpreter_prompt = machine._format_interpreter_prompt(hypothesis)
        self.assertIn("Interpreter Agent", interpreter_prompt)
        self.assertIn(hypothesis, interpreter_prompt)
        self.assertIn("formalize", interpreter_prompt.lower())

        # Test theorist prompt
        theorist_prompt = machine._format_theorist_prompt(formalized)
        self.assertIn("Theorist Agent", theorist_prompt)
        self.assertIn(formalized, theorist_prompt)
        self.assertIn("consequences", theorist_prompt.lower())
        self.assertIn("predictions", theorist_prompt.lower())

        # Test adversary prompt
        adversary_prompt = machine._format_adversary_prompt(formalized, consequences)
        self.assertIn("Adversary Agent", adversary_prompt)
        self.assertIn(formalized, adversary_prompt)
        self.assertIn(consequences, adversary_prompt)
        self.assertIn("falsify", adversary_prompt.lower())

        # Test evidence prompt
        evidence_prompt = machine._format_evidence_prompt(formalized)
        self.assertIn("Evidence Agent", evidence_prompt)
        self.assertIn(formalized, evidence_prompt)
        self.assertIn("evidence", evidence_prompt.lower())

        # Test judge prompt
        judge_prompt = machine._format_judge_prompt(formalized, consequences, falsification, evidence)
        self.assertIn("Judge Agent", judge_prompt)
        self.assertIn(formalized, judge_prompt)
        self.assertIn(consequences, judge_prompt)
        self.assertIn(falsification, judge_prompt)
        self.assertIn(evidence, judge_prompt)
        self.assertIn("confidence level", judge_prompt.lower())

    def test_load_hypothesis_from_file(self):
        """Test loading hypothesis from file"""
        test_hypothesis = "Energy is conserved in all isolated systems"
        test_file = os.path.join(self.temp_dir.name, "test_hypothesis.txt")

        with open(test_file, 'w') as f:
            f.write(test_hypothesis + "\n")

        loaded_hypothesis = load_hypothesis_from_file(test_file)
        self.assertEqual(loaded_hypothesis, test_hypothesis)

        test_hypothesis_with_whitespace = "  " + test_hypothesis + "  \n\n"
        with open(test_file, 'w') as f:
            f.write(test_hypothesis_with_whitespace)

        loaded_hypothesis = load_hypothesis_from_file(test_file)
        self.assertEqual(loaded_hypothesis, test_hypothesis)

    def test_save_result_path_handling(self):
        """Test that save_result properly handles file paths"""
        with patch('agent_assembly_line.llm_factory.LLMFactory.create_llm_and_embeddings') as mock_create:
            mock_create.return_value = (MagicMock(), MagicMock())
            machine = ProofRefutationMachine(mode='local', debug=False)

        result = EvaluationResult(
            hypothesis="Test",
            formalized_statement="Formalized",
            derived_consequences="Consequences",
            falsification_attempts="Falsification",
            evidence_assessment="Evidence",
            final_verdict="Verdict",
            confidence_level="High",
            processing_time=1.0,
            timestamp=1234567890.0
        )

        output_dir = os.path.join(self.temp_dir.name, "subdir", "results")
        output_path = os.path.join(output_dir, "test_output")

        try:
            machine.save_result(result, output_path, quiet=True)

            json_path = output_path + ".json"
            md_path = output_path + ".md"

            self.assertTrue(os.path.exists(json_path))
            self.assertTrue(os.path.exists(md_path))
            self.assertTrue(os.path.exists(output_dir))

        except Exception as e:
            self.fail(f"save_result failed with directory creation: {e}")


class TestAgentConfiguration(unittest.TestCase):
    """Test agent configuration and mode settings"""

    def test_model_identifier_mapping(self):
        """Test that mode correctly maps to model identifiers"""
        with patch('agent_assembly_line.llm_factory.LLMFactory.create_llm_and_embeddings') as mock_create:
            mock_create.return_value = (MagicMock(), MagicMock())

            # Test local mode
            try:
                machine_local = ProofRefutationMachine(mode='local', debug=False)
                for agent_name, agent in machine_local.agents.items():
                    self.assertEqual(agent.config.model_identifier, "ollama:gemma2:latest")
                    self.assertEqual(agent.config.llm_type, "ollama")
                    self.assertEqual(agent.config.model_name, "gemma2:latest")
            except Exception as e:
                self.fail(f"Local mode configuration failed: {e}")

            # Test cloud mode
            try:
                machine_cloud = ProofRefutationMachine(mode='cloud', debug=False)
                for agent_name, agent in machine_cloud.agents.items():
                    self.assertEqual(agent.config.model_identifier, "openai:gpt-4o")
                    self.assertEqual(agent.config.llm_type, "openai")
                    self.assertEqual(agent.config.model_name, "gpt-4o")
            except Exception as e:
                self.fail(f"Cloud mode configuration failed: {e}")

    def test_agent_names_preserved(self):
        """Test that agent names are preserved after mode configuration"""
        with patch('agent_assembly_line.llm_factory.LLMFactory.create_llm_and_embeddings') as mock_create:
            mock_create.return_value = (MagicMock(), MagicMock())
            machine = ProofRefutationMachine(mode='local', debug=False)

        expected_names = {
            'interpreter': 'interpreter_agent',
            'theorist': 'theorist_agent',
            'adversary': 'adversary_agent',
            'evidence': 'evidence_agent',
            'judge': 'judge_agent'
        }

        for key, expected_name in expected_names.items():
            self.assertEqual(machine.agents[key].name, expected_name)


if __name__ == '__main__':
    unittest.main()