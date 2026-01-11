from typing import Optional, List, Literal, Union, Any
from enum import IntEnum, IntFlag

class RequestAdapterStatus(IntEnum):
    SUCCESS: int
    CALLBACK_CANCELLED: int
    UNAVAILABLE: int
    ERROR: int


class AdapterType(IntEnum):
    DISCRETE_GPU: int
    INTEGRATED_GPU: int
    CPU: int
    UNKNOWN: int


class AddressMode(IntEnum):
    UNDEFINED: int
    CLAMP_TO_EDGE: int
    REPEAT: int
    MIRROR_REPEAT: int


class BackendType(IntEnum):
    UNDEFINED: int
    NULL: int
    WEB_GPU: int
    D3D11: int
    D3D12: int
    METAL: int
    VULKAN: int
    OPEN_GL: int
    OPEN_GLES: int


class BufferBindingType(IntEnum):
    BINDING_NOT_USED: int
    UNDEFINED: int
    UNIFORM: int
    STORAGE: int
    READ_ONLY_STORAGE: int


class SamplerBindingType(IntEnum):
    BINDING_NOT_USED: int
    UNDEFINED: int
    FILTERING: int
    NON_FILTERING: int
    COMPARISON: int


class TextureSampleType(IntEnum):
    BINDING_NOT_USED: int
    UNDEFINED: int
    FLOAT: int
    UNFILTERABLE_FLOAT: int
    DEPTH: int
    SINT: int
    UINT: int


class StorageTextureAccess(IntEnum):
    BINDING_NOT_USED: int
    UNDEFINED: int
    WRITE_ONLY: int
    READ_ONLY: int
    READ_WRITE: int


class BlendFactor(IntEnum):
    UNDEFINED: int
    ZERO: int
    ONE: int
    SRC: int
    ONE_MINUS_SRC: int
    SRC_ALPHA: int
    ONE_MINUS_SRC_ALPHA: int
    DST: int
    ONE_MINUS_DST: int
    DST_ALPHA: int
    ONE_MINUS_DST_ALPHA: int
    SRC_ALPHA_SATURATED: int
    CONSTANT: int
    ONE_MINUS_CONSTANT: int
    SRC1: int
    ONE_MINUS_SRC1: int
    SRC1_ALPHA: int
    ONE_MINUS_SRC1_ALPHA: int


class BlendOperation(IntEnum):
    UNDEFINED: int
    ADD: int
    SUBTRACT: int
    REVERSE_SUBTRACT: int
    MIN: int
    MAX: int


class MapAsyncStatus(IntEnum):
    SUCCESS: int
    CALLBACK_CANCELLED: int
    ERROR: int
    ABORTED: int


class BufferMapState(IntEnum):
    UNMAPPED: int
    PENDING: int
    MAPPED: int


class CompareFunction(IntEnum):
    UNDEFINED: int
    NEVER: int
    LESS: int
    EQUAL: int
    LESS_EQUAL: int
    GREATER: int
    NOT_EQUAL: int
    GREATER_EQUAL: int
    ALWAYS: int


class CompilationInfoRequestStatus(IntEnum):
    SUCCESS: int
    CALLBACK_CANCELLED: int


class CompilationMessageType(IntEnum):
    ERROR: int
    WARNING: int
    INFO: int


class CompositeAlphaMode(IntEnum):
    AUTO: int
    OPAQUE: int
    PREMULTIPLIED: int
    UNPREMULTIPLIED: int
    INHERIT: int


class AlphaMode(IntEnum):
    OPAQUE: int
    PREMULTIPLIED: int
    UNPREMULTIPLIED: int


class CreatePipelineAsyncStatus(IntEnum):
    SUCCESS: int
    CALLBACK_CANCELLED: int
    VALIDATION_ERROR: int
    INTERNAL_ERROR: int


class CullMode(IntEnum):
    UNDEFINED: int
    NONE: int
    FRONT: int
    BACK: int


class DeviceLostReason(IntEnum):
    UNKNOWN: int
    DESTROYED: int
    CALLBACK_CANCELLED: int
    FAILED_CREATION: int


class PopErrorScopeStatus(IntEnum):
    SUCCESS: int
    CALLBACK_CANCELLED: int
    ERROR: int


class ErrorFilter(IntEnum):
    VALIDATION: int
    OUT_OF_MEMORY: int
    INTERNAL: int


class ErrorType(IntEnum):
    NO_ERROR: int
    VALIDATION: int
    OUT_OF_MEMORY: int
    INTERNAL: int
    UNKNOWN: int


class LoggingType(IntEnum):
    VERBOSE: int
    INFO: int
    WARNING: int
    ERROR: int


class ExternalTextureRotation(IntEnum):
    ROTATE0_DEGREES: int
    ROTATE90_DEGREES: int
    ROTATE180_DEGREES: int
    ROTATE270_DEGREES: int


class Status(IntEnum):
    SUCCESS: int
    ERROR: int


class SharedFenceType(IntEnum):
    VK_SEMAPHORE_OPAQUE_FD: int
    SYNC_FD: int
    VK_SEMAPHORE_ZIRCON_HANDLE: int
    DXGI_SHARED_HANDLE: int
    MTL_SHARED_EVENT: int
    EGL_SYNC: int


class FeatureLevel(IntEnum):
    UNDEFINED: int
    COMPATIBILITY: int
    CORE: int


class FeatureName(IntEnum):
    DEPTH_CLIP_CONTROL: int
    DEPTH32_FLOAT_STENCIL8: int
    TIMESTAMP_QUERY: int
    TEXTURE_COMPRESSION_BC: int
    TEXTURE_COMPRESSION_BC_SLICED3D: int
    TEXTURE_COMPRESSION_ETC2: int
    TEXTURE_COMPRESSION_ASTC: int
    TEXTURE_COMPRESSION_ASTC_SLICED3D: int
    INDIRECT_FIRST_INSTANCE: int
    SHADER_F16: int
    RG11B10_UFLOAT_RENDERABLE: int
    BGRA8_UNORM_STORAGE: int
    FLOAT32_FILTERABLE: int
    FLOAT32_BLENDABLE: int
    CLIP_DISTANCES: int
    DUAL_SOURCE_BLENDING: int
    SUBGROUPS: int
    CORE_FEATURES_AND_LIMITS: int
    DAWN_INTERNAL_USAGES: int
    DAWN_MULTI_PLANAR_FORMATS: int
    DAWN_NATIVE: int
    CHROMIUM_EXPERIMENTAL_TIMESTAMP_QUERY_INSIDE_PASSES: int
    IMPLICIT_DEVICE_SYNCHRONIZATION: int
    CHROMIUM_EXPERIMENTAL_IMMEDIATE_DATA: int
    TRANSIENT_ATTACHMENTS: int
    MSAA_RENDER_TO_SINGLE_SAMPLED: int
    SUBGROUPS_F16: int
    D3D11_MULTITHREAD_PROTECTED: int
    ANGLE_TEXTURE_SHARING: int
    PIXEL_LOCAL_STORAGE_COHERENT: int
    PIXEL_LOCAL_STORAGE_NON_COHERENT: int
    UNORM16_TEXTURE_FORMATS: int
    SNORM16_TEXTURE_FORMATS: int
    MULTI_PLANAR_FORMAT_EXTENDED_USAGES: int
    MULTI_PLANAR_FORMAT_P010: int
    HOST_MAPPED_POINTER: int
    MULTI_PLANAR_RENDER_TARGETS: int
    MULTI_PLANAR_FORMAT_NV12A: int
    FRAMEBUFFER_FETCH: int
    BUFFER_MAP_EXTENDED_USAGES: int
    ADAPTER_PROPERTIES_MEMORY_HEAPS: int
    ADAPTER_PROPERTIES_D3D: int
    ADAPTER_PROPERTIES_VK: int
    R8_UNORM_STORAGE: int
    DAWN_FORMAT_CAPABILITIES: int
    DAWN_DRM_FORMAT_CAPABILITIES: int
    NORM16_TEXTURE_FORMATS: int
    MULTI_PLANAR_FORMAT_NV16: int
    MULTI_PLANAR_FORMAT_NV24: int
    MULTI_PLANAR_FORMAT_P210: int
    MULTI_PLANAR_FORMAT_P410: int
    SHARED_TEXTURE_MEMORY_VK_DEDICATED_ALLOCATION: int
    SHARED_TEXTURE_MEMORY_A_HARDWARE_BUFFER: int
    SHARED_TEXTURE_MEMORY_DMA_BUF: int
    SHARED_TEXTURE_MEMORY_OPAQUE_FD: int
    SHARED_TEXTURE_MEMORY_ZIRCON_HANDLE: int
    SHARED_TEXTURE_MEMORY_DXGI_SHARED_HANDLE: int
    SHARED_TEXTURE_MEMORY_D3D11_TEXTURE2D: int
    SHARED_TEXTURE_MEMORY_IO_SURFACE: int
    SHARED_TEXTURE_MEMORY_EGL_IMAGE: int
    SHARED_FENCE_VK_SEMAPHORE_OPAQUE_FD: int
    SHARED_FENCE_SYNC_FD: int
    SHARED_FENCE_VK_SEMAPHORE_ZIRCON_HANDLE: int
    SHARED_FENCE_DXGI_SHARED_HANDLE: int
    SHARED_FENCE_MTL_SHARED_EVENT: int
    SHARED_BUFFER_MEMORY_D3D12_RESOURCE: int
    STATIC_SAMPLERS: int
    Y_CB_CR_VULKAN_SAMPLERS: int
    SHADER_MODULE_COMPILATION_OPTIONS: int
    DAWN_LOAD_RESOLVE_TEXTURE: int
    DAWN_PARTIAL_LOAD_RESOLVE_TEXTURE: int
    MULTI_DRAW_INDIRECT: int
    DAWN_TEXEL_COPY_BUFFER_ROW_ALIGNMENT: int
    FLEXIBLE_TEXTURE_VIEWS: int
    CHROMIUM_EXPERIMENTAL_SUBGROUP_MATRIX: int
    SHARED_FENCE_EGL_SYNC: int


class FilterMode(IntEnum):
    UNDEFINED: int
    NEAREST: int
    LINEAR: int


class FrontFace(IntEnum):
    UNDEFINED: int
    CCW: int
    CW: int


class IndexFormat(IntEnum):
    UNDEFINED: int
    UINT16: int
    UINT32: int


class CallbackMode(IntEnum):
    WAIT_ANY_ONLY: int
    ALLOW_PROCESS_EVENTS: int
    ALLOW_SPONTANEOUS: int


class WaitStatus(IntEnum):
    SUCCESS: int
    TIMED_OUT: int
    ERROR: int


class VertexStepMode(IntEnum):
    UNDEFINED: int
    VERTEX: int
    INSTANCE: int


class LoadOp(IntEnum):
    UNDEFINED: int
    LOAD: int
    CLEAR: int
    EXPAND_RESOLVE_TEXTURE: int


class MipmapFilterMode(IntEnum):
    UNDEFINED: int
    NEAREST: int
    LINEAR: int


class StoreOp(IntEnum):
    UNDEFINED: int
    STORE: int
    DISCARD: int


class PowerPreference(IntEnum):
    UNDEFINED: int
    LOW_POWER: int
    HIGH_PERFORMANCE: int


class PresentMode(IntEnum):
    UNDEFINED: int
    FIFO: int
    FIFO_RELAXED: int
    IMMEDIATE: int
    MAILBOX: int


class PrimitiveTopology(IntEnum):
    UNDEFINED: int
    POINT_LIST: int
    LINE_LIST: int
    LINE_STRIP: int
    TRIANGLE_LIST: int
    TRIANGLE_STRIP: int


class QueryType(IntEnum):
    OCCLUSION: int
    TIMESTAMP: int


class QueueWorkDoneStatus(IntEnum):
    SUCCESS: int
    CALLBACK_CANCELLED: int
    ERROR: int


class RequestDeviceStatus(IntEnum):
    SUCCESS: int
    CALLBACK_CANCELLED: int
    ERROR: int


class StencilOperation(IntEnum):
    UNDEFINED: int
    KEEP: int
    ZERO: int
    REPLACE: int
    INVERT: int
    INCREMENT_CLAMP: int
    DECREMENT_CLAMP: int
    INCREMENT_WRAP: int
    DECREMENT_WRAP: int


class SType(IntEnum):
    SHADER_SOURCE_SPIRV: int
    SHADER_SOURCE_WGSL: int
    RENDER_PASS_MAX_DRAW_COUNT: int
    SURFACE_SOURCE_METAL_LAYER: int
    SURFACE_SOURCE_WINDOWS_HWND: int
    SURFACE_SOURCE_XLIB_WINDOW: int
    SURFACE_SOURCE_WAYLAND_SURFACE: int
    SURFACE_SOURCE_ANDROID_NATIVE_WINDOW: int
    SURFACE_SOURCE_XCB_WINDOW: int
    SURFACE_COLOR_MANAGEMENT: int
    REQUEST_ADAPTER_WEB_XR_OPTIONS: int
    ADAPTER_PROPERTIES_SUBGROUPS: int
    TEXTURE_BINDING_VIEW_DIMENSION_DESCRIPTOR: int
    EMSCRIPTEN_SURFACE_SOURCE_CANVAS_HTML_SELECTOR: int
    SURFACE_DESCRIPTOR_FROM_WINDOWS_CORE_WINDOW: int
    EXTERNAL_TEXTURE_BINDING_ENTRY: int
    EXTERNAL_TEXTURE_BINDING_LAYOUT: int
    SURFACE_DESCRIPTOR_FROM_WINDOWS_UWP_SWAP_CHAIN_PANEL: int
    DAWN_TEXTURE_INTERNAL_USAGE_DESCRIPTOR: int
    DAWN_ENCODER_INTERNAL_USAGE_DESCRIPTOR: int
    DAWN_INSTANCE_DESCRIPTOR: int
    DAWN_CACHE_DEVICE_DESCRIPTOR: int
    DAWN_ADAPTER_PROPERTIES_POWER_PREFERENCE: int
    DAWN_BUFFER_DESCRIPTOR_ERROR_INFO_FROM_WIRE_CLIENT: int
    DAWN_TOGGLES_DESCRIPTOR: int
    DAWN_SHADER_MODULE_SPIRV_OPTIONS_DESCRIPTOR: int
    REQUEST_ADAPTER_OPTIONS_LUID: int
    REQUEST_ADAPTER_OPTIONS_GET_GL_PROC: int
    REQUEST_ADAPTER_OPTIONS_D3D11_DEVICE: int
    DAWN_RENDER_PASS_COLOR_ATTACHMENT_RENDER_TO_SINGLE_SAMPLED: int
    RENDER_PASS_PIXEL_LOCAL_STORAGE: int
    PIPELINE_LAYOUT_PIXEL_LOCAL_STORAGE: int
    BUFFER_HOST_MAPPED_POINTER: int
    ADAPTER_PROPERTIES_MEMORY_HEAPS: int
    ADAPTER_PROPERTIES_D3D: int
    ADAPTER_PROPERTIES_VK: int
    DAWN_WIRE_WGSL_CONTROL: int
    DAWN_WGSL_BLOCKLIST: int
    DAWN_DRM_FORMAT_CAPABILITIES: int
    SHADER_MODULE_COMPILATION_OPTIONS: int
    COLOR_TARGET_STATE_EXPAND_RESOLVE_TEXTURE_DAWN: int
    RENDER_PASS_DESCRIPTOR_EXPAND_RESOLVE_RECT: int
    SHARED_TEXTURE_MEMORY_VK_DEDICATED_ALLOCATION_DESCRIPTOR: int
    SHARED_TEXTURE_MEMORY_A_HARDWARE_BUFFER_DESCRIPTOR: int
    SHARED_TEXTURE_MEMORY_DMA_BUF_DESCRIPTOR: int
    SHARED_TEXTURE_MEMORY_OPAQUE_FD_DESCRIPTOR: int
    SHARED_TEXTURE_MEMORY_ZIRCON_HANDLE_DESCRIPTOR: int
    SHARED_TEXTURE_MEMORY_DXGI_SHARED_HANDLE_DESCRIPTOR: int
    SHARED_TEXTURE_MEMORY_D3D11_TEXTURE2D_DESCRIPTOR: int
    SHARED_TEXTURE_MEMORY_IO_SURFACE_DESCRIPTOR: int
    SHARED_TEXTURE_MEMORY_EGL_IMAGE_DESCRIPTOR: int
    SHARED_TEXTURE_MEMORY_INITIALIZED_BEGIN_STATE: int
    SHARED_TEXTURE_MEMORY_INITIALIZED_END_STATE: int
    SHARED_TEXTURE_MEMORY_VK_IMAGE_LAYOUT_BEGIN_STATE: int
    SHARED_TEXTURE_MEMORY_VK_IMAGE_LAYOUT_END_STATE: int
    SHARED_TEXTURE_MEMORY_D3D_SWAPCHAIN_BEGIN_STATE: int
    SHARED_FENCE_VK_SEMAPHORE_OPAQUE_FD_DESCRIPTOR: int
    SHARED_FENCE_VK_SEMAPHORE_OPAQUE_FD_EXPORT_INFO: int
    SHARED_FENCE_SYNC_FD_DESCRIPTOR: int
    SHARED_FENCE_SYNC_FD_EXPORT_INFO: int
    SHARED_FENCE_VK_SEMAPHORE_ZIRCON_HANDLE_DESCRIPTOR: int
    SHARED_FENCE_VK_SEMAPHORE_ZIRCON_HANDLE_EXPORT_INFO: int
    SHARED_FENCE_DXGI_SHARED_HANDLE_DESCRIPTOR: int
    SHARED_FENCE_DXGI_SHARED_HANDLE_EXPORT_INFO: int
    SHARED_FENCE_MTL_SHARED_EVENT_DESCRIPTOR: int
    SHARED_FENCE_MTL_SHARED_EVENT_EXPORT_INFO: int
    SHARED_BUFFER_MEMORY_D3D12_RESOURCE_DESCRIPTOR: int
    STATIC_SAMPLER_BINDING_LAYOUT: int
    Y_CB_CR_VK_DESCRIPTOR: int
    SHARED_TEXTURE_MEMORY_A_HARDWARE_BUFFER_PROPERTIES: int
    A_HARDWARE_BUFFER_PROPERTIES: int
    DAWN_EXPERIMENTAL_IMMEDIATE_DATA_LIMITS: int
    DAWN_TEXEL_COPY_BUFFER_ROW_ALIGNMENT_LIMITS: int
    ADAPTER_PROPERTIES_SUBGROUP_MATRIX_CONFIGS: int
    SHARED_FENCE_EGL_SYNC_DESCRIPTOR: int
    SHARED_FENCE_EGL_SYNC_EXPORT_INFO: int
    DAWN_INJECTED_INVALID_S_TYPE: int
    DAWN_COMPILATION_MESSAGE_UTF16: int
    DAWN_FAKE_BUFFER_OOM_FOR_TESTING: int
    SURFACE_DESCRIPTOR_FROM_WINDOWS_WIN_UI_SWAP_CHAIN_PANEL: int


class SurfaceGetCurrentTextureStatus(IntEnum):
    SUCCESS_OPTIMAL: int
    SUCCESS_SUBOPTIMAL: int
    TIMEOUT: int
    OUTDATED: int
    LOST: int
    ERROR: int


class TextureAspect(IntEnum):
    UNDEFINED: int
    ALL: int
    STENCIL_ONLY: int
    DEPTH_ONLY: int
    PLANE0_ONLY: int
    PLANE1_ONLY: int
    PLANE2_ONLY: int


class TextureDimension(IntEnum):
    UNDEFINED: int
    E1D: int
    E2D: int
    E3D: int


class TextureFormat(IntEnum):
    UNDEFINED: int
    R8_UNORM: int
    R8_SNORM: int
    R8_UINT: int
    R8_SINT: int
    R16_UINT: int
    R16_SINT: int
    R16_FLOAT: int
    RG8_UNORM: int
    RG8_SNORM: int
    RG8_UINT: int
    RG8_SINT: int
    R32_FLOAT: int
    R32_UINT: int
    R32_SINT: int
    RG16_UINT: int
    RG16_SINT: int
    RG16_FLOAT: int
    RGBA8_UNORM: int
    RGBA8_UNORM_SRGB: int
    RGBA8_SNORM: int
    RGBA8_UINT: int
    RGBA8_SINT: int
    BGRA8_UNORM: int
    BGRA8_UNORM_SRGB: int
    RGB10A2_UINT: int
    RGB10A2_UNORM: int
    RG11B10_UFLOAT: int
    RGB9E5_UFLOAT: int
    RG32_FLOAT: int
    RG32_UINT: int
    RG32_SINT: int
    RGBA16_UINT: int
    RGBA16_SINT: int
    RGBA16_FLOAT: int
    RGBA32_FLOAT: int
    RGBA32_UINT: int
    RGBA32_SINT: int
    STENCIL8: int
    DEPTH16_UNORM: int
    DEPTH24_PLUS: int
    DEPTH24_PLUS_STENCIL8: int
    DEPTH32_FLOAT: int
    DEPTH32_FLOAT_STENCIL8: int
    BC1RGBA_UNORM: int
    BC1RGBA_UNORM_SRGB: int
    BC2RGBA_UNORM: int
    BC2RGBA_UNORM_SRGB: int
    BC3RGBA_UNORM: int
    BC3RGBA_UNORM_SRGB: int
    BC4R_UNORM: int
    BC4R_SNORM: int
    BC5RG_UNORM: int
    BC5RG_SNORM: int
    BC6HRGB_UFLOAT: int
    BC6HRGB_FLOAT: int
    BC7RGBA_UNORM: int
    BC7RGBA_UNORM_SRGB: int
    ETC2RGB8_UNORM: int
    ETC2RGB8_UNORM_SRGB: int
    ETC2RGB8A1_UNORM: int
    ETC2RGB8A1_UNORM_SRGB: int
    ETC2RGBA8_UNORM: int
    ETC2RGBA8_UNORM_SRGB: int
    EACR11_UNORM: int
    EACR11_SNORM: int
    EACRG11_UNORM: int
    EACRG11_SNORM: int
    ASTC4X4_UNORM: int
    ASTC4X4_UNORM_SRGB: int
    ASTC5X4_UNORM: int
    ASTC5X4_UNORM_SRGB: int
    ASTC5X5_UNORM: int
    ASTC5X5_UNORM_SRGB: int
    ASTC6X5_UNORM: int
    ASTC6X5_UNORM_SRGB: int
    ASTC6X6_UNORM: int
    ASTC6X6_UNORM_SRGB: int
    ASTC8X5_UNORM: int
    ASTC8X5_UNORM_SRGB: int
    ASTC8X6_UNORM: int
    ASTC8X6_UNORM_SRGB: int
    ASTC8X8_UNORM: int
    ASTC8X8_UNORM_SRGB: int
    ASTC10X5_UNORM: int
    ASTC10X5_UNORM_SRGB: int
    ASTC10X6_UNORM: int
    ASTC10X6_UNORM_SRGB: int
    ASTC10X8_UNORM: int
    ASTC10X8_UNORM_SRGB: int
    ASTC10X10_UNORM: int
    ASTC10X10_UNORM_SRGB: int
    ASTC12X10_UNORM: int
    ASTC12X10_UNORM_SRGB: int
    ASTC12X12_UNORM: int
    ASTC12X12_UNORM_SRGB: int
    R16_UNORM: int
    RG16_UNORM: int
    RGBA16_UNORM: int
    R16_SNORM: int
    RG16_SNORM: int
    RGBA16_SNORM: int
    R8BG8_BIPLANAR420_UNORM: int
    R10X6BG10X6_BIPLANAR420_UNORM: int
    R8BG8A8_TRIPLANAR420_UNORM: int
    R8BG8_BIPLANAR422_UNORM: int
    R8BG8_BIPLANAR444_UNORM: int
    R10X6BG10X6_BIPLANAR422_UNORM: int
    R10X6BG10X6_BIPLANAR444_UNORM: int
    EXTERNAL: int


class TextureViewDimension(IntEnum):
    UNDEFINED: int
    E1D: int
    E2D: int
    E2D_ARRAY: int
    CUBE: int
    CUBE_ARRAY: int
    E3D: int


class VertexFormat(IntEnum):
    UINT8: int
    UINT8X2: int
    UINT8X4: int
    SINT8: int
    SINT8X2: int
    SINT8X4: int
    UNORM8: int
    UNORM8X2: int
    UNORM8X4: int
    SNORM8: int
    SNORM8X2: int
    SNORM8X4: int
    UINT16: int
    UINT16X2: int
    UINT16X4: int
    SINT16: int
    SINT16X2: int
    SINT16X4: int
    UNORM16: int
    UNORM16X2: int
    UNORM16X4: int
    SNORM16: int
    SNORM16X2: int
    SNORM16X4: int
    FLOAT16: int
    FLOAT16X2: int
    FLOAT16X4: int
    FLOAT32: int
    FLOAT32X2: int
    FLOAT32X3: int
    FLOAT32X4: int
    UINT32: int
    UINT32X2: int
    UINT32X3: int
    UINT32X4: int
    SINT32: int
    SINT32X2: int
    SINT32X3: int
    SINT32X4: int
    UNORM10_10_10_2: int
    UNORM8X4BGRA: int


class WGSLLanguageFeatureName(IntEnum):
    READONLY_AND_READWRITE_STORAGE_TEXTURES: int
    PACKED4X8_INTEGER_DOT_PRODUCT: int
    UNRESTRICTED_POINTER_PARAMETERS: int
    POINTER_COMPOSITE_ACCESS: int
    SIZED_BINDING_ARRAY: int
    CHROMIUM_TESTING_UNIMPLEMENTED: int
    CHROMIUM_TESTING_UNSAFE_EXPERIMENTAL: int
    CHROMIUM_TESTING_EXPERIMENTAL: int
    CHROMIUM_TESTING_SHIPPED_WITH_KILLSWITCH: int
    CHROMIUM_TESTING_SHIPPED: int


class SubgroupMatrixComponentType(IntEnum):
    F32: int
    F16: int
    U32: int
    I32: int


class AdapterInfo:
    next_in_chain: Optional[Any] = None  # type: ChainedStructOut * 
    vendor: Any  # type: StringView 
    architecture: Any  # type: StringView 
    device: Any  # type: StringView 
    description: Any  # type: StringView 
    backend_type: Any  # type: BackendType 
    adapter_type: Any  # type: AdapterType 
    vendor_ID: Any  # type: uint32_t 
    device_ID: Any  # type: uint32_t 
    subgroup_min_size: Any  # type: uint32_t 
    subgroup_max_size: Any  # type: uint32_t 

class SurfaceCapabilities:
    next_in_chain: Optional[Any] = None  # type: ChainedStructOut * 
    usages: Any  # type: TextureUsage 
    format_count: Any  # type: size_t 
    formats: Any  # type: TextureFormat const * 
    present_mode_count: Any  # type: size_t 
    present_modes: Any  # type: PresentMode const * 
    alpha_mode_count: Any  # type: size_t 
    alpha_modes: Any  # type: CompositeAlphaMode const * 

class AdapterPropertiesSubgroups:
    next_in_chain: Optional[Any] = None  # type: ChainedStructOut * 
    subgroup_min_size: Any  # type: uint32_t 
    subgroup_max_size: Any  # type: uint32_t 

class DawnExperimentalImmediateDataLimits:
    next_in_chain: Optional[Any] = None  # type: ChainedStructOut * 
    max_immediate_data_range_byte_size: Any  # type: uint32_t 

class DawnTexelCopyBufferRowAlignmentLimits:
    next_in_chain: Optional[Any] = None  # type: ChainedStructOut * 
    min_texel_copy_buffer_row_alignment: Any  # type: uint32_t 

class SharedBufferMemoryProperties:
    next_in_chain: Optional[Any] = None  # type: ChainedStructOut * 
    usage: Any  # type: BufferUsage 
    size: Any  # type: uint64_t 

class SharedTextureMemoryProperties:
    next_in_chain: Optional[Any] = None  # type: ChainedStructOut * 
    usage: Any  # type: TextureUsage 
    size: Any  # type: Extent3D 
    format: Any  # type: TextureFormat 

class SharedTextureMemoryAHardwareBufferProperties:
    next_in_chain: Optional[Any] = None  # type: ChainedStructOut * 
    y_cb_cr_info: Any  # type: YCbCrVkDescriptor 

class SharedBufferMemoryEndAccessState:
    next_in_chain: Optional[Any] = None  # type: ChainedStructOut * 
    initialized: Any  # type: Bool 
    fence_count: Any  # type: size_t 
    fences: Any  # type: SharedFence const * 
    signaled_values: Any  # type: uint64_t const * 

class SharedTextureMemoryEndAccessState:
    next_in_chain: Optional[Any] = None  # type: ChainedStructOut * 
    initialized: Any  # type: Bool 
    fence_count: Any  # type: size_t 
    fences: Any  # type: SharedFence const * 
    signaled_values: Any  # type: uint64_t const * 

class SharedTextureMemoryVkImageLayoutEndState:
    next_in_chain: Optional[Any] = None  # type: ChainedStructOut * 
    old_layout: Any  # type: int32_t 
    new_layout: Any  # type: int32_t 

class SharedFenceExportInfo:
    next_in_chain: Optional[Any] = None  # type: ChainedStructOut * 
    type: Any  # type: SharedFenceType 

class SharedFenceVkSemaphoreOpaqueFDExportInfo:
    next_in_chain: Optional[Any] = None  # type: ChainedStructOut * 
    handle: Any  # type: int 

class SharedFenceSyncFDExportInfo:
    next_in_chain: Optional[Any] = None  # type: ChainedStructOut * 
    handle: Any  # type: int 

class SharedFenceVkSemaphoreZirconHandleExportInfo:
    next_in_chain: Optional[Any] = None  # type: ChainedStructOut * 
    handle: Any  # type: uint32_t 

class SharedFenceDXGISharedHandleExportInfo:
    next_in_chain: Optional[Any] = None  # type: ChainedStructOut * 
    handle: Any  # type: void * 

class SharedFenceMTLSharedEventExportInfo:
    next_in_chain: Optional[Any] = None  # type: ChainedStructOut * 
    shared_event: Any  # type: void * 

class SharedFenceEGLSyncExportInfo:
    next_in_chain: Optional[Any] = None  # type: ChainedStructOut * 
    sync: Any  # type: void * 

class DawnFormatCapabilities:
    next_in_chain: Optional[Any] = None  # type: ChainedStructOut * 

class DawnDrmFormatCapabilities:
    next_in_chain: Optional[Any] = None  # type: ChainedStructOut * 
    properties_count: Any  # type: size_t 
    properties: Any  # type: DawnDrmFormatProperties const * 

class SurfaceTexture:
    next_in_chain: Optional[Any] = None  # type: ChainedStructOut * 
    texture: Any  # type: Texture 
    status: Any  # type: SurfaceGetCurrentTextureStatus 

class DawnAdapterPropertiesPowerPreference:
    next_in_chain: Optional[Any] = None  # type: ChainedStructOut * 
    power_preference: Any  # type: PowerPreference 

class AdapterPropertiesMemoryHeaps:
    next_in_chain: Optional[Any] = None  # type: ChainedStructOut * 
    heap_count: Any  # type: size_t 
    heap_info: Any  # type: MemoryHeapInfo const * 

class AdapterPropertiesD3D:
    next_in_chain: Optional[Any] = None  # type: ChainedStructOut * 
    shader_model: Any  # type: uint32_t 

class AdapterPropertiesVk:
    next_in_chain: Optional[Any] = None  # type: ChainedStructOut * 
    driver_version: Any  # type: uint32_t 

class AdapterPropertiesSubgroupMatrixConfigs:
    next_in_chain: Optional[Any] = None  # type: ChainedStructOut * 
    config_count: Any  # type: size_t 
    configs: Any  # type: SubgroupMatrixConfig const * 

