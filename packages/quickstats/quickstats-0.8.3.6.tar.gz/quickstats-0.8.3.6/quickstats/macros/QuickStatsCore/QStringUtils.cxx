#include "QStringUtils.h"

#include <string>
#include <string_view>
#include <vector>
#include <cctype>
#include <algorithm>

namespace QStringUtils {

    std::string strip(std::string_view s, std::string_view characters) {
        const auto strBegin = s.find_first_not_of(characters);
        if (strBegin == std::string_view::npos)
            return std::string();  // All characters are to be stripped

        const auto strEnd = s.find_last_not_of(characters);
        const auto length = strEnd - strBegin + 1;

        if (strBegin == 0 && length == s.size()) {
            // Return a copy of the original string
            return std::string(s);  // Note: std::string_view doesn't own data
        } else {
            // Return the substring without leading or trailing characters
            return std::string(s.substr(strBegin, length));
        }
    }

    std::vector<std::string> split(std::string_view str, char delimiter, 
                               bool removeEmptyTokens, bool stripWhitespace) {
        std::vector<std::string> tokens;
        const size_t length = str.length();
        
        if (length == 0) {
            return tokens;
        }
    
        // Pre-reserve vector capacity
        size_t count = 1;
        const char* ptr = str.data();
        const char* const end = ptr + length;
        while (ptr < end) {
            if (*ptr++ == delimiter) ++count;
        }
        tokens.reserve(count);
    
        // Fast path for simple case
        if (!stripWhitespace && !removeEmptyTokens) {
            const char* start = str.data();
            const char* curr = start;
            while (curr < end) {
                if (*curr == delimiter) {
                    tokens.emplace_back(start, curr - start);
                    start = curr + 1;
                }
                ++curr;
            }
            tokens.emplace_back(start, end - start);
            return tokens;
        }
    
        // Regular path
        const char* start = str.data();
        const char* curr = start;
        
        while (curr < end) {
            if (*curr == delimiter) {
                size_t len = curr - start;
                if (!removeEmptyTokens || len > 0) {
                    if (stripWhitespace && len > 0) {
                        const char* token_start = start;
                        const char* token_end = curr;
                        
                        // Skip leading whitespace
                        while (token_start < token_end && (*token_start == ' ' || *token_start == '\t')) {
                            ++token_start;
                        }
                        
                        // Skip trailing whitespace
                        while (token_end > token_start && (*(token_end - 1) == ' ' || *(token_end - 1) == '\t')) {
                            --token_end;
                        }
                        
                        if (token_start < token_end || !removeEmptyTokens) {
                            tokens.emplace_back(token_start, token_end - token_start);
                        }
                    } else {
                        tokens.emplace_back(start, len);
                    }
                }
                start = curr + 1;
            }
            ++curr;
        }
    
        // Handle last token
        size_t len = end - start;
        if (!removeEmptyTokens || len > 0) {
            if (stripWhitespace && len > 0) {
                const char* token_start = start;
                const char* token_end = end;
                
                while (token_start < token_end && (*token_start == ' ' || *token_start == '\t')) {
                    ++token_start;
                }
                while (token_end > token_start && (*(token_end - 1) == ' ' || *(token_end - 1) == '\t')) {
                    --token_end;
                }
                
                if (token_start < token_end || !removeEmptyTokens) {
                    tokens.emplace_back(token_start, token_end - token_start);
                }
            } else {
                tokens.emplace_back(start, len);
            }
        }
    
        return tokens;
    }

    std::vector<std::string> split(std::string_view str, std::string_view delimiter,
                               bool removeEmptyTokens, bool stripWhitespace) {
        std::vector<std::string> tokens;
        const size_t length = str.length();
        const size_t delimiter_length = delimiter.length();
        
        if (length == 0 || delimiter_length == 0) {
            return tokens;
        }
    
        // Pre-reserve vector capacity
        size_t count = 1;
        size_t pos = 0;
        while ((pos = str.find(delimiter, pos)) != std::string_view::npos) {
            ++count;
            pos += delimiter_length;
        }
        tokens.reserve(count);
    
        // Fast path for simple case
        if (!stripWhitespace && !removeEmptyTokens) {
            size_t start = 0;
            size_t end;
            while ((end = str.find(delimiter, start)) != std::string_view::npos) {
                tokens.emplace_back(str.substr(start, end - start));
                start = end + delimiter_length;
            }
            tokens.emplace_back(str.substr(start));
            return tokens;
        }
    
        // Regular path
        size_t start = 0;
        size_t end;
        while ((end = str.find(delimiter, start)) != std::string_view::npos) {
            std::string_view token = str.substr(start, end - start);
            
            if (stripWhitespace && !token.empty()) {
                size_t token_start = token.find_first_not_of(" \t");
                if (token_start != std::string_view::npos) {
                    size_t token_end = token.find_last_not_of(" \t");
                    token = token.substr(token_start, token_end - token_start + 1);
                } else {
                    token = std::string_view();
                }
            }
            
            if (!removeEmptyTokens || !token.empty()) {
                tokens.emplace_back(token);
            }
            
            start = end + delimiter_length;
        }
    
        // Handle last token
        std::string_view token = str.substr(start);
        if (stripWhitespace && !token.empty()) {
            size_t token_start = token.find_first_not_of(" \t");
            if (token_start != std::string_view::npos) {
                size_t token_end = token.find_last_not_of(" \t");
                token = token.substr(token_start, token_end - token_start + 1);
            } else {
                token = std::string_view();
            }
        }
        
        if (!removeEmptyTokens || !token.empty()) {
            tokens.emplace_back(token);
        }
    
        return tokens;
    }

}
