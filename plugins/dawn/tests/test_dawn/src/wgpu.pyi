from typing import Optional, List, Literal, Union, Any
from enum import IntEnum, IntFlag

class RequestAdapterStatus(IntEnum):
    SUCCESS = 1
    CALLBACK_CANCELLED = 2
    UNAVAILABLE = 3
    ERROR = 4


class AdapterType(IntEnum):
    DISCRETE_GPU = 1
    INTEGRATED_GPU = 2
    CPU = 3
    UNKNOWN = 4


class AddressMode(IntEnum):
    UNDEFINED = 0
    CLAMP_TO_EDGE = 1
    REPEAT = 2
    MIRROR_REPEAT = 3


class BackendType(IntEnum):
    UNDEFINED = 0
    NULL = 1
    WEB_GPU = 2
    D3D11 = 3
    D3D12 = 4
    METAL = 5
    VULKAN = 6
    OPEN_GL = 7
    OPEN_GLES = 8


class BufferBindingType(IntEnum):
    BINDING_NOT_USED = 0
    UNDEFINED = 1
    UNIFORM = 2
    STORAGE = 3
    READ_ONLY_STORAGE = 4


class SamplerBindingType(IntEnum):
    BINDING_NOT_USED = 0
    UNDEFINED = 1
    FILTERING = 2
    NON_FILTERING = 3
    COMPARISON = 4


class TextureSampleType(IntEnum):
    BINDING_NOT_USED = 0
    UNDEFINED = 1
    FLOAT = 2
    UNFILTERABLE_FLOAT = 3
    DEPTH = 4
    SINT = 5
    UINT = 6


class StorageTextureAccess(IntEnum):
    BINDING_NOT_USED = 0
    UNDEFINED = 1
    WRITE_ONLY = 2
    READ_ONLY = 3
    READ_WRITE = 4


class BlendFactor(IntEnum):
    UNDEFINED = 0
    ZERO = 1
    ONE = 2
    SRC = 3
    ONE_MINUS_SRC = 4
    SRC_ALPHA = 5
    ONE_MINUS_SRC_ALPHA = 6
    DST = 7
    ONE_MINUS_DST = 8
    DST_ALPHA = 9
    ONE_MINUS_DST_ALPHA = 10
    SRC_ALPHA_SATURATED = 11
    CONSTANT = 12
    ONE_MINUS_CONSTANT = 13
    SRC1 = 14
    ONE_MINUS_SRC1 = 15
    SRC1_ALPHA = 16
    ONE_MINUS_SRC1_ALPHA = 17


class BlendOperation(IntEnum):
    UNDEFINED = 0
    ADD = 1
    SUBTRACT = 2
    REVERSE_SUBTRACT = 3
    MIN = 4
    MAX = 5


class MapAsyncStatus(IntEnum):
    SUCCESS = 1
    CALLBACK_CANCELLED = 2
    ERROR = 3
    ABORTED = 4


class BufferMapState(IntEnum):
    UNMAPPED = 1
    PENDING = 2
    MAPPED = 3


class CompareFunction(IntEnum):
    UNDEFINED = 0
    NEVER = 1
    LESS = 2
    EQUAL = 3
    LESS_EQUAL = 4
    GREATER = 5
    NOT_EQUAL = 6
    GREATER_EQUAL = 7
    ALWAYS = 8


class CompilationInfoRequestStatus(IntEnum):
    SUCCESS = 1
    CALLBACK_CANCELLED = 2


class CompilationMessageType(IntEnum):
    ERROR = 1
    WARNING = 2
    INFO = 3


class CompositeAlphaMode(IntEnum):
    AUTO = 0
    OPAQUE = 1
    PREMULTIPLIED = 2
    UNPREMULTIPLIED = 3
    INHERIT = 4


class AlphaMode(IntEnum):
    OPAQUE = 1
    PREMULTIPLIED = 2
    UNPREMULTIPLIED = 3


class CreatePipelineAsyncStatus(IntEnum):
    SUCCESS = 1
    CALLBACK_CANCELLED = 2
    VALIDATION_ERROR = 3
    INTERNAL_ERROR = 4


class CullMode(IntEnum):
    UNDEFINED = 0
    NONE = 1
    FRONT = 2
    BACK = 3


class DeviceLostReason(IntEnum):
    UNKNOWN = 1
    DESTROYED = 2
    CALLBACK_CANCELLED = 3
    FAILED_CREATION = 4


class PopErrorScopeStatus(IntEnum):
    SUCCESS = 1
    CALLBACK_CANCELLED = 2
    ERROR = 3


class ErrorFilter(IntEnum):
    VALIDATION = 1
    OUT_OF_MEMORY = 2
    INTERNAL = 3


class ErrorType(IntEnum):
    NO_ERROR = 1
    VALIDATION = 2
    OUT_OF_MEMORY = 3
    INTERNAL = 4
    UNKNOWN = 5


class LoggingType(IntEnum):
    VERBOSE = 1
    INFO = 2
    WARNING = 3
    ERROR = 4


class ExternalTextureRotation(IntEnum):
    ROTATE0_DEGREES = 1
    ROTATE90_DEGREES = 2
    ROTATE180_DEGREES = 3
    ROTATE270_DEGREES = 4


class Status(IntEnum):
    SUCCESS = 1
    ERROR = 2


class SharedFenceType(IntEnum):
    VK_SEMAPHORE_OPAQUE_FD = 1
    SYNC_FD = 2
    VK_SEMAPHORE_ZIRCON_HANDLE = 3
    DXGI_SHARED_HANDLE = 4
    MTL_SHARED_EVENT = 5
    EGL_SYNC = 6


class FeatureLevel(IntEnum):
    UNDEFINED = 0
    COMPATIBILITY = 1
    CORE = 2


class FeatureName(IntEnum):
    DEPTH_CLIP_CONTROL = 1
    DEPTH32_FLOAT_STENCIL8 = 2
    TIMESTAMP_QUERY = 3
    TEXTURE_COMPRESSION_BC = 4
    TEXTURE_COMPRESSION_BC_SLICED3D = 5
    TEXTURE_COMPRESSION_ETC2 = 6
    TEXTURE_COMPRESSION_ASTC = 7
    TEXTURE_COMPRESSION_ASTC_SLICED3D = 8
    INDIRECT_FIRST_INSTANCE = 9
    SHADER_F16 = 10
    RG11B10_UFLOAT_RENDERABLE = 11
    BGRA8_UNORM_STORAGE = 12
    FLOAT32_FILTERABLE = 13
    FLOAT32_BLENDABLE = 14
    CLIP_DISTANCES = 15
    DUAL_SOURCE_BLENDING = 16
    SUBGROUPS = 17
    CORE_FEATURES_AND_LIMITS = 18
    DAWN_INTERNAL_USAGES = 0
    DAWN_MULTI_PLANAR_FORMATS = 1
    DAWN_NATIVE = 2
    CHROMIUM_EXPERIMENTAL_TIMESTAMP_QUERY_INSIDE_PASSES = 3
    IMPLICIT_DEVICE_SYNCHRONIZATION = 4
    CHROMIUM_EXPERIMENTAL_IMMEDIATE_DATA = 5
    TRANSIENT_ATTACHMENTS = 6
    MSAA_RENDER_TO_SINGLE_SAMPLED = 7
    SUBGROUPS_F16 = 8
    D3D11_MULTITHREAD_PROTECTED = 9
    ANGLE_TEXTURE_SHARING = 10
    PIXEL_LOCAL_STORAGE_COHERENT = 11
    PIXEL_LOCAL_STORAGE_NON_COHERENT = 12
    UNORM16_TEXTURE_FORMATS = 13
    SNORM16_TEXTURE_FORMATS = 14
    MULTI_PLANAR_FORMAT_EXTENDED_USAGES = 15
    MULTI_PLANAR_FORMAT_P010 = 16
    HOST_MAPPED_POINTER = 17
    MULTI_PLANAR_RENDER_TARGETS = 18
    MULTI_PLANAR_FORMAT_NV12A = 19
    FRAMEBUFFER_FETCH = 20
    BUFFER_MAP_EXTENDED_USAGES = 21
    ADAPTER_PROPERTIES_MEMORY_HEAPS = 22
    ADAPTER_PROPERTIES_D3D = 23
    ADAPTER_PROPERTIES_VK = 24
    R8_UNORM_STORAGE = 25
    DAWN_FORMAT_CAPABILITIES = 26
    DAWN_DRM_FORMAT_CAPABILITIES = 27
    NORM16_TEXTURE_FORMATS = 28
    MULTI_PLANAR_FORMAT_NV16 = 29
    MULTI_PLANAR_FORMAT_NV24 = 30
    MULTI_PLANAR_FORMAT_P210 = 31
    MULTI_PLANAR_FORMAT_P410 = 32
    SHARED_TEXTURE_MEMORY_VK_DEDICATED_ALLOCATION = 33
    SHARED_TEXTURE_MEMORY_A_HARDWARE_BUFFER = 34
    SHARED_TEXTURE_MEMORY_DMA_BUF = 35
    SHARED_TEXTURE_MEMORY_OPAQUE_FD = 36
    SHARED_TEXTURE_MEMORY_ZIRCON_HANDLE = 37
    SHARED_TEXTURE_MEMORY_DXGI_SHARED_HANDLE = 38
    SHARED_TEXTURE_MEMORY_D3D11_TEXTURE2D = 39
    SHARED_TEXTURE_MEMORY_IO_SURFACE = 40
    SHARED_TEXTURE_MEMORY_EGL_IMAGE = 41
    SHARED_FENCE_VK_SEMAPHORE_OPAQUE_FD = 42
    SHARED_FENCE_SYNC_FD = 43
    SHARED_FENCE_VK_SEMAPHORE_ZIRCON_HANDLE = 44
    SHARED_FENCE_DXGI_SHARED_HANDLE = 45
    SHARED_FENCE_MTL_SHARED_EVENT = 46
    SHARED_BUFFER_MEMORY_D3D12_RESOURCE = 47
    STATIC_SAMPLERS = 48
    Y_CB_CR_VULKAN_SAMPLERS = 49
    SHADER_MODULE_COMPILATION_OPTIONS = 50
    DAWN_LOAD_RESOLVE_TEXTURE = 51
    DAWN_PARTIAL_LOAD_RESOLVE_TEXTURE = 52
    MULTI_DRAW_INDIRECT = 53
    DAWN_TEXEL_COPY_BUFFER_ROW_ALIGNMENT = 55
    FLEXIBLE_TEXTURE_VIEWS = 56
    CHROMIUM_EXPERIMENTAL_SUBGROUP_MATRIX = 57
    SHARED_FENCE_EGL_SYNC = 58


class FilterMode(IntEnum):
    UNDEFINED = 0
    NEAREST = 1
    LINEAR = 2


class FrontFace(IntEnum):
    UNDEFINED = 0
    CCW = 1
    CW = 2


class IndexFormat(IntEnum):
    UNDEFINED = 0
    UINT16 = 1
    UINT32 = 2


class CallbackMode(IntEnum):
    WAIT_ANY_ONLY = 1
    ALLOW_PROCESS_EVENTS = 2
    ALLOW_SPONTANEOUS = 3


class WaitStatus(IntEnum):
    SUCCESS = 1
    TIMED_OUT = 2
    ERROR = 3


class VertexStepMode(IntEnum):
    UNDEFINED = 0
    VERTEX = 1
    INSTANCE = 2


class LoadOp(IntEnum):
    UNDEFINED = 0
    LOAD = 1
    CLEAR = 2
    EXPAND_RESOLVE_TEXTURE = 3


class MipmapFilterMode(IntEnum):
    UNDEFINED = 0
    NEAREST = 1
    LINEAR = 2


class StoreOp(IntEnum):
    UNDEFINED = 0
    STORE = 1
    DISCARD = 2


class PowerPreference(IntEnum):
    UNDEFINED = 0
    LOW_POWER = 1
    HIGH_PERFORMANCE = 2


class PresentMode(IntEnum):
    UNDEFINED = 0
    FIFO = 1
    FIFO_RELAXED = 2
    IMMEDIATE = 3
    MAILBOX = 4


class PrimitiveTopology(IntEnum):
    UNDEFINED = 0
    POINT_LIST = 1
    LINE_LIST = 2
    LINE_STRIP = 3
    TRIANGLE_LIST = 4
    TRIANGLE_STRIP = 5


class QueryType(IntEnum):
    OCCLUSION = 1
    TIMESTAMP = 2


class QueueWorkDoneStatus(IntEnum):
    SUCCESS = 1
    CALLBACK_CANCELLED = 2
    ERROR = 3


class RequestDeviceStatus(IntEnum):
    SUCCESS = 1
    CALLBACK_CANCELLED = 2
    ERROR = 3


class StencilOperation(IntEnum):
    UNDEFINED = 0
    KEEP = 1
    ZERO = 2
    REPLACE = 3
    INVERT = 4
    INCREMENT_CLAMP = 5
    DECREMENT_CLAMP = 6
    INCREMENT_WRAP = 7
    DECREMENT_WRAP = 8


class SType(IntEnum):
    SHADER_SOURCE_SPIRV = 1
    SHADER_SOURCE_WGSL = 2
    RENDER_PASS_MAX_DRAW_COUNT = 3
    SURFACE_SOURCE_METAL_LAYER = 4
    SURFACE_SOURCE_WINDOWS_HWND = 5
    SURFACE_SOURCE_XLIB_WINDOW = 6
    SURFACE_SOURCE_WAYLAND_SURFACE = 7
    SURFACE_SOURCE_ANDROID_NATIVE_WINDOW = 8
    SURFACE_SOURCE_XCB_WINDOW = 9
    SURFACE_COLOR_MANAGEMENT = 10
    REQUEST_ADAPTER_WEB_XR_OPTIONS = 11
    ADAPTER_PROPERTIES_SUBGROUPS = 12
    TEXTURE_BINDING_VIEW_DIMENSION_DESCRIPTOR = 0
    EMSCRIPTEN_SURFACE_SOURCE_CANVAS_HTML_SELECTOR = 0
    SURFACE_DESCRIPTOR_FROM_WINDOWS_CORE_WINDOW = 0
    EXTERNAL_TEXTURE_BINDING_ENTRY = 1
    EXTERNAL_TEXTURE_BINDING_LAYOUT = 2
    SURFACE_DESCRIPTOR_FROM_WINDOWS_UWP_SWAP_CHAIN_PANEL = 3
    DAWN_TEXTURE_INTERNAL_USAGE_DESCRIPTOR = 4
    DAWN_ENCODER_INTERNAL_USAGE_DESCRIPTOR = 5
    DAWN_INSTANCE_DESCRIPTOR = 6
    DAWN_CACHE_DEVICE_DESCRIPTOR = 7
    DAWN_ADAPTER_PROPERTIES_POWER_PREFERENCE = 8
    DAWN_BUFFER_DESCRIPTOR_ERROR_INFO_FROM_WIRE_CLIENT = 9
    DAWN_TOGGLES_DESCRIPTOR = 10
    DAWN_SHADER_MODULE_SPIRV_OPTIONS_DESCRIPTOR = 11
    REQUEST_ADAPTER_OPTIONS_LUID = 12
    REQUEST_ADAPTER_OPTIONS_GET_GL_PROC = 13
    REQUEST_ADAPTER_OPTIONS_D3D11_DEVICE = 14
    DAWN_RENDER_PASS_COLOR_ATTACHMENT_RENDER_TO_SINGLE_SAMPLED = 15
    RENDER_PASS_PIXEL_LOCAL_STORAGE = 16
    PIPELINE_LAYOUT_PIXEL_LOCAL_STORAGE = 17
    BUFFER_HOST_MAPPED_POINTER = 18
    ADAPTER_PROPERTIES_MEMORY_HEAPS = 19
    ADAPTER_PROPERTIES_D3D = 20
    ADAPTER_PROPERTIES_VK = 21
    DAWN_WIRE_WGSL_CONTROL = 22
    DAWN_WGSL_BLOCKLIST = 23
    DAWN_DRM_FORMAT_CAPABILITIES = 24
    SHADER_MODULE_COMPILATION_OPTIONS = 25
    COLOR_TARGET_STATE_EXPAND_RESOLVE_TEXTURE_DAWN = 26
    RENDER_PASS_DESCRIPTOR_EXPAND_RESOLVE_RECT = 27
    SHARED_TEXTURE_MEMORY_VK_DEDICATED_ALLOCATION_DESCRIPTOR = 28
    SHARED_TEXTURE_MEMORY_A_HARDWARE_BUFFER_DESCRIPTOR = 29
    SHARED_TEXTURE_MEMORY_DMA_BUF_DESCRIPTOR = 30
    SHARED_TEXTURE_MEMORY_OPAQUE_FD_DESCRIPTOR = 31
    SHARED_TEXTURE_MEMORY_ZIRCON_HANDLE_DESCRIPTOR = 32
    SHARED_TEXTURE_MEMORY_DXGI_SHARED_HANDLE_DESCRIPTOR = 33
    SHARED_TEXTURE_MEMORY_D3D11_TEXTURE2D_DESCRIPTOR = 34
    SHARED_TEXTURE_MEMORY_IO_SURFACE_DESCRIPTOR = 35
    SHARED_TEXTURE_MEMORY_EGL_IMAGE_DESCRIPTOR = 36
    SHARED_TEXTURE_MEMORY_INITIALIZED_BEGIN_STATE = 37
    SHARED_TEXTURE_MEMORY_INITIALIZED_END_STATE = 38
    SHARED_TEXTURE_MEMORY_VK_IMAGE_LAYOUT_BEGIN_STATE = 39
    SHARED_TEXTURE_MEMORY_VK_IMAGE_LAYOUT_END_STATE = 40
    SHARED_TEXTURE_MEMORY_D3D_SWAPCHAIN_BEGIN_STATE = 41
    SHARED_FENCE_VK_SEMAPHORE_OPAQUE_FD_DESCRIPTOR = 42
    SHARED_FENCE_VK_SEMAPHORE_OPAQUE_FD_EXPORT_INFO = 43
    SHARED_FENCE_SYNC_FD_DESCRIPTOR = 44
    SHARED_FENCE_SYNC_FD_EXPORT_INFO = 45
    SHARED_FENCE_VK_SEMAPHORE_ZIRCON_HANDLE_DESCRIPTOR = 46
    SHARED_FENCE_VK_SEMAPHORE_ZIRCON_HANDLE_EXPORT_INFO = 47
    SHARED_FENCE_DXGI_SHARED_HANDLE_DESCRIPTOR = 48
    SHARED_FENCE_DXGI_SHARED_HANDLE_EXPORT_INFO = 49
    SHARED_FENCE_MTL_SHARED_EVENT_DESCRIPTOR = 50
    SHARED_FENCE_MTL_SHARED_EVENT_EXPORT_INFO = 51
    SHARED_BUFFER_MEMORY_D3D12_RESOURCE_DESCRIPTOR = 52
    STATIC_SAMPLER_BINDING_LAYOUT = 53
    Y_CB_CR_VK_DESCRIPTOR = 54
    SHARED_TEXTURE_MEMORY_A_HARDWARE_BUFFER_PROPERTIES = 55
    A_HARDWARE_BUFFER_PROPERTIES = 56
    DAWN_EXPERIMENTAL_IMMEDIATE_DATA_LIMITS = 57
    DAWN_TEXEL_COPY_BUFFER_ROW_ALIGNMENT_LIMITS = 58
    ADAPTER_PROPERTIES_SUBGROUP_MATRIX_CONFIGS = 59
    SHARED_FENCE_EGL_SYNC_DESCRIPTOR = 60
    SHARED_FENCE_EGL_SYNC_EXPORT_INFO = 61
    DAWN_INJECTED_INVALID_S_TYPE = 62
    DAWN_COMPILATION_MESSAGE_UTF16 = 63
    DAWN_FAKE_BUFFER_OOM_FOR_TESTING = 64
    SURFACE_DESCRIPTOR_FROM_WINDOWS_WIN_UI_SWAP_CHAIN_PANEL = 65


class SurfaceGetCurrentTextureStatus(IntEnum):
    SUCCESS_OPTIMAL = 1
    SUCCESS_SUBOPTIMAL = 2
    TIMEOUT = 3
    OUTDATED = 4
    LOST = 5
    ERROR = 6


class TextureAspect(IntEnum):
    UNDEFINED = 0
    ALL = 1
    STENCIL_ONLY = 2
    DEPTH_ONLY = 3
    PLANE0_ONLY = 0
    PLANE1_ONLY = 1
    PLANE2_ONLY = 2


class TextureDimension(IntEnum):
    UNDEFINED = 0
    E1D = 1
    E2D = 2
    E3D = 3


class TextureFormat(IntEnum):
    UNDEFINED = 0
    R8_UNORM = 1
    R8_SNORM = 2
    R8_UINT = 3
    R8_SINT = 4
    R16_UINT = 5
    R16_SINT = 6
    R16_FLOAT = 7
    RG8_UNORM = 8
    RG8_SNORM = 9
    RG8_UINT = 10
    RG8_SINT = 11
    R32_FLOAT = 12
    R32_UINT = 13
    R32_SINT = 14
    RG16_UINT = 15
    RG16_SINT = 16
    RG16_FLOAT = 17
    RGBA8_UNORM = 18
    RGBA8_UNORM_SRGB = 19
    RGBA8_SNORM = 20
    RGBA8_UINT = 21
    RGBA8_SINT = 22
    BGRA8_UNORM = 23
    BGRA8_UNORM_SRGB = 24
    RGB10A2_UINT = 25
    RGB10A2_UNORM = 26
    RG11B10_UFLOAT = 27
    RGB9E5_UFLOAT = 28
    RG32_FLOAT = 29
    RG32_UINT = 30
    RG32_SINT = 31
    RGBA16_UINT = 32
    RGBA16_SINT = 33
    RGBA16_FLOAT = 34
    RGBA32_FLOAT = 35
    RGBA32_UINT = 36
    RGBA32_SINT = 37
    STENCIL8 = 38
    DEPTH16_UNORM = 39
    DEPTH24_PLUS = 40
    DEPTH24_PLUS_STENCIL8 = 41
    DEPTH32_FLOAT = 42
    DEPTH32_FLOAT_STENCIL8 = 43
    BC1RGBA_UNORM = 44
    BC1RGBA_UNORM_SRGB = 45
    BC2RGBA_UNORM = 46
    BC2RGBA_UNORM_SRGB = 47
    BC3RGBA_UNORM = 48
    BC3RGBA_UNORM_SRGB = 49
    BC4R_UNORM = 50
    BC4R_SNORM = 51
    BC5RG_UNORM = 52
    BC5RG_SNORM = 53
    BC6HRGB_UFLOAT = 54
    BC6HRGB_FLOAT = 55
    BC7RGBA_UNORM = 56
    BC7RGBA_UNORM_SRGB = 57
    ETC2RGB8_UNORM = 58
    ETC2RGB8_UNORM_SRGB = 59
    ETC2RGB8A1_UNORM = 60
    ETC2RGB8A1_UNORM_SRGB = 61
    ETC2RGBA8_UNORM = 62
    ETC2RGBA8_UNORM_SRGB = 63
    EACR11_UNORM = 64
    EACR11_SNORM = 65
    EACRG11_UNORM = 66
    EACRG11_SNORM = 67
    ASTC4X4_UNORM = 68
    ASTC4X4_UNORM_SRGB = 69
    ASTC5X4_UNORM = 70
    ASTC5X4_UNORM_SRGB = 71
    ASTC5X5_UNORM = 72
    ASTC5X5_UNORM_SRGB = 73
    ASTC6X5_UNORM = 74
    ASTC6X5_UNORM_SRGB = 75
    ASTC6X6_UNORM = 76
    ASTC6X6_UNORM_SRGB = 77
    ASTC8X5_UNORM = 78
    ASTC8X5_UNORM_SRGB = 79
    ASTC8X6_UNORM = 80
    ASTC8X6_UNORM_SRGB = 81
    ASTC8X8_UNORM = 82
    ASTC8X8_UNORM_SRGB = 83
    ASTC10X5_UNORM = 84
    ASTC10X5_UNORM_SRGB = 85
    ASTC10X6_UNORM = 86
    ASTC10X6_UNORM_SRGB = 87
    ASTC10X8_UNORM = 88
    ASTC10X8_UNORM_SRGB = 89
    ASTC10X10_UNORM = 90
    ASTC10X10_UNORM_SRGB = 91
    ASTC12X10_UNORM = 92
    ASTC12X10_UNORM_SRGB = 93
    ASTC12X12_UNORM = 94
    ASTC12X12_UNORM_SRGB = 95
    R16_UNORM = 0
    RG16_UNORM = 1
    RGBA16_UNORM = 2
    R16_SNORM = 3
    RG16_SNORM = 4
    RGBA16_SNORM = 5
    R8BG8_BIPLANAR420_UNORM = 6
    R10X6BG10X6_BIPLANAR420_UNORM = 7
    R8BG8A8_TRIPLANAR420_UNORM = 8
    R8BG8_BIPLANAR422_UNORM = 9
    R8BG8_BIPLANAR444_UNORM = 10
    R10X6BG10X6_BIPLANAR422_UNORM = 11
    R10X6BG10X6_BIPLANAR444_UNORM = 12
    EXTERNAL = 13


class TextureViewDimension(IntEnum):
    UNDEFINED = 0
    E1D = 1
    E2D = 2
    E2D_ARRAY = 3
    CUBE = 4
    CUBE_ARRAY = 5
    E3D = 6


class VertexFormat(IntEnum):
    UINT8 = 1
    UINT8X2 = 2
    UINT8X4 = 3
    SINT8 = 4
    SINT8X2 = 5
    SINT8X4 = 6
    UNORM8 = 7
    UNORM8X2 = 8
    UNORM8X4 = 9
    SNORM8 = 10
    SNORM8X2 = 11
    SNORM8X4 = 12
    UINT16 = 13
    UINT16X2 = 14
    UINT16X4 = 15
    SINT16 = 16
    SINT16X2 = 17
    SINT16X4 = 18
    UNORM16 = 19
    UNORM16X2 = 20
    UNORM16X4 = 21
    SNORM16 = 22
    SNORM16X2 = 23
    SNORM16X4 = 24
    FLOAT16 = 25
    FLOAT16X2 = 26
    FLOAT16X4 = 27
    FLOAT32 = 28
    FLOAT32X2 = 29
    FLOAT32X3 = 30
    FLOAT32X4 = 31
    UINT32 = 32
    UINT32X2 = 33
    UINT32X3 = 34
    UINT32X4 = 35
    SINT32 = 36
    SINT32X2 = 37
    SINT32X3 = 38
    SINT32X4 = 39
    UNORM10_10_10_2 = 40
    UNORM8X4BGRA = 41


class WGSLLanguageFeatureName(IntEnum):
    READONLY_AND_READWRITE_STORAGE_TEXTURES = 1
    PACKED4X8_INTEGER_DOT_PRODUCT = 2
    UNRESTRICTED_POINTER_PARAMETERS = 3
    POINTER_COMPOSITE_ACCESS = 4
    SIZED_BINDING_ARRAY = 5
    CHROMIUM_TESTING_UNIMPLEMENTED = 0
    CHROMIUM_TESTING_UNSAFE_EXPERIMENTAL = 1
    CHROMIUM_TESTING_EXPERIMENTAL = 2
    CHROMIUM_TESTING_SHIPPED_WITH_KILLSWITCH = 3
    CHROMIUM_TESTING_SHIPPED = 4


class SubgroupMatrixComponentType(IntEnum):
    F32 = 1
    F16 = 2
    U32 = 3
    I32 = 4


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

