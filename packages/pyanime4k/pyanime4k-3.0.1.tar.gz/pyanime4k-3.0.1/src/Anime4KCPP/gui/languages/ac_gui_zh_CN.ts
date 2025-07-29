<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="zh_CN">
<context>
    <name>ExternI18N</name>
    <message>
        <location filename="../../build/gui/i18n/i18n_marker_ac_specs_hpp.cpp" line="7"/>
        <source>Lightweight CNN, detail enhancement.</source>
        <translation>轻量CNN，细节增强。</translation>
    </message>
    <message>
        <location filename="../../build/gui/i18n/i18n_marker_ac_specs_hpp.cpp" line="8"/>
        <source>Lightweight CNN, mild denoising.</source>
        <translation>轻量CNN，轻度降噪。</translation>
    </message>
    <message>
        <location filename="../../build/gui/i18n/i18n_marker_ac_specs_hpp.cpp" line="9"/>
        <source>Lightweight CNN, moderate denoising.</source>
        <translation>轻量CNN，中度降噪。</translation>
    </message>
    <message>
        <location filename="../../build/gui/i18n/i18n_marker_ac_specs_hpp.cpp" line="10"/>
        <source>Lightweight CNN, heavy denoising.</source>
        <translation>轻量CNN，强力降噪。</translation>
    </message>
    <message>
        <location filename="../../build/gui/i18n/i18n_marker_ac_specs_hpp.cpp" line="11"/>
        <source>Lightweight CNN, extreme denoising.</source>
        <translation>轻量CNN，极致降噪。</translation>
    </message>
    <message>
        <location filename="../../build/gui/i18n/i18n_marker_ac_specs_hpp.cpp" line="12"/>
        <source>Lightweight ResNet, mild denoising.</source>
        <translation>轻量ResNet，轻度降噪。</translation>
    </message>
    <message>
        <location filename="../../build/gui/i18n/i18n_marker_ac_specs_hpp.cpp" line="15"/>
        <source>General-purpose CPU processing with optional SIMD acceleration.</source>
        <translation>通用CPU计算，支持SIMD加速。</translation>
    </message>
    <message>
        <location filename="../../build/gui/i18n/i18n_marker_ac_specs_hpp.cpp" line="16"/>
        <source>Cross-platform acceleration requiring OpenCL 1.2+ compliant devices.</source>
        <translation>跨平台异构计算加速，需要支持OpenCL1.2+标准的设备。</translation>
    </message>
    <message>
        <location filename="../../build/gui/i18n/i18n_marker_ac_specs_hpp.cpp" line="17"/>
        <source>NVIDIA GPU acceleration requiring Compute Capability 5.0+.</source>
        <translation>NVIDIA GPU加速，需CUDA计算能力5.0+的设备。</translation>
    </message>
</context>
<context>
    <name>MainWindow</name>
    <message>
        <location filename="../ui/MainWindow.ui" line="14"/>
        <source>Anime4KCPP</source>
        <translation>Anime4KCPP</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="21"/>
        <location filename="../ui/MainWindow.ui" line="350"/>
        <source>Settings</source>
        <translation>设置</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="62"/>
        <location filename="../ui/MainWindow.ui" line="144"/>
        <location filename="../ui/MainWindow.ui" line="168"/>
        <location filename="../src/MainWindow.cpp" line="197"/>
        <source>image</source>
        <translation>图像</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="199"/>
        <source>decoder</source>
        <translation>解码器</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="158"/>
        <source>encoder</source>
        <translation>编码器</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="27"/>
        <location filename="../ui/MainWindow.ui" line="93"/>
        <location filename="../ui/MainWindow.ui" line="185"/>
        <location filename="../src/MainWindow.cpp" line="197"/>
        <source>video</source>
        <translation>视频</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="117"/>
        <source>format</source>
        <translation>格式</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="34"/>
        <source>bitrate</source>
        <translation>比特率</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="48"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;The decoder name passed to FFmpeg&apos;s library.&lt;/span&gt;&lt;/p&gt;&lt;p&gt;This setting specifies the decoder (typically no manual configuration required). Available values depend on the library version. Refer to FFmpeg documentation for details.&lt;/p&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;Leave blank&lt;/span&gt;: Auto-select the decoder based on the input file.&lt;/p&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;Typical options&lt;/span&gt;: h264, hevc, h264_qsv, h264_amf, h264_cuvid, etc.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;解码器名称，传递给FFmpeg库。&lt;/span&gt;&lt;/p&gt;&lt;p&gt;此设置用于指定解码器（通常无需手动配置）。可用选项取决于FFmpeg库的版本，详情请参考FFmpeg文档。&lt;/p&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;留空&lt;/span&gt;: 根据输入文件自动选择解码器。&lt;/p&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;示例&lt;/span&gt;: h264, hevc, h264_qsv, h264_amf, h264_cuvid 等。&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="55"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;The encoder name passed to FFmpeg&apos;s library.&lt;/span&gt;&lt;/p&gt;&lt;p&gt;This setting determines the output codec, and controls hardware acceleration support. Available values depend on the version of the library. Refer to FFmpeg documentation for details.&lt;/p&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;Leave blank&lt;/span&gt;: Auto-select the encoder based on the file extension.&lt;/p&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;Typical options&lt;/span&gt;: libopenh264, libx264, libx265, h264_qsv, hevc_qsv, h264_nvenc, hevc_nvenc, h264_amf, hevc_amf, etc.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;编码器名称，传递给FFmpeg库。&lt;/span&gt;&lt;/p&gt;&lt;p&gt;此设置用于指定输出编码，并控制硬件加速功能。可用选项取决于FFmpeg库的版本，详情请参考FFmpeg文档。&lt;/p&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;留空&lt;/span&gt;: 根据输出文件扩展名自动选择编码器。&lt;/p&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;示例&lt;/span&gt;: libopenh264, libx264, libx265, h264_qsv, hevc_qsv, h264_nvenc, hevc_nvenc, h264_amf, hevc_amf 等。&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="131"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;the pixel format passed to FFmpeg&apos;s library.&lt;/span&gt;&lt;/p&gt;&lt;p&gt;This setting defines the pixel format for the encoder. Note that some encoders require specific formats. Refer to FFmpeg documentation for details.&lt;/p&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;Troubleshooting&lt;/span&gt;: If some hardware acceleration encoders initialization fails, try setting this field to p010 (10bit) or nv12 (8bit).&lt;/p&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;Leave blank&lt;/span&gt;: Auto-select the pixel format based on the decoder.&lt;/p&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;Typical options&lt;/span&gt;: yuv420p, yuv420p10, nv12, p010, etc.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;像素格式，传递给FFmpeg库。&lt;/span&gt;&lt;/p&gt;&lt;p&gt;此设置用于指定编码器的像素格式。请注意部分编码器需特定格式，详情请参考FFmpeg文档。&lt;/p&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;故障排查&lt;/span&gt;: 若硬件编码器初始化失败，可尝试将此字段设为p010 (10bit)或nv12 (8bit)。&lt;/p&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;留空&lt;/span&gt;: 根据解码器自动选择像素格式。&lt;/p&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;示例&lt;/span&gt;: yuv420p, yuv420p10, nv12, p010 等。&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="79"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;The bitrate passed to FFmpeg&apos;s library.&lt;/span&gt;&lt;/p&gt;&lt;p&gt;This affects the output video&apos;s file size and quality. The unit is &lt;span style=&quot; font-weight:700;&quot;&gt;kb/s&lt;/span&gt;.&lt;/p&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;Leave blank&lt;/span&gt;: auto-select the bitrate based on the input file.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;比特率，传递给FFmpeg库。&lt;/span&gt;&lt;/p&gt;&lt;p&gt;设置将影响输出视频的文件大小与画质。单位为&lt;span style=&quot; font-weight:700;&quot;&gt;kb/s&lt;/span&gt;。&lt;/p&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;留空&lt;/span&gt;: 根据输入文件自动选择比特率。&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="72"/>
        <location filename="../ui/MainWindow.ui" line="206"/>
        <source>select</source>
        <translation>选择</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="124"/>
        <location filename="../ui/MainWindow.ui" line="151"/>
        <location filename="../src/MainWindow.cpp" line="130"/>
        <source>open</source>
        <translation>打开</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="213"/>
        <source>prefix</source>
        <translation>前缀</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="192"/>
        <source>suffix</source>
        <translation>后缀</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="41"/>
        <source>codec hints</source>
        <translation>编解码提示参数</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="86"/>
        <source>output path</source>
        <translation>输出路径</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="226"/>
        <source>Parameters</source>
        <translation>参数</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="232"/>
        <source>processor</source>
        <translation>处理器</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="242"/>
        <source>device</source>
        <translation>设备</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="249"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;For CPU, it represents different acceleration methods.&lt;/p&gt;&lt;p&gt;For GPU, it represents the devices to use.&lt;/p&gt;&lt;p&gt;Check available value in menu: &lt;span style=&quot; font-weight:700;&quot;&gt;Help-&amp;gt;List devices&lt;/span&gt;.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;对于CPU该值为加速方式。&lt;/p&gt;&lt;p&gt;对于GPU该值为使用的设备。&lt;/p&gt;&lt;p&gt;可在菜单中检查可用值：&lt;span style=&quot; font-weight:700;&quot;&gt;帮助&amp;gt;列出设备&lt;/span&gt;。&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="256"/>
        <source>factor</source>
        <translation>系数</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="263"/>
        <source>Upscaling factor for each dimension.</source>
        <translation>每个维度的放大系数。</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="270"/>
        <source>model</source>
        <translation>模型</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="283"/>
        <source>add</source>
        <translation>添加</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="290"/>
        <source>clear</source>
        <translation>清除</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="297"/>
        <source>start</source>
        <translation>开始</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="304"/>
        <source>stop</source>
        <translation>停止</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="338"/>
        <source>File</source>
        <translation>文件</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="346"/>
        <source>Help</source>
        <translation>帮助</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="354"/>
        <source>Style</source>
        <translation>风格</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="372"/>
        <location filename="../src/MainWindow.cpp" line="344"/>
        <source>About</source>
        <translation>关于</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="377"/>
        <source>Add</source>
        <translation>添加</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="382"/>
        <location filename="../src/MainWindow.cpp" line="263"/>
        <source>Exit</source>
        <translation>退出</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="387"/>
        <source>List devices</source>
        <translation>列出设备</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="395"/>
        <location filename="../src/MainWindow.cpp" line="263"/>
        <source>Exit confirmation</source>
        <translation>退出确认</translation>
    </message>
    <message>
        <location filename="../ui/MainWindow.ui" line="400"/>
        <location filename="../src/MainWindow.cpp" line="318"/>
        <source>License</source>
        <translation>许可证</translation>
    </message>
    <message>
        <location filename="../src/MainWindow.cpp" line="123"/>
        <source>type</source>
        <translation>类型</translation>
    </message>
    <message>
        <location filename="../src/MainWindow.cpp" line="123"/>
        <source>status</source>
        <translation>状态</translation>
    </message>
    <message>
        <location filename="../src/MainWindow.cpp" line="123"/>
        <source>name</source>
        <translation>名称</translation>
    </message>
    <message>
        <location filename="../src/MainWindow.cpp" line="123"/>
        <source>output name</source>
        <translation>输出名称</translation>
    </message>
    <message>
        <location filename="../src/MainWindow.cpp" line="123"/>
        <source>path</source>
        <translation>路径</translation>
    </message>
    <message>
        <location filename="../src/MainWindow.cpp" line="131"/>
        <source>remove</source>
        <translation>移除</translation>
    </message>
    <message>
        <location filename="../src/MainWindow.cpp" line="198"/>
        <source>ready</source>
        <translation>就绪</translation>
    </message>
    <message>
        <location filename="../src/MainWindow.cpp" line="223"/>
        <source>input</source>
        <translation>输入</translation>
    </message>
    <message>
        <location filename="../src/MainWindow.cpp" line="223"/>
        <source>output</source>
        <translation>输出</translation>
    </message>
    <message>
        <location filename="../src/MainWindow.cpp" line="206"/>
        <source>succeeded</source>
        <translation>成功</translation>
    </message>
    <message>
        <location filename="../src/MainWindow.cpp" line="206"/>
        <source>failed</source>
        <translation>失败</translation>
    </message>
    <message>
        <location filename="../src/MainWindow.cpp" line="306"/>
        <source>Devices</source>
        <translation>设备</translation>
    </message>
    <message>
        <location filename="../src/MainWindow.cpp" line="362"/>
        <source>Anime4KCPP: A high performance anime upscaler</source>
        <translation>Anime4KCPP：高性能动漫超分工具</translation>
    </message>
    <message>
        <location filename="../src/MainWindow.cpp" line="363"/>
        <source>core version</source>
        <translation>核心版本</translation>
    </message>
    <message>
        <location filename="../src/MainWindow.cpp" line="364"/>
        <source>video module</source>
        <translation>视频模块</translation>
    </message>
    <message>
        <location filename="../src/MainWindow.cpp" line="365"/>
        <source>build date</source>
        <translation>构建日期</translation>
    </message>
    <message>
        <location filename="../src/MainWindow.cpp" line="366"/>
        <source>toolchain</source>
        <translation>工具链</translation>
    </message>
    <message>
        <location filename="../src/MainWindow.cpp" line="367"/>
        <source>Copyright</source>
        <translation>版权所有</translation>
    </message>
    <message>
        <location filename="../src/MainWindow.cpp" line="368"/>
        <source>disabled</source>
        <translation>不可用</translation>
    </message>
</context>
</TS>
