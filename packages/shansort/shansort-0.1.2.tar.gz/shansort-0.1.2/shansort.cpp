#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <string>
#include <algorithm>
#include <cstring>
#include <cstdint>

namespace py = pybind11;

// Helpers for double <-> sortable uint64
inline uint64_t float_to_key(double v) {
    uint64_t x;
    std::memcpy(&x, &v, sizeof(double));
    if (x & (1ULL << 63))  // negative number
        return ~x;          // invert all bits
    else
        return x ^ (1ULL << 63);  // flip sign bit
}

inline double key_to_float(uint64_t k) {
    uint64_t x;
    if (k & (1ULL << 63))  // original positive
        x = k ^ (1ULL << 63);
    else                   // original negative
        x = ~k;
    double v;
    std::memcpy(&v, &x, sizeof(double));
    return v;
}

// Check if sorted
template <typename T>
int check_sorted(const std::vector<T>& data) {
    if (data.size() <= 1) return 1;
    bool asc = true, desc = true;
    for (size_t i = 1; i < data.size(); ++i) {
        if (data[i] < data[i - 1]) asc = false;
        if (data[i] > data[i - 1]) desc = false;
        if (!asc && !desc) return 0;
    }
    return asc ? 1 : (desc ? -1 : 0);
}

// Integer radix sort
std::vector<int64_t> sort_int(std::vector<int64_t> data) {
    int flag = check_sorted(data);
    if (flag == 1) return data;
    if (flag == -1) {
        std::reverse(data.begin(), data.end());
        return data;
    }
    std::vector<uint64_t> keys(data.size());
    for (size_t i = 0; i < data.size(); ++i)
        keys[i] = static_cast<uint64_t>(data[i]) ^ (1ULL << 63);

    std::vector<uint64_t> temp(data.size());
    constexpr int radix = 8, bits = 64, buckets = 1 << radix, passes = bits / radix;

    for (int pass = 0; pass < passes; ++pass) {
        std::vector<size_t> count(buckets + 1, 0);
        size_t shift = pass * radix;
        for (auto k : keys) ++count[((k >> shift) & (buckets - 1)) + 1];
        for (int i = 1; i < buckets + 1; ++i) count[i] += count[i - 1];
        for (auto k : keys) temp[count[(k >> shift) & (buckets - 1)]++] = k;
        keys.swap(temp);
    }

    for (size_t i = 0; i < data.size(); ++i)
        data[i] = static_cast<int64_t>(keys[i] ^ (1ULL << 63));
    return data;
}

// Float radix sort
std::vector<double> sort_double(std::vector<double> data) {
    int flag = check_sorted(data);
    if (flag == 1) return data;
    if (flag == -1) {
        std::reverse(data.begin(), data.end());
        return data;
    }
    std::vector<uint64_t> keys(data.size());
    for (size_t i = 0; i < data.size(); ++i)
        keys[i] = float_to_key(data[i]);

    std::vector<uint64_t> temp(data.size());
    constexpr int radix = 8, bits = 64, buckets = 1 << radix, passes = bits / radix;

    for (int pass = 0; pass < passes; ++pass) {
        std::vector<size_t> count(buckets + 1, 0);
        size_t shift = pass * radix;
        for (auto k : keys) ++count[((k >> shift) & (buckets - 1)) + 1];
        for (int i = 1; i < buckets + 1; ++i) count[i] += count[i - 1];
        for (auto k : keys) temp[count[(k >> shift) & (buckets - 1)]++] = k;
        keys.swap(temp);
    }

    for (size_t i = 0; i < data.size(); ++i)
        data[i] = key_to_float(keys[i]);
    return data;
}

// ASCII string radix sort
std::vector<std::string> sort_string(std::vector<std::string> data) {
    int flag = check_sorted(data);
    if (flag == 1) return data;
    if (flag == -1) {
        std::reverse(data.begin(), data.end());
        return data;
    }
    size_t max_len = 0;
    for (auto& s : data) max_len = std::max(max_len, s.size());

    std::vector<std::string> temp(data.size());
    for (int pos = (int)max_len - 1; pos >= 0; --pos) {
        std::vector<size_t> count(257, 0);
        for (auto& s : data) count[(pos < s.size() ? s[pos] : 0) + 1]++;
        for (int i = 1; i < 257; ++i) count[i] += count[i - 1];
        for (auto& s : data) temp[count[(pos < s.size() ? s[pos] : 0)]++] = s;
        std::swap(data, temp);
    }
    return data;
}

// Unified dispatcher
py::list sort(py::list input) {
    if (py::len(input) == 0)
        return py::list();

    py::object first = input[0];

    if (py::isinstance<py::int_>(first)) {
        std::vector<int64_t> vec = input.cast<std::vector<int64_t>>();
        return py::cast(sort_int(vec));
    } else if (py::isinstance<py::float_>(first)) {
        std::vector<double> vec = input.cast<std::vector<double>>();
        return py::cast(sort_double(vec));
    } else if (py::isinstance<py::str>(first)) {
        std::vector<std::string> vec = input.cast<std::vector<std::string>>();
        return py::cast(sort_string(vec));
    } else {
        throw std::invalid_argument("Unsupported type");
    }
}

PYBIND11_MODULE(shansort, m) {
    m.doc() = "Unified fast sort for int, float, and string using radix sort";
    m.def("sort", &sort, "Sort a list of int, float, or string");
}


