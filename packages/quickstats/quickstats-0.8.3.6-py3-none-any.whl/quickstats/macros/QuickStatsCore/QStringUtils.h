#ifndef __QStringUtils_H__
#define __QStringUtils_H__

#include <string>
#include <string_view>
#include <vector>
#include <initializer_list>
#include <iterator>
#include <cctype>
#include <algorithm>

namespace QStringUtils {

    /**
     * @brief Removes leading and trailing characters from a string.
     * 
     * @param s String to strip
     * @param characters Set of characters to remove (defaults to whitespace and tabs)
     * @return std::string New string with specified characters removed from both ends
     * 
     * @example
     *   strip("  hello  ")          -> "hello"
     *   strip("###test###", "#")    -> "test"
     *   strip("  \t  ")             -> ""
     *   strip("hello")              -> "hello"
     *   strip("xx*test**x", "*x")   -> "test"
     */
    std::string strip(std::string_view s, std::string_view characters = " \t");

    /**
     * @brief Splits a string into tokens using a single character delimiter.
     * 
     * @param str String to split
     * @param delimiter Single character to use as delimiter (defaults to space)
     * @param removeEmptyTokens If true, empty tokens are removed from result (defaults to true)
     * @param stripWhitespace If true, whitespace is stripped from each token (defaults to false)
     * @return std::vector<std::string> Vector of tokens
     * 
     * @example
     *   split("a,b,c", ',')                    -> ["a", "b", "c"]
     *   split("a,,b,c", ',')                   -> ["a", "b", "c"]
     *   split("a,,b,c", ',', false)            -> ["a", "", "b", "c"]
     *   split(" a , b , c ", ',', true, true)  -> ["a", "b", "c"]
     *   split("", ',')                         -> []
     *   split("abc")                           -> ["abc"]
     */
    std::vector<std::string> split(std::string_view str, char delimiter = ' ',
                                   bool removeEmptyTokens = true, bool stripWhitespace = false);

    /**
     * @brief Splits a string into tokens using a string delimiter.
     * 
     * @param str String to split
     * @param delimiter String to use as delimiter
     * @param removeEmptyTokens If true, empty tokens are removed from result (defaults to true)
     * @param stripWhitespace If true, whitespace is stripped from each token (defaults to false)
     * @return std::vector<std::string> Vector of tokens
     * 
     * @example
     *   split("a::b::c", "::")                    -> ["a", "b", "c"]
     *   split("a||||b||c", "||")                  -> ["a", "", "b", "c"]
     *   split("a-->b-->c", "-->")                 -> ["a", "b", "c"]
     *   split(" a <> b <> c ", "<>", true, true)  -> ["a", "b", "c"]
     *   split("", "||")                           -> []
     *   split("abc", "")                          -> []
     */
    std::vector<std::string> split(std::string_view str, std::string_view delimiter,
                                   bool removeEmptyTokens = true, bool stripWhitespace = false);

    /**
     * @brief Joins an iterable collection of strings with a delimiter.
     * Works with any container that provides begin/end iterators and contains
     * string-like elements (std::string, const char*, std::string_view).
     * 
     * @param elements Container of strings to join
     * @param delimiter String to insert between elements
     * @return std::string Joined string
     * 
     * @example
     *   std::vector<std::string> vec = {"a", "b", "c"};
     *   join(vec, ", ")                           -> "a, b, c"
     *   join(vec, "")                             -> "abc"
     *   
     *   std::list<const char*> list = {"x", "y"};
     *   join(list, " -> ")                        -> "x -> y"
     *   
     *   join({"1", "2", "3"}, "|")                -> "1|2|3"
     *   join(std::vector<std::string>{}, ",")     -> ""
     */
    template<typename Iterable>
    std::string join(const Iterable& elements, std::string_view delimiter);

    /**
     * @brief Specialization of join for std::initializer_list.
     * Allows for convenient inline usage with brace-enclosed lists.
     * 
     * @param elements Initializer list of strings
     * @param delimiter String to insert between elements
     * @return std::string Joined string
     * 
     * @example
     *   join({"x", "y", "z"}, ", ")              -> "x, y, z"
     *   join({"single"}, "-")                    -> "single"
     *   join({}, "any")                          -> ""
     */
    template<typename T>
    std::string join(const std::initializer_list<T>& elements, std::string_view delimiter);

    // Include definitions for template functions (must be in header)
    template<typename Iterable>
    std::string join(const Iterable& elements, std::string_view delimiter) {
        using std::begin;
        using std::end;
    
        auto it = begin(elements);
        auto it_end = end(elements);
    
        if (it == it_end) return "";
    
        size_t total_length = 0;
        size_t delimiter_length = delimiter.length();
        size_t element_count = 0;
    
        // First pass: calculate total length
        for (auto elem_it = it; elem_it != it_end; ++elem_it) {
            std::string_view elem = *elem_it;
            total_length += elem.length();
            ++element_count;
        }
        total_length += delimiter_length * (element_count - 1);
    
        std::string result;
        result.reserve(total_length);
    
        // Second pass: concatenate elements
        it = begin(elements);
        result.append(*it);
        ++it;
        for (; it != it_end; ++it) {
            result.append(delimiter);
            result.append(*it);
        }
    
        return result;
    }

    template<typename T>
    std::string join(const std::initializer_list<T>& elements, std::string_view delimiter) {
        return join<std::initializer_list<T>>(elements, delimiter);
    }

}

#endif