#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/operators.h>
#include <pybind11/stl.h>

#include <cxbind/cxbind.h>
#include <crunge/wgpu/pywgpu.h>
#include <crunge/wgpu/crunge-wgpu.h>
#include <crunge/wgpu/conversions.h>

namespace py = pybind11;

using namespace pywgpu;

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
    

py::class_<Adapter> _Adapter(m, "Adapter");
registry.on(m, "Adapter", _Adapter);

_Adapter
    .def("get_instance",&pywgpu::Adapter::GetInstance
        , py::return_value_policy::automatic_reference)
        
    .def("get_limits",&pywgpu::Adapter::GetLimits
        , py::arg("limits")
        , py::return_value_policy::automatic_reference)
        
    .def("get_info",&pywgpu::Adapter::GetInfo
        , py::arg("info")
        , py::return_value_policy::automatic_reference)
        
    .def("has_feature",&pywgpu::Adapter::HasFeature
        , py::arg("feature")
        , py::return_value_policy::automatic_reference)
        
    .def("get_features",&pywgpu::Adapter::GetFeatures
        , py::arg("features")
        , py::return_value_policy::automatic_reference)
        
    .def("_request_device",&pywgpu::Adapter::RequestDevice
        , py::arg("options"), py::arg("callback_info")
        , py::return_value_policy::automatic_reference)
        
    .def("create_device",&pywgpu::Adapter::CreateDevice
        , py::arg("descriptor") = nullptr
        , py::return_value_policy::automatic_reference)
        
    .def("get_format_capabilities",&pywgpu::Adapter::GetFormatCapabilities
        , py::arg("format"), py::arg("capabilities")
        , py::return_value_policy::automatic_reference)
        
    ;

py::class_<BindGroup> _BindGroup(m, "BindGroup");
registry.on(m, "BindGroup", _BindGroup);

_BindGroup
    .def("set_label",&pywgpu::BindGroup::SetLabel
        , py::arg("label")
        , py::return_value_policy::automatic_reference)
        
    ;

py::class_<BindGroupLayout> _BindGroupLayout(m, "BindGroupLayout");
registry.on(m, "BindGroupLayout", _BindGroupLayout);

_BindGroupLayout
    .def("set_label",&pywgpu::BindGroupLayout::SetLabel
        , py::arg("label")
        , py::return_value_policy::automatic_reference)
        
    ;

py::class_<Buffer> _Buffer(m, "Buffer");
registry.on(m, "Buffer", _Buffer);

_Buffer
    .def("_map_async",&pywgpu::Buffer::MapAsync
        , py::arg("mode"), py::arg("offset"), py::arg("size"), py::arg("callback_info")
        , py::return_value_policy::automatic_reference)
        
    .def("get_mapped_range",&pywgpu::Buffer::GetMappedRange
        , py::arg("offset") = 0, py::arg("size") = kWholeMapSize
        , py::return_value_policy::automatic_reference)
        
    .def("get_const_mapped_range",&pywgpu::Buffer::GetConstMappedRange
        , py::arg("offset") = 0, py::arg("size") = kWholeMapSize
        , py::return_value_policy::automatic_reference)
        
    .def("write_mapped_range",[](pywgpu::Buffer& self, size_t offset, py::buffer data) {
        py::buffer_info dataInfo = data.request();
        void const* _data = (void const*)dataInfo.ptr;
        auto size = dataInfo.size * dataInfo.itemsize;
        
        return self.WriteMappedRange(offset, _data, size);
        }
        , py::arg("offset"), py::arg("data")
        , py::return_value_policy::automatic_reference)
        
    .def("read_mapped_range",[](pywgpu::Buffer& self, size_t offset, py::buffer data) {
        py::buffer_info dataInfo = data.request();
        void * _data = (void *)dataInfo.ptr;
        auto size = dataInfo.size * dataInfo.itemsize;
        
        return self.ReadMappedRange(offset, _data, size);
        }
        , py::arg("offset"), py::arg("data")
        , py::return_value_policy::automatic_reference)
        
    .def("set_label",&pywgpu::Buffer::SetLabel
        , py::arg("label")
        , py::return_value_policy::automatic_reference)
        
    .def("get_usage",&pywgpu::Buffer::GetUsage
        , py::return_value_policy::automatic_reference)
        
    .def("get_size",&pywgpu::Buffer::GetSize
        , py::return_value_policy::automatic_reference)
        
    .def("get_map_state",&pywgpu::Buffer::GetMapState
        , py::return_value_policy::automatic_reference)
        
    .def("unmap",&pywgpu::Buffer::Unmap
        , py::return_value_policy::automatic_reference)
        
    .def("destroy",&pywgpu::Buffer::Destroy
        , py::return_value_policy::automatic_reference)
        
    ;

py::class_<CommandBuffer> _CommandBuffer(m, "CommandBuffer");
registry.on(m, "CommandBuffer", _CommandBuffer);

_CommandBuffer
    .def("set_label",&pywgpu::CommandBuffer::SetLabel
        , py::arg("label")
        , py::return_value_policy::automatic_reference)
        
    ;

py::class_<CommandEncoder> _CommandEncoder(m, "CommandEncoder");
registry.on(m, "CommandEncoder", _CommandEncoder);

_CommandEncoder
    .def("finish",&pywgpu::CommandEncoder::Finish
        , py::arg("descriptor") = nullptr
        , py::return_value_policy::automatic_reference)
        
    .def("begin_compute_pass",&pywgpu::CommandEncoder::BeginComputePass
        , py::arg("descriptor") = nullptr
        , py::return_value_policy::automatic_reference)
        
    .def("begin_render_pass",&pywgpu::CommandEncoder::BeginRenderPass
        , py::arg("descriptor")
        , py::return_value_policy::automatic_reference)
        
    .def("copy_buffer_to_buffer",&pywgpu::CommandEncoder::CopyBufferToBuffer
        , py::arg("source"), py::arg("source_offset"), py::arg("destination"), py::arg("destination_offset"), py::arg("size")
        , py::return_value_policy::automatic_reference)
        
    .def("copy_buffer_to_texture",&pywgpu::CommandEncoder::CopyBufferToTexture
        , py::arg("source"), py::arg("destination"), py::arg("copy_size")
        , py::return_value_policy::automatic_reference)
        
    .def("copy_texture_to_buffer",&pywgpu::CommandEncoder::CopyTextureToBuffer
        , py::arg("source"), py::arg("destination"), py::arg("copy_size")
        , py::return_value_policy::automatic_reference)
        
    .def("copy_texture_to_texture",&pywgpu::CommandEncoder::CopyTextureToTexture
        , py::arg("source"), py::arg("destination"), py::arg("copy_size")
        , py::return_value_policy::automatic_reference)
        
    .def("clear_buffer",&pywgpu::CommandEncoder::ClearBuffer
        , py::arg("buffer"), py::arg("offset") = 0, py::arg("size") = kWholeSize
        , py::return_value_policy::automatic_reference)
        
    .def("inject_validation_error",&pywgpu::CommandEncoder::InjectValidationError
        , py::arg("message")
        , py::return_value_policy::automatic_reference)
        
    .def("insert_debug_marker",&pywgpu::CommandEncoder::InsertDebugMarker
        , py::arg("marker_label")
        , py::return_value_policy::automatic_reference)
        
    .def("pop_debug_group",&pywgpu::CommandEncoder::PopDebugGroup
        , py::return_value_policy::automatic_reference)
        
    .def("push_debug_group",&pywgpu::CommandEncoder::PushDebugGroup
        , py::arg("group_label")
        , py::return_value_policy::automatic_reference)
        
    .def("resolve_query_set",&pywgpu::CommandEncoder::ResolveQuerySet
        , py::arg("query_set"), py::arg("first_query"), py::arg("query_count"), py::arg("destination"), py::arg("destination_offset")
        , py::return_value_policy::automatic_reference)
        
    .def("write_buffer",[](pywgpu::CommandEncoder& self, Buffer buffer, uint64_t bufferOffset, py::buffer data) {
        py::buffer_info dataInfo = data.request();
        uint8_t const* _data = (uint8_t const*)dataInfo.ptr;
        auto size = dataInfo.size * dataInfo.itemsize;
        
        return self.WriteBuffer(buffer, bufferOffset, _data, size);
        }
        , py::arg("buffer"), py::arg("buffer_offset"), py::arg("data")
        , py::return_value_policy::automatic_reference)
        
    .def("write_timestamp",&pywgpu::CommandEncoder::WriteTimestamp
        , py::arg("query_set"), py::arg("query_index")
        , py::return_value_policy::automatic_reference)
        
    .def("set_label",&pywgpu::CommandEncoder::SetLabel
        , py::arg("label")
        , py::return_value_policy::automatic_reference)
        
    ;

py::class_<ComputePassEncoder> _ComputePassEncoder(m, "ComputePassEncoder");
registry.on(m, "ComputePassEncoder", _ComputePassEncoder);

_ComputePassEncoder
    .def("insert_debug_marker",&pywgpu::ComputePassEncoder::InsertDebugMarker
        , py::arg("marker_label")
        , py::return_value_policy::automatic_reference)
        
    .def("pop_debug_group",&pywgpu::ComputePassEncoder::PopDebugGroup
        , py::return_value_policy::automatic_reference)
        
    .def("push_debug_group",&pywgpu::ComputePassEncoder::PushDebugGroup
        , py::arg("group_label")
        , py::return_value_policy::automatic_reference)
        
    .def("set_pipeline",&pywgpu::ComputePassEncoder::SetPipeline
        , py::arg("pipeline")
        , py::return_value_policy::automatic_reference)
        
    .def("set_bind_group",[](pywgpu::ComputePassEncoder& self, uint32_t groupIndex, BindGroup group, std::optional<py::buffer> dynamicOffsets) {
        py::buffer_info dynamicOffsetsInfo = dynamicOffsets.has_value() ? dynamicOffsets.value().request() : py::buffer_info();
        uint32_t const* _dynamicOffsets = (uint32_t const*)dynamicOffsetsInfo.ptr;
        auto dynamicOffsetCount = dynamicOffsetsInfo.size * dynamicOffsetsInfo.itemsize;
        
        return self.SetBindGroup(groupIndex, group, dynamicOffsetCount, _dynamicOffsets);
        }
        , py::arg("group_index"), py::arg("group"), py::arg("dynamic_offsets") = nullptr
        , py::return_value_policy::automatic_reference)
        
    .def("write_timestamp",&pywgpu::ComputePassEncoder::WriteTimestamp
        , py::arg("query_set"), py::arg("query_index")
        , py::return_value_policy::automatic_reference)
        
    .def("dispatch_workgroups",&pywgpu::ComputePassEncoder::DispatchWorkgroups
        , py::arg("workgroupCountX"), py::arg("workgroupCountY") = 1, py::arg("workgroupCountZ") = 1
        , py::return_value_policy::automatic_reference)
        
    .def("dispatch_workgroups_indirect",&pywgpu::ComputePassEncoder::DispatchWorkgroupsIndirect
        , py::arg("indirect_buffer"), py::arg("indirect_offset")
        , py::return_value_policy::automatic_reference)
        
    .def("end",&pywgpu::ComputePassEncoder::End
        , py::return_value_policy::automatic_reference)
        
    .def("set_label",&pywgpu::ComputePassEncoder::SetLabel
        , py::arg("label")
        , py::return_value_policy::automatic_reference)
        
    .def("set_immediate_data",[](pywgpu::ComputePassEncoder& self, uint32_t offset, py::buffer data) {
        py::buffer_info dataInfo = data.request();
        void const* _data = (void const*)dataInfo.ptr;
        auto size = dataInfo.size * dataInfo.itemsize;
        
        return self.SetImmediateData(offset, _data, size);
        }
        , py::arg("offset"), py::arg("data")
        , py::return_value_policy::automatic_reference)
        
    ;

py::class_<ComputePipeline> _ComputePipeline(m, "ComputePipeline");
registry.on(m, "ComputePipeline", _ComputePipeline);

_ComputePipeline
    .def("get_bind_group_layout",&pywgpu::ComputePipeline::GetBindGroupLayout
        , py::arg("group_index")
        , py::return_value_policy::automatic_reference)
        
    .def("set_label",&pywgpu::ComputePipeline::SetLabel
        , py::arg("label")
        , py::return_value_policy::automatic_reference)
        
    ;

py::class_<Device> _Device(m, "Device");
registry.on(m, "Device", _Device);

_Device
    .def("create_bind_group",&pywgpu::Device::CreateBindGroup
        , py::arg("descriptor")
        , py::return_value_policy::automatic_reference)
        
    .def("create_bind_group_layout",&pywgpu::Device::CreateBindGroupLayout
        , py::arg("descriptor")
        , py::return_value_policy::automatic_reference)
        
    .def("create_buffer",&pywgpu::Device::CreateBuffer
        , py::arg("descriptor")
        , py::return_value_policy::automatic_reference)
        
    .def("create_error_buffer",&pywgpu::Device::CreateErrorBuffer
        , py::arg("descriptor")
        , py::return_value_policy::automatic_reference)
        
    .def("create_command_encoder",&pywgpu::Device::CreateCommandEncoder
        , py::arg("descriptor") = nullptr
        , py::return_value_policy::automatic_reference)
        
    .def("create_compute_pipeline",&pywgpu::Device::CreateComputePipeline
        , py::arg("descriptor")
        , py::return_value_policy::automatic_reference)
        
    .def("_create_compute_pipeline_async",&pywgpu::Device::CreateComputePipelineAsync
        , py::arg("descriptor"), py::arg("callback_info")
        , py::return_value_policy::automatic_reference)
        
    .def("create_external_texture",&pywgpu::Device::CreateExternalTexture
        , py::arg("external_texture_descriptor")
        , py::return_value_policy::automatic_reference)
        
    .def("create_error_external_texture",&pywgpu::Device::CreateErrorExternalTexture
        , py::return_value_policy::automatic_reference)
        
    .def("create_pipeline_layout",&pywgpu::Device::CreatePipelineLayout
        , py::arg("descriptor")
        , py::return_value_policy::automatic_reference)
        
    .def("create_query_set",&pywgpu::Device::CreateQuerySet
        , py::arg("descriptor")
        , py::return_value_policy::automatic_reference)
        
    .def("_create_render_pipeline_async",&pywgpu::Device::CreateRenderPipelineAsync
        , py::arg("descriptor"), py::arg("callback_info")
        , py::return_value_policy::automatic_reference)
        
    .def("create_render_bundle_encoder",&pywgpu::Device::CreateRenderBundleEncoder
        , py::arg("descriptor")
        , py::return_value_policy::automatic_reference)
        
    .def("create_render_pipeline",&pywgpu::Device::CreateRenderPipeline
        , py::arg("descriptor")
        , py::return_value_policy::automatic_reference)
        
    .def("create_sampler",&pywgpu::Device::CreateSampler
        , py::arg("descriptor") = nullptr
        , py::return_value_policy::automatic_reference)
        
    .def("create_shader_module",&pywgpu::Device::CreateShaderModule
        , py::arg("descriptor")
        , py::return_value_policy::automatic_reference)
        
    .def("create_error_shader_module",&pywgpu::Device::CreateErrorShaderModule
        , py::arg("descriptor"), py::arg("error_message")
        , py::return_value_policy::automatic_reference)
        
    .def("create_texture",&pywgpu::Device::CreateTexture
        , py::arg("descriptor")
        , py::return_value_policy::automatic_reference)
        
    .def("import_shared_buffer_memory",&pywgpu::Device::ImportSharedBufferMemory
        , py::arg("descriptor")
        , py::return_value_policy::automatic_reference)
        
    .def("import_shared_texture_memory",&pywgpu::Device::ImportSharedTextureMemory
        , py::arg("descriptor")
        , py::return_value_policy::automatic_reference)
        
    .def("import_shared_fence",&pywgpu::Device::ImportSharedFence
        , py::arg("descriptor")
        , py::return_value_policy::automatic_reference)
        
    .def("create_error_texture",&pywgpu::Device::CreateErrorTexture
        , py::arg("descriptor")
        , py::return_value_policy::automatic_reference)
        
    .def("destroy",&pywgpu::Device::Destroy
        , py::return_value_policy::automatic_reference)
        
    .def("get_a_hardware_buffer_properties",&pywgpu::Device::GetAHardwareBufferProperties
        , py::arg("handle"), py::arg("properties")
        , py::return_value_policy::automatic_reference)
        
    .def("get_limits",&pywgpu::Device::GetLimits
        , py::arg("limits")
        , py::return_value_policy::automatic_reference)
        
    .def("_get_lost_future",&pywgpu::Device::GetLostFuture
        , py::return_value_policy::automatic_reference)
        
    .def("has_feature",&pywgpu::Device::HasFeature
        , py::arg("feature")
        , py::return_value_policy::automatic_reference)
        
    .def("get_features",&pywgpu::Device::GetFeatures
        , py::arg("features")
        , py::return_value_policy::automatic_reference)
        
    .def("get_adapter_info",&pywgpu::Device::GetAdapterInfo
        , py::arg("adapter_info")
        , py::return_value_policy::automatic_reference)
        
    .def("get_adapter",&pywgpu::Device::GetAdapter
        , py::return_value_policy::automatic_reference)
        
    .def("get_queue",&pywgpu::Device::GetQueue
        , py::return_value_policy::automatic_reference)
        
    .def("inject_error",&pywgpu::Device::InjectError
        , py::arg("type"), py::arg("message")
        , py::return_value_policy::automatic_reference)
        
    .def("force_loss",&pywgpu::Device::ForceLoss
        , py::arg("type"), py::arg("message")
        , py::return_value_policy::automatic_reference)
        
    .def("tick",&pywgpu::Device::Tick
        , py::return_value_policy::automatic_reference)
        
    .def("set_logging_callback",&pywgpu::Device::SetLoggingCallback
        , py::arg("callback_info")
        , py::return_value_policy::automatic_reference)
        
    .def("push_error_scope",&pywgpu::Device::PushErrorScope
        , py::arg("filter")
        , py::return_value_policy::automatic_reference)
        
    .def("_pop_error_scope",&pywgpu::Device::PopErrorScope
        , py::arg("callback_info")
        , py::return_value_policy::automatic_reference)
        
    .def("set_label",&pywgpu::Device::SetLabel
        , py::arg("label")
        , py::return_value_policy::automatic_reference)
        
    .def("validate_texture_descriptor",&pywgpu::Device::ValidateTextureDescriptor
        , py::arg("descriptor")
        , py::return_value_policy::automatic_reference)
        
    ;

py::class_<ExternalTexture> _ExternalTexture(m, "ExternalTexture");
registry.on(m, "ExternalTexture", _ExternalTexture);

_ExternalTexture
    .def("set_label",&pywgpu::ExternalTexture::SetLabel
        , py::arg("label")
        , py::return_value_policy::automatic_reference)
        
    .def("destroy",&pywgpu::ExternalTexture::Destroy
        , py::return_value_policy::automatic_reference)
        
    .def("expire",&pywgpu::ExternalTexture::Expire
        , py::return_value_policy::automatic_reference)
        
    .def("refresh",&pywgpu::ExternalTexture::Refresh
        , py::return_value_policy::automatic_reference)
        
    ;

py::class_<SharedBufferMemory> _SharedBufferMemory(m, "SharedBufferMemory");
registry.on(m, "SharedBufferMemory", _SharedBufferMemory);

_SharedBufferMemory
    .def("set_label",&pywgpu::SharedBufferMemory::SetLabel
        , py::arg("label")
        , py::return_value_policy::automatic_reference)
        
    .def("get_properties",&pywgpu::SharedBufferMemory::GetProperties
        , py::arg("properties")
        , py::return_value_policy::automatic_reference)
        
    .def("create_buffer",&pywgpu::SharedBufferMemory::CreateBuffer
        , py::arg("descriptor") = nullptr
        , py::return_value_policy::automatic_reference)
        
    .def("begin_access",&pywgpu::SharedBufferMemory::BeginAccess
        , py::arg("buffer"), py::arg("descriptor")
        , py::return_value_policy::automatic_reference)
        
    .def("end_access",&pywgpu::SharedBufferMemory::EndAccess
        , py::arg("buffer"), py::arg("descriptor")
        , py::return_value_policy::automatic_reference)
        
    .def("is_device_lost",&pywgpu::SharedBufferMemory::IsDeviceLost
        , py::return_value_policy::automatic_reference)
        
    ;

py::class_<SharedTextureMemory> _SharedTextureMemory(m, "SharedTextureMemory");
registry.on(m, "SharedTextureMemory", _SharedTextureMemory);

_SharedTextureMemory
    .def("set_label",&pywgpu::SharedTextureMemory::SetLabel
        , py::arg("label")
        , py::return_value_policy::automatic_reference)
        
    .def("get_properties",&pywgpu::SharedTextureMemory::GetProperties
        , py::arg("properties")
        , py::return_value_policy::automatic_reference)
        
    .def("create_texture",&pywgpu::SharedTextureMemory::CreateTexture
        , py::arg("descriptor") = nullptr
        , py::return_value_policy::automatic_reference)
        
    .def("begin_access",&pywgpu::SharedTextureMemory::BeginAccess
        , py::arg("texture"), py::arg("descriptor")
        , py::return_value_policy::automatic_reference)
        
    .def("end_access",&pywgpu::SharedTextureMemory::EndAccess
        , py::arg("texture"), py::arg("descriptor")
        , py::return_value_policy::automatic_reference)
        
    .def("is_device_lost",&pywgpu::SharedTextureMemory::IsDeviceLost
        , py::return_value_policy::automatic_reference)
        
    ;

py::class_<SharedFence> _SharedFence(m, "SharedFence");
registry.on(m, "SharedFence", _SharedFence);

_SharedFence
    .def("export_info",&pywgpu::SharedFence::ExportInfo
        , py::arg("info")
        , py::return_value_policy::automatic_reference)
        
    ;

py::class_<Instance> _Instance(m, "Instance");
registry.on(m, "Instance", _Instance);

_Instance
    .def("create_surface",&pywgpu::Instance::CreateSurface
        , py::arg("descriptor")
        , py::return_value_policy::automatic_reference)
        
    .def("process_events",&pywgpu::Instance::ProcessEvents
        , py::return_value_policy::automatic_reference)
        
    .def("wait_any",[](pywgpu::Instance& self, std::vector<pywgpu::FutureWaitInfo> futures, uint64_t timeoutNS) {
        pywgpu::FutureWaitInfo * _futures = (pywgpu::FutureWaitInfo *)futures.data();
        auto futureCount = futures.size();
        
        return self.WaitAny(futureCount, _futures, timeoutNS);
        }
        , py::arg("futures"), py::arg("timeout_NS")
        , py::return_value_policy::automatic_reference)
        
    .def("_request_adapter",&pywgpu::Instance::RequestAdapter
        , py::arg("options"), py::arg("callback_info")
        , py::return_value_policy::automatic_reference)
        
    .def("has_WGSL_language_feature",&pywgpu::Instance::HasWGSLLanguageFeature
        , py::arg("feature")
        , py::return_value_policy::automatic_reference)
        
    .def("get_WGSL_language_features",&pywgpu::Instance::GetWGSLLanguageFeatures
        , py::arg("features")
        , py::return_value_policy::automatic_reference)
        
    ;

py::class_<PipelineLayout> _PipelineLayout(m, "PipelineLayout");
registry.on(m, "PipelineLayout", _PipelineLayout);

_PipelineLayout
    .def("set_label",&pywgpu::PipelineLayout::SetLabel
        , py::arg("label")
        , py::return_value_policy::automatic_reference)
        
    ;

py::class_<QuerySet> _QuerySet(m, "QuerySet");
registry.on(m, "QuerySet", _QuerySet);

_QuerySet
    .def("set_label",&pywgpu::QuerySet::SetLabel
        , py::arg("label")
        , py::return_value_policy::automatic_reference)
        
    .def("get_type",&pywgpu::QuerySet::GetType
        , py::return_value_policy::automatic_reference)
        
    .def("get_count",&pywgpu::QuerySet::GetCount
        , py::return_value_policy::automatic_reference)
        
    .def("destroy",&pywgpu::QuerySet::Destroy
        , py::return_value_policy::automatic_reference)
        
    ;

py::class_<Queue> _Queue(m, "Queue");
registry.on(m, "Queue", _Queue);

_Queue
    .def("submit",[](pywgpu::Queue& self, std::vector<pywgpu::CommandBuffer> commands) {
        pywgpu::CommandBuffer const* _commands = (pywgpu::CommandBuffer const*)commands.data();
        auto commandCount = commands.size();
        
        return self.Submit(commandCount, _commands);
        }
        , py::arg("commands")
        , py::return_value_policy::automatic_reference)
        
    .def("_on_submitted_work_done",&pywgpu::Queue::OnSubmittedWorkDone
        , py::arg("callback_info")
        , py::return_value_policy::automatic_reference)
        
    .def("write_buffer",[](pywgpu::Queue& self, Buffer buffer, uint64_t bufferOffset, py::buffer data) {
        py::buffer_info dataInfo = data.request();
        void const* _data = (void const*)dataInfo.ptr;
        auto size = dataInfo.size * dataInfo.itemsize;
        
        return self.WriteBuffer(buffer, bufferOffset, _data, size);
        }
        , py::arg("buffer"), py::arg("buffer_offset"), py::arg("data")
        , py::return_value_policy::automatic_reference)
        
    .def("write_texture",[](pywgpu::Queue& self, TexelCopyTextureInfo const * destination, py::buffer data, TexelCopyBufferLayout const * dataLayout, Extent3D const * writeSize) {
        py::buffer_info dataInfo = data.request();
        void const* _data = (void const*)dataInfo.ptr;
        auto dataSize = dataInfo.size * dataInfo.itemsize;
        
        return self.WriteTexture(destination, _data, dataSize, dataLayout, writeSize);
        }
        , py::arg("destination"), py::arg("data"), py::arg("data_layout"), py::arg("write_size")
        , py::return_value_policy::automatic_reference)
        
    .def("copy_texture_for_browser",&pywgpu::Queue::CopyTextureForBrowser
        , py::arg("source"), py::arg("destination"), py::arg("copy_size"), py::arg("options")
        , py::return_value_policy::automatic_reference)
        
    .def("copy_external_texture_for_browser",&pywgpu::Queue::CopyExternalTextureForBrowser
        , py::arg("source"), py::arg("destination"), py::arg("copy_size"), py::arg("options")
        , py::return_value_policy::automatic_reference)
        
    .def("set_label",&pywgpu::Queue::SetLabel
        , py::arg("label")
        , py::return_value_policy::automatic_reference)
        
    ;

py::class_<RenderBundle> _RenderBundle(m, "RenderBundle");
registry.on(m, "RenderBundle", _RenderBundle);

_RenderBundle
    .def("set_label",&pywgpu::RenderBundle::SetLabel
        , py::arg("label")
        , py::return_value_policy::automatic_reference)
        
    ;

py::class_<RenderBundleEncoder> _RenderBundleEncoder(m, "RenderBundleEncoder");
registry.on(m, "RenderBundleEncoder", _RenderBundleEncoder);

_RenderBundleEncoder
    .def("set_pipeline",&pywgpu::RenderBundleEncoder::SetPipeline
        , py::arg("pipeline")
        , py::return_value_policy::automatic_reference)
        
    .def("set_bind_group",[](pywgpu::RenderBundleEncoder& self, uint32_t groupIndex, BindGroup group, std::optional<py::buffer> dynamicOffsets) {
        py::buffer_info dynamicOffsetsInfo = dynamicOffsets.has_value() ? dynamicOffsets.value().request() : py::buffer_info();
        uint32_t const* _dynamicOffsets = (uint32_t const*)dynamicOffsetsInfo.ptr;
        auto dynamicOffsetCount = dynamicOffsetsInfo.size * dynamicOffsetsInfo.itemsize;
        
        return self.SetBindGroup(groupIndex, group, dynamicOffsetCount, _dynamicOffsets);
        }
        , py::arg("group_index"), py::arg("group"), py::arg("dynamic_offsets") = nullptr
        , py::return_value_policy::automatic_reference)
        
    .def("draw",&pywgpu::RenderBundleEncoder::Draw
        , py::arg("vertex_count"), py::arg("instance_count") = 1, py::arg("first_vertex") = 0, py::arg("first_instance") = 0
        , py::return_value_policy::automatic_reference)
        
    .def("draw_indexed",&pywgpu::RenderBundleEncoder::DrawIndexed
        , py::arg("index_count"), py::arg("instance_count") = 1, py::arg("first_index") = 0, py::arg("base_vertex") = 0, py::arg("first_instance") = 0
        , py::return_value_policy::automatic_reference)
        
    .def("draw_indirect",&pywgpu::RenderBundleEncoder::DrawIndirect
        , py::arg("indirect_buffer"), py::arg("indirect_offset")
        , py::return_value_policy::automatic_reference)
        
    .def("draw_indexed_indirect",&pywgpu::RenderBundleEncoder::DrawIndexedIndirect
        , py::arg("indirect_buffer"), py::arg("indirect_offset")
        , py::return_value_policy::automatic_reference)
        
    .def("insert_debug_marker",&pywgpu::RenderBundleEncoder::InsertDebugMarker
        , py::arg("marker_label")
        , py::return_value_policy::automatic_reference)
        
    .def("pop_debug_group",&pywgpu::RenderBundleEncoder::PopDebugGroup
        , py::return_value_policy::automatic_reference)
        
    .def("push_debug_group",&pywgpu::RenderBundleEncoder::PushDebugGroup
        , py::arg("group_label")
        , py::return_value_policy::automatic_reference)
        
    .def("set_vertex_buffer",&pywgpu::RenderBundleEncoder::SetVertexBuffer
        , py::arg("slot"), py::arg("buffer"), py::arg("offset") = 0, py::arg("size") = kWholeSize
        , py::return_value_policy::automatic_reference)
        
    .def("set_index_buffer",&pywgpu::RenderBundleEncoder::SetIndexBuffer
        , py::arg("buffer"), py::arg("format"), py::arg("offset") = 0, py::arg("size") = kWholeSize
        , py::return_value_policy::automatic_reference)
        
    .def("finish",&pywgpu::RenderBundleEncoder::Finish
        , py::arg("descriptor") = nullptr
        , py::return_value_policy::automatic_reference)
        
    .def("set_label",&pywgpu::RenderBundleEncoder::SetLabel
        , py::arg("label")
        , py::return_value_policy::automatic_reference)
        
    .def("set_immediate_data",[](pywgpu::RenderBundleEncoder& self, uint32_t offset, py::buffer data) {
        py::buffer_info dataInfo = data.request();
        void const* _data = (void const*)dataInfo.ptr;
        auto size = dataInfo.size * dataInfo.itemsize;
        
        return self.SetImmediateData(offset, _data, size);
        }
        , py::arg("offset"), py::arg("data")
        , py::return_value_policy::automatic_reference)
        
    ;

py::class_<RenderPassEncoder> _RenderPassEncoder(m, "RenderPassEncoder");
registry.on(m, "RenderPassEncoder", _RenderPassEncoder);

_RenderPassEncoder
    .def("set_pipeline",&pywgpu::RenderPassEncoder::SetPipeline
        , py::arg("pipeline")
        , py::return_value_policy::automatic_reference)
        
    .def("set_bind_group",[](pywgpu::RenderPassEncoder& self, uint32_t groupIndex, BindGroup group, std::optional<py::buffer> dynamicOffsets) {
        py::buffer_info dynamicOffsetsInfo = dynamicOffsets.has_value() ? dynamicOffsets.value().request() : py::buffer_info();
        uint32_t const* _dynamicOffsets = (uint32_t const*)dynamicOffsetsInfo.ptr;
        auto dynamicOffsetCount = dynamicOffsetsInfo.size * dynamicOffsetsInfo.itemsize;
        
        return self.SetBindGroup(groupIndex, group, dynamicOffsetCount, _dynamicOffsets);
        }
        , py::arg("group_index"), py::arg("group"), py::arg("dynamic_offsets") = nullptr
        , py::return_value_policy::automatic_reference)
        
    .def("draw",&pywgpu::RenderPassEncoder::Draw
        , py::arg("vertex_count"), py::arg("instance_count") = 1, py::arg("first_vertex") = 0, py::arg("first_instance") = 0
        , py::return_value_policy::automatic_reference)
        
    .def("draw_indexed",&pywgpu::RenderPassEncoder::DrawIndexed
        , py::arg("index_count"), py::arg("instance_count") = 1, py::arg("first_index") = 0, py::arg("base_vertex") = 0, py::arg("first_instance") = 0
        , py::return_value_policy::automatic_reference)
        
    .def("draw_indirect",&pywgpu::RenderPassEncoder::DrawIndirect
        , py::arg("indirect_buffer"), py::arg("indirect_offset")
        , py::return_value_policy::automatic_reference)
        
    .def("draw_indexed_indirect",&pywgpu::RenderPassEncoder::DrawIndexedIndirect
        , py::arg("indirect_buffer"), py::arg("indirect_offset")
        , py::return_value_policy::automatic_reference)
        
    .def("multi_draw_indirect",&pywgpu::RenderPassEncoder::MultiDrawIndirect
        , py::arg("indirect_buffer"), py::arg("indirect_offset"), py::arg("max_draw_count"), py::arg("draw_count_buffer"), py::arg("draw_count_buffer_offset") = 0
        , py::return_value_policy::automatic_reference)
        
    .def("multi_draw_indexed_indirect",&pywgpu::RenderPassEncoder::MultiDrawIndexedIndirect
        , py::arg("indirect_buffer"), py::arg("indirect_offset"), py::arg("max_draw_count"), py::arg("draw_count_buffer"), py::arg("draw_count_buffer_offset") = 0
        , py::return_value_policy::automatic_reference)
        
    .def("execute_bundles",[](pywgpu::RenderPassEncoder& self, std::vector<pywgpu::RenderBundle> bundles) {
        pywgpu::RenderBundle const* _bundles = (pywgpu::RenderBundle const*)bundles.data();
        auto bundleCount = bundles.size();
        
        return self.ExecuteBundles(bundleCount, _bundles);
        }
        , py::arg("bundles")
        , py::return_value_policy::automatic_reference)
        
    .def("insert_debug_marker",&pywgpu::RenderPassEncoder::InsertDebugMarker
        , py::arg("marker_label")
        , py::return_value_policy::automatic_reference)
        
    .def("pop_debug_group",&pywgpu::RenderPassEncoder::PopDebugGroup
        , py::return_value_policy::automatic_reference)
        
    .def("push_debug_group",&pywgpu::RenderPassEncoder::PushDebugGroup
        , py::arg("group_label")
        , py::return_value_policy::automatic_reference)
        
    .def("set_stencil_reference",&pywgpu::RenderPassEncoder::SetStencilReference
        , py::arg("reference")
        , py::return_value_policy::automatic_reference)
        
    .def("set_blend_constant",&pywgpu::RenderPassEncoder::SetBlendConstant
        , py::arg("color")
        , py::return_value_policy::automatic_reference)
        
    .def("set_viewport",&pywgpu::RenderPassEncoder::SetViewport
        , py::arg("x"), py::arg("y"), py::arg("width"), py::arg("height"), py::arg("min_depth"), py::arg("max_depth")
        , py::return_value_policy::automatic_reference)
        
    .def("set_scissor_rect",&pywgpu::RenderPassEncoder::SetScissorRect
        , py::arg("x"), py::arg("y"), py::arg("width"), py::arg("height")
        , py::return_value_policy::automatic_reference)
        
    .def("set_vertex_buffer",&pywgpu::RenderPassEncoder::SetVertexBuffer
        , py::arg("slot"), py::arg("buffer"), py::arg("offset") = 0, py::arg("size") = kWholeSize
        , py::return_value_policy::automatic_reference)
        
    .def("set_index_buffer",&pywgpu::RenderPassEncoder::SetIndexBuffer
        , py::arg("buffer"), py::arg("format"), py::arg("offset") = 0, py::arg("size") = kWholeSize
        , py::return_value_policy::automatic_reference)
        
    .def("begin_occlusion_query",&pywgpu::RenderPassEncoder::BeginOcclusionQuery
        , py::arg("query_index")
        , py::return_value_policy::automatic_reference)
        
    .def("end_occlusion_query",&pywgpu::RenderPassEncoder::EndOcclusionQuery
        , py::return_value_policy::automatic_reference)
        
    .def("write_timestamp",&pywgpu::RenderPassEncoder::WriteTimestamp
        , py::arg("query_set"), py::arg("query_index")
        , py::return_value_policy::automatic_reference)
        
    .def("pixel_local_storage_barrier",&pywgpu::RenderPassEncoder::PixelLocalStorageBarrier
        , py::return_value_policy::automatic_reference)
        
    .def("end",&pywgpu::RenderPassEncoder::End
        , py::return_value_policy::automatic_reference)
        
    .def("set_label",&pywgpu::RenderPassEncoder::SetLabel
        , py::arg("label")
        , py::return_value_policy::automatic_reference)
        
    .def("set_immediate_data",[](pywgpu::RenderPassEncoder& self, uint32_t offset, py::buffer data) {
        py::buffer_info dataInfo = data.request();
        void const* _data = (void const*)dataInfo.ptr;
        auto size = dataInfo.size * dataInfo.itemsize;
        
        return self.SetImmediateData(offset, _data, size);
        }
        , py::arg("offset"), py::arg("data")
        , py::return_value_policy::automatic_reference)
        
    ;

py::class_<RenderPipeline> _RenderPipeline(m, "RenderPipeline");
registry.on(m, "RenderPipeline", _RenderPipeline);

_RenderPipeline
    .def("get_bind_group_layout",&pywgpu::RenderPipeline::GetBindGroupLayout
        , py::arg("group_index")
        , py::return_value_policy::automatic_reference)
        
    .def("set_label",&pywgpu::RenderPipeline::SetLabel
        , py::arg("label")
        , py::return_value_policy::automatic_reference)
        
    ;

py::class_<Sampler> _Sampler(m, "Sampler");
registry.on(m, "Sampler", _Sampler);

_Sampler
    .def("set_label",&pywgpu::Sampler::SetLabel
        , py::arg("label")
        , py::return_value_policy::automatic_reference)
        
    ;

py::class_<ShaderModule> _ShaderModule(m, "ShaderModule");
registry.on(m, "ShaderModule", _ShaderModule);

_ShaderModule
    .def("_get_compilation_info",&pywgpu::ShaderModule::GetCompilationInfo
        , py::arg("callback_info")
        , py::return_value_policy::automatic_reference)
        
    .def("set_label",&pywgpu::ShaderModule::SetLabel
        , py::arg("label")
        , py::return_value_policy::automatic_reference)
        
    ;

py::class_<Surface> _Surface(m, "Surface");
registry.on(m, "Surface", _Surface);

_Surface
    .def("configure",&pywgpu::Surface::Configure
        , py::arg("config")
        , py::return_value_policy::automatic_reference)
        
    .def("get_capabilities",&pywgpu::Surface::GetCapabilities
        , py::arg("adapter"), py::arg("capabilities")
        , py::return_value_policy::automatic_reference)
        
    .def("get_current_texture",&pywgpu::Surface::GetCurrentTexture
        , py::arg("surface_texture")
        , py::return_value_policy::automatic_reference)
        
    .def("present",&pywgpu::Surface::Present
        , py::return_value_policy::automatic_reference)
        
    .def("unconfigure",&pywgpu::Surface::Unconfigure
        , py::return_value_policy::automatic_reference)
        
    .def("set_label",&pywgpu::Surface::SetLabel
        , py::arg("label")
        , py::return_value_policy::automatic_reference)
        
    ;

py::class_<Texture> _Texture(m, "Texture");
registry.on(m, "Texture", _Texture);

_Texture
    .def("create_view",&pywgpu::Texture::CreateView
        , py::arg("descriptor") = nullptr
        , py::return_value_policy::automatic_reference)
        
    .def("create_error_view",&pywgpu::Texture::CreateErrorView
        , py::arg("descriptor") = nullptr
        , py::return_value_policy::automatic_reference)
        
    .def("set_label",&pywgpu::Texture::SetLabel
        , py::arg("label")
        , py::return_value_policy::automatic_reference)
        
    .def("get_width",&pywgpu::Texture::GetWidth
        , py::return_value_policy::automatic_reference)
        
    .def("get_height",&pywgpu::Texture::GetHeight
        , py::return_value_policy::automatic_reference)
        
    .def("get_depth_or_array_layers",&pywgpu::Texture::GetDepthOrArrayLayers
        , py::return_value_policy::automatic_reference)
        
    .def("get_mip_level_count",&pywgpu::Texture::GetMipLevelCount
        , py::return_value_policy::automatic_reference)
        
    .def("get_sample_count",&pywgpu::Texture::GetSampleCount
        , py::return_value_policy::automatic_reference)
        
    .def("get_dimension",&pywgpu::Texture::GetDimension
        , py::return_value_policy::automatic_reference)
        
    .def("get_format",&pywgpu::Texture::GetFormat
        , py::return_value_policy::automatic_reference)
        
    .def("get_usage",&pywgpu::Texture::GetUsage
        , py::return_value_policy::automatic_reference)
        
    .def("destroy",&pywgpu::Texture::Destroy
        , py::return_value_policy::automatic_reference)
        
    ;

py::class_<TextureView> _TextureView(m, "TextureView");
registry.on(m, "TextureView", _TextureView);

_TextureView
    .def("set_label",&pywgpu::TextureView::SetLabel
        , py::arg("label")
        , py::return_value_policy::automatic_reference)
        
    ;

py::class_<INTERNAL_HAVE_EMDAWNWEBGPU_HEADER> _INTERNAL_HAVE_EMDAWNWEBGPU_HEADER(m, "INTERNAL_HAVE_EMDAWNWEBGPU_HEADER");
registry.on(m, "INTERNAL_HAVE_EMDAWNWEBGPU_HEADER", _INTERNAL_HAVE_EMDAWNWEBGPU_HEADER);

_INTERNAL_HAVE_EMDAWNWEBGPU_HEADER
    .def_readwrite("unused", &pywgpu::INTERNAL_HAVE_EMDAWNWEBGPU_HEADER::unused)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::INTERNAL_HAVE_EMDAWNWEBGPU_HEADER obj{};
        static const std::set<std::string> allowed = {"unused"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("unused"))
        {
            auto value = kwargs["unused"].cast<Bool>();
            obj.unused = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<RequestAdapterOptions> _RequestAdapterOptions(m, "RequestAdapterOptions");
registry.on(m, "RequestAdapterOptions", _RequestAdapterOptions);

_RequestAdapterOptions
    .def_readwrite("next_in_chain", &pywgpu::RequestAdapterOptions::nextInChain)
    .def_readwrite("feature_level", &pywgpu::RequestAdapterOptions::featureLevel)
    .def_readwrite("power_preference", &pywgpu::RequestAdapterOptions::powerPreference)
    .def_readwrite("force_fallback_adapter", &pywgpu::RequestAdapterOptions::forceFallbackAdapter)
    .def_readwrite("backend_type", &pywgpu::RequestAdapterOptions::backendType)
    .def_readwrite("compatible_surface", &pywgpu::RequestAdapterOptions::compatibleSurface)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::RequestAdapterOptions obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "feature_level", "power_preference", "force_fallback_adapter", "backend_type", "compatible_surface"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("feature_level"))
        {
            auto value = kwargs["feature_level"].cast<FeatureLevel>();
            obj.featureLevel = value;
        }
        if (kwargs.contains("power_preference"))
        {
            auto value = kwargs["power_preference"].cast<PowerPreference>();
            obj.powerPreference = value;
        }
        if (kwargs.contains("force_fallback_adapter"))
        {
            auto value = kwargs["force_fallback_adapter"].cast<Bool>();
            obj.forceFallbackAdapter = value;
        }
        if (kwargs.contains("backend_type"))
        {
            auto value = kwargs["backend_type"].cast<BackendType>();
            obj.backendType = value;
        }
        if (kwargs.contains("compatible_surface"))
        {
            auto value = kwargs["compatible_surface"].cast<Surface>();
            obj.compatibleSurface = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

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

py::class_<DeviceDescriptor> _DeviceDescriptor(m, "DeviceDescriptor");
registry.on(m, "DeviceDescriptor", _DeviceDescriptor);

_DeviceDescriptor
    .def_readwrite("next_in_chain", &pywgpu::DeviceDescriptor::nextInChain)
    .def_readwrite("label", &pywgpu::DeviceDescriptor::label)
    .def_readwrite("required_feature_count", &pywgpu::DeviceDescriptor::requiredFeatureCount)
    .def_readwrite("required_features", &pywgpu::DeviceDescriptor::requiredFeatures)
    .def_readwrite("required_limits", &pywgpu::DeviceDescriptor::requiredLimits)
    .def_readwrite("default_queue", &pywgpu::DeviceDescriptor::defaultQueue)
    .def_readwrite("device_lost_callback_info", &pywgpu::DeviceDescriptor::deviceLostCallbackInfo)
    .def_readwrite("uncaptured_error_callback_info", &pywgpu::DeviceDescriptor::uncapturedErrorCallbackInfo)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::DeviceDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "label", "required_features", "required_limits", "default_queue", "device_lost_callback_info", "uncaptured_error_callback_info"};
        static const std::set<std::string> required = {"device_lost_callback_info", "uncaptured_error_callback_info"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("label"))
        {
            auto value = kwargs["label"].cast<StringView>();
            obj.label = value;
        }
        if (kwargs.contains("required_features"))
        {
            auto _value = kwargs["required_features"].cast<std::vector<FeatureName>>();
            auto count = _value.size();
            auto value = new FeatureName[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.requiredFeatures = value;
            obj.requiredFeatureCount = count;
        }
        if (kwargs.contains("required_limits"))
        {
            auto value = kwargs["required_limits"].cast<Limits const *>();
            obj.requiredLimits = value;
        }
        if (kwargs.contains("default_queue"))
        {
            auto value = kwargs["default_queue"].cast<QueueDescriptor>();
            obj.defaultQueue = value;
        }
        if (kwargs.contains("device_lost_callback_info"))
        {
            auto value = kwargs["device_lost_callback_info"].cast<DeviceLostCallbackInfo>();
            obj.deviceLostCallbackInfo = value;
        }
        if (kwargs.contains("uncaptured_error_callback_info"))
        {
            auto value = kwargs["uncaptured_error_callback_info"].cast<UncapturedErrorCallbackInfo>();
            obj.uncapturedErrorCallbackInfo = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<DawnTogglesDescriptor, ChainedStruct> _DawnTogglesDescriptor(m, "DawnTogglesDescriptor");
registry.on(m, "DawnTogglesDescriptor", _DawnTogglesDescriptor);

_DawnTogglesDescriptor
    .def_readwrite("next_in_chain", &pywgpu::DawnTogglesDescriptor::nextInChain)
    .def_readwrite("enabled_toggle_count", &pywgpu::DawnTogglesDescriptor::enabledToggleCount)
    .def_readwrite("disabled_toggle_count", &pywgpu::DawnTogglesDescriptor::disabledToggleCount)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::DawnTogglesDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "enabled_toggles", "disabled_toggles"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<DawnCacheDeviceDescriptor, ChainedStruct> _DawnCacheDeviceDescriptor(m, "DawnCacheDeviceDescriptor");
registry.on(m, "DawnCacheDeviceDescriptor", _DawnCacheDeviceDescriptor);

_DawnCacheDeviceDescriptor
    .def_readwrite("next_in_chain", &pywgpu::DawnCacheDeviceDescriptor::nextInChain)
    .def_readwrite("isolation_key", &pywgpu::DawnCacheDeviceDescriptor::isolationKey)
    .def_readwrite("function_userdata", &pywgpu::DawnCacheDeviceDescriptor::functionUserdata)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::DawnCacheDeviceDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "isolation_key", "load_data_function", "store_data_function", "function_userdata"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("isolation_key"))
        {
            auto value = kwargs["isolation_key"].cast<StringView>();
            obj.isolationKey = value;
        }
        if (kwargs.contains("function_userdata"))
        {
            auto value = kwargs["function_userdata"].cast<void *>();
            obj.functionUserdata = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<DawnWGSLBlocklist, ChainedStruct> _DawnWGSLBlocklist(m, "DawnWGSLBlocklist");
registry.on(m, "DawnWGSLBlocklist", _DawnWGSLBlocklist);

_DawnWGSLBlocklist
    .def_readwrite("next_in_chain", &pywgpu::DawnWGSLBlocklist::nextInChain)
    .def_readwrite("blocklisted_feature_count", &pywgpu::DawnWGSLBlocklist::blocklistedFeatureCount)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::DawnWGSLBlocklist obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "blocklisted_features"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<BindGroupEntry> _BindGroupEntry(m, "BindGroupEntry");
registry.on(m, "BindGroupEntry", _BindGroupEntry);

_BindGroupEntry
    .def_readwrite("next_in_chain", &pywgpu::BindGroupEntry::nextInChain)
    .def_readwrite("binding", &pywgpu::BindGroupEntry::binding)
    .def_readwrite("buffer", &pywgpu::BindGroupEntry::buffer)
    .def_readwrite("offset", &pywgpu::BindGroupEntry::offset)
    .def_readwrite("size", &pywgpu::BindGroupEntry::size)
    .def_readwrite("sampler", &pywgpu::BindGroupEntry::sampler)
    .def_readwrite("texture_view", &pywgpu::BindGroupEntry::textureView)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::BindGroupEntry obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "binding", "buffer", "offset", "size", "sampler", "texture_view"};
        static const std::set<std::string> required = {"binding"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("binding"))
        {
            auto value = kwargs["binding"].cast<uint32_t>();
            obj.binding = value;
        }
        if (kwargs.contains("buffer"))
        {
            auto value = kwargs["buffer"].cast<Buffer>();
            obj.buffer = value;
        }
        if (kwargs.contains("offset"))
        {
            auto value = kwargs["offset"].cast<uint64_t>();
            obj.offset = value;
        }
        if (kwargs.contains("size"))
        {
            auto value = kwargs["size"].cast<uint64_t>();
            obj.size = value;
        }
        if (kwargs.contains("sampler"))
        {
            auto value = kwargs["sampler"].cast<Sampler>();
            obj.sampler = value;
        }
        if (kwargs.contains("texture_view"))
        {
            auto value = kwargs["texture_view"].cast<TextureView>();
            obj.textureView = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<BindGroupDescriptor> _BindGroupDescriptor(m, "BindGroupDescriptor");
registry.on(m, "BindGroupDescriptor", _BindGroupDescriptor);

_BindGroupDescriptor
    .def_readwrite("next_in_chain", &pywgpu::BindGroupDescriptor::nextInChain)
    .def_readwrite("label", &pywgpu::BindGroupDescriptor::label)
    .def_readwrite("layout", &pywgpu::BindGroupDescriptor::layout)
    .def_readwrite("entry_count", &pywgpu::BindGroupDescriptor::entryCount)
    .def_readwrite("entries", &pywgpu::BindGroupDescriptor::entries)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::BindGroupDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "label", "layout", "entries"};
        static const std::set<std::string> required = {"layout", "entries"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("label"))
        {
            auto value = kwargs["label"].cast<StringView>();
            obj.label = value;
        }
        if (kwargs.contains("layout"))
        {
            auto value = kwargs["layout"].cast<BindGroupLayout>();
            obj.layout = value;
        }
        if (kwargs.contains("entries"))
        {
            auto _value = kwargs["entries"].cast<std::vector<BindGroupEntry>>();
            auto count = _value.size();
            auto value = new BindGroupEntry[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.entries = value;
            obj.entryCount = count;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<BufferBindingLayout> _BufferBindingLayout(m, "BufferBindingLayout");
registry.on(m, "BufferBindingLayout", _BufferBindingLayout);

_BufferBindingLayout
    .def_readwrite("next_in_chain", &pywgpu::BufferBindingLayout::nextInChain)
    .def_readwrite("type", &pywgpu::BufferBindingLayout::type)
    .def_readwrite("has_dynamic_offset", &pywgpu::BufferBindingLayout::hasDynamicOffset)
    .def_readwrite("min_binding_size", &pywgpu::BufferBindingLayout::minBindingSize)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::BufferBindingLayout obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "type", "has_dynamic_offset", "min_binding_size"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("type"))
        {
            auto value = kwargs["type"].cast<BufferBindingType>();
            obj.type = value;
        }
        if (kwargs.contains("has_dynamic_offset"))
        {
            auto value = kwargs["has_dynamic_offset"].cast<Bool>();
            obj.hasDynamicOffset = value;
        }
        if (kwargs.contains("min_binding_size"))
        {
            auto value = kwargs["min_binding_size"].cast<uint64_t>();
            obj.minBindingSize = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SamplerBindingLayout> _SamplerBindingLayout(m, "SamplerBindingLayout");
registry.on(m, "SamplerBindingLayout", _SamplerBindingLayout);

_SamplerBindingLayout
    .def_readwrite("next_in_chain", &pywgpu::SamplerBindingLayout::nextInChain)
    .def_readwrite("type", &pywgpu::SamplerBindingLayout::type)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SamplerBindingLayout obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "type"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("type"))
        {
            auto value = kwargs["type"].cast<SamplerBindingType>();
            obj.type = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<StaticSamplerBindingLayout, ChainedStruct> _StaticSamplerBindingLayout(m, "StaticSamplerBindingLayout");
registry.on(m, "StaticSamplerBindingLayout", _StaticSamplerBindingLayout);

_StaticSamplerBindingLayout
    .def_readwrite("next_in_chain", &pywgpu::StaticSamplerBindingLayout::nextInChain)
    .def_readwrite("sampler", &pywgpu::StaticSamplerBindingLayout::sampler)
    .def_readwrite("sampled_texture_binding", &pywgpu::StaticSamplerBindingLayout::sampledTextureBinding)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::StaticSamplerBindingLayout obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "sampler", "sampled_texture_binding"};
        static const std::set<std::string> required = {"sampler"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("sampler"))
        {
            auto value = kwargs["sampler"].cast<Sampler>();
            obj.sampler = value;
        }
        if (kwargs.contains("sampled_texture_binding"))
        {
            auto value = kwargs["sampled_texture_binding"].cast<uint32_t>();
            obj.sampledTextureBinding = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<TextureBindingLayout> _TextureBindingLayout(m, "TextureBindingLayout");
registry.on(m, "TextureBindingLayout", _TextureBindingLayout);

_TextureBindingLayout
    .def_readwrite("next_in_chain", &pywgpu::TextureBindingLayout::nextInChain)
    .def_readwrite("sample_type", &pywgpu::TextureBindingLayout::sampleType)
    .def_readwrite("view_dimension", &pywgpu::TextureBindingLayout::viewDimension)
    .def_readwrite("multisampled", &pywgpu::TextureBindingLayout::multisampled)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::TextureBindingLayout obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "sample_type", "view_dimension", "multisampled"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("sample_type"))
        {
            auto value = kwargs["sample_type"].cast<TextureSampleType>();
            obj.sampleType = value;
        }
        if (kwargs.contains("view_dimension"))
        {
            auto value = kwargs["view_dimension"].cast<TextureViewDimension>();
            obj.viewDimension = value;
        }
        if (kwargs.contains("multisampled"))
        {
            auto value = kwargs["multisampled"].cast<Bool>();
            obj.multisampled = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
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

py::class_<SurfaceConfiguration> _SurfaceConfiguration(m, "SurfaceConfiguration");
registry.on(m, "SurfaceConfiguration", _SurfaceConfiguration);

_SurfaceConfiguration
    .def_readwrite("next_in_chain", &pywgpu::SurfaceConfiguration::nextInChain)
    .def_readwrite("device", &pywgpu::SurfaceConfiguration::device)
    .def_readwrite("format", &pywgpu::SurfaceConfiguration::format)
    .def_readwrite("usage", &pywgpu::SurfaceConfiguration::usage)
    .def_readwrite("width", &pywgpu::SurfaceConfiguration::width)
    .def_readwrite("height", &pywgpu::SurfaceConfiguration::height)
    .def_readwrite("view_format_count", &pywgpu::SurfaceConfiguration::viewFormatCount)
    .def_readwrite("view_formats", &pywgpu::SurfaceConfiguration::viewFormats)
    .def_readwrite("alpha_mode", &pywgpu::SurfaceConfiguration::alphaMode)
    .def_readwrite("present_mode", &pywgpu::SurfaceConfiguration::presentMode)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SurfaceConfiguration obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "device", "format", "usage", "width", "height", "view_formats", "alpha_mode", "present_mode"};
        static const std::set<std::string> required = {"device", "width", "height"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("device"))
        {
            auto value = kwargs["device"].cast<Device>();
            obj.device = value;
        }
        if (kwargs.contains("format"))
        {
            auto value = kwargs["format"].cast<TextureFormat>();
            obj.format = value;
        }
        if (kwargs.contains("usage"))
        {
            auto value = kwargs["usage"].cast<TextureUsage>();
            obj.usage = value;
        }
        if (kwargs.contains("width"))
        {
            auto value = kwargs["width"].cast<uint32_t>();
            obj.width = value;
        }
        if (kwargs.contains("height"))
        {
            auto value = kwargs["height"].cast<uint32_t>();
            obj.height = value;
        }
        if (kwargs.contains("view_formats"))
        {
            auto _value = kwargs["view_formats"].cast<std::vector<TextureFormat>>();
            auto count = _value.size();
            auto value = new TextureFormat[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.viewFormats = value;
            obj.viewFormatCount = count;
        }
        if (kwargs.contains("alpha_mode"))
        {
            auto value = kwargs["alpha_mode"].cast<CompositeAlphaMode>();
            obj.alphaMode = value;
        }
        if (kwargs.contains("present_mode"))
        {
            auto value = kwargs["present_mode"].cast<PresentMode>();
            obj.presentMode = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<ExternalTextureBindingEntry, ChainedStruct> _ExternalTextureBindingEntry(m, "ExternalTextureBindingEntry");
registry.on(m, "ExternalTextureBindingEntry", _ExternalTextureBindingEntry);

_ExternalTextureBindingEntry
    .def_readwrite("next_in_chain", &pywgpu::ExternalTextureBindingEntry::nextInChain)
    .def_readwrite("external_texture", &pywgpu::ExternalTextureBindingEntry::externalTexture)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::ExternalTextureBindingEntry obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "external_texture"};
        static const std::set<std::string> required = {"external_texture"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("external_texture"))
        {
            auto value = kwargs["external_texture"].cast<ExternalTexture>();
            obj.externalTexture = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<ExternalTextureBindingLayout, ChainedStruct> _ExternalTextureBindingLayout(m, "ExternalTextureBindingLayout");
registry.on(m, "ExternalTextureBindingLayout", _ExternalTextureBindingLayout);

_ExternalTextureBindingLayout
    .def_readwrite("next_in_chain", &pywgpu::ExternalTextureBindingLayout::nextInChain)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::ExternalTextureBindingLayout obj{};
        static const std::set<std::string> allowed = {"next_in_chain"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<StorageTextureBindingLayout> _StorageTextureBindingLayout(m, "StorageTextureBindingLayout");
registry.on(m, "StorageTextureBindingLayout", _StorageTextureBindingLayout);

_StorageTextureBindingLayout
    .def_readwrite("next_in_chain", &pywgpu::StorageTextureBindingLayout::nextInChain)
    .def_readwrite("access", &pywgpu::StorageTextureBindingLayout::access)
    .def_readwrite("format", &pywgpu::StorageTextureBindingLayout::format)
    .def_readwrite("view_dimension", &pywgpu::StorageTextureBindingLayout::viewDimension)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::StorageTextureBindingLayout obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "access", "format", "view_dimension"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("access"))
        {
            auto value = kwargs["access"].cast<StorageTextureAccess>();
            obj.access = value;
        }
        if (kwargs.contains("format"))
        {
            auto value = kwargs["format"].cast<TextureFormat>();
            obj.format = value;
        }
        if (kwargs.contains("view_dimension"))
        {
            auto value = kwargs["view_dimension"].cast<TextureViewDimension>();
            obj.viewDimension = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<BindGroupLayoutEntry> _BindGroupLayoutEntry(m, "BindGroupLayoutEntry");
registry.on(m, "BindGroupLayoutEntry", _BindGroupLayoutEntry);

_BindGroupLayoutEntry
    .def_readwrite("next_in_chain", &pywgpu::BindGroupLayoutEntry::nextInChain)
    .def_readwrite("binding", &pywgpu::BindGroupLayoutEntry::binding)
    .def_readwrite("visibility", &pywgpu::BindGroupLayoutEntry::visibility)
    .def_readwrite("buffer", &pywgpu::BindGroupLayoutEntry::buffer)
    .def_readwrite("sampler", &pywgpu::BindGroupLayoutEntry::sampler)
    .def_readwrite("texture", &pywgpu::BindGroupLayoutEntry::texture)
    .def_readwrite("storage_texture", &pywgpu::BindGroupLayoutEntry::storageTexture)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::BindGroupLayoutEntry obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "binding", "visibility", "buffer", "sampler", "texture", "storage_texture"};
        static const std::set<std::string> required = {"binding"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("binding"))
        {
            auto value = kwargs["binding"].cast<uint32_t>();
            obj.binding = value;
        }
        if (kwargs.contains("visibility"))
        {
            auto value = kwargs["visibility"].cast<ShaderStage>();
            obj.visibility = value;
        }
        if (kwargs.contains("buffer"))
        {
            auto value = kwargs["buffer"].cast<BufferBindingLayout>();
            obj.buffer = value;
        }
        if (kwargs.contains("sampler"))
        {
            auto value = kwargs["sampler"].cast<SamplerBindingLayout>();
            obj.sampler = value;
        }
        if (kwargs.contains("texture"))
        {
            auto value = kwargs["texture"].cast<TextureBindingLayout>();
            obj.texture = value;
        }
        if (kwargs.contains("storage_texture"))
        {
            auto value = kwargs["storage_texture"].cast<StorageTextureBindingLayout>();
            obj.storageTexture = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<BindGroupLayoutDescriptor> _BindGroupLayoutDescriptor(m, "BindGroupLayoutDescriptor");
registry.on(m, "BindGroupLayoutDescriptor", _BindGroupLayoutDescriptor);

_BindGroupLayoutDescriptor
    .def_readwrite("next_in_chain", &pywgpu::BindGroupLayoutDescriptor::nextInChain)
    .def_readwrite("label", &pywgpu::BindGroupLayoutDescriptor::label)
    .def_readwrite("entry_count", &pywgpu::BindGroupLayoutDescriptor::entryCount)
    .def_readwrite("entries", &pywgpu::BindGroupLayoutDescriptor::entries)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::BindGroupLayoutDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "label", "entries"};
        static const std::set<std::string> required = {"entries"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("label"))
        {
            auto value = kwargs["label"].cast<StringView>();
            obj.label = value;
        }
        if (kwargs.contains("entries"))
        {
            auto _value = kwargs["entries"].cast<std::vector<BindGroupLayoutEntry>>();
            auto count = _value.size();
            auto value = new BindGroupLayoutEntry[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.entries = value;
            obj.entryCount = count;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<BlendComponent> _BlendComponent(m, "BlendComponent");
registry.on(m, "BlendComponent", _BlendComponent);

_BlendComponent
    .def_readwrite("operation", &pywgpu::BlendComponent::operation)
    .def_readwrite("src_factor", &pywgpu::BlendComponent::srcFactor)
    .def_readwrite("dst_factor", &pywgpu::BlendComponent::dstFactor)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::BlendComponent obj{};
        static const std::set<std::string> allowed = {"operation", "src_factor", "dst_factor"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("operation"))
        {
            auto value = kwargs["operation"].cast<BlendOperation>();
            obj.operation = value;
        }
        if (kwargs.contains("src_factor"))
        {
            auto value = kwargs["src_factor"].cast<BlendFactor>();
            obj.srcFactor = value;
        }
        if (kwargs.contains("dst_factor"))
        {
            auto value = kwargs["dst_factor"].cast<BlendFactor>();
            obj.dstFactor = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<BufferDescriptor> _BufferDescriptor(m, "BufferDescriptor");
registry.on(m, "BufferDescriptor", _BufferDescriptor);

_BufferDescriptor
    .def_readwrite("next_in_chain", &pywgpu::BufferDescriptor::nextInChain)
    .def_readwrite("label", &pywgpu::BufferDescriptor::label)
    .def_readwrite("usage", &pywgpu::BufferDescriptor::usage)
    .def_readwrite("size", &pywgpu::BufferDescriptor::size)
    .def_readwrite("mapped_at_creation", &pywgpu::BufferDescriptor::mappedAtCreation)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::BufferDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "label", "usage", "size", "mapped_at_creation"};
        static const std::set<std::string> required = {"size"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("label"))
        {
            auto value = kwargs["label"].cast<StringView>();
            obj.label = value;
        }
        if (kwargs.contains("usage"))
        {
            auto value = kwargs["usage"].cast<BufferUsage>();
            obj.usage = value;
        }
        if (kwargs.contains("size"))
        {
            auto value = kwargs["size"].cast<uint64_t>();
            obj.size = value;
        }
        if (kwargs.contains("mapped_at_creation"))
        {
            auto value = kwargs["mapped_at_creation"].cast<Bool>();
            obj.mappedAtCreation = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<BufferHostMappedPointer, ChainedStruct> _BufferHostMappedPointer(m, "BufferHostMappedPointer");
registry.on(m, "BufferHostMappedPointer", _BufferHostMappedPointer);

_BufferHostMappedPointer
    .def_readwrite("next_in_chain", &pywgpu::BufferHostMappedPointer::nextInChain)
    .def_readwrite("pointer", &pywgpu::BufferHostMappedPointer::pointer)
    .def_readwrite("userdata", &pywgpu::BufferHostMappedPointer::userdata)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::BufferHostMappedPointer obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "pointer", "dispose_callback", "userdata"};
        static const std::set<std::string> required = {"pointer", "dispose_callback", "userdata"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("pointer"))
        {
            auto value = kwargs["pointer"].cast<void *>();
            obj.pointer = value;
        }
        if (kwargs.contains("userdata"))
        {
            auto value = kwargs["userdata"].cast<void *>();
            obj.userdata = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<Color> _Color(m, "Color");
registry.on(m, "Color", _Color);

_Color
    .def_readwrite("r", &pywgpu::Color::r)
    .def_readwrite("g", &pywgpu::Color::g)
    .def_readwrite("b", &pywgpu::Color::b)
    .def_readwrite("a", &pywgpu::Color::a)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::Color obj{};
        static const std::set<std::string> allowed = {"r", "g", "b", "a"};
        static const std::set<std::string> required = {"r", "g", "b", "a"};
        
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
        
        if (kwargs.contains("r"))
        {
            auto value = kwargs["r"].cast<double>();
            obj.r = value;
        }
        if (kwargs.contains("g"))
        {
            auto value = kwargs["g"].cast<double>();
            obj.g = value;
        }
        if (kwargs.contains("b"))
        {
            auto value = kwargs["b"].cast<double>();
            obj.b = value;
        }
        if (kwargs.contains("a"))
        {
            auto value = kwargs["a"].cast<double>();
            obj.a = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<ConstantEntry> _ConstantEntry(m, "ConstantEntry");
registry.on(m, "ConstantEntry", _ConstantEntry);

_ConstantEntry
    .def_readwrite("next_in_chain", &pywgpu::ConstantEntry::nextInChain)
    .def_readwrite("key", &pywgpu::ConstantEntry::key)
    .def_readwrite("value", &pywgpu::ConstantEntry::value)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::ConstantEntry obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "key", "value"};
        static const std::set<std::string> required = {"value"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("key"))
        {
            auto value = kwargs["key"].cast<StringView>();
            obj.key = value;
        }
        if (kwargs.contains("value"))
        {
            auto value = kwargs["value"].cast<double>();
            obj.value = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<CommandBufferDescriptor> _CommandBufferDescriptor(m, "CommandBufferDescriptor");
registry.on(m, "CommandBufferDescriptor", _CommandBufferDescriptor);

_CommandBufferDescriptor
    .def_readwrite("next_in_chain", &pywgpu::CommandBufferDescriptor::nextInChain)
    .def_readwrite("label", &pywgpu::CommandBufferDescriptor::label)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::CommandBufferDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "label"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("label"))
        {
            auto value = kwargs["label"].cast<StringView>();
            obj.label = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<CommandEncoderDescriptor> _CommandEncoderDescriptor(m, "CommandEncoderDescriptor");
registry.on(m, "CommandEncoderDescriptor", _CommandEncoderDescriptor);

_CommandEncoderDescriptor
    .def_readwrite("next_in_chain", &pywgpu::CommandEncoderDescriptor::nextInChain)
    .def_readwrite("label", &pywgpu::CommandEncoderDescriptor::label)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::CommandEncoderDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "label"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("label"))
        {
            auto value = kwargs["label"].cast<StringView>();
            obj.label = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<CompilationInfo> _CompilationInfo(m, "CompilationInfo");
registry.on(m, "CompilationInfo", _CompilationInfo);

_CompilationInfo
    .def_readwrite("next_in_chain", &pywgpu::CompilationInfo::nextInChain)
    .def_readwrite("message_count", &pywgpu::CompilationInfo::messageCount)
    .def_readwrite("messages", &pywgpu::CompilationInfo::messages)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::CompilationInfo obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "messages"};
        static const std::set<std::string> required = {"messages"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("messages"))
        {
            auto _value = kwargs["messages"].cast<std::vector<CompilationMessage>>();
            auto count = _value.size();
            auto value = new CompilationMessage[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.messages = value;
            obj.messageCount = count;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<CompilationMessage> _CompilationMessage(m, "CompilationMessage");
registry.on(m, "CompilationMessage", _CompilationMessage);

_CompilationMessage
    .def_readwrite("next_in_chain", &pywgpu::CompilationMessage::nextInChain)
    .def_readwrite("message", &pywgpu::CompilationMessage::message)
    .def_readwrite("type", &pywgpu::CompilationMessage::type)
    .def_readwrite("line_num", &pywgpu::CompilationMessage::lineNum)
    .def_readwrite("line_pos", &pywgpu::CompilationMessage::linePos)
    .def_readwrite("offset", &pywgpu::CompilationMessage::offset)
    .def_readwrite("length", &pywgpu::CompilationMessage::length)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::CompilationMessage obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "message", "type", "line_num", "line_pos", "offset", "length"};
        static const std::set<std::string> required = {"line_num", "line_pos", "offset", "length"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("message"))
        {
            auto value = kwargs["message"].cast<StringView>();
            obj.message = value;
        }
        if (kwargs.contains("type"))
        {
            auto value = kwargs["type"].cast<CompilationMessageType>();
            obj.type = value;
        }
        if (kwargs.contains("line_num"))
        {
            auto value = kwargs["line_num"].cast<uint64_t>();
            obj.lineNum = value;
        }
        if (kwargs.contains("line_pos"))
        {
            auto value = kwargs["line_pos"].cast<uint64_t>();
            obj.linePos = value;
        }
        if (kwargs.contains("offset"))
        {
            auto value = kwargs["offset"].cast<uint64_t>();
            obj.offset = value;
        }
        if (kwargs.contains("length"))
        {
            auto value = kwargs["length"].cast<uint64_t>();
            obj.length = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<DawnCompilationMessageUtf16, ChainedStruct> _DawnCompilationMessageUtf16(m, "DawnCompilationMessageUtf16");
registry.on(m, "DawnCompilationMessageUtf16", _DawnCompilationMessageUtf16);

_DawnCompilationMessageUtf16
    .def_readwrite("next_in_chain", &pywgpu::DawnCompilationMessageUtf16::nextInChain)
    .def_readwrite("line_pos", &pywgpu::DawnCompilationMessageUtf16::linePos)
    .def_readwrite("offset", &pywgpu::DawnCompilationMessageUtf16::offset)
    .def_readwrite("length", &pywgpu::DawnCompilationMessageUtf16::length)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::DawnCompilationMessageUtf16 obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "line_pos", "offset", "length"};
        static const std::set<std::string> required = {"line_pos", "offset", "length"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("line_pos"))
        {
            auto value = kwargs["line_pos"].cast<uint64_t>();
            obj.linePos = value;
        }
        if (kwargs.contains("offset"))
        {
            auto value = kwargs["offset"].cast<uint64_t>();
            obj.offset = value;
        }
        if (kwargs.contains("length"))
        {
            auto value = kwargs["length"].cast<uint64_t>();
            obj.length = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<ComputePassDescriptor> _ComputePassDescriptor(m, "ComputePassDescriptor");
registry.on(m, "ComputePassDescriptor", _ComputePassDescriptor);

_ComputePassDescriptor
    .def_readwrite("next_in_chain", &pywgpu::ComputePassDescriptor::nextInChain)
    .def_readwrite("label", &pywgpu::ComputePassDescriptor::label)
    .def_readwrite("timestamp_writes", &pywgpu::ComputePassDescriptor::timestampWrites)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::ComputePassDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "label", "timestamp_writes"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("label"))
        {
            auto value = kwargs["label"].cast<StringView>();
            obj.label = value;
        }
        if (kwargs.contains("timestamp_writes"))
        {
            auto value = kwargs["timestamp_writes"].cast<PassTimestampWrites const *>();
            obj.timestampWrites = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<ComputePipelineDescriptor> _ComputePipelineDescriptor(m, "ComputePipelineDescriptor");
registry.on(m, "ComputePipelineDescriptor", _ComputePipelineDescriptor);

_ComputePipelineDescriptor
    .def_readwrite("next_in_chain", &pywgpu::ComputePipelineDescriptor::nextInChain)
    .def_readwrite("label", &pywgpu::ComputePipelineDescriptor::label)
    .def_readwrite("layout", &pywgpu::ComputePipelineDescriptor::layout)
    .def_readwrite("compute", &pywgpu::ComputePipelineDescriptor::compute)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::ComputePipelineDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "label", "layout", "compute"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("label"))
        {
            auto value = kwargs["label"].cast<StringView>();
            obj.label = value;
        }
        if (kwargs.contains("layout"))
        {
            auto value = kwargs["layout"].cast<PipelineLayout>();
            obj.layout = value;
        }
        if (kwargs.contains("compute"))
        {
            auto value = kwargs["compute"].cast<ComputeState>();
            obj.compute = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<CopyTextureForBrowserOptions> _CopyTextureForBrowserOptions(m, "CopyTextureForBrowserOptions");
registry.on(m, "CopyTextureForBrowserOptions", _CopyTextureForBrowserOptions);

_CopyTextureForBrowserOptions
    .def_readwrite("next_in_chain", &pywgpu::CopyTextureForBrowserOptions::nextInChain)
    .def_readwrite("flip_y", &pywgpu::CopyTextureForBrowserOptions::flipY)
    .def_readwrite("needs_color_space_conversion", &pywgpu::CopyTextureForBrowserOptions::needsColorSpaceConversion)
    .def_readwrite("src_alpha_mode", &pywgpu::CopyTextureForBrowserOptions::srcAlphaMode)
    .def_readwrite("src_transfer_function_parameters", &pywgpu::CopyTextureForBrowserOptions::srcTransferFunctionParameters)
    .def_readwrite("conversion_matrix", &pywgpu::CopyTextureForBrowserOptions::conversionMatrix)
    .def_readwrite("dst_transfer_function_parameters", &pywgpu::CopyTextureForBrowserOptions::dstTransferFunctionParameters)
    .def_readwrite("dst_alpha_mode", &pywgpu::CopyTextureForBrowserOptions::dstAlphaMode)
    .def_readwrite("internal_usage", &pywgpu::CopyTextureForBrowserOptions::internalUsage)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::CopyTextureForBrowserOptions obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "flip_y", "needs_color_space_conversion", "src_alpha_mode", "src_transfer_function_parameters", "conversion_matrix", "dst_transfer_function_parameters", "dst_alpha_mode", "internal_usage"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("flip_y"))
        {
            auto value = kwargs["flip_y"].cast<Bool>();
            obj.flipY = value;
        }
        if (kwargs.contains("needs_color_space_conversion"))
        {
            auto value = kwargs["needs_color_space_conversion"].cast<Bool>();
            obj.needsColorSpaceConversion = value;
        }
        if (kwargs.contains("src_alpha_mode"))
        {
            auto value = kwargs["src_alpha_mode"].cast<AlphaMode>();
            obj.srcAlphaMode = value;
        }
        if (kwargs.contains("src_transfer_function_parameters"))
        {
            auto _value = kwargs["src_transfer_function_parameters"].cast<std::vector<float>>();
            auto count = _value.size();
            auto value = new float[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.srcTransferFunctionParameters = value;
        }
        if (kwargs.contains("conversion_matrix"))
        {
            auto _value = kwargs["conversion_matrix"].cast<std::vector<float>>();
            auto count = _value.size();
            auto value = new float[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.conversionMatrix = value;
        }
        if (kwargs.contains("dst_transfer_function_parameters"))
        {
            auto _value = kwargs["dst_transfer_function_parameters"].cast<std::vector<float>>();
            auto count = _value.size();
            auto value = new float[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.dstTransferFunctionParameters = value;
        }
        if (kwargs.contains("dst_alpha_mode"))
        {
            auto value = kwargs["dst_alpha_mode"].cast<AlphaMode>();
            obj.dstAlphaMode = value;
        }
        if (kwargs.contains("internal_usage"))
        {
            auto value = kwargs["internal_usage"].cast<Bool>();
            obj.internalUsage = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<AHardwareBufferProperties> _AHardwareBufferProperties(m, "AHardwareBufferProperties");
registry.on(m, "AHardwareBufferProperties", _AHardwareBufferProperties);

_AHardwareBufferProperties
    .def_readwrite("y_cb_cr_info", &pywgpu::AHardwareBufferProperties::yCbCrInfo)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::AHardwareBufferProperties obj{};
        static const std::set<std::string> allowed = {"y_cb_cr_info"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("y_cb_cr_info"))
        {
            auto value = kwargs["y_cb_cr_info"].cast<YCbCrVkDescriptor>();
            obj.yCbCrInfo = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<Limits> _Limits(m, "Limits");
registry.on(m, "Limits", _Limits);

_Limits
    .def_readonly("next_in_chain", &pywgpu::Limits::nextInChain)
    .def_readonly("max_texture_dimension_1D", &pywgpu::Limits::maxTextureDimension1D)
    .def_readonly("max_texture_dimension_2D", &pywgpu::Limits::maxTextureDimension2D)
    .def_readonly("max_texture_dimension_3D", &pywgpu::Limits::maxTextureDimension3D)
    .def_readonly("max_texture_array_layers", &pywgpu::Limits::maxTextureArrayLayers)
    .def_readonly("max_bind_groups", &pywgpu::Limits::maxBindGroups)
    .def_readonly("max_bind_groups_plus_vertex_buffers", &pywgpu::Limits::maxBindGroupsPlusVertexBuffers)
    .def_readonly("max_bindings_per_bind_group", &pywgpu::Limits::maxBindingsPerBindGroup)
    .def_readonly("max_dynamic_uniform_buffers_per_pipeline_layout", &pywgpu::Limits::maxDynamicUniformBuffersPerPipelineLayout)
    .def_readonly("max_dynamic_storage_buffers_per_pipeline_layout", &pywgpu::Limits::maxDynamicStorageBuffersPerPipelineLayout)
    .def_readonly("max_sampled_textures_per_shader_stage", &pywgpu::Limits::maxSampledTexturesPerShaderStage)
    .def_readonly("max_samplers_per_shader_stage", &pywgpu::Limits::maxSamplersPerShaderStage)
    .def_readonly("max_storage_buffers_per_shader_stage", &pywgpu::Limits::maxStorageBuffersPerShaderStage)
    .def_readonly("max_storage_textures_per_shader_stage", &pywgpu::Limits::maxStorageTexturesPerShaderStage)
    .def_readonly("max_uniform_buffers_per_shader_stage", &pywgpu::Limits::maxUniformBuffersPerShaderStage)
    .def_readonly("max_uniform_buffer_binding_size", &pywgpu::Limits::maxUniformBufferBindingSize)
    .def_readonly("max_storage_buffer_binding_size", &pywgpu::Limits::maxStorageBufferBindingSize)
    .def_readonly("min_uniform_buffer_offset_alignment", &pywgpu::Limits::minUniformBufferOffsetAlignment)
    .def_readonly("min_storage_buffer_offset_alignment", &pywgpu::Limits::minStorageBufferOffsetAlignment)
    .def_readonly("max_vertex_buffers", &pywgpu::Limits::maxVertexBuffers)
    .def_readonly("max_buffer_size", &pywgpu::Limits::maxBufferSize)
    .def_readonly("max_vertex_attributes", &pywgpu::Limits::maxVertexAttributes)
    .def_readonly("max_vertex_buffer_array_stride", &pywgpu::Limits::maxVertexBufferArrayStride)
    .def_readonly("max_inter_stage_shader_variables", &pywgpu::Limits::maxInterStageShaderVariables)
    .def_readonly("max_color_attachments", &pywgpu::Limits::maxColorAttachments)
    .def_readonly("max_color_attachment_bytes_per_sample", &pywgpu::Limits::maxColorAttachmentBytesPerSample)
    .def_readonly("max_compute_workgroup_storage_size", &pywgpu::Limits::maxComputeWorkgroupStorageSize)
    .def_readonly("max_compute_invocations_per_workgroup", &pywgpu::Limits::maxComputeInvocationsPerWorkgroup)
    .def_readonly("max_compute_workgroup_size_x", &pywgpu::Limits::maxComputeWorkgroupSizeX)
    .def_readonly("max_compute_workgroup_size_y", &pywgpu::Limits::maxComputeWorkgroupSizeY)
    .def_readonly("max_compute_workgroup_size_z", &pywgpu::Limits::maxComputeWorkgroupSizeZ)
    .def_readonly("max_compute_workgroups_per_dimension", &pywgpu::Limits::maxComputeWorkgroupsPerDimension)
    .def_readonly("max_storage_buffers_in_vertex_stage", &pywgpu::Limits::maxStorageBuffersInVertexStage)
    .def_readonly("max_storage_textures_in_vertex_stage", &pywgpu::Limits::maxStorageTexturesInVertexStage)
    .def_readonly("max_storage_buffers_in_fragment_stage", &pywgpu::Limits::maxStorageBuffersInFragmentStage)
    .def_readonly("max_storage_textures_in_fragment_stage", &pywgpu::Limits::maxStorageTexturesInFragmentStage)
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

py::class_<SupportedFeatures> _SupportedFeatures(m, "SupportedFeatures");
registry.on(m, "SupportedFeatures", _SupportedFeatures);

_SupportedFeatures
    .def_readwrite("feature_count", &pywgpu::SupportedFeatures::featureCount)
    .def_readwrite("features", &pywgpu::SupportedFeatures::features)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SupportedFeatures obj{};
        static const std::set<std::string> allowed = {"features"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("features"))
        {
            auto _value = kwargs["features"].cast<std::vector<FeatureName>>();
            auto count = _value.size();
            auto value = new FeatureName[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.features = value;
            obj.featureCount = count;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SupportedWGSLLanguageFeatures> _SupportedWGSLLanguageFeatures(m, "SupportedWGSLLanguageFeatures");
registry.on(m, "SupportedWGSLLanguageFeatures", _SupportedWGSLLanguageFeatures);

_SupportedWGSLLanguageFeatures
    .def_readwrite("feature_count", &pywgpu::SupportedWGSLLanguageFeatures::featureCount)
    .def_readwrite("features", &pywgpu::SupportedWGSLLanguageFeatures::features)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SupportedWGSLLanguageFeatures obj{};
        static const std::set<std::string> allowed = {"features"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("features"))
        {
            auto _value = kwargs["features"].cast<std::vector<WGSLLanguageFeatureName>>();
            auto count = _value.size();
            auto value = new WGSLLanguageFeatureName[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.features = value;
            obj.featureCount = count;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<Extent2D> _Extent2D(m, "Extent2D");
registry.on(m, "Extent2D", _Extent2D);

_Extent2D
    .def_readwrite("width", &pywgpu::Extent2D::width)
    .def_readwrite("height", &pywgpu::Extent2D::height)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::Extent2D obj{};
        static const std::set<std::string> allowed = {"width", "height"};
        static const std::set<std::string> required = {"width", "height"};
        
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
        
        if (kwargs.contains("width"))
        {
            auto value = kwargs["width"].cast<uint32_t>();
            obj.width = value;
        }
        if (kwargs.contains("height"))
        {
            auto value = kwargs["height"].cast<uint32_t>();
            obj.height = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<Extent3D> _Extent3D(m, "Extent3D");
registry.on(m, "Extent3D", _Extent3D);

_Extent3D
    .def_readwrite("width", &pywgpu::Extent3D::width)
    .def_readwrite("height", &pywgpu::Extent3D::height)
    .def_readwrite("depth_or_array_layers", &pywgpu::Extent3D::depthOrArrayLayers)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::Extent3D obj{};
        static const std::set<std::string> allowed = {"width", "height", "depth_or_array_layers"};
        static const std::set<std::string> required = {"width"};
        
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
        
        if (kwargs.contains("width"))
        {
            auto value = kwargs["width"].cast<uint32_t>();
            obj.width = value;
        }
        if (kwargs.contains("height"))
        {
            auto value = kwargs["height"].cast<uint32_t>();
            obj.height = value;
        }
        if (kwargs.contains("depth_or_array_layers"))
        {
            auto value = kwargs["depth_or_array_layers"].cast<uint32_t>();
            obj.depthOrArrayLayers = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<ExternalTextureDescriptor> _ExternalTextureDescriptor(m, "ExternalTextureDescriptor");
registry.on(m, "ExternalTextureDescriptor", _ExternalTextureDescriptor);

_ExternalTextureDescriptor
    .def_readwrite("next_in_chain", &pywgpu::ExternalTextureDescriptor::nextInChain)
    .def_readwrite("label", &pywgpu::ExternalTextureDescriptor::label)
    .def_readwrite("plane_0", &pywgpu::ExternalTextureDescriptor::plane0)
    .def_readwrite("plane_1", &pywgpu::ExternalTextureDescriptor::plane1)
    .def_readwrite("crop_origin", &pywgpu::ExternalTextureDescriptor::cropOrigin)
    .def_readwrite("crop_size", &pywgpu::ExternalTextureDescriptor::cropSize)
    .def_readwrite("apparent_size", &pywgpu::ExternalTextureDescriptor::apparentSize)
    .def_readwrite("do_yuv_to_rgb_conversion_only", &pywgpu::ExternalTextureDescriptor::doYuvToRgbConversionOnly)
    .def_readwrite("yuv_to_rgb_conversion_matrix", &pywgpu::ExternalTextureDescriptor::yuvToRgbConversionMatrix)
    .def_readwrite("src_transfer_function_parameters", &pywgpu::ExternalTextureDescriptor::srcTransferFunctionParameters)
    .def_readwrite("dst_transfer_function_parameters", &pywgpu::ExternalTextureDescriptor::dstTransferFunctionParameters)
    .def_readwrite("gamut_conversion_matrix", &pywgpu::ExternalTextureDescriptor::gamutConversionMatrix)
    .def_readwrite("mirrored", &pywgpu::ExternalTextureDescriptor::mirrored)
    .def_readwrite("rotation", &pywgpu::ExternalTextureDescriptor::rotation)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::ExternalTextureDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "label", "plane_0", "plane_1", "crop_origin", "crop_size", "apparent_size", "do_yuv_to_rgb_conversion_only", "yuv_to_rgb_conversion_matrix", "src_transfer_function_parameters", "dst_transfer_function_parameters", "gamut_conversion_matrix", "mirrored", "rotation"};
        static const std::set<std::string> required = {"plane_0", "src_transfer_function_parameters", "dst_transfer_function_parameters", "gamut_conversion_matrix"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("label"))
        {
            auto value = kwargs["label"].cast<StringView>();
            obj.label = value;
        }
        if (kwargs.contains("plane_0"))
        {
            auto value = kwargs["plane_0"].cast<TextureView>();
            obj.plane0 = value;
        }
        if (kwargs.contains("plane_1"))
        {
            auto value = kwargs["plane_1"].cast<TextureView>();
            obj.plane1 = value;
        }
        if (kwargs.contains("crop_origin"))
        {
            auto value = kwargs["crop_origin"].cast<Origin2D>();
            obj.cropOrigin = value;
        }
        if (kwargs.contains("crop_size"))
        {
            auto value = kwargs["crop_size"].cast<Extent2D>();
            obj.cropSize = value;
        }
        if (kwargs.contains("apparent_size"))
        {
            auto value = kwargs["apparent_size"].cast<Extent2D>();
            obj.apparentSize = value;
        }
        if (kwargs.contains("do_yuv_to_rgb_conversion_only"))
        {
            auto value = kwargs["do_yuv_to_rgb_conversion_only"].cast<Bool>();
            obj.doYuvToRgbConversionOnly = value;
        }
        if (kwargs.contains("yuv_to_rgb_conversion_matrix"))
        {
            auto _value = kwargs["yuv_to_rgb_conversion_matrix"].cast<std::vector<float>>();
            auto count = _value.size();
            auto value = new float[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.yuvToRgbConversionMatrix = value;
        }
        if (kwargs.contains("src_transfer_function_parameters"))
        {
            auto _value = kwargs["src_transfer_function_parameters"].cast<std::vector<float>>();
            auto count = _value.size();
            auto value = new float[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.srcTransferFunctionParameters = value;
        }
        if (kwargs.contains("dst_transfer_function_parameters"))
        {
            auto _value = kwargs["dst_transfer_function_parameters"].cast<std::vector<float>>();
            auto count = _value.size();
            auto value = new float[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.dstTransferFunctionParameters = value;
        }
        if (kwargs.contains("gamut_conversion_matrix"))
        {
            auto _value = kwargs["gamut_conversion_matrix"].cast<std::vector<float>>();
            auto count = _value.size();
            auto value = new float[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.gamutConversionMatrix = value;
        }
        if (kwargs.contains("mirrored"))
        {
            auto value = kwargs["mirrored"].cast<Bool>();
            obj.mirrored = value;
        }
        if (kwargs.contains("rotation"))
        {
            auto value = kwargs["rotation"].cast<ExternalTextureRotation>();
            obj.rotation = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SharedBufferMemoryProperties> _SharedBufferMemoryProperties(m, "SharedBufferMemoryProperties");
registry.on(m, "SharedBufferMemoryProperties", _SharedBufferMemoryProperties);

_SharedBufferMemoryProperties
    .def_readonly("next_in_chain", &pywgpu::SharedBufferMemoryProperties::nextInChain)
    .def_readonly("usage", &pywgpu::SharedBufferMemoryProperties::usage)
    .def_readonly("size", &pywgpu::SharedBufferMemoryProperties::size)
    .def(py::init<>())
    ;

py::class_<SharedBufferMemoryDescriptor> _SharedBufferMemoryDescriptor(m, "SharedBufferMemoryDescriptor");
registry.on(m, "SharedBufferMemoryDescriptor", _SharedBufferMemoryDescriptor);

_SharedBufferMemoryDescriptor
    .def_readwrite("next_in_chain", &pywgpu::SharedBufferMemoryDescriptor::nextInChain)
    .def_readwrite("label", &pywgpu::SharedBufferMemoryDescriptor::label)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SharedBufferMemoryDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "label"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("label"))
        {
            auto value = kwargs["label"].cast<StringView>();
            obj.label = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
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

py::class_<SharedTextureMemoryDescriptor> _SharedTextureMemoryDescriptor(m, "SharedTextureMemoryDescriptor");
registry.on(m, "SharedTextureMemoryDescriptor", _SharedTextureMemoryDescriptor);

_SharedTextureMemoryDescriptor
    .def_readwrite("next_in_chain", &pywgpu::SharedTextureMemoryDescriptor::nextInChain)
    .def_readwrite("label", &pywgpu::SharedTextureMemoryDescriptor::label)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SharedTextureMemoryDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "label"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("label"))
        {
            auto value = kwargs["label"].cast<StringView>();
            obj.label = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SharedBufferMemoryBeginAccessDescriptor> _SharedBufferMemoryBeginAccessDescriptor(m, "SharedBufferMemoryBeginAccessDescriptor");
registry.on(m, "SharedBufferMemoryBeginAccessDescriptor", _SharedBufferMemoryBeginAccessDescriptor);

_SharedBufferMemoryBeginAccessDescriptor
    .def_readwrite("next_in_chain", &pywgpu::SharedBufferMemoryBeginAccessDescriptor::nextInChain)
    .def_readwrite("initialized", &pywgpu::SharedBufferMemoryBeginAccessDescriptor::initialized)
    .def_readwrite("fence_count", &pywgpu::SharedBufferMemoryBeginAccessDescriptor::fenceCount)
    .def_readwrite("fences", &pywgpu::SharedBufferMemoryBeginAccessDescriptor::fences)
    .def_readwrite("signaled_values", &pywgpu::SharedBufferMemoryBeginAccessDescriptor::signaledValues)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SharedBufferMemoryBeginAccessDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "initialized", "fences", "signaled_values"};
        static const std::set<std::string> required = {"initialized"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("initialized"))
        {
            auto value = kwargs["initialized"].cast<Bool>();
            obj.initialized = value;
        }
        if (kwargs.contains("fences"))
        {
            auto _value = kwargs["fences"].cast<std::vector<SharedFence>>();
            auto count = _value.size();
            auto value = new SharedFence[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.fences = value;
            obj.fenceCount = count;
        }
        if (kwargs.contains("signaled_values"))
        {
            auto _value = kwargs["signaled_values"].cast<std::vector<uint64_t>>();
            auto count = _value.size();
            auto value = new uint64_t[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.signaledValues = value;
            obj.fenceCount = count;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
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

py::class_<SharedTextureMemoryVkDedicatedAllocationDescriptor, ChainedStruct> _SharedTextureMemoryVkDedicatedAllocationDescriptor(m, "SharedTextureMemoryVkDedicatedAllocationDescriptor");
registry.on(m, "SharedTextureMemoryVkDedicatedAllocationDescriptor", _SharedTextureMemoryVkDedicatedAllocationDescriptor);

_SharedTextureMemoryVkDedicatedAllocationDescriptor
    .def_readwrite("next_in_chain", &pywgpu::SharedTextureMemoryVkDedicatedAllocationDescriptor::nextInChain)
    .def_readwrite("dedicated_allocation", &pywgpu::SharedTextureMemoryVkDedicatedAllocationDescriptor::dedicatedAllocation)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SharedTextureMemoryVkDedicatedAllocationDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "dedicated_allocation"};
        static const std::set<std::string> required = {"dedicated_allocation"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("dedicated_allocation"))
        {
            auto value = kwargs["dedicated_allocation"].cast<Bool>();
            obj.dedicatedAllocation = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SharedTextureMemoryAHardwareBufferDescriptor, ChainedStruct> _SharedTextureMemoryAHardwareBufferDescriptor(m, "SharedTextureMemoryAHardwareBufferDescriptor");
registry.on(m, "SharedTextureMemoryAHardwareBufferDescriptor", _SharedTextureMemoryAHardwareBufferDescriptor);

_SharedTextureMemoryAHardwareBufferDescriptor
    .def_readwrite("next_in_chain", &pywgpu::SharedTextureMemoryAHardwareBufferDescriptor::nextInChain)
    .def_readwrite("handle", &pywgpu::SharedTextureMemoryAHardwareBufferDescriptor::handle)
    .def_readwrite("use_external_format", &pywgpu::SharedTextureMemoryAHardwareBufferDescriptor::useExternalFormat)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SharedTextureMemoryAHardwareBufferDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "handle", "use_external_format"};
        static const std::set<std::string> required = {"handle", "use_external_format"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("handle"))
        {
            auto value = kwargs["handle"].cast<void *>();
            obj.handle = value;
        }
        if (kwargs.contains("use_external_format"))
        {
            auto value = kwargs["use_external_format"].cast<Bool>();
            obj.useExternalFormat = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SharedTextureMemoryDmaBufPlane> _SharedTextureMemoryDmaBufPlane(m, "SharedTextureMemoryDmaBufPlane");
registry.on(m, "SharedTextureMemoryDmaBufPlane", _SharedTextureMemoryDmaBufPlane);

_SharedTextureMemoryDmaBufPlane
    .def_readwrite("fd", &pywgpu::SharedTextureMemoryDmaBufPlane::fd)
    .def_readwrite("offset", &pywgpu::SharedTextureMemoryDmaBufPlane::offset)
    .def_readwrite("stride", &pywgpu::SharedTextureMemoryDmaBufPlane::stride)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SharedTextureMemoryDmaBufPlane obj{};
        static const std::set<std::string> allowed = {"fd", "offset", "stride"};
        static const std::set<std::string> required = {"fd", "offset", "stride"};
        
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
        
        if (kwargs.contains("fd"))
        {
            auto value = kwargs["fd"].cast<int>();
            obj.fd = value;
        }
        if (kwargs.contains("offset"))
        {
            auto value = kwargs["offset"].cast<uint64_t>();
            obj.offset = value;
        }
        if (kwargs.contains("stride"))
        {
            auto value = kwargs["stride"].cast<uint32_t>();
            obj.stride = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SharedTextureMemoryDmaBufDescriptor, ChainedStruct> _SharedTextureMemoryDmaBufDescriptor(m, "SharedTextureMemoryDmaBufDescriptor");
registry.on(m, "SharedTextureMemoryDmaBufDescriptor", _SharedTextureMemoryDmaBufDescriptor);

_SharedTextureMemoryDmaBufDescriptor
    .def_readwrite("next_in_chain", &pywgpu::SharedTextureMemoryDmaBufDescriptor::nextInChain)
    .def_readwrite("size", &pywgpu::SharedTextureMemoryDmaBufDescriptor::size)
    .def_readwrite("drm_format", &pywgpu::SharedTextureMemoryDmaBufDescriptor::drmFormat)
    .def_readwrite("drm_modifier", &pywgpu::SharedTextureMemoryDmaBufDescriptor::drmModifier)
    .def_readwrite("plane_count", &pywgpu::SharedTextureMemoryDmaBufDescriptor::planeCount)
    .def_readwrite("planes", &pywgpu::SharedTextureMemoryDmaBufDescriptor::planes)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SharedTextureMemoryDmaBufDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "size", "drm_format", "drm_modifier", "planes"};
        static const std::set<std::string> required = {"drm_format", "drm_modifier", "planes"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("size"))
        {
            auto value = kwargs["size"].cast<Extent3D>();
            obj.size = value;
        }
        if (kwargs.contains("drm_format"))
        {
            auto value = kwargs["drm_format"].cast<uint32_t>();
            obj.drmFormat = value;
        }
        if (kwargs.contains("drm_modifier"))
        {
            auto value = kwargs["drm_modifier"].cast<uint64_t>();
            obj.drmModifier = value;
        }
        if (kwargs.contains("planes"))
        {
            auto _value = kwargs["planes"].cast<std::vector<SharedTextureMemoryDmaBufPlane>>();
            auto count = _value.size();
            auto value = new SharedTextureMemoryDmaBufPlane[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.planes = value;
            obj.planeCount = count;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SharedTextureMemoryOpaqueFDDescriptor, ChainedStruct> _SharedTextureMemoryOpaqueFDDescriptor(m, "SharedTextureMemoryOpaqueFDDescriptor");
registry.on(m, "SharedTextureMemoryOpaqueFDDescriptor", _SharedTextureMemoryOpaqueFDDescriptor);

_SharedTextureMemoryOpaqueFDDescriptor
    .def_readwrite("next_in_chain", &pywgpu::SharedTextureMemoryOpaqueFDDescriptor::nextInChain)
    .def_readwrite("vk_image_create_info", &pywgpu::SharedTextureMemoryOpaqueFDDescriptor::vkImageCreateInfo)
    .def_readwrite("memory_FD", &pywgpu::SharedTextureMemoryOpaqueFDDescriptor::memoryFD)
    .def_readwrite("memory_type_index", &pywgpu::SharedTextureMemoryOpaqueFDDescriptor::memoryTypeIndex)
    .def_readwrite("allocation_size", &pywgpu::SharedTextureMemoryOpaqueFDDescriptor::allocationSize)
    .def_readwrite("dedicated_allocation", &pywgpu::SharedTextureMemoryOpaqueFDDescriptor::dedicatedAllocation)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SharedTextureMemoryOpaqueFDDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "vk_image_create_info", "memory_FD", "memory_type_index", "allocation_size", "dedicated_allocation"};
        static const std::set<std::string> required = {"vk_image_create_info", "memory_FD", "memory_type_index", "allocation_size", "dedicated_allocation"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("vk_image_create_info"))
        {
            auto value = kwargs["vk_image_create_info"].cast<void const *>();
            obj.vkImageCreateInfo = value;
        }
        if (kwargs.contains("memory_FD"))
        {
            auto value = kwargs["memory_FD"].cast<int>();
            obj.memoryFD = value;
        }
        if (kwargs.contains("memory_type_index"))
        {
            auto value = kwargs["memory_type_index"].cast<uint32_t>();
            obj.memoryTypeIndex = value;
        }
        if (kwargs.contains("allocation_size"))
        {
            auto value = kwargs["allocation_size"].cast<uint64_t>();
            obj.allocationSize = value;
        }
        if (kwargs.contains("dedicated_allocation"))
        {
            auto value = kwargs["dedicated_allocation"].cast<Bool>();
            obj.dedicatedAllocation = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SharedTextureMemoryZirconHandleDescriptor, ChainedStruct> _SharedTextureMemoryZirconHandleDescriptor(m, "SharedTextureMemoryZirconHandleDescriptor");
registry.on(m, "SharedTextureMemoryZirconHandleDescriptor", _SharedTextureMemoryZirconHandleDescriptor);

_SharedTextureMemoryZirconHandleDescriptor
    .def_readwrite("next_in_chain", &pywgpu::SharedTextureMemoryZirconHandleDescriptor::nextInChain)
    .def_readwrite("memory_FD", &pywgpu::SharedTextureMemoryZirconHandleDescriptor::memoryFD)
    .def_readwrite("allocation_size", &pywgpu::SharedTextureMemoryZirconHandleDescriptor::allocationSize)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SharedTextureMemoryZirconHandleDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "memory_FD", "allocation_size"};
        static const std::set<std::string> required = {"memory_FD", "allocation_size"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("memory_FD"))
        {
            auto value = kwargs["memory_FD"].cast<uint32_t>();
            obj.memoryFD = value;
        }
        if (kwargs.contains("allocation_size"))
        {
            auto value = kwargs["allocation_size"].cast<uint64_t>();
            obj.allocationSize = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SharedTextureMemoryDXGISharedHandleDescriptor, ChainedStruct> _SharedTextureMemoryDXGISharedHandleDescriptor(m, "SharedTextureMemoryDXGISharedHandleDescriptor");
registry.on(m, "SharedTextureMemoryDXGISharedHandleDescriptor", _SharedTextureMemoryDXGISharedHandleDescriptor);

_SharedTextureMemoryDXGISharedHandleDescriptor
    .def_readwrite("next_in_chain", &pywgpu::SharedTextureMemoryDXGISharedHandleDescriptor::nextInChain)
    .def_readwrite("handle", &pywgpu::SharedTextureMemoryDXGISharedHandleDescriptor::handle)
    .def_readwrite("use_keyed_mutex", &pywgpu::SharedTextureMemoryDXGISharedHandleDescriptor::useKeyedMutex)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SharedTextureMemoryDXGISharedHandleDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "handle", "use_keyed_mutex"};
        static const std::set<std::string> required = {"handle", "use_keyed_mutex"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("handle"))
        {
            auto value = kwargs["handle"].cast<void *>();
            obj.handle = value;
        }
        if (kwargs.contains("use_keyed_mutex"))
        {
            auto value = kwargs["use_keyed_mutex"].cast<Bool>();
            obj.useKeyedMutex = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SharedTextureMemoryIOSurfaceDescriptor, ChainedStruct> _SharedTextureMemoryIOSurfaceDescriptor(m, "SharedTextureMemoryIOSurfaceDescriptor");
registry.on(m, "SharedTextureMemoryIOSurfaceDescriptor", _SharedTextureMemoryIOSurfaceDescriptor);

_SharedTextureMemoryIOSurfaceDescriptor
    .def_readwrite("next_in_chain", &pywgpu::SharedTextureMemoryIOSurfaceDescriptor::nextInChain)
    .def_readwrite("io_surface", &pywgpu::SharedTextureMemoryIOSurfaceDescriptor::ioSurface)
    .def_readwrite("allow_storage_binding", &pywgpu::SharedTextureMemoryIOSurfaceDescriptor::allowStorageBinding)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SharedTextureMemoryIOSurfaceDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "io_surface", "allow_storage_binding"};
        static const std::set<std::string> required = {"io_surface"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("io_surface"))
        {
            auto value = kwargs["io_surface"].cast<void *>();
            obj.ioSurface = value;
        }
        if (kwargs.contains("allow_storage_binding"))
        {
            auto value = kwargs["allow_storage_binding"].cast<Bool>();
            obj.allowStorageBinding = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SharedTextureMemoryEGLImageDescriptor, ChainedStruct> _SharedTextureMemoryEGLImageDescriptor(m, "SharedTextureMemoryEGLImageDescriptor");
registry.on(m, "SharedTextureMemoryEGLImageDescriptor", _SharedTextureMemoryEGLImageDescriptor);

_SharedTextureMemoryEGLImageDescriptor
    .def_readwrite("next_in_chain", &pywgpu::SharedTextureMemoryEGLImageDescriptor::nextInChain)
    .def_readwrite("image", &pywgpu::SharedTextureMemoryEGLImageDescriptor::image)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SharedTextureMemoryEGLImageDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "image"};
        static const std::set<std::string> required = {"image"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("image"))
        {
            auto value = kwargs["image"].cast<void *>();
            obj.image = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SharedTextureMemoryBeginAccessDescriptor> _SharedTextureMemoryBeginAccessDescriptor(m, "SharedTextureMemoryBeginAccessDescriptor");
registry.on(m, "SharedTextureMemoryBeginAccessDescriptor", _SharedTextureMemoryBeginAccessDescriptor);

_SharedTextureMemoryBeginAccessDescriptor
    .def_readwrite("next_in_chain", &pywgpu::SharedTextureMemoryBeginAccessDescriptor::nextInChain)
    .def_readwrite("concurrent_read", &pywgpu::SharedTextureMemoryBeginAccessDescriptor::concurrentRead)
    .def_readwrite("initialized", &pywgpu::SharedTextureMemoryBeginAccessDescriptor::initialized)
    .def_readwrite("fence_count", &pywgpu::SharedTextureMemoryBeginAccessDescriptor::fenceCount)
    .def_readwrite("fences", &pywgpu::SharedTextureMemoryBeginAccessDescriptor::fences)
    .def_readwrite("signaled_values", &pywgpu::SharedTextureMemoryBeginAccessDescriptor::signaledValues)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SharedTextureMemoryBeginAccessDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "concurrent_read", "initialized", "fences", "signaled_values"};
        static const std::set<std::string> required = {"concurrent_read", "initialized", "fences", "signaled_values"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("concurrent_read"))
        {
            auto value = kwargs["concurrent_read"].cast<Bool>();
            obj.concurrentRead = value;
        }
        if (kwargs.contains("initialized"))
        {
            auto value = kwargs["initialized"].cast<Bool>();
            obj.initialized = value;
        }
        if (kwargs.contains("fences"))
        {
            auto _value = kwargs["fences"].cast<std::vector<SharedFence>>();
            auto count = _value.size();
            auto value = new SharedFence[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.fences = value;
            obj.fenceCount = count;
        }
        if (kwargs.contains("signaled_values"))
        {
            auto _value = kwargs["signaled_values"].cast<std::vector<uint64_t>>();
            auto count = _value.size();
            auto value = new uint64_t[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.signaledValues = value;
            obj.fenceCount = count;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
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

py::class_<SharedTextureMemoryVkImageLayoutBeginState, ChainedStruct> _SharedTextureMemoryVkImageLayoutBeginState(m, "SharedTextureMemoryVkImageLayoutBeginState");
registry.on(m, "SharedTextureMemoryVkImageLayoutBeginState", _SharedTextureMemoryVkImageLayoutBeginState);

_SharedTextureMemoryVkImageLayoutBeginState
    .def_readwrite("next_in_chain", &pywgpu::SharedTextureMemoryVkImageLayoutBeginState::nextInChain)
    .def_readwrite("old_layout", &pywgpu::SharedTextureMemoryVkImageLayoutBeginState::oldLayout)
    .def_readwrite("new_layout", &pywgpu::SharedTextureMemoryVkImageLayoutBeginState::newLayout)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SharedTextureMemoryVkImageLayoutBeginState obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "old_layout", "new_layout"};
        static const std::set<std::string> required = {"old_layout", "new_layout"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("old_layout"))
        {
            auto value = kwargs["old_layout"].cast<int32_t>();
            obj.oldLayout = value;
        }
        if (kwargs.contains("new_layout"))
        {
            auto value = kwargs["new_layout"].cast<int32_t>();
            obj.newLayout = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SharedTextureMemoryVkImageLayoutEndState, ChainedStructOut> _SharedTextureMemoryVkImageLayoutEndState(m, "SharedTextureMemoryVkImageLayoutEndState");
registry.on(m, "SharedTextureMemoryVkImageLayoutEndState", _SharedTextureMemoryVkImageLayoutEndState);

_SharedTextureMemoryVkImageLayoutEndState
    .def_readonly("next_in_chain", &pywgpu::SharedTextureMemoryVkImageLayoutEndState::nextInChain)
    .def_readonly("old_layout", &pywgpu::SharedTextureMemoryVkImageLayoutEndState::oldLayout)
    .def_readonly("new_layout", &pywgpu::SharedTextureMemoryVkImageLayoutEndState::newLayout)
    .def(py::init<>())
    ;

py::class_<SharedTextureMemoryD3DSwapchainBeginState, ChainedStruct> _SharedTextureMemoryD3DSwapchainBeginState(m, "SharedTextureMemoryD3DSwapchainBeginState");
registry.on(m, "SharedTextureMemoryD3DSwapchainBeginState", _SharedTextureMemoryD3DSwapchainBeginState);

_SharedTextureMemoryD3DSwapchainBeginState
    .def_readwrite("next_in_chain", &pywgpu::SharedTextureMemoryD3DSwapchainBeginState::nextInChain)
    .def_readwrite("is_swapchain", &pywgpu::SharedTextureMemoryD3DSwapchainBeginState::isSwapchain)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SharedTextureMemoryD3DSwapchainBeginState obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "is_swapchain"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("is_swapchain"))
        {
            auto value = kwargs["is_swapchain"].cast<Bool>();
            obj.isSwapchain = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SharedFenceDescriptor> _SharedFenceDescriptor(m, "SharedFenceDescriptor");
registry.on(m, "SharedFenceDescriptor", _SharedFenceDescriptor);

_SharedFenceDescriptor
    .def_readwrite("next_in_chain", &pywgpu::SharedFenceDescriptor::nextInChain)
    .def_readwrite("label", &pywgpu::SharedFenceDescriptor::label)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SharedFenceDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "label"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("label"))
        {
            auto value = kwargs["label"].cast<StringView>();
            obj.label = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SharedFenceVkSemaphoreOpaqueFDDescriptor, ChainedStruct> _SharedFenceVkSemaphoreOpaqueFDDescriptor(m, "SharedFenceVkSemaphoreOpaqueFDDescriptor");
registry.on(m, "SharedFenceVkSemaphoreOpaqueFDDescriptor", _SharedFenceVkSemaphoreOpaqueFDDescriptor);

_SharedFenceVkSemaphoreOpaqueFDDescriptor
    .def_readwrite("next_in_chain", &pywgpu::SharedFenceVkSemaphoreOpaqueFDDescriptor::nextInChain)
    .def_readwrite("handle", &pywgpu::SharedFenceVkSemaphoreOpaqueFDDescriptor::handle)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SharedFenceVkSemaphoreOpaqueFDDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "handle"};
        static const std::set<std::string> required = {"handle"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("handle"))
        {
            auto value = kwargs["handle"].cast<int>();
            obj.handle = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SharedFenceSyncFDDescriptor, ChainedStruct> _SharedFenceSyncFDDescriptor(m, "SharedFenceSyncFDDescriptor");
registry.on(m, "SharedFenceSyncFDDescriptor", _SharedFenceSyncFDDescriptor);

_SharedFenceSyncFDDescriptor
    .def_readwrite("next_in_chain", &pywgpu::SharedFenceSyncFDDescriptor::nextInChain)
    .def_readwrite("handle", &pywgpu::SharedFenceSyncFDDescriptor::handle)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SharedFenceSyncFDDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "handle"};
        static const std::set<std::string> required = {"handle"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("handle"))
        {
            auto value = kwargs["handle"].cast<int>();
            obj.handle = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SharedFenceVkSemaphoreZirconHandleDescriptor, ChainedStruct> _SharedFenceVkSemaphoreZirconHandleDescriptor(m, "SharedFenceVkSemaphoreZirconHandleDescriptor");
registry.on(m, "SharedFenceVkSemaphoreZirconHandleDescriptor", _SharedFenceVkSemaphoreZirconHandleDescriptor);

_SharedFenceVkSemaphoreZirconHandleDescriptor
    .def_readwrite("next_in_chain", &pywgpu::SharedFenceVkSemaphoreZirconHandleDescriptor::nextInChain)
    .def_readwrite("handle", &pywgpu::SharedFenceVkSemaphoreZirconHandleDescriptor::handle)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SharedFenceVkSemaphoreZirconHandleDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "handle"};
        static const std::set<std::string> required = {"handle"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("handle"))
        {
            auto value = kwargs["handle"].cast<uint32_t>();
            obj.handle = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SharedFenceDXGISharedHandleDescriptor, ChainedStruct> _SharedFenceDXGISharedHandleDescriptor(m, "SharedFenceDXGISharedHandleDescriptor");
registry.on(m, "SharedFenceDXGISharedHandleDescriptor", _SharedFenceDXGISharedHandleDescriptor);

_SharedFenceDXGISharedHandleDescriptor
    .def_readwrite("next_in_chain", &pywgpu::SharedFenceDXGISharedHandleDescriptor::nextInChain)
    .def_readwrite("handle", &pywgpu::SharedFenceDXGISharedHandleDescriptor::handle)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SharedFenceDXGISharedHandleDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "handle"};
        static const std::set<std::string> required = {"handle"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("handle"))
        {
            auto value = kwargs["handle"].cast<void *>();
            obj.handle = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SharedFenceMTLSharedEventDescriptor, ChainedStruct> _SharedFenceMTLSharedEventDescriptor(m, "SharedFenceMTLSharedEventDescriptor");
registry.on(m, "SharedFenceMTLSharedEventDescriptor", _SharedFenceMTLSharedEventDescriptor);

_SharedFenceMTLSharedEventDescriptor
    .def_readwrite("next_in_chain", &pywgpu::SharedFenceMTLSharedEventDescriptor::nextInChain)
    .def_readwrite("shared_event", &pywgpu::SharedFenceMTLSharedEventDescriptor::sharedEvent)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SharedFenceMTLSharedEventDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "shared_event"};
        static const std::set<std::string> required = {"shared_event"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("shared_event"))
        {
            auto value = kwargs["shared_event"].cast<void *>();
            obj.sharedEvent = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SharedFenceEGLSyncDescriptor, ChainedStruct> _SharedFenceEGLSyncDescriptor(m, "SharedFenceEGLSyncDescriptor");
registry.on(m, "SharedFenceEGLSyncDescriptor", _SharedFenceEGLSyncDescriptor);

_SharedFenceEGLSyncDescriptor
    .def_readwrite("next_in_chain", &pywgpu::SharedFenceEGLSyncDescriptor::nextInChain)
    .def_readwrite("sync", &pywgpu::SharedFenceEGLSyncDescriptor::sync)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SharedFenceEGLSyncDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "sync"};
        static const std::set<std::string> required = {"sync"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("sync"))
        {
            auto value = kwargs["sync"].cast<void *>();
            obj.sync = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<DawnFakeBufferOOMForTesting, ChainedStruct> _DawnFakeBufferOOMForTesting(m, "DawnFakeBufferOOMForTesting");
registry.on(m, "DawnFakeBufferOOMForTesting", _DawnFakeBufferOOMForTesting);

_DawnFakeBufferOOMForTesting
    .def_readwrite("next_in_chain", &pywgpu::DawnFakeBufferOOMForTesting::nextInChain)
    .def_readwrite("fake_OOM_at_wire_client_map", &pywgpu::DawnFakeBufferOOMForTesting::fakeOOMAtWireClientMap)
    .def_readwrite("fake_OOM_at_native_map", &pywgpu::DawnFakeBufferOOMForTesting::fakeOOMAtNativeMap)
    .def_readwrite("fake_OOM_at_device", &pywgpu::DawnFakeBufferOOMForTesting::fakeOOMAtDevice)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::DawnFakeBufferOOMForTesting obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "fake_OOM_at_wire_client_map", "fake_OOM_at_native_map", "fake_OOM_at_device"};
        static const std::set<std::string> required = {"fake_OOM_at_wire_client_map", "fake_OOM_at_native_map", "fake_OOM_at_device"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("fake_OOM_at_wire_client_map"))
        {
            auto value = kwargs["fake_OOM_at_wire_client_map"].cast<Bool>();
            obj.fakeOOMAtWireClientMap = value;
        }
        if (kwargs.contains("fake_OOM_at_native_map"))
        {
            auto value = kwargs["fake_OOM_at_native_map"].cast<Bool>();
            obj.fakeOOMAtNativeMap = value;
        }
        if (kwargs.contains("fake_OOM_at_device"))
        {
            auto value = kwargs["fake_OOM_at_device"].cast<Bool>();
            obj.fakeOOMAtDevice = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
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

py::class_<DawnDrmFormatProperties> _DawnDrmFormatProperties(m, "DawnDrmFormatProperties");
registry.on(m, "DawnDrmFormatProperties", _DawnDrmFormatProperties);

_DawnDrmFormatProperties
    .def_readwrite("modifier", &pywgpu::DawnDrmFormatProperties::modifier)
    .def_readwrite("modifier_plane_count", &pywgpu::DawnDrmFormatProperties::modifierPlaneCount)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::DawnDrmFormatProperties obj{};
        static const std::set<std::string> allowed = {"modifier", "modifier_plane_count"};
        static const std::set<std::string> required = {"modifier", "modifier_plane_count"};
        
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
        
        if (kwargs.contains("modifier"))
        {
            auto value = kwargs["modifier"].cast<uint64_t>();
            obj.modifier = value;
        }
        if (kwargs.contains("modifier_plane_count"))
        {
            auto value = kwargs["modifier_plane_count"].cast<uint32_t>();
            obj.modifierPlaneCount = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<TexelCopyBufferInfo> _TexelCopyBufferInfo(m, "TexelCopyBufferInfo");
registry.on(m, "TexelCopyBufferInfo", _TexelCopyBufferInfo);

_TexelCopyBufferInfo
    .def_readwrite("layout", &pywgpu::TexelCopyBufferInfo::layout)
    .def_readwrite("buffer", &pywgpu::TexelCopyBufferInfo::buffer)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::TexelCopyBufferInfo obj{};
        static const std::set<std::string> allowed = {"layout", "buffer"};
        static const std::set<std::string> required = {"buffer"};
        
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
        
        if (kwargs.contains("layout"))
        {
            auto value = kwargs["layout"].cast<TexelCopyBufferLayout>();
            obj.layout = value;
        }
        if (kwargs.contains("buffer"))
        {
            auto value = kwargs["buffer"].cast<Buffer>();
            obj.buffer = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<TexelCopyBufferLayout> _TexelCopyBufferLayout(m, "TexelCopyBufferLayout");
registry.on(m, "TexelCopyBufferLayout", _TexelCopyBufferLayout);

_TexelCopyBufferLayout
    .def_readwrite("offset", &pywgpu::TexelCopyBufferLayout::offset)
    .def_readwrite("bytes_per_row", &pywgpu::TexelCopyBufferLayout::bytesPerRow)
    .def_readwrite("rows_per_image", &pywgpu::TexelCopyBufferLayout::rowsPerImage)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::TexelCopyBufferLayout obj{};
        static const std::set<std::string> allowed = {"offset", "bytes_per_row", "rows_per_image"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("offset"))
        {
            auto value = kwargs["offset"].cast<uint64_t>();
            obj.offset = value;
        }
        if (kwargs.contains("bytes_per_row"))
        {
            auto value = kwargs["bytes_per_row"].cast<uint32_t>();
            obj.bytesPerRow = value;
        }
        if (kwargs.contains("rows_per_image"))
        {
            auto value = kwargs["rows_per_image"].cast<uint32_t>();
            obj.rowsPerImage = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<TexelCopyTextureInfo> _TexelCopyTextureInfo(m, "TexelCopyTextureInfo");
registry.on(m, "TexelCopyTextureInfo", _TexelCopyTextureInfo);

_TexelCopyTextureInfo
    .def_readwrite("texture", &pywgpu::TexelCopyTextureInfo::texture)
    .def_readwrite("mip_level", &pywgpu::TexelCopyTextureInfo::mipLevel)
    .def_readwrite("origin", &pywgpu::TexelCopyTextureInfo::origin)
    .def_readwrite("aspect", &pywgpu::TexelCopyTextureInfo::aspect)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::TexelCopyTextureInfo obj{};
        static const std::set<std::string> allowed = {"texture", "mip_level", "origin", "aspect"};
        static const std::set<std::string> required = {"texture"};
        
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
        
        if (kwargs.contains("texture"))
        {
            auto value = kwargs["texture"].cast<Texture>();
            obj.texture = value;
        }
        if (kwargs.contains("mip_level"))
        {
            auto value = kwargs["mip_level"].cast<uint32_t>();
            obj.mipLevel = value;
        }
        if (kwargs.contains("origin"))
        {
            auto value = kwargs["origin"].cast<Origin3D>();
            obj.origin = value;
        }
        if (kwargs.contains("aspect"))
        {
            auto value = kwargs["aspect"].cast<TextureAspect>();
            obj.aspect = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<ImageCopyExternalTexture> _ImageCopyExternalTexture(m, "ImageCopyExternalTexture");
registry.on(m, "ImageCopyExternalTexture", _ImageCopyExternalTexture);

_ImageCopyExternalTexture
    .def_readwrite("next_in_chain", &pywgpu::ImageCopyExternalTexture::nextInChain)
    .def_readwrite("external_texture", &pywgpu::ImageCopyExternalTexture::externalTexture)
    .def_readwrite("origin", &pywgpu::ImageCopyExternalTexture::origin)
    .def_readwrite("natural_size", &pywgpu::ImageCopyExternalTexture::naturalSize)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::ImageCopyExternalTexture obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "external_texture", "origin", "natural_size"};
        static const std::set<std::string> required = {"external_texture"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("external_texture"))
        {
            auto value = kwargs["external_texture"].cast<ExternalTexture>();
            obj.externalTexture = value;
        }
        if (kwargs.contains("origin"))
        {
            auto value = kwargs["origin"].cast<Origin3D>();
            obj.origin = value;
        }
        if (kwargs.contains("natural_size"))
        {
            auto value = kwargs["natural_size"].cast<Extent2D>();
            obj.naturalSize = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
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

py::class_<FutureWaitInfo> _FutureWaitInfo(m, "FutureWaitInfo");
registry.on(m, "FutureWaitInfo", _FutureWaitInfo);

_FutureWaitInfo
    .def_readwrite("future", &pywgpu::FutureWaitInfo::future)
    .def_readwrite("completed", &pywgpu::FutureWaitInfo::completed)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::FutureWaitInfo obj{};
        static const std::set<std::string> allowed = {"future", "completed"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("future"))
        {
            auto value = kwargs["future"].cast<Future>();
            obj.future = value;
        }
        if (kwargs.contains("completed"))
        {
            auto value = kwargs["completed"].cast<Bool>();
            obj.completed = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<InstanceCapabilities> _InstanceCapabilities(m, "InstanceCapabilities");
registry.on(m, "InstanceCapabilities", _InstanceCapabilities);

_InstanceCapabilities
    .def_readwrite("next_in_chain", &pywgpu::InstanceCapabilities::nextInChain)
    .def_readwrite("timed_wait_any_enable", &pywgpu::InstanceCapabilities::timedWaitAnyEnable)
    .def_readwrite("timed_wait_any_max_count", &pywgpu::InstanceCapabilities::timedWaitAnyMaxCount)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::InstanceCapabilities obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "timed_wait_any_enable", "timed_wait_any_max_count"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStructOut *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("timed_wait_any_enable"))
        {
            auto value = kwargs["timed_wait_any_enable"].cast<Bool>();
            obj.timedWaitAnyEnable = value;
        }
        if (kwargs.contains("timed_wait_any_max_count"))
        {
            auto value = kwargs["timed_wait_any_max_count"].cast<size_t>();
            obj.timedWaitAnyMaxCount = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<InstanceDescriptor> _InstanceDescriptor(m, "InstanceDescriptor");
registry.on(m, "InstanceDescriptor", _InstanceDescriptor);

_InstanceDescriptor
    .def_readwrite("next_in_chain", &pywgpu::InstanceDescriptor::nextInChain)
    .def_readwrite("capabilities", &pywgpu::InstanceDescriptor::capabilities)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::InstanceDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "capabilities"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("capabilities"))
        {
            auto value = kwargs["capabilities"].cast<InstanceCapabilities>();
            obj.capabilities = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<DawnWireWGSLControl, ChainedStruct> _DawnWireWGSLControl(m, "DawnWireWGSLControl");
registry.on(m, "DawnWireWGSLControl", _DawnWireWGSLControl);

_DawnWireWGSLControl
    .def_readwrite("next_in_chain", &pywgpu::DawnWireWGSLControl::nextInChain)
    .def_readwrite("enable_experimental", &pywgpu::DawnWireWGSLControl::enableExperimental)
    .def_readwrite("enable_unsafe", &pywgpu::DawnWireWGSLControl::enableUnsafe)
    .def_readwrite("enable_testing", &pywgpu::DawnWireWGSLControl::enableTesting)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::DawnWireWGSLControl obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "enable_experimental", "enable_unsafe", "enable_testing"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("enable_experimental"))
        {
            auto value = kwargs["enable_experimental"].cast<Bool>();
            obj.enableExperimental = value;
        }
        if (kwargs.contains("enable_unsafe"))
        {
            auto value = kwargs["enable_unsafe"].cast<Bool>();
            obj.enableUnsafe = value;
        }
        if (kwargs.contains("enable_testing"))
        {
            auto value = kwargs["enable_testing"].cast<Bool>();
            obj.enableTesting = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<DawnInjectedInvalidSType, ChainedStruct> _DawnInjectedInvalidSType(m, "DawnInjectedInvalidSType");
registry.on(m, "DawnInjectedInvalidSType", _DawnInjectedInvalidSType);

_DawnInjectedInvalidSType
    .def_readwrite("next_in_chain", &pywgpu::DawnInjectedInvalidSType::nextInChain)
    .def_readwrite("invalid_s_type", &pywgpu::DawnInjectedInvalidSType::invalidSType)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::DawnInjectedInvalidSType obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "invalid_s_type"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("invalid_s_type"))
        {
            auto value = kwargs["invalid_s_type"].cast<SType>();
            obj.invalidSType = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<VertexAttribute> _VertexAttribute(m, "VertexAttribute");
registry.on(m, "VertexAttribute", _VertexAttribute);

_VertexAttribute
    .def_readwrite("next_in_chain", &pywgpu::VertexAttribute::nextInChain)
    .def_readwrite("format", &pywgpu::VertexAttribute::format)
    .def_readwrite("offset", &pywgpu::VertexAttribute::offset)
    .def_readwrite("shader_location", &pywgpu::VertexAttribute::shaderLocation)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::VertexAttribute obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "format", "offset", "shader_location"};
        static const std::set<std::string> required = {"offset", "shader_location"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("format"))
        {
            auto value = kwargs["format"].cast<VertexFormat>();
            obj.format = value;
        }
        if (kwargs.contains("offset"))
        {
            auto value = kwargs["offset"].cast<uint64_t>();
            obj.offset = value;
        }
        if (kwargs.contains("shader_location"))
        {
            auto value = kwargs["shader_location"].cast<uint32_t>();
            obj.shaderLocation = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<VertexBufferLayout> _VertexBufferLayout(m, "VertexBufferLayout");
registry.on(m, "VertexBufferLayout", _VertexBufferLayout);

_VertexBufferLayout
    .def_readwrite("next_in_chain", &pywgpu::VertexBufferLayout::nextInChain)
    .def_readwrite("step_mode", &pywgpu::VertexBufferLayout::stepMode)
    .def_readwrite("array_stride", &pywgpu::VertexBufferLayout::arrayStride)
    .def_readwrite("attribute_count", &pywgpu::VertexBufferLayout::attributeCount)
    .def_readwrite("attributes", &pywgpu::VertexBufferLayout::attributes)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::VertexBufferLayout obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "step_mode", "array_stride", "attributes"};
        static const std::set<std::string> required = {"array_stride", "attributes"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("step_mode"))
        {
            auto value = kwargs["step_mode"].cast<VertexStepMode>();
            obj.stepMode = value;
        }
        if (kwargs.contains("array_stride"))
        {
            auto value = kwargs["array_stride"].cast<uint64_t>();
            obj.arrayStride = value;
        }
        if (kwargs.contains("attributes"))
        {
            auto _value = kwargs["attributes"].cast<std::vector<VertexAttribute>>();
            auto count = _value.size();
            auto value = new VertexAttribute[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.attributes = value;
            obj.attributeCount = count;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<Origin3D> _Origin3D(m, "Origin3D");
registry.on(m, "Origin3D", _Origin3D);

_Origin3D
    .def_readwrite("x", &pywgpu::Origin3D::x)
    .def_readwrite("y", &pywgpu::Origin3D::y)
    .def_readwrite("z", &pywgpu::Origin3D::z)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::Origin3D obj{};
        static const std::set<std::string> allowed = {"x", "y", "z"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("x"))
        {
            auto value = kwargs["x"].cast<uint32_t>();
            obj.x = value;
        }
        if (kwargs.contains("y"))
        {
            auto value = kwargs["y"].cast<uint32_t>();
            obj.y = value;
        }
        if (kwargs.contains("z"))
        {
            auto value = kwargs["z"].cast<uint32_t>();
            obj.z = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<Origin2D> _Origin2D(m, "Origin2D");
registry.on(m, "Origin2D", _Origin2D);

_Origin2D
    .def_readwrite("x", &pywgpu::Origin2D::x)
    .def_readwrite("y", &pywgpu::Origin2D::y)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::Origin2D obj{};
        static const std::set<std::string> allowed = {"x", "y"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("x"))
        {
            auto value = kwargs["x"].cast<uint32_t>();
            obj.x = value;
        }
        if (kwargs.contains("y"))
        {
            auto value = kwargs["y"].cast<uint32_t>();
            obj.y = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<PassTimestampWrites> _PassTimestampWrites(m, "PassTimestampWrites");
registry.on(m, "PassTimestampWrites", _PassTimestampWrites);

_PassTimestampWrites
    .def_readwrite("next_in_chain", &pywgpu::PassTimestampWrites::nextInChain)
    .def_readwrite("query_set", &pywgpu::PassTimestampWrites::querySet)
    .def_readwrite("beginning_of_pass_write_index", &pywgpu::PassTimestampWrites::beginningOfPassWriteIndex)
    .def_readwrite("end_of_pass_write_index", &pywgpu::PassTimestampWrites::endOfPassWriteIndex)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::PassTimestampWrites obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "query_set", "beginning_of_pass_write_index", "end_of_pass_write_index"};
        static const std::set<std::string> required = {"query_set"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("query_set"))
        {
            auto value = kwargs["query_set"].cast<QuerySet>();
            obj.querySet = value;
        }
        if (kwargs.contains("beginning_of_pass_write_index"))
        {
            auto value = kwargs["beginning_of_pass_write_index"].cast<uint32_t>();
            obj.beginningOfPassWriteIndex = value;
        }
        if (kwargs.contains("end_of_pass_write_index"))
        {
            auto value = kwargs["end_of_pass_write_index"].cast<uint32_t>();
            obj.endOfPassWriteIndex = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<PipelineLayoutDescriptor> _PipelineLayoutDescriptor(m, "PipelineLayoutDescriptor");
registry.on(m, "PipelineLayoutDescriptor", _PipelineLayoutDescriptor);

_PipelineLayoutDescriptor
    .def_readwrite("next_in_chain", &pywgpu::PipelineLayoutDescriptor::nextInChain)
    .def_readwrite("label", &pywgpu::PipelineLayoutDescriptor::label)
    .def_readwrite("bind_group_layout_count", &pywgpu::PipelineLayoutDescriptor::bindGroupLayoutCount)
    .def_readwrite("bind_group_layouts", &pywgpu::PipelineLayoutDescriptor::bindGroupLayouts)
    .def_readwrite("immediate_data_range_byte_size", &pywgpu::PipelineLayoutDescriptor::immediateDataRangeByteSize)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::PipelineLayoutDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "label", "bind_group_layouts", "immediate_data_range_byte_size"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("label"))
        {
            auto value = kwargs["label"].cast<StringView>();
            obj.label = value;
        }
        if (kwargs.contains("bind_group_layouts"))
        {
            auto _value = kwargs["bind_group_layouts"].cast<std::vector<BindGroupLayout>>();
            auto count = _value.size();
            auto value = new BindGroupLayout[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.bindGroupLayouts = value;
            obj.bindGroupLayoutCount = count;
        }
        if (kwargs.contains("immediate_data_range_byte_size"))
        {
            auto value = kwargs["immediate_data_range_byte_size"].cast<uint32_t>();
            obj.immediateDataRangeByteSize = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<PipelineLayoutPixelLocalStorage, ChainedStruct> _PipelineLayoutPixelLocalStorage(m, "PipelineLayoutPixelLocalStorage");
registry.on(m, "PipelineLayoutPixelLocalStorage", _PipelineLayoutPixelLocalStorage);

_PipelineLayoutPixelLocalStorage
    .def_readwrite("next_in_chain", &pywgpu::PipelineLayoutPixelLocalStorage::nextInChain)
    .def_readwrite("total_pixel_local_storage_size", &pywgpu::PipelineLayoutPixelLocalStorage::totalPixelLocalStorageSize)
    .def_readwrite("storage_attachment_count", &pywgpu::PipelineLayoutPixelLocalStorage::storageAttachmentCount)
    .def_readwrite("storage_attachments", &pywgpu::PipelineLayoutPixelLocalStorage::storageAttachments)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::PipelineLayoutPixelLocalStorage obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "total_pixel_local_storage_size", "storage_attachments"};
        static const std::set<std::string> required = {"total_pixel_local_storage_size"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("total_pixel_local_storage_size"))
        {
            auto value = kwargs["total_pixel_local_storage_size"].cast<uint64_t>();
            obj.totalPixelLocalStorageSize = value;
        }
        if (kwargs.contains("storage_attachments"))
        {
            auto _value = kwargs["storage_attachments"].cast<std::vector<PipelineLayoutStorageAttachment>>();
            auto count = _value.size();
            auto value = new PipelineLayoutStorageAttachment[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.storageAttachments = value;
            obj.storageAttachmentCount = count;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<PipelineLayoutStorageAttachment> _PipelineLayoutStorageAttachment(m, "PipelineLayoutStorageAttachment");
registry.on(m, "PipelineLayoutStorageAttachment", _PipelineLayoutStorageAttachment);

_PipelineLayoutStorageAttachment
    .def_readwrite("next_in_chain", &pywgpu::PipelineLayoutStorageAttachment::nextInChain)
    .def_readwrite("offset", &pywgpu::PipelineLayoutStorageAttachment::offset)
    .def_readwrite("format", &pywgpu::PipelineLayoutStorageAttachment::format)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::PipelineLayoutStorageAttachment obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "offset", "format"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("offset"))
        {
            auto value = kwargs["offset"].cast<uint64_t>();
            obj.offset = value;
        }
        if (kwargs.contains("format"))
        {
            auto value = kwargs["format"].cast<TextureFormat>();
            obj.format = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<ComputeState> _ComputeState(m, "ComputeState");
registry.on(m, "ComputeState", _ComputeState);

_ComputeState
    .def_readwrite("next_in_chain", &pywgpu::ComputeState::nextInChain)
    .def_readwrite("module", &pywgpu::ComputeState::module)
    .def_readwrite("entry_point", &pywgpu::ComputeState::entryPoint)
    .def_readwrite("constant_count", &pywgpu::ComputeState::constantCount)
    .def_readwrite("constants", &pywgpu::ComputeState::constants)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::ComputeState obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "module", "entry_point", "constants"};
        static const std::set<std::string> required = {"module"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("module"))
        {
            auto value = kwargs["module"].cast<ShaderModule>();
            obj.module = value;
        }
        if (kwargs.contains("entry_point"))
        {
            auto value = kwargs["entry_point"].cast<StringView>();
            obj.entryPoint = value;
        }
        if (kwargs.contains("constants"))
        {
            auto _value = kwargs["constants"].cast<std::vector<ConstantEntry>>();
            auto count = _value.size();
            auto value = new ConstantEntry[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.constants = value;
            obj.constantCount = count;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<QuerySetDescriptor> _QuerySetDescriptor(m, "QuerySetDescriptor");
registry.on(m, "QuerySetDescriptor", _QuerySetDescriptor);

_QuerySetDescriptor
    .def_readwrite("next_in_chain", &pywgpu::QuerySetDescriptor::nextInChain)
    .def_readwrite("label", &pywgpu::QuerySetDescriptor::label)
    .def_readwrite("type", &pywgpu::QuerySetDescriptor::type)
    .def_readwrite("count", &pywgpu::QuerySetDescriptor::count)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::QuerySetDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "label", "type", "count"};
        static const std::set<std::string> required = {"count"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("label"))
        {
            auto value = kwargs["label"].cast<StringView>();
            obj.label = value;
        }
        if (kwargs.contains("type"))
        {
            auto value = kwargs["type"].cast<QueryType>();
            obj.type = value;
        }
        if (kwargs.contains("count"))
        {
            auto value = kwargs["count"].cast<uint32_t>();
            obj.count = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<QueueDescriptor> _QueueDescriptor(m, "QueueDescriptor");
registry.on(m, "QueueDescriptor", _QueueDescriptor);

_QueueDescriptor
    .def_readwrite("next_in_chain", &pywgpu::QueueDescriptor::nextInChain)
    .def_readwrite("label", &pywgpu::QueueDescriptor::label)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::QueueDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "label"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("label"))
        {
            auto value = kwargs["label"].cast<StringView>();
            obj.label = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<RenderBundleDescriptor> _RenderBundleDescriptor(m, "RenderBundleDescriptor");
registry.on(m, "RenderBundleDescriptor", _RenderBundleDescriptor);

_RenderBundleDescriptor
    .def_readwrite("next_in_chain", &pywgpu::RenderBundleDescriptor::nextInChain)
    .def_readwrite("label", &pywgpu::RenderBundleDescriptor::label)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::RenderBundleDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "label"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("label"))
        {
            auto value = kwargs["label"].cast<StringView>();
            obj.label = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<RenderBundleEncoderDescriptor> _RenderBundleEncoderDescriptor(m, "RenderBundleEncoderDescriptor");
registry.on(m, "RenderBundleEncoderDescriptor", _RenderBundleEncoderDescriptor);

_RenderBundleEncoderDescriptor
    .def_readwrite("next_in_chain", &pywgpu::RenderBundleEncoderDescriptor::nextInChain)
    .def_readwrite("label", &pywgpu::RenderBundleEncoderDescriptor::label)
    .def_readwrite("color_format_count", &pywgpu::RenderBundleEncoderDescriptor::colorFormatCount)
    .def_readwrite("color_formats", &pywgpu::RenderBundleEncoderDescriptor::colorFormats)
    .def_readwrite("depth_stencil_format", &pywgpu::RenderBundleEncoderDescriptor::depthStencilFormat)
    .def_readwrite("sample_count", &pywgpu::RenderBundleEncoderDescriptor::sampleCount)
    .def_readwrite("depth_read_only", &pywgpu::RenderBundleEncoderDescriptor::depthReadOnly)
    .def_readwrite("stencil_read_only", &pywgpu::RenderBundleEncoderDescriptor::stencilReadOnly)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::RenderBundleEncoderDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "label", "color_formats", "depth_stencil_format", "sample_count", "depth_read_only", "stencil_read_only"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("label"))
        {
            auto value = kwargs["label"].cast<StringView>();
            obj.label = value;
        }
        if (kwargs.contains("color_formats"))
        {
            auto _value = kwargs["color_formats"].cast<std::vector<TextureFormat>>();
            auto count = _value.size();
            auto value = new TextureFormat[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.colorFormats = value;
            obj.colorFormatCount = count;
        }
        if (kwargs.contains("depth_stencil_format"))
        {
            auto value = kwargs["depth_stencil_format"].cast<TextureFormat>();
            obj.depthStencilFormat = value;
        }
        if (kwargs.contains("sample_count"))
        {
            auto value = kwargs["sample_count"].cast<uint32_t>();
            obj.sampleCount = value;
        }
        if (kwargs.contains("depth_read_only"))
        {
            auto value = kwargs["depth_read_only"].cast<Bool>();
            obj.depthReadOnly = value;
        }
        if (kwargs.contains("stencil_read_only"))
        {
            auto value = kwargs["stencil_read_only"].cast<Bool>();
            obj.stencilReadOnly = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<RenderPassColorAttachment> _RenderPassColorAttachment(m, "RenderPassColorAttachment");
registry.on(m, "RenderPassColorAttachment", _RenderPassColorAttachment);

_RenderPassColorAttachment
    .def_readwrite("next_in_chain", &pywgpu::RenderPassColorAttachment::nextInChain)
    .def_readwrite("view", &pywgpu::RenderPassColorAttachment::view)
    .def_readwrite("depth_slice", &pywgpu::RenderPassColorAttachment::depthSlice)
    .def_readwrite("resolve_target", &pywgpu::RenderPassColorAttachment::resolveTarget)
    .def_readwrite("load_op", &pywgpu::RenderPassColorAttachment::loadOp)
    .def_readwrite("store_op", &pywgpu::RenderPassColorAttachment::storeOp)
    .def_readwrite("clear_value", &pywgpu::RenderPassColorAttachment::clearValue)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::RenderPassColorAttachment obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "view", "depth_slice", "resolve_target", "load_op", "store_op", "clear_value"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("view"))
        {
            auto value = kwargs["view"].cast<TextureView>();
            obj.view = value;
        }
        if (kwargs.contains("depth_slice"))
        {
            auto value = kwargs["depth_slice"].cast<uint32_t>();
            obj.depthSlice = value;
        }
        if (kwargs.contains("resolve_target"))
        {
            auto value = kwargs["resolve_target"].cast<TextureView>();
            obj.resolveTarget = value;
        }
        if (kwargs.contains("load_op"))
        {
            auto value = kwargs["load_op"].cast<LoadOp>();
            obj.loadOp = value;
        }
        if (kwargs.contains("store_op"))
        {
            auto value = kwargs["store_op"].cast<StoreOp>();
            obj.storeOp = value;
        }
        if (kwargs.contains("clear_value"))
        {
            auto value = kwargs["clear_value"].cast<Color>();
            obj.clearValue = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<DawnRenderPassColorAttachmentRenderToSingleSampled, ChainedStruct> _DawnRenderPassColorAttachmentRenderToSingleSampled(m, "DawnRenderPassColorAttachmentRenderToSingleSampled");
registry.on(m, "DawnRenderPassColorAttachmentRenderToSingleSampled", _DawnRenderPassColorAttachmentRenderToSingleSampled);

_DawnRenderPassColorAttachmentRenderToSingleSampled
    .def_readwrite("next_in_chain", &pywgpu::DawnRenderPassColorAttachmentRenderToSingleSampled::nextInChain)
    .def_readwrite("implicit_sample_count", &pywgpu::DawnRenderPassColorAttachmentRenderToSingleSampled::implicitSampleCount)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::DawnRenderPassColorAttachmentRenderToSingleSampled obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "implicit_sample_count"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("implicit_sample_count"))
        {
            auto value = kwargs["implicit_sample_count"].cast<uint32_t>();
            obj.implicitSampleCount = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<RenderPassDepthStencilAttachment> _RenderPassDepthStencilAttachment(m, "RenderPassDepthStencilAttachment");
registry.on(m, "RenderPassDepthStencilAttachment", _RenderPassDepthStencilAttachment);

_RenderPassDepthStencilAttachment
    .def_readwrite("next_in_chain", &pywgpu::RenderPassDepthStencilAttachment::nextInChain)
    .def_readwrite("view", &pywgpu::RenderPassDepthStencilAttachment::view)
    .def_readwrite("depth_load_op", &pywgpu::RenderPassDepthStencilAttachment::depthLoadOp)
    .def_readwrite("depth_store_op", &pywgpu::RenderPassDepthStencilAttachment::depthStoreOp)
    .def_readwrite("depth_clear_value", &pywgpu::RenderPassDepthStencilAttachment::depthClearValue)
    .def_readwrite("depth_read_only", &pywgpu::RenderPassDepthStencilAttachment::depthReadOnly)
    .def_readwrite("stencil_load_op", &pywgpu::RenderPassDepthStencilAttachment::stencilLoadOp)
    .def_readwrite("stencil_store_op", &pywgpu::RenderPassDepthStencilAttachment::stencilStoreOp)
    .def_readwrite("stencil_clear_value", &pywgpu::RenderPassDepthStencilAttachment::stencilClearValue)
    .def_readwrite("stencil_read_only", &pywgpu::RenderPassDepthStencilAttachment::stencilReadOnly)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::RenderPassDepthStencilAttachment obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "view", "depth_load_op", "depth_store_op", "depth_clear_value", "depth_read_only", "stencil_load_op", "stencil_store_op", "stencil_clear_value", "stencil_read_only"};
        static const std::set<std::string> required = {"view"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("view"))
        {
            auto value = kwargs["view"].cast<TextureView>();
            obj.view = value;
        }
        if (kwargs.contains("depth_load_op"))
        {
            auto value = kwargs["depth_load_op"].cast<LoadOp>();
            obj.depthLoadOp = value;
        }
        if (kwargs.contains("depth_store_op"))
        {
            auto value = kwargs["depth_store_op"].cast<StoreOp>();
            obj.depthStoreOp = value;
        }
        if (kwargs.contains("depth_clear_value"))
        {
            auto value = kwargs["depth_clear_value"].cast<float>();
            obj.depthClearValue = value;
        }
        if (kwargs.contains("depth_read_only"))
        {
            auto value = kwargs["depth_read_only"].cast<Bool>();
            obj.depthReadOnly = value;
        }
        if (kwargs.contains("stencil_load_op"))
        {
            auto value = kwargs["stencil_load_op"].cast<LoadOp>();
            obj.stencilLoadOp = value;
        }
        if (kwargs.contains("stencil_store_op"))
        {
            auto value = kwargs["stencil_store_op"].cast<StoreOp>();
            obj.stencilStoreOp = value;
        }
        if (kwargs.contains("stencil_clear_value"))
        {
            auto value = kwargs["stencil_clear_value"].cast<uint32_t>();
            obj.stencilClearValue = value;
        }
        if (kwargs.contains("stencil_read_only"))
        {
            auto value = kwargs["stencil_read_only"].cast<Bool>();
            obj.stencilReadOnly = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<RenderPassDescriptor> _RenderPassDescriptor(m, "RenderPassDescriptor");
registry.on(m, "RenderPassDescriptor", _RenderPassDescriptor);

_RenderPassDescriptor
    .def_readwrite("next_in_chain", &pywgpu::RenderPassDescriptor::nextInChain)
    .def_readwrite("label", &pywgpu::RenderPassDescriptor::label)
    .def_readwrite("color_attachment_count", &pywgpu::RenderPassDescriptor::colorAttachmentCount)
    .def_readwrite("color_attachments", &pywgpu::RenderPassDescriptor::colorAttachments)
    .def_readwrite("depth_stencil_attachment", &pywgpu::RenderPassDescriptor::depthStencilAttachment)
    .def_readwrite("occlusion_query_set", &pywgpu::RenderPassDescriptor::occlusionQuerySet)
    .def_readwrite("timestamp_writes", &pywgpu::RenderPassDescriptor::timestampWrites)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::RenderPassDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "label", "color_attachments", "depth_stencil_attachment", "occlusion_query_set", "timestamp_writes"};
        static const std::set<std::string> required = {"color_attachments"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("label"))
        {
            auto value = kwargs["label"].cast<StringView>();
            obj.label = value;
        }
        if (kwargs.contains("color_attachments"))
        {
            auto _value = kwargs["color_attachments"].cast<std::vector<RenderPassColorAttachment>>();
            auto count = _value.size();
            auto value = new RenderPassColorAttachment[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.colorAttachments = value;
            obj.colorAttachmentCount = count;
        }
        if (kwargs.contains("depth_stencil_attachment"))
        {
            auto value = kwargs["depth_stencil_attachment"].cast<RenderPassDepthStencilAttachment const *>();
            obj.depthStencilAttachment = value;
        }
        if (kwargs.contains("occlusion_query_set"))
        {
            auto value = kwargs["occlusion_query_set"].cast<QuerySet>();
            obj.occlusionQuerySet = value;
        }
        if (kwargs.contains("timestamp_writes"))
        {
            auto value = kwargs["timestamp_writes"].cast<PassTimestampWrites const *>();
            obj.timestampWrites = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<RenderPassMaxDrawCount, ChainedStruct> _RenderPassMaxDrawCount(m, "RenderPassMaxDrawCount");
registry.on(m, "RenderPassMaxDrawCount", _RenderPassMaxDrawCount);

_RenderPassMaxDrawCount
    .def_readwrite("next_in_chain", &pywgpu::RenderPassMaxDrawCount::nextInChain)
    .def_readwrite("max_draw_count", &pywgpu::RenderPassMaxDrawCount::maxDrawCount)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::RenderPassMaxDrawCount obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "max_draw_count"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("max_draw_count"))
        {
            auto value = kwargs["max_draw_count"].cast<uint64_t>();
            obj.maxDrawCount = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<RenderPassDescriptorExpandResolveRect, ChainedStruct> _RenderPassDescriptorExpandResolveRect(m, "RenderPassDescriptorExpandResolveRect");
registry.on(m, "RenderPassDescriptorExpandResolveRect", _RenderPassDescriptorExpandResolveRect);

_RenderPassDescriptorExpandResolveRect
    .def_readwrite("next_in_chain", &pywgpu::RenderPassDescriptorExpandResolveRect::nextInChain)
    .def_readwrite("x", &pywgpu::RenderPassDescriptorExpandResolveRect::x)
    .def_readwrite("y", &pywgpu::RenderPassDescriptorExpandResolveRect::y)
    .def_readwrite("width", &pywgpu::RenderPassDescriptorExpandResolveRect::width)
    .def_readwrite("height", &pywgpu::RenderPassDescriptorExpandResolveRect::height)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::RenderPassDescriptorExpandResolveRect obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "x", "y", "width", "height"};
        static const std::set<std::string> required = {"x", "y", "width", "height"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("x"))
        {
            auto value = kwargs["x"].cast<uint32_t>();
            obj.x = value;
        }
        if (kwargs.contains("y"))
        {
            auto value = kwargs["y"].cast<uint32_t>();
            obj.y = value;
        }
        if (kwargs.contains("width"))
        {
            auto value = kwargs["width"].cast<uint32_t>();
            obj.width = value;
        }
        if (kwargs.contains("height"))
        {
            auto value = kwargs["height"].cast<uint32_t>();
            obj.height = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<RenderPassPixelLocalStorage, ChainedStruct> _RenderPassPixelLocalStorage(m, "RenderPassPixelLocalStorage");
registry.on(m, "RenderPassPixelLocalStorage", _RenderPassPixelLocalStorage);

_RenderPassPixelLocalStorage
    .def_readwrite("next_in_chain", &pywgpu::RenderPassPixelLocalStorage::nextInChain)
    .def_readwrite("total_pixel_local_storage_size", &pywgpu::RenderPassPixelLocalStorage::totalPixelLocalStorageSize)
    .def_readwrite("storage_attachment_count", &pywgpu::RenderPassPixelLocalStorage::storageAttachmentCount)
    .def_readwrite("storage_attachments", &pywgpu::RenderPassPixelLocalStorage::storageAttachments)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::RenderPassPixelLocalStorage obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "total_pixel_local_storage_size", "storage_attachments"};
        static const std::set<std::string> required = {"total_pixel_local_storage_size"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("total_pixel_local_storage_size"))
        {
            auto value = kwargs["total_pixel_local_storage_size"].cast<uint64_t>();
            obj.totalPixelLocalStorageSize = value;
        }
        if (kwargs.contains("storage_attachments"))
        {
            auto _value = kwargs["storage_attachments"].cast<std::vector<RenderPassStorageAttachment>>();
            auto count = _value.size();
            auto value = new RenderPassStorageAttachment[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.storageAttachments = value;
            obj.storageAttachmentCount = count;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<RenderPassStorageAttachment> _RenderPassStorageAttachment(m, "RenderPassStorageAttachment");
registry.on(m, "RenderPassStorageAttachment", _RenderPassStorageAttachment);

_RenderPassStorageAttachment
    .def_readwrite("next_in_chain", &pywgpu::RenderPassStorageAttachment::nextInChain)
    .def_readwrite("offset", &pywgpu::RenderPassStorageAttachment::offset)
    .def_readwrite("storage", &pywgpu::RenderPassStorageAttachment::storage)
    .def_readwrite("load_op", &pywgpu::RenderPassStorageAttachment::loadOp)
    .def_readwrite("store_op", &pywgpu::RenderPassStorageAttachment::storeOp)
    .def_readwrite("clear_value", &pywgpu::RenderPassStorageAttachment::clearValue)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::RenderPassStorageAttachment obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "offset", "storage", "load_op", "store_op", "clear_value"};
        static const std::set<std::string> required = {"storage"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("offset"))
        {
            auto value = kwargs["offset"].cast<uint64_t>();
            obj.offset = value;
        }
        if (kwargs.contains("storage"))
        {
            auto value = kwargs["storage"].cast<TextureView>();
            obj.storage = value;
        }
        if (kwargs.contains("load_op"))
        {
            auto value = kwargs["load_op"].cast<LoadOp>();
            obj.loadOp = value;
        }
        if (kwargs.contains("store_op"))
        {
            auto value = kwargs["store_op"].cast<StoreOp>();
            obj.storeOp = value;
        }
        if (kwargs.contains("clear_value"))
        {
            auto value = kwargs["clear_value"].cast<Color>();
            obj.clearValue = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<VertexState> _VertexState(m, "VertexState");
registry.on(m, "VertexState", _VertexState);

_VertexState
    .def_readwrite("next_in_chain", &pywgpu::VertexState::nextInChain)
    .def_readwrite("module", &pywgpu::VertexState::module)
    .def_readwrite("entry_point", &pywgpu::VertexState::entryPoint)
    .def_readwrite("constant_count", &pywgpu::VertexState::constantCount)
    .def_readwrite("constants", &pywgpu::VertexState::constants)
    .def_readwrite("buffer_count", &pywgpu::VertexState::bufferCount)
    .def_readwrite("buffers", &pywgpu::VertexState::buffers)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::VertexState obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "module", "entry_point", "constants", "buffers"};
        static const std::set<std::string> required = {"module"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("module"))
        {
            auto value = kwargs["module"].cast<ShaderModule>();
            obj.module = value;
        }
        if (kwargs.contains("entry_point"))
        {
            auto value = kwargs["entry_point"].cast<StringView>();
            obj.entryPoint = value;
        }
        if (kwargs.contains("constants"))
        {
            auto _value = kwargs["constants"].cast<std::vector<ConstantEntry>>();
            auto count = _value.size();
            auto value = new ConstantEntry[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.constants = value;
            obj.constantCount = count;
        }
        if (kwargs.contains("buffers"))
        {
            auto _value = kwargs["buffers"].cast<std::vector<VertexBufferLayout>>();
            auto count = _value.size();
            auto value = new VertexBufferLayout[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.buffers = value;
            obj.bufferCount = count;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<PrimitiveState> _PrimitiveState(m, "PrimitiveState");
registry.on(m, "PrimitiveState", _PrimitiveState);

_PrimitiveState
    .def_readwrite("next_in_chain", &pywgpu::PrimitiveState::nextInChain)
    .def_readwrite("topology", &pywgpu::PrimitiveState::topology)
    .def_readwrite("strip_index_format", &pywgpu::PrimitiveState::stripIndexFormat)
    .def_readwrite("front_face", &pywgpu::PrimitiveState::frontFace)
    .def_readwrite("cull_mode", &pywgpu::PrimitiveState::cullMode)
    .def_readwrite("unclipped_depth", &pywgpu::PrimitiveState::unclippedDepth)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::PrimitiveState obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "topology", "strip_index_format", "front_face", "cull_mode", "unclipped_depth"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("topology"))
        {
            auto value = kwargs["topology"].cast<PrimitiveTopology>();
            obj.topology = value;
        }
        if (kwargs.contains("strip_index_format"))
        {
            auto value = kwargs["strip_index_format"].cast<IndexFormat>();
            obj.stripIndexFormat = value;
        }
        if (kwargs.contains("front_face"))
        {
            auto value = kwargs["front_face"].cast<FrontFace>();
            obj.frontFace = value;
        }
        if (kwargs.contains("cull_mode"))
        {
            auto value = kwargs["cull_mode"].cast<CullMode>();
            obj.cullMode = value;
        }
        if (kwargs.contains("unclipped_depth"))
        {
            auto value = kwargs["unclipped_depth"].cast<Bool>();
            obj.unclippedDepth = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<DepthStencilState> _DepthStencilState(m, "DepthStencilState");
registry.on(m, "DepthStencilState", _DepthStencilState);

_DepthStencilState
    .def_readwrite("next_in_chain", &pywgpu::DepthStencilState::nextInChain)
    .def_readwrite("format", &pywgpu::DepthStencilState::format)
    .def_readwrite("depth_write_enabled", &pywgpu::DepthStencilState::depthWriteEnabled)
    .def_readwrite("depth_compare", &pywgpu::DepthStencilState::depthCompare)
    .def_readwrite("stencil_front", &pywgpu::DepthStencilState::stencilFront)
    .def_readwrite("stencil_back", &pywgpu::DepthStencilState::stencilBack)
    .def_readwrite("stencil_read_mask", &pywgpu::DepthStencilState::stencilReadMask)
    .def_readwrite("stencil_write_mask", &pywgpu::DepthStencilState::stencilWriteMask)
    .def_readwrite("depth_bias", &pywgpu::DepthStencilState::depthBias)
    .def_readwrite("depth_bias_slope_scale", &pywgpu::DepthStencilState::depthBiasSlopeScale)
    .def_readwrite("depth_bias_clamp", &pywgpu::DepthStencilState::depthBiasClamp)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::DepthStencilState obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "format", "depth_write_enabled", "depth_compare", "stencil_front", "stencil_back", "stencil_read_mask", "stencil_write_mask", "depth_bias", "depth_bias_slope_scale", "depth_bias_clamp"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("format"))
        {
            auto value = kwargs["format"].cast<TextureFormat>();
            obj.format = value;
        }
        if (kwargs.contains("depth_write_enabled"))
        {
            auto value = kwargs["depth_write_enabled"].cast<OptionalBool>();
            obj.depthWriteEnabled = value;
        }
        if (kwargs.contains("depth_compare"))
        {
            auto value = kwargs["depth_compare"].cast<CompareFunction>();
            obj.depthCompare = value;
        }
        if (kwargs.contains("stencil_front"))
        {
            auto value = kwargs["stencil_front"].cast<StencilFaceState>();
            obj.stencilFront = value;
        }
        if (kwargs.contains("stencil_back"))
        {
            auto value = kwargs["stencil_back"].cast<StencilFaceState>();
            obj.stencilBack = value;
        }
        if (kwargs.contains("stencil_read_mask"))
        {
            auto value = kwargs["stencil_read_mask"].cast<uint32_t>();
            obj.stencilReadMask = value;
        }
        if (kwargs.contains("stencil_write_mask"))
        {
            auto value = kwargs["stencil_write_mask"].cast<uint32_t>();
            obj.stencilWriteMask = value;
        }
        if (kwargs.contains("depth_bias"))
        {
            auto value = kwargs["depth_bias"].cast<int32_t>();
            obj.depthBias = value;
        }
        if (kwargs.contains("depth_bias_slope_scale"))
        {
            auto value = kwargs["depth_bias_slope_scale"].cast<float>();
            obj.depthBiasSlopeScale = value;
        }
        if (kwargs.contains("depth_bias_clamp"))
        {
            auto value = kwargs["depth_bias_clamp"].cast<float>();
            obj.depthBiasClamp = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<MultisampleState> _MultisampleState(m, "MultisampleState");
registry.on(m, "MultisampleState", _MultisampleState);

_MultisampleState
    .def_readwrite("next_in_chain", &pywgpu::MultisampleState::nextInChain)
    .def_readwrite("count", &pywgpu::MultisampleState::count)
    .def_readwrite("mask", &pywgpu::MultisampleState::mask)
    .def_readwrite("alpha_to_coverage_enabled", &pywgpu::MultisampleState::alphaToCoverageEnabled)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::MultisampleState obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "count", "mask", "alpha_to_coverage_enabled"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("count"))
        {
            auto value = kwargs["count"].cast<uint32_t>();
            obj.count = value;
        }
        if (kwargs.contains("mask"))
        {
            auto value = kwargs["mask"].cast<uint32_t>();
            obj.mask = value;
        }
        if (kwargs.contains("alpha_to_coverage_enabled"))
        {
            auto value = kwargs["alpha_to_coverage_enabled"].cast<Bool>();
            obj.alphaToCoverageEnabled = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<FragmentState> _FragmentState(m, "FragmentState");
registry.on(m, "FragmentState", _FragmentState);

_FragmentState
    .def_readwrite("next_in_chain", &pywgpu::FragmentState::nextInChain)
    .def_readwrite("module", &pywgpu::FragmentState::module)
    .def_readwrite("entry_point", &pywgpu::FragmentState::entryPoint)
    .def_readwrite("constant_count", &pywgpu::FragmentState::constantCount)
    .def_readwrite("constants", &pywgpu::FragmentState::constants)
    .def_readwrite("target_count", &pywgpu::FragmentState::targetCount)
    .def_readwrite("targets", &pywgpu::FragmentState::targets)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::FragmentState obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "module", "entry_point", "constants", "targets"};
        static const std::set<std::string> required = {"module", "targets"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("module"))
        {
            auto value = kwargs["module"].cast<ShaderModule>();
            obj.module = value;
        }
        if (kwargs.contains("entry_point"))
        {
            auto value = kwargs["entry_point"].cast<StringView>();
            obj.entryPoint = value;
        }
        if (kwargs.contains("constants"))
        {
            auto _value = kwargs["constants"].cast<std::vector<ConstantEntry>>();
            auto count = _value.size();
            auto value = new ConstantEntry[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.constants = value;
            obj.constantCount = count;
        }
        if (kwargs.contains("targets"))
        {
            auto _value = kwargs["targets"].cast<std::vector<ColorTargetState>>();
            auto count = _value.size();
            auto value = new ColorTargetState[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.targets = value;
            obj.targetCount = count;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<ColorTargetState> _ColorTargetState(m, "ColorTargetState");
registry.on(m, "ColorTargetState", _ColorTargetState);

_ColorTargetState
    .def_readwrite("next_in_chain", &pywgpu::ColorTargetState::nextInChain)
    .def_readwrite("format", &pywgpu::ColorTargetState::format)
    .def_readwrite("blend", &pywgpu::ColorTargetState::blend)
    .def_readwrite("write_mask", &pywgpu::ColorTargetState::writeMask)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::ColorTargetState obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "format", "blend", "write_mask"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("format"))
        {
            auto value = kwargs["format"].cast<TextureFormat>();
            obj.format = value;
        }
        if (kwargs.contains("blend"))
        {
            auto value = kwargs["blend"].cast<BlendState const *>();
            obj.blend = value;
        }
        if (kwargs.contains("write_mask"))
        {
            auto value = kwargs["write_mask"].cast<ColorWriteMask>();
            obj.writeMask = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<ColorTargetStateExpandResolveTextureDawn, ChainedStruct> _ColorTargetStateExpandResolveTextureDawn(m, "ColorTargetStateExpandResolveTextureDawn");
registry.on(m, "ColorTargetStateExpandResolveTextureDawn", _ColorTargetStateExpandResolveTextureDawn);

_ColorTargetStateExpandResolveTextureDawn
    .def_readwrite("next_in_chain", &pywgpu::ColorTargetStateExpandResolveTextureDawn::nextInChain)
    .def_readwrite("enabled", &pywgpu::ColorTargetStateExpandResolveTextureDawn::enabled)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::ColorTargetStateExpandResolveTextureDawn obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "enabled"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("enabled"))
        {
            auto value = kwargs["enabled"].cast<Bool>();
            obj.enabled = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<BlendState> _BlendState(m, "BlendState");
registry.on(m, "BlendState", _BlendState);

_BlendState
    .def_readwrite("color", &pywgpu::BlendState::color)
    .def_readwrite("alpha", &pywgpu::BlendState::alpha)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::BlendState obj{};
        static const std::set<std::string> allowed = {"color", "alpha"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("color"))
        {
            auto value = kwargs["color"].cast<BlendComponent>();
            obj.color = value;
        }
        if (kwargs.contains("alpha"))
        {
            auto value = kwargs["alpha"].cast<BlendComponent>();
            obj.alpha = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<RenderPipelineDescriptor> _RenderPipelineDescriptor(m, "RenderPipelineDescriptor");
registry.on(m, "RenderPipelineDescriptor", _RenderPipelineDescriptor);

_RenderPipelineDescriptor
    .def_readwrite("next_in_chain", &pywgpu::RenderPipelineDescriptor::nextInChain)
    .def_readwrite("label", &pywgpu::RenderPipelineDescriptor::label)
    .def_readwrite("layout", &pywgpu::RenderPipelineDescriptor::layout)
    .def_readwrite("vertex", &pywgpu::RenderPipelineDescriptor::vertex)
    .def_readwrite("primitive", &pywgpu::RenderPipelineDescriptor::primitive)
    .def_readwrite("depth_stencil", &pywgpu::RenderPipelineDescriptor::depthStencil)
    .def_readwrite("multisample", &pywgpu::RenderPipelineDescriptor::multisample)
    .def_readwrite("fragment", &pywgpu::RenderPipelineDescriptor::fragment)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::RenderPipelineDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "label", "layout", "vertex", "primitive", "depth_stencil", "multisample", "fragment"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("label"))
        {
            auto value = kwargs["label"].cast<StringView>();
            obj.label = value;
        }
        if (kwargs.contains("layout"))
        {
            auto value = kwargs["layout"].cast<PipelineLayout>();
            obj.layout = value;
        }
        if (kwargs.contains("vertex"))
        {
            auto value = kwargs["vertex"].cast<VertexState>();
            obj.vertex = value;
        }
        if (kwargs.contains("primitive"))
        {
            auto value = kwargs["primitive"].cast<PrimitiveState>();
            obj.primitive = value;
        }
        if (kwargs.contains("depth_stencil"))
        {
            auto value = kwargs["depth_stencil"].cast<DepthStencilState const *>();
            obj.depthStencil = value;
        }
        if (kwargs.contains("multisample"))
        {
            auto value = kwargs["multisample"].cast<MultisampleState>();
            obj.multisample = value;
        }
        if (kwargs.contains("fragment"))
        {
            auto value = kwargs["fragment"].cast<FragmentState const *>();
            obj.fragment = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SamplerDescriptor> _SamplerDescriptor(m, "SamplerDescriptor");
registry.on(m, "SamplerDescriptor", _SamplerDescriptor);

_SamplerDescriptor
    .def_readwrite("next_in_chain", &pywgpu::SamplerDescriptor::nextInChain)
    .def_readwrite("label", &pywgpu::SamplerDescriptor::label)
    .def_readwrite("address_mode_u", &pywgpu::SamplerDescriptor::addressModeU)
    .def_readwrite("address_mode_v", &pywgpu::SamplerDescriptor::addressModeV)
    .def_readwrite("address_mode_w", &pywgpu::SamplerDescriptor::addressModeW)
    .def_readwrite("mag_filter", &pywgpu::SamplerDescriptor::magFilter)
    .def_readwrite("min_filter", &pywgpu::SamplerDescriptor::minFilter)
    .def_readwrite("mipmap_filter", &pywgpu::SamplerDescriptor::mipmapFilter)
    .def_readwrite("lod_min_clamp", &pywgpu::SamplerDescriptor::lodMinClamp)
    .def_readwrite("lod_max_clamp", &pywgpu::SamplerDescriptor::lodMaxClamp)
    .def_readwrite("compare", &pywgpu::SamplerDescriptor::compare)
    .def_readwrite("max_anisotropy", &pywgpu::SamplerDescriptor::maxAnisotropy)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SamplerDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "label", "address_mode_u", "address_mode_v", "address_mode_w", "mag_filter", "min_filter", "mipmap_filter", "lod_min_clamp", "lod_max_clamp", "compare", "max_anisotropy"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("label"))
        {
            auto value = kwargs["label"].cast<StringView>();
            obj.label = value;
        }
        if (kwargs.contains("address_mode_u"))
        {
            auto value = kwargs["address_mode_u"].cast<AddressMode>();
            obj.addressModeU = value;
        }
        if (kwargs.contains("address_mode_v"))
        {
            auto value = kwargs["address_mode_v"].cast<AddressMode>();
            obj.addressModeV = value;
        }
        if (kwargs.contains("address_mode_w"))
        {
            auto value = kwargs["address_mode_w"].cast<AddressMode>();
            obj.addressModeW = value;
        }
        if (kwargs.contains("mag_filter"))
        {
            auto value = kwargs["mag_filter"].cast<FilterMode>();
            obj.magFilter = value;
        }
        if (kwargs.contains("min_filter"))
        {
            auto value = kwargs["min_filter"].cast<FilterMode>();
            obj.minFilter = value;
        }
        if (kwargs.contains("mipmap_filter"))
        {
            auto value = kwargs["mipmap_filter"].cast<MipmapFilterMode>();
            obj.mipmapFilter = value;
        }
        if (kwargs.contains("lod_min_clamp"))
        {
            auto value = kwargs["lod_min_clamp"].cast<float>();
            obj.lodMinClamp = value;
        }
        if (kwargs.contains("lod_max_clamp"))
        {
            auto value = kwargs["lod_max_clamp"].cast<float>();
            obj.lodMaxClamp = value;
        }
        if (kwargs.contains("compare"))
        {
            auto value = kwargs["compare"].cast<CompareFunction>();
            obj.compare = value;
        }
        if (kwargs.contains("max_anisotropy"))
        {
            auto value = kwargs["max_anisotropy"].cast<uint16_t>();
            obj.maxAnisotropy = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<ShaderModuleDescriptor> _ShaderModuleDescriptor(m, "ShaderModuleDescriptor");
registry.on(m, "ShaderModuleDescriptor", _ShaderModuleDescriptor);

_ShaderModuleDescriptor
    .def_readwrite("next_in_chain", &pywgpu::ShaderModuleDescriptor::nextInChain)
    .def_readwrite("label", &pywgpu::ShaderModuleDescriptor::label)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::ShaderModuleDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "label"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("label"))
        {
            auto value = kwargs["label"].cast<StringView>();
            obj.label = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<ShaderSourceSPIRV, ChainedStruct> _ShaderSourceSPIRV(m, "ShaderSourceSPIRV");
registry.on(m, "ShaderSourceSPIRV", _ShaderSourceSPIRV);

_ShaderSourceSPIRV
    .def_readwrite("next_in_chain", &pywgpu::ShaderSourceSPIRV::nextInChain)
    .def_readwrite("code_size", &pywgpu::ShaderSourceSPIRV::codeSize)
    .def_readwrite("code", &pywgpu::ShaderSourceSPIRV::code)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::ShaderSourceSPIRV obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "code"};
        static const std::set<std::string> required = {"code"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("code"))
        {
            auto _value = kwargs["code"].cast<std::vector<uint32_t>>();
            auto count = _value.size();
            auto value = new uint32_t[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.code = value;
            obj.codeSize = count;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<ShaderSourceWGSL, ChainedStruct> _ShaderSourceWGSL(m, "ShaderSourceWGSL");
registry.on(m, "ShaderSourceWGSL", _ShaderSourceWGSL);

_ShaderSourceWGSL
    .def_readwrite("next_in_chain", &pywgpu::ShaderSourceWGSL::nextInChain)
    .def_readwrite("code", &pywgpu::ShaderSourceWGSL::code)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::ShaderSourceWGSL obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "code"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("code"))
        {
            auto value = kwargs["code"].cast<StringView>();
            obj.code = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<DawnShaderModuleSPIRVOptionsDescriptor, ChainedStruct> _DawnShaderModuleSPIRVOptionsDescriptor(m, "DawnShaderModuleSPIRVOptionsDescriptor");
registry.on(m, "DawnShaderModuleSPIRVOptionsDescriptor", _DawnShaderModuleSPIRVOptionsDescriptor);

_DawnShaderModuleSPIRVOptionsDescriptor
    .def_readwrite("next_in_chain", &pywgpu::DawnShaderModuleSPIRVOptionsDescriptor::nextInChain)
    .def_readwrite("allow_non_uniform_derivatives", &pywgpu::DawnShaderModuleSPIRVOptionsDescriptor::allowNonUniformDerivatives)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::DawnShaderModuleSPIRVOptionsDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "allow_non_uniform_derivatives"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("allow_non_uniform_derivatives"))
        {
            auto value = kwargs["allow_non_uniform_derivatives"].cast<Bool>();
            obj.allowNonUniformDerivatives = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<ShaderModuleCompilationOptions, ChainedStruct> _ShaderModuleCompilationOptions(m, "ShaderModuleCompilationOptions");
registry.on(m, "ShaderModuleCompilationOptions", _ShaderModuleCompilationOptions);

_ShaderModuleCompilationOptions
    .def_readwrite("next_in_chain", &pywgpu::ShaderModuleCompilationOptions::nextInChain)
    .def_readwrite("strict_math", &pywgpu::ShaderModuleCompilationOptions::strictMath)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::ShaderModuleCompilationOptions obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "strict_math"};
        static const std::set<std::string> required = {"strict_math"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("strict_math"))
        {
            auto value = kwargs["strict_math"].cast<Bool>();
            obj.strictMath = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<StencilFaceState> _StencilFaceState(m, "StencilFaceState");
registry.on(m, "StencilFaceState", _StencilFaceState);

_StencilFaceState
    .def_readwrite("compare", &pywgpu::StencilFaceState::compare)
    .def_readwrite("fail_op", &pywgpu::StencilFaceState::failOp)
    .def_readwrite("depth_fail_op", &pywgpu::StencilFaceState::depthFailOp)
    .def_readwrite("pass_op", &pywgpu::StencilFaceState::passOp)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::StencilFaceState obj{};
        static const std::set<std::string> allowed = {"compare", "fail_op", "depth_fail_op", "pass_op"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("compare"))
        {
            auto value = kwargs["compare"].cast<CompareFunction>();
            obj.compare = value;
        }
        if (kwargs.contains("fail_op"))
        {
            auto value = kwargs["fail_op"].cast<StencilOperation>();
            obj.failOp = value;
        }
        if (kwargs.contains("depth_fail_op"))
        {
            auto value = kwargs["depth_fail_op"].cast<StencilOperation>();
            obj.depthFailOp = value;
        }
        if (kwargs.contains("pass_op"))
        {
            auto value = kwargs["pass_op"].cast<StencilOperation>();
            obj.passOp = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SurfaceDescriptor> _SurfaceDescriptor(m, "SurfaceDescriptor");
registry.on(m, "SurfaceDescriptor", _SurfaceDescriptor);

_SurfaceDescriptor
    .def_readwrite("next_in_chain", &pywgpu::SurfaceDescriptor::nextInChain)
    .def_readwrite("label", &pywgpu::SurfaceDescriptor::label)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SurfaceDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "label"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("label"))
        {
            auto value = kwargs["label"].cast<StringView>();
            obj.label = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SurfaceSourceAndroidNativeWindow, ChainedStruct> _SurfaceSourceAndroidNativeWindow(m, "SurfaceSourceAndroidNativeWindow");
registry.on(m, "SurfaceSourceAndroidNativeWindow", _SurfaceSourceAndroidNativeWindow);

_SurfaceSourceAndroidNativeWindow
    .def_readwrite("next_in_chain", &pywgpu::SurfaceSourceAndroidNativeWindow::nextInChain)
    .def_readwrite("window", &pywgpu::SurfaceSourceAndroidNativeWindow::window)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SurfaceSourceAndroidNativeWindow obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "window"};
        static const std::set<std::string> required = {"window"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("window"))
        {
            auto value = kwargs["window"].cast<void *>();
            obj.window = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<EmscriptenSurfaceSourceCanvasHTMLSelector, ChainedStruct> _EmscriptenSurfaceSourceCanvasHTMLSelector(m, "EmscriptenSurfaceSourceCanvasHTMLSelector");
registry.on(m, "EmscriptenSurfaceSourceCanvasHTMLSelector", _EmscriptenSurfaceSourceCanvasHTMLSelector);

_EmscriptenSurfaceSourceCanvasHTMLSelector
    .def_readwrite("next_in_chain", &pywgpu::EmscriptenSurfaceSourceCanvasHTMLSelector::nextInChain)
    .def_readwrite("selector", &pywgpu::EmscriptenSurfaceSourceCanvasHTMLSelector::selector)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::EmscriptenSurfaceSourceCanvasHTMLSelector obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "selector"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("selector"))
        {
            auto value = kwargs["selector"].cast<StringView>();
            obj.selector = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SurfaceSourceMetalLayer, ChainedStruct> _SurfaceSourceMetalLayer(m, "SurfaceSourceMetalLayer");
registry.on(m, "SurfaceSourceMetalLayer", _SurfaceSourceMetalLayer);

_SurfaceSourceMetalLayer
    .def_readwrite("next_in_chain", &pywgpu::SurfaceSourceMetalLayer::nextInChain)
    .def_readwrite("layer", &pywgpu::SurfaceSourceMetalLayer::layer)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SurfaceSourceMetalLayer obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "layer"};
        static const std::set<std::string> required = {"layer"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("layer"))
        {
            auto value = kwargs["layer"].cast<void *>();
            obj.layer = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SurfaceSourceWindowsHWND, ChainedStruct> _SurfaceSourceWindowsHWND(m, "SurfaceSourceWindowsHWND");
registry.on(m, "SurfaceSourceWindowsHWND", _SurfaceSourceWindowsHWND);

_SurfaceSourceWindowsHWND
    .def_readwrite("next_in_chain", &pywgpu::SurfaceSourceWindowsHWND::nextInChain)
    .def_readwrite("hinstance", &pywgpu::SurfaceSourceWindowsHWND::hinstance)
    .def_readwrite("hwnd", &pywgpu::SurfaceSourceWindowsHWND::hwnd)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SurfaceSourceWindowsHWND obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "hinstance", "hwnd"};
        static const std::set<std::string> required = {"hinstance", "hwnd"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("hinstance"))
        {
            auto value = kwargs["hinstance"].cast<void *>();
            obj.hinstance = value;
        }
        if (kwargs.contains("hwnd"))
        {
            auto value = kwargs["hwnd"].cast<void *>();
            obj.hwnd = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SurfaceSourceXCBWindow, ChainedStruct> _SurfaceSourceXCBWindow(m, "SurfaceSourceXCBWindow");
registry.on(m, "SurfaceSourceXCBWindow", _SurfaceSourceXCBWindow);

_SurfaceSourceXCBWindow
    .def_readwrite("next_in_chain", &pywgpu::SurfaceSourceXCBWindow::nextInChain)
    .def_readwrite("connection", &pywgpu::SurfaceSourceXCBWindow::connection)
    .def_readwrite("window", &pywgpu::SurfaceSourceXCBWindow::window)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SurfaceSourceXCBWindow obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "connection", "window"};
        static const std::set<std::string> required = {"connection", "window"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("connection"))
        {
            auto value = kwargs["connection"].cast<void *>();
            obj.connection = value;
        }
        if (kwargs.contains("window"))
        {
            auto value = kwargs["window"].cast<uint32_t>();
            obj.window = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SurfaceSourceXlibWindow, ChainedStruct> _SurfaceSourceXlibWindow(m, "SurfaceSourceXlibWindow");
registry.on(m, "SurfaceSourceXlibWindow", _SurfaceSourceXlibWindow);

_SurfaceSourceXlibWindow
    .def_readwrite("next_in_chain", &pywgpu::SurfaceSourceXlibWindow::nextInChain)
    .def_readwrite("display", &pywgpu::SurfaceSourceXlibWindow::display)
    .def_readwrite("window", &pywgpu::SurfaceSourceXlibWindow::window)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SurfaceSourceXlibWindow obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "display", "window"};
        static const std::set<std::string> required = {"display", "window"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("display"))
        {
            auto value = kwargs["display"].cast<void *>();
            obj.display = value;
        }
        if (kwargs.contains("window"))
        {
            auto value = kwargs["window"].cast<uint64_t>();
            obj.window = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SurfaceSourceWaylandSurface, ChainedStruct> _SurfaceSourceWaylandSurface(m, "SurfaceSourceWaylandSurface");
registry.on(m, "SurfaceSourceWaylandSurface", _SurfaceSourceWaylandSurface);

_SurfaceSourceWaylandSurface
    .def_readwrite("next_in_chain", &pywgpu::SurfaceSourceWaylandSurface::nextInChain)
    .def_readwrite("display", &pywgpu::SurfaceSourceWaylandSurface::display)
    .def_readwrite("surface", &pywgpu::SurfaceSourceWaylandSurface::surface)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SurfaceSourceWaylandSurface obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "display", "surface"};
        static const std::set<std::string> required = {"display", "surface"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("display"))
        {
            auto value = kwargs["display"].cast<void *>();
            obj.display = value;
        }
        if (kwargs.contains("surface"))
        {
            auto value = kwargs["surface"].cast<void *>();
            obj.surface = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SurfaceDescriptorFromWindowsCoreWindow, ChainedStruct> _SurfaceDescriptorFromWindowsCoreWindow(m, "SurfaceDescriptorFromWindowsCoreWindow");
registry.on(m, "SurfaceDescriptorFromWindowsCoreWindow", _SurfaceDescriptorFromWindowsCoreWindow);

_SurfaceDescriptorFromWindowsCoreWindow
    .def_readwrite("next_in_chain", &pywgpu::SurfaceDescriptorFromWindowsCoreWindow::nextInChain)
    .def_readwrite("core_window", &pywgpu::SurfaceDescriptorFromWindowsCoreWindow::coreWindow)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SurfaceDescriptorFromWindowsCoreWindow obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "core_window"};
        static const std::set<std::string> required = {"core_window"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("core_window"))
        {
            auto value = kwargs["core_window"].cast<void *>();
            obj.coreWindow = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SurfaceDescriptorFromWindowsUWPSwapChainPanel, ChainedStruct> _SurfaceDescriptorFromWindowsUWPSwapChainPanel(m, "SurfaceDescriptorFromWindowsUWPSwapChainPanel");
registry.on(m, "SurfaceDescriptorFromWindowsUWPSwapChainPanel", _SurfaceDescriptorFromWindowsUWPSwapChainPanel);

_SurfaceDescriptorFromWindowsUWPSwapChainPanel
    .def_readwrite("next_in_chain", &pywgpu::SurfaceDescriptorFromWindowsUWPSwapChainPanel::nextInChain)
    .def_readwrite("swap_chain_panel", &pywgpu::SurfaceDescriptorFromWindowsUWPSwapChainPanel::swapChainPanel)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SurfaceDescriptorFromWindowsUWPSwapChainPanel obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "swap_chain_panel"};
        static const std::set<std::string> required = {"swap_chain_panel"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("swap_chain_panel"))
        {
            auto value = kwargs["swap_chain_panel"].cast<void *>();
            obj.swapChainPanel = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SurfaceDescriptorFromWindowsWinUISwapChainPanel, ChainedStruct> _SurfaceDescriptorFromWindowsWinUISwapChainPanel(m, "SurfaceDescriptorFromWindowsWinUISwapChainPanel");
registry.on(m, "SurfaceDescriptorFromWindowsWinUISwapChainPanel", _SurfaceDescriptorFromWindowsWinUISwapChainPanel);

_SurfaceDescriptorFromWindowsWinUISwapChainPanel
    .def_readwrite("next_in_chain", &pywgpu::SurfaceDescriptorFromWindowsWinUISwapChainPanel::nextInChain)
    .def_readwrite("swap_chain_panel", &pywgpu::SurfaceDescriptorFromWindowsWinUISwapChainPanel::swapChainPanel)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SurfaceDescriptorFromWindowsWinUISwapChainPanel obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "swap_chain_panel"};
        static const std::set<std::string> required = {"swap_chain_panel"};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("swap_chain_panel"))
        {
            auto value = kwargs["swap_chain_panel"].cast<void *>();
            obj.swapChainPanel = value;
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

py::class_<TextureDescriptor> _TextureDescriptor(m, "TextureDescriptor");
registry.on(m, "TextureDescriptor", _TextureDescriptor);

_TextureDescriptor
    .def_readwrite("next_in_chain", &pywgpu::TextureDescriptor::nextInChain)
    .def_readwrite("label", &pywgpu::TextureDescriptor::label)
    .def_readwrite("usage", &pywgpu::TextureDescriptor::usage)
    .def_readwrite("dimension", &pywgpu::TextureDescriptor::dimension)
    .def_readwrite("size", &pywgpu::TextureDescriptor::size)
    .def_readwrite("format", &pywgpu::TextureDescriptor::format)
    .def_readwrite("mip_level_count", &pywgpu::TextureDescriptor::mipLevelCount)
    .def_readwrite("sample_count", &pywgpu::TextureDescriptor::sampleCount)
    .def_readwrite("view_format_count", &pywgpu::TextureDescriptor::viewFormatCount)
    .def_readwrite("view_formats", &pywgpu::TextureDescriptor::viewFormats)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::TextureDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "label", "usage", "dimension", "size", "format", "mip_level_count", "sample_count", "view_formats"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("label"))
        {
            auto value = kwargs["label"].cast<StringView>();
            obj.label = value;
        }
        if (kwargs.contains("usage"))
        {
            auto value = kwargs["usage"].cast<TextureUsage>();
            obj.usage = value;
        }
        if (kwargs.contains("dimension"))
        {
            auto value = kwargs["dimension"].cast<TextureDimension>();
            obj.dimension = value;
        }
        if (kwargs.contains("size"))
        {
            auto value = kwargs["size"].cast<Extent3D>();
            obj.size = value;
        }
        if (kwargs.contains("format"))
        {
            auto value = kwargs["format"].cast<TextureFormat>();
            obj.format = value;
        }
        if (kwargs.contains("mip_level_count"))
        {
            auto value = kwargs["mip_level_count"].cast<uint32_t>();
            obj.mipLevelCount = value;
        }
        if (kwargs.contains("sample_count"))
        {
            auto value = kwargs["sample_count"].cast<uint32_t>();
            obj.sampleCount = value;
        }
        if (kwargs.contains("view_formats"))
        {
            auto _value = kwargs["view_formats"].cast<std::vector<TextureFormat>>();
            auto count = _value.size();
            auto value = new TextureFormat[count];
            std::copy(_value.begin(), _value.end(), value);
            obj.viewFormats = value;
            obj.viewFormatCount = count;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<TextureBindingViewDimensionDescriptor, ChainedStruct> _TextureBindingViewDimensionDescriptor(m, "TextureBindingViewDimensionDescriptor");
registry.on(m, "TextureBindingViewDimensionDescriptor", _TextureBindingViewDimensionDescriptor);

_TextureBindingViewDimensionDescriptor
    .def_readwrite("next_in_chain", &pywgpu::TextureBindingViewDimensionDescriptor::nextInChain)
    .def_readwrite("texture_binding_view_dimension", &pywgpu::TextureBindingViewDimensionDescriptor::textureBindingViewDimension)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::TextureBindingViewDimensionDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "texture_binding_view_dimension"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("texture_binding_view_dimension"))
        {
            auto value = kwargs["texture_binding_view_dimension"].cast<TextureViewDimension>();
            obj.textureBindingViewDimension = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<TextureViewDescriptor> _TextureViewDescriptor(m, "TextureViewDescriptor");
registry.on(m, "TextureViewDescriptor", _TextureViewDescriptor);

_TextureViewDescriptor
    .def_readwrite("next_in_chain", &pywgpu::TextureViewDescriptor::nextInChain)
    .def_readwrite("label", &pywgpu::TextureViewDescriptor::label)
    .def_readwrite("format", &pywgpu::TextureViewDescriptor::format)
    .def_readwrite("dimension", &pywgpu::TextureViewDescriptor::dimension)
    .def_readwrite("base_mip_level", &pywgpu::TextureViewDescriptor::baseMipLevel)
    .def_readwrite("mip_level_count", &pywgpu::TextureViewDescriptor::mipLevelCount)
    .def_readwrite("base_array_layer", &pywgpu::TextureViewDescriptor::baseArrayLayer)
    .def_readwrite("array_layer_count", &pywgpu::TextureViewDescriptor::arrayLayerCount)
    .def_readwrite("aspect", &pywgpu::TextureViewDescriptor::aspect)
    .def_readwrite("usage", &pywgpu::TextureViewDescriptor::usage)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::TextureViewDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "label", "format", "dimension", "base_mip_level", "mip_level_count", "base_array_layer", "array_layer_count", "aspect", "usage"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("label"))
        {
            auto value = kwargs["label"].cast<StringView>();
            obj.label = value;
        }
        if (kwargs.contains("format"))
        {
            auto value = kwargs["format"].cast<TextureFormat>();
            obj.format = value;
        }
        if (kwargs.contains("dimension"))
        {
            auto value = kwargs["dimension"].cast<TextureViewDimension>();
            obj.dimension = value;
        }
        if (kwargs.contains("base_mip_level"))
        {
            auto value = kwargs["base_mip_level"].cast<uint32_t>();
            obj.baseMipLevel = value;
        }
        if (kwargs.contains("mip_level_count"))
        {
            auto value = kwargs["mip_level_count"].cast<uint32_t>();
            obj.mipLevelCount = value;
        }
        if (kwargs.contains("base_array_layer"))
        {
            auto value = kwargs["base_array_layer"].cast<uint32_t>();
            obj.baseArrayLayer = value;
        }
        if (kwargs.contains("array_layer_count"))
        {
            auto value = kwargs["array_layer_count"].cast<uint32_t>();
            obj.arrayLayerCount = value;
        }
        if (kwargs.contains("aspect"))
        {
            auto value = kwargs["aspect"].cast<TextureAspect>();
            obj.aspect = value;
        }
        if (kwargs.contains("usage"))
        {
            auto value = kwargs["usage"].cast<TextureUsage>();
            obj.usage = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<YCbCrVkDescriptor, ChainedStruct> _YCbCrVkDescriptor(m, "YCbCrVkDescriptor");
registry.on(m, "YCbCrVkDescriptor", _YCbCrVkDescriptor);

_YCbCrVkDescriptor
    .def_readwrite("next_in_chain", &pywgpu::YCbCrVkDescriptor::nextInChain)
    .def_readwrite("vk_format", &pywgpu::YCbCrVkDescriptor::vkFormat)
    .def_readwrite("vk_y_cb_cr_model", &pywgpu::YCbCrVkDescriptor::vkYCbCrModel)
    .def_readwrite("vk_y_cb_cr_range", &pywgpu::YCbCrVkDescriptor::vkYCbCrRange)
    .def_readwrite("vk_component_swizzle_red", &pywgpu::YCbCrVkDescriptor::vkComponentSwizzleRed)
    .def_readwrite("vk_component_swizzle_green", &pywgpu::YCbCrVkDescriptor::vkComponentSwizzleGreen)
    .def_readwrite("vk_component_swizzle_blue", &pywgpu::YCbCrVkDescriptor::vkComponentSwizzleBlue)
    .def_readwrite("vk_component_swizzle_alpha", &pywgpu::YCbCrVkDescriptor::vkComponentSwizzleAlpha)
    .def_readwrite("vk_x_chroma_offset", &pywgpu::YCbCrVkDescriptor::vkXChromaOffset)
    .def_readwrite("vk_y_chroma_offset", &pywgpu::YCbCrVkDescriptor::vkYChromaOffset)
    .def_readwrite("vk_chroma_filter", &pywgpu::YCbCrVkDescriptor::vkChromaFilter)
    .def_readwrite("force_explicit_reconstruction", &pywgpu::YCbCrVkDescriptor::forceExplicitReconstruction)
    .def_readwrite("external_format", &pywgpu::YCbCrVkDescriptor::externalFormat)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::YCbCrVkDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "vk_format", "vk_y_cb_cr_model", "vk_y_cb_cr_range", "vk_component_swizzle_red", "vk_component_swizzle_green", "vk_component_swizzle_blue", "vk_component_swizzle_alpha", "vk_x_chroma_offset", "vk_y_chroma_offset", "vk_chroma_filter", "force_explicit_reconstruction", "external_format"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("vk_format"))
        {
            auto value = kwargs["vk_format"].cast<uint32_t>();
            obj.vkFormat = value;
        }
        if (kwargs.contains("vk_y_cb_cr_model"))
        {
            auto value = kwargs["vk_y_cb_cr_model"].cast<uint32_t>();
            obj.vkYCbCrModel = value;
        }
        if (kwargs.contains("vk_y_cb_cr_range"))
        {
            auto value = kwargs["vk_y_cb_cr_range"].cast<uint32_t>();
            obj.vkYCbCrRange = value;
        }
        if (kwargs.contains("vk_component_swizzle_red"))
        {
            auto value = kwargs["vk_component_swizzle_red"].cast<uint32_t>();
            obj.vkComponentSwizzleRed = value;
        }
        if (kwargs.contains("vk_component_swizzle_green"))
        {
            auto value = kwargs["vk_component_swizzle_green"].cast<uint32_t>();
            obj.vkComponentSwizzleGreen = value;
        }
        if (kwargs.contains("vk_component_swizzle_blue"))
        {
            auto value = kwargs["vk_component_swizzle_blue"].cast<uint32_t>();
            obj.vkComponentSwizzleBlue = value;
        }
        if (kwargs.contains("vk_component_swizzle_alpha"))
        {
            auto value = kwargs["vk_component_swizzle_alpha"].cast<uint32_t>();
            obj.vkComponentSwizzleAlpha = value;
        }
        if (kwargs.contains("vk_x_chroma_offset"))
        {
            auto value = kwargs["vk_x_chroma_offset"].cast<uint32_t>();
            obj.vkXChromaOffset = value;
        }
        if (kwargs.contains("vk_y_chroma_offset"))
        {
            auto value = kwargs["vk_y_chroma_offset"].cast<uint32_t>();
            obj.vkYChromaOffset = value;
        }
        if (kwargs.contains("vk_chroma_filter"))
        {
            auto value = kwargs["vk_chroma_filter"].cast<FilterMode>();
            obj.vkChromaFilter = value;
        }
        if (kwargs.contains("force_explicit_reconstruction"))
        {
            auto value = kwargs["force_explicit_reconstruction"].cast<Bool>();
            obj.forceExplicitReconstruction = value;
        }
        if (kwargs.contains("external_format"))
        {
            auto value = kwargs["external_format"].cast<uint64_t>();
            obj.externalFormat = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<DawnTextureInternalUsageDescriptor, ChainedStruct> _DawnTextureInternalUsageDescriptor(m, "DawnTextureInternalUsageDescriptor");
registry.on(m, "DawnTextureInternalUsageDescriptor", _DawnTextureInternalUsageDescriptor);

_DawnTextureInternalUsageDescriptor
    .def_readwrite("next_in_chain", &pywgpu::DawnTextureInternalUsageDescriptor::nextInChain)
    .def_readwrite("internal_usage", &pywgpu::DawnTextureInternalUsageDescriptor::internalUsage)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::DawnTextureInternalUsageDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "internal_usage"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("internal_usage"))
        {
            auto value = kwargs["internal_usage"].cast<TextureUsage>();
            obj.internalUsage = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<DawnEncoderInternalUsageDescriptor, ChainedStruct> _DawnEncoderInternalUsageDescriptor(m, "DawnEncoderInternalUsageDescriptor");
registry.on(m, "DawnEncoderInternalUsageDescriptor", _DawnEncoderInternalUsageDescriptor);

_DawnEncoderInternalUsageDescriptor
    .def_readwrite("next_in_chain", &pywgpu::DawnEncoderInternalUsageDescriptor::nextInChain)
    .def_readwrite("use_internal_usages", &pywgpu::DawnEncoderInternalUsageDescriptor::useInternalUsages)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::DawnEncoderInternalUsageDescriptor obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "use_internal_usages"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("use_internal_usages"))
        {
            auto value = kwargs["use_internal_usages"].cast<Bool>();
            obj.useInternalUsages = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<DawnAdapterPropertiesPowerPreference, ChainedStructOut> _DawnAdapterPropertiesPowerPreference(m, "DawnAdapterPropertiesPowerPreference");
registry.on(m, "DawnAdapterPropertiesPowerPreference", _DawnAdapterPropertiesPowerPreference);

_DawnAdapterPropertiesPowerPreference
    .def_readonly("next_in_chain", &pywgpu::DawnAdapterPropertiesPowerPreference::nextInChain)
    .def_readonly("power_preference", &pywgpu::DawnAdapterPropertiesPowerPreference::powerPreference)
    .def(py::init<>())
    ;

py::class_<MemoryHeapInfo> _MemoryHeapInfo(m, "MemoryHeapInfo");
registry.on(m, "MemoryHeapInfo", _MemoryHeapInfo);

_MemoryHeapInfo
    .def_readwrite("properties", &pywgpu::MemoryHeapInfo::properties)
    .def_readwrite("size", &pywgpu::MemoryHeapInfo::size)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::MemoryHeapInfo obj{};
        static const std::set<std::string> allowed = {"properties", "size"};
        static const std::set<std::string> required = {"size"};
        
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
        
        if (kwargs.contains("properties"))
        {
            auto value = kwargs["properties"].cast<HeapProperty>();
            obj.properties = value;
        }
        if (kwargs.contains("size"))
        {
            auto value = kwargs["size"].cast<uint64_t>();
            obj.size = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
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

py::class_<DawnBufferDescriptorErrorInfoFromWireClient, ChainedStruct> _DawnBufferDescriptorErrorInfoFromWireClient(m, "DawnBufferDescriptorErrorInfoFromWireClient");
registry.on(m, "DawnBufferDescriptorErrorInfoFromWireClient", _DawnBufferDescriptorErrorInfoFromWireClient);

_DawnBufferDescriptorErrorInfoFromWireClient
    .def_readwrite("next_in_chain", &pywgpu::DawnBufferDescriptorErrorInfoFromWireClient::nextInChain)
    .def_readwrite("out_of_memory", &pywgpu::DawnBufferDescriptorErrorInfoFromWireClient::outOfMemory)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::DawnBufferDescriptorErrorInfoFromWireClient obj{};
        static const std::set<std::string> allowed = {"next_in_chain", "out_of_memory"};
        static const std::set<std::string> required = {};
        
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
        
        if (kwargs.contains("next_in_chain"))
        {
            auto value = kwargs["next_in_chain"].cast<ChainedStruct const *>();
            obj.nextInChain = value;
        }
        if (kwargs.contains("out_of_memory"))
        {
            auto value = kwargs["out_of_memory"].cast<Bool>();
            obj.outOfMemory = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<SubgroupMatrixConfig> _SubgroupMatrixConfig(m, "SubgroupMatrixConfig");
registry.on(m, "SubgroupMatrixConfig", _SubgroupMatrixConfig);

_SubgroupMatrixConfig
    .def_readwrite("component_type", &pywgpu::SubgroupMatrixConfig::componentType)
    .def_readwrite("result_component_type", &pywgpu::SubgroupMatrixConfig::resultComponentType)
    .def_readwrite("M", &pywgpu::SubgroupMatrixConfig::M)
    .def_readwrite("N", &pywgpu::SubgroupMatrixConfig::N)
    .def_readwrite("K", &pywgpu::SubgroupMatrixConfig::K)
    .def(py::init([](const py::kwargs& kwargs) {
        pywgpu::SubgroupMatrixConfig obj{};
        static const std::set<std::string> allowed = {"component_type", "result_component_type", "M", "N", "K"};
        static const std::set<std::string> required = {"M", "N", "K"};
        
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
        
        if (kwargs.contains("component_type"))
        {
            auto value = kwargs["component_type"].cast<SubgroupMatrixComponentType>();
            obj.componentType = value;
        }
        if (kwargs.contains("result_component_type"))
        {
            auto value = kwargs["result_component_type"].cast<SubgroupMatrixComponentType>();
            obj.resultComponentType = value;
        }
        if (kwargs.contains("M"))
        {
            auto value = kwargs["M"].cast<uint32_t>();
            obj.M = value;
        }
        if (kwargs.contains("N"))
        {
            auto value = kwargs["N"].cast<uint32_t>();
            obj.N = value;
        }
        if (kwargs.contains("K"))
        {
            auto value = kwargs["K"].cast<uint32_t>();
            obj.K = value;
        }
        return obj;
    }), py::return_value_policy::automatic_reference)
    ;

py::class_<AdapterPropertiesSubgroupMatrixConfigs, ChainedStructOut> _AdapterPropertiesSubgroupMatrixConfigs(m, "AdapterPropertiesSubgroupMatrixConfigs");
registry.on(m, "AdapterPropertiesSubgroupMatrixConfigs", _AdapterPropertiesSubgroupMatrixConfigs);

_AdapterPropertiesSubgroupMatrixConfigs
    .def_readonly("next_in_chain", &pywgpu::AdapterPropertiesSubgroupMatrixConfigs::nextInChain)
    .def_readonly("config_count", &pywgpu::AdapterPropertiesSubgroupMatrixConfigs::configCount)
    .def_readonly("configs", &pywgpu::AdapterPropertiesSubgroupMatrixConfigs::configs)
    .def(py::init<>())
    ;

m.def("create_instance", &pywgpu::CreateInstance
    , py::arg("descriptor") = nullptr
    , py::return_value_policy::automatic_reference)            
;

m.def("get_instance_capabilities", &pywgpu::GetInstanceCapabilities
    , py::arg("capabilities")
    , py::return_value_policy::automatic_reference)            
;


}