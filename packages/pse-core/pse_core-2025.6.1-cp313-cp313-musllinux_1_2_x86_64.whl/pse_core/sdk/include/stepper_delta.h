#pragma once

#include <nanobind/nanobind.h>
#include <nanobind/intrusive/ref.h>
#include <nanobind/stl/string.h>
#include <tsl/htrie_map.h>
#include <set>
#include <string>
#include <tuple>
#include <vector>
#include <optional>
#include <unordered_map>
#include <cstdint>

namespace nb = nanobind;

// forward declaration
class Stepper;

/**
 * @brief Represents the result of a state transition after consuming a token
 *
 * StepperDelta encapsulates the outcome of advancing a Stepper with a token,
 * including metadata about the transition. It serves as the core data structure
 * for tracking and comparing possible paths through the state machine, enabling
 * sophisticated path selection when multiple valid transitions exist.
 *
 * Key responsibilities:
 * - Track steppers after token consumption
 * - Record metadata about transitions (token, healing status, scores)
 * - Compare and select optimal paths based on multiple criteria
 * - Support token healing by tracking partially matched tokens
 */
class StepperDelta
{
public:
    /**
     * @brief Constructs a new StepperDelta
     *
     * @param stepper The stepper after consuming a token
     * @param token The token that was consumed
     * @param was_healed Whether token healing was applied
     */
    StepperDelta(nb::ref<Stepper> stepper, std::string token, bool was_healed)
        : stepper_(stepper), token_(std::move(token)), was_healed_(was_healed) {}

    //=========================================================================
    // Core Accessors and Mutators
    //=========================================================================

    /**
     * @brief Gets the stepper after transition
     *
     * @return Reference to the stepper
     */
    nb::ref<Stepper> stepper() const { return stepper_; }

    /**
     * @brief Sets the stepper
     *
     * @param stepper New stepper reference
     */
    void set_stepper(nb::ref<Stepper> stepper) { stepper_ = stepper; }

    /**
     * @brief Gets the consumed token
     *
     * @return The token string
     */
    const std::string &token() const { return token_; }

    /**
     * @brief Sets the token
     *
     * @param token New token string
     */
    void set_token(std::string token) { token_ = std::move(token); }

    /**
     * @brief Checks if token healing was applied
     *
     * @return true if the token was healed
     */
    bool was_healed() const { return was_healed_; }

    /**
     * @brief Sets the healing status
     *
     * @param was_healed New healing status
     */
    void set_was_healed(bool was_healed) { was_healed_ = was_healed; }

    /**
     * @brief Gets the associated token ID
     *
     * @return The token ID if available
     */
    std::optional<uint32_t> token_id() const { return token_id_; }

    /**
     * @brief Sets the token ID
     *
     * @param token_id The token ID
     */
    void set_token_id(uint32_t token_id) { token_id_ = token_id; }

    /**
     * @brief Gets the score of this transition
     *
     * Higher scores indicate more probable transitions.
     *
     * @return The score if available
     */
    std::optional<float> score() const { return score_; }

    /**
     * @brief Sets the score
     *
     * @param score The new score
     */
    void set_score(float score) { score_ = score; }

    //=========================================================================
    // Path Selection and Comparison
    //=========================================================================

    /**
     * @brief Selects the optimal path from multiple candidates
     *
     * Implements a sophisticated path selection algorithm that chooses the best
     * token path based on a hierarchical set of criteria:
     * 1. Accepted states (highest priority)
     * 2. Non-healed tokens preferred over healed ones
     * 3. Higher scores
     * 4. Longer tokens (when scores are equal)
     *
     * @param steppers Set of StepperDelta candidates
     * @param vocab Vocabulary mapping from tokens to token IDs
     * @param multi_token_mapping Optional mapping for multi-token sequences
     * @return Tuple of selected token IDs and corresponding steppers
     */
    static std::tuple<std::vector<uint32_t>, std::vector<nb::ref<Stepper>>> choose_best_path(
        const std::set<StepperDelta>& steppers,
        const tsl::htrie_map<char, std::vector<uint32_t>> &vocab,
        const std::optional<std::unordered_map<uint32_t, std::vector<uint32_t>>> &multi_token_mapping
    );

    /**
     * @brief Checks if this path is "attractive" for further exploration
     *
     * A path is considered attractive if it either:
     * - Reaches an accept state
     * - Did not require token healing
     *
     * @return true if the path should be preferred
     */
    bool is_attractive_path() const;

    /**
     * @brief Less-than comparison operator
     *
     * Provides an ordering for StepperDelta objects, useful for containers like sets.
     *
     * @param other The StepperDelta to compare with
     * @return true if this object is less than the other
     */
    bool operator<(const StepperDelta &other) const;

    /**
     * @brief Gets a string representation
     *
     * @return String describing this StepperDelta
     */
    std::string to_string() const;
protected:
    //=========================================================================
    // Member Variables
    //=========================================================================

    /** The stepper after consuming a token */
    nb::ref<Stepper> stepper_;

    /** The token that was consumed */
    std::string token_;

    /** Whether token healing was applied */
    bool was_healed_;

    /** The score/probability of this transition */
    std::optional<float> score_;

    /** The associated token ID */
    std::optional<uint32_t> token_id_;
};
