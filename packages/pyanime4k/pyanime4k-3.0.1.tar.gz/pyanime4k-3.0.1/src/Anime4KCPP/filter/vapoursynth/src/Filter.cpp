#include <cstdint>
#include <cstring>
#include <memory>

#include <VapourSynth4.h>
#include <VSHelper4.h>

#include "AC/Core.hpp"

#define SET_ERROR(msg) { vsapi->mapSetError(out, (msg)); if (node) vsapi->freeNode(node); return; }

struct Data
{
    int type;
    double factor;
    std::shared_ptr<ac::core::Processor> processor;
    VSNode* node;
    VSVideoInfo vi;
};

static const VSFrame* VS_CC filter(int n, int activationReason, void* instanceData, void** /*frameData*/, VSFrameContext* frameCtx, VSCore* core, const VSAPI* vsapi)
{
    auto data = static_cast<Data*>(instanceData);

    if (activationReason == arInitial) vsapi->requestFrameFilter(n, data->node, frameCtx);
    else if (activationReason == arAllFramesReady)
    {
        auto src = vsapi->getFrameFilter(n, data->node, frameCtx);
        auto fi = vsapi->getVideoFrameFormat(src);
        auto dst = vsapi->newVideoFrame(fi, data->vi.width, data->vi.height, src, core);
        //y
        ac::core::Image srcy{ vsapi->getFrameWidth(src, 0), vsapi->getFrameHeight(src, 0), 1, data->type, const_cast<std::uint8_t*>(vsapi->getReadPtr(src, 0)), static_cast<int>(vsapi->getStride(src, 0)) };
        ac::core::Image dsty{ vsapi->getFrameWidth(dst, 0), vsapi->getFrameHeight(dst, 0), 1, data->type, vsapi->getWritePtr(dst, 0), static_cast<int>(vsapi->getStride(dst, 0)) };
        data->processor->process(srcy, dsty, data->factor);
        if (!data->processor->ok()) vsapi->setFilterError(data->processor->error(), frameCtx);
        //uv
        for (int p = 1; p < fi->numPlanes; p++)
        {
            ac::core::Image srcp{ vsapi->getFrameWidth(src, p), vsapi->getFrameHeight(src, p), 1, data->type, const_cast<std::uint8_t*>(vsapi->getReadPtr(src, p)), static_cast<int>(vsapi->getStride(src, p)) };
            ac::core::Image dstp{ vsapi->getFrameWidth(dst, p), vsapi->getFrameHeight(dst, p), 1, data->type, vsapi->getWritePtr(dst, p), static_cast<int>(vsapi->getStride(dst, p)) };
            ac::core::resize(srcp, dstp, 0.0, 0.0);
        }

        vsapi->freeFrame(src);
        return dst;
    }
    return nullptr;
}

static void VS_CC destory(void* instanceData, VSCore* /*core*/, const VSAPI* vsapi)
{
    auto data = static_cast<Data*>(instanceData);
    vsapi->freeNode(data->node);
    delete data;
}

static void VS_CC create(const VSMap* in, VSMap* out, void* /*userData*/, VSCore* core, const VSAPI* vsapi)
{
    int err = peSuccess;

    auto node = vsapi->mapGetNode(in, "clip", 0, &err);
    if (err != peSuccess) SET_ERROR("Anime4KCPP: no clip");
    auto vi = vsapi->getVideoInfo(node);

    auto type = [&]() ->int {
        if (vsh::isConstantVideoFormat(vi) && (vi->format.colorFamily == cfYUV || vi->format.colorFamily == cfGray))
        {
            if (vi->format.sampleType == stInteger && vi->format.bitsPerSample == 8) return ac::core::Image::UInt8;
            if (vi->format.sampleType == stInteger && vi->format.bitsPerSample == 16) return ac::core::Image::UInt16;
            if (vi->format.sampleType == stFloat && vi->format.bitsPerSample == 32) return ac::core::Image::Float32;
        }
        return 0;
    }();
    if (!type) SET_ERROR("Anime4KCPP: only planar YUV uint8, uint16 and float32 input supported");

    auto factor = static_cast<double>(vsapi->mapGetFloat(in, "factor", 0, &err));
    if (err != peSuccess) factor = 2.0;
    if (factor <= 1.0) SET_ERROR("Anime4KCPP: this is a upscaler, so make sure factor > 1.0");

    auto processorType = vsapi->mapGetData(in, "processor", 0, &err);
    if (err != peSuccess) processorType = "cpu";

    auto device = static_cast<int>(vsapi->mapGetInt(in, "device", 0, &err));
    if (err != peSuccess) device = 0;
    if (device < 0) SET_ERROR("Anime4KCPP: the device index cannot be negative");

    auto model = vsapi->mapGetData(in, "model", 0, &err);
    if (err != peSuccess) model = "acnet-hdn0";

    auto data = new Data{};
    data->node = node;
    data->vi = *vi;
    data->vi.width = static_cast<decltype(data->vi.width)>(vi->width * factor);
    data->vi.height = static_cast<decltype(data->vi.height)>(vi->height * factor);
    data->type = type;
    data->factor = factor;
    data->processor = ac::core::Processor::create(ac::core::Processor::type(processorType), device, model);
    if (!data->processor->ok()) SET_ERROR(data->processor->error());

    VSFilterDependency deps[] = { {node, rpGeneral} };
    vsapi->createVideoFilter(out, "Upscale", &data->vi, filter, destory, fmParallel, deps, 1, data, core);
}

VS_EXTERNAL_API(void) VapourSynthPluginInit2(VSPlugin* plugin, const VSPLUGINAPI* vspapi)
{
    vspapi->configPlugin("github.tianzerl.anime4kcpp", "anime4kcpp", "Anime4KCPP for VapourSynth", VS_MAKE_VERSION(3, 0), VAPOURSYNTH_API_VERSION, 0, plugin);
    vspapi->registerFunction("ACUpscale",
        "clip:vnode;"
        "factor:float:opt;"
        "processor:data:opt;"
        "device:int:opt;"
        "model:data:opt;",
        "clip:vnode;", create, nullptr, plugin);

    vspapi->registerFunction("ACInfoList",
        "",
        "info:data[];",
        [](const VSMap* /*in*/, VSMap* out, void* /*userData*/, VSCore* /*core*/, const VSAPI* vsapi) -> void {
            vsapi->mapSetData(out, "info", ac::core::Processor::info<ac::core::Processor::CPU>(), -1, dtUtf8, maAppend);
#       ifdef AC_CORE_WITH_OPENCL
            vsapi->mapSetData(out, "info", ac::core::Processor::info<ac::core::Processor::OpenCL>(), -1, dtUtf8, maAppend);
#       endif
#       ifdef AC_CORE_WITH_CUDA
            vsapi->mapSetData(out, "info", ac::core::Processor::info<ac::core::Processor::CUDA>(), -1, dtUtf8, maAppend);
#       endif
        }, nullptr, plugin);
}
