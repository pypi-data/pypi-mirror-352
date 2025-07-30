#pragma once

#include "dtypes.h"
#include "state_machine.h"
#include "stepper.h"
#include "stepper_delta.h"
#include <nanobind/nanobind.h>
#include <nanobind/intrusive/counter.h>
#include <nanobind/intrusive/ref.h>
#include <nanobind/ndarray.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/vector.h>
#include <nanobind/stl/unordered_map.h>
#include <nanobind/stl/tuple.h>
#include <nanobind/stl/optional.h>
#include <optional>
#include <set>
#include <string>
#include <tsl/htrie_map.h>
#include <tuple>
#include <vector>
#include <any>
#include <unordered_map>
#include <memory>
#include <random>
#include <Eigen>

namespace nb = nanobind;

/**
 * @brief Orchestrates token processing and interfaces with language models
 *
 * The Engine class serves as the central coordinator for the PSE core system,
 * managing token consumption, tokenization, and logit processing for language
 * model integration. It acts as the interface between language models and
 * the grammatical constraints defined by StateMachines.
 *
 * Key responsibilities:
 * - Process and modify logit distributions to enforce grammar constraints
 * - Handle token consumption and state machine traversal
 * - Manage vocabulary mappings between token IDs and strings
 * - Support multi-token sequences and token healing
 * - Track active steppers and state machine positions
 * - Determine valid/invalid tokens based on current state
 *
 * The Engine implements two main workflows:
 * 1. Generation: Modifies language model logits to enforce grammatical constraints
 * 2. Parsing: Consumes tokens to validate input against a grammar
 */
class Engine
{
public:
    /**
     * @brief Type definition for token identifiers
     */
    using TokenId = uint32_t;

    /**
     * @brief Maps from token IDs to their string representations
     */
    using ReverseVocabulary = std::unordered_map<TokenId, std::string>;

    /**
     * @brief Maps token IDs to sequences of token IDs
     *
     * Used for handling cases where a single token in the grammar
     * corresponds to multiple tokens in the model's vocabulary.
     */
    using MultiTokenMapping = std::unordered_map<TokenId, std::vector<TokenId>>;

    /**
     * @brief Type for token sampling function
     *
     * Takes a tensor of log probabilities and returns sampled token IDs
     */
    using Sampler = nb::typed<nb::callable, nb::ndarray<nb::ndim<2>>(...)>;

    /**
     * @brief Type for token decoding function
     *
     * Takes a list of token IDs and returns a string
     */
    using DecodeFunction = std::function< std::string(std::vector<int>) >;

    /**
     * @brief Type for token encoding function
     *
     * Takes a string and returns a list of token IDs
     */
    using EncodeFunction = std::function< std::vector<int>(std::string) >;

    //=========================================================================
    // Member Variables
    //=========================================================================

    /** Optional state machine defining the grammar constraints */
    std::optional<nb::ref<StateMachine>> state_machine_;

    /** Active steppers representing current positions in the state machine */
    std::vector<nb::ref<Stepper>> steppers_;

    /** Start and end delimiter strings */
    std::tuple<std::string, std::string> delimiters_;

    /** Mapping of token strings to their token IDs */
    tsl::htrie_map<char, std::vector<TokenId>> vocabulary_;

    /** Mapping of token IDs to their string representations */
    ReverseVocabulary reverse_vocabulary_;

    /** Token decoding function */
    DecodeFunction decode_function_;

    /** Token encoding function */
    EncodeFunction encode_function_;

    /** Mapping for multi-token sequences */
    MultiTokenMapping multi_token_mapping_;

    /** Whether to strictly enforce constraints */
    bool strict_;

    /** Whether to enable multi-token handling */
    bool multi_token_sampling_;

    /** Maximum number of resampling attempts */
    int max_resamples_;

    /** Token IDs that should be treated as control tokens */
    std::vector<TokenId> control_tokens_;

    /**
     * @brief Constructs a new Engine
     *
     * @param raw_vocabulary Mapping from token strings to their token IDs
     * @param encode_function Function to encode strings to token IDs
     * @param decode_function Function to decode token IDs to strings
     * @param strict Whether to strictly enforce constraints (no fallback)
     * @param multi_token_sampling Whether to enable multi-token sequence handling
     * @param max_resamples Maximum number of sampling attempts for a valid token
     * @param control_tokens Token IDs that should be blocked until reaching an accept state
     */
    Engine(
        std::unordered_map<std::string, TokenId> raw_vocabulary,
        EncodeFunction encode_function,
        DecodeFunction decode_function,
        bool strict = false,
        bool multi_token_sampling = true,
        int max_resamples = 5,
        std::vector<TokenId> control_tokens = {});

    /**
     * @brief Virtual destructor
     */
    virtual ~Engine() = default;

    //=========================================================================
    // Logit Processing Methods
    //=========================================================================

    /**
     * @brief Gets a token mask for the current state
     *
     * @param vocab_size The vocabulary size
     * @return Vector of boolean values indicating valid tokens
     */
    std::vector<bool> compute_token_mask(size_t vocab_size);

    /**
     * @brief Masks invalid tokens in logit tensor
     *
     * Sets probabilities of invalid tokens to negative infinity,
     * enforcing grammatical constraints during sampling.
     *
     * @param logits Tensor of token logits [batch_size x vocab_size]
     * @return Modified tensor with invalid tokens masked
     */
    nb::ndarray<> mask_invalid_tokens(nb::ndarray<> logits);

    /**
     * @brief Selects next tokens based on logits and sampling
     *
     * Samples tokens, tests if they're valid by advancing steppers,
     * and selects the best path based on multiple criteria.
     *
     * @param logprobs Tensor of log probabilities [1 x vocab_size]
     * @param sampler Function to sample from the log probabilities
     * @return Vector of selected token IDs
     */
    std::vector<TokenId> select_next_tokens(nb::ndarray<> logprobs, Sampler sampler);

    //=========================================================================
    // Token Validation Methods
    //=========================================================================

    /**
     * @brief Gets valid token sequences from current state
     *
     * @return Set of valid token sequences as vectors of strings
     */
    std::set<std::vector<std::string>> get_valid_tokens();

    /**
     * @brief Converts valid token strings to token IDs
     *
     * Also populates multi_token_mapping_ for multi-token sequences.
     *
     * @param valid_tokens Set of valid token sequences
     * @return Set of valid token IDs
     */
    std::set<TokenId> get_valid_token_ids(std::set<std::vector<std::string>> valid_tokens);

    /**
     * @brief Gets invalid token IDs based on current state
     *
     * @return Set of invalid token IDs
     */
    std::set<TokenId> get_invalid_token_ids();

    //=========================================================================
    // Token Consumption Methods
    //=========================================================================

    /**
     * @brief Consumes a single token and advances steppers
     *
     * This is the core method for token processing during parsing.
     *
     * @param token_id The token ID to consume
     * @param token_healing Whether to attempt to repair partial token matches
     * @return Vector of StepperDelta objects representing possible new states
     */
    std::vector<StepperDelta> consume_token(TokenId token_id, bool token_healing = true);

    /**
     * @brief Consumes raw text directly
     *
     * Parses the text without tokenization, using the state machine directly.
     *
     * @param raw_input The text to consume
     * @param token_healing Whether to attempt token healing
     */
    void consume_text(std::string &raw_input, bool token_healing = false)
    {
        auto new_steppers = std::vector<nb::ref<Stepper>>();
        for (const auto &step_result : StateMachine::advance_all_sequential(steppers_, raw_input, vocabulary_, token_healing))
        {
            new_steppers.push_back(step_result.stepper());
        }

        // update the steppers with the consumed token ids
        // the steppers have already consumed the tokens,
        // we just need to update them with the token ids
        // they just consumed.
        // this is normally done in the sample loop, but
        // we need to do it here because we are consuming raw text.
        for (auto &stepper : new_steppers)
        {
            auto token_ids = this->encode_function_(raw_input);
            //cast token_ids to std::vector<uint32_t>
            std::vector<uint32_t> token_ids_vector(token_ids.begin(), token_ids.end());
            stepper->append_token_ids(token_ids_vector);
        }
        this->steppers_ = new_steppers;
    }

    /**
     * @brief Consumes a single token and advances steppers
     *
     * This is a convenience method that consumes a single token and advances
     * the steppers. It is equivalent to calling consume_token with the same
     * token ID and token healing.
     *
     * @param token_id The token ID to consume
     * @param token_healing Whether to attempt to repair partial token matches
     */
    std::optional<TokenId> consume(TokenId token_id, bool token_healing = true)
    {
        auto new_steppers = std::vector<nb::ref<Stepper>>();
        for (const auto &step_result : consume_token(token_id, token_healing))
        {
            auto stepper = step_result.stepper();
            stepper->append_token_ids({token_id});
            new_steppers.push_back(stepper);
        }
        if (new_steppers.size() == 0)
        {
            return std::nullopt;
        }
        this->steppers_ = new_steppers;
        return token_id;
    }

    //=========================================================================
    // State Query Methods
    //=========================================================================

    /**
     * @brief Gets the live token safe output for this stepper
     *
     * @param decode_function The function to decode token IDs to strings
     * @return The live token safe output
     */
    std::optional<std::tuple<std::string, std::string>> get_live_token_safe_output(std::function<std::string(std::vector<int>)> decode_function) const;

    /**
     * @brief Retrieves the current state identifier.
     *
     * This method checks the current state of all active steppers and returns a common
     * state identifier if and only if all steppers are in the same state. If the engine
     * does not have an associated state machine, or if the steppers are in different states,
     * the method returns an empty optional.
     *
     * @return An optional string containing the common state identifier, or an empty optional
     *         if no state machine is present, no identifiers are found, or if steppers are in
     *         different states.
     */
    std::optional<std::string> get_current_state() const
    {
        // Return std::nullopt if no state machine is associated.
        if (!state_machine_)
        {
            return std::nullopt;
        }

        // Use a variable to store the common state identifier.
        std::optional<std::string> common_state;

        // Iterate through all active steppers.
        for (const auto& stepper : steppers_)
        {
            // Retrieve the identifier for the current stepper.
            const auto& id = stepper->get_identifier();

            // If the stepper has no identifier, skip it.
            if (!id)
            {
                continue;
            }
            // If no common state has been found yet, initialize it with the current identifier.
            if (!common_state.has_value())
            {
                common_state = id;
            }
            // If a common state exists, check if the current identifier matches it.
            else if (*common_state != *id)
            {
                // If identifiers differ, return std::nullopt, indicating no single common state.
                return std::nullopt;
            }
        }

        // Return the common state identifier (or std::nullopt if no steppers or no identifiers).
        return common_state;
    }

    /**
     * @brief Checks if any stepper has reached an accept state
     *
     * @return true if any stepper has reached an accept state
     */
    bool has_reached_accept_state() const
    {
        if (!state_machine_)
        {
            return false;
        }

        for (auto &w : steppers_)
        {
            if (w->has_reached_accept_state())
            {
                return true;
            }
        }
        return false;
    }


    /**
     * @brief Resets the engine to initial state
     *
     * @param hard_reset If true, removes the state machine as well
     */
    void reset(bool hard_reset = false)
    {
        if (hard_reset)
        {
            state_machine_ = std::nullopt;
            steppers_.clear();
        }
        else if (state_machine_)
        {
            steppers_ = (*state_machine_)->get_steppers();
        }
    }

    /**
     * @brief Gets whether the engine is in strict mode
     *
     * @return true if in strict mode
     */
    bool is_strict() const { return this->strict_; }

    /**
     * @brief Gets a human-readable representation of the engine state
     *
     * @return String representation showing all steppers
     */
    virtual std::string to_readable() const
    {
        std::string result = "\n";
        bool first = true;
        for (auto &w : steppers_)
        {
            if (!first)
            {
                result += ", ";
            }
            result += w->to_readable();
            first = false;
        }
        result += "\n";
        return result;
    }
    //=========================================================================
    // Tokenization Methods
    //=========================================================================

    /**
     * @brief Breaks text into valid token sequences
     *
     * Finds all possible ways to tokenize the input text based on vocabulary.
     *
     * @param text The text to tokenize
     * @return Set of valid token sequences
     */
    std::set<std::vector<std::string>> break_into_tokens(const std::string& text) const;

    /**
     * @brief Selects a random token ID from possible options
     *
     * Used for multi-token handling when multiple IDs map to the same string.
     *
     * @param possible_token_ids Vector of possible token IDs
     * @return A randomly selected token ID
     */
    static TokenId get_random_token_id(std::vector<TokenId> possible_token_ids)
    {
        static std::mt19937 rng{std::random_device{}()};
        return possible_token_ids[std::uniform_int_distribution<size_t>{0, possible_token_ids.size() - 1}(rng)];
    }

private:
    /**
     * @brief Populates multi-token mapping from a sequence of tokens
     *
     * @param valid_tokens Vector of token strings forming a sequence
     */
    void populate_multi_token_mapping(const std::vector<std::string>& valid_tokens);

    /**
     * @brief Samples a token using the provided sampler
     *
     * @param log_probs Tensor of log probabilities
     * @param sampler Sampling function
     * @return Sampled token ID or nullopt if sampling failed
     */
    std::optional<TokenId> sample_token(nb::ndarray<> &log_probs, Engine::Sampler &sampler);

    /**
     * @brief Masks a specific token ID in a tensor
     *
     * Sets the probability of a token to negative infinity across different dtypes.
     *
     * @param tensor Tensor to modify
     * @param batch_id Batch index
     * @param token_id Token ID to mask
     * @param score Score to unmask the token to
     */
    void unmask_token(nb::ndarray<> tensor, size_t batch_id, size_t token_id, float score) const
    {
        auto type = tensor.dtype();
        if (type == nb::dtype<Eigen::bfloat16>())
        {
            auto tensor_view = tensor.view<Eigen::bfloat16, nb::ndim<2>>();
            tensor_view(batch_id, token_id) = static_cast<Eigen::bfloat16>(score);
        }
        else if (type == nb::dtype<Eigen::half>())
        {
            auto tensor_view = tensor.view<Eigen::half, nb::ndim<2>>();
            tensor_view(batch_id, token_id) = static_cast<Eigen::half>(score);
        }
        else if (type == nb::dtype<float>())
        {
            auto tensor_view = tensor.view<float, nb::ndim<2>>();
            tensor_view(batch_id, token_id) = static_cast<float>(score);
        }
        else if (type == nb::dtype<int8_t>())
        {
            auto tensor_view = tensor.view<int8_t, nb::ndim<2>>();
            tensor_view(batch_id, token_id) = score;
        }
        else
        {
            throw std::runtime_error("Unsupported tensor dtype for masking");
        }
    }

    /**
     * @brief Masks a specific token ID in a tensor
     *
     * Sets the probability of a token to negative infinity across different dtypes.
     *
     * @param tensor Tensor to modify
     * @param batch_id Batch index
     * @param token_id Token ID to mask
     * @return Original score before masking
     */
    float mask_invalid_id(nb::ndarray<> tensor, size_t batch_id, size_t token_id) const
    {
        auto type = tensor.dtype();
        float score;
        if (type == nb::dtype<Eigen::bfloat16>())
        {
            auto tensor_view = tensor.view<Eigen::bfloat16, nb::ndim<2>>();
            score = tensor_view(batch_id, token_id);
            tensor_view(batch_id, token_id) = -std::numeric_limits<Eigen::bfloat16>::infinity();
        }
        else if (type == nb::dtype<Eigen::half>())
        {
            auto tensor_view = tensor.view<Eigen::half, nb::ndim<2>>();
            score = tensor_view(batch_id, token_id);
            tensor_view(batch_id, token_id) = -std::numeric_limits<Eigen::half>::infinity();
        }
        else if (type == nb::dtype<float>())
        {
            auto tensor_view = tensor.view<float, nb::ndim<2>>();
            score = tensor_view(batch_id, token_id);
            tensor_view(batch_id, token_id) = -std::numeric_limits<float>::infinity();
        }
        else if (type == nb::dtype<int8_t>())
        {
            auto tensor_view = tensor.view<int8_t, nb::ndim<2>>();
            score = tensor_view(batch_id, token_id);
            tensor_view(batch_id, token_id) = std::numeric_limits<int8_t>::min();
        }
        else
        {
            throw std::runtime_error("Unsupported tensor dtype for masking");
        }
        return score;
    }
};
