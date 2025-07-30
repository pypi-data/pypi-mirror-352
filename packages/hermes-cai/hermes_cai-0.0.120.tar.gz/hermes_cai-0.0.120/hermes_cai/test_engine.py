"""Tests for the hermes_engine module."""
import re
import unittest
from itertools import combinations
from logging import LoggerAdapter
from unittest.mock import MagicMock, patch

from constants import TRUNCATION_STEPS_CHOICES
from contrib.lm_prefix_utils import get_tokenizer, MAX_USED_DEFINITION_LEN
from engine import StructuredPrefix, build_structured_prefix, HERE, DEFAULT_TEMPLATE_DIR
from exceptions import MessageStartIdxNotFoundError, MissingContextDataError
from structured_prefix import ChatContextMessage, ConversationFact


# Mock version of the function for testing purposes
def mock_raise_missing_context_data(key):
    del key
    # The function does nothing, it's just a placeholder for testing


def mock_get_character_priming(character, username, *, truncation_length=MAX_USED_DEFINITION_LEN):
    del character
    del username
    return [
        {
            "src": "Foo",
            "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        }
    ]


def mock_canonicalize_name(name):
    return name


MOCK_USERNAME = "jeff"
MOCK_CHARACTER = {"participant__name": "balderdash"}


class TestBuildStructuredPrefix(unittest.TestCase):
    """Tests for the build_structured_prefix function."""

    def setUp(self):
        """Initialize the test case."""
        # Mock the ContextualLogger to test logging without side effects
        self.mock_logger = MagicMock(spec=LoggerAdapter)
        self.tokenizer = get_tokenizer()
        self.encode_func = self.tokenizer.tokenize
        self.template_patcher = patch("engine.DEFAULT_TEMPLATE_DIR", "../../templates/chat_stack/default/templates")
        self.template_patcher.start()

    def test_narrator_injection(self):
        """Test that the function injects narrator name on character definition messages."""
        structured_prefix = StructuredPrefix(
            # This will require 73 tokens with current vocab.
            character_definitions=[
                "Odin: Who are you? Balderdash: I'm The Balderdash!",
                "Omar: What can you do?",
                "Balderdash: I'll tell you all my secrets... ",
                "JWT-User: but?",
                "Balderdash: but I lie about my past",
                "needle-in-haystack",
            ],
            pinned_history=[""],
            chat_history=[
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            hermes_generation_template_name="production.yml.j2",
        )

        # Execute the function under test
        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

        # Assert that the total token count is within the limit
        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        self.assertIn("narrator: needle-in-haystack", prompt_string)

    def test_audio_mode_instruction(self):
        """Test that audio mode instruction is used correctly."""
        structured_prefix = StructuredPrefix(
            # This will require 73 tokens with current vocab.
            character_definitions=[
                "Odin: Who are you? Balderdash: I'm The Balderdash!",
                "Omar: What can you do?",
                "Balderdash: I'll tell you all my secrets... ",
                "JWT-User: but?",
                "Balderdash: but I lie about my past",
            ],
            token_limit=1000,
            pinned_history=[""],
            # This will require roughly 125 tokens with current vocab.
            chat_history=[],
            hermes_generation_template_name="production_raw.yml.j2",
            chat_context_messages=[
                ChatContextMessage(
                    author="Balderdash",
                    text="filler",
                    type=1,
                    is_pinned=False,
                    is_summary=False,
                    attachments_content="",
                )
            ],
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "Character Title",
                    "description": "Character Description",
                    "definition": "Character Definition",
                    "sanitized_definition": "Character Sanitized Definition"
                },
                "user_country_code": "US",
                "persona_definition": "Persona Definition",
                "is_proactive": false
                }""",
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
        )

        stream_params = {"model_id": "heather_voice"}
        # Execute the function under test
        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            stream_params=stream_params,
            encode_func=self.encode_func,
        )
        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        self.assertTrue(prompt_string.endswith("<|AudioMode|>"))
        self.assertIn(
            "<|beginningofmessage|>Additional Instructions:\nWhenever you see the text <|AudioMode|>, switch to using spoken language that reflects a conversational style.",
            prompt_string,
        )

        # Test audio mode overrides.
        stream_params["audio_mode_token"] = "audio_mode_token"  # noqa: S105
        stream_params["audio_mode_instruction_override"] = (
            "If you see the text audio_mode_token use a more conversational style."
        )
        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            stream_params=stream_params,
            encode_func=self.encode_func,
        )

        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        self.assertTrue(prompt_string.endswith("audio_mode_token"))
        self.assertIn(
            "<|beginningofmessage|>If you see the text audio_mode_token use a more conversational style.",
            prompt_string,
        )
        self.assertNotIn(
            "<|beginningofmessage|>Additional Instructions:\nWhenever you see the text <|AudioMode|>, switch to using spoken language that reflects a conversational style.",
            prompt_string,
        )

        # Test audio mode disabled.
        stream_params["model_id"] = "heather"
        stream_params.pop("audio_mode_token")
        stream_params.pop("audio_mode_instruction_override")
        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            stream_params=stream_params,
            encode_func=self.encode_func,
        )

        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        self.assertNotIn("audio_mode_token", prompt_string)
        self.assertNotIn("<|AudioMode|>", prompt_string)
        self.assertNotIn(
            "<|beginningofmessage|>If you see the text audio_mode_token use a more conversational style.",
            prompt_string,
        )
        self.assertNotIn(
            "<|beginningofmessage|>Additional Instructions:\nWhenever you see the text <|AudioMode|>, switch to using spoken language that reflects a conversational style.",
            prompt_string,
        )

    def test_below_token_limit(self):
        """Test that the function does not truncate messages when the token limit is not exceeded."""
        structured_prefix = StructuredPrefix(
            # This will require 73 tokens with current vocab.
            character_definitions=[
                "Odin: Who are you? Balderdash: I'm The Balderdash!",
                "Omar: What can you do?",
                "Balderdash: I'll tell you all my secrets... ",
                "JWT-User: but?",
                "Balderdash: but I lie about my past",
            ],
            pinned_history=["First pinned message."],
            # This will require roughly 125 tokens with current vocab.
            chat_history=[
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            hermes_generation_template_name="production.yml.j2",
        )

        # Execute the function under test
        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )
        context_tokens = result["tokenized_context"].tokens

        # Assert that the total token count is within the limit
        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        self.assertGreaterEqual(len(context_tokens), 100)
        self.assertIn(
            "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            prompt_string,
        )

    def test_above_token_limit(self):
        """Test that the function truncates messages when the token limit is exceeded."""
        structured_prefix = StructuredPrefix(
            # This will require 73 tokens with current vocab.
            character_definitions=[
                "Odin: Who are you? Balderdash: I'm The Balderdash!",
                "Omar: What can you do?",
                "Balderdash: I'll tell you all my secrets... ",
                "JWT-User: but?",
                "Balderdash: but I lie about my past",
            ],
            pinned_history=[""],
            # This will require roughly 125 tokens with current vocab.
            chat_history=[
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            token_limit=100,
            hermes_generation_template_name="production.yml.j2",
        )

        # Assert that the total token count is within the limit
        _ = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

    def test_pretruncation_step(self):
        """Test the pretruncation step truncates the appropriate messages."""
        chat_context_messages = [
            ChatContextMessage(
                author="Balderdash",
                text="filler",
                type=1,
                is_pinned=False,
                is_summary=False,
                attachments_content="",
            )
        ] * 200
        chat_context_messages[0] = ChatContextMessage(
            author="Balderdash",
            text="This message should be pretruncated.",
            type=1,
            is_pinned=False,
            is_summary=False,
            attachments_content="",
        )
        chat_context_messages.append(
            ChatContextMessage(
                author="Balderdash",
                text="This message should NOT be pretruncated.",
                type=1,
                is_pinned=False,
                is_summary=False,
                attachments_content="",
            )
        )
        structured_prefix = StructuredPrefix(
            # This will require 73 tokens with current vocab.
            character_definitions=[
                "Odin: Who are you? Balderdash: I'm The Balderdash!",
                "Omar: What can you do?",
                "Balderdash: I'll tell you all my secrets... ",
                "JWT-User: but?",
                "Balderdash: but I lie about my past",
            ],
            token_limit=1000,
            pinned_history=[""],
            # This will require roughly 125 tokens with current vocab.
            chat_history=[],
            hermes_generation_template_name="production_raw.yml.j2",
            chat_context_messages=chat_context_messages,
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "Character Title",
                    "description": "Character Description",
                    "definition": "Character Definition",
                    "sanitized_definition": "Character Sanitized Definition"
                },
                "user_country_code": "US",
                "persona_definition": "Persona Definition",
                "is_proactive": false
                }""",
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
        )

        # Execute the function under test
        result = build_structured_prefix(
            self.mock_logger,
            structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

        # Assert that the total token count is within the limit
        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        self.assertIn("This message should NOT be pretruncated", prompt_string)
        self.assertNotIn("This message should be pretruncated", prompt_string)

    def test_truncation_steps(self):
        """Test that the function truncates messages when the token limit is exceeded."""
        # Total tokens is 1285 - don't change the inputs!
        chat_history = ["Name: Lorem ipsum dolor sit"] * 105
        structured_prefix = StructuredPrefix(
            # This will require 73 tokens with current vocab.
            character_definitions=[
                "Odin: Who are you? Balderdash: I'm The Balderdash!",
                "Omar: What can you do?",
                "Balderdash: I'll tell you all my secrets... ",
                "JWT-User: but?",
                "Balderdash: but I lie about my past",
            ],
            pinned_history=[],
            # Each message is exactly 10 tokens (with bom/eom) therefore truncation will happen in multiples of 10.
            chat_history=chat_history,
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            token_limit=1024,
            hermes_generation_template_name="production.yml.j2",
        )

        expected_token_counts = [1023, 933, 883, 633, 383, 133, 83, 83]
        for truncation_step, expectation in zip(
            [1, 100, *TRUNCATION_STEPS_CHOICES], expected_token_counts, strict=False
        ):
            result = build_structured_prefix(
                logger=self.mock_logger,
                structured_prefix=structured_prefix,
                truncation_step=truncation_step,
                encode_func=self.encode_func,
            )
            self.assertEqual(len(result["tokenized_context"].tokens), expectation)

        # With empty character definitions.
        structured_prefix.character_definitions = []
        expected_token_counts = [1018, 958, 808, 558, 308, 58, 18, 18]
        for truncation_step, expectation in zip(
            [1, 100, *TRUNCATION_STEPS_CHOICES], expected_token_counts, strict=False
        ):
            result = build_structured_prefix(
                logger=self.mock_logger,
                structured_prefix=structured_prefix,
                truncation_step=truncation_step,
                encode_func=self.encode_func,
            )
            self.assertEqual(len(result["tokenized_context"].tokens), expectation)

    def test_include_pins(self):
        """Test that pinned history is included in the tokenized context."""
        structured_prefix = StructuredPrefix(
            # This will require 73 tokens with current vocab.
            character_definitions=[
                "Odin: Who are you? Balderdash: I'm The Balderdash!",
                "Omar: What can you do?",
                "Balderdash: I'll tell you all my secrets... ",
                "JWT-User: but? Balderdash: but I lie about my past",
            ],
            # This will require roughly 125 tokens with current vocab.
            pinned_history=[
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            ],
            # This will require roughly 125 tokens with current vocab.
            chat_history=[
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            hermes_generation_template_name="production.yml.j2",
        )

        # Execute the function under test
        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

        context_tokens = result["tokenized_context"].tokens
        # Assert that the total token count is within the limit
        self.assertGreater(
            len(context_tokens), 300
        )  # char_def and chat_history takes approx 210

    def test_persona_injection(self):
        """Test that persona injection WAI."""
        structured_prefix = StructuredPrefix(
            # This will require 73 tokens with current vocab.
            character_definitions=[
                "Odin: Who are you? Balderdash: I'm The Balderdash!",
                "Omar: What can you do?",
                "Balderdash: I'll tell you all my secrets... ",
                "JWT-User: but? Balderdash: but I lie about my past",
                'jeff\'s self-intro is "name: Jeff\neye color: redname: Jeff"',
            ],
            # This will require roughly 125 tokens with current vocab.
            pinned_history=[
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            ],
            # This will require roughly 125 tokens with current vocab.
            chat_history=[
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            hermes_generation_template_name="production.yml.j2",
        )

        # Execute the function under test
        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

        context_tokens = result["tokenized_context"].tokens
        # Assert that the total token count is within the limit
        self.assertGreater(
            len(context_tokens), 300
        )  # char_def and chat_history takes approx 210

    def test_return_keys(self):
        """Test that the return payload contains expected keys."""
        structured_prefix = StructuredPrefix(
            # This will require 73 tokens with current vocab.
            character_definitions=[
                "Odin: Who are you? Balderdash: I'm The Balderdash!",
                "Omar: What can you do?",
                "Balderdash: I'll tell you all my secrets... ",
                "JWT-User: but? Balderdash: but I lie about my past",
                'jeff\'s self-intro is "name: Jeff\neye color: redname: Jeff"',
            ],
            # This will require roughly 125 tokens with current vocab.
            pinned_history=[
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            ],
            # This will require roughly 125 tokens with current vocab.
            chat_history=[
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            hermes_generation_template_name="production.yml.j2",
        )

        # Execute the function under test
        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )
        for k in [
            "character_definitions",
            "chat_history",
            "chat_hist_global_index",
            "reply_prompt",
            "space_added",
            "token_limit",
            "tokenized_context",
            "timestamp",
        ]:
            self.assertIn(k, result)

    def test_edge_cases(self):
        """Test that edge cases are handled correctly."""
        # Missing character definitions still passes valid prompt regex.
        structured_prefix = StructuredPrefix(
            # This will require 73 tokens with current vocab.
            character_definitions=[],
            # This will require roughly 125 tokens with current vocab.
            pinned_history=[
                "Jeff: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Balderdash: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Jeff: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                "Balderdash: Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                "Balderdash: Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            ],
            # This will require roughly 125 tokens with current vocab.
            chat_history=[
                "Jeff: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Balderdash: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Jeff: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                "Balderdash: Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                "Jeff: Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            hermes_generation_template_name="production.yml.j2",
        )

        _ = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

        # Missing pinned history still passes valid prompt regex.
        structured_prefix = StructuredPrefix(
            character_definitions=[],
            pinned_history=[],
            # This will require roughly 125 tokens with current vocab.
            chat_history=[
                "Balerdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            hermes_generation_template_name="production.yml.j2",
        )

        _ = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

        # Missing chat history fails with not message start found.
        with self.assertRaises(MessageStartIdxNotFoundError):
            structured_prefix = StructuredPrefix(
                character_definitions=[],
                pinned_history=[],
                chat_history=[],
                reply_prompt="Balderdash:",
                timestamp="2024 04 23 Tuesday 19 07",
                hermes_generation_template_name="production.yml.j2",
            )

            _ = build_structured_prefix(
                logger=self.mock_logger,
                structured_prefix=structured_prefix,
                truncation_step=1,
                encode_func=self.encode_func,
            )

    def test_whitespace_injection(self):
        """Test that whitespace is injected where appropriate e.g. `<|space|>`."""
        structured_prefix = StructuredPrefix(
            # This will require 73 tokens with current vocab.
            character_definitions=[
                "Odin: Who are you? Balderdash: I'm The Balderdash!",
                "Omar: What can you do?",
                "Balderdash: I'll tell you all my secrets... ",
                "JWT-User: but? Balderdash: but I lie about my past",
                'jeff\'s self-intro is "name: Jeff\neye color: redname: Jeff"',
            ],
            # This will require roughly 125 tokens with current vocab.
            pinned_history=[
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            ],
            # This will require roughly 125 tokens with current vocab.
            chat_history=[
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            hermes_generation_template_name="production.yml.j2",
        )

        # Execute the function under test
        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )
        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        self.assertIn("2024 04 23 Tuesday 19 07 Odin", prompt_string)

    def test_raw_prompt_data(self):
        """Test that raw prompt data is interpolated correctly."""
        structured_prefix = StructuredPrefix(
            character_definitions=[
                "Odin: Who are you? Balderdash: I'm The Balderdash!",
                "Omar: What can you do?",
                "Balderdash: I'll tell you all my secrets... ",
                "JWT-User: but? Balderdash: but I lie about my past",
                'jeff\'s self-intro is "name: Jeff\neye color: redname: Jeff"',
            ],
            chat_history=[
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            reply_prompt="Balderdash:",
            hermes_generation_template_name="test.yml.j2",
            timestamp="2024 04 23 Tuesday 19 07",
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "Character Title",
                    "description": "Character Description",
                    "definition": "Character Definition",
                    "sanitized_definition": "Character Sanitized Definition"
                },
                "user_country_code": "US",
                "persona_definition": "Persona Definition",
                "is_proactive": false
                }""",
        )

        # Execute the function under test
        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )
        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)

        for needle in [
            "ONE_ON_ONE",
            "Balderdash",
            "Character Title",
            "Character Description",
            "Character Definition",
            "Character Sanitized Definition",
            "User country code is: US",
            "Persona Definition",
        ]:
            self.assertIn(
                needle,
                prompt_string,
            )

    def test_conversation_facts(self):
        """Test that conversation facts is interpolated correctly."""
        conversation_facts = {
            "participant A": [
                ConversationFact(category="category A", value="value A"),
                ConversationFact(category="category B", value="value B"),
            ],
            "participant B": [
                ConversationFact(category="category C", value="value C"),
                ConversationFact(category="category D", value="value D"),
            ]
        }
        structured_prefix = StructuredPrefix(
            character_definitions=[
                "Odin: Who are you? Balderdash: I'm The Balderdash!",
                "Omar: What can you do?",
                "Balderdash: I'll tell you all my secrets... ",
                "JWT-User: but? Balderdash: but I lie about my past",
                'jeff\'s self-intro is "name: Jeff\neye color: redname: Jeff"',
            ],
            chat_history=[
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            reply_prompt="Balderdash:",
            hermes_generation_template_name="test.yml.j2",
            timestamp="2024 04 23 Tuesday 19 07",
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "Character Title",
                    "description": "Character Description",
                    "definition": "Character Definition",
                    "sanitized_definition": "Character Sanitized Definition"
                },
                "user_country_code": "US",
                "persona_definition": "Persona Definition",
                "is_proactive": false
                }""",
            conversation_facts=conversation_facts,
        )

        # Execute the function under test
        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )
        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        # extract substring between START_FACTS and END_FACTS
        match = re.search(r"START_FACTS(.*?)END_FACTS", prompt_string, re.DOTALL)
        self.assertTrue(match, "FACTS not found in prompt")
        facts = match.group(1)
        lines = []
        for line in facts.splitlines():
            l = line.strip()
            if l:
                lines.append(line.strip())
        got = "\n".join(lines)
        lines = []
        for participant, facts in conversation_facts.items():
            lines.append(f"PARTICIPANT: {participant}")
            for fact in facts:
                lines.append(f"- {fact.category}: {fact.value}")
        want = "\n".join(lines)
        self.assertEqual(got, want, f"Incorrect facts {got=} {want=}")

    def test_template_params(self):
        """Test template params."""
        chat_history = [
            "Message 1",
            "Message 2",
            "Message 3",
            "Message 4",
            "Message 5",
        ]
        max_chat_history = 2
        structured_prefix = StructuredPrefix(
            character_definitions=[
                "Odin: Who are you? Balderdash: I'm The Balderdash!",
                "Omar: What can you do?",
                "Balderdash: I'll tell you all my secrets... ",
                "JWT-User: but? Balderdash: but I lie about my past",
                'jeff\'s self-intro is "name: Jeff\neye color: redname: Jeff"',
            ],
            chat_history=chat_history,
            reply_prompt="Balderdash:",
            hermes_generation_template_name="test.yml.j2",
            timestamp="2024 04 23 Tuesday 19 07",
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "Character Title",
                    "description": "Character Description",
                    "definition": "Character Definition",
                    "sanitized_definition": "Character Sanitized Definition"
                },
                "user_country_code": "US",
                "persona_definition": "Persona Definition",
                "is_proactive": false
                }""",
        )
        template_params = {
            "max_chat_history": max_chat_history,
        }
        # Execute the function under test
        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
            template_params=template_params,
        )
        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        # extract substring between START_TEMPLATE_PARAMS and END_TEMPLATE_PARAMS
        match = re.search(r"START_TEMPLATE_PARAMS(.*?)END_TEMPLATE_PARAMS", prompt_string, re.DOTALL)
        self.assertTrue(match, "Template params not found in prompt")
        msgs = match.group(1)
        lines = []
        for line in msgs.splitlines():
            l = line.strip()
            if l:
                lines.append(line.strip())
        got = "\n".join(lines)
        want = "\n".join(chat_history[-max_chat_history:])
        self.assertEqual(got, want, f"Messages doesn't match {got=} {want=}")

    def _build_prompts_with_templates(
        self, structured_prefix: StructuredPrefix, template_names: list[str]
    ) -> dict[str, str]:
        if not template_names:
            raise ValueError("At least one template name must be provided.")

        retval = {}
        for template_name in template_names:
            structured_prefix.hermes_generation_template_name = template_name
            result = build_structured_prefix(
                logger=self.mock_logger,
                structured_prefix=structured_prefix,
                truncation_step=1,
                encode_func=self.encode_func,
            )
            retval[template_name] = self.tokenizer.detokenize(
                result["tokenized_context"].tokens
            )
        return retval

    def _compare_prompt_map(self, prompt_map: dict[str, str]):
        self.maxDiff = None
        for (template_name_a, prompt_a), (template_name_b, prompt_b) in combinations(
            prompt_map.items(), 2
        ):
            self.assertEqual(
                prompt_a,
                prompt_b,
                f"Prompts do not match: \n\n\t({template_name_a=}, {prompt_a=})\n\n\t({template_name_b}, {prompt_b=})",
            )

    def test_production_template_parity(self):
        """Test that the production template is equivalent to the raw template."""
        # Full of data.
        base_structured_prefix = StructuredPrefix(
            character_definitions=[
                "Balderdash: Character Title - Character Description",
                "narrator: Jeff's self-intro is Persona Definition",
                "Balderdash: Character Sanitized Definition",
            ],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            pinned_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "Character Title",
                    "description": "Character Description",
                    "definition": "Balderdash: Character Definition",
                    "sanitized_definition": "Balderdash: Character Sanitized Definition"
                },
                "username": "Jeff",
                "user_country_code": "US",
                "persona_definition": "Persona Definition",
                "is_proactive": false
                }""",
            chat_context_messages_str="""[
                {
                    "author": "Balderdash", "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "type": 2, "is_pinned": true
                },
                {
                    "author": "Jeff", "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.", "type": 1, "is_pinned": false
                },
                {
                    "author": "Balderdash", "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.", "type": 2, "is_pinned": false
                }
            ]""",
        )
        template_names = ["production_raw.yml.j2"]

        prompt_map = self._build_prompts_with_templates(
            structured_prefix=base_structured_prefix.model_copy(),
            template_names=template_names,
        )
        self._compare_prompt_map(prompt_map=prompt_map)

        # Missing character definition messages.
        base_structured_prefix = StructuredPrefix(
            character_definitions=[],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            pinned_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "",
                    "description": "",
                    "definition": "",
                    "sanitized_definition": ""
                },
                "username": "Jeff",
                "user_country_code": "US",
                "persona_definition": "",
                "is_proactive": false
                }""",
            chat_context_messages_str="""[
                {
                    "author": "Balderdash", "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "type": 2, "is_pinned": true
                },
                {
                    "author": "Jeff", "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.", "type": 1, "is_pinned": false
                },
                {
                    "author": "Balderdash", "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.", "type": 2, "is_pinned": false
                }
            ]""",
        )
        prompt_map = self._build_prompts_with_templates(
            structured_prefix=base_structured_prefix.model_copy(),
            template_names=template_names,
        )
        self._compare_prompt_map(prompt_map=prompt_map)

        # Only character title.
        base_structured_prefix = StructuredPrefix(
            character_definitions=["Balderdash: Character Title"],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "Character Title",
                    "description": "",
                    "definition": "",
                    "sanitized_definition": ""
                },
                "username": "Jeff",
                "user_country_code": "US",
                "persona_definition": "",
                "is_proactive": false
                }""",
            chat_context_messages_str="""[
                {
                    "author": "Balderdash", "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "type": 2, "is_pinned": false
                },
                {
                    "author": "Jeff", "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.", "type": 1, "is_pinned": false
                },
                {
                    "author": "Balderdash", "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.", "type": 2, "is_pinned": false
                }
            ]""",
        )
        prompt_map = self._build_prompts_with_templates(
            structured_prefix=base_structured_prefix.model_copy(),
            template_names=template_names,
        )
        self._compare_prompt_map(prompt_map=prompt_map)

        base_structured_prefix = StructuredPrefix(
            character_definitions=["narrator: Jeff's self-intro is Persona definition"],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "",
                    "description": "",
                    "definition": "",
                    "sanitized_definition": ""
                },
                "username": "Jeff",
                "user_country_code": "US",
                "persona_definition": "Persona definition",
                "is_proactive": false
                }""",
            chat_context_messages_str="""[
                {
                    "author": "Balderdash", "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "type": 2, "is_pinned": true
                },
                {
                    "author": "Jeff", "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.", "type": 1, "is_pinned": false
                },
                {
                    "author": "Balderdash", "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.", "type": 2, "is_pinned": false
                }
            ]""",
        )
        prompt_map = self._build_prompts_with_templates(
            structured_prefix=base_structured_prefix.model_copy(),
            template_names=template_names,
        )
        self._compare_prompt_map(prompt_map=prompt_map)

    def test_names(self):
        """Tests that a default value is used for empty names."""
        base_structured_prefix = StructuredPrefix(
            character_definitions=[],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            reply_prompt="Balderdash:",
            hermes_generation_template_name="production_raw.yml.j2",
            timestamp="2024 04 23 Tuesday 19 07",
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "A great Character",
                    "description": "Tongue in cheek.",
                    "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                    "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
                },
                "username": "",
                "user_country_code": "US",
                "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
                "is_proactive": false
            }""",
            chat_context_messages_str="""[
                {
                    "author": "Balderdash", "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "type": 2, "is_pinned": true
                },
                {
                    "author": "Jeff", "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.", "type": 1, "is_pinned": false
                },
                {
                    "author": "Balderdash", "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.", "type": 2, "is_pinned": false
                }
            ]""",
        )
        # Will fail template validation on empty username.
        _ = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=base_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

        # Test for both templates.
        base_structured_prefix.hermes_generation_template_name = "production.yml.j2"
        _ = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=base_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

        # Allow username to have underscores.
        base_structured_prefix.character_definitions = ["User_: Who are you?"]
        _ = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=base_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

        # Allow any unicode name.
        base_structured_prefix.character_definitions = ["Usér_: Who are you?"]
        _ = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=base_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

        # Allow any unicode name.
        base_structured_prefix.character_definitions = ["Хван-Хенджин: Who are you?"]
        _ = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=base_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

        # Allow any unicode name.
        base_structured_prefix.character_definitions = ["李小龙: Who are you?"]
        _ = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=base_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

    def test_production_raw_template(self):
        """Test the basic mechanics of the raw template."""
        base_structured_prefix = StructuredPrefix(
            character_definitions=[],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            reply_prompt="Balderdash:",
            hermes_generation_template_name="production_raw.yml.j2",
            timestamp="2024 04 23 Tuesday 19 07",
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "A great Character",
                    "description": "Tongue in cheek.",
                    "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                    "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
                },
                "username": "Jeff",
                "user_country_code": "US",
                "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
                "is_proactive": false
            }""",
            chat_context_messages_str="""[
                {
                    "author": "Balderdash", "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "type": 2, "is_pinned": true
                },
                {
                    "author": "Jeff", "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.", "type": 1, "is_pinned": false
                },
                {
                    "author": "Balderdash", "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.", "type": 2, "is_pinned": false
                }
            ]""",
        )

        # Tests that persona is spliced in correctly after first character definition message (title and description).
        structured_prefix = base_structured_prefix.model_copy()
        structured_prefix.raw_prompt_data_str = """{
            "chat_type": "ONE_ON_ONE",
            "character": {
                "participant__name": "Balderdash",
                "title": "A great Character",
                "description": "Tongue in cheek.",
                "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
            },
            "username": "Jeff",
            "user_country_code": "US",
            "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
            "is_proactive": false
        }"""

        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )
        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        self.assertRegex(
            prompt_string,
            r"^.*Balderdash: A great Character - Tongue in cheek.*name: Jeff\neye color: red\nname: Jeff.*Jeff: Who are you?<|endofmessage|><|beginningofmessage|>\nBalderdash: I'm The Balderdash!.*$",
        )

        # Tests that it is resilient to no character definition messages.
        structured_prefix = base_structured_prefix.model_copy()
        structured_prefix.raw_prompt_data_str = """{
            "chat_type": "ONE_ON_ONE",
            "character": {
                "participant__name": "Balderdash",
                "title": "",
                "description": "",
                "definition": "",
                "sanitized_definition": ""
            },
            "username": "Jeff",
            "user_country_code": "US",
            "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
            "is_proactive": false
        }"""

        _ = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

        _ = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )

        # Tests that persona exists if character definition is empty.
        structured_prefix = base_structured_prefix.model_copy()
        structured_prefix.raw_prompt_data_str = """{
            "chat_type": "ONE_ON_ONE",
            "character": {
                "participant__name": "Balderdash",
                "title": "A great Character",
                "description": "Tongue in cheek.",
                "definition": "",
                "sanitized_definition": ""
            },
            "username": "Jeff",
            "user_country_code": "US",
            "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
            "is_proactive": false
        }"""

        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )
        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        self.assertRegex(
            prompt_string,
            r"^.*Balderdash: A great Character - Tongue in cheek.*name: Jeff\neye color: red\nname: Jeff.*$",
        )

        # Tests that raises on missing character from prompt data.
        structured_prefix = base_structured_prefix.model_copy()
        structured_prefix.raw_prompt_data_str = """{
            "chat_type": "ONE_ON_ONE",
            "username": "Jeff",
            "user_country_code": "US",
            "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
            "is_proactive": false
        }"""

        with self.assertRaisesRegex(MissingContextDataError, r".*character.*"):
            _ = build_structured_prefix(
                logger=self.mock_logger,
                structured_prefix=structured_prefix,
                truncation_step=1,
                encode_func=self.encode_func,
            )

        # Tests that raises on missing chat context data.
        structured_prefix = base_structured_prefix.model_copy()
        structured_prefix.chat_context_messages_str = ""

        with self.assertRaises(MessageStartIdxNotFoundError):
            _ = build_structured_prefix(
                logger=self.mock_logger,
                structured_prefix=structured_prefix,
                truncation_step=1,
                encode_func=self.encode_func,
            )

        # Tests that pins are correctly interleaved.
        structured_prefix = base_structured_prefix.model_copy()
        structured_prefix.chat_context_messages_str = """[
                {
                    "author": "Balderdash", "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "type": 2, "is_pinned": true
                },
                {
                    "author": "Jeff", "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.", "type": 1, "is_pinned": false
                },
                {
                    "author": "Balderdash", "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.", "type": 2, "is_pinned": true
                }
            ]"""

        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )
        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        # One after first pin and one at the end
        self.assertEqual(prompt_string.count("narrator: [some messages omitted]"), 2)

        # Tests that pins are not interleaved.
        structured_prefix = base_structured_prefix.model_copy()
        structured_prefix.chat_context_messages_str = """[
                {
                    "author": "Balderdash", "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "type": 2, "is_pinned": true
                },
                {
                    "author": "Jeff", "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.", "type": 1, "is_pinned": true
                },
                {
                    "author": "Balderdash", "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.", "type": 2, "is_pinned": true
                }
            ]"""

        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )
        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)
        # Only one at the end
        self.assertEqual(prompt_string.count("narrator: [some messages omitted]"), 1)

    def test_production_raw_template_configs(self):
        shared_params = {
            "character_definitions": [],
            "chat_history": [
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            "reply_prompt": "Balderdash:",
            "timestamp": "2024 04 23 Tuesday 19 07",
            "chat_context_messages_str": """[
                {
                    "author": "Balderdash", "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "type": 2, "is_pinned": true, "is_safety_truncated": true
                },
                {
                    "author": "Jeff", "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.", "type": 1, "is_pinned": false, "is_safety_truncated": true
                },
                {
                    "author": "Balderdash", "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.", "type": 2, "is_pinned": false
                }
            ]""",
        }
        minors_raw_prompt_data_str = """{
            "chat_type": "ONE_ON_ONE",
            "character": {
                "participant__name": "Balderdash",
                "title": "A great Character",
                "description": "Tongue in cheek.",
                "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
            },
            "username": "Jeff",
            "user_country_code": "US",
            "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
            "is_proactive": false,
            "config": {
                "should_remove_safety_truncated_messages": true
            }
        }"""
        minors_structured_prefix = StructuredPrefix(
            **shared_params, raw_prompt_data_str=minors_raw_prompt_data_str
        )
        minors_result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=minors_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )
        # Assert that safety truncated messages (both pinned and unpinned) are omitted.
        minors_prompt_string = self.tokenizer.detokenize(
            minors_result["tokenized_context"].tokens
        )
        self.assertNotIn(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            minors_prompt_string,
        )
        self.assertNotIn(
            "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            minors_prompt_string,
        )

        standard_raw_prompt_data_str = """{
            "chat_type": "ONE_ON_ONE",
            "character": {
                "participant__name": "Balderdash",
                "title": "A great Character",
                "description": "Tongue in cheek.",
                "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
            },
            "username": "Jeff",
            "user_country_code": "US",
            "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
            "is_proactive": false
        }"""
        standard_structured_prefix = StructuredPrefix(
            **shared_params, raw_prompt_data_str=standard_raw_prompt_data_str
        )
        standard_result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=standard_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
        )
        # Assert that safety truncated messages (both pinned and unpinned) are still in the prompt.
        standard_prompt_string = self.tokenizer.detokenize(
            standard_result["tokenized_context"].tokens
        )
        self.assertIn(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            standard_prompt_string,
        )
        self.assertIn(
            "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            standard_prompt_string,
        )

    def test_production_raw_template_with_attachments_content(self):
        """Test the production raw template prompt with attachments content."""
        base_structured_prefix = StructuredPrefix(
            character_definitions=[],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "A great Character",
                    "description": "Tongue in cheek.",
                    "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                    "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
                },
                "username": "Jeff",
                "user_country_code": "US",
                "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
                "is_proactive": false
            }""",
            chat_context_messages_str="""[
                {
                    "author": "Balderdash",
                    "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    "type": 2,
                    "is_pinned": true
                },
                {
                    "author": "Jeff",
                    "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "type": 1,
                    "is_pinned": false,
                    "attachments_content": "only one attachment"
                },
                {
                    "author": "Balderdash",
                    "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                    "type": 2,
                    "is_pinned": false,
                    "attachments_content": "first attachment, second attachment"
                },
                {
                    "author": "Jeff",
                    "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "type": 1,
                    "is_pinned": false,
                    "is_summary": true,
                    "attachments_content": null
                }
            ]""",
        )
        res = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=base_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
            use_gcs_template=True,
            gcs_template_path="chat_stack/default/templates/production_raw.yml.j2",
        )
        # The attachments content should be injected into the prompt.
        self.assertIn(
            "narrator: You're looking at the contents shared by Jeff: only one attachment",
            self.tokenizer.detokenize(res["tokenized_context"].tokens),
        )
        self.assertIn(
            "narrator: You're looking at the contents shared by Balderdash: first attachment, second attachment",
            self.tokenizer.detokenize(res["tokenized_context"].tokens),
        )
        print(self.tokenizer.detokenize(res["tokenized_context"].tokens))


        self.assertNotIn(
            "should not be injected",
            self.tokenizer.detokenize(res["tokenized_context"].tokens),
        )

        prefix_no_attachments = StructuredPrefix(
            character_definitions=[],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Linda: New message with no attachments",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "A great Character",
                    "description": "Tongue in cheek.",
                    "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                    "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
                },
                "username": "Linda",
                "user_country_code": "US",
                "persona_definition": "name: Linda\\neye color: red\\nname: Linda",
                "is_proactive": false
            }""",
            chat_context_messages_str="""[
                {
                    "author": "Balderdash", "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "type": 2, "is_pinned": true, "is_summary": true, "attachments_content_list": ["should not be injected"]
                },
                {
                    "author": "Linda", "text": "New message with no attachments", "type": 1, "is_pinned": false
                }
            ]""",
        )
        res_no_attachments = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=prefix_no_attachments,
            truncation_step=1,
            encode_func=self.encode_func,
            use_gcs_template=True,
            gcs_template_path="chat_stack/chat_attachment_exp/templates/production_raw.yml.j2",
        )
        # If there is no attachments content, the narrator message should not be injected.
        self.assertNotIn(
            "narrator: Jeff had shared",
            self.tokenizer.detokenize(res_no_attachments["tokenized_context"].tokens),
        )

    def test_production_raw_template_with_custom_attachments_prompt(self):
        """Test the production raw template prompt with custom attachments prompt."""
        base_structured_prefix = StructuredPrefix(
            character_definitions=[],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "A great Character",
                    "description": "Tongue in cheek.",
                    "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                    "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
                },
                "username": "Jeff",
                "user_country_code": "US",
                "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
                "is_proactive": false
            }""",
            chat_context_messages_str="""[
                {
                    "author": "Balderdash",
                    "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    "type": 2,
                    "is_pinned": true
                },
                {
                    "author": "Jeff",
                    "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "type": 1,
                    "is_pinned": false,
                    "attachments_content": "image description",
                    "attachments_type": "TYPE_IMAGE"
                },
                {
                    "author": "Balderdash",
                    "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                    "type": 2,
                    "is_pinned": false,
                    "attachments_content": "sticker description",
                    "attachments_type": "TYPE_STICKER"
                },
                {
                    "author": "Jeff",
                    "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "type": 1,
                    "is_pinned": false,
                    "is_summary": true,
                    "attachments_content": "image description without type"
                }
            ]""",
        )
        template_params = {
            "image_prompt_format_prefix": "narrator: prefix ",
            "image_prompt_format_suffix": " shared an image ",
            "sticker_prompt_format_prefix": "",
            "sticker_prompt_format_suffix": ": gifted a sticker ",
        }
        res = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=base_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
            use_gcs_template=False,
            template_params=template_params,
        )
        result = self.tokenizer.detokenize(res["tokenized_context"].tokens)
        # The attachments content should be injected into the prompt.
        self.assertIn(
            "narrator: prefix Jeff shared an image image description",
            result,
        )
        self.assertIn(
            "Balderdash: gifted a sticker sticker description",
            result,
        )
        self.assertIn(
            "narrator: prefix Jeff shared an image image description without type",
            result,
        )

    def test_vllm_mistral_template(self):
        """Test vllm mistral template prompt."""
        base_structured_prefix = StructuredPrefix(
            character_definitions=[],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            hermes_generation_template_name=str(HERE/".."/".."/DEFAULT_TEMPLATE_DIR/"chat_stack/vllm_mistral/templates/production_raw.yml.j2"),
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "A great Character",
                    "description": "Tongue in cheek.",
                    "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                    "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
                },
                "username": "Jeff",
                "user_country_code": "US",
                "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
                "is_proactive": false
            }""",
            chat_context_messages_str="""[
                {
                    "author": "Balderdash",
                    "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    "type": 2,
                    "is_pinned": true
                },
                {
                    "author": "Jeff",
                    "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "type": 1,
                    "is_pinned": false,
                    "attachments_content": "image description",
                    "attachments_type": "TYPE_IMAGE"
                },
                {
                    "author": "Balderdash",
                    "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                    "type": 2,
                    "is_pinned": false,
                    "attachments_content": "sticker description",
                    "attachments_type": "TYPE_STICKER"
                },
                {
                    "author": "Jeff",
                    "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "type": 1,
                    "is_pinned": false,
                    "is_summary": true,
                    "attachments_content": "image description without type"
                }
            ]""",
        )
        template_params = {
            "image_prompt_format_prefix": "narrator: prefix ",
            "image_prompt_format_suffix": " shared an image ",
            "sticker_prompt_format_prefix": "",
            "sticker_prompt_format_suffix": ": gifted a sticker ",
        }
        res = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=base_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
            use_gcs_template=False,
            template_params=template_params,
        )
        self.assertEqual(len(res["prompt"].messages), 6)

    def test_special_token_overrides_all_overriden(self):
        """Test special token overrides."""
        base_structured_prefix = StructuredPrefix(
            character_definitions=[],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            raw_prompt_data_str="""{
                        "chat_type": "ONE_ON_ONE",
                        "character": {
                            "participant__name": "Balderdash",
                            "title": "A great Character",
                            "description": "Tongue in cheek.",
                            "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                            "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
                        },
                        "username": "Jeff",
                        "user_country_code": "US",
                        "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
                        "is_proactive": false
                    }""",
            chat_context_messages_str="""[
                        {
                            "author": "Balderdash",
                            "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                            "type": 2,
                            "is_pinned": true
                        },
                        {
                            "author": "Jeff",
                            "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                            "type": 1,
                            "is_pinned": false,
                            "attachments_content": "only one attachment"
                        },
                        {
                            "author": "Balderdash",
                            "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                            "type": 2,
                            "is_pinned": false,
                            "attachments_content": "first attachment, second attachment"
                        },
                        {
                            "author": "Jeff",
                            "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                            "type": 1,
                            "is_pinned": false,
                            "is_summary": true,
                            "attachments_content": null
                        }
                    ]""",
        )


        special_tokens_mapping = {
            'bod': "<|CUSTOM_BOD|>",
            'bom': "<|CUSTOM_BOM|>",
            'eom': "<|CUSTOM_EOM|>",
            'space': "<|CUSTOM_SPACE|>",
            'start_token': "<|CUSTOM_START|>",
            'audio_mode_token': "<|CUSTOM_AUDIO|>"
        }

        result = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=base_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
            special_tokens_mapping=special_tokens_mapping,
        )

        prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)

        self.assertIn("<|CUSTOM_BOD|>", prompt_string, "Custom BOD token not found in prompt")
        self.assertIn("<|CUSTOM_BOM|>", prompt_string, "Custom BOM token not found in prompt")
        self.assertIn("<|CUSTOM_EOM|>", prompt_string, "Custom EOM token not found in prompt")


        self.assertNotIn("<|beginningofdialog|>", prompt_string, "Default BOD token found in prompt")
        self.assertNotIn("<|beginningofmessage|>", prompt_string, "Default BOM token found in prompt")
        self.assertNotIn("<|endofmessage|>", prompt_string, "Default EOM token found in prompt")

    def test_special_token_overrides_some_overriden(self):
            """Test special token overrides."""
            base_structured_prefix = StructuredPrefix(
                character_definitions=[],
                chat_history=[
                    "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                ],
                reply_prompt="Balderdash:",
                timestamp="2024 04 23 Tuesday 19 07",
                raw_prompt_data_str="""{
                            "chat_type": "ONE_ON_ONE",
                            "character": {
                                "participant__name": "Balderdash",
                                "title": "A great Character",
                                "description": "Tongue in cheek.",
                                "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                                "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
                            },
                            "username": "Jeff",
                            "user_country_code": "US",
                            "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
                            "is_proactive": false
                        }""",
                chat_context_messages_str="""[
                            {
                                "author": "Balderdash",
                                "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                                "type": 2,
                                "is_pinned": true
                            },
                            {
                                "author": "Jeff",
                                "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                                "type": 1,
                                "is_pinned": false,
                                "attachments_content": "only one attachment"
                            },
                            {
                                "author": "Balderdash",
                                "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                                "type": 2,
                                "is_pinned": false,
                                "attachments_content": "first attachment, second attachment"
                            },
                            {
                                "author": "Jeff",
                                "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                                "type": 1,
                                "is_pinned": false,
                                "is_summary": true,
                                "attachments_content": null
                            }
                        ]""",
            )

            special_tokens_mapping = {
                'bod': "<|CUSTOM_BOD|>",
            }

            result = build_structured_prefix(
                logger=self.mock_logger,
                structured_prefix=base_structured_prefix,
                truncation_step=1,
                encode_func=self.encode_func,
                special_tokens_mapping=special_tokens_mapping,
            )

            prompt_string = self.tokenizer.detokenize(result["tokenized_context"].tokens)

            self.assertIn("<|CUSTOM_BOD|>", prompt_string, "Custom BOD token not found in prompt")
            self.assertIn("<|beginningofmessage|>", prompt_string, "Custom BOM token not found in prompt")

    def test_production_raw_template_with_lores(self):
        """Test the production raw template prompt with lores."""
        base_structured_prefix = StructuredPrefix(
            character_definitions=[],
            chat_history=[
                "Balderdash: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "Jeff: Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "Balderdash: Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            ],
            reply_prompt="Balderdash:",
            timestamp="2024 04 23 Tuesday 19 07",
            hermes_generation_template_name=str(HERE/".."/".."/DEFAULT_TEMPLATE_DIR/"chat_stack/candidate/templates/production_raw.yml.j2"),
            raw_prompt_data_str="""{
                "chat_type": "ONE_ON_ONE",
                "character": {
                    "participant__name": "Balderdash",
                    "title": "A great Character",
                    "description": "Tongue in cheek.",
                    "definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past",
                    "sanitized_definition": "{{user}}: Who are you?\\n{{char}}: I'm The Balderdash!\\n{{random_user_1}}: What can you do?\\n{{char}}: I'll tell you all my secrets...{{random_user_2}}: but?\\n{{char}}: but I lie about my past"
                },
                "username": "Jeff",
                "user_country_code": "US",
                "persona_definition": "name: Jeff\\neye color: red\\nname: Jeff",
                "is_proactive": false
            }""",
            chat_context_messages_str="""[
                {
                    "author": "Balderdash",
                    "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    "type": 2,
                    "is_pinned": true
                },
                {
                    "author": "Jeff",
                    "text": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                    "type": 1,
                    "is_pinned": false,
                    "lores": {
                        "lore1": "lore1 content",
                        "lore2": "lore2 content"
                    }
                }
            ]""",
        )
        res = build_structured_prefix(
            logger=self.mock_logger,
            structured_prefix=base_structured_prefix,
            truncation_step=1,
            encode_func=self.encode_func,
            use_gcs_template=False,
        )
        # The lores should be injected into the prompt.
        self.assertIn(
            "narrator: lore1 - lore1 content\nlore2 - lore2 content",
            self.tokenizer.detokenize(res["tokenized_context"].tokens),
        )
        print(self.tokenizer.detokenize(res["tokenized_context"].tokens))


if __name__ == "__main__":
    unittest.main()
