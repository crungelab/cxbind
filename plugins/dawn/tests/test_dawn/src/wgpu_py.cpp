#include <typeinfo>
#include <sstream>
#ifdef __GNUG__
  #include <cxxabi.h>
  #include <cstdlib>
#endif

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/operators.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include <crunge/wgpu/pywgpu.h>
#include <crunge/wgpu/crunge-wgpu.h>
#include <crunge/wgpu/conversions.h>

inline std::string demangle_type_name(const char* name) {
#ifdef __GNUG__
    int status = 0;
    char* dem = abi::__cxa_demangle(name, nullptr, nullptr, &status);
    std::string out = (status == 0 && dem) ? dem : name;
    std::free(dem);
    return out;
#else
    return name;
#endif
}

inline std::string py_type_qualname(py::handle h) {
    if (h.is_none()) return "None";
    py::object t = py::type::of(h);
    std::string mod = py::str(t.attr("__module__"));
    std::string name = py::str(t.attr("__qualname__"));
    return mod + "." + name;
}

struct LinearAlloc {
    uint8_t* base = nullptr;
    size_t cap = 0, off = 0;

    explicit LinearAlloc(size_t capacity = 64 * 1024) {
        base = (uint8_t*)std::malloc(capacity);
        if (!base) throw std::bad_alloc();
        cap = capacity;
    }
    ~LinearAlloc() { std::free(base); }

    void* alloc(size_t n, size_t align) {
        size_t p = (off + (align - 1)) & ~(align - 1);
        if (p + n > cap) throw std::runtime_error("LinearAlloc overflow");
        off = p + n;
        return base + p;
    }

    template<class T>
    T* alloc_array(size_t count) {
        return reinterpret_cast<T*>(alloc(sizeof(T) * count, alignof(T)));
    }

    template<class T>
    T* make() {
        void* p = alloc(sizeof(T), alignof(T));
        return new (p) T{}; // value-init
    }

    template<class T>
    T* make_array(size_t count) {
        T* p = alloc_array<T>(count);
        for (size_t i = 0; i < count; ++i) {
            new (&p[i]) T{}; // value-init each element
        }
        return p;
    }

    const char* copy_cstr(const std::string& s) {
        char* p = (char*)alloc(s.size() + 1, alignof(char));
        std::memcpy(p, s.c_str(), s.size() + 1);
        return p;
    }
};

struct BuildCtx {
    LinearAlloc& la;
    //const ChainRegistry* chains = nullptr; // optional; nullptr if you don't support nextInChain yet
};

// Fallback: if no overload exists for T, this will be selected.
template<class T>
inline void fill(T&, py::handle h, BuildCtx) {
    std::ostringstream oss;
    oss << "No generated fill(T&, py::handle, BuildCtx) overload for C++ type '"
        << demangle_type_name(typeid(T).name())
        << "'. Python value type was '" << py_type_qualname(h) << "'.";
    throw std::runtime_error(oss.str());
}

template <class T>
struct Builder {
    BuildCtx ctx;

    explicit Builder(BuildCtx c) : ctx(c) {}

    // Allocate one T and fill it.
    T* build(py::handle dc) {
        if (dc.is_none()) return nullptr;
        auto* p = ctx.la.make<T>();
        fill(*p, dc);
        return p;
    }

    // Allocate N Ts and fill each element.
    T* build_array(py::handle seq_h, uint32_t* outCount) {
        if (seq_h.is_none()) {
            *outCount = 0;
            return nullptr;
        }
        py::sequence seq = seq_h.cast<py::sequence>();
        *outCount = static_cast<uint32_t>(seq.size());
        if (*outCount == 0) return nullptr;

        T* arr = ctx.la.make_array<T>(*outCount);
        for (uint32_t i = 0; i < *outCount; ++i) {
            fill(arr[i], seq[i]);
        }
        return arr;
    }

    void fill(T& out, py::handle h) {
        using ::fill;
        fill(out, h, ctx);
    }

    // Common helpers
    const char* str_or_null(py::handle h) {
        if (h.is_none()) return nullptr;
        return ctx.la.copy_cstr(std::string(py::str(h)));
    }

    template <class H>
    H handle(py::handle h) { return h.cast<H>(); }

    template <class U>
    U* optional_ptr(py::handle h) {
        if (h.is_none()) return nullptr;
        return Builder<U>(ctx).build(h);
    }
};

template <class DstEnum, class SrcEnum>
constexpr DstEnum enum_cast(SrcEnum v) {
    using U = std::underlying_type_t<SrcEnum>;
    return static_cast<DstEnum>(static_cast<U>(v));
}

namespace py = pybind11;

using namespace pywgpu;

inline void fill(pywgpu::RequestAdapterOptions& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_feature_level = handle.attr("feature_level");
    if (!py_feature_level.is_none())
    {
        auto value = handle.attr("feature_level").cast<FeatureLevel>();
        obj.featureLevel = value;
    }
    auto py_power_preference = handle.attr("power_preference");
    if (!py_power_preference.is_none())
    {
        auto value = handle.attr("power_preference").cast<PowerPreference>();
        obj.powerPreference = value;
    }
    auto py_force_fallback_adapter = handle.attr("force_fallback_adapter");
    if (!py_force_fallback_adapter.is_none())
    {
        auto value = handle.attr("force_fallback_adapter").cast<Bool>();
        obj.forceFallbackAdapter = value;
    }
    auto py_backend_type = handle.attr("backend_type");
    if (!py_backend_type.is_none())
    {
        auto value = handle.attr("backend_type").cast<BackendType>();
        obj.backendType = value;
    }
    auto py_compatible_surface = handle.attr("compatible_surface");
    if (!py_compatible_surface.is_none())
    {
        auto value = handle.attr("compatible_surface").cast<Surface>();
        obj.compatibleSurface = value;
    }
}

inline void fill(pywgpu::DeviceDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_label = handle.attr("label");
    if (!py_label.is_none())
    {
        auto value = handle.attr("label").cast<StringView>();
        obj.label = value;
    }
    auto py_required_features = handle.attr("required_features");
    if (!py_required_features.is_none())
    {
        auto py_list = handle.attr("required_features").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<FeatureName>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<FeatureName>();
        }

        obj.requiredFeatures = value;
        obj.requiredFeatureCount = count;
    }
    auto py_required_limits = handle.attr("required_limits");
    if (!py_required_limits.is_none())
    {
        auto value = Builder<Limits>(ctx).build(handle.attr("required_limits"));
        obj.requiredLimits = value;
    }
    auto py_default_queue = handle.attr("default_queue");
    if (!py_default_queue.is_none())
    {
        Builder<QueueDescriptor>(ctx).fill(obj.defaultQueue, handle.attr("default_queue"));
    }
    auto py_device_lost_callback_info = handle.attr("device_lost_callback_info");
    if (!py_device_lost_callback_info.is_none())
    {
        auto value = handle.attr("device_lost_callback_info").cast<DeviceLostCallbackInfo>();
        obj.deviceLostCallbackInfo = value;
    }
    auto py_uncaptured_error_callback_info = handle.attr("uncaptured_error_callback_info");
    if (!py_uncaptured_error_callback_info.is_none())
    {
        auto value = handle.attr("uncaptured_error_callback_info").cast<UncapturedErrorCallbackInfo>();
        obj.uncapturedErrorCallbackInfo = value;
    }
}

inline void fill(pywgpu::DawnTogglesDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
}

inline void fill(pywgpu::DawnCacheDeviceDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_isolation_key = handle.attr("isolation_key");
    if (!py_isolation_key.is_none())
    {
        auto value = handle.attr("isolation_key").cast<StringView>();
        obj.isolationKey = value;
    }
    auto py_function_userdata = handle.attr("function_userdata");
    if (!py_function_userdata.is_none())
    {
        auto value = handle.attr("function_userdata").cast<void *>();
        obj.functionUserdata = value;
    }
}

inline void fill(pywgpu::DawnWGSLBlocklist& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
}

inline void fill(pywgpu::BindGroupEntry& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_binding = handle.attr("binding");
    if (!py_binding.is_none())
    {
        auto value = handle.attr("binding").cast<uint32_t>();
        obj.binding = value;
    }
    auto py_buffer = handle.attr("buffer");
    if (!py_buffer.is_none())
    {
        auto value = handle.attr("buffer").cast<Buffer>();
        obj.buffer = value;
    }
    auto py_offset = handle.attr("offset");
    if (!py_offset.is_none())
    {
        auto value = handle.attr("offset").cast<uint64_t>();
        obj.offset = value;
    }
    auto py_size = handle.attr("size");
    if (!py_size.is_none())
    {
        auto value = handle.attr("size").cast<uint64_t>();
        obj.size = value;
    }
    auto py_sampler = handle.attr("sampler");
    if (!py_sampler.is_none())
    {
        auto value = handle.attr("sampler").cast<Sampler>();
        obj.sampler = value;
    }
    auto py_texture_view = handle.attr("texture_view");
    if (!py_texture_view.is_none())
    {
        auto value = handle.attr("texture_view").cast<TextureView>();
        obj.textureView = value;
    }
}

inline void fill(pywgpu::BindGroupDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_label = handle.attr("label");
    if (!py_label.is_none())
    {
        auto value = handle.attr("label").cast<StringView>();
        obj.label = value;
    }
    auto py_layout = handle.attr("layout");
    if (!py_layout.is_none())
    {
        auto value = handle.attr("layout").cast<BindGroupLayout>();
        obj.layout = value;
    }
    auto py_entries = handle.attr("entries");
    if (!py_entries.is_none())
    {
        auto py_list = handle.attr("entries").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<BindGroupEntry>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<BindGroupEntry>();
        }

        obj.entries = value;
        obj.entryCount = count;
    }
}

inline void fill(pywgpu::BufferBindingLayout& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_type = handle.attr("type");
    if (!py_type.is_none())
    {
        auto value = handle.attr("type").cast<BufferBindingType>();
        obj.type = value;
    }
    auto py_has_dynamic_offset = handle.attr("has_dynamic_offset");
    if (!py_has_dynamic_offset.is_none())
    {
        auto value = handle.attr("has_dynamic_offset").cast<Bool>();
        obj.hasDynamicOffset = value;
    }
    auto py_min_binding_size = handle.attr("min_binding_size");
    if (!py_min_binding_size.is_none())
    {
        auto value = handle.attr("min_binding_size").cast<uint64_t>();
        obj.minBindingSize = value;
    }
}

inline void fill(pywgpu::SamplerBindingLayout& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_type = handle.attr("type");
    if (!py_type.is_none())
    {
        auto value = handle.attr("type").cast<SamplerBindingType>();
        obj.type = value;
    }
}

inline void fill(pywgpu::StaticSamplerBindingLayout& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_sampler = handle.attr("sampler");
    if (!py_sampler.is_none())
    {
        auto value = handle.attr("sampler").cast<Sampler>();
        obj.sampler = value;
    }
    auto py_sampled_texture_binding = handle.attr("sampled_texture_binding");
    if (!py_sampled_texture_binding.is_none())
    {
        auto value = handle.attr("sampled_texture_binding").cast<uint32_t>();
        obj.sampledTextureBinding = value;
    }
}

inline void fill(pywgpu::TextureBindingLayout& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_sample_type = handle.attr("sample_type");
    if (!py_sample_type.is_none())
    {
        auto value = handle.attr("sample_type").cast<TextureSampleType>();
        obj.sampleType = value;
    }
    auto py_view_dimension = handle.attr("view_dimension");
    if (!py_view_dimension.is_none())
    {
        auto value = handle.attr("view_dimension").cast<TextureViewDimension>();
        obj.viewDimension = value;
    }
    auto py_multisampled = handle.attr("multisampled");
    if (!py_multisampled.is_none())
    {
        auto value = handle.attr("multisampled").cast<Bool>();
        obj.multisampled = value;
    }
}

inline void fill(pywgpu::SurfaceConfiguration& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_device = handle.attr("device");
    if (!py_device.is_none())
    {
        auto value = handle.attr("device").cast<Device>();
        obj.device = value;
    }
    auto py_format = handle.attr("format");
    if (!py_format.is_none())
    {
        auto value = handle.attr("format").cast<TextureFormat>();
        obj.format = value;
    }
    auto py_usage = handle.attr("usage");
    if (!py_usage.is_none())
    {
        auto value = handle.attr("usage").cast<TextureUsage>();
        obj.usage = value;
    }
    auto py_width = handle.attr("width");
    if (!py_width.is_none())
    {
        auto value = handle.attr("width").cast<uint32_t>();
        obj.width = value;
    }
    auto py_height = handle.attr("height");
    if (!py_height.is_none())
    {
        auto value = handle.attr("height").cast<uint32_t>();
        obj.height = value;
    }
    auto py_view_formats = handle.attr("view_formats");
    if (!py_view_formats.is_none())
    {
        auto py_list = handle.attr("view_formats").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<TextureFormat>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<TextureFormat>();
        }

        obj.viewFormats = value;
        obj.viewFormatCount = count;
    }
    auto py_alpha_mode = handle.attr("alpha_mode");
    if (!py_alpha_mode.is_none())
    {
        auto value = handle.attr("alpha_mode").cast<CompositeAlphaMode>();
        obj.alphaMode = value;
    }
    auto py_present_mode = handle.attr("present_mode");
    if (!py_present_mode.is_none())
    {
        auto value = handle.attr("present_mode").cast<PresentMode>();
        obj.presentMode = value;
    }
}

inline void fill(pywgpu::ExternalTextureBindingEntry& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_external_texture = handle.attr("external_texture");
    if (!py_external_texture.is_none())
    {
        auto value = handle.attr("external_texture").cast<ExternalTexture>();
        obj.externalTexture = value;
    }
}

inline void fill(pywgpu::ExternalTextureBindingLayout& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
}

inline void fill(pywgpu::StorageTextureBindingLayout& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_access = handle.attr("access");
    if (!py_access.is_none())
    {
        auto value = handle.attr("access").cast<StorageTextureAccess>();
        obj.access = value;
    }
    auto py_format = handle.attr("format");
    if (!py_format.is_none())
    {
        auto value = handle.attr("format").cast<TextureFormat>();
        obj.format = value;
    }
    auto py_view_dimension = handle.attr("view_dimension");
    if (!py_view_dimension.is_none())
    {
        auto value = handle.attr("view_dimension").cast<TextureViewDimension>();
        obj.viewDimension = value;
    }
}

inline void fill(pywgpu::BindGroupLayoutEntry& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_binding = handle.attr("binding");
    if (!py_binding.is_none())
    {
        auto value = handle.attr("binding").cast<uint32_t>();
        obj.binding = value;
    }
    auto py_visibility = handle.attr("visibility");
    if (!py_visibility.is_none())
    {
        auto value = handle.attr("visibility").cast<ShaderStage>();
        obj.visibility = value;
    }
    auto py_buffer = handle.attr("buffer");
    if (!py_buffer.is_none())
    {
        Builder<BufferBindingLayout>(ctx).fill(obj.buffer, handle.attr("buffer"));
    }
    auto py_sampler = handle.attr("sampler");
    if (!py_sampler.is_none())
    {
        Builder<SamplerBindingLayout>(ctx).fill(obj.sampler, handle.attr("sampler"));
    }
    auto py_texture = handle.attr("texture");
    if (!py_texture.is_none())
    {
        Builder<TextureBindingLayout>(ctx).fill(obj.texture, handle.attr("texture"));
    }
    auto py_storage_texture = handle.attr("storage_texture");
    if (!py_storage_texture.is_none())
    {
        Builder<StorageTextureBindingLayout>(ctx).fill(obj.storageTexture, handle.attr("storage_texture"));
    }
}

inline void fill(pywgpu::BindGroupLayoutDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_label = handle.attr("label");
    if (!py_label.is_none())
    {
        auto value = handle.attr("label").cast<StringView>();
        obj.label = value;
    }
    auto py_entries = handle.attr("entries");
    if (!py_entries.is_none())
    {
        auto py_list = handle.attr("entries").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<BindGroupLayoutEntry>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<BindGroupLayoutEntry>();
        }

        obj.entries = value;
        obj.entryCount = count;
    }
}

inline void fill(pywgpu::BlendComponent& obj, py::handle handle, BuildCtx ctx) {
    auto py_operation = handle.attr("operation");
    if (!py_operation.is_none())
    {
        auto value = handle.attr("operation").cast<BlendOperation>();
        obj.operation = value;
    }
    auto py_src_factor = handle.attr("src_factor");
    if (!py_src_factor.is_none())
    {
        auto value = handle.attr("src_factor").cast<BlendFactor>();
        obj.srcFactor = value;
    }
    auto py_dst_factor = handle.attr("dst_factor");
    if (!py_dst_factor.is_none())
    {
        auto value = handle.attr("dst_factor").cast<BlendFactor>();
        obj.dstFactor = value;
    }
}

inline void fill(pywgpu::BufferDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_label = handle.attr("label");
    if (!py_label.is_none())
    {
        auto value = handle.attr("label").cast<StringView>();
        obj.label = value;
    }
    auto py_usage = handle.attr("usage");
    if (!py_usage.is_none())
    {
        auto value = handle.attr("usage").cast<BufferUsage>();
        obj.usage = value;
    }
    auto py_size = handle.attr("size");
    if (!py_size.is_none())
    {
        auto value = handle.attr("size").cast<uint64_t>();
        obj.size = value;
    }
    auto py_mapped_at_creation = handle.attr("mapped_at_creation");
    if (!py_mapped_at_creation.is_none())
    {
        auto value = handle.attr("mapped_at_creation").cast<Bool>();
        obj.mappedAtCreation = value;
    }
}

inline void fill(pywgpu::BufferHostMappedPointer& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_pointer = handle.attr("pointer");
    if (!py_pointer.is_none())
    {
        auto value = handle.attr("pointer").cast<void *>();
        obj.pointer = value;
    }
    auto py_userdata = handle.attr("userdata");
    if (!py_userdata.is_none())
    {
        auto value = handle.attr("userdata").cast<void *>();
        obj.userdata = value;
    }
}

inline void fill(pywgpu::Color& obj, py::handle handle, BuildCtx ctx) {
    auto py_r = handle.attr("r");
    if (!py_r.is_none())
    {
        auto value = handle.attr("r").cast<double>();
        obj.r = value;
    }
    auto py_g = handle.attr("g");
    if (!py_g.is_none())
    {
        auto value = handle.attr("g").cast<double>();
        obj.g = value;
    }
    auto py_b = handle.attr("b");
    if (!py_b.is_none())
    {
        auto value = handle.attr("b").cast<double>();
        obj.b = value;
    }
    auto py_a = handle.attr("a");
    if (!py_a.is_none())
    {
        auto value = handle.attr("a").cast<double>();
        obj.a = value;
    }
}

inline void fill(pywgpu::ConstantEntry& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_key = handle.attr("key");
    if (!py_key.is_none())
    {
        auto value = handle.attr("key").cast<StringView>();
        obj.key = value;
    }
    auto py_value = handle.attr("value");
    if (!py_value.is_none())
    {
        auto value = handle.attr("value").cast<double>();
        obj.value = value;
    }
}

inline void fill(pywgpu::CommandBufferDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_label = handle.attr("label");
    if (!py_label.is_none())
    {
        auto value = handle.attr("label").cast<StringView>();
        obj.label = value;
    }
}

inline void fill(pywgpu::CommandEncoderDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_label = handle.attr("label");
    if (!py_label.is_none())
    {
        auto value = handle.attr("label").cast<StringView>();
        obj.label = value;
    }
}

inline void fill(pywgpu::CompilationInfo& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_messages = handle.attr("messages");
    if (!py_messages.is_none())
    {
        auto py_list = handle.attr("messages").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<CompilationMessage>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<CompilationMessage>();
        }

        obj.messages = value;
        obj.messageCount = count;
    }
}

inline void fill(pywgpu::CompilationMessage& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_message = handle.attr("message");
    if (!py_message.is_none())
    {
        auto value = handle.attr("message").cast<StringView>();
        obj.message = value;
    }
    auto py_type = handle.attr("type");
    if (!py_type.is_none())
    {
        auto value = handle.attr("type").cast<CompilationMessageType>();
        obj.type = value;
    }
    auto py_line_num = handle.attr("line_num");
    if (!py_line_num.is_none())
    {
        auto value = handle.attr("line_num").cast<uint64_t>();
        obj.lineNum = value;
    }
    auto py_line_pos = handle.attr("line_pos");
    if (!py_line_pos.is_none())
    {
        auto value = handle.attr("line_pos").cast<uint64_t>();
        obj.linePos = value;
    }
    auto py_offset = handle.attr("offset");
    if (!py_offset.is_none())
    {
        auto value = handle.attr("offset").cast<uint64_t>();
        obj.offset = value;
    }
    auto py_length = handle.attr("length");
    if (!py_length.is_none())
    {
        auto value = handle.attr("length").cast<uint64_t>();
        obj.length = value;
    }
}

inline void fill(pywgpu::DawnCompilationMessageUtf16& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_line_pos = handle.attr("line_pos");
    if (!py_line_pos.is_none())
    {
        auto value = handle.attr("line_pos").cast<uint64_t>();
        obj.linePos = value;
    }
    auto py_offset = handle.attr("offset");
    if (!py_offset.is_none())
    {
        auto value = handle.attr("offset").cast<uint64_t>();
        obj.offset = value;
    }
    auto py_length = handle.attr("length");
    if (!py_length.is_none())
    {
        auto value = handle.attr("length").cast<uint64_t>();
        obj.length = value;
    }
}

inline void fill(pywgpu::ComputePassDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_label = handle.attr("label");
    if (!py_label.is_none())
    {
        auto value = handle.attr("label").cast<StringView>();
        obj.label = value;
    }
    auto py_timestamp_writes = handle.attr("timestamp_writes");
    if (!py_timestamp_writes.is_none())
    {
        auto value = Builder<PassTimestampWrites>(ctx).build(handle.attr("timestamp_writes"));
        obj.timestampWrites = value;
    }
}

inline void fill(pywgpu::ComputePipelineDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_label = handle.attr("label");
    if (!py_label.is_none())
    {
        auto value = handle.attr("label").cast<StringView>();
        obj.label = value;
    }
    auto py_layout = handle.attr("layout");
    if (!py_layout.is_none())
    {
        auto value = handle.attr("layout").cast<PipelineLayout>();
        obj.layout = value;
    }
    auto py_compute = handle.attr("compute");
    if (!py_compute.is_none())
    {
        Builder<ComputeState>(ctx).fill(obj.compute, handle.attr("compute"));
    }
}

inline void fill(pywgpu::CopyTextureForBrowserOptions& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_flip_y = handle.attr("flip_y");
    if (!py_flip_y.is_none())
    {
        auto value = handle.attr("flip_y").cast<Bool>();
        obj.flipY = value;
    }
    auto py_needs_color_space_conversion = handle.attr("needs_color_space_conversion");
    if (!py_needs_color_space_conversion.is_none())
    {
        auto value = handle.attr("needs_color_space_conversion").cast<Bool>();
        obj.needsColorSpaceConversion = value;
    }
    auto py_src_alpha_mode = handle.attr("src_alpha_mode");
    if (!py_src_alpha_mode.is_none())
    {
        auto value = handle.attr("src_alpha_mode").cast<AlphaMode>();
        obj.srcAlphaMode = value;
    }
    auto py_src_transfer_function_parameters = handle.attr("src_transfer_function_parameters");
    if (!py_src_transfer_function_parameters.is_none())
    {
        auto py_list = handle.attr("src_transfer_function_parameters").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<float>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<float>();
        }

        obj.srcTransferFunctionParameters = value;
    }
    auto py_conversion_matrix = handle.attr("conversion_matrix");
    if (!py_conversion_matrix.is_none())
    {
        auto py_list = handle.attr("conversion_matrix").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<float>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<float>();
        }

        obj.conversionMatrix = value;
    }
    auto py_dst_transfer_function_parameters = handle.attr("dst_transfer_function_parameters");
    if (!py_dst_transfer_function_parameters.is_none())
    {
        auto py_list = handle.attr("dst_transfer_function_parameters").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<float>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<float>();
        }

        obj.dstTransferFunctionParameters = value;
    }
    auto py_dst_alpha_mode = handle.attr("dst_alpha_mode");
    if (!py_dst_alpha_mode.is_none())
    {
        auto value = handle.attr("dst_alpha_mode").cast<AlphaMode>();
        obj.dstAlphaMode = value;
    }
    auto py_internal_usage = handle.attr("internal_usage");
    if (!py_internal_usage.is_none())
    {
        auto value = handle.attr("internal_usage").cast<Bool>();
        obj.internalUsage = value;
    }
}

inline void fill(pywgpu::AHardwareBufferProperties& obj, py::handle handle, BuildCtx ctx) {
    auto py_y_cb_cr_info = handle.attr("y_cb_cr_info");
    if (!py_y_cb_cr_info.is_none())
    {
        Builder<YCbCrVkDescriptor>(ctx).fill(obj.yCbCrInfo, handle.attr("y_cb_cr_info"));
    }
}

inline void fill(pywgpu::Limits& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStructOut>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_max_texture_dimension_1D = handle.attr("max_texture_dimension_1D");
    if (!py_max_texture_dimension_1D.is_none())
    {
        auto value = handle.attr("max_texture_dimension_1D").cast<uint32_t>();
        obj.maxTextureDimension1D = value;
    }
    auto py_max_texture_dimension_2D = handle.attr("max_texture_dimension_2D");
    if (!py_max_texture_dimension_2D.is_none())
    {
        auto value = handle.attr("max_texture_dimension_2D").cast<uint32_t>();
        obj.maxTextureDimension2D = value;
    }
    auto py_max_texture_dimension_3D = handle.attr("max_texture_dimension_3D");
    if (!py_max_texture_dimension_3D.is_none())
    {
        auto value = handle.attr("max_texture_dimension_3D").cast<uint32_t>();
        obj.maxTextureDimension3D = value;
    }
    auto py_max_texture_array_layers = handle.attr("max_texture_array_layers");
    if (!py_max_texture_array_layers.is_none())
    {
        auto value = handle.attr("max_texture_array_layers").cast<uint32_t>();
        obj.maxTextureArrayLayers = value;
    }
    auto py_max_bind_groups = handle.attr("max_bind_groups");
    if (!py_max_bind_groups.is_none())
    {
        auto value = handle.attr("max_bind_groups").cast<uint32_t>();
        obj.maxBindGroups = value;
    }
    auto py_max_bind_groups_plus_vertex_buffers = handle.attr("max_bind_groups_plus_vertex_buffers");
    if (!py_max_bind_groups_plus_vertex_buffers.is_none())
    {
        auto value = handle.attr("max_bind_groups_plus_vertex_buffers").cast<uint32_t>();
        obj.maxBindGroupsPlusVertexBuffers = value;
    }
    auto py_max_bindings_per_bind_group = handle.attr("max_bindings_per_bind_group");
    if (!py_max_bindings_per_bind_group.is_none())
    {
        auto value = handle.attr("max_bindings_per_bind_group").cast<uint32_t>();
        obj.maxBindingsPerBindGroup = value;
    }
    auto py_max_dynamic_uniform_buffers_per_pipeline_layout = handle.attr("max_dynamic_uniform_buffers_per_pipeline_layout");
    if (!py_max_dynamic_uniform_buffers_per_pipeline_layout.is_none())
    {
        auto value = handle.attr("max_dynamic_uniform_buffers_per_pipeline_layout").cast<uint32_t>();
        obj.maxDynamicUniformBuffersPerPipelineLayout = value;
    }
    auto py_max_dynamic_storage_buffers_per_pipeline_layout = handle.attr("max_dynamic_storage_buffers_per_pipeline_layout");
    if (!py_max_dynamic_storage_buffers_per_pipeline_layout.is_none())
    {
        auto value = handle.attr("max_dynamic_storage_buffers_per_pipeline_layout").cast<uint32_t>();
        obj.maxDynamicStorageBuffersPerPipelineLayout = value;
    }
    auto py_max_sampled_textures_per_shader_stage = handle.attr("max_sampled_textures_per_shader_stage");
    if (!py_max_sampled_textures_per_shader_stage.is_none())
    {
        auto value = handle.attr("max_sampled_textures_per_shader_stage").cast<uint32_t>();
        obj.maxSampledTexturesPerShaderStage = value;
    }
    auto py_max_samplers_per_shader_stage = handle.attr("max_samplers_per_shader_stage");
    if (!py_max_samplers_per_shader_stage.is_none())
    {
        auto value = handle.attr("max_samplers_per_shader_stage").cast<uint32_t>();
        obj.maxSamplersPerShaderStage = value;
    }
    auto py_max_storage_buffers_per_shader_stage = handle.attr("max_storage_buffers_per_shader_stage");
    if (!py_max_storage_buffers_per_shader_stage.is_none())
    {
        auto value = handle.attr("max_storage_buffers_per_shader_stage").cast<uint32_t>();
        obj.maxStorageBuffersPerShaderStage = value;
    }
    auto py_max_storage_textures_per_shader_stage = handle.attr("max_storage_textures_per_shader_stage");
    if (!py_max_storage_textures_per_shader_stage.is_none())
    {
        auto value = handle.attr("max_storage_textures_per_shader_stage").cast<uint32_t>();
        obj.maxStorageTexturesPerShaderStage = value;
    }
    auto py_max_uniform_buffers_per_shader_stage = handle.attr("max_uniform_buffers_per_shader_stage");
    if (!py_max_uniform_buffers_per_shader_stage.is_none())
    {
        auto value = handle.attr("max_uniform_buffers_per_shader_stage").cast<uint32_t>();
        obj.maxUniformBuffersPerShaderStage = value;
    }
    auto py_max_uniform_buffer_binding_size = handle.attr("max_uniform_buffer_binding_size");
    if (!py_max_uniform_buffer_binding_size.is_none())
    {
        auto value = handle.attr("max_uniform_buffer_binding_size").cast<uint64_t>();
        obj.maxUniformBufferBindingSize = value;
    }
    auto py_max_storage_buffer_binding_size = handle.attr("max_storage_buffer_binding_size");
    if (!py_max_storage_buffer_binding_size.is_none())
    {
        auto value = handle.attr("max_storage_buffer_binding_size").cast<uint64_t>();
        obj.maxStorageBufferBindingSize = value;
    }
    auto py_min_uniform_buffer_offset_alignment = handle.attr("min_uniform_buffer_offset_alignment");
    if (!py_min_uniform_buffer_offset_alignment.is_none())
    {
        auto value = handle.attr("min_uniform_buffer_offset_alignment").cast<uint32_t>();
        obj.minUniformBufferOffsetAlignment = value;
    }
    auto py_min_storage_buffer_offset_alignment = handle.attr("min_storage_buffer_offset_alignment");
    if (!py_min_storage_buffer_offset_alignment.is_none())
    {
        auto value = handle.attr("min_storage_buffer_offset_alignment").cast<uint32_t>();
        obj.minStorageBufferOffsetAlignment = value;
    }
    auto py_max_vertex_buffers = handle.attr("max_vertex_buffers");
    if (!py_max_vertex_buffers.is_none())
    {
        auto value = handle.attr("max_vertex_buffers").cast<uint32_t>();
        obj.maxVertexBuffers = value;
    }
    auto py_max_buffer_size = handle.attr("max_buffer_size");
    if (!py_max_buffer_size.is_none())
    {
        auto value = handle.attr("max_buffer_size").cast<uint64_t>();
        obj.maxBufferSize = value;
    }
    auto py_max_vertex_attributes = handle.attr("max_vertex_attributes");
    if (!py_max_vertex_attributes.is_none())
    {
        auto value = handle.attr("max_vertex_attributes").cast<uint32_t>();
        obj.maxVertexAttributes = value;
    }
    auto py_max_vertex_buffer_array_stride = handle.attr("max_vertex_buffer_array_stride");
    if (!py_max_vertex_buffer_array_stride.is_none())
    {
        auto value = handle.attr("max_vertex_buffer_array_stride").cast<uint32_t>();
        obj.maxVertexBufferArrayStride = value;
    }
    auto py_max_inter_stage_shader_variables = handle.attr("max_inter_stage_shader_variables");
    if (!py_max_inter_stage_shader_variables.is_none())
    {
        auto value = handle.attr("max_inter_stage_shader_variables").cast<uint32_t>();
        obj.maxInterStageShaderVariables = value;
    }
    auto py_max_color_attachments = handle.attr("max_color_attachments");
    if (!py_max_color_attachments.is_none())
    {
        auto value = handle.attr("max_color_attachments").cast<uint32_t>();
        obj.maxColorAttachments = value;
    }
    auto py_max_color_attachment_bytes_per_sample = handle.attr("max_color_attachment_bytes_per_sample");
    if (!py_max_color_attachment_bytes_per_sample.is_none())
    {
        auto value = handle.attr("max_color_attachment_bytes_per_sample").cast<uint32_t>();
        obj.maxColorAttachmentBytesPerSample = value;
    }
    auto py_max_compute_workgroup_storage_size = handle.attr("max_compute_workgroup_storage_size");
    if (!py_max_compute_workgroup_storage_size.is_none())
    {
        auto value = handle.attr("max_compute_workgroup_storage_size").cast<uint32_t>();
        obj.maxComputeWorkgroupStorageSize = value;
    }
    auto py_max_compute_invocations_per_workgroup = handle.attr("max_compute_invocations_per_workgroup");
    if (!py_max_compute_invocations_per_workgroup.is_none())
    {
        auto value = handle.attr("max_compute_invocations_per_workgroup").cast<uint32_t>();
        obj.maxComputeInvocationsPerWorkgroup = value;
    }
    auto py_max_compute_workgroup_size_x = handle.attr("max_compute_workgroup_size_x");
    if (!py_max_compute_workgroup_size_x.is_none())
    {
        auto value = handle.attr("max_compute_workgroup_size_x").cast<uint32_t>();
        obj.maxComputeWorkgroupSizeX = value;
    }
    auto py_max_compute_workgroup_size_y = handle.attr("max_compute_workgroup_size_y");
    if (!py_max_compute_workgroup_size_y.is_none())
    {
        auto value = handle.attr("max_compute_workgroup_size_y").cast<uint32_t>();
        obj.maxComputeWorkgroupSizeY = value;
    }
    auto py_max_compute_workgroup_size_z = handle.attr("max_compute_workgroup_size_z");
    if (!py_max_compute_workgroup_size_z.is_none())
    {
        auto value = handle.attr("max_compute_workgroup_size_z").cast<uint32_t>();
        obj.maxComputeWorkgroupSizeZ = value;
    }
    auto py_max_compute_workgroups_per_dimension = handle.attr("max_compute_workgroups_per_dimension");
    if (!py_max_compute_workgroups_per_dimension.is_none())
    {
        auto value = handle.attr("max_compute_workgroups_per_dimension").cast<uint32_t>();
        obj.maxComputeWorkgroupsPerDimension = value;
    }
    auto py_max_storage_buffers_in_vertex_stage = handle.attr("max_storage_buffers_in_vertex_stage");
    if (!py_max_storage_buffers_in_vertex_stage.is_none())
    {
        auto value = handle.attr("max_storage_buffers_in_vertex_stage").cast<uint32_t>();
        obj.maxStorageBuffersInVertexStage = value;
    }
    auto py_max_storage_textures_in_vertex_stage = handle.attr("max_storage_textures_in_vertex_stage");
    if (!py_max_storage_textures_in_vertex_stage.is_none())
    {
        auto value = handle.attr("max_storage_textures_in_vertex_stage").cast<uint32_t>();
        obj.maxStorageTexturesInVertexStage = value;
    }
    auto py_max_storage_buffers_in_fragment_stage = handle.attr("max_storage_buffers_in_fragment_stage");
    if (!py_max_storage_buffers_in_fragment_stage.is_none())
    {
        auto value = handle.attr("max_storage_buffers_in_fragment_stage").cast<uint32_t>();
        obj.maxStorageBuffersInFragmentStage = value;
    }
    auto py_max_storage_textures_in_fragment_stage = handle.attr("max_storage_textures_in_fragment_stage");
    if (!py_max_storage_textures_in_fragment_stage.is_none())
    {
        auto value = handle.attr("max_storage_textures_in_fragment_stage").cast<uint32_t>();
        obj.maxStorageTexturesInFragmentStage = value;
    }
}

inline void fill(pywgpu::SupportedFeatures& obj, py::handle handle, BuildCtx ctx) {
    auto py_features = handle.attr("features");
    if (!py_features.is_none())
    {
        auto py_list = handle.attr("features").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<FeatureName>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<FeatureName>();
        }

        obj.features = value;
        obj.featureCount = count;
    }
}

inline void fill(pywgpu::SupportedWGSLLanguageFeatures& obj, py::handle handle, BuildCtx ctx) {
    auto py_features = handle.attr("features");
    if (!py_features.is_none())
    {
        auto py_list = handle.attr("features").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<WGSLLanguageFeatureName>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<WGSLLanguageFeatureName>();
        }

        obj.features = value;
        obj.featureCount = count;
    }
}

inline void fill(pywgpu::Extent2D& obj, py::handle handle, BuildCtx ctx) {
    auto py_width = handle.attr("width");
    if (!py_width.is_none())
    {
        auto value = handle.attr("width").cast<uint32_t>();
        obj.width = value;
    }
    auto py_height = handle.attr("height");
    if (!py_height.is_none())
    {
        auto value = handle.attr("height").cast<uint32_t>();
        obj.height = value;
    }
}

inline void fill(pywgpu::Extent3D& obj, py::handle handle, BuildCtx ctx) {
    auto py_width = handle.attr("width");
    if (!py_width.is_none())
    {
        auto value = handle.attr("width").cast<uint32_t>();
        obj.width = value;
    }
    auto py_height = handle.attr("height");
    if (!py_height.is_none())
    {
        auto value = handle.attr("height").cast<uint32_t>();
        obj.height = value;
    }
    auto py_depth_or_array_layers = handle.attr("depth_or_array_layers");
    if (!py_depth_or_array_layers.is_none())
    {
        auto value = handle.attr("depth_or_array_layers").cast<uint32_t>();
        obj.depthOrArrayLayers = value;
    }
}

inline void fill(pywgpu::ExternalTextureDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_label = handle.attr("label");
    if (!py_label.is_none())
    {
        auto value = handle.attr("label").cast<StringView>();
        obj.label = value;
    }
    auto py_plane_0 = handle.attr("plane_0");
    if (!py_plane_0.is_none())
    {
        auto value = handle.attr("plane_0").cast<TextureView>();
        obj.plane0 = value;
    }
    auto py_plane_1 = handle.attr("plane_1");
    if (!py_plane_1.is_none())
    {
        auto value = handle.attr("plane_1").cast<TextureView>();
        obj.plane1 = value;
    }
    auto py_crop_origin = handle.attr("crop_origin");
    if (!py_crop_origin.is_none())
    {
        Builder<Origin2D>(ctx).fill(obj.cropOrigin, handle.attr("crop_origin"));
    }
    auto py_crop_size = handle.attr("crop_size");
    if (!py_crop_size.is_none())
    {
        Builder<Extent2D>(ctx).fill(obj.cropSize, handle.attr("crop_size"));
    }
    auto py_apparent_size = handle.attr("apparent_size");
    if (!py_apparent_size.is_none())
    {
        Builder<Extent2D>(ctx).fill(obj.apparentSize, handle.attr("apparent_size"));
    }
    auto py_do_yuv_to_rgb_conversion_only = handle.attr("do_yuv_to_rgb_conversion_only");
    if (!py_do_yuv_to_rgb_conversion_only.is_none())
    {
        auto value = handle.attr("do_yuv_to_rgb_conversion_only").cast<Bool>();
        obj.doYuvToRgbConversionOnly = value;
    }
    auto py_yuv_to_rgb_conversion_matrix = handle.attr("yuv_to_rgb_conversion_matrix");
    if (!py_yuv_to_rgb_conversion_matrix.is_none())
    {
        auto py_list = handle.attr("yuv_to_rgb_conversion_matrix").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<float>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<float>();
        }

        obj.yuvToRgbConversionMatrix = value;
    }
    auto py_src_transfer_function_parameters = handle.attr("src_transfer_function_parameters");
    if (!py_src_transfer_function_parameters.is_none())
    {
        auto py_list = handle.attr("src_transfer_function_parameters").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<float>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<float>();
        }

        obj.srcTransferFunctionParameters = value;
    }
    auto py_dst_transfer_function_parameters = handle.attr("dst_transfer_function_parameters");
    if (!py_dst_transfer_function_parameters.is_none())
    {
        auto py_list = handle.attr("dst_transfer_function_parameters").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<float>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<float>();
        }

        obj.dstTransferFunctionParameters = value;
    }
    auto py_gamut_conversion_matrix = handle.attr("gamut_conversion_matrix");
    if (!py_gamut_conversion_matrix.is_none())
    {
        auto py_list = handle.attr("gamut_conversion_matrix").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<float>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<float>();
        }

        obj.gamutConversionMatrix = value;
    }
    auto py_mirrored = handle.attr("mirrored");
    if (!py_mirrored.is_none())
    {
        auto value = handle.attr("mirrored").cast<Bool>();
        obj.mirrored = value;
    }
    auto py_rotation = handle.attr("rotation");
    if (!py_rotation.is_none())
    {
        auto value = handle.attr("rotation").cast<ExternalTextureRotation>();
        obj.rotation = value;
    }
}

inline void fill(pywgpu::SharedBufferMemoryDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_label = handle.attr("label");
    if (!py_label.is_none())
    {
        auto value = handle.attr("label").cast<StringView>();
        obj.label = value;
    }
}

inline void fill(pywgpu::SharedTextureMemoryDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_label = handle.attr("label");
    if (!py_label.is_none())
    {
        auto value = handle.attr("label").cast<StringView>();
        obj.label = value;
    }
}

inline void fill(pywgpu::SharedBufferMemoryBeginAccessDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_initialized = handle.attr("initialized");
    if (!py_initialized.is_none())
    {
        auto value = handle.attr("initialized").cast<Bool>();
        obj.initialized = value;
    }
    auto py_fences = handle.attr("fences");
    if (!py_fences.is_none())
    {
        auto py_list = handle.attr("fences").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<SharedFence>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<SharedFence>();
        }

        obj.fences = value;
        obj.fenceCount = count;
    }
    auto py_signaled_values = handle.attr("signaled_values");
    if (!py_signaled_values.is_none())
    {
        auto py_list = handle.attr("signaled_values").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<uint64_t>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<uint64_t>();
        }

        obj.signaledValues = value;
        obj.fenceCount = count;
    }
}

inline void fill(pywgpu::SharedTextureMemoryVkDedicatedAllocationDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_dedicated_allocation = handle.attr("dedicated_allocation");
    if (!py_dedicated_allocation.is_none())
    {
        auto value = handle.attr("dedicated_allocation").cast<Bool>();
        obj.dedicatedAllocation = value;
    }
}

inline void fill(pywgpu::SharedTextureMemoryAHardwareBufferDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_handle = handle.attr("handle");
    if (!py_handle.is_none())
    {
        auto value = handle.attr("handle").cast<void *>();
        obj.handle = value;
    }
    auto py_use_external_format = handle.attr("use_external_format");
    if (!py_use_external_format.is_none())
    {
        auto value = handle.attr("use_external_format").cast<Bool>();
        obj.useExternalFormat = value;
    }
}

inline void fill(pywgpu::SharedTextureMemoryDmaBufPlane& obj, py::handle handle, BuildCtx ctx) {
    auto py_fd = handle.attr("fd");
    if (!py_fd.is_none())
    {
        auto value = handle.attr("fd").cast<int>();
        obj.fd = value;
    }
    auto py_offset = handle.attr("offset");
    if (!py_offset.is_none())
    {
        auto value = handle.attr("offset").cast<uint64_t>();
        obj.offset = value;
    }
    auto py_stride = handle.attr("stride");
    if (!py_stride.is_none())
    {
        auto value = handle.attr("stride").cast<uint32_t>();
        obj.stride = value;
    }
}

inline void fill(pywgpu::SharedTextureMemoryDmaBufDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_size = handle.attr("size");
    if (!py_size.is_none())
    {
        Builder<Extent3D>(ctx).fill(obj.size, handle.attr("size"));
    }
    auto py_drm_format = handle.attr("drm_format");
    if (!py_drm_format.is_none())
    {
        auto value = handle.attr("drm_format").cast<uint32_t>();
        obj.drmFormat = value;
    }
    auto py_drm_modifier = handle.attr("drm_modifier");
    if (!py_drm_modifier.is_none())
    {
        auto value = handle.attr("drm_modifier").cast<uint64_t>();
        obj.drmModifier = value;
    }
    auto py_planes = handle.attr("planes");
    if (!py_planes.is_none())
    {
        auto py_list = handle.attr("planes").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<SharedTextureMemoryDmaBufPlane>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<SharedTextureMemoryDmaBufPlane>();
        }

        obj.planes = value;
        obj.planeCount = count;
    }
}

inline void fill(pywgpu::SharedTextureMemoryOpaqueFDDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_vk_image_create_info = handle.attr("vk_image_create_info");
    if (!py_vk_image_create_info.is_none())
    {
        auto value = handle.attr("vk_image_create_info").cast<void const *>();
        obj.vkImageCreateInfo = value;
    }
    auto py_memory_FD = handle.attr("memory_FD");
    if (!py_memory_FD.is_none())
    {
        auto value = handle.attr("memory_FD").cast<int>();
        obj.memoryFD = value;
    }
    auto py_memory_type_index = handle.attr("memory_type_index");
    if (!py_memory_type_index.is_none())
    {
        auto value = handle.attr("memory_type_index").cast<uint32_t>();
        obj.memoryTypeIndex = value;
    }
    auto py_allocation_size = handle.attr("allocation_size");
    if (!py_allocation_size.is_none())
    {
        auto value = handle.attr("allocation_size").cast<uint64_t>();
        obj.allocationSize = value;
    }
    auto py_dedicated_allocation = handle.attr("dedicated_allocation");
    if (!py_dedicated_allocation.is_none())
    {
        auto value = handle.attr("dedicated_allocation").cast<Bool>();
        obj.dedicatedAllocation = value;
    }
}

inline void fill(pywgpu::SharedTextureMemoryZirconHandleDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_memory_FD = handle.attr("memory_FD");
    if (!py_memory_FD.is_none())
    {
        auto value = handle.attr("memory_FD").cast<uint32_t>();
        obj.memoryFD = value;
    }
    auto py_allocation_size = handle.attr("allocation_size");
    if (!py_allocation_size.is_none())
    {
        auto value = handle.attr("allocation_size").cast<uint64_t>();
        obj.allocationSize = value;
    }
}

inline void fill(pywgpu::SharedTextureMemoryDXGISharedHandleDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_handle = handle.attr("handle");
    if (!py_handle.is_none())
    {
        auto value = handle.attr("handle").cast<void *>();
        obj.handle = value;
    }
    auto py_use_keyed_mutex = handle.attr("use_keyed_mutex");
    if (!py_use_keyed_mutex.is_none())
    {
        auto value = handle.attr("use_keyed_mutex").cast<Bool>();
        obj.useKeyedMutex = value;
    }
}

inline void fill(pywgpu::SharedTextureMemoryIOSurfaceDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_io_surface = handle.attr("io_surface");
    if (!py_io_surface.is_none())
    {
        auto value = handle.attr("io_surface").cast<void *>();
        obj.ioSurface = value;
    }
    auto py_allow_storage_binding = handle.attr("allow_storage_binding");
    if (!py_allow_storage_binding.is_none())
    {
        auto value = handle.attr("allow_storage_binding").cast<Bool>();
        obj.allowStorageBinding = value;
    }
}

inline void fill(pywgpu::SharedTextureMemoryEGLImageDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_image = handle.attr("image");
    if (!py_image.is_none())
    {
        auto value = handle.attr("image").cast<void *>();
        obj.image = value;
    }
}

inline void fill(pywgpu::SharedTextureMemoryBeginAccessDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_concurrent_read = handle.attr("concurrent_read");
    if (!py_concurrent_read.is_none())
    {
        auto value = handle.attr("concurrent_read").cast<Bool>();
        obj.concurrentRead = value;
    }
    auto py_initialized = handle.attr("initialized");
    if (!py_initialized.is_none())
    {
        auto value = handle.attr("initialized").cast<Bool>();
        obj.initialized = value;
    }
    auto py_fences = handle.attr("fences");
    if (!py_fences.is_none())
    {
        auto py_list = handle.attr("fences").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<SharedFence>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<SharedFence>();
        }

        obj.fences = value;
        obj.fenceCount = count;
    }
    auto py_signaled_values = handle.attr("signaled_values");
    if (!py_signaled_values.is_none())
    {
        auto py_list = handle.attr("signaled_values").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<uint64_t>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<uint64_t>();
        }

        obj.signaledValues = value;
        obj.fenceCount = count;
    }
}

inline void fill(pywgpu::SharedTextureMemoryVkImageLayoutBeginState& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_old_layout = handle.attr("old_layout");
    if (!py_old_layout.is_none())
    {
        auto value = handle.attr("old_layout").cast<int32_t>();
        obj.oldLayout = value;
    }
    auto py_new_layout = handle.attr("new_layout");
    if (!py_new_layout.is_none())
    {
        auto value = handle.attr("new_layout").cast<int32_t>();
        obj.newLayout = value;
    }
}

inline void fill(pywgpu::SharedTextureMemoryD3DSwapchainBeginState& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_is_swapchain = handle.attr("is_swapchain");
    if (!py_is_swapchain.is_none())
    {
        auto value = handle.attr("is_swapchain").cast<Bool>();
        obj.isSwapchain = value;
    }
}

inline void fill(pywgpu::SharedFenceDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_label = handle.attr("label");
    if (!py_label.is_none())
    {
        auto value = handle.attr("label").cast<StringView>();
        obj.label = value;
    }
}

inline void fill(pywgpu::SharedFenceVkSemaphoreOpaqueFDDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_handle = handle.attr("handle");
    if (!py_handle.is_none())
    {
        auto value = handle.attr("handle").cast<int>();
        obj.handle = value;
    }
}

inline void fill(pywgpu::SharedFenceSyncFDDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_handle = handle.attr("handle");
    if (!py_handle.is_none())
    {
        auto value = handle.attr("handle").cast<int>();
        obj.handle = value;
    }
}

inline void fill(pywgpu::SharedFenceVkSemaphoreZirconHandleDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_handle = handle.attr("handle");
    if (!py_handle.is_none())
    {
        auto value = handle.attr("handle").cast<uint32_t>();
        obj.handle = value;
    }
}

inline void fill(pywgpu::SharedFenceDXGISharedHandleDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_handle = handle.attr("handle");
    if (!py_handle.is_none())
    {
        auto value = handle.attr("handle").cast<void *>();
        obj.handle = value;
    }
}

inline void fill(pywgpu::SharedFenceMTLSharedEventDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_shared_event = handle.attr("shared_event");
    if (!py_shared_event.is_none())
    {
        auto value = handle.attr("shared_event").cast<void *>();
        obj.sharedEvent = value;
    }
}

inline void fill(pywgpu::SharedFenceEGLSyncDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_sync = handle.attr("sync");
    if (!py_sync.is_none())
    {
        auto value = handle.attr("sync").cast<void *>();
        obj.sync = value;
    }
}

inline void fill(pywgpu::DawnFakeBufferOOMForTesting& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_fake_OOM_at_wire_client_map = handle.attr("fake_OOM_at_wire_client_map");
    if (!py_fake_OOM_at_wire_client_map.is_none())
    {
        auto value = handle.attr("fake_OOM_at_wire_client_map").cast<Bool>();
        obj.fakeOOMAtWireClientMap = value;
    }
    auto py_fake_OOM_at_native_map = handle.attr("fake_OOM_at_native_map");
    if (!py_fake_OOM_at_native_map.is_none())
    {
        auto value = handle.attr("fake_OOM_at_native_map").cast<Bool>();
        obj.fakeOOMAtNativeMap = value;
    }
    auto py_fake_OOM_at_device = handle.attr("fake_OOM_at_device");
    if (!py_fake_OOM_at_device.is_none())
    {
        auto value = handle.attr("fake_OOM_at_device").cast<Bool>();
        obj.fakeOOMAtDevice = value;
    }
}

inline void fill(pywgpu::DawnDrmFormatProperties& obj, py::handle handle, BuildCtx ctx) {
    auto py_modifier = handle.attr("modifier");
    if (!py_modifier.is_none())
    {
        auto value = handle.attr("modifier").cast<uint64_t>();
        obj.modifier = value;
    }
    auto py_modifier_plane_count = handle.attr("modifier_plane_count");
    if (!py_modifier_plane_count.is_none())
    {
        auto value = handle.attr("modifier_plane_count").cast<uint32_t>();
        obj.modifierPlaneCount = value;
    }
}

inline void fill(pywgpu::TexelCopyBufferInfo& obj, py::handle handle, BuildCtx ctx) {
    auto py_layout = handle.attr("layout");
    if (!py_layout.is_none())
    {
        Builder<TexelCopyBufferLayout>(ctx).fill(obj.layout, handle.attr("layout"));
    }
    auto py_buffer = handle.attr("buffer");
    if (!py_buffer.is_none())
    {
        auto value = handle.attr("buffer").cast<Buffer>();
        obj.buffer = value;
    }
}

inline void fill(pywgpu::TexelCopyBufferLayout& obj, py::handle handle, BuildCtx ctx) {
    auto py_offset = handle.attr("offset");
    if (!py_offset.is_none())
    {
        auto value = handle.attr("offset").cast<uint64_t>();
        obj.offset = value;
    }
    auto py_bytes_per_row = handle.attr("bytes_per_row");
    if (!py_bytes_per_row.is_none())
    {
        auto value = handle.attr("bytes_per_row").cast<uint32_t>();
        obj.bytesPerRow = value;
    }
    auto py_rows_per_image = handle.attr("rows_per_image");
    if (!py_rows_per_image.is_none())
    {
        auto value = handle.attr("rows_per_image").cast<uint32_t>();
        obj.rowsPerImage = value;
    }
}

inline void fill(pywgpu::TexelCopyTextureInfo& obj, py::handle handle, BuildCtx ctx) {
    auto py_texture = handle.attr("texture");
    if (!py_texture.is_none())
    {
        auto value = handle.attr("texture").cast<Texture>();
        obj.texture = value;
    }
    auto py_mip_level = handle.attr("mip_level");
    if (!py_mip_level.is_none())
    {
        auto value = handle.attr("mip_level").cast<uint32_t>();
        obj.mipLevel = value;
    }
    auto py_origin = handle.attr("origin");
    if (!py_origin.is_none())
    {
        Builder<Origin3D>(ctx).fill(obj.origin, handle.attr("origin"));
    }
    auto py_aspect = handle.attr("aspect");
    if (!py_aspect.is_none())
    {
        auto value = handle.attr("aspect").cast<TextureAspect>();
        obj.aspect = value;
    }
}

inline void fill(pywgpu::ImageCopyExternalTexture& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_external_texture = handle.attr("external_texture");
    if (!py_external_texture.is_none())
    {
        auto value = handle.attr("external_texture").cast<ExternalTexture>();
        obj.externalTexture = value;
    }
    auto py_origin = handle.attr("origin");
    if (!py_origin.is_none())
    {
        Builder<Origin3D>(ctx).fill(obj.origin, handle.attr("origin"));
    }
    auto py_natural_size = handle.attr("natural_size");
    if (!py_natural_size.is_none())
    {
        Builder<Extent2D>(ctx).fill(obj.naturalSize, handle.attr("natural_size"));
    }
}

inline void fill(pywgpu::FutureWaitInfo& obj, py::handle handle, BuildCtx ctx) {
    auto py_future = handle.attr("future");
    if (!py_future.is_none())
    {
        auto value = handle.attr("future").cast<Future>();
        obj.future = value;
    }
    auto py_completed = handle.attr("completed");
    if (!py_completed.is_none())
    {
        auto value = handle.attr("completed").cast<Bool>();
        obj.completed = value;
    }
}

inline void fill(pywgpu::InstanceCapabilities& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStructOut>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_timed_wait_any_enable = handle.attr("timed_wait_any_enable");
    if (!py_timed_wait_any_enable.is_none())
    {
        auto value = handle.attr("timed_wait_any_enable").cast<Bool>();
        obj.timedWaitAnyEnable = value;
    }
    auto py_timed_wait_any_max_count = handle.attr("timed_wait_any_max_count");
    if (!py_timed_wait_any_max_count.is_none())
    {
        auto value = handle.attr("timed_wait_any_max_count").cast<size_t>();
        obj.timedWaitAnyMaxCount = value;
    }
}

inline void fill(pywgpu::InstanceDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_capabilities = handle.attr("capabilities");
    if (!py_capabilities.is_none())
    {
        Builder<InstanceCapabilities>(ctx).fill(obj.capabilities, handle.attr("capabilities"));
    }
}

inline void fill(pywgpu::DawnWireWGSLControl& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_enable_experimental = handle.attr("enable_experimental");
    if (!py_enable_experimental.is_none())
    {
        auto value = handle.attr("enable_experimental").cast<Bool>();
        obj.enableExperimental = value;
    }
    auto py_enable_unsafe = handle.attr("enable_unsafe");
    if (!py_enable_unsafe.is_none())
    {
        auto value = handle.attr("enable_unsafe").cast<Bool>();
        obj.enableUnsafe = value;
    }
    auto py_enable_testing = handle.attr("enable_testing");
    if (!py_enable_testing.is_none())
    {
        auto value = handle.attr("enable_testing").cast<Bool>();
        obj.enableTesting = value;
    }
}

inline void fill(pywgpu::DawnInjectedInvalidSType& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_invalid_s_type = handle.attr("invalid_s_type");
    if (!py_invalid_s_type.is_none())
    {
        auto value = handle.attr("invalid_s_type").cast<SType>();
        obj.invalidSType = value;
    }
}

inline void fill(pywgpu::VertexAttribute& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_format = handle.attr("format");
    if (!py_format.is_none())
    {
        auto value = handle.attr("format").cast<VertexFormat>();
        obj.format = value;
    }
    auto py_offset = handle.attr("offset");
    if (!py_offset.is_none())
    {
        auto value = handle.attr("offset").cast<uint64_t>();
        obj.offset = value;
    }
    auto py_shader_location = handle.attr("shader_location");
    if (!py_shader_location.is_none())
    {
        auto value = handle.attr("shader_location").cast<uint32_t>();
        obj.shaderLocation = value;
    }
}

inline void fill(pywgpu::VertexBufferLayout& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_step_mode = handle.attr("step_mode");
    if (!py_step_mode.is_none())
    {
        auto value = handle.attr("step_mode").cast<VertexStepMode>();
        obj.stepMode = value;
    }
    auto py_array_stride = handle.attr("array_stride");
    if (!py_array_stride.is_none())
    {
        auto value = handle.attr("array_stride").cast<uint64_t>();
        obj.arrayStride = value;
    }
    auto py_attributes = handle.attr("attributes");
    if (!py_attributes.is_none())
    {
        auto py_list = handle.attr("attributes").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<VertexAttribute>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<VertexAttribute>();
        }

        obj.attributes = value;
        obj.attributeCount = count;
    }
}

inline void fill(pywgpu::Origin3D& obj, py::handle handle, BuildCtx ctx) {
    auto py_x = handle.attr("x");
    if (!py_x.is_none())
    {
        auto value = handle.attr("x").cast<uint32_t>();
        obj.x = value;
    }
    auto py_y = handle.attr("y");
    if (!py_y.is_none())
    {
        auto value = handle.attr("y").cast<uint32_t>();
        obj.y = value;
    }
    auto py_z = handle.attr("z");
    if (!py_z.is_none())
    {
        auto value = handle.attr("z").cast<uint32_t>();
        obj.z = value;
    }
}

inline void fill(pywgpu::Origin2D& obj, py::handle handle, BuildCtx ctx) {
    auto py_x = handle.attr("x");
    if (!py_x.is_none())
    {
        auto value = handle.attr("x").cast<uint32_t>();
        obj.x = value;
    }
    auto py_y = handle.attr("y");
    if (!py_y.is_none())
    {
        auto value = handle.attr("y").cast<uint32_t>();
        obj.y = value;
    }
}

inline void fill(pywgpu::PassTimestampWrites& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_query_set = handle.attr("query_set");
    if (!py_query_set.is_none())
    {
        auto value = handle.attr("query_set").cast<QuerySet>();
        obj.querySet = value;
    }
    auto py_beginning_of_pass_write_index = handle.attr("beginning_of_pass_write_index");
    if (!py_beginning_of_pass_write_index.is_none())
    {
        auto value = handle.attr("beginning_of_pass_write_index").cast<uint32_t>();
        obj.beginningOfPassWriteIndex = value;
    }
    auto py_end_of_pass_write_index = handle.attr("end_of_pass_write_index");
    if (!py_end_of_pass_write_index.is_none())
    {
        auto value = handle.attr("end_of_pass_write_index").cast<uint32_t>();
        obj.endOfPassWriteIndex = value;
    }
}

inline void fill(pywgpu::PipelineLayoutDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_label = handle.attr("label");
    if (!py_label.is_none())
    {
        auto value = handle.attr("label").cast<StringView>();
        obj.label = value;
    }
    auto py_bind_group_layouts = handle.attr("bind_group_layouts");
    if (!py_bind_group_layouts.is_none())
    {
        auto py_list = handle.attr("bind_group_layouts").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<BindGroupLayout>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<BindGroupLayout>();
        }

        obj.bindGroupLayouts = value;
        obj.bindGroupLayoutCount = count;
    }
    auto py_immediate_data_range_byte_size = handle.attr("immediate_data_range_byte_size");
    if (!py_immediate_data_range_byte_size.is_none())
    {
        auto value = handle.attr("immediate_data_range_byte_size").cast<uint32_t>();
        obj.immediateDataRangeByteSize = value;
    }
}

inline void fill(pywgpu::PipelineLayoutPixelLocalStorage& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_total_pixel_local_storage_size = handle.attr("total_pixel_local_storage_size");
    if (!py_total_pixel_local_storage_size.is_none())
    {
        auto value = handle.attr("total_pixel_local_storage_size").cast<uint64_t>();
        obj.totalPixelLocalStorageSize = value;
    }
    auto py_storage_attachments = handle.attr("storage_attachments");
    if (!py_storage_attachments.is_none())
    {
        auto py_list = handle.attr("storage_attachments").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<PipelineLayoutStorageAttachment>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<PipelineLayoutStorageAttachment>();
        }

        obj.storageAttachments = value;
        obj.storageAttachmentCount = count;
    }
}

inline void fill(pywgpu::PipelineLayoutStorageAttachment& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_offset = handle.attr("offset");
    if (!py_offset.is_none())
    {
        auto value = handle.attr("offset").cast<uint64_t>();
        obj.offset = value;
    }
    auto py_format = handle.attr("format");
    if (!py_format.is_none())
    {
        auto value = handle.attr("format").cast<TextureFormat>();
        obj.format = value;
    }
}

inline void fill(pywgpu::ComputeState& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_module = handle.attr("module");
    if (!py_module.is_none())
    {
        auto value = handle.attr("module").cast<ShaderModule>();
        obj.module = value;
    }
    auto py_entry_point = handle.attr("entry_point");
    if (!py_entry_point.is_none())
    {
        auto value = handle.attr("entry_point").cast<StringView>();
        obj.entryPoint = value;
    }
    auto py_constants = handle.attr("constants");
    if (!py_constants.is_none())
    {
        auto py_list = handle.attr("constants").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<ConstantEntry>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<ConstantEntry>();
        }

        obj.constants = value;
        obj.constantCount = count;
    }
}

inline void fill(pywgpu::QuerySetDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_label = handle.attr("label");
    if (!py_label.is_none())
    {
        auto value = handle.attr("label").cast<StringView>();
        obj.label = value;
    }
    auto py_type = handle.attr("type");
    if (!py_type.is_none())
    {
        auto value = handle.attr("type").cast<QueryType>();
        obj.type = value;
    }
    auto py_count = handle.attr("count");
    if (!py_count.is_none())
    {
        auto value = handle.attr("count").cast<uint32_t>();
        obj.count = value;
    }
}

inline void fill(pywgpu::QueueDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_label = handle.attr("label");
    if (!py_label.is_none())
    {
        auto value = handle.attr("label").cast<StringView>();
        obj.label = value;
    }
}

inline void fill(pywgpu::RenderBundleDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_label = handle.attr("label");
    if (!py_label.is_none())
    {
        auto value = handle.attr("label").cast<StringView>();
        obj.label = value;
    }
}

inline void fill(pywgpu::RenderBundleEncoderDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_label = handle.attr("label");
    if (!py_label.is_none())
    {
        auto value = handle.attr("label").cast<StringView>();
        obj.label = value;
    }
    auto py_color_formats = handle.attr("color_formats");
    if (!py_color_formats.is_none())
    {
        auto py_list = handle.attr("color_formats").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<TextureFormat>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<TextureFormat>();
        }

        obj.colorFormats = value;
        obj.colorFormatCount = count;
    }
    auto py_depth_stencil_format = handle.attr("depth_stencil_format");
    if (!py_depth_stencil_format.is_none())
    {
        auto value = handle.attr("depth_stencil_format").cast<TextureFormat>();
        obj.depthStencilFormat = value;
    }
    auto py_sample_count = handle.attr("sample_count");
    if (!py_sample_count.is_none())
    {
        auto value = handle.attr("sample_count").cast<uint32_t>();
        obj.sampleCount = value;
    }
    auto py_depth_read_only = handle.attr("depth_read_only");
    if (!py_depth_read_only.is_none())
    {
        auto value = handle.attr("depth_read_only").cast<Bool>();
        obj.depthReadOnly = value;
    }
    auto py_stencil_read_only = handle.attr("stencil_read_only");
    if (!py_stencil_read_only.is_none())
    {
        auto value = handle.attr("stencil_read_only").cast<Bool>();
        obj.stencilReadOnly = value;
    }
}

inline void fill(pywgpu::RenderPassColorAttachment& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_view = handle.attr("view");
    if (!py_view.is_none())
    {
        auto value = handle.attr("view").cast<TextureView>();
        obj.view = value;
    }
    auto py_depth_slice = handle.attr("depth_slice");
    if (!py_depth_slice.is_none())
    {
        auto value = handle.attr("depth_slice").cast<uint32_t>();
        obj.depthSlice = value;
    }
    auto py_resolve_target = handle.attr("resolve_target");
    if (!py_resolve_target.is_none())
    {
        auto value = handle.attr("resolve_target").cast<TextureView>();
        obj.resolveTarget = value;
    }
    auto py_load_op = handle.attr("load_op");
    if (!py_load_op.is_none())
    {
        auto value = handle.attr("load_op").cast<LoadOp>();
        obj.loadOp = value;
    }
    auto py_store_op = handle.attr("store_op");
    if (!py_store_op.is_none())
    {
        auto value = handle.attr("store_op").cast<StoreOp>();
        obj.storeOp = value;
    }
    auto py_clear_value = handle.attr("clear_value");
    if (!py_clear_value.is_none())
    {
        Builder<Color>(ctx).fill(obj.clearValue, handle.attr("clear_value"));
    }
}

inline void fill(pywgpu::DawnRenderPassColorAttachmentRenderToSingleSampled& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_implicit_sample_count = handle.attr("implicit_sample_count");
    if (!py_implicit_sample_count.is_none())
    {
        auto value = handle.attr("implicit_sample_count").cast<uint32_t>();
        obj.implicitSampleCount = value;
    }
}

inline void fill(pywgpu::RenderPassDepthStencilAttachment& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_view = handle.attr("view");
    if (!py_view.is_none())
    {
        auto value = handle.attr("view").cast<TextureView>();
        obj.view = value;
    }
    auto py_depth_load_op = handle.attr("depth_load_op");
    if (!py_depth_load_op.is_none())
    {
        auto value = handle.attr("depth_load_op").cast<LoadOp>();
        obj.depthLoadOp = value;
    }
    auto py_depth_store_op = handle.attr("depth_store_op");
    if (!py_depth_store_op.is_none())
    {
        auto value = handle.attr("depth_store_op").cast<StoreOp>();
        obj.depthStoreOp = value;
    }
    auto py_depth_clear_value = handle.attr("depth_clear_value");
    if (!py_depth_clear_value.is_none())
    {
        auto value = handle.attr("depth_clear_value").cast<float>();
        obj.depthClearValue = value;
    }
    auto py_depth_read_only = handle.attr("depth_read_only");
    if (!py_depth_read_only.is_none())
    {
        auto value = handle.attr("depth_read_only").cast<Bool>();
        obj.depthReadOnly = value;
    }
    auto py_stencil_load_op = handle.attr("stencil_load_op");
    if (!py_stencil_load_op.is_none())
    {
        auto value = handle.attr("stencil_load_op").cast<LoadOp>();
        obj.stencilLoadOp = value;
    }
    auto py_stencil_store_op = handle.attr("stencil_store_op");
    if (!py_stencil_store_op.is_none())
    {
        auto value = handle.attr("stencil_store_op").cast<StoreOp>();
        obj.stencilStoreOp = value;
    }
    auto py_stencil_clear_value = handle.attr("stencil_clear_value");
    if (!py_stencil_clear_value.is_none())
    {
        auto value = handle.attr("stencil_clear_value").cast<uint32_t>();
        obj.stencilClearValue = value;
    }
    auto py_stencil_read_only = handle.attr("stencil_read_only");
    if (!py_stencil_read_only.is_none())
    {
        auto value = handle.attr("stencil_read_only").cast<Bool>();
        obj.stencilReadOnly = value;
    }
}

inline void fill(pywgpu::RenderPassDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_label = handle.attr("label");
    if (!py_label.is_none())
    {
        auto value = handle.attr("label").cast<StringView>();
        obj.label = value;
    }
    auto py_color_attachments = handle.attr("color_attachments");
    if (!py_color_attachments.is_none())
    {
        auto py_list = handle.attr("color_attachments").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<RenderPassColorAttachment>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<RenderPassColorAttachment>();
        }

        obj.colorAttachments = value;
        obj.colorAttachmentCount = count;
    }
    auto py_depth_stencil_attachment = handle.attr("depth_stencil_attachment");
    if (!py_depth_stencil_attachment.is_none())
    {
        auto value = Builder<RenderPassDepthStencilAttachment>(ctx).build(handle.attr("depth_stencil_attachment"));
        obj.depthStencilAttachment = value;
    }
    auto py_occlusion_query_set = handle.attr("occlusion_query_set");
    if (!py_occlusion_query_set.is_none())
    {
        auto value = handle.attr("occlusion_query_set").cast<QuerySet>();
        obj.occlusionQuerySet = value;
    }
    auto py_timestamp_writes = handle.attr("timestamp_writes");
    if (!py_timestamp_writes.is_none())
    {
        auto value = Builder<PassTimestampWrites>(ctx).build(handle.attr("timestamp_writes"));
        obj.timestampWrites = value;
    }
}

inline void fill(pywgpu::RenderPassMaxDrawCount& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_max_draw_count = handle.attr("max_draw_count");
    if (!py_max_draw_count.is_none())
    {
        auto value = handle.attr("max_draw_count").cast<uint64_t>();
        obj.maxDrawCount = value;
    }
}

inline void fill(pywgpu::RenderPassDescriptorExpandResolveRect& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_x = handle.attr("x");
    if (!py_x.is_none())
    {
        auto value = handle.attr("x").cast<uint32_t>();
        obj.x = value;
    }
    auto py_y = handle.attr("y");
    if (!py_y.is_none())
    {
        auto value = handle.attr("y").cast<uint32_t>();
        obj.y = value;
    }
    auto py_width = handle.attr("width");
    if (!py_width.is_none())
    {
        auto value = handle.attr("width").cast<uint32_t>();
        obj.width = value;
    }
    auto py_height = handle.attr("height");
    if (!py_height.is_none())
    {
        auto value = handle.attr("height").cast<uint32_t>();
        obj.height = value;
    }
}

inline void fill(pywgpu::RenderPassPixelLocalStorage& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_total_pixel_local_storage_size = handle.attr("total_pixel_local_storage_size");
    if (!py_total_pixel_local_storage_size.is_none())
    {
        auto value = handle.attr("total_pixel_local_storage_size").cast<uint64_t>();
        obj.totalPixelLocalStorageSize = value;
    }
    auto py_storage_attachments = handle.attr("storage_attachments");
    if (!py_storage_attachments.is_none())
    {
        auto py_list = handle.attr("storage_attachments").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<RenderPassStorageAttachment>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<RenderPassStorageAttachment>();
        }

        obj.storageAttachments = value;
        obj.storageAttachmentCount = count;
    }
}

inline void fill(pywgpu::RenderPassStorageAttachment& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_offset = handle.attr("offset");
    if (!py_offset.is_none())
    {
        auto value = handle.attr("offset").cast<uint64_t>();
        obj.offset = value;
    }
    auto py_storage = handle.attr("storage");
    if (!py_storage.is_none())
    {
        auto value = handle.attr("storage").cast<TextureView>();
        obj.storage = value;
    }
    auto py_load_op = handle.attr("load_op");
    if (!py_load_op.is_none())
    {
        auto value = handle.attr("load_op").cast<LoadOp>();
        obj.loadOp = value;
    }
    auto py_store_op = handle.attr("store_op");
    if (!py_store_op.is_none())
    {
        auto value = handle.attr("store_op").cast<StoreOp>();
        obj.storeOp = value;
    }
    auto py_clear_value = handle.attr("clear_value");
    if (!py_clear_value.is_none())
    {
        Builder<Color>(ctx).fill(obj.clearValue, handle.attr("clear_value"));
    }
}

inline void fill(pywgpu::VertexState& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_module = handle.attr("module");
    if (!py_module.is_none())
    {
        auto value = handle.attr("module").cast<ShaderModule>();
        obj.module = value;
    }
    auto py_entry_point = handle.attr("entry_point");
    if (!py_entry_point.is_none())
    {
        auto value = handle.attr("entry_point").cast<StringView>();
        obj.entryPoint = value;
    }
    auto py_constants = handle.attr("constants");
    if (!py_constants.is_none())
    {
        auto py_list = handle.attr("constants").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<ConstantEntry>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<ConstantEntry>();
        }

        obj.constants = value;
        obj.constantCount = count;
    }
    auto py_buffers = handle.attr("buffers");
    if (!py_buffers.is_none())
    {
        auto py_list = handle.attr("buffers").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<VertexBufferLayout>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<VertexBufferLayout>();
        }

        obj.buffers = value;
        obj.bufferCount = count;
    }
}

inline void fill(pywgpu::PrimitiveState& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_topology = handle.attr("topology");
    if (!py_topology.is_none())
    {
        auto value = handle.attr("topology").cast<PrimitiveTopology>();
        obj.topology = value;
    }
    auto py_strip_index_format = handle.attr("strip_index_format");
    if (!py_strip_index_format.is_none())
    {
        auto value = handle.attr("strip_index_format").cast<IndexFormat>();
        obj.stripIndexFormat = value;
    }
    auto py_front_face = handle.attr("front_face");
    if (!py_front_face.is_none())
    {
        auto value = handle.attr("front_face").cast<FrontFace>();
        obj.frontFace = value;
    }
    auto py_cull_mode = handle.attr("cull_mode");
    if (!py_cull_mode.is_none())
    {
        auto value = handle.attr("cull_mode").cast<CullMode>();
        obj.cullMode = value;
    }
    auto py_unclipped_depth = handle.attr("unclipped_depth");
    if (!py_unclipped_depth.is_none())
    {
        auto value = handle.attr("unclipped_depth").cast<Bool>();
        obj.unclippedDepth = value;
    }
}

inline void fill(pywgpu::DepthStencilState& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_format = handle.attr("format");
    if (!py_format.is_none())
    {
        auto value = handle.attr("format").cast<TextureFormat>();
        obj.format = value;
    }
    auto py_depth_write_enabled = handle.attr("depth_write_enabled");
    if (!py_depth_write_enabled.is_none())
    {
        auto value = handle.attr("depth_write_enabled").cast<OptionalBool>();
        obj.depthWriteEnabled = value;
    }
    auto py_depth_compare = handle.attr("depth_compare");
    if (!py_depth_compare.is_none())
    {
        auto value = handle.attr("depth_compare").cast<CompareFunction>();
        obj.depthCompare = value;
    }
    auto py_stencil_front = handle.attr("stencil_front");
    if (!py_stencil_front.is_none())
    {
        Builder<StencilFaceState>(ctx).fill(obj.stencilFront, handle.attr("stencil_front"));
    }
    auto py_stencil_back = handle.attr("stencil_back");
    if (!py_stencil_back.is_none())
    {
        Builder<StencilFaceState>(ctx).fill(obj.stencilBack, handle.attr("stencil_back"));
    }
    auto py_stencil_read_mask = handle.attr("stencil_read_mask");
    if (!py_stencil_read_mask.is_none())
    {
        auto value = handle.attr("stencil_read_mask").cast<uint32_t>();
        obj.stencilReadMask = value;
    }
    auto py_stencil_write_mask = handle.attr("stencil_write_mask");
    if (!py_stencil_write_mask.is_none())
    {
        auto value = handle.attr("stencil_write_mask").cast<uint32_t>();
        obj.stencilWriteMask = value;
    }
    auto py_depth_bias = handle.attr("depth_bias");
    if (!py_depth_bias.is_none())
    {
        auto value = handle.attr("depth_bias").cast<int32_t>();
        obj.depthBias = value;
    }
    auto py_depth_bias_slope_scale = handle.attr("depth_bias_slope_scale");
    if (!py_depth_bias_slope_scale.is_none())
    {
        auto value = handle.attr("depth_bias_slope_scale").cast<float>();
        obj.depthBiasSlopeScale = value;
    }
    auto py_depth_bias_clamp = handle.attr("depth_bias_clamp");
    if (!py_depth_bias_clamp.is_none())
    {
        auto value = handle.attr("depth_bias_clamp").cast<float>();
        obj.depthBiasClamp = value;
    }
}

inline void fill(pywgpu::MultisampleState& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_count = handle.attr("count");
    if (!py_count.is_none())
    {
        auto value = handle.attr("count").cast<uint32_t>();
        obj.count = value;
    }
    auto py_mask = handle.attr("mask");
    if (!py_mask.is_none())
    {
        auto value = handle.attr("mask").cast<uint32_t>();
        obj.mask = value;
    }
    auto py_alpha_to_coverage_enabled = handle.attr("alpha_to_coverage_enabled");
    if (!py_alpha_to_coverage_enabled.is_none())
    {
        auto value = handle.attr("alpha_to_coverage_enabled").cast<Bool>();
        obj.alphaToCoverageEnabled = value;
    }
}

inline void fill(pywgpu::FragmentState& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_module = handle.attr("module");
    if (!py_module.is_none())
    {
        auto value = handle.attr("module").cast<ShaderModule>();
        obj.module = value;
    }
    auto py_entry_point = handle.attr("entry_point");
    if (!py_entry_point.is_none())
    {
        auto value = handle.attr("entry_point").cast<StringView>();
        obj.entryPoint = value;
    }
    auto py_constants = handle.attr("constants");
    if (!py_constants.is_none())
    {
        auto py_list = handle.attr("constants").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<ConstantEntry>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<ConstantEntry>();
        }

        obj.constants = value;
        obj.constantCount = count;
    }
    auto py_targets = handle.attr("targets");
    if (!py_targets.is_none())
    {
        auto py_list = handle.attr("targets").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<ColorTargetState>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<ColorTargetState>();
        }

        obj.targets = value;
        obj.targetCount = count;
    }
}

inline void fill(pywgpu::ColorTargetState& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_format = handle.attr("format");
    if (!py_format.is_none())
    {
        auto value = handle.attr("format").cast<TextureFormat>();
        obj.format = value;
    }
    auto py_blend = handle.attr("blend");
    if (!py_blend.is_none())
    {
        auto value = Builder<BlendState>(ctx).build(handle.attr("blend"));
        obj.blend = value;
    }
    auto py_write_mask = handle.attr("write_mask");
    if (!py_write_mask.is_none())
    {
        auto value = handle.attr("write_mask").cast<ColorWriteMask>();
        obj.writeMask = value;
    }
}

inline void fill(pywgpu::ColorTargetStateExpandResolveTextureDawn& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_enabled = handle.attr("enabled");
    if (!py_enabled.is_none())
    {
        auto value = handle.attr("enabled").cast<Bool>();
        obj.enabled = value;
    }
}

inline void fill(pywgpu::BlendState& obj, py::handle handle, BuildCtx ctx) {
    auto py_color = handle.attr("color");
    if (!py_color.is_none())
    {
        Builder<BlendComponent>(ctx).fill(obj.color, handle.attr("color"));
    }
    auto py_alpha = handle.attr("alpha");
    if (!py_alpha.is_none())
    {
        Builder<BlendComponent>(ctx).fill(obj.alpha, handle.attr("alpha"));
    }
}

inline void fill(pywgpu::RenderPipelineDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_label = handle.attr("label");
    if (!py_label.is_none())
    {
        auto value = handle.attr("label").cast<StringView>();
        obj.label = value;
    }
    auto py_layout = handle.attr("layout");
    if (!py_layout.is_none())
    {
        auto value = handle.attr("layout").cast<PipelineLayout>();
        obj.layout = value;
    }
    auto py_vertex = handle.attr("vertex");
    if (!py_vertex.is_none())
    {
        Builder<VertexState>(ctx).fill(obj.vertex, handle.attr("vertex"));
    }
    auto py_primitive = handle.attr("primitive");
    if (!py_primitive.is_none())
    {
        Builder<PrimitiveState>(ctx).fill(obj.primitive, handle.attr("primitive"));
    }
    auto py_depth_stencil = handle.attr("depth_stencil");
    if (!py_depth_stencil.is_none())
    {
        auto value = Builder<DepthStencilState>(ctx).build(handle.attr("depth_stencil"));
        obj.depthStencil = value;
    }
    auto py_multisample = handle.attr("multisample");
    if (!py_multisample.is_none())
    {
        Builder<MultisampleState>(ctx).fill(obj.multisample, handle.attr("multisample"));
    }
    auto py_fragment = handle.attr("fragment");
    if (!py_fragment.is_none())
    {
        auto value = Builder<FragmentState>(ctx).build(handle.attr("fragment"));
        obj.fragment = value;
    }
}

inline void fill(pywgpu::SamplerDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_label = handle.attr("label");
    if (!py_label.is_none())
    {
        auto value = handle.attr("label").cast<StringView>();
        obj.label = value;
    }
    auto py_address_mode_u = handle.attr("address_mode_u");
    if (!py_address_mode_u.is_none())
    {
        auto value = handle.attr("address_mode_u").cast<AddressMode>();
        obj.addressModeU = value;
    }
    auto py_address_mode_v = handle.attr("address_mode_v");
    if (!py_address_mode_v.is_none())
    {
        auto value = handle.attr("address_mode_v").cast<AddressMode>();
        obj.addressModeV = value;
    }
    auto py_address_mode_w = handle.attr("address_mode_w");
    if (!py_address_mode_w.is_none())
    {
        auto value = handle.attr("address_mode_w").cast<AddressMode>();
        obj.addressModeW = value;
    }
    auto py_mag_filter = handle.attr("mag_filter");
    if (!py_mag_filter.is_none())
    {
        auto value = handle.attr("mag_filter").cast<FilterMode>();
        obj.magFilter = value;
    }
    auto py_min_filter = handle.attr("min_filter");
    if (!py_min_filter.is_none())
    {
        auto value = handle.attr("min_filter").cast<FilterMode>();
        obj.minFilter = value;
    }
    auto py_mipmap_filter = handle.attr("mipmap_filter");
    if (!py_mipmap_filter.is_none())
    {
        auto value = handle.attr("mipmap_filter").cast<MipmapFilterMode>();
        obj.mipmapFilter = value;
    }
    auto py_lod_min_clamp = handle.attr("lod_min_clamp");
    if (!py_lod_min_clamp.is_none())
    {
        auto value = handle.attr("lod_min_clamp").cast<float>();
        obj.lodMinClamp = value;
    }
    auto py_lod_max_clamp = handle.attr("lod_max_clamp");
    if (!py_lod_max_clamp.is_none())
    {
        auto value = handle.attr("lod_max_clamp").cast<float>();
        obj.lodMaxClamp = value;
    }
    auto py_compare = handle.attr("compare");
    if (!py_compare.is_none())
    {
        auto value = handle.attr("compare").cast<CompareFunction>();
        obj.compare = value;
    }
    auto py_max_anisotropy = handle.attr("max_anisotropy");
    if (!py_max_anisotropy.is_none())
    {
        auto value = handle.attr("max_anisotropy").cast<uint16_t>();
        obj.maxAnisotropy = value;
    }
}

inline void fill(pywgpu::ShaderModuleDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_label = handle.attr("label");
    if (!py_label.is_none())
    {
        auto value = handle.attr("label").cast<StringView>();
        obj.label = value;
    }
}

inline void fill(pywgpu::ShaderSourceSPIRV& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_code = handle.attr("code");
    if (!py_code.is_none())
    {
        auto py_list = handle.attr("code").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<uint32_t>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<uint32_t>();
        }

        obj.code = value;
        obj.codeSize = count;
    }
}

inline void fill(pywgpu::ShaderSourceWGSL& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_code = handle.attr("code");
    if (!py_code.is_none())
    {
        auto value = handle.attr("code").cast<StringView>();
        obj.code = value;
    }
}

inline void fill(pywgpu::DawnShaderModuleSPIRVOptionsDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_allow_non_uniform_derivatives = handle.attr("allow_non_uniform_derivatives");
    if (!py_allow_non_uniform_derivatives.is_none())
    {
        auto value = handle.attr("allow_non_uniform_derivatives").cast<Bool>();
        obj.allowNonUniformDerivatives = value;
    }
}

inline void fill(pywgpu::ShaderModuleCompilationOptions& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_strict_math = handle.attr("strict_math");
    if (!py_strict_math.is_none())
    {
        auto value = handle.attr("strict_math").cast<Bool>();
        obj.strictMath = value;
    }
}

inline void fill(pywgpu::StencilFaceState& obj, py::handle handle, BuildCtx ctx) {
    auto py_compare = handle.attr("compare");
    if (!py_compare.is_none())
    {
        auto value = handle.attr("compare").cast<CompareFunction>();
        obj.compare = value;
    }
    auto py_fail_op = handle.attr("fail_op");
    if (!py_fail_op.is_none())
    {
        auto value = handle.attr("fail_op").cast<StencilOperation>();
        obj.failOp = value;
    }
    auto py_depth_fail_op = handle.attr("depth_fail_op");
    if (!py_depth_fail_op.is_none())
    {
        auto value = handle.attr("depth_fail_op").cast<StencilOperation>();
        obj.depthFailOp = value;
    }
    auto py_pass_op = handle.attr("pass_op");
    if (!py_pass_op.is_none())
    {
        auto value = handle.attr("pass_op").cast<StencilOperation>();
        obj.passOp = value;
    }
}

inline void fill(pywgpu::SurfaceDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_label = handle.attr("label");
    if (!py_label.is_none())
    {
        auto value = handle.attr("label").cast<StringView>();
        obj.label = value;
    }
}

inline void fill(pywgpu::SurfaceSourceAndroidNativeWindow& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_window = handle.attr("window");
    if (!py_window.is_none())
    {
        auto value = handle.attr("window").cast<void *>();
        obj.window = value;
    }
}

inline void fill(pywgpu::EmscriptenSurfaceSourceCanvasHTMLSelector& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_selector = handle.attr("selector");
    if (!py_selector.is_none())
    {
        auto value = handle.attr("selector").cast<StringView>();
        obj.selector = value;
    }
}

inline void fill(pywgpu::SurfaceSourceMetalLayer& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_layer = handle.attr("layer");
    if (!py_layer.is_none())
    {
        auto value = handle.attr("layer").cast<void *>();
        obj.layer = value;
    }
}

inline void fill(pywgpu::SurfaceSourceWindowsHWND& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_hinstance = handle.attr("hinstance");
    if (!py_hinstance.is_none())
    {
        auto value = handle.attr("hinstance").cast<void *>();
        obj.hinstance = value;
    }
    auto py_hwnd = handle.attr("hwnd");
    if (!py_hwnd.is_none())
    {
        auto value = handle.attr("hwnd").cast<void *>();
        obj.hwnd = value;
    }
}

inline void fill(pywgpu::SurfaceSourceXCBWindow& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_connection = handle.attr("connection");
    if (!py_connection.is_none())
    {
        auto value = handle.attr("connection").cast<void *>();
        obj.connection = value;
    }
    auto py_window = handle.attr("window");
    if (!py_window.is_none())
    {
        auto value = handle.attr("window").cast<uint32_t>();
        obj.window = value;
    }
}

inline void fill(pywgpu::SurfaceSourceXlibWindow& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_display = handle.attr("display");
    if (!py_display.is_none())
    {
        auto value = handle.attr("display").cast<void *>();
        obj.display = value;
    }
    auto py_window = handle.attr("window");
    if (!py_window.is_none())
    {
        auto value = handle.attr("window").cast<uint64_t>();
        obj.window = value;
    }
}

inline void fill(pywgpu::SurfaceSourceWaylandSurface& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_display = handle.attr("display");
    if (!py_display.is_none())
    {
        auto value = handle.attr("display").cast<void *>();
        obj.display = value;
    }
    auto py_surface = handle.attr("surface");
    if (!py_surface.is_none())
    {
        auto value = handle.attr("surface").cast<void *>();
        obj.surface = value;
    }
}

inline void fill(pywgpu::SurfaceDescriptorFromWindowsCoreWindow& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_core_window = handle.attr("core_window");
    if (!py_core_window.is_none())
    {
        auto value = handle.attr("core_window").cast<void *>();
        obj.coreWindow = value;
    }
}

inline void fill(pywgpu::SurfaceDescriptorFromWindowsUWPSwapChainPanel& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_swap_chain_panel = handle.attr("swap_chain_panel");
    if (!py_swap_chain_panel.is_none())
    {
        auto value = handle.attr("swap_chain_panel").cast<void *>();
        obj.swapChainPanel = value;
    }
}

inline void fill(pywgpu::SurfaceDescriptorFromWindowsWinUISwapChainPanel& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_swap_chain_panel = handle.attr("swap_chain_panel");
    if (!py_swap_chain_panel.is_none())
    {
        auto value = handle.attr("swap_chain_panel").cast<void *>();
        obj.swapChainPanel = value;
    }
}

inline void fill(pywgpu::TextureDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_label = handle.attr("label");
    if (!py_label.is_none())
    {
        auto value = handle.attr("label").cast<StringView>();
        obj.label = value;
    }
    auto py_usage = handle.attr("usage");
    if (!py_usage.is_none())
    {
        auto value = handle.attr("usage").cast<TextureUsage>();
        obj.usage = value;
    }
    auto py_dimension = handle.attr("dimension");
    if (!py_dimension.is_none())
    {
        auto value = handle.attr("dimension").cast<TextureDimension>();
        obj.dimension = value;
    }
    auto py_size = handle.attr("size");
    if (!py_size.is_none())
    {
        Builder<Extent3D>(ctx).fill(obj.size, handle.attr("size"));
    }
    auto py_format = handle.attr("format");
    if (!py_format.is_none())
    {
        auto value = handle.attr("format").cast<TextureFormat>();
        obj.format = value;
    }
    auto py_mip_level_count = handle.attr("mip_level_count");
    if (!py_mip_level_count.is_none())
    {
        auto value = handle.attr("mip_level_count").cast<uint32_t>();
        obj.mipLevelCount = value;
    }
    auto py_sample_count = handle.attr("sample_count");
    if (!py_sample_count.is_none())
    {
        auto value = handle.attr("sample_count").cast<uint32_t>();
        obj.sampleCount = value;
    }
    auto py_view_formats = handle.attr("view_formats");
    if (!py_view_formats.is_none())
    {
        auto py_list = handle.attr("view_formats").cast<py::sequence>();
        uint32_t count = static_cast<uint32_t>(py_list.size());
        auto* value = ctx.la.alloc_array<TextureFormat>(count);
        for (uint32_t i = 0; i < count; ++i) {
            value[i] = py_list[i].cast<TextureFormat>();
        }

        obj.viewFormats = value;
        obj.viewFormatCount = count;
    }
}

inline void fill(pywgpu::TextureBindingViewDimensionDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_texture_binding_view_dimension = handle.attr("texture_binding_view_dimension");
    if (!py_texture_binding_view_dimension.is_none())
    {
        auto value = handle.attr("texture_binding_view_dimension").cast<TextureViewDimension>();
        obj.textureBindingViewDimension = value;
    }
}

inline void fill(pywgpu::TextureViewDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_label = handle.attr("label");
    if (!py_label.is_none())
    {
        auto value = handle.attr("label").cast<StringView>();
        obj.label = value;
    }
    auto py_format = handle.attr("format");
    if (!py_format.is_none())
    {
        auto value = handle.attr("format").cast<TextureFormat>();
        obj.format = value;
    }
    auto py_dimension = handle.attr("dimension");
    if (!py_dimension.is_none())
    {
        auto value = handle.attr("dimension").cast<TextureViewDimension>();
        obj.dimension = value;
    }
    auto py_base_mip_level = handle.attr("base_mip_level");
    if (!py_base_mip_level.is_none())
    {
        auto value = handle.attr("base_mip_level").cast<uint32_t>();
        obj.baseMipLevel = value;
    }
    auto py_mip_level_count = handle.attr("mip_level_count");
    if (!py_mip_level_count.is_none())
    {
        auto value = handle.attr("mip_level_count").cast<uint32_t>();
        obj.mipLevelCount = value;
    }
    auto py_base_array_layer = handle.attr("base_array_layer");
    if (!py_base_array_layer.is_none())
    {
        auto value = handle.attr("base_array_layer").cast<uint32_t>();
        obj.baseArrayLayer = value;
    }
    auto py_array_layer_count = handle.attr("array_layer_count");
    if (!py_array_layer_count.is_none())
    {
        auto value = handle.attr("array_layer_count").cast<uint32_t>();
        obj.arrayLayerCount = value;
    }
    auto py_aspect = handle.attr("aspect");
    if (!py_aspect.is_none())
    {
        auto value = handle.attr("aspect").cast<TextureAspect>();
        obj.aspect = value;
    }
    auto py_usage = handle.attr("usage");
    if (!py_usage.is_none())
    {
        auto value = handle.attr("usage").cast<TextureUsage>();
        obj.usage = value;
    }
}

inline void fill(pywgpu::YCbCrVkDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_vk_format = handle.attr("vk_format");
    if (!py_vk_format.is_none())
    {
        auto value = handle.attr("vk_format").cast<uint32_t>();
        obj.vkFormat = value;
    }
    auto py_vk_y_cb_cr_model = handle.attr("vk_y_cb_cr_model");
    if (!py_vk_y_cb_cr_model.is_none())
    {
        auto value = handle.attr("vk_y_cb_cr_model").cast<uint32_t>();
        obj.vkYCbCrModel = value;
    }
    auto py_vk_y_cb_cr_range = handle.attr("vk_y_cb_cr_range");
    if (!py_vk_y_cb_cr_range.is_none())
    {
        auto value = handle.attr("vk_y_cb_cr_range").cast<uint32_t>();
        obj.vkYCbCrRange = value;
    }
    auto py_vk_component_swizzle_red = handle.attr("vk_component_swizzle_red");
    if (!py_vk_component_swizzle_red.is_none())
    {
        auto value = handle.attr("vk_component_swizzle_red").cast<uint32_t>();
        obj.vkComponentSwizzleRed = value;
    }
    auto py_vk_component_swizzle_green = handle.attr("vk_component_swizzle_green");
    if (!py_vk_component_swizzle_green.is_none())
    {
        auto value = handle.attr("vk_component_swizzle_green").cast<uint32_t>();
        obj.vkComponentSwizzleGreen = value;
    }
    auto py_vk_component_swizzle_blue = handle.attr("vk_component_swizzle_blue");
    if (!py_vk_component_swizzle_blue.is_none())
    {
        auto value = handle.attr("vk_component_swizzle_blue").cast<uint32_t>();
        obj.vkComponentSwizzleBlue = value;
    }
    auto py_vk_component_swizzle_alpha = handle.attr("vk_component_swizzle_alpha");
    if (!py_vk_component_swizzle_alpha.is_none())
    {
        auto value = handle.attr("vk_component_swizzle_alpha").cast<uint32_t>();
        obj.vkComponentSwizzleAlpha = value;
    }
    auto py_vk_x_chroma_offset = handle.attr("vk_x_chroma_offset");
    if (!py_vk_x_chroma_offset.is_none())
    {
        auto value = handle.attr("vk_x_chroma_offset").cast<uint32_t>();
        obj.vkXChromaOffset = value;
    }
    auto py_vk_y_chroma_offset = handle.attr("vk_y_chroma_offset");
    if (!py_vk_y_chroma_offset.is_none())
    {
        auto value = handle.attr("vk_y_chroma_offset").cast<uint32_t>();
        obj.vkYChromaOffset = value;
    }
    auto py_vk_chroma_filter = handle.attr("vk_chroma_filter");
    if (!py_vk_chroma_filter.is_none())
    {
        auto value = handle.attr("vk_chroma_filter").cast<FilterMode>();
        obj.vkChromaFilter = value;
    }
    auto py_force_explicit_reconstruction = handle.attr("force_explicit_reconstruction");
    if (!py_force_explicit_reconstruction.is_none())
    {
        auto value = handle.attr("force_explicit_reconstruction").cast<Bool>();
        obj.forceExplicitReconstruction = value;
    }
    auto py_external_format = handle.attr("external_format");
    if (!py_external_format.is_none())
    {
        auto value = handle.attr("external_format").cast<uint64_t>();
        obj.externalFormat = value;
    }
}

inline void fill(pywgpu::DawnTextureInternalUsageDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_internal_usage = handle.attr("internal_usage");
    if (!py_internal_usage.is_none())
    {
        auto value = handle.attr("internal_usage").cast<TextureUsage>();
        obj.internalUsage = value;
    }
}

inline void fill(pywgpu::DawnEncoderInternalUsageDescriptor& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_use_internal_usages = handle.attr("use_internal_usages");
    if (!py_use_internal_usages.is_none())
    {
        auto value = handle.attr("use_internal_usages").cast<Bool>();
        obj.useInternalUsages = value;
    }
}

inline void fill(pywgpu::MemoryHeapInfo& obj, py::handle handle, BuildCtx ctx) {
    auto py_properties = handle.attr("properties");
    if (!py_properties.is_none())
    {
        auto value = handle.attr("properties").cast<HeapProperty>();
        obj.properties = value;
    }
    auto py_size = handle.attr("size");
    if (!py_size.is_none())
    {
        auto value = handle.attr("size").cast<uint64_t>();
        obj.size = value;
    }
}

inline void fill(pywgpu::DawnBufferDescriptorErrorInfoFromWireClient& obj, py::handle handle, BuildCtx ctx) {
    auto py_next_in_chain = handle.attr("next_in_chain");
    if (!py_next_in_chain.is_none())
    {
        auto value = Builder<ChainedStruct>(ctx).build(handle.attr("next_in_chain"));
        obj.nextInChain = value;
    }
    auto py_out_of_memory = handle.attr("out_of_memory");
    if (!py_out_of_memory.is_none())
    {
        auto value = handle.attr("out_of_memory").cast<Bool>();
        obj.outOfMemory = value;
    }
}

inline void fill(pywgpu::SubgroupMatrixConfig& obj, py::handle handle, BuildCtx ctx) {
    auto py_component_type = handle.attr("component_type");
    if (!py_component_type.is_none())
    {
        auto value = handle.attr("component_type").cast<SubgroupMatrixComponentType>();
        obj.componentType = value;
    }
    auto py_result_component_type = handle.attr("result_component_type");
    if (!py_result_component_type.is_none())
    {
        auto value = handle.attr("result_component_type").cast<SubgroupMatrixComponentType>();
        obj.resultComponentType = value;
    }
    auto py_M = handle.attr("M");
    if (!py_M.is_none())
    {
        auto value = handle.attr("M").cast<uint32_t>();
        obj.M = value;
    }
    auto py_N = handle.attr("N");
    if (!py_N.is_none())
    {
        auto value = handle.attr("N").cast<uint32_t>();
        obj.N = value;
    }
    auto py_K = handle.attr("K");
    if (!py_K.is_none())
    {
        auto value = handle.attr("K").cast<uint32_t>();
        obj.K = value;
    }
}



void init_wgpu_py_auto(py::module &m, Registry &registry) {
py::enum_<RequestAdapterStatus>(m, "RequestAdapterStatus", py::arithmetic())
    .value("SUCCESS", RequestAdapterStatus::Success)
    .value("CALLBACK_CANCELLED", RequestAdapterStatus::CallbackCancelled)
    .value("UNAVAILABLE", RequestAdapterStatus::Unavailable)
    .value("ERROR", RequestAdapterStatus::Error)
;

py::enum_<AdapterType>(m, "AdapterType", py::arithmetic())
    .value("DISCRETE_GPU", AdapterType::DiscreteGPU)
    .value("INTEGRATED_GPU", AdapterType::IntegratedGPU)
    .value("CPU", AdapterType::CPU)
    .value("UNKNOWN", AdapterType::Unknown)
;

py::enum_<AddressMode>(m, "AddressMode", py::arithmetic())
    .value("UNDEFINED", AddressMode::Undefined)
    .value("CLAMP_TO_EDGE", AddressMode::ClampToEdge)
    .value("REPEAT", AddressMode::Repeat)
    .value("MIRROR_REPEAT", AddressMode::MirrorRepeat)
;

py::enum_<BackendType>(m, "BackendType", py::arithmetic())
    .value("UNDEFINED", BackendType::Undefined)
    .value("NULL", BackendType::Null)
    .value("WEB_GPU", BackendType::WebGPU)
    .value("D3D11", BackendType::D3D11)
    .value("D3D12", BackendType::D3D12)
    .value("METAL", BackendType::Metal)
    .value("VULKAN", BackendType::Vulkan)
    .value("OPEN_GL", BackendType::OpenGL)
    .value("OPEN_GLES", BackendType::OpenGLES)
;

py::enum_<BufferBindingType>(m, "BufferBindingType", py::arithmetic())
    .value("BINDING_NOT_USED", BufferBindingType::BindingNotUsed)
    .value("UNDEFINED", BufferBindingType::Undefined)
    .value("UNIFORM", BufferBindingType::Uniform)
    .value("STORAGE", BufferBindingType::Storage)
    .value("READ_ONLY_STORAGE", BufferBindingType::ReadOnlyStorage)
;

py::enum_<SamplerBindingType>(m, "SamplerBindingType", py::arithmetic())
    .value("BINDING_NOT_USED", SamplerBindingType::BindingNotUsed)
    .value("UNDEFINED", SamplerBindingType::Undefined)
    .value("FILTERING", SamplerBindingType::Filtering)
    .value("NON_FILTERING", SamplerBindingType::NonFiltering)
    .value("COMPARISON", SamplerBindingType::Comparison)
;

py::enum_<TextureSampleType>(m, "TextureSampleType", py::arithmetic())
    .value("BINDING_NOT_USED", TextureSampleType::BindingNotUsed)
    .value("UNDEFINED", TextureSampleType::Undefined)
    .value("FLOAT", TextureSampleType::Float)
    .value("UNFILTERABLE_FLOAT", TextureSampleType::UnfilterableFloat)
    .value("DEPTH", TextureSampleType::Depth)
    .value("SINT", TextureSampleType::Sint)
    .value("UINT", TextureSampleType::Uint)
;

py::enum_<StorageTextureAccess>(m, "StorageTextureAccess", py::arithmetic())
    .value("BINDING_NOT_USED", StorageTextureAccess::BindingNotUsed)
    .value("UNDEFINED", StorageTextureAccess::Undefined)
    .value("WRITE_ONLY", StorageTextureAccess::WriteOnly)
    .value("READ_ONLY", StorageTextureAccess::ReadOnly)
    .value("READ_WRITE", StorageTextureAccess::ReadWrite)
;

py::enum_<BlendFactor>(m, "BlendFactor", py::arithmetic())
    .value("UNDEFINED", BlendFactor::Undefined)
    .value("ZERO", BlendFactor::Zero)
    .value("ONE", BlendFactor::One)
    .value("SRC", BlendFactor::Src)
    .value("ONE_MINUS_SRC", BlendFactor::OneMinusSrc)
    .value("SRC_ALPHA", BlendFactor::SrcAlpha)
    .value("ONE_MINUS_SRC_ALPHA", BlendFactor::OneMinusSrcAlpha)
    .value("DST", BlendFactor::Dst)
    .value("ONE_MINUS_DST", BlendFactor::OneMinusDst)
    .value("DST_ALPHA", BlendFactor::DstAlpha)
    .value("ONE_MINUS_DST_ALPHA", BlendFactor::OneMinusDstAlpha)
    .value("SRC_ALPHA_SATURATED", BlendFactor::SrcAlphaSaturated)
    .value("CONSTANT", BlendFactor::Constant)
    .value("ONE_MINUS_CONSTANT", BlendFactor::OneMinusConstant)
    .value("SRC1", BlendFactor::Src1)
    .value("ONE_MINUS_SRC1", BlendFactor::OneMinusSrc1)
    .value("SRC1_ALPHA", BlendFactor::Src1Alpha)
    .value("ONE_MINUS_SRC1_ALPHA", BlendFactor::OneMinusSrc1Alpha)
;

py::enum_<BlendOperation>(m, "BlendOperation", py::arithmetic())
    .value("UNDEFINED", BlendOperation::Undefined)
    .value("ADD", BlendOperation::Add)
    .value("SUBTRACT", BlendOperation::Subtract)
    .value("REVERSE_SUBTRACT", BlendOperation::ReverseSubtract)
    .value("MIN", BlendOperation::Min)
    .value("MAX", BlendOperation::Max)
;

py::enum_<MapAsyncStatus>(m, "MapAsyncStatus", py::arithmetic())
    .value("SUCCESS", MapAsyncStatus::Success)
    .value("CALLBACK_CANCELLED", MapAsyncStatus::CallbackCancelled)
    .value("ERROR", MapAsyncStatus::Error)
    .value("ABORTED", MapAsyncStatus::Aborted)
;

py::enum_<BufferMapState>(m, "BufferMapState", py::arithmetic())
    .value("UNMAPPED", BufferMapState::Unmapped)
    .value("PENDING", BufferMapState::Pending)
    .value("MAPPED", BufferMapState::Mapped)
;

py::enum_<CompareFunction>(m, "CompareFunction", py::arithmetic())
    .value("UNDEFINED", CompareFunction::Undefined)
    .value("NEVER", CompareFunction::Never)
    .value("LESS", CompareFunction::Less)
    .value("EQUAL", CompareFunction::Equal)
    .value("LESS_EQUAL", CompareFunction::LessEqual)
    .value("GREATER", CompareFunction::Greater)
    .value("NOT_EQUAL", CompareFunction::NotEqual)
    .value("GREATER_EQUAL", CompareFunction::GreaterEqual)
    .value("ALWAYS", CompareFunction::Always)
;

py::enum_<CompilationInfoRequestStatus>(m, "CompilationInfoRequestStatus", py::arithmetic())
    .value("SUCCESS", CompilationInfoRequestStatus::Success)
    .value("CALLBACK_CANCELLED", CompilationInfoRequestStatus::CallbackCancelled)
;

py::enum_<CompilationMessageType>(m, "CompilationMessageType", py::arithmetic())
    .value("ERROR", CompilationMessageType::Error)
    .value("WARNING", CompilationMessageType::Warning)
    .value("INFO", CompilationMessageType::Info)
;

py::enum_<CompositeAlphaMode>(m, "CompositeAlphaMode", py::arithmetic())
    .value("AUTO", CompositeAlphaMode::Auto)
    .value("OPAQUE", CompositeAlphaMode::Opaque)
    .value("PREMULTIPLIED", CompositeAlphaMode::Premultiplied)
    .value("UNPREMULTIPLIED", CompositeAlphaMode::Unpremultiplied)
    .value("INHERIT", CompositeAlphaMode::Inherit)
;

py::enum_<AlphaMode>(m, "AlphaMode", py::arithmetic())
    .value("OPAQUE", AlphaMode::Opaque)
    .value("PREMULTIPLIED", AlphaMode::Premultiplied)
    .value("UNPREMULTIPLIED", AlphaMode::Unpremultiplied)
;

py::enum_<CreatePipelineAsyncStatus>(m, "CreatePipelineAsyncStatus", py::arithmetic())
    .value("SUCCESS", CreatePipelineAsyncStatus::Success)
    .value("CALLBACK_CANCELLED", CreatePipelineAsyncStatus::CallbackCancelled)
    .value("VALIDATION_ERROR", CreatePipelineAsyncStatus::ValidationError)
    .value("INTERNAL_ERROR", CreatePipelineAsyncStatus::InternalError)
;

py::enum_<CullMode>(m, "CullMode", py::arithmetic())
    .value("UNDEFINED", CullMode::Undefined)
    .value("NONE", CullMode::None)
    .value("FRONT", CullMode::Front)
    .value("BACK", CullMode::Back)
;

py::enum_<DeviceLostReason>(m, "DeviceLostReason", py::arithmetic())
    .value("UNKNOWN", DeviceLostReason::Unknown)
    .value("DESTROYED", DeviceLostReason::Destroyed)
    .value("CALLBACK_CANCELLED", DeviceLostReason::CallbackCancelled)
    .value("FAILED_CREATION", DeviceLostReason::FailedCreation)
;

py::enum_<PopErrorScopeStatus>(m, "PopErrorScopeStatus", py::arithmetic())
    .value("SUCCESS", PopErrorScopeStatus::Success)
    .value("CALLBACK_CANCELLED", PopErrorScopeStatus::CallbackCancelled)
    .value("ERROR", PopErrorScopeStatus::Error)
;

py::enum_<ErrorFilter>(m, "ErrorFilter", py::arithmetic())
    .value("VALIDATION", ErrorFilter::Validation)
    .value("OUT_OF_MEMORY", ErrorFilter::OutOfMemory)
    .value("INTERNAL", ErrorFilter::Internal)
;

py::enum_<ErrorType>(m, "ErrorType", py::arithmetic())
    .value("NO_ERROR", ErrorType::NoError)
    .value("VALIDATION", ErrorType::Validation)
    .value("OUT_OF_MEMORY", ErrorType::OutOfMemory)
    .value("INTERNAL", ErrorType::Internal)
    .value("UNKNOWN", ErrorType::Unknown)
;

py::enum_<LoggingType>(m, "LoggingType", py::arithmetic())
    .value("VERBOSE", LoggingType::Verbose)
    .value("INFO", LoggingType::Info)
    .value("WARNING", LoggingType::Warning)
    .value("ERROR", LoggingType::Error)
;

py::enum_<ExternalTextureRotation>(m, "ExternalTextureRotation", py::arithmetic())
    .value("ROTATE0_DEGREES", ExternalTextureRotation::Rotate0Degrees)
    .value("ROTATE90_DEGREES", ExternalTextureRotation::Rotate90Degrees)
    .value("ROTATE180_DEGREES", ExternalTextureRotation::Rotate180Degrees)
    .value("ROTATE270_DEGREES", ExternalTextureRotation::Rotate270Degrees)
;

py::enum_<Status>(m, "Status", py::arithmetic())
    .value("SUCCESS", Status::Success)
    .value("ERROR", Status::Error)
;

py::enum_<SharedFenceType>(m, "SharedFenceType", py::arithmetic())
    .value("VK_SEMAPHORE_OPAQUE_FD", SharedFenceType::VkSemaphoreOpaqueFD)
    .value("SYNC_FD", SharedFenceType::SyncFD)
    .value("VK_SEMAPHORE_ZIRCON_HANDLE", SharedFenceType::VkSemaphoreZirconHandle)
    .value("DXGI_SHARED_HANDLE", SharedFenceType::DXGISharedHandle)
    .value("MTL_SHARED_EVENT", SharedFenceType::MTLSharedEvent)
    .value("EGL_SYNC", SharedFenceType::EGLSync)
;

py::enum_<FeatureLevel>(m, "FeatureLevel", py::arithmetic())
    .value("UNDEFINED", FeatureLevel::Undefined)
    .value("COMPATIBILITY", FeatureLevel::Compatibility)
    .value("CORE", FeatureLevel::Core)
;

py::enum_<FeatureName>(m, "FeatureName", py::arithmetic())
    .value("DEPTH_CLIP_CONTROL", FeatureName::DepthClipControl)
    .value("DEPTH32_FLOAT_STENCIL8", FeatureName::Depth32FloatStencil8)
    .value("TIMESTAMP_QUERY", FeatureName::TimestampQuery)
    .value("TEXTURE_COMPRESSION_BC", FeatureName::TextureCompressionBC)
    .value("TEXTURE_COMPRESSION_BC_SLICED3D", FeatureName::TextureCompressionBCSliced3D)
    .value("TEXTURE_COMPRESSION_ETC2", FeatureName::TextureCompressionETC2)
    .value("TEXTURE_COMPRESSION_ASTC", FeatureName::TextureCompressionASTC)
    .value("TEXTURE_COMPRESSION_ASTC_SLICED3D", FeatureName::TextureCompressionASTCSliced3D)
    .value("INDIRECT_FIRST_INSTANCE", FeatureName::IndirectFirstInstance)
    .value("SHADER_F16", FeatureName::ShaderF16)
    .value("RG11B10_UFLOAT_RENDERABLE", FeatureName::RG11B10UfloatRenderable)
    .value("BGRA8_UNORM_STORAGE", FeatureName::BGRA8UnormStorage)
    .value("FLOAT32_FILTERABLE", FeatureName::Float32Filterable)
    .value("FLOAT32_BLENDABLE", FeatureName::Float32Blendable)
    .value("CLIP_DISTANCES", FeatureName::ClipDistances)
    .value("DUAL_SOURCE_BLENDING", FeatureName::DualSourceBlending)
    .value("SUBGROUPS", FeatureName::Subgroups)
    .value("CORE_FEATURES_AND_LIMITS", FeatureName::CoreFeaturesAndLimits)
    .value("DAWN_INTERNAL_USAGES", FeatureName::DawnInternalUsages)
    .value("DAWN_MULTI_PLANAR_FORMATS", FeatureName::DawnMultiPlanarFormats)
    .value("DAWN_NATIVE", FeatureName::DawnNative)
    .value("CHROMIUM_EXPERIMENTAL_TIMESTAMP_QUERY_INSIDE_PASSES", FeatureName::ChromiumExperimentalTimestampQueryInsidePasses)
    .value("IMPLICIT_DEVICE_SYNCHRONIZATION", FeatureName::ImplicitDeviceSynchronization)
    .value("CHROMIUM_EXPERIMENTAL_IMMEDIATE_DATA", FeatureName::ChromiumExperimentalImmediateData)
    .value("TRANSIENT_ATTACHMENTS", FeatureName::TransientAttachments)
    .value("MSAA_RENDER_TO_SINGLE_SAMPLED", FeatureName::MSAARenderToSingleSampled)
    .value("SUBGROUPS_F16", FeatureName::SubgroupsF16)
    .value("D3D11_MULTITHREAD_PROTECTED", FeatureName::D3D11MultithreadProtected)
    .value("ANGLE_TEXTURE_SHARING", FeatureName::ANGLETextureSharing)
    .value("PIXEL_LOCAL_STORAGE_COHERENT", FeatureName::PixelLocalStorageCoherent)
    .value("PIXEL_LOCAL_STORAGE_NON_COHERENT", FeatureName::PixelLocalStorageNonCoherent)
    .value("UNORM16_TEXTURE_FORMATS", FeatureName::Unorm16TextureFormats)
    .value("SNORM16_TEXTURE_FORMATS", FeatureName::Snorm16TextureFormats)
    .value("MULTI_PLANAR_FORMAT_EXTENDED_USAGES", FeatureName::MultiPlanarFormatExtendedUsages)
    .value("MULTI_PLANAR_FORMAT_P010", FeatureName::MultiPlanarFormatP010)
    .value("HOST_MAPPED_POINTER", FeatureName::HostMappedPointer)
    .value("MULTI_PLANAR_RENDER_TARGETS", FeatureName::MultiPlanarRenderTargets)
    .value("MULTI_PLANAR_FORMAT_NV12A", FeatureName::MultiPlanarFormatNv12a)
    .value("FRAMEBUFFER_FETCH", FeatureName::FramebufferFetch)
    .value("BUFFER_MAP_EXTENDED_USAGES", FeatureName::BufferMapExtendedUsages)
    .value("ADAPTER_PROPERTIES_MEMORY_HEAPS", FeatureName::AdapterPropertiesMemoryHeaps)
    .value("ADAPTER_PROPERTIES_D3D", FeatureName::AdapterPropertiesD3D)
    .value("ADAPTER_PROPERTIES_VK", FeatureName::AdapterPropertiesVk)
    .value("R8_UNORM_STORAGE", FeatureName::R8UnormStorage)
    .value("DAWN_FORMAT_CAPABILITIES", FeatureName::DawnFormatCapabilities)
    .value("DAWN_DRM_FORMAT_CAPABILITIES", FeatureName::DawnDrmFormatCapabilities)
    .value("NORM16_TEXTURE_FORMATS", FeatureName::Norm16TextureFormats)
    .value("MULTI_PLANAR_FORMAT_NV16", FeatureName::MultiPlanarFormatNv16)
    .value("MULTI_PLANAR_FORMAT_NV24", FeatureName::MultiPlanarFormatNv24)
    .value("MULTI_PLANAR_FORMAT_P210", FeatureName::MultiPlanarFormatP210)
    .value("MULTI_PLANAR_FORMAT_P410", FeatureName::MultiPlanarFormatP410)
    .value("SHARED_TEXTURE_MEMORY_VK_DEDICATED_ALLOCATION", FeatureName::SharedTextureMemoryVkDedicatedAllocation)
    .value("SHARED_TEXTURE_MEMORY_A_HARDWARE_BUFFER", FeatureName::SharedTextureMemoryAHardwareBuffer)
    .value("SHARED_TEXTURE_MEMORY_DMA_BUF", FeatureName::SharedTextureMemoryDmaBuf)
    .value("SHARED_TEXTURE_MEMORY_OPAQUE_FD", FeatureName::SharedTextureMemoryOpaqueFD)
    .value("SHARED_TEXTURE_MEMORY_ZIRCON_HANDLE", FeatureName::SharedTextureMemoryZirconHandle)
    .value("SHARED_TEXTURE_MEMORY_DXGI_SHARED_HANDLE", FeatureName::SharedTextureMemoryDXGISharedHandle)
    .value("SHARED_TEXTURE_MEMORY_D3D11_TEXTURE2D", FeatureName::SharedTextureMemoryD3D11Texture2D)
    .value("SHARED_TEXTURE_MEMORY_IO_SURFACE", FeatureName::SharedTextureMemoryIOSurface)
    .value("SHARED_TEXTURE_MEMORY_EGL_IMAGE", FeatureName::SharedTextureMemoryEGLImage)
    .value("SHARED_FENCE_VK_SEMAPHORE_OPAQUE_FD", FeatureName::SharedFenceVkSemaphoreOpaqueFD)
    .value("SHARED_FENCE_SYNC_FD", FeatureName::SharedFenceSyncFD)
    .value("SHARED_FENCE_VK_SEMAPHORE_ZIRCON_HANDLE", FeatureName::SharedFenceVkSemaphoreZirconHandle)
    .value("SHARED_FENCE_DXGI_SHARED_HANDLE", FeatureName::SharedFenceDXGISharedHandle)
    .value("SHARED_FENCE_MTL_SHARED_EVENT", FeatureName::SharedFenceMTLSharedEvent)
    .value("SHARED_BUFFER_MEMORY_D3D12_RESOURCE", FeatureName::SharedBufferMemoryD3D12Resource)
    .value("STATIC_SAMPLERS", FeatureName::StaticSamplers)
    .value("Y_CB_CR_VULKAN_SAMPLERS", FeatureName::YCbCrVulkanSamplers)
    .value("SHADER_MODULE_COMPILATION_OPTIONS", FeatureName::ShaderModuleCompilationOptions)
    .value("DAWN_LOAD_RESOLVE_TEXTURE", FeatureName::DawnLoadResolveTexture)
    .value("DAWN_PARTIAL_LOAD_RESOLVE_TEXTURE", FeatureName::DawnPartialLoadResolveTexture)
    .value("MULTI_DRAW_INDIRECT", FeatureName::MultiDrawIndirect)
    .value("DAWN_TEXEL_COPY_BUFFER_ROW_ALIGNMENT", FeatureName::DawnTexelCopyBufferRowAlignment)
    .value("FLEXIBLE_TEXTURE_VIEWS", FeatureName::FlexibleTextureViews)
    .value("CHROMIUM_EXPERIMENTAL_SUBGROUP_MATRIX", FeatureName::ChromiumExperimentalSubgroupMatrix)
    .value("SHARED_FENCE_EGL_SYNC", FeatureName::SharedFenceEGLSync)
;

py::enum_<FilterMode>(m, "FilterMode", py::arithmetic())
    .value("UNDEFINED", FilterMode::Undefined)
    .value("NEAREST", FilterMode::Nearest)
    .value("LINEAR", FilterMode::Linear)
;

py::enum_<FrontFace>(m, "FrontFace", py::arithmetic())
    .value("UNDEFINED", FrontFace::Undefined)
    .value("CCW", FrontFace::CCW)
    .value("CW", FrontFace::CW)
;

py::enum_<IndexFormat>(m, "IndexFormat", py::arithmetic())
    .value("UNDEFINED", IndexFormat::Undefined)
    .value("UINT16", IndexFormat::Uint16)
    .value("UINT32", IndexFormat::Uint32)
;

py::enum_<CallbackMode>(m, "CallbackMode", py::arithmetic())
    .value("WAIT_ANY_ONLY", CallbackMode::WaitAnyOnly)
    .value("ALLOW_PROCESS_EVENTS", CallbackMode::AllowProcessEvents)
    .value("ALLOW_SPONTANEOUS", CallbackMode::AllowSpontaneous)
;

py::enum_<WaitStatus>(m, "WaitStatus", py::arithmetic())
    .value("SUCCESS", WaitStatus::Success)
    .value("TIMED_OUT", WaitStatus::TimedOut)
    .value("ERROR", WaitStatus::Error)
;

py::enum_<VertexStepMode>(m, "VertexStepMode", py::arithmetic())
    .value("UNDEFINED", VertexStepMode::Undefined)
    .value("VERTEX", VertexStepMode::Vertex)
    .value("INSTANCE", VertexStepMode::Instance)
;

py::enum_<LoadOp>(m, "LoadOp", py::arithmetic())
    .value("UNDEFINED", LoadOp::Undefined)
    .value("LOAD", LoadOp::Load)
    .value("CLEAR", LoadOp::Clear)
    .value("EXPAND_RESOLVE_TEXTURE", LoadOp::ExpandResolveTexture)
;

py::enum_<MipmapFilterMode>(m, "MipmapFilterMode", py::arithmetic())
    .value("UNDEFINED", MipmapFilterMode::Undefined)
    .value("NEAREST", MipmapFilterMode::Nearest)
    .value("LINEAR", MipmapFilterMode::Linear)
;

py::enum_<StoreOp>(m, "StoreOp", py::arithmetic())
    .value("UNDEFINED", StoreOp::Undefined)
    .value("STORE", StoreOp::Store)
    .value("DISCARD", StoreOp::Discard)
;

py::enum_<PowerPreference>(m, "PowerPreference", py::arithmetic())
    .value("UNDEFINED", PowerPreference::Undefined)
    .value("LOW_POWER", PowerPreference::LowPower)
    .value("HIGH_PERFORMANCE", PowerPreference::HighPerformance)
;

py::enum_<PresentMode>(m, "PresentMode", py::arithmetic())
    .value("UNDEFINED", PresentMode::Undefined)
    .value("FIFO", PresentMode::Fifo)
    .value("FIFO_RELAXED", PresentMode::FifoRelaxed)
    .value("IMMEDIATE", PresentMode::Immediate)
    .value("MAILBOX", PresentMode::Mailbox)
;

py::enum_<PrimitiveTopology>(m, "PrimitiveTopology", py::arithmetic())
    .value("UNDEFINED", PrimitiveTopology::Undefined)
    .value("POINT_LIST", PrimitiveTopology::PointList)
    .value("LINE_LIST", PrimitiveTopology::LineList)
    .value("LINE_STRIP", PrimitiveTopology::LineStrip)
    .value("TRIANGLE_LIST", PrimitiveTopology::TriangleList)
    .value("TRIANGLE_STRIP", PrimitiveTopology::TriangleStrip)
;

py::enum_<QueryType>(m, "QueryType", py::arithmetic())
    .value("OCCLUSION", QueryType::Occlusion)
    .value("TIMESTAMP", QueryType::Timestamp)
;

py::enum_<QueueWorkDoneStatus>(m, "QueueWorkDoneStatus", py::arithmetic())
    .value("SUCCESS", QueueWorkDoneStatus::Success)
    .value("CALLBACK_CANCELLED", QueueWorkDoneStatus::CallbackCancelled)
    .value("ERROR", QueueWorkDoneStatus::Error)
;

py::enum_<RequestDeviceStatus>(m, "RequestDeviceStatus", py::arithmetic())
    .value("SUCCESS", RequestDeviceStatus::Success)
    .value("CALLBACK_CANCELLED", RequestDeviceStatus::CallbackCancelled)
    .value("ERROR", RequestDeviceStatus::Error)
;

py::enum_<StencilOperation>(m, "StencilOperation", py::arithmetic())
    .value("UNDEFINED", StencilOperation::Undefined)
    .value("KEEP", StencilOperation::Keep)
    .value("ZERO", StencilOperation::Zero)
    .value("REPLACE", StencilOperation::Replace)
    .value("INVERT", StencilOperation::Invert)
    .value("INCREMENT_CLAMP", StencilOperation::IncrementClamp)
    .value("DECREMENT_CLAMP", StencilOperation::DecrementClamp)
    .value("INCREMENT_WRAP", StencilOperation::IncrementWrap)
    .value("DECREMENT_WRAP", StencilOperation::DecrementWrap)
;

py::enum_<SType>(m, "SType", py::arithmetic())
    .value("SHADER_SOURCE_SPIRV", SType::ShaderSourceSPIRV)
    .value("SHADER_SOURCE_WGSL", SType::ShaderSourceWGSL)
    .value("RENDER_PASS_MAX_DRAW_COUNT", SType::RenderPassMaxDrawCount)
    .value("SURFACE_SOURCE_METAL_LAYER", SType::SurfaceSourceMetalLayer)
    .value("SURFACE_SOURCE_WINDOWS_HWND", SType::SurfaceSourceWindowsHWND)
    .value("SURFACE_SOURCE_XLIB_WINDOW", SType::SurfaceSourceXlibWindow)
    .value("SURFACE_SOURCE_WAYLAND_SURFACE", SType::SurfaceSourceWaylandSurface)
    .value("SURFACE_SOURCE_ANDROID_NATIVE_WINDOW", SType::SurfaceSourceAndroidNativeWindow)
    .value("SURFACE_SOURCE_XCB_WINDOW", SType::SurfaceSourceXCBWindow)
    .value("SURFACE_COLOR_MANAGEMENT", SType::SurfaceColorManagement)
    .value("REQUEST_ADAPTER_WEB_XR_OPTIONS", SType::RequestAdapterWebXROptions)
    .value("ADAPTER_PROPERTIES_SUBGROUPS", SType::AdapterPropertiesSubgroups)
    .value("TEXTURE_BINDING_VIEW_DIMENSION_DESCRIPTOR", SType::TextureBindingViewDimensionDescriptor)
    .value("EMSCRIPTEN_SURFACE_SOURCE_CANVAS_HTML_SELECTOR", SType::EmscriptenSurfaceSourceCanvasHTMLSelector)
    .value("SURFACE_DESCRIPTOR_FROM_WINDOWS_CORE_WINDOW", SType::SurfaceDescriptorFromWindowsCoreWindow)
    .value("EXTERNAL_TEXTURE_BINDING_ENTRY", SType::ExternalTextureBindingEntry)
    .value("EXTERNAL_TEXTURE_BINDING_LAYOUT", SType::ExternalTextureBindingLayout)
    .value("SURFACE_DESCRIPTOR_FROM_WINDOWS_UWP_SWAP_CHAIN_PANEL", SType::SurfaceDescriptorFromWindowsUWPSwapChainPanel)
    .value("DAWN_TEXTURE_INTERNAL_USAGE_DESCRIPTOR", SType::DawnTextureInternalUsageDescriptor)
    .value("DAWN_ENCODER_INTERNAL_USAGE_DESCRIPTOR", SType::DawnEncoderInternalUsageDescriptor)
    .value("DAWN_INSTANCE_DESCRIPTOR", SType::DawnInstanceDescriptor)
    .value("DAWN_CACHE_DEVICE_DESCRIPTOR", SType::DawnCacheDeviceDescriptor)
    .value("DAWN_ADAPTER_PROPERTIES_POWER_PREFERENCE", SType::DawnAdapterPropertiesPowerPreference)
    .value("DAWN_BUFFER_DESCRIPTOR_ERROR_INFO_FROM_WIRE_CLIENT", SType::DawnBufferDescriptorErrorInfoFromWireClient)
    .value("DAWN_TOGGLES_DESCRIPTOR", SType::DawnTogglesDescriptor)
    .value("DAWN_SHADER_MODULE_SPIRV_OPTIONS_DESCRIPTOR", SType::DawnShaderModuleSPIRVOptionsDescriptor)
    .value("REQUEST_ADAPTER_OPTIONS_LUID", SType::RequestAdapterOptionsLUID)
    .value("REQUEST_ADAPTER_OPTIONS_GET_GL_PROC", SType::RequestAdapterOptionsGetGLProc)
    .value("REQUEST_ADAPTER_OPTIONS_D3D11_DEVICE", SType::RequestAdapterOptionsD3D11Device)
    .value("DAWN_RENDER_PASS_COLOR_ATTACHMENT_RENDER_TO_SINGLE_SAMPLED", SType::DawnRenderPassColorAttachmentRenderToSingleSampled)
    .value("RENDER_PASS_PIXEL_LOCAL_STORAGE", SType::RenderPassPixelLocalStorage)
    .value("PIPELINE_LAYOUT_PIXEL_LOCAL_STORAGE", SType::PipelineLayoutPixelLocalStorage)
    .value("BUFFER_HOST_MAPPED_POINTER", SType::BufferHostMappedPointer)
    .value("ADAPTER_PROPERTIES_MEMORY_HEAPS", SType::AdapterPropertiesMemoryHeaps)
    .value("ADAPTER_PROPERTIES_D3D", SType::AdapterPropertiesD3D)
    .value("ADAPTER_PROPERTIES_VK", SType::AdapterPropertiesVk)
    .value("DAWN_WIRE_WGSL_CONTROL", SType::DawnWireWGSLControl)
    .value("DAWN_WGSL_BLOCKLIST", SType::DawnWGSLBlocklist)
    .value("DAWN_DRM_FORMAT_CAPABILITIES", SType::DawnDrmFormatCapabilities)
    .value("SHADER_MODULE_COMPILATION_OPTIONS", SType::ShaderModuleCompilationOptions)
    .value("COLOR_TARGET_STATE_EXPAND_RESOLVE_TEXTURE_DAWN", SType::ColorTargetStateExpandResolveTextureDawn)
    .value("RENDER_PASS_DESCRIPTOR_EXPAND_RESOLVE_RECT", SType::RenderPassDescriptorExpandResolveRect)
    .value("SHARED_TEXTURE_MEMORY_VK_DEDICATED_ALLOCATION_DESCRIPTOR", SType::SharedTextureMemoryVkDedicatedAllocationDescriptor)
    .value("SHARED_TEXTURE_MEMORY_A_HARDWARE_BUFFER_DESCRIPTOR", SType::SharedTextureMemoryAHardwareBufferDescriptor)
    .value("SHARED_TEXTURE_MEMORY_DMA_BUF_DESCRIPTOR", SType::SharedTextureMemoryDmaBufDescriptor)
    .value("SHARED_TEXTURE_MEMORY_OPAQUE_FD_DESCRIPTOR", SType::SharedTextureMemoryOpaqueFDDescriptor)
    .value("SHARED_TEXTURE_MEMORY_ZIRCON_HANDLE_DESCRIPTOR", SType::SharedTextureMemoryZirconHandleDescriptor)
    .value("SHARED_TEXTURE_MEMORY_DXGI_SHARED_HANDLE_DESCRIPTOR", SType::SharedTextureMemoryDXGISharedHandleDescriptor)
    .value("SHARED_TEXTURE_MEMORY_D3D11_TEXTURE2D_DESCRIPTOR", SType::SharedTextureMemoryD3D11Texture2DDescriptor)
    .value("SHARED_TEXTURE_MEMORY_IO_SURFACE_DESCRIPTOR", SType::SharedTextureMemoryIOSurfaceDescriptor)
    .value("SHARED_TEXTURE_MEMORY_EGL_IMAGE_DESCRIPTOR", SType::SharedTextureMemoryEGLImageDescriptor)
    .value("SHARED_TEXTURE_MEMORY_INITIALIZED_BEGIN_STATE", SType::SharedTextureMemoryInitializedBeginState)
    .value("SHARED_TEXTURE_MEMORY_INITIALIZED_END_STATE", SType::SharedTextureMemoryInitializedEndState)
    .value("SHARED_TEXTURE_MEMORY_VK_IMAGE_LAYOUT_BEGIN_STATE", SType::SharedTextureMemoryVkImageLayoutBeginState)
    .value("SHARED_TEXTURE_MEMORY_VK_IMAGE_LAYOUT_END_STATE", SType::SharedTextureMemoryVkImageLayoutEndState)
    .value("SHARED_TEXTURE_MEMORY_D3D_SWAPCHAIN_BEGIN_STATE", SType::SharedTextureMemoryD3DSwapchainBeginState)
    .value("SHARED_FENCE_VK_SEMAPHORE_OPAQUE_FD_DESCRIPTOR", SType::SharedFenceVkSemaphoreOpaqueFDDescriptor)
    .value("SHARED_FENCE_VK_SEMAPHORE_OPAQUE_FD_EXPORT_INFO", SType::SharedFenceVkSemaphoreOpaqueFDExportInfo)
    .value("SHARED_FENCE_SYNC_FD_DESCRIPTOR", SType::SharedFenceSyncFDDescriptor)
    .value("SHARED_FENCE_SYNC_FD_EXPORT_INFO", SType::SharedFenceSyncFDExportInfo)
    .value("SHARED_FENCE_VK_SEMAPHORE_ZIRCON_HANDLE_DESCRIPTOR", SType::SharedFenceVkSemaphoreZirconHandleDescriptor)
    .value("SHARED_FENCE_VK_SEMAPHORE_ZIRCON_HANDLE_EXPORT_INFO", SType::SharedFenceVkSemaphoreZirconHandleExportInfo)
    .value("SHARED_FENCE_DXGI_SHARED_HANDLE_DESCRIPTOR", SType::SharedFenceDXGISharedHandleDescriptor)
    .value("SHARED_FENCE_DXGI_SHARED_HANDLE_EXPORT_INFO", SType::SharedFenceDXGISharedHandleExportInfo)
    .value("SHARED_FENCE_MTL_SHARED_EVENT_DESCRIPTOR", SType::SharedFenceMTLSharedEventDescriptor)
    .value("SHARED_FENCE_MTL_SHARED_EVENT_EXPORT_INFO", SType::SharedFenceMTLSharedEventExportInfo)
    .value("SHARED_BUFFER_MEMORY_D3D12_RESOURCE_DESCRIPTOR", SType::SharedBufferMemoryD3D12ResourceDescriptor)
    .value("STATIC_SAMPLER_BINDING_LAYOUT", SType::StaticSamplerBindingLayout)
    .value("Y_CB_CR_VK_DESCRIPTOR", SType::YCbCrVkDescriptor)
    .value("SHARED_TEXTURE_MEMORY_A_HARDWARE_BUFFER_PROPERTIES", SType::SharedTextureMemoryAHardwareBufferProperties)
    .value("A_HARDWARE_BUFFER_PROPERTIES", SType::AHardwareBufferProperties)
    .value("DAWN_EXPERIMENTAL_IMMEDIATE_DATA_LIMITS", SType::DawnExperimentalImmediateDataLimits)
    .value("DAWN_TEXEL_COPY_BUFFER_ROW_ALIGNMENT_LIMITS", SType::DawnTexelCopyBufferRowAlignmentLimits)
    .value("ADAPTER_PROPERTIES_SUBGROUP_MATRIX_CONFIGS", SType::AdapterPropertiesSubgroupMatrixConfigs)
    .value("SHARED_FENCE_EGL_SYNC_DESCRIPTOR", SType::SharedFenceEGLSyncDescriptor)
    .value("SHARED_FENCE_EGL_SYNC_EXPORT_INFO", SType::SharedFenceEGLSyncExportInfo)
    .value("DAWN_INJECTED_INVALID_S_TYPE", SType::DawnInjectedInvalidSType)
    .value("DAWN_COMPILATION_MESSAGE_UTF16", SType::DawnCompilationMessageUtf16)
    .value("DAWN_FAKE_BUFFER_OOM_FOR_TESTING", SType::DawnFakeBufferOOMForTesting)
    .value("SURFACE_DESCRIPTOR_FROM_WINDOWS_WIN_UI_SWAP_CHAIN_PANEL", SType::SurfaceDescriptorFromWindowsWinUISwapChainPanel)
;

py::enum_<SurfaceGetCurrentTextureStatus>(m, "SurfaceGetCurrentTextureStatus", py::arithmetic())
    .value("SUCCESS_OPTIMAL", SurfaceGetCurrentTextureStatus::SuccessOptimal)
    .value("SUCCESS_SUBOPTIMAL", SurfaceGetCurrentTextureStatus::SuccessSuboptimal)
    .value("TIMEOUT", SurfaceGetCurrentTextureStatus::Timeout)
    .value("OUTDATED", SurfaceGetCurrentTextureStatus::Outdated)
    .value("LOST", SurfaceGetCurrentTextureStatus::Lost)
    .value("ERROR", SurfaceGetCurrentTextureStatus::Error)
;

py::enum_<TextureAspect>(m, "TextureAspect", py::arithmetic())
    .value("UNDEFINED", TextureAspect::Undefined)
    .value("ALL", TextureAspect::All)
    .value("STENCIL_ONLY", TextureAspect::StencilOnly)
    .value("DEPTH_ONLY", TextureAspect::DepthOnly)
    .value("PLANE0_ONLY", TextureAspect::Plane0Only)
    .value("PLANE1_ONLY", TextureAspect::Plane1Only)
    .value("PLANE2_ONLY", TextureAspect::Plane2Only)
;

py::enum_<TextureDimension>(m, "TextureDimension", py::arithmetic())
    .value("UNDEFINED", TextureDimension::Undefined)
    .value("E1D", TextureDimension::e1D)
    .value("E2D", TextureDimension::e2D)
    .value("E3D", TextureDimension::e3D)
;

py::enum_<TextureFormat>(m, "TextureFormat", py::arithmetic())
    .value("UNDEFINED", TextureFormat::Undefined)
    .value("R8_UNORM", TextureFormat::R8Unorm)
    .value("R8_SNORM", TextureFormat::R8Snorm)
    .value("R8_UINT", TextureFormat::R8Uint)
    .value("R8_SINT", TextureFormat::R8Sint)
    .value("R16_UINT", TextureFormat::R16Uint)
    .value("R16_SINT", TextureFormat::R16Sint)
    .value("R16_FLOAT", TextureFormat::R16Float)
    .value("RG8_UNORM", TextureFormat::RG8Unorm)
    .value("RG8_SNORM", TextureFormat::RG8Snorm)
    .value("RG8_UINT", TextureFormat::RG8Uint)
    .value("RG8_SINT", TextureFormat::RG8Sint)
    .value("R32_FLOAT", TextureFormat::R32Float)
    .value("R32_UINT", TextureFormat::R32Uint)
    .value("R32_SINT", TextureFormat::R32Sint)
    .value("RG16_UINT", TextureFormat::RG16Uint)
    .value("RG16_SINT", TextureFormat::RG16Sint)
    .value("RG16_FLOAT", TextureFormat::RG16Float)
    .value("RGBA8_UNORM", TextureFormat::RGBA8Unorm)
    .value("RGBA8_UNORM_SRGB", TextureFormat::RGBA8UnormSrgb)
    .value("RGBA8_SNORM", TextureFormat::RGBA8Snorm)
    .value("RGBA8_UINT", TextureFormat::RGBA8Uint)
    .value("RGBA8_SINT", TextureFormat::RGBA8Sint)
    .value("BGRA8_UNORM", TextureFormat::BGRA8Unorm)
    .value("BGRA8_UNORM_SRGB", TextureFormat::BGRA8UnormSrgb)
    .value("RGB10A2_UINT", TextureFormat::RGB10A2Uint)
    .value("RGB10A2_UNORM", TextureFormat::RGB10A2Unorm)
    .value("RG11B10_UFLOAT", TextureFormat::RG11B10Ufloat)
    .value("RGB9E5_UFLOAT", TextureFormat::RGB9E5Ufloat)
    .value("RG32_FLOAT", TextureFormat::RG32Float)
    .value("RG32_UINT", TextureFormat::RG32Uint)
    .value("RG32_SINT", TextureFormat::RG32Sint)
    .value("RGBA16_UINT", TextureFormat::RGBA16Uint)
    .value("RGBA16_SINT", TextureFormat::RGBA16Sint)
    .value("RGBA16_FLOAT", TextureFormat::RGBA16Float)
    .value("RGBA32_FLOAT", TextureFormat::RGBA32Float)
    .value("RGBA32_UINT", TextureFormat::RGBA32Uint)
    .value("RGBA32_SINT", TextureFormat::RGBA32Sint)
    .value("STENCIL8", TextureFormat::Stencil8)
    .value("DEPTH16_UNORM", TextureFormat::Depth16Unorm)
    .value("DEPTH24_PLUS", TextureFormat::Depth24Plus)
    .value("DEPTH24_PLUS_STENCIL8", TextureFormat::Depth24PlusStencil8)
    .value("DEPTH32_FLOAT", TextureFormat::Depth32Float)
    .value("DEPTH32_FLOAT_STENCIL8", TextureFormat::Depth32FloatStencil8)
    .value("BC1RGBA_UNORM", TextureFormat::BC1RGBAUnorm)
    .value("BC1RGBA_UNORM_SRGB", TextureFormat::BC1RGBAUnormSrgb)
    .value("BC2RGBA_UNORM", TextureFormat::BC2RGBAUnorm)
    .value("BC2RGBA_UNORM_SRGB", TextureFormat::BC2RGBAUnormSrgb)
    .value("BC3RGBA_UNORM", TextureFormat::BC3RGBAUnorm)
    .value("BC3RGBA_UNORM_SRGB", TextureFormat::BC3RGBAUnormSrgb)
    .value("BC4R_UNORM", TextureFormat::BC4RUnorm)
    .value("BC4R_SNORM", TextureFormat::BC4RSnorm)
    .value("BC5RG_UNORM", TextureFormat::BC5RGUnorm)
    .value("BC5RG_SNORM", TextureFormat::BC5RGSnorm)
    .value("BC6HRGB_UFLOAT", TextureFormat::BC6HRGBUfloat)
    .value("BC6HRGB_FLOAT", TextureFormat::BC6HRGBFloat)
    .value("BC7RGBA_UNORM", TextureFormat::BC7RGBAUnorm)
    .value("BC7RGBA_UNORM_SRGB", TextureFormat::BC7RGBAUnormSrgb)
    .value("ETC2RGB8_UNORM", TextureFormat::ETC2RGB8Unorm)
    .value("ETC2RGB8_UNORM_SRGB", TextureFormat::ETC2RGB8UnormSrgb)
    .value("ETC2RGB8A1_UNORM", TextureFormat::ETC2RGB8A1Unorm)
    .value("ETC2RGB8A1_UNORM_SRGB", TextureFormat::ETC2RGB8A1UnormSrgb)
    .value("ETC2RGBA8_UNORM", TextureFormat::ETC2RGBA8Unorm)
    .value("ETC2RGBA8_UNORM_SRGB", TextureFormat::ETC2RGBA8UnormSrgb)
    .value("EACR11_UNORM", TextureFormat::EACR11Unorm)
    .value("EACR11_SNORM", TextureFormat::EACR11Snorm)
    .value("EACRG11_UNORM", TextureFormat::EACRG11Unorm)
    .value("EACRG11_SNORM", TextureFormat::EACRG11Snorm)
    .value("ASTC4X4_UNORM", TextureFormat::ASTC4x4Unorm)
    .value("ASTC4X4_UNORM_SRGB", TextureFormat::ASTC4x4UnormSrgb)
    .value("ASTC5X4_UNORM", TextureFormat::ASTC5x4Unorm)
    .value("ASTC5X4_UNORM_SRGB", TextureFormat::ASTC5x4UnormSrgb)
    .value("ASTC5X5_UNORM", TextureFormat::ASTC5x5Unorm)
    .value("ASTC5X5_UNORM_SRGB", TextureFormat::ASTC5x5UnormSrgb)
    .value("ASTC6X5_UNORM", TextureFormat::ASTC6x5Unorm)
    .value("ASTC6X5_UNORM_SRGB", TextureFormat::ASTC6x5UnormSrgb)
    .value("ASTC6X6_UNORM", TextureFormat::ASTC6x6Unorm)
    .value("ASTC6X6_UNORM_SRGB", TextureFormat::ASTC6x6UnormSrgb)
    .value("ASTC8X5_UNORM", TextureFormat::ASTC8x5Unorm)
    .value("ASTC8X5_UNORM_SRGB", TextureFormat::ASTC8x5UnormSrgb)
    .value("ASTC8X6_UNORM", TextureFormat::ASTC8x6Unorm)
    .value("ASTC8X6_UNORM_SRGB", TextureFormat::ASTC8x6UnormSrgb)
    .value("ASTC8X8_UNORM", TextureFormat::ASTC8x8Unorm)
    .value("ASTC8X8_UNORM_SRGB", TextureFormat::ASTC8x8UnormSrgb)
    .value("ASTC10X5_UNORM", TextureFormat::ASTC10x5Unorm)
    .value("ASTC10X5_UNORM_SRGB", TextureFormat::ASTC10x5UnormSrgb)
    .value("ASTC10X6_UNORM", TextureFormat::ASTC10x6Unorm)
    .value("ASTC10X6_UNORM_SRGB", TextureFormat::ASTC10x6UnormSrgb)
    .value("ASTC10X8_UNORM", TextureFormat::ASTC10x8Unorm)
    .value("ASTC10X8_UNORM_SRGB", TextureFormat::ASTC10x8UnormSrgb)
    .value("ASTC10X10_UNORM", TextureFormat::ASTC10x10Unorm)
    .value("ASTC10X10_UNORM_SRGB", TextureFormat::ASTC10x10UnormSrgb)
    .value("ASTC12X10_UNORM", TextureFormat::ASTC12x10Unorm)
    .value("ASTC12X10_UNORM_SRGB", TextureFormat::ASTC12x10UnormSrgb)
    .value("ASTC12X12_UNORM", TextureFormat::ASTC12x12Unorm)
    .value("ASTC12X12_UNORM_SRGB", TextureFormat::ASTC12x12UnormSrgb)
    .value("R16_UNORM", TextureFormat::R16Unorm)
    .value("RG16_UNORM", TextureFormat::RG16Unorm)
    .value("RGBA16_UNORM", TextureFormat::RGBA16Unorm)
    .value("R16_SNORM", TextureFormat::R16Snorm)
    .value("RG16_SNORM", TextureFormat::RG16Snorm)
    .value("RGBA16_SNORM", TextureFormat::RGBA16Snorm)
    .value("R8BG8_BIPLANAR420_UNORM", TextureFormat::R8BG8Biplanar420Unorm)
    .value("R10X6BG10X6_BIPLANAR420_UNORM", TextureFormat::R10X6BG10X6Biplanar420Unorm)
    .value("R8BG8A8_TRIPLANAR420_UNORM", TextureFormat::R8BG8A8Triplanar420Unorm)
    .value("R8BG8_BIPLANAR422_UNORM", TextureFormat::R8BG8Biplanar422Unorm)
    .value("R8BG8_BIPLANAR444_UNORM", TextureFormat::R8BG8Biplanar444Unorm)
    .value("R10X6BG10X6_BIPLANAR422_UNORM", TextureFormat::R10X6BG10X6Biplanar422Unorm)
    .value("R10X6BG10X6_BIPLANAR444_UNORM", TextureFormat::R10X6BG10X6Biplanar444Unorm)
    .value("EXTERNAL", TextureFormat::External)
;

py::enum_<TextureViewDimension>(m, "TextureViewDimension", py::arithmetic())
    .value("UNDEFINED", TextureViewDimension::Undefined)
    .value("E1D", TextureViewDimension::e1D)
    .value("E2D", TextureViewDimension::e2D)
    .value("E2D_ARRAY", TextureViewDimension::e2DArray)
    .value("CUBE", TextureViewDimension::Cube)
    .value("CUBE_ARRAY", TextureViewDimension::CubeArray)
    .value("E3D", TextureViewDimension::e3D)
;

py::enum_<VertexFormat>(m, "VertexFormat", py::arithmetic())
    .value("UINT8", VertexFormat::Uint8)
    .value("UINT8X2", VertexFormat::Uint8x2)
    .value("UINT8X4", VertexFormat::Uint8x4)
    .value("SINT8", VertexFormat::Sint8)
    .value("SINT8X2", VertexFormat::Sint8x2)
    .value("SINT8X4", VertexFormat::Sint8x4)
    .value("UNORM8", VertexFormat::Unorm8)
    .value("UNORM8X2", VertexFormat::Unorm8x2)
    .value("UNORM8X4", VertexFormat::Unorm8x4)
    .value("SNORM8", VertexFormat::Snorm8)
    .value("SNORM8X2", VertexFormat::Snorm8x2)
    .value("SNORM8X4", VertexFormat::Snorm8x4)
    .value("UINT16", VertexFormat::Uint16)
    .value("UINT16X2", VertexFormat::Uint16x2)
    .value("UINT16X4", VertexFormat::Uint16x4)
    .value("SINT16", VertexFormat::Sint16)
    .value("SINT16X2", VertexFormat::Sint16x2)
    .value("SINT16X4", VertexFormat::Sint16x4)
    .value("UNORM16", VertexFormat::Unorm16)
    .value("UNORM16X2", VertexFormat::Unorm16x2)
    .value("UNORM16X4", VertexFormat::Unorm16x4)
    .value("SNORM16", VertexFormat::Snorm16)
    .value("SNORM16X2", VertexFormat::Snorm16x2)
    .value("SNORM16X4", VertexFormat::Snorm16x4)
    .value("FLOAT16", VertexFormat::Float16)
    .value("FLOAT16X2", VertexFormat::Float16x2)
    .value("FLOAT16X4", VertexFormat::Float16x4)
    .value("FLOAT32", VertexFormat::Float32)
    .value("FLOAT32X2", VertexFormat::Float32x2)
    .value("FLOAT32X3", VertexFormat::Float32x3)
    .value("FLOAT32X4", VertexFormat::Float32x4)
    .value("UINT32", VertexFormat::Uint32)
    .value("UINT32X2", VertexFormat::Uint32x2)
    .value("UINT32X3", VertexFormat::Uint32x3)
    .value("UINT32X4", VertexFormat::Uint32x4)
    .value("SINT32", VertexFormat::Sint32)
    .value("SINT32X2", VertexFormat::Sint32x2)
    .value("SINT32X3", VertexFormat::Sint32x3)
    .value("SINT32X4", VertexFormat::Sint32x4)
    .value("UNORM10_10_10_2", VertexFormat::Unorm10_10_10_2)
    .value("UNORM8X4BGRA", VertexFormat::Unorm8x4BGRA)
;

py::enum_<WGSLLanguageFeatureName>(m, "WGSLLanguageFeatureName", py::arithmetic())
    .value("READONLY_AND_READWRITE_STORAGE_TEXTURES", WGSLLanguageFeatureName::ReadonlyAndReadwriteStorageTextures)
    .value("PACKED4X8_INTEGER_DOT_PRODUCT", WGSLLanguageFeatureName::Packed4x8IntegerDotProduct)
    .value("UNRESTRICTED_POINTER_PARAMETERS", WGSLLanguageFeatureName::UnrestrictedPointerParameters)
    .value("POINTER_COMPOSITE_ACCESS", WGSLLanguageFeatureName::PointerCompositeAccess)
    .value("SIZED_BINDING_ARRAY", WGSLLanguageFeatureName::SizedBindingArray)
    .value("CHROMIUM_TESTING_UNIMPLEMENTED", WGSLLanguageFeatureName::ChromiumTestingUnimplemented)
    .value("CHROMIUM_TESTING_UNSAFE_EXPERIMENTAL", WGSLLanguageFeatureName::ChromiumTestingUnsafeExperimental)
    .value("CHROMIUM_TESTING_EXPERIMENTAL", WGSLLanguageFeatureName::ChromiumTestingExperimental)
    .value("CHROMIUM_TESTING_SHIPPED_WITH_KILLSWITCH", WGSLLanguageFeatureName::ChromiumTestingShippedWithKillswitch)
    .value("CHROMIUM_TESTING_SHIPPED", WGSLLanguageFeatureName::ChromiumTestingShipped)
;

py::enum_<SubgroupMatrixComponentType>(m, "SubgroupMatrixComponentType", py::arithmetic())
    .value("F32", SubgroupMatrixComponentType::F32)
    .value("F16", SubgroupMatrixComponentType::F16)
    .value("U32", SubgroupMatrixComponentType::U32)
    .value("I32", SubgroupMatrixComponentType::I32)
;

py::enum_<BufferUsage>(m, "BufferUsage", py::arithmetic())
    .value("NONE", BufferUsage::None)
    .value("MAP_READ", BufferUsage::MapRead)
    .value("MAP_WRITE", BufferUsage::MapWrite)
    .value("COPY_SRC", BufferUsage::CopySrc)
    .value("COPY_DST", BufferUsage::CopyDst)
    .value("INDEX", BufferUsage::Index)
    .value("VERTEX", BufferUsage::Vertex)
    .value("UNIFORM", BufferUsage::Uniform)
    .value("STORAGE", BufferUsage::Storage)
    .value("INDIRECT", BufferUsage::Indirect)
    .value("QUERY_RESOLVE", BufferUsage::QueryResolve)
    
    .def("__or__", [](pywgpu::BufferUsage& a, pywgpu::BufferUsage& b) {
        return (pywgpu::BufferUsage)(a | b);
    }, py::is_operator());
    

py::enum_<ColorWriteMask>(m, "ColorWriteMask", py::arithmetic())
    .value("NONE", ColorWriteMask::None)
    .value("RED", ColorWriteMask::Red)
    .value("GREEN", ColorWriteMask::Green)
    .value("BLUE", ColorWriteMask::Blue)
    .value("ALPHA", ColorWriteMask::Alpha)
    .value("ALL", ColorWriteMask::All)
    
    .def("__or__", [](pywgpu::ColorWriteMask& a, pywgpu::ColorWriteMask& b) {
        return (pywgpu::ColorWriteMask)(a | b);
    }, py::is_operator());
    

py::enum_<MapMode>(m, "MapMode", py::arithmetic())
    .value("NONE", MapMode::None)
    .value("READ", MapMode::Read)
    .value("WRITE", MapMode::Write)
    
    .def("__or__", [](pywgpu::MapMode& a, pywgpu::MapMode& b) {
        return (pywgpu::MapMode)(a | b);
    }, py::is_operator());
    

py::enum_<ShaderStage>(m, "ShaderStage", py::arithmetic())
    .value("NONE", ShaderStage::None)
    .value("VERTEX", ShaderStage::Vertex)
    .value("FRAGMENT", ShaderStage::Fragment)
    .value("COMPUTE", ShaderStage::Compute)
    
    .def("__or__", [](pywgpu::ShaderStage& a, pywgpu::ShaderStage& b) {
        return (pywgpu::ShaderStage)(a | b);
    }, py::is_operator());
    

py::enum_<TextureUsage>(m, "TextureUsage", py::arithmetic())
    .value("NONE", TextureUsage::None)
    .value("COPY_SRC", TextureUsage::CopySrc)
    .value("COPY_DST", TextureUsage::CopyDst)
    .value("TEXTURE_BINDING", TextureUsage::TextureBinding)
    .value("STORAGE_BINDING", TextureUsage::StorageBinding)
    .value("RENDER_ATTACHMENT", TextureUsage::RenderAttachment)
    .value("TRANSIENT_ATTACHMENT", TextureUsage::TransientAttachment)
    .value("STORAGE_ATTACHMENT", TextureUsage::StorageAttachment)
    
    .def("__or__", [](pywgpu::TextureUsage& a, pywgpu::TextureUsage& b) {
        return (pywgpu::TextureUsage)(a | b);
    }, py::is_operator());
    

py::enum_<HeapProperty>(m, "HeapProperty", py::arithmetic())
    .value("NONE", HeapProperty::None)
    .value("DEVICE_LOCAL", HeapProperty::DeviceLocal)
    .value("HOST_VISIBLE", HeapProperty::HostVisible)
    .value("HOST_COHERENT", HeapProperty::HostCoherent)
    .value("HOST_UNCACHED", HeapProperty::HostUncached)
    .value("HOST_CACHED", HeapProperty::HostCached)
    
    .def("__or__", [](pywgpu::HeapProperty& a, pywgpu::HeapProperty& b) {
        return (pywgpu::HeapProperty)(a | b);
    }, py::is_operator());
    

py::class_<AdapterInfo> _AdapterInfo(m, "AdapterInfo");
registry.on(m, "AdapterInfo", _AdapterInfo);

_AdapterInfo
    .def_readonly("next_in_chain", &pywgpu::AdapterInfo::nextInChain)
    .def_readonly("vendor", &pywgpu::AdapterInfo::vendor)
    .def_readonly("architecture", &pywgpu::AdapterInfo::architecture)
    .def_readonly("device", &pywgpu::AdapterInfo::device)
    .def_readonly("description", &pywgpu::AdapterInfo::description)
    .def_readonly("backend_type", &pywgpu::AdapterInfo::backendType)
    .def_readonly("adapter_type", &pywgpu::AdapterInfo::adapterType)
    .def_readonly("vendor_ID", &pywgpu::AdapterInfo::vendorID)
    .def_readonly("device_ID", &pywgpu::AdapterInfo::deviceID)
    .def_readonly("subgroup_min_size", &pywgpu::AdapterInfo::subgroupMinSize)
    .def_readonly("subgroup_max_size", &pywgpu::AdapterInfo::subgroupMaxSize)
    .def(py::init<>())
    ;

py::class_<SurfaceCapabilities> _SurfaceCapabilities(m, "SurfaceCapabilities");
registry.on(m, "SurfaceCapabilities", _SurfaceCapabilities);

_SurfaceCapabilities
    .def_readonly("next_in_chain", &pywgpu::SurfaceCapabilities::nextInChain)
    .def_readonly("usages", &pywgpu::SurfaceCapabilities::usages)
    .def_readonly("format_count", &pywgpu::SurfaceCapabilities::formatCount)
    .def_readonly("formats", &pywgpu::SurfaceCapabilities::formats)
    .def_readonly("present_mode_count", &pywgpu::SurfaceCapabilities::presentModeCount)
    .def_readonly("present_modes", &pywgpu::SurfaceCapabilities::presentModes)
    .def_readonly("alpha_mode_count", &pywgpu::SurfaceCapabilities::alphaModeCount)
    .def_readonly("alpha_modes", &pywgpu::SurfaceCapabilities::alphaModes)
    .def(py::init<>())
    ;

py::class_<AdapterPropertiesSubgroups, ChainedStructOut> _AdapterPropertiesSubgroups(m, "AdapterPropertiesSubgroups");
registry.on(m, "AdapterPropertiesSubgroups", _AdapterPropertiesSubgroups);

_AdapterPropertiesSubgroups
    .def_readonly("next_in_chain", &pywgpu::AdapterPropertiesSubgroups::nextInChain)
    .def_readonly("subgroup_min_size", &pywgpu::AdapterPropertiesSubgroups::subgroupMinSize)
    .def_readonly("subgroup_max_size", &pywgpu::AdapterPropertiesSubgroups::subgroupMaxSize)
    .def(py::init<>())
    ;

py::class_<DawnExperimentalImmediateDataLimits, ChainedStructOut> _DawnExperimentalImmediateDataLimits(m, "DawnExperimentalImmediateDataLimits");
registry.on(m, "DawnExperimentalImmediateDataLimits", _DawnExperimentalImmediateDataLimits);

_DawnExperimentalImmediateDataLimits
    .def_readonly("next_in_chain", &pywgpu::DawnExperimentalImmediateDataLimits::nextInChain)
    .def_readonly("max_immediate_data_range_byte_size", &pywgpu::DawnExperimentalImmediateDataLimits::maxImmediateDataRangeByteSize)
    .def(py::init<>())
    ;

py::class_<DawnTexelCopyBufferRowAlignmentLimits, ChainedStructOut> _DawnTexelCopyBufferRowAlignmentLimits(m, "DawnTexelCopyBufferRowAlignmentLimits");
registry.on(m, "DawnTexelCopyBufferRowAlignmentLimits", _DawnTexelCopyBufferRowAlignmentLimits);

_DawnTexelCopyBufferRowAlignmentLimits
    .def_readonly("next_in_chain", &pywgpu::DawnTexelCopyBufferRowAlignmentLimits::nextInChain)
    .def_readonly("min_texel_copy_buffer_row_alignment", &pywgpu::DawnTexelCopyBufferRowAlignmentLimits::minTexelCopyBufferRowAlignment)
    .def(py::init<>())
    ;

py::class_<SharedBufferMemoryProperties> _SharedBufferMemoryProperties(m, "SharedBufferMemoryProperties");
registry.on(m, "SharedBufferMemoryProperties", _SharedBufferMemoryProperties);

_SharedBufferMemoryProperties
    .def_readonly("next_in_chain", &pywgpu::SharedBufferMemoryProperties::nextInChain)
    .def_readonly("usage", &pywgpu::SharedBufferMemoryProperties::usage)
    .def_readonly("size", &pywgpu::SharedBufferMemoryProperties::size)
    .def(py::init<>())
    ;

py::class_<SharedTextureMemoryProperties> _SharedTextureMemoryProperties(m, "SharedTextureMemoryProperties");
registry.on(m, "SharedTextureMemoryProperties", _SharedTextureMemoryProperties);

_SharedTextureMemoryProperties
    .def_readonly("next_in_chain", &pywgpu::SharedTextureMemoryProperties::nextInChain)
    .def_readonly("usage", &pywgpu::SharedTextureMemoryProperties::usage)
    .def_readonly("size", &pywgpu::SharedTextureMemoryProperties::size)
    .def_readonly("format", &pywgpu::SharedTextureMemoryProperties::format)
    .def(py::init<>())
    ;

py::class_<SharedTextureMemoryAHardwareBufferProperties, ChainedStructOut> _SharedTextureMemoryAHardwareBufferProperties(m, "SharedTextureMemoryAHardwareBufferProperties");
registry.on(m, "SharedTextureMemoryAHardwareBufferProperties", _SharedTextureMemoryAHardwareBufferProperties);

_SharedTextureMemoryAHardwareBufferProperties
    .def_readonly("next_in_chain", &pywgpu::SharedTextureMemoryAHardwareBufferProperties::nextInChain)
    .def_readonly("y_cb_cr_info", &pywgpu::SharedTextureMemoryAHardwareBufferProperties::yCbCrInfo)
    .def(py::init<>())
    ;

py::class_<SharedBufferMemoryEndAccessState> _SharedBufferMemoryEndAccessState(m, "SharedBufferMemoryEndAccessState");
registry.on(m, "SharedBufferMemoryEndAccessState", _SharedBufferMemoryEndAccessState);

_SharedBufferMemoryEndAccessState
    .def_readonly("next_in_chain", &pywgpu::SharedBufferMemoryEndAccessState::nextInChain)
    .def_readonly("initialized", &pywgpu::SharedBufferMemoryEndAccessState::initialized)
    .def_readonly("fence_count", &pywgpu::SharedBufferMemoryEndAccessState::fenceCount)
    .def_readonly("fences", &pywgpu::SharedBufferMemoryEndAccessState::fences)
    .def_readonly("signaled_values", &pywgpu::SharedBufferMemoryEndAccessState::signaledValues)
    .def(py::init<>())
    ;

py::class_<SharedTextureMemoryEndAccessState> _SharedTextureMemoryEndAccessState(m, "SharedTextureMemoryEndAccessState");
registry.on(m, "SharedTextureMemoryEndAccessState", _SharedTextureMemoryEndAccessState);

_SharedTextureMemoryEndAccessState
    .def_readonly("next_in_chain", &pywgpu::SharedTextureMemoryEndAccessState::nextInChain)
    .def_readonly("initialized", &pywgpu::SharedTextureMemoryEndAccessState::initialized)
    .def_readonly("fence_count", &pywgpu::SharedTextureMemoryEndAccessState::fenceCount)
    .def_readonly("fences", &pywgpu::SharedTextureMemoryEndAccessState::fences)
    .def_readonly("signaled_values", &pywgpu::SharedTextureMemoryEndAccessState::signaledValues)
    .def(py::init<>())
    ;

py::class_<SharedTextureMemoryVkImageLayoutEndState, ChainedStructOut> _SharedTextureMemoryVkImageLayoutEndState(m, "SharedTextureMemoryVkImageLayoutEndState");
registry.on(m, "SharedTextureMemoryVkImageLayoutEndState", _SharedTextureMemoryVkImageLayoutEndState);

_SharedTextureMemoryVkImageLayoutEndState
    .def_readonly("next_in_chain", &pywgpu::SharedTextureMemoryVkImageLayoutEndState::nextInChain)
    .def_readonly("old_layout", &pywgpu::SharedTextureMemoryVkImageLayoutEndState::oldLayout)
    .def_readonly("new_layout", &pywgpu::SharedTextureMemoryVkImageLayoutEndState::newLayout)
    .def(py::init<>())
    ;

py::class_<SharedFenceExportInfo> _SharedFenceExportInfo(m, "SharedFenceExportInfo");
registry.on(m, "SharedFenceExportInfo", _SharedFenceExportInfo);

_SharedFenceExportInfo
    .def_readonly("next_in_chain", &pywgpu::SharedFenceExportInfo::nextInChain)
    .def_readonly("type", &pywgpu::SharedFenceExportInfo::type)
    .def(py::init<>())
    ;

py::class_<SharedFenceVkSemaphoreOpaqueFDExportInfo, ChainedStructOut> _SharedFenceVkSemaphoreOpaqueFDExportInfo(m, "SharedFenceVkSemaphoreOpaqueFDExportInfo");
registry.on(m, "SharedFenceVkSemaphoreOpaqueFDExportInfo", _SharedFenceVkSemaphoreOpaqueFDExportInfo);

_SharedFenceVkSemaphoreOpaqueFDExportInfo
    .def_readonly("next_in_chain", &pywgpu::SharedFenceVkSemaphoreOpaqueFDExportInfo::nextInChain)
    .def_readonly("handle", &pywgpu::SharedFenceVkSemaphoreOpaqueFDExportInfo::handle)
    .def(py::init<>())
    ;

py::class_<SharedFenceSyncFDExportInfo, ChainedStructOut> _SharedFenceSyncFDExportInfo(m, "SharedFenceSyncFDExportInfo");
registry.on(m, "SharedFenceSyncFDExportInfo", _SharedFenceSyncFDExportInfo);

_SharedFenceSyncFDExportInfo
    .def_readonly("next_in_chain", &pywgpu::SharedFenceSyncFDExportInfo::nextInChain)
    .def_readonly("handle", &pywgpu::SharedFenceSyncFDExportInfo::handle)
    .def(py::init<>())
    ;

py::class_<SharedFenceVkSemaphoreZirconHandleExportInfo, ChainedStructOut> _SharedFenceVkSemaphoreZirconHandleExportInfo(m, "SharedFenceVkSemaphoreZirconHandleExportInfo");
registry.on(m, "SharedFenceVkSemaphoreZirconHandleExportInfo", _SharedFenceVkSemaphoreZirconHandleExportInfo);

_SharedFenceVkSemaphoreZirconHandleExportInfo
    .def_readonly("next_in_chain", &pywgpu::SharedFenceVkSemaphoreZirconHandleExportInfo::nextInChain)
    .def_readonly("handle", &pywgpu::SharedFenceVkSemaphoreZirconHandleExportInfo::handle)
    .def(py::init<>())
    ;

py::class_<SharedFenceDXGISharedHandleExportInfo, ChainedStructOut> _SharedFenceDXGISharedHandleExportInfo(m, "SharedFenceDXGISharedHandleExportInfo");
registry.on(m, "SharedFenceDXGISharedHandleExportInfo", _SharedFenceDXGISharedHandleExportInfo);

_SharedFenceDXGISharedHandleExportInfo
    .def_readonly("next_in_chain", &pywgpu::SharedFenceDXGISharedHandleExportInfo::nextInChain)
    .def_readonly("handle", &pywgpu::SharedFenceDXGISharedHandleExportInfo::handle)
    .def(py::init<>())
    ;

py::class_<SharedFenceMTLSharedEventExportInfo, ChainedStructOut> _SharedFenceMTLSharedEventExportInfo(m, "SharedFenceMTLSharedEventExportInfo");
registry.on(m, "SharedFenceMTLSharedEventExportInfo", _SharedFenceMTLSharedEventExportInfo);

_SharedFenceMTLSharedEventExportInfo
    .def_readonly("next_in_chain", &pywgpu::SharedFenceMTLSharedEventExportInfo::nextInChain)
    .def_readonly("shared_event", &pywgpu::SharedFenceMTLSharedEventExportInfo::sharedEvent)
    .def(py::init<>())
    ;

py::class_<SharedFenceEGLSyncExportInfo, ChainedStructOut> _SharedFenceEGLSyncExportInfo(m, "SharedFenceEGLSyncExportInfo");
registry.on(m, "SharedFenceEGLSyncExportInfo", _SharedFenceEGLSyncExportInfo);

_SharedFenceEGLSyncExportInfo
    .def_readonly("next_in_chain", &pywgpu::SharedFenceEGLSyncExportInfo::nextInChain)
    .def_readonly("sync", &pywgpu::SharedFenceEGLSyncExportInfo::sync)
    .def(py::init<>())
    ;

py::class_<DawnFormatCapabilities> _DawnFormatCapabilities(m, "DawnFormatCapabilities");
registry.on(m, "DawnFormatCapabilities", _DawnFormatCapabilities);

_DawnFormatCapabilities
    .def_readonly("next_in_chain", &pywgpu::DawnFormatCapabilities::nextInChain)
    .def(py::init<>())
    ;

py::class_<DawnDrmFormatCapabilities, ChainedStructOut> _DawnDrmFormatCapabilities(m, "DawnDrmFormatCapabilities");
registry.on(m, "DawnDrmFormatCapabilities", _DawnDrmFormatCapabilities);

_DawnDrmFormatCapabilities
    .def_readonly("next_in_chain", &pywgpu::DawnDrmFormatCapabilities::nextInChain)
    .def_readonly("properties_count", &pywgpu::DawnDrmFormatCapabilities::propertiesCount)
    .def_readonly("properties", &pywgpu::DawnDrmFormatCapabilities::properties)
    .def(py::init<>())
    ;

py::class_<Future> _Future(m, "Future");
registry.on(m, "Future", _Future);

_Future
    .def_readwrite("id", &pywgpu::Future::id)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::Future obj{};
        static const std::set<std::string> allowed = {"id"};
        static const std::set<std::string> required = {"id"};
        
        // Check for unknown keys
        for (auto& item : kwargs) {
            std::string key = py::cast<std::string>(item.first);
            if (!allowed.count(key)) {
                throw py::key_error("Unknown keyword argument: '" + key + "'");
            }
        }

        // Check for required keys
        for (const auto& key : required) {
            if (!kwargs.contains(key.c_str())) {
                throw py::key_error("Missing required keyword argument: '" + key + "'");
            }
        }
        
        if (kwargs.contains("id"))
        {
            auto value = kwargs["id"].cast<uint64_t>();
            obj.id = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SurfaceTexture> _SurfaceTexture(m, "SurfaceTexture");
registry.on(m, "SurfaceTexture", _SurfaceTexture);

_SurfaceTexture
    .def_readonly("next_in_chain", &pywgpu::SurfaceTexture::nextInChain)
    .def_readonly("texture", &pywgpu::SurfaceTexture::texture)
    .def_readonly("status", &pywgpu::SurfaceTexture::status)
    .def(py::init<>())
    ;

py::class_<DawnAdapterPropertiesPowerPreference, ChainedStructOut> _DawnAdapterPropertiesPowerPreference(m, "DawnAdapterPropertiesPowerPreference");
registry.on(m, "DawnAdapterPropertiesPowerPreference", _DawnAdapterPropertiesPowerPreference);

_DawnAdapterPropertiesPowerPreference
    .def_readonly("next_in_chain", &pywgpu::DawnAdapterPropertiesPowerPreference::nextInChain)
    .def_readonly("power_preference", &pywgpu::DawnAdapterPropertiesPowerPreference::powerPreference)
    .def(py::init<>())
    ;

py::class_<AdapterPropertiesMemoryHeaps, ChainedStructOut> _AdapterPropertiesMemoryHeaps(m, "AdapterPropertiesMemoryHeaps");
registry.on(m, "AdapterPropertiesMemoryHeaps", _AdapterPropertiesMemoryHeaps);

_AdapterPropertiesMemoryHeaps
    .def_readonly("next_in_chain", &pywgpu::AdapterPropertiesMemoryHeaps::nextInChain)
    .def_readonly("heap_count", &pywgpu::AdapterPropertiesMemoryHeaps::heapCount)
    .def_readonly("heap_info", &pywgpu::AdapterPropertiesMemoryHeaps::heapInfo)
    .def(py::init<>())
    ;

py::class_<AdapterPropertiesD3D, ChainedStructOut> _AdapterPropertiesD3D(m, "AdapterPropertiesD3D");
registry.on(m, "AdapterPropertiesD3D", _AdapterPropertiesD3D);

_AdapterPropertiesD3D
    .def_readonly("next_in_chain", &pywgpu::AdapterPropertiesD3D::nextInChain)
    .def_readonly("shader_model", &pywgpu::AdapterPropertiesD3D::shaderModel)
    .def(py::init<>())
    ;

py::class_<AdapterPropertiesVk, ChainedStructOut> _AdapterPropertiesVk(m, "AdapterPropertiesVk");
registry.on(m, "AdapterPropertiesVk", _AdapterPropertiesVk);

_AdapterPropertiesVk
    .def_readonly("next_in_chain", &pywgpu::AdapterPropertiesVk::nextInChain)
    .def_readonly("driver_version", &pywgpu::AdapterPropertiesVk::driverVersion)
    .def(py::init<>())
    ;

py::class_<AdapterPropertiesSubgroupMatrixConfigs, ChainedStructOut> _AdapterPropertiesSubgroupMatrixConfigs(m, "AdapterPropertiesSubgroupMatrixConfigs");
registry.on(m, "AdapterPropertiesSubgroupMatrixConfigs", _AdapterPropertiesSubgroupMatrixConfigs);

_AdapterPropertiesSubgroupMatrixConfigs
    .def_readonly("next_in_chain", &pywgpu::AdapterPropertiesSubgroupMatrixConfigs::nextInChain)
    .def_readonly("config_count", &pywgpu::AdapterPropertiesSubgroupMatrixConfigs::configCount)
    .def_readonly("configs", &pywgpu::AdapterPropertiesSubgroupMatrixConfigs::configs)
    .def(py::init<>())
    ;

py::class_<Adapter> _Adapter(m, "Adapter");
registry.on(m, "Adapter", _Adapter);

_Adapter
.def("get_instance",&pywgpu::Adapter::GetInstance
)

.def("get_limits",[](pywgpu::Adapter& self, py::handle limits) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::Limits * _limits = Builder<Limits>(ctx).build(limits);
        
        return self.GetLimits(_limits);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("limits"))

.def("get_info",&pywgpu::Adapter::GetInfo
, py::arg("info"))

.def("has_feature",&pywgpu::Adapter::HasFeature
, py::arg("feature"))

.def("get_features",[](pywgpu::Adapter& self, py::handle features) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::SupportedFeatures * _features = Builder<SupportedFeatures>(ctx).build(features);
        
        return self.GetFeatures(_features);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("features"))

.def("_request_device",[](pywgpu::Adapter& self, py::handle options, RequestDeviceCallbackInfo callbackInfo) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::DeviceDescriptor const* _options = Builder<DeviceDescriptor>(ctx).build(options);
        
        return self.RequestDevice(_options, callbackInfo);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("options"), py::arg("callback_info"))

.def("create_device",[](pywgpu::Adapter& self, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::DeviceDescriptor const* _descriptor = Builder<DeviceDescriptor>(ctx).build(descriptor);
        
        return self.CreateDevice(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor") = nullptr)

.def("get_format_capabilities",&pywgpu::Adapter::GetFormatCapabilities
, py::arg("format"), py::arg("capabilities"))

;

py::class_<BindGroup> _BindGroup(m, "BindGroup");
registry.on(m, "BindGroup", _BindGroup);

_BindGroup
.def("set_label",&pywgpu::BindGroup::SetLabel
, py::arg("label"))

;

py::class_<BindGroupLayout> _BindGroupLayout(m, "BindGroupLayout");
registry.on(m, "BindGroupLayout", _BindGroupLayout);

_BindGroupLayout
.def("set_label",&pywgpu::BindGroupLayout::SetLabel
, py::arg("label"))

;

py::class_<Buffer> _Buffer(m, "Buffer");
registry.on(m, "Buffer", _Buffer);

_Buffer
.def("_map_async",&pywgpu::Buffer::MapAsync
, py::arg("mode"), py::arg("offset"), py::arg("size"), py::arg("callback_info"))

.def("get_mapped_range",&pywgpu::Buffer::GetMappedRange
, py::arg("offset") = 0, py::arg("size") = kWholeMapSize)

.def("get_const_mapped_range",&pywgpu::Buffer::GetConstMappedRange
, py::arg("offset") = 0, py::arg("size") = kWholeMapSize)

.def("write_mapped_range",[](pywgpu::Buffer& self, size_t offset, py::buffer data) {
    try {
        py::buffer_info dataInfo = data.request();
        void const* _data = (void const*)dataInfo.ptr;
        auto size = ((dataInfo.size * dataInfo.itemsize) + 3) & ~size_t(3);
        
        return self.WriteMappedRange(offset, _data, size);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("offset"), py::arg("data"))

.def("read_mapped_range",[](pywgpu::Buffer& self, size_t offset, py::buffer data) {
    try {
        py::buffer_info dataInfo = data.request();
        void * _data = (void *)dataInfo.ptr;
        auto size = ((dataInfo.size * dataInfo.itemsize) + 3) & ~size_t(3);
        
        return self.ReadMappedRange(offset, _data, size);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("offset"), py::arg("data"))

.def("set_label",&pywgpu::Buffer::SetLabel
, py::arg("label"))

.def("get_usage",&pywgpu::Buffer::GetUsage
)

.def("get_size",&pywgpu::Buffer::GetSize
)

.def("get_map_state",&pywgpu::Buffer::GetMapState
)

.def("unmap",&pywgpu::Buffer::Unmap
)

.def("destroy",&pywgpu::Buffer::Destroy
)

;

py::class_<CommandBuffer> _CommandBuffer(m, "CommandBuffer");
registry.on(m, "CommandBuffer", _CommandBuffer);

_CommandBuffer
.def("set_label",&pywgpu::CommandBuffer::SetLabel
, py::arg("label"))

;

py::class_<CommandEncoder> _CommandEncoder(m, "CommandEncoder");
registry.on(m, "CommandEncoder", _CommandEncoder);

_CommandEncoder
.def("finish",[](pywgpu::CommandEncoder& self, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::CommandBufferDescriptor const* _descriptor = Builder<CommandBufferDescriptor>(ctx).build(descriptor);
        
        return self.Finish(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor") = nullptr)

.def("begin_compute_pass",[](pywgpu::CommandEncoder& self, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::ComputePassDescriptor const* _descriptor = Builder<ComputePassDescriptor>(ctx).build(descriptor);
        
        return self.BeginComputePass(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor") = nullptr)

.def("begin_render_pass",[](pywgpu::CommandEncoder& self, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::RenderPassDescriptor const* _descriptor = Builder<RenderPassDescriptor>(ctx).build(descriptor);
        
        return self.BeginRenderPass(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor"))

.def("copy_buffer_to_buffer",&pywgpu::CommandEncoder::CopyBufferToBuffer
, py::arg("source"), py::arg("source_offset"), py::arg("destination"), py::arg("destination_offset"), py::arg("size"))

.def("copy_buffer_to_texture",[](pywgpu::CommandEncoder& self, py::handle source, py::handle destination, py::handle copySize) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::TexelCopyBufferInfo const* _source = Builder<TexelCopyBufferInfo>(ctx).build(source);
        
        pywgpu::TexelCopyTextureInfo const* _destination = Builder<TexelCopyTextureInfo>(ctx).build(destination);
        
        pywgpu::Extent3D const* _copySize = Builder<Extent3D>(ctx).build(copySize);
        
        return self.CopyBufferToTexture(_source, _destination, _copySize);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("source"), py::arg("destination"), py::arg("copy_size"))

.def("copy_texture_to_buffer",[](pywgpu::CommandEncoder& self, py::handle source, py::handle destination, py::handle copySize) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::TexelCopyTextureInfo const* _source = Builder<TexelCopyTextureInfo>(ctx).build(source);
        
        pywgpu::TexelCopyBufferInfo const* _destination = Builder<TexelCopyBufferInfo>(ctx).build(destination);
        
        pywgpu::Extent3D const* _copySize = Builder<Extent3D>(ctx).build(copySize);
        
        return self.CopyTextureToBuffer(_source, _destination, _copySize);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("source"), py::arg("destination"), py::arg("copy_size"))

.def("copy_texture_to_texture",[](pywgpu::CommandEncoder& self, py::handle source, py::handle destination, py::handle copySize) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::TexelCopyTextureInfo const* _source = Builder<TexelCopyTextureInfo>(ctx).build(source);
        
        pywgpu::TexelCopyTextureInfo const* _destination = Builder<TexelCopyTextureInfo>(ctx).build(destination);
        
        pywgpu::Extent3D const* _copySize = Builder<Extent3D>(ctx).build(copySize);
        
        return self.CopyTextureToTexture(_source, _destination, _copySize);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("source"), py::arg("destination"), py::arg("copy_size"))

.def("clear_buffer",&pywgpu::CommandEncoder::ClearBuffer
, py::arg("buffer"), py::arg("offset") = 0, py::arg("size") = kWholeSize)

.def("inject_validation_error",&pywgpu::CommandEncoder::InjectValidationError
, py::arg("message"))

.def("insert_debug_marker",&pywgpu::CommandEncoder::InsertDebugMarker
, py::arg("marker_label"))

.def("pop_debug_group",&pywgpu::CommandEncoder::PopDebugGroup
)

.def("push_debug_group",&pywgpu::CommandEncoder::PushDebugGroup
, py::arg("group_label"))

.def("resolve_query_set",&pywgpu::CommandEncoder::ResolveQuerySet
, py::arg("query_set"), py::arg("first_query"), py::arg("query_count"), py::arg("destination"), py::arg("destination_offset"))

.def("write_buffer",[](pywgpu::CommandEncoder& self, Buffer buffer, uint64_t bufferOffset, py::buffer data) {
    try {
        py::buffer_info dataInfo = data.request();
        uint8_t const* _data = (uint8_t const*)dataInfo.ptr;
        auto size = ((dataInfo.size * dataInfo.itemsize) + 3) & ~size_t(3);
        
        return self.WriteBuffer(buffer, bufferOffset, _data, size);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("buffer"), py::arg("buffer_offset"), py::arg("data"))

.def("write_timestamp",&pywgpu::CommandEncoder::WriteTimestamp
, py::arg("query_set"), py::arg("query_index"))

.def("set_label",&pywgpu::CommandEncoder::SetLabel
, py::arg("label"))

;

py::class_<ComputePassEncoder> _ComputePassEncoder(m, "ComputePassEncoder");
registry.on(m, "ComputePassEncoder", _ComputePassEncoder);

_ComputePassEncoder
.def("insert_debug_marker",&pywgpu::ComputePassEncoder::InsertDebugMarker
, py::arg("marker_label"))

.def("pop_debug_group",&pywgpu::ComputePassEncoder::PopDebugGroup
)

.def("push_debug_group",&pywgpu::ComputePassEncoder::PushDebugGroup
, py::arg("group_label"))

.def("set_pipeline",&pywgpu::ComputePassEncoder::SetPipeline
, py::arg("pipeline"))

.def("set_bind_group",[](pywgpu::ComputePassEncoder& self, uint32_t groupIndex, BindGroup group, std::optional<py::buffer> dynamicOffsets) {
    try {
        py::buffer_info dynamicOffsetsInfo = dynamicOffsets.has_value() ? dynamicOffsets.value().request() : py::buffer_info();
        uint32_t const* _dynamicOffsets = (uint32_t const*)dynamicOffsetsInfo.ptr;
        auto dynamicOffsetCount = ((dynamicOffsetsInfo.size * dynamicOffsetsInfo.itemsize) + 3) & ~size_t(3);
        
        return self.SetBindGroup(groupIndex, group, dynamicOffsetCount, _dynamicOffsets);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("group_index"), py::arg("group"), py::arg("dynamic_offsets") = nullptr)

.def("write_timestamp",&pywgpu::ComputePassEncoder::WriteTimestamp
, py::arg("query_set"), py::arg("query_index"))

.def("dispatch_workgroups",&pywgpu::ComputePassEncoder::DispatchWorkgroups
, py::arg("workgroupCountX"), py::arg("workgroupCountY") = 1, py::arg("workgroupCountZ") = 1)

.def("dispatch_workgroups_indirect",&pywgpu::ComputePassEncoder::DispatchWorkgroupsIndirect
, py::arg("indirect_buffer"), py::arg("indirect_offset"))

.def("end",&pywgpu::ComputePassEncoder::End
)

.def("set_label",&pywgpu::ComputePassEncoder::SetLabel
, py::arg("label"))

.def("set_immediate_data",[](pywgpu::ComputePassEncoder& self, uint32_t offset, py::buffer data) {
    try {
        py::buffer_info dataInfo = data.request();
        void const* _data = (void const*)dataInfo.ptr;
        auto size = ((dataInfo.size * dataInfo.itemsize) + 3) & ~size_t(3);
        
        return self.SetImmediateData(offset, _data, size);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("offset"), py::arg("data"))

;

py::class_<ComputePipeline> _ComputePipeline(m, "ComputePipeline");
registry.on(m, "ComputePipeline", _ComputePipeline);

_ComputePipeline
.def("get_bind_group_layout",&pywgpu::ComputePipeline::GetBindGroupLayout
, py::arg("group_index"))

.def("set_label",&pywgpu::ComputePipeline::SetLabel
, py::arg("label"))

;

py::class_<Device> _Device(m, "Device");
registry.on(m, "Device", _Device);

_Device
.def("create_bind_group",[](pywgpu::Device& self, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::BindGroupDescriptor const* _descriptor = Builder<BindGroupDescriptor>(ctx).build(descriptor);
        
        return self.CreateBindGroup(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor"))

.def("create_bind_group_layout",[](pywgpu::Device& self, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::BindGroupLayoutDescriptor const* _descriptor = Builder<BindGroupLayoutDescriptor>(ctx).build(descriptor);
        
        return self.CreateBindGroupLayout(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor"))

.def("create_buffer",[](pywgpu::Device& self, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::BufferDescriptor const* _descriptor = Builder<BufferDescriptor>(ctx).build(descriptor);
        
        return self.CreateBuffer(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor"))

.def("create_error_buffer",[](pywgpu::Device& self, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::BufferDescriptor const* _descriptor = Builder<BufferDescriptor>(ctx).build(descriptor);
        
        return self.CreateErrorBuffer(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor"))

.def("create_command_encoder",[](pywgpu::Device& self, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::CommandEncoderDescriptor const* _descriptor = Builder<CommandEncoderDescriptor>(ctx).build(descriptor);
        
        return self.CreateCommandEncoder(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor") = nullptr)

.def("create_compute_pipeline",[](pywgpu::Device& self, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::ComputePipelineDescriptor const* _descriptor = Builder<ComputePipelineDescriptor>(ctx).build(descriptor);
        
        return self.CreateComputePipeline(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor"))

.def("_create_compute_pipeline_async",[](pywgpu::Device& self, py::handle descriptor, CreateComputePipelineAsyncCallbackInfo callbackInfo) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::ComputePipelineDescriptor const* _descriptor = Builder<ComputePipelineDescriptor>(ctx).build(descriptor);
        
        return self.CreateComputePipelineAsync(_descriptor, callbackInfo);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor"), py::arg("callback_info"))

.def("create_external_texture",[](pywgpu::Device& self, py::handle externalTextureDescriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::ExternalTextureDescriptor const* _externalTextureDescriptor = Builder<ExternalTextureDescriptor>(ctx).build(externalTextureDescriptor);
        
        return self.CreateExternalTexture(_externalTextureDescriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("external_texture_descriptor"))

.def("create_error_external_texture",&pywgpu::Device::CreateErrorExternalTexture
)

.def("create_pipeline_layout",[](pywgpu::Device& self, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::PipelineLayoutDescriptor const* _descriptor = Builder<PipelineLayoutDescriptor>(ctx).build(descriptor);
        
        return self.CreatePipelineLayout(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor"))

.def("create_query_set",[](pywgpu::Device& self, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::QuerySetDescriptor const* _descriptor = Builder<QuerySetDescriptor>(ctx).build(descriptor);
        
        return self.CreateQuerySet(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor"))

.def("_create_render_pipeline_async",[](pywgpu::Device& self, py::handle descriptor, CreateRenderPipelineAsyncCallbackInfo callbackInfo) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::RenderPipelineDescriptor const* _descriptor = Builder<RenderPipelineDescriptor>(ctx).build(descriptor);
        
        return self.CreateRenderPipelineAsync(_descriptor, callbackInfo);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor"), py::arg("callback_info"))

.def("create_render_bundle_encoder",[](pywgpu::Device& self, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::RenderBundleEncoderDescriptor const* _descriptor = Builder<RenderBundleEncoderDescriptor>(ctx).build(descriptor);
        
        return self.CreateRenderBundleEncoder(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor"))

.def("create_render_pipeline",[](pywgpu::Device& self, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::RenderPipelineDescriptor const* _descriptor = Builder<RenderPipelineDescriptor>(ctx).build(descriptor);
        
        return self.CreateRenderPipeline(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor"))

.def("create_sampler",[](pywgpu::Device& self, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::SamplerDescriptor const* _descriptor = Builder<SamplerDescriptor>(ctx).build(descriptor);
        
        return self.CreateSampler(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor") = nullptr)

.def("create_shader_module",[](pywgpu::Device& self, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::ShaderModuleDescriptor const* _descriptor = Builder<ShaderModuleDescriptor>(ctx).build(descriptor);
        
        return self.CreateShaderModule(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor"))

.def("create_error_shader_module",[](pywgpu::Device& self, py::handle descriptor, StringView errorMessage) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::ShaderModuleDescriptor const* _descriptor = Builder<ShaderModuleDescriptor>(ctx).build(descriptor);
        
        return self.CreateErrorShaderModule(_descriptor, errorMessage);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor"), py::arg("error_message"))

.def("create_texture",[](pywgpu::Device& self, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::TextureDescriptor const* _descriptor = Builder<TextureDescriptor>(ctx).build(descriptor);
        
        return self.CreateTexture(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor"))

.def("import_shared_buffer_memory",[](pywgpu::Device& self, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::SharedBufferMemoryDescriptor const* _descriptor = Builder<SharedBufferMemoryDescriptor>(ctx).build(descriptor);
        
        return self.ImportSharedBufferMemory(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor"))

.def("import_shared_texture_memory",[](pywgpu::Device& self, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::SharedTextureMemoryDescriptor const* _descriptor = Builder<SharedTextureMemoryDescriptor>(ctx).build(descriptor);
        
        return self.ImportSharedTextureMemory(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor"))

.def("import_shared_fence",[](pywgpu::Device& self, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::SharedFenceDescriptor const* _descriptor = Builder<SharedFenceDescriptor>(ctx).build(descriptor);
        
        return self.ImportSharedFence(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor"))

.def("create_error_texture",[](pywgpu::Device& self, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::TextureDescriptor const* _descriptor = Builder<TextureDescriptor>(ctx).build(descriptor);
        
        return self.CreateErrorTexture(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor"))

.def("destroy",&pywgpu::Device::Destroy
)

.def("get_a_hardware_buffer_properties",[](pywgpu::Device& self, void * handle, py::handle properties) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::AHardwareBufferProperties * _properties = Builder<AHardwareBufferProperties>(ctx).build(properties);
        
        return self.GetAHardwareBufferProperties(handle, _properties);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("handle"), py::arg("properties"))

.def("get_limits",[](pywgpu::Device& self, py::handle limits) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::Limits * _limits = Builder<Limits>(ctx).build(limits);
        
        return self.GetLimits(_limits);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("limits"))

.def("_get_lost_future",&pywgpu::Device::GetLostFuture
)

.def("has_feature",&pywgpu::Device::HasFeature
, py::arg("feature"))

.def("get_features",[](pywgpu::Device& self, py::handle features) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::SupportedFeatures * _features = Builder<SupportedFeatures>(ctx).build(features);
        
        return self.GetFeatures(_features);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("features"))

.def("get_adapter_info",&pywgpu::Device::GetAdapterInfo
, py::arg("adapter_info"))

.def("get_adapter",&pywgpu::Device::GetAdapter
)

.def("get_queue",&pywgpu::Device::GetQueue
)

.def("inject_error",&pywgpu::Device::InjectError
, py::arg("type"), py::arg("message"))

.def("force_loss",&pywgpu::Device::ForceLoss
, py::arg("type"), py::arg("message"))

.def("tick",&pywgpu::Device::Tick
)

.def("set_logging_callback",&pywgpu::Device::SetLoggingCallback
, py::arg("callback_info"))

.def("push_error_scope",&pywgpu::Device::PushErrorScope
, py::arg("filter"))

.def("_pop_error_scope",&pywgpu::Device::PopErrorScope
, py::arg("callback_info"))

.def("set_label",&pywgpu::Device::SetLabel
, py::arg("label"))

.def("validate_texture_descriptor",[](pywgpu::Device& self, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::TextureDescriptor const* _descriptor = Builder<TextureDescriptor>(ctx).build(descriptor);
        
        return self.ValidateTextureDescriptor(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor"))

;

py::class_<ExternalTexture> _ExternalTexture(m, "ExternalTexture");
registry.on(m, "ExternalTexture", _ExternalTexture);

_ExternalTexture
.def("set_label",&pywgpu::ExternalTexture::SetLabel
, py::arg("label"))

.def("destroy",&pywgpu::ExternalTexture::Destroy
)

.def("expire",&pywgpu::ExternalTexture::Expire
)

.def("refresh",&pywgpu::ExternalTexture::Refresh
)

;

py::class_<SharedBufferMemory> _SharedBufferMemory(m, "SharedBufferMemory");
registry.on(m, "SharedBufferMemory", _SharedBufferMemory);

_SharedBufferMemory
.def("set_label",&pywgpu::SharedBufferMemory::SetLabel
, py::arg("label"))

.def("get_properties",&pywgpu::SharedBufferMemory::GetProperties
, py::arg("properties"))

.def("create_buffer",[](pywgpu::SharedBufferMemory& self, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::BufferDescriptor const* _descriptor = Builder<BufferDescriptor>(ctx).build(descriptor);
        
        return self.CreateBuffer(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor") = nullptr)

.def("begin_access",[](pywgpu::SharedBufferMemory& self, Buffer buffer, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::SharedBufferMemoryBeginAccessDescriptor const* _descriptor = Builder<SharedBufferMemoryBeginAccessDescriptor>(ctx).build(descriptor);
        
        return self.BeginAccess(buffer, _descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("buffer"), py::arg("descriptor"))

.def("end_access",&pywgpu::SharedBufferMemory::EndAccess
, py::arg("buffer"), py::arg("descriptor"))

.def("is_device_lost",&pywgpu::SharedBufferMemory::IsDeviceLost
)

;

py::class_<SharedTextureMemory> _SharedTextureMemory(m, "SharedTextureMemory");
registry.on(m, "SharedTextureMemory", _SharedTextureMemory);

_SharedTextureMemory
.def("set_label",&pywgpu::SharedTextureMemory::SetLabel
, py::arg("label"))

.def("get_properties",&pywgpu::SharedTextureMemory::GetProperties
, py::arg("properties"))

.def("create_texture",[](pywgpu::SharedTextureMemory& self, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::TextureDescriptor const* _descriptor = Builder<TextureDescriptor>(ctx).build(descriptor);
        
        return self.CreateTexture(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor") = nullptr)

.def("begin_access",[](pywgpu::SharedTextureMemory& self, Texture texture, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::SharedTextureMemoryBeginAccessDescriptor const* _descriptor = Builder<SharedTextureMemoryBeginAccessDescriptor>(ctx).build(descriptor);
        
        return self.BeginAccess(texture, _descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("texture"), py::arg("descriptor"))

.def("end_access",&pywgpu::SharedTextureMemory::EndAccess
, py::arg("texture"), py::arg("descriptor"))

.def("is_device_lost",&pywgpu::SharedTextureMemory::IsDeviceLost
)

;

py::class_<SharedFence> _SharedFence(m, "SharedFence");
registry.on(m, "SharedFence", _SharedFence);

_SharedFence
.def("export_info",&pywgpu::SharedFence::ExportInfo
, py::arg("info"))

;

py::class_<Instance> _Instance(m, "Instance");
registry.on(m, "Instance", _Instance);

_Instance
.def("create_surface",[](pywgpu::Instance& self, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::SurfaceDescriptor const* _descriptor = Builder<SurfaceDescriptor>(ctx).build(descriptor);
        
        return self.CreateSurface(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor"))

.def("process_events",&pywgpu::Instance::ProcessEvents
)

.def("wait_any",[](pywgpu::Instance& self, py::handle futures, uint64_t timeoutNS) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        uint32_t futureCount;
        pywgpu::FutureWaitInfo * _futures = Builder<FutureWaitInfo>(ctx).build_array(futures, &futureCount);
        
        return self.WaitAny(futureCount, _futures, timeoutNS);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("futures"), py::arg("timeout_NS"))

.def("_request_adapter",[](pywgpu::Instance& self, py::handle options, RequestAdapterCallbackInfo callbackInfo) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::RequestAdapterOptions const* _options = Builder<RequestAdapterOptions>(ctx).build(options);
        
        return self.RequestAdapter(_options, callbackInfo);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("options"), py::arg("callback_info"))

.def("has_WGSL_language_feature",&pywgpu::Instance::HasWGSLLanguageFeature
, py::arg("feature"))

.def("get_WGSL_language_features",[](pywgpu::Instance& self, py::handle features) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::SupportedWGSLLanguageFeatures * _features = Builder<SupportedWGSLLanguageFeatures>(ctx).build(features);
        
        return self.GetWGSLLanguageFeatures(_features);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("features"))

;

py::class_<PipelineLayout> _PipelineLayout(m, "PipelineLayout");
registry.on(m, "PipelineLayout", _PipelineLayout);

_PipelineLayout
.def("set_label",&pywgpu::PipelineLayout::SetLabel
, py::arg("label"))

;

py::class_<QuerySet> _QuerySet(m, "QuerySet");
registry.on(m, "QuerySet", _QuerySet);

_QuerySet
.def("set_label",&pywgpu::QuerySet::SetLabel
, py::arg("label"))

.def("get_type",&pywgpu::QuerySet::GetType
)

.def("get_count",&pywgpu::QuerySet::GetCount
)

.def("destroy",&pywgpu::QuerySet::Destroy
)

;

py::class_<Queue> _Queue(m, "Queue");
registry.on(m, "Queue", _Queue);

_Queue
.def("submit",[](pywgpu::Queue& self, std::vector<pywgpu::CommandBuffer> commands) {
    try {
        pywgpu::CommandBuffer const* _commands = (pywgpu::CommandBuffer const*)commands.data();
        auto commandCount = commands.size();
        
        return self.Submit(commandCount, _commands);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("commands"))

.def("_on_submitted_work_done",&pywgpu::Queue::OnSubmittedWorkDone
, py::arg("callback_info"))

.def("write_buffer",[](pywgpu::Queue& self, Buffer buffer, uint64_t bufferOffset, py::buffer data) {
    try {
        py::buffer_info dataInfo = data.request();
        void const* _data = (void const*)dataInfo.ptr;
        auto size = ((dataInfo.size * dataInfo.itemsize) + 3) & ~size_t(3);
        
        return self.WriteBuffer(buffer, bufferOffset, _data, size);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("buffer"), py::arg("buffer_offset"), py::arg("data"))

.def("write_texture",[](pywgpu::Queue& self, py::handle destination, py::buffer data, py::handle dataLayout, py::handle writeSize) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::TexelCopyTextureInfo const* _destination = Builder<TexelCopyTextureInfo>(ctx).build(destination);
        
        py::buffer_info dataInfo = data.request();
        void const* _data = (void const*)dataInfo.ptr;
        auto dataSize = ((dataInfo.size * dataInfo.itemsize) + 3) & ~size_t(3);
        
        pywgpu::TexelCopyBufferLayout const* _dataLayout = Builder<TexelCopyBufferLayout>(ctx).build(dataLayout);
        
        pywgpu::Extent3D const* _writeSize = Builder<Extent3D>(ctx).build(writeSize);
        
        return self.WriteTexture(_destination, _data, dataSize, _dataLayout, _writeSize);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("destination"), py::arg("data"), py::arg("data_layout"), py::arg("write_size"))

.def("copy_texture_for_browser",[](pywgpu::Queue& self, py::handle source, py::handle destination, py::handle copySize, py::handle options) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::TexelCopyTextureInfo const* _source = Builder<TexelCopyTextureInfo>(ctx).build(source);
        
        pywgpu::TexelCopyTextureInfo const* _destination = Builder<TexelCopyTextureInfo>(ctx).build(destination);
        
        pywgpu::Extent3D const* _copySize = Builder<Extent3D>(ctx).build(copySize);
        
        pywgpu::CopyTextureForBrowserOptions const* _options = Builder<CopyTextureForBrowserOptions>(ctx).build(options);
        
        return self.CopyTextureForBrowser(_source, _destination, _copySize, _options);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("source"), py::arg("destination"), py::arg("copy_size"), py::arg("options"))

.def("copy_external_texture_for_browser",[](pywgpu::Queue& self, py::handle source, py::handle destination, py::handle copySize, py::handle options) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::ImageCopyExternalTexture const* _source = Builder<ImageCopyExternalTexture>(ctx).build(source);
        
        pywgpu::TexelCopyTextureInfo const* _destination = Builder<TexelCopyTextureInfo>(ctx).build(destination);
        
        pywgpu::Extent3D const* _copySize = Builder<Extent3D>(ctx).build(copySize);
        
        pywgpu::CopyTextureForBrowserOptions const* _options = Builder<CopyTextureForBrowserOptions>(ctx).build(options);
        
        return self.CopyExternalTextureForBrowser(_source, _destination, _copySize, _options);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("source"), py::arg("destination"), py::arg("copy_size"), py::arg("options"))

.def("set_label",&pywgpu::Queue::SetLabel
, py::arg("label"))

;

py::class_<RenderBundle> _RenderBundle(m, "RenderBundle");
registry.on(m, "RenderBundle", _RenderBundle);

_RenderBundle
.def("set_label",&pywgpu::RenderBundle::SetLabel
, py::arg("label"))

;

py::class_<RenderBundleEncoder> _RenderBundleEncoder(m, "RenderBundleEncoder");
registry.on(m, "RenderBundleEncoder", _RenderBundleEncoder);

_RenderBundleEncoder
.def("set_pipeline",&pywgpu::RenderBundleEncoder::SetPipeline
, py::arg("pipeline"))

.def("set_bind_group",[](pywgpu::RenderBundleEncoder& self, uint32_t groupIndex, BindGroup group, std::optional<py::buffer> dynamicOffsets) {
    try {
        py::buffer_info dynamicOffsetsInfo = dynamicOffsets.has_value() ? dynamicOffsets.value().request() : py::buffer_info();
        uint32_t const* _dynamicOffsets = (uint32_t const*)dynamicOffsetsInfo.ptr;
        auto dynamicOffsetCount = ((dynamicOffsetsInfo.size * dynamicOffsetsInfo.itemsize) + 3) & ~size_t(3);
        
        return self.SetBindGroup(groupIndex, group, dynamicOffsetCount, _dynamicOffsets);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("group_index"), py::arg("group"), py::arg("dynamic_offsets") = nullptr)

.def("draw",&pywgpu::RenderBundleEncoder::Draw
, py::arg("vertex_count"), py::arg("instance_count") = 1, py::arg("first_vertex") = 0, py::arg("first_instance") = 0)

.def("draw_indexed",&pywgpu::RenderBundleEncoder::DrawIndexed
, py::arg("index_count"), py::arg("instance_count") = 1, py::arg("first_index") = 0, py::arg("base_vertex") = 0, py::arg("first_instance") = 0)

.def("draw_indirect",&pywgpu::RenderBundleEncoder::DrawIndirect
, py::arg("indirect_buffer"), py::arg("indirect_offset"))

.def("draw_indexed_indirect",&pywgpu::RenderBundleEncoder::DrawIndexedIndirect
, py::arg("indirect_buffer"), py::arg("indirect_offset"))

.def("insert_debug_marker",&pywgpu::RenderBundleEncoder::InsertDebugMarker
, py::arg("marker_label"))

.def("pop_debug_group",&pywgpu::RenderBundleEncoder::PopDebugGroup
)

.def("push_debug_group",&pywgpu::RenderBundleEncoder::PushDebugGroup
, py::arg("group_label"))

.def("set_vertex_buffer",&pywgpu::RenderBundleEncoder::SetVertexBuffer
, py::arg("slot"), py::arg("buffer"), py::arg("offset") = 0, py::arg("size") = kWholeSize)

.def("set_index_buffer",&pywgpu::RenderBundleEncoder::SetIndexBuffer
, py::arg("buffer"), py::arg("format"), py::arg("offset") = 0, py::arg("size") = kWholeSize)

.def("finish",[](pywgpu::RenderBundleEncoder& self, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::RenderBundleDescriptor const* _descriptor = Builder<RenderBundleDescriptor>(ctx).build(descriptor);
        
        return self.Finish(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor") = nullptr)

.def("set_label",&pywgpu::RenderBundleEncoder::SetLabel
, py::arg("label"))

.def("set_immediate_data",[](pywgpu::RenderBundleEncoder& self, uint32_t offset, py::buffer data) {
    try {
        py::buffer_info dataInfo = data.request();
        void const* _data = (void const*)dataInfo.ptr;
        auto size = ((dataInfo.size * dataInfo.itemsize) + 3) & ~size_t(3);
        
        return self.SetImmediateData(offset, _data, size);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("offset"), py::arg("data"))

;

py::class_<RenderPassEncoder> _RenderPassEncoder(m, "RenderPassEncoder");
registry.on(m, "RenderPassEncoder", _RenderPassEncoder);

_RenderPassEncoder
.def("set_pipeline",&pywgpu::RenderPassEncoder::SetPipeline
, py::arg("pipeline"))

.def("set_bind_group",[](pywgpu::RenderPassEncoder& self, uint32_t groupIndex, BindGroup group, std::optional<py::buffer> dynamicOffsets) {
    try {
        py::buffer_info dynamicOffsetsInfo = dynamicOffsets.has_value() ? dynamicOffsets.value().request() : py::buffer_info();
        uint32_t const* _dynamicOffsets = (uint32_t const*)dynamicOffsetsInfo.ptr;
        auto dynamicOffsetCount = ((dynamicOffsetsInfo.size * dynamicOffsetsInfo.itemsize) + 3) & ~size_t(3);
        
        return self.SetBindGroup(groupIndex, group, dynamicOffsetCount, _dynamicOffsets);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("group_index"), py::arg("group"), py::arg("dynamic_offsets") = nullptr)

.def("draw",&pywgpu::RenderPassEncoder::Draw
, py::arg("vertex_count"), py::arg("instance_count") = 1, py::arg("first_vertex") = 0, py::arg("first_instance") = 0)

.def("draw_indexed",&pywgpu::RenderPassEncoder::DrawIndexed
, py::arg("index_count"), py::arg("instance_count") = 1, py::arg("first_index") = 0, py::arg("base_vertex") = 0, py::arg("first_instance") = 0)

.def("draw_indirect",&pywgpu::RenderPassEncoder::DrawIndirect
, py::arg("indirect_buffer"), py::arg("indirect_offset"))

.def("draw_indexed_indirect",&pywgpu::RenderPassEncoder::DrawIndexedIndirect
, py::arg("indirect_buffer"), py::arg("indirect_offset"))

.def("multi_draw_indirect",&pywgpu::RenderPassEncoder::MultiDrawIndirect
, py::arg("indirect_buffer"), py::arg("indirect_offset"), py::arg("max_draw_count"), py::arg("draw_count_buffer"), py::arg("draw_count_buffer_offset") = 0)

.def("multi_draw_indexed_indirect",&pywgpu::RenderPassEncoder::MultiDrawIndexedIndirect
, py::arg("indirect_buffer"), py::arg("indirect_offset"), py::arg("max_draw_count"), py::arg("draw_count_buffer"), py::arg("draw_count_buffer_offset") = 0)

.def("execute_bundles",[](pywgpu::RenderPassEncoder& self, std::vector<pywgpu::RenderBundle> bundles) {
    try {
        pywgpu::RenderBundle const* _bundles = (pywgpu::RenderBundle const*)bundles.data();
        auto bundleCount = bundles.size();
        
        return self.ExecuteBundles(bundleCount, _bundles);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("bundles"))

.def("insert_debug_marker",&pywgpu::RenderPassEncoder::InsertDebugMarker
, py::arg("marker_label"))

.def("pop_debug_group",&pywgpu::RenderPassEncoder::PopDebugGroup
)

.def("push_debug_group",&pywgpu::RenderPassEncoder::PushDebugGroup
, py::arg("group_label"))

.def("set_stencil_reference",&pywgpu::RenderPassEncoder::SetStencilReference
, py::arg("reference"))

.def("set_blend_constant",[](pywgpu::RenderPassEncoder& self, py::handle color) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::Color const* _color = Builder<Color>(ctx).build(color);
        
        return self.SetBlendConstant(_color);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("color"))

.def("set_viewport",&pywgpu::RenderPassEncoder::SetViewport
, py::arg("x"), py::arg("y"), py::arg("width"), py::arg("height"), py::arg("min_depth"), py::arg("max_depth"))

.def("set_scissor_rect",&pywgpu::RenderPassEncoder::SetScissorRect
, py::arg("x"), py::arg("y"), py::arg("width"), py::arg("height"))

.def("set_vertex_buffer",&pywgpu::RenderPassEncoder::SetVertexBuffer
, py::arg("slot"), py::arg("buffer"), py::arg("offset") = 0, py::arg("size") = kWholeSize)

.def("set_index_buffer",&pywgpu::RenderPassEncoder::SetIndexBuffer
, py::arg("buffer"), py::arg("format"), py::arg("offset") = 0, py::arg("size") = kWholeSize)

.def("begin_occlusion_query",&pywgpu::RenderPassEncoder::BeginOcclusionQuery
, py::arg("query_index"))

.def("end_occlusion_query",&pywgpu::RenderPassEncoder::EndOcclusionQuery
)

.def("write_timestamp",&pywgpu::RenderPassEncoder::WriteTimestamp
, py::arg("query_set"), py::arg("query_index"))

.def("pixel_local_storage_barrier",&pywgpu::RenderPassEncoder::PixelLocalStorageBarrier
)

.def("end",&pywgpu::RenderPassEncoder::End
)

.def("set_label",&pywgpu::RenderPassEncoder::SetLabel
, py::arg("label"))

.def("set_immediate_data",[](pywgpu::RenderPassEncoder& self, uint32_t offset, py::buffer data) {
    try {
        py::buffer_info dataInfo = data.request();
        void const* _data = (void const*)dataInfo.ptr;
        auto size = ((dataInfo.size * dataInfo.itemsize) + 3) & ~size_t(3);
        
        return self.SetImmediateData(offset, _data, size);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("offset"), py::arg("data"))

;

py::class_<RenderPipeline> _RenderPipeline(m, "RenderPipeline");
registry.on(m, "RenderPipeline", _RenderPipeline);

_RenderPipeline
.def("get_bind_group_layout",&pywgpu::RenderPipeline::GetBindGroupLayout
, py::arg("group_index"))

.def("set_label",&pywgpu::RenderPipeline::SetLabel
, py::arg("label"))

;

py::class_<Sampler> _Sampler(m, "Sampler");
registry.on(m, "Sampler", _Sampler);

_Sampler
.def("set_label",&pywgpu::Sampler::SetLabel
, py::arg("label"))

;

py::class_<ShaderModule> _ShaderModule(m, "ShaderModule");
registry.on(m, "ShaderModule", _ShaderModule);

_ShaderModule
.def("_get_compilation_info",&pywgpu::ShaderModule::GetCompilationInfo
, py::arg("callback_info"))

.def("set_label",&pywgpu::ShaderModule::SetLabel
, py::arg("label"))

;

py::class_<Surface> _Surface(m, "Surface");
registry.on(m, "Surface", _Surface);

_Surface
.def("configure",[](pywgpu::Surface& self, py::handle config) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::SurfaceConfiguration const* _config = Builder<SurfaceConfiguration>(ctx).build(config);
        
        return self.Configure(_config);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("config"))

.def("get_capabilities",&pywgpu::Surface::GetCapabilities
, py::arg("adapter"), py::arg("capabilities"))

.def("get_current_texture",&pywgpu::Surface::GetCurrentTexture
, py::arg("surface_texture"))

.def("present",&pywgpu::Surface::Present
)

.def("unconfigure",&pywgpu::Surface::Unconfigure
)

.def("set_label",&pywgpu::Surface::SetLabel
, py::arg("label"))

;

py::class_<Texture> _Texture(m, "Texture");
registry.on(m, "Texture", _Texture);

_Texture
.def("create_view",[](pywgpu::Texture& self, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::TextureViewDescriptor const* _descriptor = Builder<TextureViewDescriptor>(ctx).build(descriptor);
        
        return self.CreateView(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor") = nullptr)

.def("create_error_view",[](pywgpu::Texture& self, py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::TextureViewDescriptor const* _descriptor = Builder<TextureViewDescriptor>(ctx).build(descriptor);
        
        return self.CreateErrorView(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor") = nullptr)

.def("set_label",&pywgpu::Texture::SetLabel
, py::arg("label"))

.def("get_width",&pywgpu::Texture::GetWidth
)

.def("get_height",&pywgpu::Texture::GetHeight
)

.def("get_depth_or_array_layers",&pywgpu::Texture::GetDepthOrArrayLayers
)

.def("get_mip_level_count",&pywgpu::Texture::GetMipLevelCount
)

.def("get_sample_count",&pywgpu::Texture::GetSampleCount
)

.def("get_dimension",&pywgpu::Texture::GetDimension
)

.def("get_format",&pywgpu::Texture::GetFormat
)

.def("get_usage",&pywgpu::Texture::GetUsage
)

.def("destroy",&pywgpu::Texture::Destroy
)

;

py::class_<TextureView> _TextureView(m, "TextureView");
registry.on(m, "TextureView", _TextureView);

_TextureView
.def("set_label",&pywgpu::TextureView::SetLabel
, py::arg("label"))

;

m.def("create_instance",[](py::handle descriptor) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::InstanceDescriptor const* _descriptor = Builder<InstanceDescriptor>(ctx).build(descriptor);
        
        return CreateInstance(_descriptor);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("descriptor") = nullptr)

;

m.def("get_instance_capabilities",[](py::handle capabilities) {
    try {
        
        LinearAlloc la{};
        BuildCtx ctx{la};
        
        pywgpu::InstanceCapabilities * _capabilities = Builder<InstanceCapabilities>(ctx).build(capabilities);
        
        return GetInstanceCapabilities(_capabilities);
    
    } catch (const py::error_already_set& e) {
        // propagate Python-side exception with stack
        throw;
    } catch (const std::exception& e) {
        fprintf(stderr, "C++ exception what(): '%s'\n", e.what());
        PyErr_SetString(PyExc_RuntimeError, e.what());
        throw py::error_already_set();
    }
    
}
, py::arg("capabilities"))

;


}