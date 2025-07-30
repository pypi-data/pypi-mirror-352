import logging
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langframe._backends import LocalSessionState

import polars as pl
from langframe._constants import PREFIX_TOKENS_PER_MESSAGE
from langframe._backends.local.semantic_operators.types import LMRequestMessages
from langframe._backends.local.semantic_operators.utils import (
    convert_row_to_instruction_context,
    uppercase_instruction_placeholder,
)

logger = logging.getLogger(__name__)


class Reduce:
    SYSTEM_PROMPT = (
        "You are an AI assistant specialized in hierarchical document aggregation. "
        "You are part of a multi-stage aggregation pipeline. Your task is to synthesize a specific group of one or more documents "
        "in multiple rounds, reducing the text inputs within that group into a single coherent output that satisfies the user instruction. "
        "Document(s) within this group may be raw and structured (labeled with fields like [FIELD_1] or [FIELD_2]) or synthesized summaries. "
        "User instructions will refer to these structured fields using square brackets. "
        "Even in later stages where raw field labels are no longer present, you must continue to follow the instruction based on what those fields originally represented. "
        "Your goal is to preserve key insights, eliminate redundancy within this group, and maintain fidelity to the original instruction across all levels of aggregation for this group."
    )

    SYSTEM_MESSAGE = {
        "role": "system",
        "content": SYSTEM_PROMPT,
    }

    LEAF_INSTRUCTION_TEMPLATE = (
        "# Document Aggregation: Primary Level\n\n"
        "## Your Task\n"
        "You will be provided with one or more raw input documents from a group and a user instruction. "
        "Each document includes structured fields labeled in square brackets like [FIELD_NAME]. "
        "For example, an article document might include the fields: [TITLE], [BODY], and [TAG]. "
        "The user instruction will reference these fields directly. "
        "For instance, it might ask you to 'Summarize the articles using each article's [TITLE], [BODY], and [TAG]. "
        "Your job is to synthesize all relevant information from all input documents within the group into a single coherent response that fulfills the instruction. "
        "Preserve nuance across documents, draw meaningful connections, and avoid repetition.\n\n"
        "## User Instruction:\n"
        "{user_instruction}\n\n"
        "## Input Document(s):\n"
        "{docs_str}\n\n"
        "## Your Response:\n"
    )

    NODE_INSTRUCTION_TEMPLATE = (
        "# Document Aggregation: Higher Level Synthesis (Synthesizing Prior Summaries)\n\n"
        "## Your Task\n"
        "You are provided with a list of already-synthesized documents. Remember that these summaries were generated to capture the key information from "
        "raw documents based on the original user instruction, which used structured fields like [ARTICLE_TITLE], [ARTICLE_CONTENT], and [TAG].\n\n"
        "While the original field labels are not visible now, the essential information they represented has been preserved and condensed within these summaries. "
        "Your task is to further synthesize these summaries, ensuring that the final output remains faithful to the original instruction. "
        "Preserve nuance, remove redundancy, and ensure the result reads as a single, cohesive piece.\n\n"
        "## Original User Instruction:\n"
        "{user_instruction}\n\n"
        "## Input Summaries:\n"
        "{docs_str}\n\n"
        "## Your Response:\n"
    )

    def __init__(self, input: pl.Series, user_instruction: str, app_name: str):
        from langframe._backends import LocalSessionManager

        self.input = input
        self.user_instruction = uppercase_instruction_placeholder(user_instruction)
        session_state: LocalSessionState = (
            LocalSessionManager().get_existing_session(app_name)._session_state
        )
        self.language_model = session_state.language_model
        self.prefix_tokens = (
            self.language_model.count_tokens([self.SYSTEM_MESSAGE])
            + PREFIX_TOKENS_PER_MESSAGE
        )

    def execute(self) -> pl.Series:
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(
                executor.map(lambda x: self._reduce_group(*x), enumerate(self.input))
            )
        return pl.Series(results)

    @staticmethod
    def _format_leaf_doc(doc: dict[str, str], doc_number: int) -> str:
        return f"Document {doc_number}:\n{convert_row_to_instruction_context(doc)}"

    @staticmethod
    def _format_node_doc(doc: str, doc_number: int) -> str:
        return f"Document {doc_number}:\n{doc}"

    def _reduce_group(self, group_index: int, group: pl.Series) -> str | None:
        """
        Reduces a single group of documents hierarchically until a single output is obtained.

        Args:
            group_index: The index of the current group being processed.
            group: A Polars Series containing the documents in the current group.

        Returns:
            The final synthesized output for the group.
        """
        operation_name = f"semantic.reduce(group={group_index})"
        docs = group.to_list()
        tree_level = 0
        while len(docs) > 1 or tree_level == 0:
            messages_batch = self._build_request_messages_batch(docs, tree_level)
            if not messages_batch:
                return None
            messages_list = [msg.to_message_list() for msg in messages_batch]
            responses = self.language_model.get_completions(
                messages=messages_list, operation_name=operation_name
            )
            reduced_docs = [response.completion for response in responses]
            docs = reduced_docs
            tree_level += 1
        return docs[0]

    def _build_request_messages_batch(
        self, docs: list[dict[str, str] | str], tree_level: int
    ) -> list[LMRequestMessages] | None:
        """
        Creates batches of requests for documents in the same tree level to be processed by the language model.

        Args:
            docs: A list of documents (raw or synthesized) to be batched.
            tree_level: The current level of the aggregation tree (0 for leaf nodes).

        Returns:
            A list of Prompt objects, where each Prompt represents a batch of documents
            formatted according to the current tree level and user instruction.
        """

        def is_valid(doc):
            if not bool(doc):
                return False
            if isinstance(doc, dict):
                return all(doc.values())
            return True

        def format(doc, i):
            return (
                self._format_leaf_doc(doc, i)
                if tree_level == 0
                else self._format_node_doc(doc, i)
            )

        user_template = (
            self.LEAF_INSTRUCTION_TEMPLATE
            if tree_level == 0
            else self.NODE_INSTRUCTION_TEMPLATE
        )
        user_message_tokens = (
            self.language_model.count_tokens(user_template) + self.prefix_tokens
        )
        max_input_tokens = (
            self.language_model.max_ctx_len - self.language_model.max_completion_tokens
        )

        messages_batch: list[LMRequestMessages] = []
        request_docs: list[str] = []
        request_tokens = 0
        doc_index = 1

        for doc in docs:
            if not is_valid(doc):
                continue

            formatted = format(doc, doc_index)
            doc_tokens = self.language_model.count_tokens(formatted)

            if user_message_tokens + doc_tokens > max_input_tokens:
                raise ValueError(
                    f"sem.reduce document is too large ({doc_tokens} tokens) and exceeds the maximum allowed size. "
                    f"Please reduce the document size by either: "
                    f"1) Summarizing the content before processing, or "
                    f"2) Breaking it into smaller chunks using methods like text.recursive_character_chunk() or text.token_chunk(). "
                )

            # Flush batch if adding this doc would exceed context
            if user_message_tokens + request_tokens + doc_tokens > max_input_tokens:
                messages_batch.append(
                    self._build_request_messages(user_template, request_docs)
                )
                logger.debug(
                    f"Tree level {tree_level}: created batch with {len(request_docs)} documents."
                )
                request_docs = [formatted]
                request_tokens = doc_tokens
            else:
                request_docs.append(formatted)
                request_tokens += doc_tokens

            doc_index += 1

        if request_docs:
            messages_batch.append(
                self._build_request_messages(user_template, request_docs)
            )
            logger.debug(
                f"Tree level {tree_level}: created final batch with {len(request_docs)} documents."
            )
        if not messages_batch:
            return None
        return messages_batch

    def _build_request_messages(
        self, template: str, docs: list[str]
    ) -> LMRequestMessages:
        """
        Builds a user message for the LLM.

        Args:
            template: The instruction template to use (LEAF or NODE).
            docs: A list of formatted documents to include in the prompt.

        Returns:
            A LMRequestMessages ready to be sent to the LLM.
        """
        return LMRequestMessages(
            system=self.SYSTEM_PROMPT,
            user=template.format(
                docs_str="\n".join(docs), user_instruction=self.user_instruction
            ),
            examples=[],
        )
