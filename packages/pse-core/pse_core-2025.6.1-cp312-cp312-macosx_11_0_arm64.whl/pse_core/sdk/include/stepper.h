#pragma once

#include "state_machine.h"
#include <tsl/htrie_set.h>
#include <nlohmann/json.hpp>
#include <nanobind/stl/string.h>
#include <nanobind/nanobind.h>
#include <nanobind/intrusive/counter.h>
#include <nanobind/intrusive/ref.h>
#include <optional>
#include <set>
#include <string>
#include <tuple>
#include <vector>
#include <any>

namespace nb = nanobind;

/**
 * @brief Stepper class for traversing state machines
 *
 * The Stepper class represents a position within a state machine and manages traversal
 * through states as tokens are consumed. It maintains the current state, transition history,
 * and accumulated values during parsing or generation.
 *
 * Key responsibilities:
 * - Track current position within the state machine
 * - Consume tokens and advance through valid transitions
 * - Manage sub-steppers for hierarchical state machine composition
 * - Maintain history of traversed states
 * - Determine valid and invalid continuations from the current state
 *
 * The Stepper follows an immutable pattern where operations produce new Stepper instances
 * rather than modifying existing ones. This enables concurrent exploration of multiple
 * possible paths through the state machine.
 */
class Stepper : public nb::intrusive_base
{
public:
    using StateId = StateMachine::StateId;

    //=========================================================================
    // Constructor & Destructor
    //=========================================================================

    /**
     * @brief Constructs a new Stepper
     *
     * @param state_machine The state machine this stepper will traverse
     * @param current_state Optional starting state; uses the state machine's start state if not provided
     */
    Stepper(nb::ref<StateMachine> state_machine, std::optional<StateId> current_state = std::nullopt);

    /**
     * @brief Virtual destructor
     */
    virtual ~Stepper() override = default;

    /**
     * @brief Creates a copy of this stepper
     *
     * Creates a new stepper with the same state and history. This is a key method
     * that enables the exploration of multiple paths through the state machine.
     *
     * @return A new stepper instance with the same state
     */
    virtual nb::ref<Stepper> clone() const;

    //=========================================================================
    // State Transition Decision Methods
    //=========================================================================

    /**
     * @brief Determines if this stepper should begin processing the given token
     *
     * @param token The token to evaluate
     * @return true if the stepper should start processing this token
     */
    virtual bool should_start_step(const std::string& token) const;

    /**
     * @brief Determines if this stepper has finished its current step
     *
     * @return true if the stepper should complete its current step
     */
    virtual bool should_complete_step() const;

    /**
     * @brief Determines if this stepper should branch into multiple paths
     *
     * @return true if the stepper should explore multiple paths
     */
    virtual bool should_branch() const;

    //=========================================================================
    // State Query Methods
    //=========================================================================

    /**
     * @brief Checks if this stepper accepts any token input
     *
     * @return true if any token is valid from the current state
     */
    virtual bool accepts_any_token() const;

    /**
     * @brief Checks if this stepper can accept more input
     *
     * @return true if the stepper can continue consuming tokens
     */
    virtual bool can_accept_more_input() const;

    /**
     * @brief Checks if this stepper has reached an accept state
     *
     * @return true if the current state is an accept state
     */
    virtual bool has_reached_accept_state() const;

    /**
     * @brief Checks if this stepper's state machine is optional
     *
     * @return true if the state machine is optional
     */
    virtual inline bool is_optional() const { return state_machine_->is_optional(); };

    /**
     * @brief Checks if this stepper is currently within a value
     *
     * @return true if the stepper is accumulating a value
     */
    virtual bool is_within_value() const;

    /**
     * @brief Consumes a token and advances the stepper
     *
     * This is the primary method for token processing. It delegates to the
     * state machine's advance_stepper method to handle the token consumption.
     *
     * @param token The token string to consume
     * @return A vector of new steppers representing possible paths after consuming the token
     */
    virtual std::vector<nb::ref<Stepper>> consume(std::string token)
    {
        return state_machine_->advance_stepper(nb::ref<Stepper>(this), token);
    };

    //=========================================================================
    // State Transition Methods
    //=========================================================================

    /**
     * @brief Creates a new stepper with updated state
     *
     * @param new_value Optional new value to set
     * @param remaining_input Optional remaining input to set
     * @return A new stepper with the updated state
     */
    nb::ref<Stepper> step(const std::optional<std::string>& new_value = std::nullopt,
                          const std::optional<std::string>& remaining_input = std::nullopt);

    /**
     * @brief Starts a transition to a new state with a sub-stepper
     *
     * This initiates a hierarchical transition where a sub-stepper handles
     * part of the token processing before the parent stepper completes the transition.
     *
     * @param sub_stepper The stepper to use for the transition
     * @param target_state The target state to transition to
     * @param token Optional token that triggered this transition
     * @return A new stepper with the transition started, or nullopt if invalid
     */
    std::optional<nb::ref<Stepper>> start_step(
        nb::ref<Stepper> sub_stepper,
        StateId target_state,
        std::optional<std::string> token = std::nullopt);

    /**
     * @brief Completes a transition started by a sub-stepper
     *
     * After a sub-stepper has finished processing, this method completes
     * the transition in the parent stepper, potentially generating multiple
     * result paths.
     *
     * @param sub_stepper The sub-stepper that has completed its processing
     * @return A vector of new steppers representing possible paths after completing the step
     */
    std::vector<nb::ref<Stepper>> complete_step(nb::ref<Stepper> sub_stepper);

    /**
     * @brief Creates multiple branched steppers to explore different paths
     *
     * This enables the non-deterministic exploration of multiple possible
     * paths through the state machine simultaneously.
     *
     * @param token Optional token to consider when creating branches
     * @return A vector of new steppers representing different branch paths
     */
    std::vector<nb::ref<Stepper>> branch(const std::optional<std::string>& token = std::nullopt);

    //=========================================================================
    // Token and Continuation Methods
    //=========================================================================

    /**
     * @brief Gets the valid token continuations from the current state
     *
     * Returns a list of strings that are valid next tokens from the
     * current state in the state machine.
     *
     * @return A vector of valid continuation strings
     */
    virtual std::vector<std::string> get_valid_continuations() const;

    /**
     * @brief Gets the invalid token continuations from the current state
     *
     * Returns a list of strings that should be explicitly prohibited
     * as next tokens from the current state.
     *
     * @return A vector of invalid continuation strings
     */
    virtual std::vector<std::string> get_invalid_continuations() const;

    //=========================================================================
    // Value Accessors & Mutators
    //=========================================================================

    /**
     * @brief Gets the final state of the stepper
     *
     * @return A vector of steppers representing the final state
     */
    virtual std::vector<nb::ref<Stepper>> get_final_state();

    /**
     * @brief Gets the current parsed value
     *
     * Returns the accumulated value as a Python object, converting from
     * the internal string representation to an appropriate type.
     *
     * @return A Python object representing the current value
     */
    virtual nb::object get_current_value() const;

    /**
     * @brief Gets the raw string value
     *
     * Returns the raw string representation of the accumulated value
     * without any type conversion.
     *
     * @return The raw string value
     */
    virtual std::string get_raw_value() const;

    /**
     * @brief Sets the raw value
     *
     * @param value The new raw value
     */
    virtual void set_raw_value(const std::optional<std::string> &value) { raw_value_ = value; }

    /**
     * @brief Sets the raw value
     *
     * @param value The new raw value
     */
    virtual std::optional<std::string> get_internal_raw_value() const { return raw_value_; }

    //=========================================================================
    // Input State Management
    //=========================================================================

    /**
     * @brief Gets the remaining input to be processed
     *
     * @return The remaining input string, if any
     */
    virtual std::optional<std::string> get_remaining_input() const { return remaining_input_; }

    /**
     * @brief Sets the remaining input
     *
     * @param input The new remaining input
     */
    virtual void set_remaining_input(const std::optional<std::string> &input) { remaining_input_ = input; }

    //=========================================================================
    // History Management
    //=========================================================================

    /**
     * @brief Gets the token IDs that have been consumed by this stepper
     *
     * @return The vector of token IDs
     */
    virtual std::vector<uint32_t> get_token_ids_history() const;

    /**
     * @brief Gets the history of accepted steppers
     *
     * @return Vector of steppers in the history
     */
    virtual const std::vector<nb::ref<Stepper>> &get_history() const { return history_; }

    /**
     * @brief Sets the history vector
     *
     * @param history The new history vector
     */
    virtual void set_history(const std::vector<nb::ref<Stepper>> &history) { history_ = history; }

    /**
     * @brief Adds a stepper to the history
     *
     * This is called when a transition completes successfully.
     *
     * @param stepper The stepper to add to history
     */
    virtual void add_to_history(nb::ref<Stepper> stepper)
    {
        auto new_consumed_character_count = get_consumed_character_count() + stepper->get_consumed_character_count();
        set_consumed_character_count(new_consumed_character_count);
        history_.push_back(stepper);
    }

    //=========================================================================
    // State Management
    //=========================================================================

    /**
     * @brief Gets the identifier for this stepper
     *
     * @return The identifier
     */
    virtual std::optional<std::string> get_identifier() const
    {
        if (this->sub_stepper_)
        {
            auto sub_identifier = this->sub_stepper_->get_identifier();
            if (sub_identifier)
            {
                return sub_identifier;
            }
        }
        return state_machine_->get_identifier();
    }

    /**
     * @brief Gets the current state ID
     *
     * @return The current state
     */
    virtual StateId get_current_state() const { return current_state_; }

    /**
     * @brief Sets the current state
     *
     * @param state The new current state
     */
    virtual void set_current_state(StateId state) { current_state_ = state; }

    /**
     * @brief Gets the target state for an in-progress transition
     *
     * @return The target state, if a transition is in progress
     */
    virtual std::optional<StateId> get_target_state() const { return target_state_; }

    /**
     * @brief Sets the target state
     *
     * @param state The new target state
     */
    virtual void set_target_state(std::optional<StateId> state) { target_state_ = state; }

    /**
     * @brief Gets the count of consumed characters
     *
     * @return The number of characters consumed
     */
    virtual size_t get_consumed_character_count() const { return consumed_character_count_; }

    /**
     * @brief Sets the consumed character count
     *
     * @param count The new consumed character count
     */
    virtual void set_consumed_character_count(size_t count) { consumed_character_count_ = count; }

    /**
     * @brief Sets the token IDs history
     *
     * @param token_ids The new token IDs history
     */
    virtual void set_token_ids_history(const std::vector<uint32_t> &token_ids) { token_ids_history_ = token_ids; }

    /**
     * @brief Sets the token IDs
     *
     * @param token_ids The new token IDs
     */
    virtual void append_token_ids(const std::vector<uint32_t> &token_ids);

    /**
     * @brief Gets the token safe output for this stepper
     *
     * @param decode_function The function to decode token IDs to strings
     * @return The token safe output
     */
    virtual std::string get_token_safe_output(std::function<std::string(std::vector<int>)> decode_function) const;

    //=========================================================================
    // State Machine & Sub-Stepper Management
    //=========================================================================

    /**
     * @brief Gets the associated state machine
     *
     * @return Reference to the state machine
     */
    virtual nb::ref<StateMachine> get_state_machine() const { return state_machine_; }

    /**
     * @brief Sets the state machine
     *
     * @param machine The new state machine
     */
    virtual void set_state_machine(nb::ref<StateMachine> machine) { state_machine_ = machine; }

    /**
     * @brief Gets the current sub-stepper
     *
     * The sub-stepper handles a nested portion of the state traversal.
     *
     * @return Reference to the sub-stepper, if any
     */
    virtual nb::ref<Stepper> get_sub_stepper() const { return sub_stepper_; }

    /**
     * @brief Sets the sub-stepper
     *
     * @param stepper The new sub-stepper
     */
    virtual void set_sub_stepper(nb::ref<Stepper> stepper) { sub_stepper_ = stepper; }

    //=========================================================================
    // Operators & String Representation
    //=========================================================================

    /**
     * @brief Equality comparison operator
     *
     * Compares two steppers based on their state and accumulated value.
     *
     * @param other The stepper to compare with
     * @return true if both steppers are equal
     */
    virtual bool operator==(const Stepper &other) const;

    /**
     * @brief Less-than comparison operator
     *
     * Provides an ordering for steppers, useful for containers like sets.
     *
     * @param other The stepper to compare with
     * @return true if this stepper is less than the other
     */
    virtual bool operator<(const Stepper &other) const;

    /**
     * @brief Converts the stepper to a compact string representation
     *
     * @return A string representation of the stepper
     */
    virtual std::string to_string() const
    {
        std::string prefix = has_reached_accept_state() ? "✅ " : "";
        std::string shortened_header = prefix + state_machine_->to_string() + ".Stepper";
        std::string state_info = "State: " + StateMachine::state_to_string(current_state_);
        if (target_state_)
        {
            if (current_state_ == *target_state_)
            {
                state_info += " 🔄 " + StateMachine::state_to_string(current_state_);
            }
            else
            {
                state_info += " ➔ " + StateMachine::state_to_string(*target_state_);
            }
        }
        std::string single_line = shortened_header + " (" + state_info + ")";
        return single_line;
    }

    virtual std::string to_readable() const
    {
        std::string prefix = has_reached_accept_state() ? "✅ " : "";
        std::string header = prefix + state_machine_->to_string() + ".Stepper";

        std::vector<std::string> info_parts;

        std::string state_info;
        if (current_state_ == state_machine_->start_state_)
        {
            state_info = "State: \033[34m▶️ " + StateMachine::state_to_string(current_state_) + "\033[0m"; // Blue, Start symbol
        }
        else if (std::find(state_machine_->end_states_.begin(), state_machine_->end_states_.end(), current_state_) != state_machine_->end_states_.end())
        {
            state_info = "State: \033[32m🏁 " + StateMachine::state_to_string(current_state_) + "\033[0m"; // Green, End symbol
        }
        else
        {
            state_info = "State: " + StateMachine::state_to_string(current_state_); // default
        }

        if (target_state_)
        {
            if (current_state_ == *target_state_ && this->can_accept_more_input())
            {
                state_info += " 🔄 " + StateMachine::state_to_string(current_state_);
            }
            else if (current_state_ != *target_state_)
            {
                state_info += " ➔ " + StateMachine::state_to_string(*target_state_);
            }
        }
        info_parts.push_back(state_info);

        std::string current_value = this->get_raw_value();
        if (current_value.find('\n') != std::string::npos)
        {
            std::string escaped_str = "";
            for (char c : current_value)
            {
                if (c == '\n')
                {
                    escaped_str += "\\n";
                }
                else
                {
                    escaped_str += c;
                }
            }
            current_value = escaped_str;
        }
        if (!current_value.empty())
        {
            info_parts.push_back("Value: \033[32m" + current_value + "\033[0m");
        }

        if (auto remaining_input = this->get_remaining_input())
        {
            if (remaining_input->find('\n') != std::string::npos)
            {
                std::string escaped_str = "";
                for (char c : *remaining_input)
                {
                    if (c == '\n')
                    {
                        escaped_str += "\\n";
                    }
                    else
                    {
                        escaped_str += c;
                    }
                }
                *remaining_input = escaped_str;
            }
            info_parts.push_back("Remaining input: \033[33m" + *remaining_input + "\033[0m");
        }

        if (sub_stepper_)
        {
            std::string transition_repr = sub_stepper_->to_readable();
            if (transition_repr.find('\n') == std::string::npos &&
                transition_repr.length() < 40)
            {
                info_parts.push_back("Transition: " + transition_repr);
            }
            else
            {
                std::string indented_transition = "  " + transition_repr;
                std::string indent = "  ";
                for (size_t pos = 0;
                     (pos = indented_transition.find('\n', pos)) != std::string::npos;
                     pos += indent.length() + 1)
                {
                    indented_transition.replace(pos, 1, "\n" + indent);
                }
                info_parts.push_back("Transition:\n" + indent + indented_transition);
            }
        }

        std::string single_line =
            header + " (" +
            std::accumulate(info_parts.begin(), info_parts.end(), std::string(),
                            [](const std::string &a, const std::string &b)
                            {
                                return a.empty() ? b : a + ", " + b;
                            }) +
            ")";
        if (single_line.length() <= 80)
        {
            return single_line;
        }

        std::ostringstream oss;
        oss << header << " {\n";
        for (auto &part : info_parts)
        {
            oss << "  " << part << "\n";
        }
        oss << "}";
        return oss.str();
    }

protected:
    //=========================================================================
    // Member Variables
    //=========================================================================

    /** History of steppers that led to the current state */
    std::vector<nb::ref<Stepper>> history_;

    /** Token IDs that have been consumed by this stepper */
    std::vector<uint32_t> token_ids_history_;

    /** Number of characters consumed by this stepper */
    size_t consumed_character_count_;

    /** Current state ID within the state machine */
    StateId current_state_;

    /** Raw accumulated value as a string */
    std::optional<std::string> raw_value_;

    /** Any remaining input that hasn't been consumed yet */
    std::optional<std::string> remaining_input_;

    /** Reference to the associated state machine */
    nb::ref<StateMachine> state_machine_;

    /** Target state for in-progress transitions */
    std::optional<StateId> target_state_;

    /** Sub-stepper handling a nested state machine traversal */
    nb::ref<Stepper> sub_stepper_;

private:
    //=========================================================================
    // Helper Methods
    //=========================================================================

    /**
     * @brief Calculates the length of a UTF-8 string in characters
     *
     * Properly counts characters in UTF-8 encoded strings, accounting for
     * multi-byte character sequences.
     *
     * @param utf8_str The UTF-8 encoded string
     * @return The number of characters (code points) in the string
     */
    size_t utf8_string_length(const std::string &utf8_str)
    {
        size_t length = 0;
        size_t i = 0;

        while (i < utf8_str.size())
        {
            unsigned char c = static_cast<unsigned char>(utf8_str[i]);
            if (c <= 0x7F)
            { // 1-byte sequence
                i += 1;
            }
            else if (c <= 0xDF && i + 1 < utf8_str.size())
            { // 2-byte sequence
                i += 2;
            }
            else if (c <= 0xEF && i + 2 < utf8_str.size())
            { // 3-byte sequence
                i += 3;
            }
            else if (i + 3 < utf8_str.size())
            { // 4-byte sequence
                i += 4;
            }
            else
            { // Incomplete sequence, treat as single byte
                i += 1;
            }
            length++;
        }
        return length;
    }

    /**
     * @brief Converts a nlohmann::json object to a nanobind Python object
     *
     * Recursively converts JSON data to Python objects, handling all JSON types
     * (null, boolean, number, string, array, object).
     *
     * @param j The JSON value to convert
     * @return The equivalent Python object
     */
    static nb::object from_json(const nlohmann::json &j)
    {
        if (j.is_null())
        {
            return nb::none();
        }
        else if (j.is_boolean())
        {
            return nb::bool_(j.get<bool>());
        }
        else if (j.is_number_integer())
        {
            return nb::int_(j.get<long>());
        }
        else if (j.is_number_float())
        {
            return nb::float_(j.get<double>());
        }
        else if (j.is_string())
        {
            return nb::str(j.get<std::string>().c_str());
        }
        else if (j.is_array())
        {
            nb::list obj;
            for (const auto &el : j)
            {
                obj.append(from_json(el));
            }
            return std::move(obj);
        }
        else // Object
        {
            nb::dict obj;
            for (nlohmann::json::const_iterator it = j.cbegin(); it != j.cend(); ++it)
            {
                obj[nb::str(it.key().c_str())] = from_json(it.value());
            }
            return std::move(obj);
        }
    }
};
