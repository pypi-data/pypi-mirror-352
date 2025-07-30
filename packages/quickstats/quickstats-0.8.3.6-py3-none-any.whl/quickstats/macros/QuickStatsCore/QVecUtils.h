#ifndef __QVecUtils_H__
#define __QVecUtils_H__

#include <vector>
#include <string>
#include <type_traits>
#include <sstream>
#include <iomanip>

namespace QVecUtils {

    template <typename T>
    std::vector<std::string> vecNumToStr(const std::vector<T>& numbers, int precision = -1) {
        static_assert(std::is_arithmetic<T>::value,
                      "Template type must be a numeric type (int, float, double, etc.)");
    
        std::vector<std::string> result;
        result.reserve(numbers.size());
    
        if constexpr (std::is_floating_point<T>::value) {
            std::ostringstream oss;
    
            if (precision >= 0) {
                oss << std::fixed << std::setprecision(precision);
            } else {
                oss << std::setprecision(std::numeric_limits<T>::max_digits10);
            }
    
            for (const T& num : numbers) {
                oss.str("");
                oss.clear();
                oss << num;
                result.push_back(oss.str());
            }
        } else {
            for (const T& num : numbers) {
                result.push_back(std::to_string(num));
            }
        }
    
        return result;
    }

    template<typename T>
    std::vector<T> ptrToVec(const T* ptr, size_t size) {
        if (ptr == nullptr && size > 0) {
            throw std::invalid_argument("input pointer cannot be null");
        }
        if (size == 0) {
            return {};
        }
    
        return std::vector<T>(ptr, ptr + size);
    }
}

#endif