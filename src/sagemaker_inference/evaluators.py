import abc
import logging
from typing import List, Optional

import jmespath
from typing_extensions import Final, final

logger = logging.getLogger(__name__)


class ExpressionEvaluator(metaclass=abc.ABCMeta):
    """An evaluator to evaluate an expression with values then return boolean result for each value."""

    # Some hard-limit if we don't add any code anywhere to set the limit:
    #  - If it is defined in EndpointConfig, then no longer than 4K which is the max length of
    #    a Docker environment variable.
    #  - If it is from HTTP header, then all headers in total share the limit 4K or 8K.
    # Usually it is short, but in multi-class case, it can be a long if the caller want to check the predicted label
    # against a long list of long labels. But still 4K or 8K is too long, maybe we can start from a small number.
    __MAX_LENGTH_OF_EXPRESSION: Final[int] = 64

    @staticmethod
    def _validate_expression(expression: Optional[str] = None):
        if expression and len(expression) > ExpressionEvaluator.__MAX_LENGTH_OF_EXPRESSION:
            raise Exception(
                f"The expression exceeds the maximum allowed length {ExpressionEvaluator.__MAX_LENGTH_OF_EXPRESSION}"
            )

    def __init__(self, expression: Optional[str] = None):
        """Constructor.

        :param expression: expression from explainer config
        """
        self._validate_expression(expression)

    @abc.abstractmethod
    def evaluate_all(self, values: List, expression: Optional[str] = None) -> List[bool]:
        """Evaluate the expression for a list of values.

        :param values: The values.
        :param expression: The expression.
        :return: A list of results, one for each value.
        """


@final
class JMESPathExpressionEvaluator(ExpressionEvaluator):
    """An evaluator to evaluate a JMESPath expression (https://jmespath.org/) with values.

    The values are supposed to be a deserialized model output. For each value, the customer provided expression
    is supposed to evaluate it to a boolean result. JMESPath is a query language which support logical operators
    and a few built-in functions. It won't execute arbitrary code or do maths.
    """

    # If an expression is not provided to init method then this value is used, it evaluates all values as True.
    __DEFAULT_INIT_EXPRESSION: Final[str] = "`true`"

    def __init__(self, expression: Optional[str] = None):
        """Constructor."""
        super().__init__(expression)
        self.__expression = expression if expression else self.__DEFAULT_INIT_EXPRESSION
        try:
            self.__compiled_expression = jmespath.compile(self.__expression)
        except ValueError as e:
            # All JMESPath exceptions inherits ValueError as a base Exception
            # https://github.com/jmespath/jmespath.py/blob/develop/jmespath/exceptions.py
            error_msg = str(e)
            logger.exception(error_msg)
            raise Exception(error_msg)

    def evaluate_all(self, values: List, expression: Optional[str] = None) -> List[bool]:
        """Evaluate the expression for a list of values.

        :param values: The values deserialized from model output, each value should be a List or a Dict.
        :param expression: The expression.
        :return: A list of results, one for each value.
        """
        self._validate_expression(expression)
        try:
            if expression:
                exp = expression
                compiled_exp = jmespath.compile(expression)
            else:
                exp = self.__expression
                compiled_exp = self.__compiled_expression
        except ValueError as e:
            # All JMESPath exceptions inherits ValueError as a base Exception
            # https://github.com/jmespath/jmespath.py/blob/develop/jmespath/exceptions.py
            error_msg = str(e)
            logger.exception(error_msg)
            raise Exception(error_msg)
        # A shortcut if the expression is boolean constant
        if exp == "`true`":
            return [True] * len(values)
        if exp == "`false`":
            return [False] * len(values)
        return [self.__evaluate(exp, compiled_exp, value) for value in values]

    @staticmethod
    def __evaluate(expression: str, compiled_expression: jmespath.parser.ParsedResult, value=None) -> bool:
        """Evaluate the given expression with the value.

        :param expression: The expression string.
        :param compiled_expression: The compiled JMESPath expression.
        :param value: The variable value.
        :return: The result.
        :raise TypeError: if the evaluation result is not a boolean value.
        """
        result = compiled_expression.search(value)
        if not isinstance(result, bool):
            raise Exception(
                f"Result of expression '{expression}' with value '{value}' shall be boolean, but got {type(result)}"
            )
        return result

