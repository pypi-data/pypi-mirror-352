#pragma once
#include <nanobind/trampoline.h>
#include "state_machine.h"
#include "stepper.h"

/**
 * @brief Trampoline class that enables subclassing StateMachine in Python
 *
 * The PyStateMachine class serves as a bridge between C++ and Python, allowing Python code
 * to override virtual methods in the StateMachine class. It uses nanobind's trampoline
 * mechanism to route virtual method calls to Python implementations when a StateMachine
 * is subclassed in Python.
 *
 * This enables creating custom grammar definitions in Python while maintaining
 * the performance benefits of the C++ core implementation. Python developers can
 * define specialized state machines with custom validation logic, transitions,
 * and behaviors.
 */
class PyStateMachine : public StateMachine
{
    /**
     * Declare this class as a trampoline for StateMachine with 7 overridable methods
     */
    NB_TRAMPOLINE(StateMachine, 7);

    //=========================================================================
    // Stepper Creation and Management Methods
    //=========================================================================

    /**
     * @brief Creates a new stepper for traversing this state machine (Python override)
     *
     * Routes calls to the Python implementation of get_new_stepper() if overridden.
     *
     * @param state Optional starting state
     * @return A new stepper instance
     */
    nb::ref<Stepper> get_new_stepper(std::optional<StateId> state = std::nullopt) override
    {
        NB_OVERRIDE(get_new_stepper, state);
    }

    /**
     * @brief Creates multiple steppers for this state machine (Python override)
     *
     * Routes calls to the Python implementation of get_steppers() if overridden.
     *
     * @param state Optional starting state
     * @return A vector of stepper instances
     */
    std::vector<nb::ref<Stepper>> get_steppers(std::optional<StateId> state = std::nullopt) override
    {
        NB_OVERRIDE(get_steppers, state);
    }

    /**
     * @brief Gets the outgoing edges from a given state (Python override)
     *
     * Routes calls to the Python implementation of get_edges() if overridden.
     *
     * @param state The state to get edges from
     * @return A vector of edges
     */
    std::vector<Edge> get_edges(StateId state) const override
    {
        NB_OVERRIDE(get_edges, state);
    }

    /**
     * @brief Gets possible transitions for a stepper (Python override)
     *
     * Routes calls to the Python implementation of get_transitions() if overridden.
     *
     * @param stepper The stepper to get transitions for
     * @return A vector of (stepper, target state) tuples
     */
    std::vector<std::tuple<nb::ref<Stepper>, StateId>> get_transitions(nb::ref<Stepper> stepper) const override
    {
        NB_OVERRIDE(get_transitions, stepper);
    }

    //=========================================================================
    // Comparison and String Representation
    //=========================================================================

    /**
     * @brief Equality comparison operator (Python override)
     *
     * Routes calls to the Python implementation of __eq__() if overridden.
     *
     * @param other The state machine to compare with
     * @return true if both state machines are equivalent
     */
    bool operator==(nb::ref<StateMachine> other) const override
    {
        NB_OVERRIDE_NAME("__eq__", operator==, other);
    }

    /**
     * @brief Gets a string representation (Python override)
     *
     * Routes calls to the Python implementation of __str__() if overridden.
     *
     * @return String representation
     */
    std::string to_string() const override
    {
        NB_OVERRIDE_NAME("__str__", to_string);
    }

    /**
     * @brief Gets a detailed string representation (Python override)
     *
     * Routes calls to the Python implementation of __repr__() if overridden.
     *
     * @param indentation_level Indentation level for pretty-printing
     * @return Detailed string representation
     */
    std::string to_readable([[maybe_unused]] size_t indentation_level = 0) const override
    {
        NB_OVERRIDE_NAME("__repr__", to_readable);
    }
};
