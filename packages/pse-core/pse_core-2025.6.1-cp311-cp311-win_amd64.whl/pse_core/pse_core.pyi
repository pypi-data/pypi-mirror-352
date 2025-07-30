"""PSE Core Module: State Machine Grammar Constraints for Language Models

This module provides the core classes for defining and traversing grammar-based
constraints for language model token generation. The system implements a
non-deterministic state machine approach that allows efficient exploration of
multiple valid paths without excessive backtracking.

Key components:
- StateMachine: Defines grammar rules through state transitions
- Stepper: Represents a position in a state machine with traversal methods
- StepperDelta: Represents state changes after token consumption
- Engine: Orchestrates token processing and logit modification
- TrieMap: Efficient string-to-value mapping for tokenization
"""

from __future__ import annotations

from abc import ABC
from collections.abc import Callable
from typing import Any, Self, TypeVar

# Type variable for array-like objects (tensors)
Array_Type = TypeVar("Array_Type")

# Type aliases for core PSE types
StateId = int | str
Edge = tuple[StateMachine, StateId]
StateGraph = dict[StateId, list[Edge]]

class Engine(ABC):
    """Orchestrates token processing and interfaces with language models.

    The Engine class serves as the central coordinator for the PSE core system,
    managing token consumption, tokenization, and logit processing for language
    model integration. It acts as the interface between language models and
    the grammatical constraints defined by StateMachines.

    Key responsibilities:
    - Process and modify logit distributions to enforce grammar constraints
    - Sample tokens from logit distributions with optional multi-token sampling and token healing and resampling
    - Handle token consumption and state machine traversal
    - Manage vocabulary mappings between token IDs and strings
    - Track active steppers and state machine positions
    - Determine valid/invalid tokens based on current state
    """

    def __init__(
        self,
        vocabulary: dict[str, int],
        encode_function: Callable[[str], list[int]],
        decode_function: Callable[[list[int]], str],
        strict: bool = False,
        multi_token_sampling: bool = True,
        max_resamples: int = 5,
        control_tokens: list[int] = [],
    ) -> None:
        """Initialize the engine with tokenization mappings and behavior parameters.

        Args:
            vocabulary: Mapping from token strings to their token IDs
            encode_function: Function to encode strings to token IDs
            decode_function: Function to decode token IDs to strings
            strict: Whether to strictly enforce constraints (no fallback)
            multi_token_sampling: Whether to enable multi-token sequence handling
            max_resamples: Maximum number of sampling attempts for a valid token
            control_tokens: Token IDs that should be blocked until reaching an accept state
        """
        ...

    def __call__(self, tokens: Array_Type, scores: Array_Type) -> Array_Type:
        """Process logits scores and return the corrected logits.

        Args:
            tokens: Current token sequence
            scores: Original logit scores to modify

        Returns:
            Modified logit scores with invalid tokens masked
        """
        ...

    def compute_token_mask(self, vocab_size: int) -> list[bool]:
        """Computes a token mask for the current state.

        Args:
            vocab_size: The vocabulary size
        """
        ...

    def mask_invalid_tokens(self, scores: Array_Type) -> Array_Type:
        """Masks invalid tokens in logit tensor.

        Sets probabilities of invalid tokens to negative infinity,
        enforcing grammatical constraints during sampling.

        Args:
            scores: Tensor of token logits [batch_size x vocab_size]

        Returns:
            Modified tensor with invalid tokens masked
        """
        ...

    def select_next_tokens(
        self, log_probs: Array_Type, sampler: Callable[[Array_Type], Array_Type]
    ) -> list[list[int]]:
        """Selects next tokens based on logits and sampling.

        Samples tokens, tests if they're valid by advancing steppers,
        and selects the best path based on multiple criteria.

        Args:
            log_probs: Tensor of log probabilities [1 x vocab_size]
            sampler: Function to sample from the log probabilities

        Returns:
            List of selected token ID sequences
        """
        ...

    def consume(self, token_id: int, token_healing: bool = True) -> int | None:
        """Consumes a single token and advances steppers.

        Advances the engine's state(steppers) by consuming a single token.

        Args:
            token_id: The token ID to consume
            token_healing: Whether to attempt token healing
        """
        ...

    def consume_text(self, input: str, token_healing: bool = False) -> None:
        """Consumes raw text directly without tokenization.

        Parses the text using the state machine directly.

        Args:
            input: The raw text to consume
            token_healing: Whether to attempt token healing
        """
        ...

    def break_into_tokens(self, text: str) -> set[list[str]]:
        """Breaks text into all possible token sequences.

        Finds all possible ways to tokenize the input text based on vocabulary.

        Args:
            text: The text to tokenize

        Returns:
            Set of valid token sequences
        """
        ...

    def reset(self, hard_reset: bool = False) -> None:
        """Reset the engine to initial state.

        Args:
            hard_reset: If True, removes the state machine as well
        """
        ...

    def get_current_state(self) -> str | None:
        """Get the current state identifier from active steppers.

        Returns:
            The current state identifier if all steppers share the same state, or None if no common state exists
        """
        ...

    def get_live_token_safe_output(self, decode_function: Callable[[list[int]], str]) -> tuple[str, str] | None:
        """Get the live token safe output for the current state.

        Returns:
            The live token safe output for the current state, or None if no output is available
        """
        ...

    @property
    def has_reached_accept_state(self) -> bool:
        """Check if any stepper has reached an accept state.

        Returns:
            True if any stepper has reached an accept state
        """
        ...

    @property
    def state_machine(self) -> StateMachine | None:
        """The state machine defining the grammar constraints."""
        ...

    @state_machine.setter
    def state_machine(self, value: StateMachine | None) -> None: ...

    @property
    def vocabulary(self) -> TrieMap:
        """Mapping of token strings to their token IDs."""
        ...

    @property
    def reverse_vocabulary(self) -> dict[int, str]:
        """Mapping of token IDs to their string representations."""
        ...

    @property
    def steppers(self) -> list[Stepper]:
        """Active steppers representing current positions in the state machine."""
        ...

    @steppers.setter
    def steppers(self, value: list[Stepper]) -> None: ...

    @property
    def multi_token_mapping(self) -> dict[int, list[int]]:
        """Mapping for multi-token sequences.

        Maps token IDs to sequences of token IDs for handling cases where
        a single token in the grammar corresponds to multiple tokens in the
        model's vocabulary.
        """
        ...

    @multi_token_mapping.setter
    def multi_token_mapping(self, value: dict[int, list[int]]) -> None: ...

class StateMachine:
    """Defines a grammar as a finite state machine with transitions between states.

    The StateMachine class represents a grammar through a graph of states and transitions.
    It serves as the core definition of valid token sequences and patterns. Each transition
    between states can have an associated sub-state machine, enabling hierarchical grammar
    composition.

    Key responsibilities:
    - Define states and transitions that form a grammar
    - Create Stepper instances to traverse the state machine
    - Process transitions as tokens are consumed
    - Maintain the structure of valid paths through the state space
    - Support hierarchical composition through nested state machines
    """

    def __init__(
        self,
        state_graph: StateGraph | None = None,
        start_state: StateId = 0,
        end_states: list[StateId] | None = None,
        is_optional: bool = False,
        is_case_sensitive: bool = True,
        identifier: str | None = None,
    ) -> None:
        """Initialize a new state machine.

        Args:
            state_graph: Graph defining states and transitions
            start_state: The initial state
            end_states: States that represent valid completion points
            is_optional: Whether this state machine is optional
            is_case_sensitive: Whether token matching should be case-sensitive
            identifier: A human-readable identifier for the state machine
        """
        ...

    @property
    def is_optional(self) -> bool:
        """Check if the state machine is optional.

        An optional state machine can be skipped entirely during parsing.

        Returns:
            True if optional, False otherwise
        """
        ...

    @property
    def is_case_sensitive(self) -> bool:
        """Check if token matching is case-sensitive.

        Returns:
            True if case-sensitive, False otherwise
        """
        ...

    def get_new_stepper(self, state: StateId | None = None) -> Stepper:
        """Create a new stepper for traversing this state machine.

        Args:
            state: Optional starting state; uses the state machine's start state if not provided

        Returns:
            A new stepper instance positioned at the specified or start state
        """
        ...

    def get_steppers(self, state: StateId | None = None) -> list[Stepper]:
        """Create multiple steppers for this state machine.

        This can create multiple steppers when the grammar allows for different
        initial paths.

        Args:
            state: Optional starting state

        Returns:
            A list of stepper instances
        """
        ...

    def get_transitions(self, stepper: Stepper) -> list[tuple[Stepper, StateId]]:
        """Get possible transitions for a stepper.

        Args:
            stepper: The stepper to get transitions for

        Returns:
            A list of (stepper, target state) tuples representing possible transitions
        """
        ...

    def get_edges(self, state: StateId) -> list[Edge]:
        """Get the outgoing edges from a given state.

        Args:
            state: The state to get edges from

        Returns:
            A list of edges (state machine, target state pairs)
        """
        ...

    def branch_stepper(
        self, stepper: Stepper, token: str | None = None
    ) -> list[Stepper]:
        """Create multiple branched steppers from a given stepper.

        This enables exploring different paths through the state machine simultaneously.

        Args:
            stepper: The stepper to branch from
            token: Optional token to consider when creating branches

        Returns:
            A list of new stepper instances representing different branch paths
        """
        ...

    def advance_stepper(self, stepper: Stepper, token: str) -> list[Stepper]:
        """Advance a stepper by consuming a token.

        This is the core method for token consumption, creating new steppers that
        represent the state after consuming the token.

        Args:
            stepper: The stepper to advance
            token: The token to consume

        Returns:
            A list of new steppers representing possible states after consuming the token
        """
        ...

    @staticmethod
    def advance_all_basic(steppers: list[Stepper], token: str) -> list[Stepper]:
        """Simplified version of advance_all that returns just the steppers.

        This is a convenience wrapper that discards metadata and just returns
        the resulting steppers. Useful when detailed transition information is
        not needed.

        Args:
            steppers: The steppers to advance
            token: The token to consume

        Returns:
            List of advanced steppers
        """
        ...

    @staticmethod
    def advance_all(
        steppers: list[Stepper],
        token: str,
        vocab: TrieMap | None = None,
        token_healing: bool = True,
    ) -> list[StepperDelta]:
        """Advance multiple steppers with a token using parallel processing.

        This method processes multiple steppers concurrently, which can improve
        performance with large numbers of steppers.

        Args:
            steppers: The steppers to advance
            token: The token to consume
            vocab: Optional vocabulary for token validation and healing
            token_healing: Whether to attempt to repair partial token matches

        Returns:
            List of StepperDelta objects containing results and metadata
        """
        ...

    def __eq__(self, other: object) -> bool:
        """Check equality based on structure, states, and properties.

        Args:
            other: The state machine to compare with

        Returns:
            True if both state machines are equivalent
        """
        ...

    def __str__(self) -> str:
        """Get a simple string representation of this state machine.

        Returns:
            String representation showing the state machine name
        """
        ...

    def __repr__(self) -> str:
        """Get a detailed string representation of this state machine.

        Returns:
            Detailed string representation showing the state graph structure
        """
        ...

    @property
    def start_state(self) -> StateId:
        """The starting state for this state machine."""
        ...

    @start_state.setter
    def start_state(self, value: StateId) -> None: ...

    @property
    def end_states(self) -> list[StateId]:
        """The set of states that represent valid end points."""
        ...

    @end_states.setter
    def end_states(self, value: list[StateId]) -> None: ...

    @property
    def state_graph(self) -> StateGraph:
        """The graph of states and transitions."""
        ...

    @state_graph.setter
    def state_graph(self, value: StateGraph) -> None: ...

    @property
    def identifier(self) -> str | None:
        """The identifier for this state machine."""
        ...

    @identifier.setter
    def identifier(self, value: str | None) -> None: ...

class Stepper:
    """Represents a position within a state machine and manages traversal.

    A Stepper tracks the current state, transition history, and accumulated values
    during parsing or generation. It implements methods for consuming tokens,
    checking valid continuations, and managing hierarchical state transitions.

    Key responsibilities:
    - Track current position within the state machine
    - Consume tokens and advance through valid transitions
    - Manage sub-steppers for hierarchical state machine composition
    - Maintain history of traversed states
    - Determine valid and invalid continuations from the current state

    The Stepper follows an immutable pattern where operations produce new Stepper
    instances rather than modifying existing ones. This enables concurrent exploration
    of multiple possible paths through the state machine.
    """

    def __init__(
        self, state_machine: StateMachine, current_state: StateId | None = None
    ) -> None:
        """Initialize a new stepper for traversing a state machine.

        Args:
            state_machine: The state machine this stepper will traverse
            current_state: Optional starting state; uses the state machine's start state if not provided
        """
        ...

    def clone(self) -> Self:
        """Create a copy of this stepper with the same state and history.

        This is a key method that enables the exploration of multiple paths
        through the state machine.

        Returns:
            A new stepper instance with the same state
        """
        ...

    def consume(self, token: str) -> list[Stepper]:
        """Consume a token and advance the stepper.

        This is the primary method for token processing. It delegates to the
        state machine's advance_stepper method to handle the token consumption.

        Args:
            token: The token string to consume

        Returns:
            A list of new steppers representing possible paths after consuming the token
        """
        ...

    def can_accept_more_input(self) -> bool:
        """Check if the stepper can continue consuming tokens.

        Returns:
            True if the stepper can continue consuming tokens
        """
        ...

    def is_within_value(self) -> bool:
        """Check if the stepper is currently accumulating a value.

        Returns:
            True if the stepper is accumulating a value
        """
        ...

    def is_optional(self) -> bool:
        """Check if this stepper's state machine is optional.

        Returns:
            True if the state machine is optional
        """
        ...

    def should_start_step(self, token: str) -> bool:
        """Determine if this stepper should begin processing the given token.

        Args:
            token: The token to evaluate

        Returns:
            True if the stepper should start processing this token
        """
        ...

    def should_complete_step(self) -> bool:
        """Determine if this stepper has finished its current step.

        Returns:
            True if the stepper should complete its current step
        """
        ...

    def should_branch(self) -> bool:
        """Determine if this stepper should branch into multiple paths.

        Returns:
            True if the stepper should explore multiple paths
        """
        ...

    def accepts_any_token(self) -> bool:
        """Check if this stepper accepts any token input.

        Returns:
            True if any token is valid from the current state
        """
        ...

    def get_valid_continuations(self) -> list[str]:
        """Get the valid token continuations from the current state.

        Returns a list of strings that are valid next tokens from the
        current state in the state machine.

        Returns:
            A list of valid continuation strings
        """
        ...

    def get_invalid_continuations(self) -> list[str]:
        """Get the invalid token continuations from the current state.

        Returns a list of strings that should be explicitly prohibited
        as next tokens from the current state.

        Returns:
            A list of invalid continuation strings
        """
        ...

    def has_reached_accept_state(self) -> bool:
        """Check if the stepper has reached an accept state.

        Returns:
            True if the current state is an accept state
        """
        ...

    def add_to_history(self, stepper: Stepper) -> None:
        """Add a stepper to the history.

        This is called when a transition completes successfully.

        Args:
            stepper: The stepper to add to history
        """
        ...

    def start_step(
        self,
        sub_stepper: Stepper,
        target_state: StateId,
        token: str | None = None,
    ) -> Stepper | None:
        """Start a transition to a new state with a sub-stepper.

        This initiates a hierarchical transition where a sub-stepper handles
        part of the token processing before the parent stepper completes the transition.

        Args:
            sub_stepper: The stepper to use for the transition
            target_state: The target state to transition to
            token: Optional token that triggered this transition

        Returns:
            A new stepper with the transition started, or None if invalid
        """
        ...

    def complete_step(
        self,
        sub_stepper: Stepper,
    ) -> list[Stepper]:
        """Complete a transition started by a sub-stepper.

        After a sub-stepper has finished processing, this method completes
        the transition in the parent stepper, potentially generating multiple
        result paths.

        Args:
            sub_stepper: The sub-stepper that has completed its processing

        Returns:
            A list of new steppers representing possible paths after completing the step
        """
        ...

    def step(
        self,
        new_value: str | None = None,
        remaining_input: str | None = None,
    ) -> Stepper:
        """Create a new stepper with updated state.

        Args:
            new_value: Optional new value to set
            remaining_input: Optional remaining input to set

        Returns:
            A new stepper with the updated state
        """
        ...

    def branch(self, token: str | None = None) -> list[Stepper]:
        """Create multiple branched steppers to explore different paths.

        This enables the non-deterministic exploration of multiple possible
        paths through the state machine simultaneously.

        Args:
            token: Optional token to consider when creating branches

        Returns:
            A list of new steppers representing different branch paths
        """
        ...

    def get_final_state(self) -> list[Stepper]:
        """Get the final state of the stepper.

        Returns:
            A list of steppers representing the final state
        """
        ...

    def get_current_value(self) -> Any:
        """Get the current parsed value.

        Returns the accumulated value as a Python object, converting from
        the internal string representation to an appropriate type.

        Returns:
            The current value from transition or history, parsed into appropriate type.
            Returns None if no value is accumulated.
        """
        ...

    def get_raw_value(self) -> str:
        """Get the raw string value without type conversion.

        Returns the raw string representation of the accumulated value
        without any type conversion.

        Returns:
            The concatenated raw values from history and transitions
        """
        ...

    def get_token_ids_history(self) -> list[int]:
        """Get the history of token IDs consumed by this stepper."""
        ...

    # Core properties
    @property
    def state_machine(self) -> StateMachine:
        """The state machine associated with this stepper."""
        ...

    @state_machine.setter
    def state_machine(self, value: StateMachine) -> None: ...

    @property
    def current_state(self) -> StateId:
        """The current state ID within the state machine."""
        ...

    @current_state.setter
    def current_state(self, value: StateId) -> None: ...

    @property
    def target_state(self) -> StateId | None:
        """The target state for in-progress transitions."""
        ...

    @target_state.setter
    def target_state(self, value: StateId | None) -> None: ...

    # Sub-stepper and history
    @property
    def sub_stepper(self) -> Stepper | None:
        """The sub-stepper handling a nested state machine traversal."""
        ...

    @sub_stepper.setter
    def sub_stepper(self, value: Stepper | None) -> None: ...

    @property
    def history(self) -> list[Stepper]:
        """The history of steppers that led to the current state."""
        ...

    @history.setter
    def history(self, value: list[Stepper]) -> None: ...

    # Input tracking
    @property
    def consumed_character_count(self) -> int:
        """The number of characters consumed by this stepper."""
        ...

    @consumed_character_count.setter
    def consumed_character_count(self, value: int) -> None: ...

    @property
    def remaining_input(self) -> str | None:
        """Any remaining input that hasn't been consumed yet."""
        ...

    @remaining_input.setter
    def remaining_input(self, value: str | None) -> None: ...

    # Value handling
    @property
    def _raw_value(self) -> str | None:
        """The raw accumulated value as a string."""
        ...

    @_raw_value.setter
    def _raw_value(self, value: str | None) -> None: ...


    def get_identifier(self) -> str | None:
        """The identifier for this stepper."""
        ...

    def get_token_safe_output(self, decode_function: Callable[[list[int]], str]) -> str:
        """The token safe output for this stepper."""
        ...

    # Magic methods
    def __eq__(self, other: object) -> bool:
        """Check equality based on state and accumulated value.

        Args:
            other: The object to compare with

        Returns:
            True if both steppers are equal; False otherwise
        """
        ...

    def __str__(self) -> str:
        """Get a compact string representation of the stepper.

        Returns:
            A string representation of the stepper
        """
        ...

    def __repr__(self) -> str:
        """Get a detailed string representation of the stepper.

        Returns:
            A detailed string representation showing state and history
        """
        ...

class StepperDelta:
    """Represents the result of a state transition after consuming a token.

    StepperDelta encapsulates the outcome of advancing a Stepper with a token,
    including metadata about the transition. It serves as the core data structure
    for tracking and comparing possible paths through the state machine, enabling
    sophisticated path selection when multiple valid transitions exist.

    Key responsibilities:
    - Track steppers after token consumption
    - Record metadata about transitions (token, healing status, scores)
    - Compare and select optimal paths based on multiple criteria
    - Support token healing by tracking partially matched tokens
    """

    def __init__(self, stepper: Stepper, token: str, was_healed: bool) -> None:
        """Initialize a new transition result.

        Args:
            stepper: The stepper in its new state after consuming a token
            token: The token that was consumed
            was_healed: Whether token healing was applied
        """
        ...

    @property
    def stepper(self) -> Stepper:
        """The stepper after consuming a token."""
        ...

    @stepper.setter
    def stepper(self, value: Stepper) -> None: ...

    @property
    def token(self) -> str:
        """The token that was consumed."""
        ...

    @token.setter
    def token(self, value: str) -> None: ...

    @property
    def was_healed(self) -> bool:
        """Whether token healing was applied."""
        ...

    @was_healed.setter
    def was_healed(self, value: bool) -> None: ...

    def is_attractive_path(self) -> bool:
        """Determine if this path is preferred for further exploration.

        A path is considered attractive if it either:
        - Reaches an accept state
        - Did not require token healing

        Returns:
            True if the path should be preferred
        """
        ...

    @staticmethod
    def choose_best_path(steppers: set[StepperDelta]) -> tuple[str, list[Stepper]]:
        """Select the optimal path from multiple candidates.

        Implements a sophisticated path selection algorithm that chooses the best
        token path based on a hierarchical set of criteria:
        1. Accepted states (highest priority)
        2. Non-healed tokens preferred over healed ones
        3. Higher scores
        4. Longer tokens (when scores are equal)

        Args:
            steppers: Set of StepperDelta candidates representing possible paths

        Returns:
            A tuple containing the chosen token and list of steppers for that path
        """
        ...

    def __eq__(self, other: object) -> bool:
        """Check equality based on stepper, token, and healing status.

        Args:
            other: The object to compare with

        Returns:
            True if both objects represent the same transition
        """
        ...

    def __lt__(self, other: StepperDelta) -> bool:
        """Compare transitions for ordering.

        Provides an ordering for StepperDelta objects, useful for containers like sets.

        Args:
            other: The StepperDelta to compare with

        Returns:
            True if this object is less than the other
        """
        ...

class TrieMap:
    """An efficient HAT-trie based map implementation for string-to-value mapping.

    This class provides an efficient implementation of a map data structure
    specifically optimized for string keys using a HAT-trie structure. It is
    used throughout PSE for vocabulary lookup and token processing.

    Key features:
    - Fast prefix-based string lookups
    - Memory-efficient storage of large vocabularies
    - Support for multi-token mappings
    """

    def __init__(self, burst_threshold: int = 1024) -> None:
        """Initialize a new TrieMap.

        Args:
            burst_threshold: Threshold for the trie's burst operation,
                             controlling the balance between memory usage and lookup speed
        """
        ...

    def insert(self, key: str, value: int) -> None:
        """Insert a key-value pair into the map.

        Args:
            key: The string key to insert
            value: The token ID to associate with the key
        """
        ...

    def insert_all(self, items: list[tuple[str, int]]) -> TrieMap:
        """Insert multiple key-value pairs into the map.

        Args:
            items: List of (key, value) tuples to insert

        Returns:
            Self for method chaining
        """
        ...

    def erase(self, key: str) -> int:
        """Remove a key-value pair from the map.

        Args:
            key: The string key to remove

        Returns:
            Number of elements removed (0 or 1)
        """
        ...

    def get(self, key: str) -> list[int] | None:
        """Find the value associated with a key.

        Args:
            key: The string key to look for

        Returns:
            The associated token IDs if found, None otherwise
        """
        ...

    def get_all(self, keys: list[str]) -> list[list[int]]:
        """Get the values associated with multiple keys.

        Args:
            keys: The list of string keys to look for

        Returns:
            A list of token ID lists associated with each key
        """
        ...

    @property
    def empty(self) -> bool:
        """Check if the map is empty.

        Returns:
            True if the map contains no elements
        """
        ...

    @property
    def size(self) -> int:
        """Get the number of elements in the map.

        Returns:
            The number of key-value pairs stored in the map
        """
        ...

    def clear(self) -> None:
        """Remove all elements from the map."""
        ...
