"""
Agent-Assembly-Line Text Cleanup Evaluator
"""

import difflib
import re
from agent_assembly_line.agent import Agent
from agent_assembly_line.config import Config

class TextCleanupEvaluator(Agent):
    """
    A specialized agent for evaluating the quality of text cleanup operations.
    Compares original and cleaned text to assess improvement.
    """

    purpose = (
        "This agent specializes in evaluating the quality of text cleanup operations. "
        "It compares original and cleaned text files to assess encoding fixes, "
        "character corrections, and overall improvement quality."
    )

    def __init__(self, mode='local', verbose=True, **kwargs):
        """
        Initializes the TextCleanupEvaluator.

        Args:
            mode (str): The mode to use ('local' or 'cloud'). Defaults to 'local'.
        """
        self.verbose = verbose

        evaluation_template = """
You are a text cleanup quality evaluator. Your task is to analyze diffs between original and cleaned text 
to assess encoding fixes and character corrections.

## Context:
- Today's date: {today}
- You are evaluating text cleanup by analyzing specific changes
- Focus on the actual changes shown in the diff
- Provide brief, focused responses

## Evaluation Criteria:
1. **Encoding Fixes**: How well were umlauts and encoding issues resolved?
2. **Character Corrections**: Were corrupted quotes, symbols, and special characters fixed?
3. **Preservation**: Was original meaning and structure preserved?
4. **Change Quality**: Are changes appropriate and targeted?

## Instructions:
1. Analyze the specific changes shown
2. Identify what was improved
3. Note any problems (briefly)
4. Score 0-100 for quality
5. Keep responses concise (1-2 sentences each)

## File Statistics:
{context}

## Changes to evaluate:
{question}

## Evaluation Report:
Provide brief responses:
- Overall Score (0-100): 
- Encoding Fixes: [one sentence describing what was fixed]
- Issues Found: [one sentence about problems, or "None"]
- Recommendations: [one sentence suggestion]
"""

        if mode == 'local':
            model_identifier = "ollama:gemma2:latest"
        elif mode == 'cloud':
            model_identifier = "openai:gpt-4o"
        else:
            raise ValueError("Invalid mode. Choose either 'local' or 'cloud'.")

        config = Config()
        config.load_conf_dict({
            "name": kwargs.get("name", "text-cleanup-evaluator"),
            "description": kwargs.get("description", "Agent for evaluating text cleanup quality"),
            "prompt": { "inline_rag_templates": evaluation_template },
            "llm": {
                "model-identifier": model_identifier
            },
        })
        super().__init__(config=config)

    def _log(self, message):
        if self.verbose:
            print(message)
    
    def _read_file_with_encoding_detection(self, file_path):
        """Read a file with automatic encoding detection."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        text = f.read()
                    self._log(f"Read file using {encoding} encoding")
                    return text
                except UnicodeDecodeError:
                    continue
            raise ValueError(f"Could not read file {file_path}")
    
    def _generate_diff(self, original_text, cleaned_text, original_path, cleaned_path):
        """Generate a unified diff between original and cleaned text."""
        original_lines = original_text.splitlines(keepends=True)
        cleaned_lines = cleaned_text.splitlines(keepends=True)
        
        diff_lines = list(difflib.unified_diff(
            original_lines,
            cleaned_lines,
            fromfile=f"a/{original_path.split('/')[-1]}",
            tofile=f"b/{cleaned_path.split('/')[-1]}",
            lineterm='',
            n=1  # Reduce context size from default 3 to 1 line
        ))
        
        if not diff_lines:
            return "No changes detected between the files.", []
        
        diff_text = ''.join(diff_lines)
        self._log(f"Generated diff with {len(diff_lines)} lines of changes ({len(diff_text)} characters)")
        
        # Parse diff into hunks for individual analysis
        hunks = self._parse_diff_hunks(diff_lines)
        self._log(f"Parsed diff into {len(hunks)} hunks for analysis")
        
        return diff_text, hunks
    
    def _parse_diff_hunks(self, diff_lines):
        """Parse diff lines into individual hunks for analysis."""
        hunks = []
        current_hunk = []
        in_hunk = False
        
        for line in diff_lines:
            if line.startswith('@@'):
                # Save previous hunk if exists
                if current_hunk:
                    hunks.append({
                        'header': current_hunk[0] if current_hunk else '',
                        'lines': current_hunk[1:] if len(current_hunk) > 1 else [],
                        'additions': len([l for l in current_hunk if l.startswith('+') and not l.startswith('+++')]),
                        'deletions': len([l for l in current_hunk if l.startswith('-') and not l.startswith('---')])
                    })
                
                # Start new hunk
                current_hunk = [line]
                in_hunk = True
            elif in_hunk:
                current_hunk.append(line)
        
        # Save last hunk
        if current_hunk:
            hunks.append({
                'header': current_hunk[0] if current_hunk else '',
                'lines': current_hunk[1:] if len(current_hunk) > 1 else [],
                'additions': len([l for l in current_hunk if l.startswith('+') and not l.startswith('+++')]),
                'deletions': len([l for l in current_hunk if l.startswith('-') and not l.startswith('---')])
            })
        
        return hunks

    def evaluate_cleanup(self, original_file_path, cleaned_file_path, log_file_path=None):
        """
        Evaluates the quality of text cleanup by analyzing each change in the diff individually.

        Args:
            original_file_path (str): Path to the original text file
            cleaned_file_path (str): Path to the cleaned text file
            log_file_path (str, optional): Path to write detailed evaluation log

        Returns:
            dict: Evaluation results including score and analysis
        """
        self._log(f"Evaluating cleanup quality using step-by-step diff analysis...")
        self._log(f"Original file: {original_file_path}")
        self._log(f"Cleaned file: {cleaned_file_path}")

        original_text = self._read_file_with_encoding_detection(original_file_path)
        
        # Read cleaned file
        try:
            with open(cleaned_file_path, 'r', encoding='utf-8') as f:
                cleaned_text = f.read()
        except UnicodeDecodeError:
            raise ValueError(f"Could not read cleaned file {cleaned_file_path}")

        diff_text, hunks = self._generate_diff(original_text, cleaned_text, original_file_path, cleaned_file_path)
        
        if not hunks:
            return {
                'overall_score': 100,
                'encoding_fixes': 'No changes needed',
                'issues_found': 'None - files are identical',
                'recommendations': 'None',
                'hunk_evaluations': [],
                'total_hunks': 0
            }
        
        file_stats = f"""
Original file: {original_file_path}
Cleaned file: {cleaned_file_path}
Original text length: {len(original_text):,} characters
Cleaned text length: {len(cleaned_text):,} characters
Change in size: {len(cleaned_text) - len(original_text):,} characters
Total hunks to analyze: {len(hunks)}
"""

        self._log(f"Analyzing {len(hunks)} hunks step by step...")
        
        hunk_evaluations = []
        evaluation_log = []
        evaluation_log.append(f"DIFF EVALUATION LOG - {original_file_path}")
        evaluation_log.append("=" * 80)
        evaluation_log.append(file_stats)
        
        for i, hunk in enumerate(hunks, 1):
            self._log(f"Analyzing hunk {i}/{len(hunks)}...")

            hunk_result = self._evaluate_hunk(hunk, i, file_stats)
            hunk_evaluations.append(hunk_result)
            
            evaluation_log.append(f"\nHUNK {i}/{len(hunks)}:")
            evaluation_log.append("-" * 40)
            evaluation_log.append(f"Header: {hunk['header']}")
            evaluation_log.append(f"Location: Line {hunk_result.get('line_info', {}).get('original_start', 'Unknown')}")
            evaluation_log.append(f"Changes: +{hunk['additions']}, -{hunk['deletions']}")
            evaluation_log.append(f"Score: {hunk_result.get('score', 'N/A')}")
            
            # Add comparison if available
            if hunk_result.get('comparison'):
                evaluation_log.append(f"\nContext with Changes:")
                evaluation_log.append(hunk_result['comparison'])
            
            evaluation_log.append(f"\nAnalysis: {hunk_result.get('analysis', 'No analysis')}")
            if hunk_result.get('issues') and 'none' not in hunk_result.get('issues', '').lower():
                evaluation_log.append(f"Issues: {hunk_result['issues']}")
            if hunk_result.get('character_fixes') and 'not specified' not in hunk_result.get('character_fixes', '').lower():
                evaluation_log.append(f"Character Fixes: {hunk_result['character_fixes']}")
            evaluation_log.append("")
        
        overall_results = self._synthesize_results(hunk_evaluations, file_stats)
        
        # Add overall results to log
        evaluation_log.append("\nOVERALL EVALUATION:")
        evaluation_log.append("=" * 80)
        evaluation_log.append(f"Overall Score: {overall_results.get('overall_score', 'N/A')}/100")
        evaluation_log.append(f"Encoding Fixes: {overall_results.get('encoding_fixes', 'N/A')}")
        evaluation_log.append(f"Issues Found: {overall_results.get('issues_found', 'N/A')}")
        evaluation_log.append(f"Recommendations: {overall_results.get('recommendations', 'N/A')}")
        
        # Write log file if requested
        if log_file_path:
            try:
                with open(log_file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(evaluation_log))
                self._log(f"Detailed evaluation log written to: {log_file_path}")
            except Exception as e:
                self._log(f"Warning: Could not write log file: {e}")
        
        overall_results.update({
            'hunk_evaluations': hunk_evaluations,
            'total_hunks': len(hunks),
            'evaluation_log': evaluation_log,
            'diff_size': len(diff_text)
        })
        
        self._log(f"Evaluation complete. Overall score: {overall_results.get('overall_score', 'N/A')}/100")
        
        return overall_results
    
    def _evaluate_hunk(self, hunk, hunk_number, file_stats):
        """
        Evaluate a single diff hunk.
        
        Args:
            hunk (dict): Hunk data with header, lines, additions, deletions
            hunk_number (int): Sequential hunk number
            file_stats (str): File statistics for context
            
        Returns:
            dict: Hunk evaluation results
        """
        hunk_content = hunk['header'] + '\n' + ''.join(hunk['lines'])
        
        # Extract line numbers from header
        line_info = self._extract_line_info(hunk['header'])
        
        all_lines = hunk['lines']
        context_lines = [line[1:] for line in all_lines if line.startswith(' ')]
        original_lines = [line[1:] for line in all_lines if line.startswith('-') and not line.startswith('---')]
        changed_lines = [line[1:] for line in all_lines if line.startswith('+') and not line.startswith('+++')]
        
        comparison = self._create_line_comparison_with_context(all_lines, line_info)
        
        # Limit individual hunk size for analysis
        max_hunk_size = 1500
        if len(hunk_content) > max_hunk_size:
            hunk_content = hunk_content[:max_hunk_size] + "\n... (hunk truncated for analysis)"
        
        hunk_prompt = f"""
Analyze this diff hunk (#{hunk_number}) for text cleanup quality.

## Change Summary:
- Lines removed: {hunk['deletions']}
- Lines added: {hunk['additions']}
- Starting line: {line_info.get('original_start', 'Unknown')}

## Context with Changes:
{comparison}

## Full Hunk:
{hunk_content}

## Instructions:
Provide brief, focused responses:
1. Score (0-100): Quality rating
2. Analysis: One sentence describing what was fixed
3. Issues: One sentence about problems, or "None"
4. Character fixes: Specific characters/encoding issues addressed

Be concise and specific.
"""
        
        try:
            self.replace_inline_text(file_stats)
            result = self.run(hunk_prompt)
            
            parsed_result = self._parse_hunk_evaluation(result, hunk_number)
            parsed_result.update({
                'hunk_number': hunk_number,
                'additions': hunk['additions'],
                'deletions': hunk['deletions'],
                'original_lines': original_lines,
                'changed_lines': changed_lines,
                'context_lines': context_lines,
                'line_info': line_info,
                'comparison': comparison,
                'raw_response': result
            })
            
            return parsed_result
            
        except Exception as e:
            self._log(f"Warning: Error evaluating hunk {hunk_number}: {e}")
            return {
                'hunk_number': hunk_number,
                'score': 50,
                'analysis': f'Error during evaluation: {str(e)}',
                'issues': 'Evaluation failed',
                'character_fixes': 'Unknown',
                'additions': hunk['additions'],
                'deletions': hunk['deletions'],
                'comparison': 'Error extracting comparison',
                'line_info': {'original_start': 'Unknown'}
            }
    
    def _extract_line_info(self, header):
        """
        Extract line number information from diff header.
        
        Args:
            header (str): Diff header like "@@ -15,3 +15,3 @@"
            
        Returns:
            dict: Line information
        """
        import re
        
        # Parse header like "@@ -15,3 +15,3 @@"
        match = re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', header)
        
        if match:
            return {
                'original_start': int(match.group(1)),
                'original_count': int(match.group(2)) if match.group(2) else 1,
                'new_start': int(match.group(3)),
                'new_count': int(match.group(4)) if match.group(4) else 1
            }
        
        return {
            'original_start': 'Unknown',
            'original_count': 'Unknown',
            'new_start': 'Unknown', 
            'new_count': 'Unknown'
        }
    
    def _create_line_comparison_with_context(self, all_lines, line_info):
        """
        Create a detailed comparison showing original and corrected text blocks.
        
        Args:
            all_lines (list): All lines from the hunk (context, removals, additions)
            line_info (dict): Line number information
            
        Returns:
            str: Formatted comparison with original and corrected blocks
        """
        if not all_lines:
            return "No changes detected"
        
        start_line = line_info.get('original_start', 1)
        line_count = line_info.get('original_count', 1)
        end_line = start_line + line_count - 1
        
        context_before = []
        context_after = []
        original_lines = []
        corrected_lines = []
        
        # Parse all lines and categorize them
        for i, line in enumerate(all_lines):
            line_content = line[1:] if len(line) > 0 else ""
            
            if line.startswith(' '):  # Context line
                # Determine if this context is before or after changes
                has_changes_after = any(l.startswith(('-', '+')) and not l.startswith(('---', '+++')) 
                                      for l in all_lines[i+1:])
                if has_changes_after:
                    context_before.append(line_content.rstrip())
                else:
                    context_after.append(line_content.rstrip())
            elif line.startswith('-') and not line.startswith('---'):
                original_lines.append(line_content.rstrip())
            elif line.startswith('+') and not line.startswith('+++'):
                corrected_lines.append(line_content.rstrip())
        
        comparison_parts = []
        
        # Header with line range
        if end_line == start_line:
            comparison_parts.append(f"Line {start_line}:")
        else:
            comparison_parts.append(f"Lines {start_line}-{end_line}:")
        
        # Separator
        comparison_parts.append("-" * 60)
        
        # Original text block (context before + original + context after)
        if context_before or original_lines or context_after:
            # Add context before without prefix
            comparison_parts.extend(context_before)
            # Add original lines with "- " prefix
            for line in original_lines:
                comparison_parts.append("- " + line)
            # Add context after without prefix
            comparison_parts.extend(context_after)
        else:
            comparison_parts.append("(no original content)")
            
        # Separator
        comparison_parts.append("-" * 60)
        
        # Corrected text block (context before + corrected + context after)
        if context_before or corrected_lines or context_after:
            # Add context before without prefix
            comparison_parts.extend(context_before)
            # Add corrected lines with "+ " prefix
            for line in corrected_lines:
                comparison_parts.append("+ " + line)
            # Add context after without prefix
            comparison_parts.extend(context_after)
        else:
            comparison_parts.append("(no corrected content)")
            
        # Final separator
        comparison_parts.append("-" * 60)
        comparison_parts.append("")  # Extra newline for spacing
        comparison_parts.append("")  # Second newline for clear separation
        
        return "\n".join(comparison_parts)
    
    def _create_line_comparison(self, original_lines, changed_lines):
        """
        Create a side-by-side comparison of original vs changed lines.
        
        Args:
            original_lines (list): Lines that were removed
            changed_lines (list): Lines that were added
            
        Returns:
            str: Formatted comparison
        """
        if not original_lines and not changed_lines:
            return "No line changes detected"
        
        comparison_parts = []
        
        # Handle line-by-line comparison
        max_lines = max(len(original_lines), len(changed_lines))
        
        for i in range(min(max_lines, 5)):  # Limit to first 5 lines for brevity
            original = original_lines[i] if i < len(original_lines) else "(no line)"
            changed = changed_lines[i] if i < len(changed_lines) else "(no line)"
            
            # Truncate very long lines
            if len(original) > 100:
                original = original[:97] + "..."
            if len(changed) > 100:
                changed = changed[:97] + "..."
            
            comparison_parts.append(f"BEFORE: {original.strip()}")
            comparison_parts.append(f"AFTER:  {changed.strip()}")
            comparison_parts.append("---")
        
        if max_lines > 5:
            comparison_parts.append(f"... and {max_lines - 5} more line changes")
        
        return "\n".join(comparison_parts)
    
    def _parse_hunk_evaluation(self, evaluation_text, hunk_number):
        """
        Parse the evaluation result for a single hunk.
        
        Args:
            evaluation_text (str): Raw evaluation response
            hunk_number (int): Hunk number for reference
            
        Returns:
            dict: Parsed hunk evaluation
        """
        result = {
            'score': 70,  # Default score
            'analysis': 'Analysis not provided',
            'issues': 'None identified',
            'character_fixes': 'Not specified'
        }
        
        lines = evaluation_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Extract score
            if 'score' in line.lower() and ('(' in line or ':' in line):
                numbers = re.findall(r'\b(\d{1,3})\b', line)
                if numbers:
                    try:
                        score = int(numbers[0])
                        if 0 <= score <= 100:
                            result['score'] = score
                    except ValueError:
                        pass
            
            # Extract sections
            elif 'analysis:' in line.lower():
                current_section = 'analysis'
                content = line.split(':', 1)[1].strip()
                if content:
                    result['analysis'] = content
            elif 'issues:' in line.lower():
                current_section = 'issues'
                content = line.split(':', 1)[1].strip()
                if content:
                    result['issues'] = content
            elif 'character fixes:' in line.lower() or 'fixes:' in line.lower():
                current_section = 'character_fixes'
                content = line.split(':', 1)[1].strip()
                if content:
                    result['character_fixes'] = content
            elif current_section and line and not line.endswith(':'):
                # Continue previous section
                if current_section in result:
                    result[current_section] += ' ' + line
        
        return result
    
    def _synthesize_results(self, hunk_evaluations, file_stats):
        """
        Combine individual hunk evaluations into overall results.
        
        Args:
            hunk_evaluations (list): List of individual hunk evaluation results
            file_stats (str): File statistics
            
        Returns:
            dict: Overall evaluation results
        """
        if not hunk_evaluations:
            return {
                'overall_score': 0,
                'encoding_fixes': 'No evaluations available',
                'issues_found': 'No evaluations performed',
                'recommendations': 'Unable to provide recommendations'
            }
        
        # Calculate weighted average score
        total_changes = sum(h['additions'] + h['deletions'] for h in hunk_evaluations)
        if total_changes == 0:
            overall_score = sum(h['score'] for h in hunk_evaluations) / len(hunk_evaluations)
        else:
            weighted_score = sum(
                h['score'] * (h['additions'] + h['deletions']) 
                for h in hunk_evaluations
            ) / total_changes
            overall_score = weighted_score
        
        all_analyses = [h.get('analysis', '') for h in hunk_evaluations if h.get('analysis')]
        all_issues = [h.get('issues', '') for h in hunk_evaluations if h.get('issues') and 'none' not in h['issues'].lower()]
        all_fixes = [h.get('character_fixes', '') for h in hunk_evaluations if h.get('character_fixes') and 'not specified' not in h['character_fixes'].lower()]
        
        encoding_fixes = '; '.join(set(all_fixes[:5])) if all_fixes else 'Character/encoding fixes performed across hunks'
        issues_found = '; '.join(set(all_issues[:3])) if all_issues else 'No major issues identified'
        
        low_score_hunks = [h for h in hunk_evaluations if h['score'] < 60]
        recommendations = []
        
        if low_score_hunks:
            recommendations.append(f"Review {len(low_score_hunks)} hunks with scores below 60")
        if len([i for i in all_issues if 'over' in i.lower() or 'aggressive' in i.lower()]) > 2:
            recommendations.append("Consider more conservative cleanup approach")
        if not all_fixes:
            recommendations.append("Document specific character fixes made")
            
        recommendations_text = '; '.join(recommendations) if recommendations else 'Overall cleanup appears satisfactory'
        
        return {
            'overall_score': int(overall_score),
            'encoding_fixes': encoding_fixes,
            'issues_found': issues_found,
            'recommendations': recommendations_text
        }

    def _parse_evaluation_result(self, evaluation_text):
        """
        Parses the evaluation result from the LLM response.
        
        Args:
            evaluation_text (str): The raw evaluation response
            
        Returns:
            dict: Parsed evaluation results
        """
        results = {
            'overall_score': 0,
            'encoding_fixes': 'Not specified',
            'issues_found': 'None identified',
            'recommendations': 'None provided',
            'raw_evaluation': evaluation_text
        }

        lines = evaluation_text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if 'overall score' in line.lower() or 'score:' in line.lower():
                numbers = re.findall(r'\d+', line)
                if numbers:
                    try:
                        results['overall_score'] = int(numbers[0])
                    except (ValueError, IndexError):
                        pass
            
            elif 'encoding fixes:' in line.lower():
                results['encoding_fixes'] = line.split(':', 1)[1].strip()
            elif 'issues found:' in line.lower():
                results['issues_found'] = line.split(':', 1)[1].strip()
            elif 'recommendations:' in line.lower():
                results['recommendations'] = line.split(':', 1)[1].strip()

        return results

    def run(self, prompt="Evaluate this text cleanup."):
        """
        Runs the evaluation agent with the given prompt.
        """
        return super().run(prompt)