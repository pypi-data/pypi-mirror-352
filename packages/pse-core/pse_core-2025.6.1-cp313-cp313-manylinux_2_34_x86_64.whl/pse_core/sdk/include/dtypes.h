#pragma once

#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>
#include <Eigen>

namespace nb = nanobind;
namespace nanobind::detail
{
    template <>
    struct dtype_traits<Eigen::bfloat16>
    {
        static constexpr dlpack::dtype value{
            (uint8_t)dlpack::dtype_code::UInt, // type code || not sure why but bfloat16's dtype code is UInt, not Float
            16,                                // size in bits
            1                                  // lanes (simd), usually set to 1
        };
        static constexpr auto name = const_name("bfloat16");
    };

    template <>
    struct dtype_traits<Eigen::half>
    {
        static constexpr dlpack::dtype value{
            (uint8_t)dlpack::dtype_code::Float, // type code
            16,                                 // size in bits
            1                                   // lanes (simd), usually set to 1
        };
        static constexpr auto name = const_name("float16");
    };

    template <>
    struct dtype_traits<float>
    {
        static constexpr dlpack::dtype value{
            (uint8_t)dlpack::dtype_code::Float,
            32,
            1};
        static constexpr auto name = const_name("float32");
    };
    template <>
    struct dtype_traits<int8_t>
    {
        static constexpr dlpack::dtype value{
            (uint8_t)dlpack::dtype_code::Int, // assuming it's a signed 8-bit integer
            8,                                // size in bits
            1                                 // lanes
        };
        static constexpr auto name = const_name("int8");
    };
}
