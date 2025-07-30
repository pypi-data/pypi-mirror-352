#pragma once
#include "stepper.h"
#include <nanobind/trampoline.h>

/**
 * @brief Trampoline class that enables subclassing Stepper in Python
 *
 * The PyStepper class serves as a bridge between C++ and Python, allowing Python code
 * to override virtual methods in the Stepper class. It uses nanobind's trampoline mechanism
 * to route virtual method calls to Python implementations when a Stepper is subclassed in Python.
 *
 * This enables extending the state machine traversal system with custom behavior defined in Python,
 * while still maintaining the performance benefits of the C++ core implementation.
 */
class PyStepper : public Stepper
{
public:
    /**
     * Declare this class as a trampoline for Stepper with 15 overridable methods
     */
    NB_TRAMPOLINE(Stepper, 18);

    //=========================================================================
    // Core Stepper Operations
    //=========================================================================

    /**
     * @brief Creates a copy of this stepper (Python override)
     *
     * Routes calls to the Python implementation of clone() if overridden.
     *
     * @return A new stepper instance with the same state
     */
    nb::ref<Stepper> clone() const override { NB_OVERRIDE(clone); }

    /**
     * @brief Consumes a token and advances the stepper (Python override)
     *
     * Routes calls to the Python implementation of consume() if overridden.
     *
     * @param token The token string to consume
     * @return A vector of new steppers representing possible paths
     */
    std::vector<nb::ref<Stepper>> consume(std::string token) override { NB_OVERRIDE(consume, token); }

    /**
     * @brief Adds a stepper to the history (Python override)
     *
     * Routes calls to the Python implementation of add_to_history() if overridden.
     *
     * @param stepper The stepper to add to history
     */
    void add_to_history(nb::ref<Stepper> stepper) override { NB_OVERRIDE(add_to_history, stepper); }

    //=========================================================================
    // State Check Methods
    //=========================================================================

    /**
     * @brief Checks if this stepper accepts any token input (Python override)
     *
     * Routes calls to the Python implementation of accepts_any_token() if overridden.
     *
     * @return true if any token is valid from the current state
     */
    bool accepts_any_token() const override { NB_OVERRIDE(accepts_any_token); }

    /**
     * @brief Checks if this stepper can accept more input (Python override)
     *
     * Routes calls to the Python implementation of can_accept_more_input() if overridden.
     *
     * @return true if the stepper can continue consuming tokens
     */
    bool can_accept_more_input() const override { NB_OVERRIDE(can_accept_more_input); }

    /**
     * @brief Checks if this stepper has reached an accept state (Python override)
     *
     * Routes calls to the Python implementation of has_reached_accept_state() if overridden.
     *
     * @return true if the current state is an accept state
     */
    bool has_reached_accept_state() const override { NB_OVERRIDE(has_reached_accept_state); }

    /**
     * @brief Checks if this stepper is currently within a value (Python override)
     *
     * Routes calls to the Python implementation of is_within_value() if overridden.
     *
     * @return true if the stepper is accumulating a value
     */
    bool is_within_value() const override { NB_OVERRIDE(is_within_value); }

    //=========================================================================
    // Step Control Methods
    //=========================================================================

    /**
     * @brief Determines if this stepper should branch (Python override)
     *
     * Routes calls to the Python implementation of should_branch() if overridden.
     *
     * @return true if the stepper should explore multiple paths
     */
    bool should_branch() const override { NB_OVERRIDE(should_branch); }

    /**
     * @brief Determines if the stepper should complete its step (Python override)
     *
     * Routes calls to the Python implementation of should_complete_step() if overridden.
     *
     * @return true if the stepper should complete its current step
     */
    bool should_complete_step() const override { NB_OVERRIDE(should_complete_step); }

    /**
     * @brief Determines if the stepper should process a token (Python override)
     *
     * Routes calls to the Python implementation of should_start_step() if overridden.
     *
     * @param token The token to evaluate
     * @return true if the stepper should start processing this token
     */
    bool should_start_step(const std::string& token) const override { NB_OVERRIDE(should_start_step, token); }

    //=========================================================================
    // Value Handling Methods
    //=========================================================================

    /**
     * @brief Gets the final state of the stepper (Python override)
     *
     * Routes calls to the Python implementation of get_final_state() if overridden.
     *
     * @return A vector of final steppers
     */
    std::vector<nb::ref<Stepper>> get_final_state() override { NB_OVERRIDE(get_final_state); }
    /**
     * @brief Gets the current parsed value (Python override)
     *
     * Routes calls to the Python implementation of get_current_value() if overridden.
     *
     * @return A Python object representing the current value
     */
    nb::object get_current_value() const override { NB_OVERRIDE(get_current_value); }

    /**
     * @brief Gets the raw string value (Python override)
     *
     * Routes calls to the Python implementation of get_raw_value() if overridden.
     *
     * @return The raw string value
     */
    std::string get_raw_value() const override { NB_OVERRIDE(get_raw_value); }

    /**
     * @brief Gets valid token continuations (Python override)
     *
     * Routes calls to the Python implementation of get_valid_continuations() if overridden.
     *
     * @return A vector of valid continuation strings
     */
    std::vector<std::string> get_valid_continuations() const override { NB_OVERRIDE(get_valid_continuations); }

    /**
     * @brief Gets invalid token continuations (Python override)
     *
     * Routes calls to the Python implementation of get_invalid_continuations() if overridden.
     *
     * @return A vector of invalid continuation strings
     */
    std::vector<std::string> get_invalid_continuations() const override { NB_OVERRIDE(get_invalid_continuations); }

    //=========================================================================
    // String Representation
    //=========================================================================

    /**
     * @brief Converts the stepper to a readable string (Python override)
     *
     * Routes calls to the Python implementation of __repr__() if overridden.
     *
     * @return A string representation of the stepper
     */
    std::string to_readable() const override { NB_OVERRIDE_NAME("__repr__", to_readable); }

    /**
     * @brief Gets the identifier for this stepper (Python override)
     *
     * Routes calls to the Python implementation of get_identifier() if overridden.
     *
     * @return The identifier
     */
    std::optional<std::string> get_identifier() const override { NB_OVERRIDE(get_identifier); }

    /**
     * @brief Gets the token safe output for this stepper (Python override)
     *
     * Routes calls to the Python implementation of get_token_safe_output() if overridden.
     *
     * @param decode_function The function to decode token IDs to strings
     * @return The token safe output
     */
    std::string get_token_safe_output(std::function<std::string(std::vector<int>)> decode_function) const override { NB_OVERRIDE(get_token_safe_output, decode_function); }
};
