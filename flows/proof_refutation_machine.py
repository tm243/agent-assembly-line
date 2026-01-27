#!/usr/bin/env python3
"""
Proof-and-Refutation Machine using the Agent Assembly Line.

This script implements a 5-agent system that takes a scientific hypothesis
and puts it through rigorous evaluation:
1. Interpreter - formalizes and clarifies the hypothesis
2. Theorist - derives logical consequences and predictions
3. Adversary - actively tries to disprove the hypothesis
4. Evidence - searches for empirical support or contradiction
5. Judge - synthesizes all outputs and makes final determination

The system is designed to resist hallucinated certainty and provide
scientific-style conclusions with proper uncertainty quantification.

Usage:
    python proof_refutation_machine.py --hypothesis "Energy is conserved in all physical systems"
    python proof_refutation_machine.py --hypothesis "Intelligence increases with brain size" --mode cloud
    python proof_refutation_machine.py --file hypothesis.txt
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict
from dataclasses import dataclass

from agent_assembly_line.agent import Agent
from agent_assembly_line.config import Config

@dataclass
class EvaluationResult:
    """Container for the complete evaluation result."""
    hypothesis: str
    formalized_statement: str
    derived_consequences: str
    falsification_attempts: str
    evidence_assessment: str
    final_verdict: str
    confidence_level: str
    processing_time: float
    timestamp: float

class ProofRefutationMachine:
    """
    A 5-agent system for rigorous hypothesis evaluation.
    """
    
    def __init__(self, mode='local', debug=False):
        """
        Initialize the proof-refutation machine.
        
        Args:
            mode: 'local' for offline LLM or 'cloud' for OpenAI/Claude
            debug: Enable debug output
        """
        self.mode = mode
        self.debug = debug
        self.agents = self._initialize_agents()
        
    def _initialize_agents(self) -> Dict[str, Agent]:
        """Initialize all 5 specialized agents."""
        agents = {}
        
        # Determine model identifier based on mode
        if self.mode == 'local':
            model_identifier = "ollama:gemma2:latest"
        elif self.mode == 'cloud':
            model_identifier = "openai:gpt-4o"
        else:
            raise ValueError(f"Invalid mode '{self.mode}'. Choose either 'local' or 'cloud'.")
        
        # Agent 1: Interpreter/Formalizer
        interpreter_config = Config()
        interpreter_config.model_identifier = model_identifier
        interpreter_config.llm_type, interpreter_config.model_name = interpreter_config.parse_model_identifier(model_identifier)
        agents['interpreter'] = Agent('interpreter_agent', config=interpreter_config, debug=self.debug)
        
        # Agent 2: Theorist/Consequence Generator
        theorist_config = Config()
        theorist_config.model_identifier = model_identifier
        theorist_config.llm_type, theorist_config.model_name = theorist_config.parse_model_identifier(model_identifier)
        agents['theorist'] = Agent('theorist_agent', config=theorist_config, debug=self.debug)
        
        # Agent 3: Adversary/Falsifier
        adversary_config = Config()
        adversary_config.model_identifier = model_identifier
        adversary_config.llm_type, adversary_config.model_name = adversary_config.parse_model_identifier(model_identifier)
        agents['adversary'] = Agent('adversary_agent', config=adversary_config, debug=self.debug)
        
        # Agent 4: Evidence/Grounding Agent
        evidence_config = Config()
        evidence_config.model_identifier = model_identifier
        evidence_config.llm_type, evidence_config.model_name = evidence_config.parse_model_identifier(model_identifier)
        agents['evidence'] = Agent('evidence_agent', config=evidence_config, debug=self.debug)
        
        # Agent 5: Judge/Synthesizer
        judge_config = Config()
        judge_config.model_identifier = model_identifier
        judge_config.llm_type, judge_config.model_name = judge_config.parse_model_identifier(model_identifier)
        agents['judge'] = Agent('judge_agent', config=judge_config, debug=self.debug)
        
        return agents
    
    def _format_interpreter_prompt(self, hypothesis: str) -> str:
        """Create the prompt for Agent 1 - Interpreter."""
        return f"""You are the Interpreter Agent.

Task:
- Rewrite the given hypothesis in precise, technical terms.
- Define all ambiguous concepts.
- Explicitly list assumptions.
- State the domain of validity (if implied).
- If the hypothesis cannot be made falsifiable, say so.

Input:
HYPOTHESIS: "{hypothesis}"

Output format:
1. Formalized statement
2. Definitions
3. Assumptions  
4. Domain of applicability

Be precise and technical. Remove ambiguity while preserving the original meaning."""

    def _format_theorist_prompt(self, formalized_statement: str) -> str:
        """Create the prompt for Agent 2 - Theorist."""
        return f"""You are the Theorist Agent.

Task:
- Assume the formalized hypothesis is correct.
- Derive necessary logical, mathematical, or physical consequences.
- Identify testable predictions.
- Include limiting cases and invariants where possible.

Input:
{formalized_statement}

Output format:
1. Derived consequences
2. Testable predictions
3. Special cases and limits

Think step-by-step through the logical implications. What MUST be true if this hypothesis is correct?"""

    def _format_adversary_prompt(self, formalized_statement: str, consequences: str) -> str:
        """Create the prompt for Agent 3 - Adversary."""
        return f"""You are the Adversary Agent.

Task:
- Attempt to falsify the hypothesis.
- Search for counterexamples, contradictions, or edge cases.
- Compare against established theories or known results.
- Identify conditions under which the hypothesis fails.

Important:
You are incentivized to DISAGREE and to be skeptical. Your job is to break this hypothesis.

Input:
FORMALIZED STATEMENT:
{formalized_statement}

DERIVED CONSEQUENCES:
{consequences}

Output format:
1. Potential counterexamples
2. Conflicts with known theory or data
3. Failure modes or restrictions

Be ruthlessly critical. What could go wrong? Where might this hypothesis fail?"""

    def _format_evidence_prompt(self, formalized_statement: str) -> str:
        """Create the prompt for Agent 4 - Evidence."""
        return f"""You are the Evidence Agent.

Task:
- Identify relevant experimental, observational, or simulation-based evidence.
- Assess whether the evidence supports or contradicts the hypothesis.
- Distinguish direct evidence from indirect or circumstantial evidence.
- Note quality, limitations, and uncertainty of evidence.

Input:
{formalized_statement}

Output format:
1. Supporting evidence
2. Contradictory evidence (if any)
3. Evidence quality and gaps

Focus on real, empirical data. What does the evidence actually say?"""

    def _format_judge_prompt(self, interpreter_output: str, theorist_output: str, 
                           adversary_output: str, evidence_output: str) -> str:
        """Create the prompt for Agent 5 - Judge."""
        return f"""You are the Judge Agent.

Task:
- Synthesize outputs from all previous agents.
- Weigh support vs falsification attempts.
- Decide whether the hypothesis is:
  (True / False / Conditionally true / Undecidable)
- Clearly state assumptions and confidence level.
- Suggest what evidence or analysis would most improve certainty.

Inputs:

INTERPRETER OUTPUT:
{interpreter_output}

THEORIST OUTPUT:
{theorist_output}

ADVERSARY OUTPUT:
{adversary_output}

EVIDENCE OUTPUT:
{evidence_output}

Output format:
1. Verdict
2. Justification
3. Confidence level
4. Conditions or caveats
5. What would change this conclusion

Make a careful, balanced decision. Avoid overconfidence. Be explicit about uncertainty."""

    def evaluate_hypothesis(self, hypothesis: str) -> EvaluationResult:
        """
        Run the complete 5-agent evaluation pipeline.
        
        Args:
            hypothesis: The scientific hypothesis to evaluate
            
        Returns:
            EvaluationResult containing all agent outputs and final verdict
        """
        start_time = time.time()
        
        if self.debug:
            print(f"🔬 Starting evaluation of: {hypothesis}")
        
        # Agent 1: Interpreter/Formalizer
        print("🔍 Agent 1: Formalizing hypothesis...")
        interpreter_prompt = self._format_interpreter_prompt(hypothesis)
        formalized_result = self.agents['interpreter'].run(interpreter_prompt, skip_rag=False)
        
        if self.debug:
            print(f"Formalized: {formalized_result[:200]}...")
        
        # Agent 2: Theorist/Consequence Generator
        print("🧠 Agent 2: Deriving consequences...")
        theorist_prompt = self._format_theorist_prompt(formalized_result)
        consequences_result = self.agents['theorist'].run(theorist_prompt, skip_rag=False)
        
        if self.debug:
            print(f"Consequences: {consequences_result[:200]}...")
        
        # Agent 3: Adversary/Falsifier
        print("⚔️ Agent 3: Attempting falsification...")
        adversary_prompt = self._format_adversary_prompt(formalized_result, consequences_result)
        falsification_result = self.agents['adversary'].run(adversary_prompt, skip_rag=False)
        
        if self.debug:
            print(f"Falsification: {falsification_result[:200]}...")
        
        # Agent 4: Evidence/Grounding Agent
        print("📊 Agent 4: Assessing evidence...")
        evidence_prompt = self._format_evidence_prompt(formalized_result)
        evidence_result = self.agents['evidence'].run(evidence_prompt, skip_rag=False)
        
        if self.debug:
            print(f"Evidence: {evidence_result[:200]}...")
        
        # Agent 5: Judge/Synthesizer
        print("⚖️ Agent 5: Making final judgment...")
        judge_prompt = self._format_judge_prompt(
            formalized_result, consequences_result, 
            falsification_result, evidence_result
        )
        verdict_result = self.agents['judge'].run(judge_prompt, skip_rag=False)
        
        processing_time = time.time() - start_time
        
        result = EvaluationResult(
            hypothesis=hypothesis,
            formalized_statement=formalized_result,
            derived_consequences=consequences_result,
            falsification_attempts=falsification_result,
            evidence_assessment=evidence_result,
            final_verdict=verdict_result,
            confidence_level=self._extract_confidence_level(verdict_result),
            processing_time=processing_time,
            timestamp=time.time()
        )
        
        print(f"✅ Evaluation completed in {processing_time:.1f} seconds")
        return result

    def _extract_confidence_level(self, judge_output: str) -> str:
        """Extract confidence level from judge output."""
        lines = judge_output.split('\n')
        lines_lower = [line.lower() for line in lines]

        for i, line_lower in enumerate(lines_lower):
            if 'confidence' in line_lower and ('level' in line_lower or ':' in line_lower):
                # Look for patterns like "confidence level: 85%" or "3. confidence level"
                if ':' in line_lower:
                    confidence_part = lines[i].split(':', 1)[1].strip()
                    if confidence_part:
                        return confidence_part
                # If it's a numbered item, get the next non-empty line
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line:
                        return next_line
        return "Not specified"
    
    def save_result(self, result: EvaluationResult, output_path: str, quiet: bool = False):
        """Save the evaluation result to a file."""
        output_data = {
            'hypothesis': result.hypothesis,
            'timestamp': result.timestamp,
            'processing_time': result.processing_time,
            'agents': {
                'interpreter': {
                    'role': 'Formalizer',
                    'output': result.formalized_statement
                },
                'theorist': {
                    'role': 'Consequence Generator',
                    'output': result.derived_consequences
                },
                'adversary': {
                    'role': 'Falsifier',
                    'output': result.falsification_attempts
                },
                'evidence': {
                    'role': 'Evidence Assessor',
                    'output': result.evidence_assessment
                },
                'judge': {
                    'role': 'Final Judge',
                    'output': result.final_verdict
                }
            }
        }
        
        # Save as JSON
        json_path = output_path.replace('.md', '.json') if output_path.endswith('.md') else output_path + '.json'
        Path(json_path).parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        # Save as Markdown
        md_path = output_path if output_path.endswith('.md') else output_path + '.md'
        Path(md_path).parent.mkdir(parents=True, exist_ok=True)
        self._save_markdown_report(result, md_path)
        
        if not quiet:
            print(f"📄 Results saved to:")
            print(f"   JSON: {json_path}")
            print(f"   Markdown: {md_path}")
    
    def _save_markdown_report(self, result: EvaluationResult, output_path: str):
        """Generate and save a markdown report of the evaluation."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        report = f"""# Hypothesis Evaluation Report

**Hypothesis:** {result.hypothesis}

**Evaluation Date:** {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result.timestamp))}

**Processing Time:** {result.processing_time:.1f} seconds

---

## Agent 1: Interpreter/Formalizer

**Role:** Remove ambiguity and make the claim falsifiable.

### Output:
{result.formalized_statement}

---

## Agent 2: Theorist/Consequence Generator  

**Role:** Assume hypothesis is true and derive implications.

### Output:
{result.derived_consequences}

---

## Agent 3: Adversary/Falsifier

**Role:** Actively try to disprove the hypothesis.

### Output:
{result.falsification_attempts}

---

## Agent 4: Evidence/Grounding Agent

**Role:** Anchor the claim in empirical reality.

### Output:
{result.evidence_assessment}

---

## Agent 5: Judge/Synthesizer

**Role:** Make the final call with uncertainty quantification.

### Final Verdict:
{result.final_verdict}

**Confidence Level:** {result.confidence_level}

---

*This report was generated by the Proof-and-Refutation Machine using the Agent Assembly Line framework.*
"""
        
        with open(output_path, 'w') as f:
            f.write(report)

def load_hypothesis_from_file(file_path: str) -> str:
    """Load hypothesis from a text file."""
    with open(file_path, 'r') as f:
        return f.read().strip()

def main():
    parser = argparse.ArgumentParser(
        description='Proof-and-Refutation Machine for Scientific Hypothesis Evaluation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s --hypothesis "Energy is conserved in all physical systems"
  %(prog)s --hypothesis "Intelligence increases with brain size" --mode cloud
  %(prog)s --file hypothesis.txt --output evaluation_report
  %(prog)s --hypothesis "Gravity is caused by curved spacetime" --debug
        '''
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--hypothesis', type=str,
                           help='Hypothesis to evaluate (as string)')
    input_group.add_argument('--file', type=str,
                           help='Path to file containing hypothesis')
    
    # Configuration options
    parser.add_argument('--mode', choices=['local', 'cloud'], default='local',
                       help='LLM mode: local (offline) or cloud (OpenAI/Claude)')
    parser.add_argument('--output', type=str,
                       help='Output file path (without extension)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug output')
    
    args = parser.parse_args()
    
    try:
        # Load hypothesis
        if args.hypothesis:
            hypothesis = args.hypothesis
        else:
            hypothesis = load_hypothesis_from_file(args.file)
            
        if not hypothesis.strip():
            print("❌ Error: Empty hypothesis provided")
            sys.exit(1)
        
        print(f"🔬 Proof-and-Refutation Machine")
        print(f"Mode: {args.mode}")
        print(f"Hypothesis: {hypothesis}")
        print("-" * 60)
        
        # Initialize and run the machine
        machine = ProofRefutationMachine(mode=args.mode, debug=args.debug)
        result = machine.evaluate_hypothesis(hypothesis)
        
        # Display summary
        print("\n" + "="*60)
        print("📋 EVALUATION SUMMARY")
        print("="*60)
        print(f"Hypothesis: {hypothesis}")
        print(f"Processing time: {result.processing_time:.1f} seconds")
        print("\nFinal verdict (excerpt):")
        print(result.final_verdict[:300] + "..." if len(result.final_verdict) > 300 else result.final_verdict)
        
        # Save results
        if args.output:
            machine.save_result(result, args.output)
        else:
            # Default output name based on hypothesis
            safe_name = "".join(c for c in hypothesis[:50] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_').lower()
            machine.save_result(result, f"hypothesis_evaluation_{safe_name}")
        
        print("\n✅ Evaluation complete!")
        
    except KeyboardInterrupt:
        print("\n❌ Evaluation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()