#pragma once

#include "stepper_delta.h"
#include <tsl/htrie_map.h>
#include <optional>
#include <string>
#include <unordered_map>
#include <variant>
#include <vector>
#include <thread>

#include <nanobind/nanobind.h>
#include <nanobind/intrusive/counter.h>
#include <nanobind/intrusive/ref.h>

namespace nb = nanobind;

// Forward declaration
class Stepper;

/**
 * @brief Defines a grammar as a finite state machine with transitions between states
 *
 * The StateMachine class represents a grammar through a graph of states and transitions.
 * It serves as the core definition of valid token sequences and patterns. Each transition
 * between states can have an associated sub-state machine, enabling hierarchical grammar
 * composition.
 *
 * Key responsibilities:
 * - Define states and transitions that form a grammar
 * - Create Stepper instances to traverse the state machine
 * - Process transitions as tokens are consumed
 * - Maintain the structure of valid paths through the state space
 * - Support hierarchical composition through nested state machines
 *
 * The StateMachine implements a directed graph where:
 * - Nodes represent grammar states
 * - Edges represent transitions, each with an associated state machine validator
 * - Multiple edges can exit a single state, supporting non-deterministic parsing
 * - Special end states mark completion of valid sequences
 */
class StateMachine : public nb::intrusive_base
{
public:
  /**
   * @brief Type definition for state identifiers, which can be integers or strings
   */
  using StateId = std::variant<int, std::string>;

  /**
   * @brief Type definition for transitions between states
   *
   * Each edge consists of:
   * - A reference to a state machine that validates the transition
   * - The target state ID to transition to
   */
  using Edge = std::pair<nb::ref<StateMachine>, StateId>;

  /**
   * @brief Type definition for the state transition graph
   *
   * Maps from state IDs to vectors of outgoing edges
   */
  using StateGraph = std::unordered_map<StateId, std::vector<Edge>>;

  //=========================================================================
  // Member Variables
  //=========================================================================

  /** The graph of states and transitions */
  StateGraph state_graph_;

  /** The starting state for this state machine */
  StateId start_state_;

  /** The set of states that represent valid end points */
  std::vector<StateId> end_states_;

  /** Whether this state machine is optional in a larger grammar */
  bool is_optional_;

  /** Whether token matching should be case-sensitive */
  bool is_case_sensitive_;

  /**
   * @brief Constructs a new state machine
   *
   * @param state_graph Graph defining states and transitions
   * @param start_state The initial state
   * @param end_states States that represent valid completion points
   * @param is_optional Whether this state machine is optional
   * @param is_case_sensitive Whether token matching should be case-sensitive
   * @param identifier A human-readable identifier for the state machine
   */
  StateMachine(
    StateGraph &&state_graph,
    StateId start_state,
    std::vector<StateId> &&end_states,
    bool is_optional = false,
    bool is_case_sensitive = true,
    std::optional<std::string> identifier = std::nullopt);

  /**
   * @brief Virtual destructor
   */
  virtual ~StateMachine() = default;

  //=========================================================================
  // State Query Methods
  //=========================================================================

  /**
   * @brief Checks if a given state is an end (accepting) state
   *
   * @param state The state to check
   * @return true if the state is an end state, false otherwise
   */
  bool is_end_state(StateId state) const { return std::ranges::find(end_states_, state) != end_states_.end(); }

  /**
   * @brief Gets whether this state machine is optional
   *
   * An optional state machine can be skipped entirely during parsing.
   *
   * @return true if optional, false otherwise
   */
  bool is_optional() const { return is_optional_; }

  /**
   * @brief Sets whether this state machine is optional
   *
   * @param value New optional status
   */
  void is_optional(bool value) { is_optional_ = value; }

  /**
   * @brief Gets whether token matching is case-sensitive
   *
   * @return true if case-sensitive, false otherwise
   */
  bool is_case_sensitive() const { return is_case_sensitive_; }

  /**
   * @brief Sets whether token matching should be case-sensitive
   *
   * @param value New case sensitivity setting
   */
  void is_case_sensitive(bool value) { is_case_sensitive_ = value; }

  //=========================================================================
  // Stepper Creation and Management Methods
  //=========================================================================

  /**
   * @brief Creates a new stepper for traversing this state machine
   *
   * @param state Optional starting state; uses the state machine's start state if not provided
   * @return A new stepper instance positioned at the specified or start state
   */
  virtual nb::ref<Stepper> get_new_stepper(std::optional<StateId> state = std::nullopt);

  /**
   * @brief Creates multiple steppers for this state machine
   *
   * This can create multiple steppers when the grammar allows for different
   * initial paths.
   *
   * @param state Optional starting state
   * @return A vector of stepper instances
   */
  virtual std::vector<nb::ref<Stepper>> get_steppers(std::optional<StateId> state = std::nullopt);

  /**
   * @brief Gets the outgoing edges from a given state
   *
   * @param state The state to get edges from
   * @return A vector of edges (state machine, target state pairs)
   */
  virtual std::vector<Edge> get_edges(StateId state) const;

  /**
   * @brief Gets possible transitions for a stepper
   *
   * @param stepper The stepper to get transitions for
   * @return A vector of (stepper, target state) tuples representing possible transitions
   */
  virtual std::vector<std::tuple<nb::ref<Stepper>, StateId>> get_transitions(nb::ref<Stepper> stepper) const;

  /**
   * @brief Creates multiple branched steppers from a given stepper
   *
   * This enables exploring different paths through the state machine simultaneously.
   *
   * @param stepper The stepper to branch from
   * @param token Optional token to consider when creating branches
   * @return A vector of new stepper instances representing different branch paths
   */
  virtual std::vector<nb::ref<Stepper>> branch_stepper(nb::ref<Stepper> stepper, std::optional<std::string> token = std::nullopt) const;

  /**
   * @brief Advances a stepper by consuming a token
   *
   * This is the core method for token consumption, creating new steppers that
   * represent the state after consuming the token.
   *
   * @param stepper The stepper to advance
   * @param token The token to consume
   * @return A vector of new steppers representing possible states after consuming the token
   */
  virtual std::vector<nb::ref<Stepper>> advance_stepper(nb::ref<Stepper> stepper, const std::string &token) const;

  //=========================================================================
  // Static Helper Methods for Token Processing
  //=========================================================================

  /**
   * @brief Advances multiple steppers with a token using parallel processing
   *
   * This method processes multiple steppers concurrently, which can improve
   * performance with large numbers of steppers.
   *
   * @param steppers The steppers to advance
   * @param token The token to consume
   * @param vocab Optional vocabulary for token validation and healing
   * @param token_healing Whether to attempt to repair partial token matches
   * @return Vector of StepperDelta objects containing results and metadata
   */
  static std::vector<StepperDelta> advance_all(
      std::vector<nb::ref<Stepper>> &steppers,
      std::string &token,
      const std::optional<tsl::htrie_map<char, std::vector<uint32_t>>> &vocab = std::nullopt,
      bool token_healing = true);

  /**
   * @brief Advances multiple steppers with a token sequentially
   *
   * Similar to advance_all but processes steppers one at a time rather than
   * in parallel. May be more efficient for small numbers of steppers.
   *
   * @param steppers The steppers to advance
   * @param token The token to consume
   * @param vocab Optional vocabulary for token validation and healing
   * @param token_healing Whether to attempt to repair partial token matches
   * @return Vector of StepperDelta objects containing results and metadata
   */
  static std::vector<StepperDelta> advance_all_sequential(
      std::vector<nb::ref<Stepper>> &steppers,
      std::string &token,
      const std::optional<tsl::htrie_map<char, std::vector<uint32_t>>> &vocab = std::nullopt,
      bool token_healing = true);

  /**
   * @brief Simplified version of advance_all that returns just the steppers
   *
   * This is a convenience wrapper that discards metadata and just returns
   * the resulting steppers. Useful when detailed transition information is
   * not needed.
   *
   * @param steppers The steppers to advance
   * @param token The token to consume
   * @return Vector of advanced steppers
   */
  static std::vector<nb::ref<Stepper>> advance_all_basic(std::vector<nb::ref<Stepper>> &steppers, std::string &token)
  {
    auto results = StateMachine::advance_all_sequential(steppers, token, std::nullopt, true);
    std::vector<nb::ref<Stepper>> advanced_steppers;
    for (auto &result : results)
    {
      advanced_steppers.push_back(result.stepper());
    }
    return advanced_steppers;
  }

  //=========================================================================
  // Comparison and String Representation
  //=========================================================================

  /**
   * @brief Equality comparison operator
   *
   * Compares two state machines based on their structure, states, and properties.
   *
   * @param other The state machine to compare with
   * @return true if both state machines are equivalent
   */
  virtual bool operator==(nb::ref<StateMachine> other) const
  {
    // lazy compare the state graph
    for (const auto &[state, _] : state_graph_)
    {
      auto transitions = get_edges(state);
      auto other_transitions = other->get_edges(state);
      if (transitions.size() != other_transitions.size()) {
        return false;
      }
      for (size_t i = 0; i < transitions.size(); ++i) {
        auto [state_machine, target_state] = transitions[i];
        auto [other_state_machine, other_target_state] = other_transitions[i];
        auto state_machine_identifier = state_machine->get_identifier().value_or(state_machine->get_name());
        auto other_state_machine_identifier = other_state_machine->get_identifier().value_or(other_state_machine->get_name());
        if (state_machine_identifier != other_state_machine_identifier || target_state != other_target_state) {
          return false;
        }
      }
    }
    return identifier_ == other->identifier_ &&
           start_state_ == other->start_state_ &&
           end_states_ == other->end_states_ &&
           is_optional_ == other->is_optional_ &&
           is_case_sensitive_ == other->is_case_sensitive_;
  }

  /**
   * @brief Gets the name of this state machine from its class
   *
   * Uses Python reflection to determine the class name of this state machine.
   *
   * @return The class name of this state machine
   */
  std::string get_name() const
  {
    nb::object obj = nb::find(this);
    nb::object cls = nb::getattr(obj, "__class__");
    nb::object name_obj = nb::getattr(cls, "__name__");
    std::string type_name = nb::str(name_obj).c_str();
    return type_name;
  }

  /**
   * @brief Gets the identifier of this state machine
   *
   * @return The identifier of this state machine
   */
  std::optional<std::string> get_identifier() const { return identifier_; }

  /**
   * @brief Sets the identifier of this state machine
   *
   * @param identifier The new identifier
   */
  void set_identifier(std::optional<std::string> identifier) { identifier_ = identifier; }

  /**
   * @brief Gets a string representation of this state machine
   *
   * Simple representation that just returns the name of the state machine.
   *
   * @return String representation
   */
  virtual std::string to_string() const
  {
    return this->get_name();
  }

  /**
   * @brief Gets a detailed string representation of this state machine
   *
   * Creates a comprehensive representation showing the state graph structure.
   *
   * @param indentation_level Indentation level for pretty-printing
   * @return Detailed string representation
   */
  virtual std::string to_readable(size_t indentation_level = 0) const
  {
    std::string result = this->get_name();

    if (state_graph_.empty())
    {
      return result + "()";
    }

    std::string indent((indentation_level + 1) * 4, ' ');

    result += "(graph={";
    std::vector<std::pair<StateId, std::vector<Edge>>> sorted_state_graph(state_graph_.begin(), state_graph_.end());
    std::sort(sorted_state_graph.begin(), sorted_state_graph.end(), [](const auto &a, const auto &b)
              { return StateMachine::state_to_string(a.first) < StateMachine::state_to_string(b.first); });
    size_t x = sorted_state_graph.size();

    for (size_t i = 0; i < x; ++i)
    {
      const auto &[state, transitions] = sorted_state_graph[i];
      std::string start_state_str = state_to_string(state);

      // Add visual cues for start and end states
      if (state == start_state_)
      {
        start_state_str = "\033[34m▶️ " + start_state_str + "\033[0m"; // Blue, Start symbol
      }
      else if (std::find(end_states_.begin(), end_states_.end(), state) != end_states_.end())
      {
        start_state_str = "\033[32m🏁 " + start_state_str + "\033[0m"; // Green, End symbol
      }

      result += "\n" + indent + start_state_str + ": ";

      std::vector<Edge> sorted_transitions = transitions;
      std::sort(sorted_transitions.begin(), sorted_transitions.end(), [](const auto &a, const auto &b)
                {
                    auto target_state_1 = StateMachine::state_to_string(a.second);
                    auto target_state_2 = StateMachine::state_to_string(b.second);
                    if (target_state_1 == "$")
                        return false;
                    if (target_state_2 == "$")
                        return true;
                    return target_state_1 < target_state_2; });

      size_t y = sorted_transitions.size();
      if (y > 1)
      {
        result += "[ ";
      }
      for (size_t j = 0; j < y; ++j)
      {
        const auto &[state_machine, target_state] = sorted_transitions[j];
        std::string target_state_str = state_to_string(target_state);

        if (target_state_str == "$")
        {
          target_state_str = "✅";
        }
        // Visually distinguish the target state if it's an end state
        else if (std::find(end_states_.begin(), end_states_.end(), target_state) != end_states_.end())
        {
          target_state_str = "\033[32m🏁 " + target_state_str + "\033[0m";
        }

        if (y > 1)
        {
          result += "\n" + indent + indent;
        }
        std::string transition_str = state_machine->to_string();
        std::string find = "\n";
        std::string replace = "\n" + indent;
        if (y > 1)
        {
          replace = "\n" + indent + indent;
        }
        size_t pos = transition_str.find(find);
        while (pos != std::string::npos)
        {
          transition_str.replace(pos, find.length(), replace);
          pos = transition_str.find(find, pos + replace.length());
        }
        result += transition_str + " --> " + target_state_str;
        if (y > 1 && j < y - 1)
        {
          result += ",";
        }
      }
      if (y > 1)
      {
        result += "\n" + indent + "]";
      }
      if (x > 1 && i < x - 1)
      {
        result += ",";
      }
    }
    result += "\n})";
    return result;
  }

  //=========================================================================
  // Static Helper Methods
  //=========================================================================

  /**
   * @brief Converts a state ID to a string representation
   *
   * Handles both integer and string state IDs, providing a uniform string
   * representation for display and debugging.
   *
   * @param state The state ID to convert
   * @return The string representation of the state
   */
  static std::string state_to_string(const StateId &state)
  {
    return std::visit([](auto &&arg) -> std::string
                      {
                        using T = std::decay_t<decltype(arg)>;
                        if constexpr (std::is_same_v<T, int>) {
                          return std::to_string(arg);
                        } else if constexpr (std::is_same_v<T, std::string>) {
                          return arg;
                        } else {
                          return "";
                        } }, state);
  }

protected:
  std::optional<std::string> identifier_;
};
