"""
Agent-Assembly-Line
"""

import unittest
import unittest.util
from agent_assembly_line.micros.test_validator_agent import TestValidatorAgent
from unittest.util import safe_repr
from distutils.util import strtobool

_MAX_LENGTH = 40

class SemanticTestCase(unittest.TestCase):
    """
    SemanticTestCase is a unit test class that provides methods to test the semantic correctness of text using a language model.

    Usage:

        assertSemanticallyEqual(first, second):
            Asserts that the semantic meaning of 'first' is the same as 'second'.
            Raises a failure exception if the texts are not semantically equal.

        assertSemanticallyCorrect(first, second):
            Asserts that the semantic meaning of 'first' is correctly interpreted by the language model when compared to 'second'.
            Raises a failure exception if the texts are not semantically correct.

        assertSemanticallyIncorrect(first, second):
            Asserts that the semantic meaning of 'first' is incorrectly interpreted by the language model when compared to 'second'.
            Raises a failure exception if the texts are semantically correct.
    """
    @classmethod
    def setUpClass(cls):
        cls.agent = TestValidatorAgent(mode='local')

    @classmethod
    def tearDownClass(cls):
        cls.agent.closeModels()

    def tearDown(self):
        self.agent.inline_context = ""
        return super().tearDown()

    def assertSemanticallyEqual(self, first, second, msg=""):
        """
        @todo try verifying this with embeddings:
        Compute cosine similarity between the embeddings of the two strings.
        If similarity > threshold (e.g., 0.8), return True, otherwise False.

        """
        # first we see if the strings are equal, that saves us a rountrip to the model
        for char in ["\n", "\r", "."]:
            first = first.replace(char, " ")
            second = second.replace(char, " ")
        first, second = first.strip(), second.strip()
        if first == second:
            return

        prompt = f"""
        Please determine if the following two statements have the same meaning.

        ## Instructions:
        - Compare the meaning of both statements.
        - If they have the same meaning, answer `True`. Otherwise, answer `False`.

        ## Statement 1:
        {first}

        ## Statement 2:
        {second}
        """

        result = self.agent.run(prompt).strip()

        try:
            is_semantically_equal = bool(strtobool(result))
        except ValueError:
            is_semantically_equal = None
        if not is_semantically_equal:
            msg = self._formatMessage(msg, "%s and %s are not semantically equal." % (safe_repr(first[0:_MAX_LENGTH]), safe_repr(second[:_MAX_LENGTH])))
            raise self.failureException(msg)

    def assertSemanticallyCorrect(self, first, second, msg = ""):

        prompt = f"""
        Please tell if the assumption is true about the text.

        ## Instructions:
        - answer only with `True` or `False`

        ## Text:
        {first}

        ## Assumption:
        {second}
        """

        result = self.agent.run(prompt).strip()
        try:
            is_semantically_correct = bool(strtobool(result))
        except ValueError:
            is_semantically_correct = None
        if not is_semantically_correct:
            msg = self._formatMessage(msg, "%s and %s are not semantically correct." % (safe_repr(first[0:_MAX_LENGTH]), safe_repr(second[:_MAX_LENGTH])))
            raise self.failureException(msg)

    def assertSemanticallyIncorrect(self, first, second, msg = ""):

        prompt = f"""
        Please tell if the assumption is true about the text.

        ## Instructions:
        - answer only with `True` or `False`

        ## Text:
        {first}

        ## Assumption:
        {second}
        """

        result = self.agent.run(prompt).strip()
        try:
            is_semantically_correct = bool(strtobool(result))
        except ValueError:
            is_semantically_correct = None
        if is_semantically_correct:
            msg = self._formatMessage(msg, "%s is semantically correct, failing assertSemanticallyIncorrect()." % (safe_repr(first[0:_MAX_LENGTH]), safe_repr(second[:_MAX_LENGTH])))
            raise self.failureException(msg)
