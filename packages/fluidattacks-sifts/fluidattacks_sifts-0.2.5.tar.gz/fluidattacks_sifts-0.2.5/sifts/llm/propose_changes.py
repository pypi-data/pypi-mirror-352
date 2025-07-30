import logging
from typing import TYPE_CHECKING

from litellm.utils import token_counter

from sifts.llm.constants import MAX_TOKEN_COUNT_FUNCTION
from sifts.llm.router import RouterStrict

if TYPE_CHECKING:
    import litellm

LOGGER = logging.getLogger(__name__)


async def get_functional_semantics(
    *,
    router: RouterStrict,
    code: str,
) -> tuple[str | None, str | None]:
    abstract_propose_prompt: list[litellm.AllMessageValues] = [
        {
            "role": "user",
            "content": f"""{code}
What is the purpose of the function in the above code snippet? Please summarize the answer in one sentence using the following format:

"Function purpose: <summary>"

Make sure to describe the primary role of the function while considering all operations it performs,
such as encryption/decryption, logging, external method calls, data processing, or returning values.
Focus only on functional aspects, not security vulnerabilities.""",  # noqa: E501
        },
    ]
    detailed_behavior_prompt: litellm.AllMessageValues = {
        "content": f"""{code}
Please summarize the functions of the above code snippet by listing all notable functionalities it performs. Include operations such as encryption/decryption, key or IV handling, I/O processing, method calls, logging, exception handling, or any other relevant behaviors. Use the following format:

"The functions of the code snippet are:
1. <functionality>
2. <functionality>
3. <functionality>
..."

Do not evaluate security aspects or potential vulnerabilities; only describe the functional behavior of the code.""",  # noqa: E501
        "role": "user",
    }

    if token_counter(messages=abstract_propose_prompt) > MAX_TOKEN_COUNT_FUNCTION:
        return None, None
    try:
        response = await router.acompletion(
            model="nova-pro",
            messages=abstract_propose_prompt,
            caching=True,
        )
    except RuntimeError:
        LOGGER.exception("Error getting functional semantics")
        return None, None

    if not response.choices:
        return None, None
    abstract_propose = response.choices[0].message.content

    response = await router.acompletion(
        model="nova-pro",
        messages=[detailed_behavior_prompt],
        caching=True,
    )
    if not response.choices:
        return None, None
    detailed_behavior = response.choices[0].message.content
    return abstract_propose, detailed_behavior
