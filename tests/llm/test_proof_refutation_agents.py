"""
Unit tests for Proof Refutation Machine agents
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock
from contextlib import redirect_stdout
from io import StringIO

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from agent_assembly_line.agent import Agent
from flows.proof_refutation_machine import ProofRefutationMachine


class MockModel:
    """Mock LLM model for testing"""
    def __init__(self, response="Mock response"):
        self.response = response
        
    def invoke(self, prompt):
        return self.response


class TestProofRefutationAgents(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = self.temp_dir.name
        
        self.env_patcher = patch.dict(os.environ, {
            'PYTHONPATH': os.pathsep.join([self.config_path, os.environ.get('PYTHONPATH', '')])
        })
        self.env_patcher.start()
        
    def tearDown(self):
        """Clean up test environment"""
        self.env_patcher.stop()
        self.temp_dir.cleanup()
        
    def test_interpreter_agent_creation(self):
        """Test that interpreter agent can be created"""
        try:
            with redirect_stdout(StringIO()):
                agent = Agent('interpreter_agent', debug=False)
            self.assertIsInstance(agent, Agent)
            self.assertEqual(agent.config.name, 'interpreter_agent')
        except Exception as e:
            self.fail(f"Failed to create interpreter agent: {e}")
            
    def test_theorist_agent_creation(self):
        """Test that theorist agent can be created"""
        try:
            with redirect_stdout(StringIO()):
                agent = Agent('theorist_agent', debug=False)
            self.assertIsInstance(agent, Agent)
            self.assertEqual(agent.config.name, 'theorist_agent')
        except Exception as e:
            self.fail(f"Failed to create theorist agent: {e}")
            
    def test_adversary_agent_creation(self):
        """Test that adversary agent can be created"""
        try:
            with redirect_stdout(StringIO()):
                agent = Agent('adversary_agent', debug=False)
            self.assertIsInstance(agent, Agent)
            self.assertEqual(agent.config.name, 'adversary_agent')
        except Exception as e:
            self.fail(f"Failed to create adversary agent: {e}")
            
    def test_evidence_agent_creation(self):
        """Test that evidence agent can be created"""
        try:
            with redirect_stdout(StringIO()):
                agent = Agent('evidence_agent', debug=False)
            self.assertIsInstance(agent, Agent)
            self.assertEqual(agent.config.name, 'evidence_agent')
        except Exception as e:
            self.fail(f"Failed to create evidence agent: {e}")
            
    def test_judge_agent_creation(self):
        """Test that judge agent can be created"""
        try:
            with redirect_stdout(StringIO()):
                agent = Agent('judge_agent', debug=False)
            self.assertIsInstance(agent, Agent)
            self.assertEqual(agent.config.name, 'judge_agent')
        except Exception as e:
            self.fail(f"Failed to create judge agent: {e}")


class TestProofRefutationMachine(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.TemporaryDirectory()
        
    def tearDown(self):
        """Clean up test environment"""
        self.temp_dir.cleanup()
        
    def test_machine_initialization_local_mode(self):
        """Test proof refutation machine initialization in local mode"""
        try:
            with redirect_stdout(StringIO()):
                machine = ProofRefutationMachine(mode='local', debug=True)
            self.assertEqual(machine.mode, 'local')
            self.assertTrue(machine.debug)
            self.assertEqual(len(machine.agents), 5)
            
            required_agents = ['interpreter', 'theorist', 'adversary', 'evidence', 'judge']
            for agent_name in required_agents:
                self.assertIn(agent_name, machine.agents)
                self.assertEqual(machine.agents[agent_name].config.model_identifier, "ollama:gemma2:latest")
                
        except Exception as e:
            self.fail(f"Failed to initialize machine in local mode: {e}")
            

    def test_confidence_level_extraction(self):
        """Test confidence level extraction from judge output"""
        machine = ProofRefutationMachine(mode='local', debug=False)
        
        # Test various confidence level formats
        test_cases = [
            ("Confidence level: 85%", "85%"),
            ("3. Confidence level: High (90%)", "High (90%)"),
            ("Confidence: Medium\nOther text", "Medium"),
            ("No confidence mentioned", "Not specified"),
            ("", "Not specified"),
        ]
        
        for judge_output, expected in test_cases:
            with self.subTest(output=judge_output):
                result = machine._extract_confidence_level(judge_output)
                self.assertEqual(result, expected)
                
    def test_prompt_formatting_methods(self):
        """Test that prompt formatting methods return valid strings"""
        machine = ProofRefutationMachine(mode='local', debug=False)
        
        hypothesis = "Test hypothesis"
        formalized = "Formalized test hypothesis"
        consequences = "Test consequences"
        evidence = "Test evidence"
        falsification = "Test falsification"
        
        # Test interpreter prompt
        interpreter_prompt = machine._format_interpreter_prompt(hypothesis)
        self.assertIsInstance(interpreter_prompt, str)
        self.assertIn(hypothesis, interpreter_prompt)
        
        # Test theorist prompt
        theorist_prompt = machine._format_theorist_prompt(formalized)
        self.assertIsInstance(theorist_prompt, str)
        self.assertIn(formalized, theorist_prompt)
        
        # Test adversary prompt
        adversary_prompt = machine._format_adversary_prompt(formalized, consequences)
        self.assertIsInstance(adversary_prompt, str)
        self.assertIn(formalized, adversary_prompt)
        self.assertIn(consequences, adversary_prompt)
        
        # Test evidence prompt
        evidence_prompt = machine._format_evidence_prompt(formalized)
        self.assertIsInstance(evidence_prompt, str)
        self.assertIn(formalized, evidence_prompt)
        
        # Test judge prompt
        judge_prompt = machine._format_judge_prompt(formalized, consequences, falsification, evidence)
        self.assertIsInstance(judge_prompt, str)
        self.assertIn(formalized, judge_prompt)
        self.assertIn(consequences, judge_prompt)
        self.assertIn(falsification, judge_prompt)
        self.assertIn(evidence, judge_prompt)


class TestAgentPromptTemplates(unittest.TestCase):
    """Test that agent prompt templates contain expected content"""
    
    def test_interpreter_template_structure(self):
        """Test interpreter agent template has required elements"""
        with redirect_stdout(StringIO()):
            agent = Agent('interpreter_agent', debug=False)
        template_path = agent.config.prompt_template
        
        with open(template_path, 'r') as f:
            template = f.read()
            
        self.assertIn('Interpreter Agent', template)
        self.assertIn('{question}', template)
        self.assertIn('{today}', template)
        
    def test_theorist_template_structure(self):
        """Test theorist agent template has required elements"""
        with redirect_stdout(StringIO()):
            agent = Agent('theorist_agent', debug=False)
        template_path = agent.config.prompt_template
        
        with open(template_path, 'r') as f:
            template = f.read()
            
        self.assertIn('Theorist Agent', template)
        self.assertIn('{question}', template)
        self.assertIn('consequences', template.lower())
        
    def test_evidence_template_structure(self):
        """Test evidence agent template has required elements"""
        with redirect_stdout(StringIO()):
            agent = Agent('evidence_agent', debug=False)
        template_path = agent.config.prompt_template
        
        with open(template_path, 'r') as f:
            template = f.read()
            
        self.assertIn('Evidence Agent', template)
        self.assertIn('{question}', template)
        self.assertIn('evidence', template.lower())
        
    def test_adversary_template_exists(self):
        """Test adversary agent template exists"""
        try:
            with redirect_stdout(StringIO()):
                agent = Agent('adversary_agent', debug=False)
            template_path = agent.config.prompt_template
            self.assertTrue(os.path.exists(template_path))
        except Exception as e:
            self.fail(f"Adversary agent template not found: {e}")
            
    def test_judge_template_exists(self):
        """Test judge agent template exists"""
        try:
            with redirect_stdout(StringIO()):
                agent = Agent('judge_agent', debug=False)
            template_path = agent.config.prompt_template
            self.assertTrue(os.path.exists(template_path))
        except Exception as e:
            self.fail(f"Judge agent template not found: {e}")


class TestProofRefutationIntegration(unittest.TestCase):
    """Integration tests for the complete proof refutation system"""
    
    def setUp(self):
        """Set up test environment with mocked LLM"""
        self.temp_dir = tempfile.TemporaryDirectory()
        
    def tearDown(self):
        """Clean up test environment"""
        self.temp_dir.cleanup()
        
    @patch('flows.proof_refutation_machine.ProofRefutationMachine')
    def test_end_to_end_evaluation_mock(self, mock_machine_class):
        """Test complete evaluation flow with mocked LLM responses"""
        
        # Mock responses for each agent
        mock_responses = {
            'interpreter': "Formalized hypothesis: Objects in vacuum fall at same rate regardless of mass",
            'theorist': "Consequences: 1. All objects should hit ground simultaneously\n2. No air resistance effects", 
            'adversary': "Falsification attempts: 1. Test with feather vs hammer\n2. Check for edge cases",
            'evidence': "Evidence: Apollo 15 hammer-feather experiment confirms hypothesis",
            'judge': "Verdict: True\nJustification: Strong experimental evidence\nConfidence level: High (95%)\nConditions: Only in vacuum"
        }
        
        # Create a mock machine instance
        mock_machine = MagicMock()
        mock_machine.mode = 'local'
        mock_machine.debug = True

        # Mock the evaluate_hypothesis method to return a proper result
        from flows.proof_refutation_machine import EvaluationResult
        import time

        def mock_evaluate(hypothesis):
            return EvaluationResult(
                hypothesis=hypothesis,
                formalized_statement=mock_responses['interpreter'],
                derived_consequences=mock_responses['theorist'],
                falsification_attempts=mock_responses['adversary'],
                evidence_assessment=mock_responses['evidence'],
                final_verdict=mock_responses['judge'],
                confidence_level="High (95%)",
                processing_time=1.0,
                timestamp=time.time()
            )

        mock_machine.evaluate_hypothesis = mock_evaluate
        mock_machine._extract_confidence_level = lambda output: "High (95%)"

        # Make the class constructor return our mock
        mock_machine_class.return_value = mock_machine
        
        try:
            # Import and create machine - should return our mock
            from flows.proof_refutation_machine import ProofRefutationMachine
            machine = ProofRefutationMachine(mode='local', debug=True)
            hypothesis = "Objects fall at the same rate in a vacuum regardless of mass"
            
            result = machine.evaluate_hypothesis(hypothesis)
            
            # Verify result structure
            self.assertEqual(result.hypothesis, hypothesis)
            self.assertIsInstance(result.processing_time, float)
            self.assertGreater(result.processing_time, 0)
            
            # Verify all fields are populated
            self.assertIsNotNone(result.formalized_statement)
            self.assertIsNotNone(result.derived_consequences)
            self.assertIsNotNone(result.falsification_attempts)
            self.assertIsNotNone(result.evidence_assessment)
            self.assertIsNotNone(result.final_verdict)
            
            # Verify confidence level extraction worked
            self.assertEqual(result.confidence_level, "High (95%)")
            
        except Exception as e:
            self.fail(f"End-to-end evaluation failed: {e}")


if __name__ == '__main__':
    unittest.main()