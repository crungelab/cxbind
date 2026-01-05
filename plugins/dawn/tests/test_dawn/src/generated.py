from dataclasses import dataclass, field
from typing import Optional, List, Literal, Union, Any

from ._wgpu import *

@dataclass(frozen=True, kw_only=True)
class RequestAdapterOptions:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    feature_level: Any = FeatureLevel.CORE  # type: FeatureLevel , default: FeatureLevel.CORE
    power_preference: Any = PowerPreference.UNDEFINED  # type: PowerPreference , default: PowerPreference.UNDEFINED
    force_fallback_adapter: Any = False  # type: Bool , default: False
    backend_type: Any = BackendType.UNDEFINED  # type: BackendType , default: BackendType.UNDEFINED
    compatible_surface: Optional[Any] = None  # type: Surface , default: None


@dataclass(frozen=True, kw_only=True)
class DeviceDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    label: Optional[Any] = None  # type: StringView , default: None
    required_feature_count: Any = 0  # type: size_t , default: 0
    required_features: Any = None  # type: FeatureName const * , default: None
    required_limits: Optional[Any] = None  # type: Limits const * , default: None
    default_queue: Any  # type: QueueDescriptor , default: None
    device_lost_callback_info: Any  # type: DeviceLostCallbackInfo , default: None
    uncaptured_error_callback_info: Any  # type: UncapturedErrorCallbackInfo , default: None


@dataclass(frozen=True, kw_only=True)
class DawnTogglesDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    enabled_toggle_count: Any = 0  # type: size_t , default: 0
    disabled_toggle_count: Any = 0  # type: size_t , default: 0


@dataclass(frozen=True, kw_only=True)
class DawnCacheDeviceDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    isolation_key: Any  # type: StringView , default: None
    function_userdata: Any = None  # type: void * , default: None


@dataclass(frozen=True, kw_only=True)
class DawnWGSLBlocklist:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    blocklisted_feature_count: Any = 0  # type: size_t , default: 0


@dataclass(frozen=True, kw_only=True)
class BindGroupEntry:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    binding: Any  # type: uint32_t , default: None
    buffer: Optional[Any] = None  # type: Buffer , default: None
    offset: Any = 0  # type: uint64_t , default: 0
    size: Any = 18446744073709551615  # type: uint64_t , default: 18446744073709551615
    sampler: Optional[Any] = None  # type: Sampler , default: None
    texture_view: Optional[Any] = None  # type: TextureView , default: None


@dataclass(frozen=True, kw_only=True)
class BindGroupDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    label: Optional[Any] = None  # type: StringView , default: None
    layout: Any  # type: BindGroupLayout , default: None
    entry_count: Any  # type: size_t , default: None
    entries: Any  # type: BindGroupEntry const * , default: None


@dataclass(frozen=True, kw_only=True)
class BufferBindingLayout:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    type: Any = BufferBindingType.UNIFORM  # type: BufferBindingType , default: BufferBindingType.UNIFORM
    has_dynamic_offset: Any = False  # type: Bool , default: False
    min_binding_size: Any = 0  # type: uint64_t , default: 0


@dataclass(frozen=True, kw_only=True)
class SamplerBindingLayout:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    type: Any = SamplerBindingType.FILTERING  # type: SamplerBindingType , default: SamplerBindingType.FILTERING


@dataclass(frozen=True, kw_only=True)
class StaticSamplerBindingLayout:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    sampler: Any  # type: Sampler , default: None
    sampled_texture_binding: Any = 4294967295  # type: uint32_t , default: 4294967295


@dataclass(frozen=True, kw_only=True)
class TextureBindingLayout:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    sample_type: Any = TextureSampleType.FLOAT  # type: TextureSampleType , default: TextureSampleType.FLOAT
    view_dimension: Any = TextureViewDimension.E2D  # type: TextureViewDimension , default: TextureViewDimension.E2D
    multisampled: Any = False  # type: Bool , default: False


@dataclass(frozen=True, kw_only=True)
class SurfaceConfiguration:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    device: Any  # type: Device , default: None
    format: Any = TextureFormat.UNDEFINED  # type: TextureFormat , default: TextureFormat.UNDEFINED
    usage: Any = TextureUsage.RENDER_ATTACHMENT  # type: TextureUsage , default: TextureUsage.RENDER_ATTACHMENT
    width: Any  # type: uint32_t , default: None
    height: Any  # type: uint32_t , default: None
    view_format_count: Any = 0  # type: size_t , default: 0
    view_formats: Any = None  # type: TextureFormat const * , default: None
    alpha_mode: Any = CompositeAlphaMode.AUTO  # type: CompositeAlphaMode , default: CompositeAlphaMode.AUTO
    present_mode: Any = PresentMode.FIFO  # type: PresentMode , default: PresentMode.FIFO


@dataclass(frozen=True, kw_only=True)
class ExternalTextureBindingEntry:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    external_texture: Any  # type: ExternalTexture , default: None


@dataclass(frozen=True, kw_only=True)
class ExternalTextureBindingLayout:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None


@dataclass(frozen=True, kw_only=True)
class StorageTextureBindingLayout:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    access: Any = StorageTextureAccess.WRITE_ONLY  # type: StorageTextureAccess , default: StorageTextureAccess.WRITE_ONLY
    format: Any = TextureFormat.UNDEFINED  # type: TextureFormat , default: TextureFormat.UNDEFINED
    view_dimension: Any = TextureViewDimension.E2D  # type: TextureViewDimension , default: TextureViewDimension.E2D


@dataclass(frozen=True, kw_only=True)
class BindGroupLayoutEntry:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    binding: Any  # type: uint32_t , default: None
    visibility: Any = ShaderStage.NONE  # type: ShaderStage , default: ShaderStage.NONE
    buffer: Any = 0  # type: BufferBindingLayout , default: 0
    sampler: Any = 0  # type: SamplerBindingLayout , default: 0
    texture: Any = 0  # type: TextureBindingLayout , default: 0
    storage_texture: Any = 0  # type: StorageTextureBindingLayout , default: 0


@dataclass(frozen=True, kw_only=True)
class BindGroupLayoutDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    label: Optional[Any] = None  # type: StringView , default: None
    entry_count: Any  # type: size_t , default: None
    entries: Any  # type: BindGroupLayoutEntry const * , default: None


@dataclass(frozen=True, kw_only=True)
class BlendComponent:
    operation: Any = BlendOperation.ADD  # type: BlendOperation , default: BlendOperation.ADD
    src_factor: Any = BlendFactor.ONE  # type: BlendFactor , default: BlendFactor.ONE
    dst_factor: Any = 0  # type: BlendFactor , default: 0


@dataclass(frozen=True, kw_only=True)
class BufferDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    label: Optional[Any] = None  # type: StringView , default: None
    usage: Any = BufferUsage.NONE  # type: BufferUsage , default: BufferUsage.NONE
    size: Any  # type: uint64_t , default: None
    mapped_at_creation: Any = False  # type: Bool , default: False


@dataclass(frozen=True, kw_only=True)
class BufferHostMappedPointer:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    pointer: Any  # type: void * , default: None
    userdata: Any  # type: void * , default: None


@dataclass(frozen=True, kw_only=True)
class Color:
    r: Any  # type: double , default: None
    g: Any  # type: double , default: None
    b: Any  # type: double , default: None
    a: Any  # type: double , default: None


@dataclass(frozen=True, kw_only=True)
class ConstantEntry:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    key: Any  # type: StringView , default: None
    value: Any  # type: double , default: None


@dataclass(frozen=True, kw_only=True)
class CommandBufferDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    label: Optional[Any] = None  # type: StringView , default: None


@dataclass(frozen=True, kw_only=True)
class CommandEncoderDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    label: Optional[Any] = None  # type: StringView , default: None


@dataclass(frozen=True, kw_only=True)
class CompilationInfo:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    message_count: Any  # type: size_t , default: None
    messages: Any  # type: CompilationMessage const * , default: None


@dataclass(frozen=True, kw_only=True)
class CompilationMessage:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    message: Any  # type: StringView , default: None
    type: Any  # type: CompilationMessageType , default: None
    line_num: Any  # type: uint64_t , default: None
    line_pos: Any  # type: uint64_t , default: None
    offset: Any  # type: uint64_t , default: None
    length: Any  # type: uint64_t , default: None


@dataclass(frozen=True, kw_only=True)
class DawnCompilationMessageUtf16:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    line_pos: Any  # type: uint64_t , default: None
    offset: Any  # type: uint64_t , default: None
    length: Any  # type: uint64_t , default: None


@dataclass(frozen=True, kw_only=True)
class ComputePassDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    label: Optional[Any] = None  # type: StringView , default: None
    timestamp_writes: Optional[Any] = None  # type: PassTimestampWrites const * , default: None


@dataclass(frozen=True, kw_only=True)
class ComputePipelineDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    label: Optional[Any] = None  # type: StringView , default: None
    layout: Optional[Any] = None  # type: PipelineLayout , default: None
    compute: Any  # type: ComputeState , default: None


@dataclass(frozen=True, kw_only=True)
class CopyTextureForBrowserOptions:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    flip_y: Any = False  # type: Bool , default: False
    needs_color_space_conversion: Any = False  # type: Bool , default: False
    src_alpha_mode: Any = AlphaMode.UNPREMULTIPLIED  # type: AlphaMode , default: AlphaMode.UNPREMULTIPLIED
    src_transfer_function_parameters: Optional[Any] = None  # type: float const * , default: None
    conversion_matrix: Optional[Any] = None  # type: float const * , default: None
    dst_transfer_function_parameters: Optional[Any] = None  # type: float const * , default: None
    dst_alpha_mode: Any = AlphaMode.UNPREMULTIPLIED  # type: AlphaMode , default: AlphaMode.UNPREMULTIPLIED
    internal_usage: Any = False  # type: Bool , default: False


@dataclass(frozen=True, kw_only=True)
class AHardwareBufferProperties:
    y_cb_cr_info: Any  # type: YCbCrVkDescriptor , default: None


@dataclass(frozen=True, kw_only=True)
class Limits:
    next_in_chain: Optional[Any] = None  # type: ChainedStructOut * , default: None
    max_texture_dimension_1D: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_texture_dimension_2D: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_texture_dimension_3D: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_texture_array_layers: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_bind_groups: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_bind_groups_plus_vertex_buffers: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_bindings_per_bind_group: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_dynamic_uniform_buffers_per_pipeline_layout: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_dynamic_storage_buffers_per_pipeline_layout: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_sampled_textures_per_shader_stage: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_samplers_per_shader_stage: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_storage_buffers_per_shader_stage: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_storage_textures_per_shader_stage: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_uniform_buffers_per_shader_stage: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_uniform_buffer_binding_size: Any = 18446744073709551615  # type: uint64_t , default: 18446744073709551615
    max_storage_buffer_binding_size: Any = 18446744073709551615  # type: uint64_t , default: 18446744073709551615
    min_uniform_buffer_offset_alignment: Any = 4294967295  # type: uint32_t , default: 4294967295
    min_storage_buffer_offset_alignment: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_vertex_buffers: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_buffer_size: Any = 18446744073709551615  # type: uint64_t , default: 18446744073709551615
    max_vertex_attributes: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_vertex_buffer_array_stride: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_inter_stage_shader_variables: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_color_attachments: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_color_attachment_bytes_per_sample: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_compute_workgroup_storage_size: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_compute_invocations_per_workgroup: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_compute_workgroup_size_x: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_compute_workgroup_size_y: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_compute_workgroup_size_z: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_compute_workgroups_per_dimension: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_storage_buffers_in_vertex_stage: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_storage_textures_in_vertex_stage: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_storage_buffers_in_fragment_stage: Any = 4294967295  # type: uint32_t , default: 4294967295
    max_storage_textures_in_fragment_stage: Any = 4294967295  # type: uint32_t , default: 4294967295


@dataclass(frozen=True, kw_only=True)
class SupportedFeatures:
    feature_count: Any  # type: size_t , default: None
    features: Any = FeatureName.DAWN_INTERNAL_USAGES  # type: FeatureName const * , default: FeatureName.DAWN_INTERNAL_USAGES


@dataclass(frozen=True, kw_only=True)
class SupportedWGSLLanguageFeatures:
    feature_count: Any  # type: size_t , default: None
    features: Any = WGSLLanguageFeatureName.CHROMIUM_TESTING_UNIMPLEMENTED  # type: WGSLLanguageFeatureName const * , default: WGSLLanguageFeatureName.CHROMIUM_TESTING_UNIMPLEMENTED


@dataclass(frozen=True, kw_only=True)
class Extent2D:
    width: Any  # type: uint32_t , default: None
    height: Any  # type: uint32_t , default: None


@dataclass(frozen=True, kw_only=True)
class Extent3D:
    width: Any  # type: uint32_t , default: None
    height: Any = 1  # type: uint32_t , default: 1
    depth_or_array_layers: Any = 1  # type: uint32_t , default: 1


@dataclass(frozen=True, kw_only=True)
class ExternalTextureDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    label: Optional[Any] = None  # type: StringView , default: None
    plane_0: Any  # type: TextureView , default: None
    plane_1: Optional[Any] = None  # type: TextureView , default: None
    crop_origin: Any  # type: Origin2D , default: None
    crop_size: Any  # type: Extent2D , default: None
    apparent_size: Any  # type: Extent2D , default: None
    do_yuv_to_rgb_conversion_only: Any = False  # type: Bool , default: False
    yuv_to_rgb_conversion_matrix: Optional[Any] = None  # type: float const * , default: None
    src_transfer_function_parameters: Any  # type: float const * , default: None
    dst_transfer_function_parameters: Any  # type: float const * , default: None
    gamut_conversion_matrix: Any  # type: float const * , default: None
    mirrored: Any = False  # type: Bool , default: False
    rotation: Any = ExternalTextureRotation.ROTATE0_DEGREES  # type: ExternalTextureRotation , default: ExternalTextureRotation.ROTATE0_DEGREES


@dataclass(frozen=True, kw_only=True)
class SharedBufferMemoryDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    label: Optional[Any] = None  # type: StringView , default: None


@dataclass(frozen=True, kw_only=True)
class SharedTextureMemoryDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    label: Optional[Any] = None  # type: StringView , default: None


@dataclass(frozen=True, kw_only=True)
class SharedBufferMemoryBeginAccessDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    initialized: Any  # type: Bool , default: None
    fence_count: Any = 0  # type: size_t , default: 0
    fences: Any  # type: SharedFence const * , default: None
    signaled_values: Any  # type: uint64_t const * , default: None


@dataclass(frozen=True, kw_only=True)
class SharedTextureMemoryVkDedicatedAllocationDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    dedicated_allocation: Any  # type: Bool , default: None


@dataclass(frozen=True, kw_only=True)
class SharedTextureMemoryAHardwareBufferDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    handle: Any  # type: void * , default: None
    use_external_format: Any  # type: Bool , default: None


@dataclass(frozen=True, kw_only=True)
class SharedTextureMemoryDmaBufPlane:
    fd: Any  # type: int , default: None
    offset: Any  # type: uint64_t , default: None
    stride: Any  # type: uint32_t , default: None


@dataclass(frozen=True, kw_only=True)
class SharedTextureMemoryDmaBufDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    size: Any  # type: Extent3D , default: None
    drm_format: Any  # type: uint32_t , default: None
    drm_modifier: Any  # type: uint64_t , default: None
    plane_count: Any  # type: size_t , default: None
    planes: Any  # type: SharedTextureMemoryDmaBufPlane const * , default: None


@dataclass(frozen=True, kw_only=True)
class SharedTextureMemoryOpaqueFDDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    vk_image_create_info: Any  # type: void const * , default: None
    memory_FD: Any  # type: int , default: None
    memory_type_index: Any  # type: uint32_t , default: None
    allocation_size: Any  # type: uint64_t , default: None
    dedicated_allocation: Any  # type: Bool , default: None


@dataclass(frozen=True, kw_only=True)
class SharedTextureMemoryZirconHandleDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    memory_FD: Any  # type: uint32_t , default: None
    allocation_size: Any  # type: uint64_t , default: None


@dataclass(frozen=True, kw_only=True)
class SharedTextureMemoryDXGISharedHandleDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    handle: Any  # type: void * , default: None
    use_keyed_mutex: Any  # type: Bool , default: None


@dataclass(frozen=True, kw_only=True)
class SharedTextureMemoryIOSurfaceDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    io_surface: Any  # type: void * , default: None
    allow_storage_binding: Any = True  # type: Bool , default: True


@dataclass(frozen=True, kw_only=True)
class SharedTextureMemoryEGLImageDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    image: Any  # type: void * , default: None


@dataclass(frozen=True, kw_only=True)
class SharedTextureMemoryBeginAccessDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    concurrent_read: Any  # type: Bool , default: None
    initialized: Any  # type: Bool , default: None
    fence_count: Any  # type: size_t , default: None
    fences: Any  # type: SharedFence const * , default: None
    signaled_values: Any  # type: uint64_t const * , default: None


@dataclass(frozen=True, kw_only=True)
class SharedTextureMemoryVkImageLayoutBeginState:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    old_layout: Any  # type: int32_t , default: None
    new_layout: Any  # type: int32_t , default: None


@dataclass(frozen=True, kw_only=True)
class SharedTextureMemoryD3DSwapchainBeginState:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    is_swapchain: Any = False  # type: Bool , default: False


@dataclass(frozen=True, kw_only=True)
class SharedFenceDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    label: Optional[Any] = None  # type: StringView , default: None


@dataclass(frozen=True, kw_only=True)
class SharedFenceVkSemaphoreOpaqueFDDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    handle: Any  # type: int , default: None


@dataclass(frozen=True, kw_only=True)
class SharedFenceSyncFDDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    handle: Any  # type: int , default: None


@dataclass(frozen=True, kw_only=True)
class SharedFenceVkSemaphoreZirconHandleDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    handle: Any  # type: uint32_t , default: None


@dataclass(frozen=True, kw_only=True)
class SharedFenceDXGISharedHandleDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    handle: Any  # type: void * , default: None


@dataclass(frozen=True, kw_only=True)
class SharedFenceMTLSharedEventDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    shared_event: Any  # type: void * , default: None


@dataclass(frozen=True, kw_only=True)
class SharedFenceEGLSyncDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    sync: Any  # type: void * , default: None


@dataclass(frozen=True, kw_only=True)
class DawnFakeBufferOOMForTesting:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    fake_OOM_at_wire_client_map: Any  # type: Bool , default: None
    fake_OOM_at_native_map: Any  # type: Bool , default: None
    fake_OOM_at_device: Any  # type: Bool , default: None


@dataclass(frozen=True, kw_only=True)
class DawnDrmFormatProperties:
    modifier: Any  # type: uint64_t , default: None
    modifier_plane_count: Any  # type: uint32_t , default: None


@dataclass(frozen=True, kw_only=True)
class TexelCopyBufferInfo:
    layout: Any  # type: TexelCopyBufferLayout , default: None
    buffer: Any  # type: Buffer , default: None


@dataclass(frozen=True, kw_only=True)
class TexelCopyBufferLayout:
    offset: Any = 0  # type: uint64_t , default: 0
    bytes_per_row: Any = 4294967295  # type: uint32_t , default: 4294967295
    rows_per_image: Any = 4294967295  # type: uint32_t , default: 4294967295


@dataclass(frozen=True, kw_only=True)
class TexelCopyTextureInfo:
    texture: Any  # type: Texture , default: None
    mip_level: Any = 0  # type: uint32_t , default: 0
    origin: Any  # type: Origin3D , default: None
    aspect: Any = TextureAspect.ALL  # type: TextureAspect , default: TextureAspect.ALL


@dataclass(frozen=True, kw_only=True)
class ImageCopyExternalTexture:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    external_texture: Any  # type: ExternalTexture , default: None
    origin: Any  # type: Origin3D , default: None
    natural_size: Any  # type: Extent2D , default: None


@dataclass(frozen=True, kw_only=True)
class FutureWaitInfo:
    future: Any  # type: Future , default: None
    completed: Any = False  # type: Bool , default: False


@dataclass(frozen=True, kw_only=True)
class InstanceCapabilities:
    next_in_chain: Optional[Any] = None  # type: ChainedStructOut * , default: None
    timed_wait_any_enable: Any = False  # type: Bool , default: False
    timed_wait_any_max_count: Any = 0  # type: size_t , default: 0


@dataclass(frozen=True, kw_only=True)
class InstanceDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    capabilities: Any  # type: InstanceCapabilities , default: None


@dataclass(frozen=True, kw_only=True)
class DawnWireWGSLControl:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    enable_experimental: Any = False  # type: Bool , default: False
    enable_unsafe: Any = False  # type: Bool , default: False
    enable_testing: Any = False  # type: Bool , default: False


@dataclass(frozen=True, kw_only=True)
class DawnInjectedInvalidSType:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    invalid_s_type: Any = SType.TEXTURE_BINDING_VIEW_DIMENSION_DESCRIPTOR  # type: SType , default: SType.TEXTURE_BINDING_VIEW_DIMENSION_DESCRIPTOR


@dataclass(frozen=True, kw_only=True)
class VertexAttribute:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    format: Any  # type: VertexFormat , default: None
    offset: Any  # type: uint64_t , default: None
    shader_location: Any  # type: uint32_t , default: None


@dataclass(frozen=True, kw_only=True)
class VertexBufferLayout:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    step_mode: Any = VertexStepMode.UNDEFINED  # type: VertexStepMode , default: VertexStepMode.UNDEFINED
    array_stride: Any  # type: uint64_t , default: None
    attribute_count: Any  # type: size_t , default: None
    attributes: Any  # type: VertexAttribute const * , default: None


@dataclass(frozen=True, kw_only=True)
class Origin3D:
    x: Any = 0  # type: uint32_t , default: 0
    y: Any = 0  # type: uint32_t , default: 0
    z: Any = 0  # type: uint32_t , default: 0


@dataclass(frozen=True, kw_only=True)
class Origin2D:
    x: Any = 0  # type: uint32_t , default: 0
    y: Any = 0  # type: uint32_t , default: 0


@dataclass(frozen=True, kw_only=True)
class PassTimestampWrites:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    query_set: Any  # type: QuerySet , default: None
    beginning_of_pass_write_index: Any = 4294967295  # type: uint32_t , default: 4294967295
    end_of_pass_write_index: Any = 4294967295  # type: uint32_t , default: 4294967295


@dataclass(frozen=True, kw_only=True)
class PipelineLayoutDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    label: Optional[Any] = None  # type: StringView , default: None
    bind_group_layout_count: Any  # type: size_t , default: None
    bind_group_layouts: Optional[Any] = None  # type: BindGroupLayout const * , default: None
    immediate_data_range_byte_size: Any = 0  # type: uint32_t , default: 0


@dataclass(frozen=True, kw_only=True)
class PipelineLayoutPixelLocalStorage:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    total_pixel_local_storage_size: Any  # type: uint64_t , default: None
    storage_attachment_count: Any = 0  # type: size_t , default: 0
    storage_attachments: Any  # type: PipelineLayoutStorageAttachment const * , default: None


@dataclass(frozen=True, kw_only=True)
class PipelineLayoutStorageAttachment:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    offset: Any = 0  # type: uint64_t , default: 0
    format: Any = TextureFormat.UNDEFINED  # type: TextureFormat , default: TextureFormat.UNDEFINED


@dataclass(frozen=True, kw_only=True)
class ComputeState:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    module: Any  # type: ShaderModule , default: None
    entry_point: Optional[Any] = None  # type: StringView , default: None
    constant_count: Any = 0  # type: size_t , default: 0
    constants: Any  # type: ConstantEntry const * , default: None


@dataclass(frozen=True, kw_only=True)
class QuerySetDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    label: Optional[Any] = None  # type: StringView , default: None
    type: Any  # type: QueryType , default: None
    count: Any  # type: uint32_t , default: None


@dataclass(frozen=True, kw_only=True)
class QueueDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    label: Optional[Any] = None  # type: StringView , default: None


@dataclass(frozen=True, kw_only=True)
class RenderBundleDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    label: Optional[Any] = None  # type: StringView , default: None


@dataclass(frozen=True, kw_only=True)
class RenderBundleEncoderDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    label: Optional[Any] = None  # type: StringView , default: None
    color_format_count: Any  # type: size_t , default: None
    color_formats: Any = TextureFormat.UNDEFINED  # type: TextureFormat const * , default: TextureFormat.UNDEFINED
    depth_stencil_format: Any = TextureFormat.UNDEFINED  # type: TextureFormat , default: TextureFormat.UNDEFINED
    sample_count: Any = 1  # type: uint32_t , default: 1
    depth_read_only: Any = False  # type: Bool , default: False
    stencil_read_only: Any = False  # type: Bool , default: False


@dataclass(frozen=True, kw_only=True)
class RenderPassColorAttachment:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    view: Optional[Any] = None  # type: TextureView , default: None
    depth_slice: Any = 4294967295  # type: uint32_t , default: 4294967295
    resolve_target: Optional[Any] = None  # type: TextureView , default: None
    load_op: Any = LoadOp.UNDEFINED  # type: LoadOp , default: LoadOp.UNDEFINED
    store_op: Any = StoreOp.UNDEFINED  # type: StoreOp , default: StoreOp.UNDEFINED
    clear_value: Any  # type: Color , default: None


@dataclass(frozen=True, kw_only=True)
class DawnRenderPassColorAttachmentRenderToSingleSampled:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    implicit_sample_count: Any = 1  # type: uint32_t , default: 1


@dataclass(frozen=True, kw_only=True)
class RenderPassDepthStencilAttachment:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    view: Any  # type: TextureView , default: None
    depth_load_op: Any = LoadOp.UNDEFINED  # type: LoadOp , default: LoadOp.UNDEFINED
    depth_store_op: Any = StoreOp.UNDEFINED  # type: StoreOp , default: StoreOp.UNDEFINED
    depth_clear_value: Any = None  # type: float , default: None
    depth_read_only: Any = False  # type: Bool , default: False
    stencil_load_op: Any = LoadOp.UNDEFINED  # type: LoadOp , default: LoadOp.UNDEFINED
    stencil_store_op: Any = StoreOp.UNDEFINED  # type: StoreOp , default: StoreOp.UNDEFINED
    stencil_clear_value: Any = 0  # type: uint32_t , default: 0
    stencil_read_only: Any = False  # type: Bool , default: False


@dataclass(frozen=True, kw_only=True)
class RenderPassDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    label: Optional[Any] = None  # type: StringView , default: None
    color_attachment_count: Any  # type: size_t , default: None
    color_attachments: Any  # type: RenderPassColorAttachment const * , default: None
    depth_stencil_attachment: Optional[Any] = None  # type: RenderPassDepthStencilAttachment const * , default: None
    occlusion_query_set: Optional[Any] = None  # type: QuerySet , default: None
    timestamp_writes: Optional[Any] = None  # type: PassTimestampWrites const * , default: None


@dataclass(frozen=True, kw_only=True)
class RenderPassMaxDrawCount:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    max_draw_count: Any = 50000000  # type: uint64_t , default: 50000000


@dataclass(frozen=True, kw_only=True)
class RenderPassDescriptorExpandResolveRect:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    x: Any  # type: uint32_t , default: None
    y: Any  # type: uint32_t , default: None
    width: Any  # type: uint32_t , default: None
    height: Any  # type: uint32_t , default: None


@dataclass(frozen=True, kw_only=True)
class RenderPassPixelLocalStorage:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    total_pixel_local_storage_size: Any  # type: uint64_t , default: None
    storage_attachment_count: Any = 0  # type: size_t , default: 0
    storage_attachments: Any  # type: RenderPassStorageAttachment const * , default: None


@dataclass(frozen=True, kw_only=True)
class RenderPassStorageAttachment:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    offset: Any = 0  # type: uint64_t , default: 0
    storage: Any  # type: TextureView , default: None
    load_op: Any = LoadOp.UNDEFINED  # type: LoadOp , default: LoadOp.UNDEFINED
    store_op: Any = StoreOp.UNDEFINED  # type: StoreOp , default: StoreOp.UNDEFINED
    clear_value: Any  # type: Color , default: None


@dataclass(frozen=True, kw_only=True)
class VertexState:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    module: Any  # type: ShaderModule , default: None
    entry_point: Optional[Any] = None  # type: StringView , default: None
    constant_count: Any = 0  # type: size_t , default: 0
    constants: Any  # type: ConstantEntry const * , default: None
    buffer_count: Any = 0  # type: size_t , default: 0
    buffers: Any  # type: VertexBufferLayout const * , default: None


@dataclass(frozen=True, kw_only=True)
class PrimitiveState:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    topology: Any = PrimitiveTopology.TRIANGLE_LIST  # type: PrimitiveTopology , default: PrimitiveTopology.TRIANGLE_LIST
    strip_index_format: Any = IndexFormat.UNDEFINED  # type: IndexFormat , default: IndexFormat.UNDEFINED
    front_face: Any = FrontFace.CCW  # type: FrontFace , default: FrontFace.CCW
    cull_mode: Any = CullMode.NONE  # type: CullMode , default: CullMode.NONE
    unclipped_depth: Any = False  # type: Bool , default: False


@dataclass(frozen=True, kw_only=True)
class DepthStencilState:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    format: Any = TextureFormat.UNDEFINED  # type: TextureFormat , default: TextureFormat.UNDEFINED
    depth_write_enabled: Any  # type: OptionalBool , default: None
    depth_compare: Any = CompareFunction.UNDEFINED  # type: CompareFunction , default: CompareFunction.UNDEFINED
    stencil_front: Any  # type: StencilFaceState , default: None
    stencil_back: Any  # type: StencilFaceState , default: None
    stencil_read_mask: Any = 0xFFFFFFFF  # type: uint32_t , default: 0xFFFFFFFF
    stencil_write_mask: Any = 0xFFFFFFFF  # type: uint32_t , default: 0xFFFFFFFF
    depth_bias: Any = 0  # type: int32_t , default: 0
    depth_bias_slope_scale: Any = 0.0  # type: float , default: 0.0
    depth_bias_clamp: Any = 0.0  # type: float , default: 0.0


@dataclass(frozen=True, kw_only=True)
class MultisampleState:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    count: Any = 1  # type: uint32_t , default: 1
    mask: Any = 0xFFFFFFFF  # type: uint32_t , default: 0xFFFFFFFF
    alpha_to_coverage_enabled: Any = False  # type: Bool , default: False


@dataclass(frozen=True, kw_only=True)
class FragmentState:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    module: Any  # type: ShaderModule , default: None
    entry_point: Optional[Any] = None  # type: StringView , default: None
    constant_count: Any = 0  # type: size_t , default: 0
    constants: Any  # type: ConstantEntry const * , default: None
    target_count: Any  # type: size_t , default: None
    targets: Any  # type: ColorTargetState const * , default: None


@dataclass(frozen=True, kw_only=True)
class ColorTargetState:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    format: Any = TextureFormat.UNDEFINED  # type: TextureFormat , default: TextureFormat.UNDEFINED
    blend: Optional[Any] = None  # type: BlendState const * , default: None
    write_mask: Any = ColorWriteMask.ALL  # type: ColorWriteMask , default: ColorWriteMask.ALL


@dataclass(frozen=True, kw_only=True)
class ColorTargetStateExpandResolveTextureDawn:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    enabled: Any = False  # type: Bool , default: False


@dataclass(frozen=True, kw_only=True)
class BlendState:
    color: Any  # type: BlendComponent , default: None
    alpha: Any  # type: BlendComponent , default: None


@dataclass(frozen=True, kw_only=True)
class RenderPipelineDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    label: Optional[Any] = None  # type: StringView , default: None
    layout: Optional[Any] = None  # type: PipelineLayout , default: None
    vertex: Any  # type: VertexState , default: None
    primitive: Any  # type: PrimitiveState , default: None
    depth_stencil: Optional[Any] = None  # type: DepthStencilState const * , default: None
    multisample: Any  # type: MultisampleState , default: None
    fragment: Optional[Any] = None  # type: FragmentState const * , default: None


@dataclass(frozen=True, kw_only=True)
class SamplerDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    label: Optional[Any] = None  # type: StringView , default: None
    address_mode_u: Any = AddressMode.CLAMP_TO_EDGE  # type: AddressMode , default: AddressMode.CLAMP_TO_EDGE
    address_mode_v: Any = AddressMode.CLAMP_TO_EDGE  # type: AddressMode , default: AddressMode.CLAMP_TO_EDGE
    address_mode_w: Any = AddressMode.CLAMP_TO_EDGE  # type: AddressMode , default: AddressMode.CLAMP_TO_EDGE
    mag_filter: Any = FilterMode.NEAREST  # type: FilterMode , default: FilterMode.NEAREST
    min_filter: Any = FilterMode.NEAREST  # type: FilterMode , default: FilterMode.NEAREST
    mipmap_filter: Any = MipmapFilterMode.NEAREST  # type: MipmapFilterMode , default: MipmapFilterMode.NEAREST
    lod_min_clamp: Any = 0.0  # type: float , default: 0.0
    lod_max_clamp: Any = 32.0  # type: float , default: 32.0
    compare: Any = CompareFunction.UNDEFINED  # type: CompareFunction , default: CompareFunction.UNDEFINED
    max_anisotropy: Any = 1  # type: uint16_t , default: 1


@dataclass(frozen=True, kw_only=True)
class ShaderModuleDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    label: Optional[Any] = None  # type: StringView , default: None


@dataclass(frozen=True, kw_only=True)
class ShaderSourceSPIRV:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    code_size: Any  # type: uint32_t , default: None
    code: Any  # type: uint32_t const * , default: None


@dataclass(frozen=True, kw_only=True)
class ShaderSourceWGSL:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    code: Any  # type: StringView , default: None


@dataclass(frozen=True, kw_only=True)
class DawnShaderModuleSPIRVOptionsDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    allow_non_uniform_derivatives: Any = False  # type: Bool , default: False


@dataclass(frozen=True, kw_only=True)
class ShaderModuleCompilationOptions:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    strict_math: Any  # type: Bool , default: None


@dataclass(frozen=True, kw_only=True)
class StencilFaceState:
    compare: Any = CompareFunction.ALWAYS  # type: CompareFunction , default: CompareFunction.ALWAYS
    fail_op: Any = StencilOperation.KEEP  # type: StencilOperation , default: StencilOperation.KEEP
    depth_fail_op: Any = StencilOperation.KEEP  # type: StencilOperation , default: StencilOperation.KEEP
    pass_op: Any = StencilOperation.KEEP  # type: StencilOperation , default: StencilOperation.KEEP


@dataclass(frozen=True, kw_only=True)
class SurfaceDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    label: Optional[Any] = None  # type: StringView , default: None


@dataclass(frozen=True, kw_only=True)
class SurfaceSourceAndroidNativeWindow:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    window: Any  # type: void * , default: None


@dataclass(frozen=True, kw_only=True)
class EmscriptenSurfaceSourceCanvasHTMLSelector:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    selector: Any  # type: StringView , default: None


@dataclass(frozen=True, kw_only=True)
class SurfaceSourceMetalLayer:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    layer: Any  # type: void * , default: None


@dataclass(frozen=True, kw_only=True)
class SurfaceSourceWindowsHWND:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    hinstance: Any  # type: void * , default: None
    hwnd: Any  # type: void * , default: None


@dataclass(frozen=True, kw_only=True)
class SurfaceSourceXCBWindow:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    connection: Any  # type: void * , default: None
    window: Any  # type: uint32_t , default: None


@dataclass(frozen=True, kw_only=True)
class SurfaceSourceXlibWindow:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    display: Any  # type: void * , default: None
    window: Any  # type: uint64_t , default: None


@dataclass(frozen=True, kw_only=True)
class SurfaceSourceWaylandSurface:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    display: Any  # type: void * , default: None
    surface: Any  # type: void * , default: None


@dataclass(frozen=True, kw_only=True)
class SurfaceDescriptorFromWindowsCoreWindow:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    core_window: Any  # type: void * , default: None


@dataclass(frozen=True, kw_only=True)
class SurfaceDescriptorFromWindowsUWPSwapChainPanel:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    swap_chain_panel: Any  # type: void * , default: None


@dataclass(frozen=True, kw_only=True)
class SurfaceDescriptorFromWindowsWinUISwapChainPanel:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    swap_chain_panel: Any  # type: void * , default: None


@dataclass(frozen=True, kw_only=True)
class TextureDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    label: Optional[Any] = None  # type: StringView , default: None
    usage: Any = TextureUsage.NONE  # type: TextureUsage , default: TextureUsage.NONE
    dimension: Any = TextureDimension.E2D  # type: TextureDimension , default: TextureDimension.E2D
    size: Any  # type: Extent3D , default: None
    format: Any = TextureFormat.UNDEFINED  # type: TextureFormat , default: TextureFormat.UNDEFINED
    mip_level_count: Any = 1  # type: uint32_t , default: 1
    sample_count: Any = 1  # type: uint32_t , default: 1
    view_format_count: Any = 0  # type: size_t , default: 0
    view_formats: Any = None  # type: TextureFormat const * , default: None


@dataclass(frozen=True, kw_only=True)
class TextureBindingViewDimensionDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    texture_binding_view_dimension: Any = TextureViewDimension.UNDEFINED  # type: TextureViewDimension , default: TextureViewDimension.UNDEFINED


@dataclass(frozen=True, kw_only=True)
class TextureViewDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    label: Optional[Any] = None  # type: StringView , default: None
    format: Any = TextureFormat.UNDEFINED  # type: TextureFormat , default: TextureFormat.UNDEFINED
    dimension: Any = TextureViewDimension.UNDEFINED  # type: TextureViewDimension , default: TextureViewDimension.UNDEFINED
    base_mip_level: Any = 0  # type: uint32_t , default: 0
    mip_level_count: Any = 4294967295  # type: uint32_t , default: 4294967295
    base_array_layer: Any = 0  # type: uint32_t , default: 0
    array_layer_count: Any = 4294967295  # type: uint32_t , default: 4294967295
    aspect: Any = TextureAspect.ALL  # type: TextureAspect , default: TextureAspect.ALL
    usage: Any = TextureUsage.NONE  # type: TextureUsage , default: TextureUsage.NONE


@dataclass(frozen=True, kw_only=True)
class YCbCrVkDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    vk_format: Any = 0  # type: uint32_t , default: 0
    vk_y_cb_cr_model: Any = 0  # type: uint32_t , default: 0
    vk_y_cb_cr_range: Any = 0  # type: uint32_t , default: 0
    vk_component_swizzle_red: Any = 0  # type: uint32_t , default: 0
    vk_component_swizzle_green: Any = 0  # type: uint32_t , default: 0
    vk_component_swizzle_blue: Any = 0  # type: uint32_t , default: 0
    vk_component_swizzle_alpha: Any = 0  # type: uint32_t , default: 0
    vk_x_chroma_offset: Any = 0  # type: uint32_t , default: 0
    vk_y_chroma_offset: Any = 0  # type: uint32_t , default: 0
    vk_chroma_filter: Any = FilterMode.NEAREST  # type: FilterMode , default: FilterMode.NEAREST
    force_explicit_reconstruction: Any = False  # type: Bool , default: False
    external_format: Any = 0  # type: uint64_t , default: 0


@dataclass(frozen=True, kw_only=True)
class DawnTextureInternalUsageDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    internal_usage: Any = TextureUsage.NONE  # type: TextureUsage , default: TextureUsage.NONE


@dataclass(frozen=True, kw_only=True)
class DawnEncoderInternalUsageDescriptor:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    use_internal_usages: Any = False  # type: Bool , default: False


@dataclass(frozen=True, kw_only=True)
class MemoryHeapInfo:
    properties: Any = HeapProperty.NONE  # type: HeapProperty , default: HeapProperty.NONE
    size: Any  # type: uint64_t , default: None


@dataclass(frozen=True, kw_only=True)
class DawnBufferDescriptorErrorInfoFromWireClient:
    next_in_chain: Optional[Any] = None  # type: ChainedStruct const * , default: None
    out_of_memory: Any = False  # type: Bool , default: False


@dataclass(frozen=True, kw_only=True)
class SubgroupMatrixConfig:
    component_type: Any  # type: SubgroupMatrixComponentType , default: None
    result_component_type: Any  # type: SubgroupMatrixComponentType , default: None
    M: Any  # type: uint32_t , default: None
    N: Any  # type: uint32_t , default: None
    K: Any  # type: uint32_t , default: None


@dataclass(frozen=True, kw_only=True)
class RequestAdapterCallbackInfo:
    mode: Any  # type: CallbackMode , default: None
    callback: Any  # type: RequestAdapterCallback , default: None


@dataclass(frozen=True, kw_only=True)
class BufferMapCallbackInfo:
    mode: Any  # type: CallbackMode , default: None
    callback: Any  # type: BufferMapCallback , default: None


@dataclass(frozen=True, kw_only=True)
class CompilationInfoCallbackInfo:
    mode: Any  # type: CallbackMode , default: None
    callback: Any  # type: CompilationInfoCallback , default: None


@dataclass(frozen=True, kw_only=True)
class CreateComputePipelineAsyncCallbackInfo:
    mode: Any  # type: CallbackMode , default: None
    callback: Any  # type: CreateComputePipelineAsyncCallback , default: None


@dataclass(frozen=True, kw_only=True)
class CreateRenderPipelineAsyncCallbackInfo:
    mode: Any  # type: CallbackMode , default: None
    callback: Any  # type: CreateRenderPipelineAsyncCallback , default: None


@dataclass(frozen=True, kw_only=True)
class DeviceLostCallbackInfo:
    mode: Any  # type: CallbackMode , default: None
    callback: Any = None  # type: DeviceLostCallback , default: None


@dataclass(frozen=True, kw_only=True)
class UncapturedErrorCallbackInfo:
    callback: Any = None  # type: UncapturedErrorCallback , default: None


@dataclass(frozen=True, kw_only=True)
class PopErrorScopeCallbackInfo:
    mode: Any  # type: CallbackMode , default: None
    callback: Any  # type: PopErrorScopeCallback , default: None


@dataclass(frozen=True, kw_only=True)
class LoggingCallbackInfo:
    callback: Any = None  # type: LoggingCallback , default: None


@dataclass(frozen=True, kw_only=True)
class QueueWorkDoneCallbackInfo:
    mode: Any  # type: CallbackMode , default: None
    callback: Any  # type: QueueWorkDoneCallback , default: None


@dataclass(frozen=True, kw_only=True)
class RequestDeviceCallbackInfo:
    mode: Any  # type: CallbackMode , default: None
    callback: Any  # type: RequestDeviceCallback , default: None


