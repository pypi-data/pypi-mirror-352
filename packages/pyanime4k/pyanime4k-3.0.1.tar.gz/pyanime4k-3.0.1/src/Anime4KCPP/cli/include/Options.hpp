#ifndef AC_CLI_OPTIONS_CPP
#define AC_CLI_OPTIONS_CPP

#include <string>
#include <vector>

#include "AC/Specs.hpp"

struct Options
{
    std::vector<std::string> inputs{};
    std::vector<std::string> outputs{};
    std::string model{ ac::specs::ModelNameList[0] };
    std::string processor{ ac::specs::ProcessorNameList[0] };
    double factor = 2.0;
    int device = 0;

    struct {
        // decoder hints
        std::string decoder{};
        std::string format{};
        // encoder hints
        std::string encoder{};
        int bitrate = 0;

        bool enable = false;
        operator bool() const noexcept { return enable; }
    } video;

    struct
    {
        bool devices = false;
        bool models = false;
        bool processors = false;
        bool version = false;
    } list;
};

Options parse(int argc, const char* const* argv) noexcept;

#endif
