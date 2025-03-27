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
        self.agent.replace_inline_text(first)
        result = self.agent.run(f"Is this '{second}' the same as the following text?").strip()
        try:
            is_semantically_equal = bool(strtobool(result))
        except ValueError:
            is_semantically_equal = None
        if not is_semantically_equal:
            msg = self._formatMessage(msg, "%s and %s are not semantically equal." % (safe_repr(first[0:_MAX_LENGTH]), safe_repr(second[:_MAX_LENGTH])))
            raise self.failureException(msg)

    def assertSemanticallyCorrect(self, first, second, msg = ""):
        self.agent.replace_inline_text(first)
        result = self.agent.run(second).strip()
        try:
            is_semantically_correct = bool(strtobool(result))
        except ValueError:
            is_semantically_correct = None
        if not is_semantically_correct:
            msg = self._formatMessage(msg, "%s and %s are not semantically correct." % (safe_repr(first[0:_MAX_LENGTH]), safe_repr(second[:_MAX_LENGTH])))
            raise self.failureException(msg)

    def assertSemanticallyIncorrect(self, first, second, msg = ""):
        self.agent.replace_inline_text(first)
        result = self.agent.run(second).strip()
        try:
            is_semantically_correct = bool(strtobool(result))
        except ValueError:
            is_semantically_correct = None
        if is_semantically_correct:
            msg = self._formatMessage(msg, "%s is semantically correct, failing assertSemanticallyIncorrect()." % (safe_repr(first[0:_MAX_LENGTH]), safe_repr(second[:_MAX_LENGTH])))
            raise self.failureException(msg)
