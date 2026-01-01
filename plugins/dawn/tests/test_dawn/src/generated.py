from dataclasses import dataclass, field
from typing import Optional, List, Literal, Union, Any

@dataclass(frozen=True)
class RequestAdapterOptions:
    next_in_chain: Any  # type: ChainedStruct const * 
    feature_level: Any  # type: FeatureLevel 
    power_preference: Any  # type: PowerPreference 
    force_fallback_adapter: Any  # type: Bool 
    backend_type: Any  # type: BackendType 
    compatible_surface: Any  # type: Surface 

@dataclass(frozen=True)
class DeviceDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    label: Any  # type: StringView 
    required_feature_count: Any  # type: size_t 
    required_features: Any  # type: FeatureName const * 
    required_limits: Any  # type: Limits const * 
    default_queue: Any  # type: QueueDescriptor 
    device_lost_callback_info: Any  # type: DeviceLostCallbackInfo 
    uncaptured_error_callback_info: Any  # type: UncapturedErrorCallbackInfo 

@dataclass(frozen=True)
class DawnTogglesDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    enabled_toggle_count: Any  # type: size_t 
    disabled_toggle_count: Any  # type: size_t 

@dataclass(frozen=True)
class DawnCacheDeviceDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    isolation_key: Any  # type: StringView 
    function_userdata: Any  # type: void * 

@dataclass(frozen=True)
class DawnWGSLBlocklist:
    next_in_chain: Any  # type: ChainedStruct const * 
    blocklisted_feature_count: Any  # type: size_t 

@dataclass(frozen=True)
class BindGroupEntry:
    next_in_chain: Any  # type: ChainedStruct const * 
    binding: Any  # type: uint32_t 
    buffer: Any  # type: Buffer 
    offset: Any  # type: uint64_t 
    size: Any  # type: uint64_t 
    sampler: Any  # type: Sampler 
    texture_view: Any  # type: TextureView 

@dataclass(frozen=True)
class BindGroupDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    label: Any  # type: StringView 
    layout: Any  # type: BindGroupLayout 
    entry_count: Any  # type: size_t 
    entries: Any  # type: BindGroupEntry const * 

@dataclass(frozen=True)
class BufferBindingLayout:
    next_in_chain: Any  # type: ChainedStruct const * 
    type: Any  # type: BufferBindingType 
    has_dynamic_offset: Any  # type: Bool 
    min_binding_size: Any  # type: uint64_t 

@dataclass(frozen=True)
class SamplerBindingLayout:
    next_in_chain: Any  # type: ChainedStruct const * 
    type: Any  # type: SamplerBindingType 

@dataclass(frozen=True)
class StaticSamplerBindingLayout:
    next_in_chain: Any  # type: ChainedStruct const * 
    sampler: Any  # type: Sampler 
    sampled_texture_binding: Any  # type: uint32_t 

@dataclass(frozen=True)
class TextureBindingLayout:
    next_in_chain: Any  # type: ChainedStruct const * 
    sample_type: Any  # type: TextureSampleType 
    view_dimension: Any  # type: TextureViewDimension 
    multisampled: Any  # type: Bool 

@dataclass(frozen=True)
class SurfaceConfiguration:
    next_in_chain: Any  # type: ChainedStruct const * 
    device: Any  # type: Device 
    format: Any  # type: TextureFormat 
    usage: Any  # type: TextureUsage 
    width: Any  # type: uint32_t 
    height: Any  # type: uint32_t 
    view_format_count: Any  # type: size_t 
    view_formats: Any  # type: TextureFormat const * 
    alpha_mode: Any  # type: CompositeAlphaMode 
    present_mode: Any  # type: PresentMode 

@dataclass(frozen=True)
class ExternalTextureBindingEntry:
    next_in_chain: Any  # type: ChainedStruct const * 
    external_texture: Any  # type: ExternalTexture 

@dataclass(frozen=True)
class ExternalTextureBindingLayout:
    next_in_chain: Any  # type: ChainedStruct const * 

@dataclass(frozen=True)
class StorageTextureBindingLayout:
    next_in_chain: Any  # type: ChainedStruct const * 
    access: Any  # type: StorageTextureAccess 
    format: Any  # type: TextureFormat 
    view_dimension: Any  # type: TextureViewDimension 

@dataclass(frozen=True)
class BindGroupLayoutEntry:
    next_in_chain: Any  # type: ChainedStruct const * 
    binding: Any  # type: uint32_t 
    visibility: Any  # type: ShaderStage 
    buffer: Any  # type: BufferBindingLayout 
    sampler: Any  # type: SamplerBindingLayout 
    texture: Any  # type: TextureBindingLayout 
    storage_texture: Any  # type: StorageTextureBindingLayout 

@dataclass(frozen=True)
class BindGroupLayoutDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    label: Any  # type: StringView 
    entry_count: Any  # type: size_t 
    entries: Any  # type: BindGroupLayoutEntry const * 

@dataclass(frozen=True)
class BlendComponent:
    operation: Any  # type: BlendOperation 
    src_factor: Any  # type: BlendFactor 
    dst_factor: Any  # type: BlendFactor 

@dataclass(frozen=True)
class BufferDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    label: Any  # type: StringView 
    usage: Any  # type: BufferUsage 
    size: Any  # type: uint64_t 
    mapped_at_creation: Any  # type: Bool 

@dataclass(frozen=True)
class BufferHostMappedPointer:
    next_in_chain: Any  # type: ChainedStruct const * 
    pointer: Any  # type: void * 
    userdata: Any  # type: void * 

@dataclass(frozen=True)
class Color:
    r: Any  # type: double 
    g: Any  # type: double 
    b: Any  # type: double 
    a: Any  # type: double 

@dataclass(frozen=True)
class ConstantEntry:
    next_in_chain: Any  # type: ChainedStruct const * 
    key: Any  # type: StringView 
    value: Any  # type: double 

@dataclass(frozen=True)
class CommandBufferDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    label: Any  # type: StringView 

@dataclass(frozen=True)
class CommandEncoderDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    label: Any  # type: StringView 

@dataclass(frozen=True)
class CompilationInfo:
    next_in_chain: Any  # type: ChainedStruct const * 
    message_count: Any  # type: size_t 
    messages: Any  # type: CompilationMessage const * 

@dataclass(frozen=True)
class CompilationMessage:
    next_in_chain: Any  # type: ChainedStruct const * 
    message: Any  # type: StringView 
    type: Any  # type: CompilationMessageType 
    line_num: Any  # type: uint64_t 
    line_pos: Any  # type: uint64_t 
    offset: Any  # type: uint64_t 
    length: Any  # type: uint64_t 

@dataclass(frozen=True)
class DawnCompilationMessageUtf16:
    next_in_chain: Any  # type: ChainedStruct const * 
    line_pos: Any  # type: uint64_t 
    offset: Any  # type: uint64_t 
    length: Any  # type: uint64_t 

@dataclass(frozen=True)
class ComputePassDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    label: Any  # type: StringView 
    timestamp_writes: Any  # type: PassTimestampWrites const * 

@dataclass(frozen=True)
class ComputePipelineDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    label: Any  # type: StringView 
    layout: Any  # type: PipelineLayout 
    compute: Any  # type: ComputeState 

@dataclass(frozen=True)
class CopyTextureForBrowserOptions:
    next_in_chain: Any  # type: ChainedStruct const * 
    flip_y: Any  # type: Bool 
    needs_color_space_conversion: Any  # type: Bool 
    src_alpha_mode: Any  # type: AlphaMode 
    src_transfer_function_parameters: Any  # type: float const * 
    conversion_matrix: Any  # type: float const * 
    dst_transfer_function_parameters: Any  # type: float const * 
    dst_alpha_mode: Any  # type: AlphaMode 
    internal_usage: Any  # type: Bool 

@dataclass(frozen=True)
class AHardwareBufferProperties:
    y_cb_cr_info: Any  # type: YCbCrVkDescriptor 

@dataclass(frozen=True)
class Limits:
    next_in_chain: Any  # type: ChainedStructOut * 
    max_texture_dimension_1D: Any  # type: uint32_t 
    max_texture_dimension_2D: Any  # type: uint32_t 
    max_texture_dimension_3D: Any  # type: uint32_t 
    max_texture_array_layers: Any  # type: uint32_t 
    max_bind_groups: Any  # type: uint32_t 
    max_bind_groups_plus_vertex_buffers: Any  # type: uint32_t 
    max_bindings_per_bind_group: Any  # type: uint32_t 
    max_dynamic_uniform_buffers_per_pipeline_layout: Any  # type: uint32_t 
    max_dynamic_storage_buffers_per_pipeline_layout: Any  # type: uint32_t 
    max_sampled_textures_per_shader_stage: Any  # type: uint32_t 
    max_samplers_per_shader_stage: Any  # type: uint32_t 
    max_storage_buffers_per_shader_stage: Any  # type: uint32_t 
    max_storage_textures_per_shader_stage: Any  # type: uint32_t 
    max_uniform_buffers_per_shader_stage: Any  # type: uint32_t 
    max_uniform_buffer_binding_size: Any  # type: uint64_t 
    max_storage_buffer_binding_size: Any  # type: uint64_t 
    min_uniform_buffer_offset_alignment: Any  # type: uint32_t 
    min_storage_buffer_offset_alignment: Any  # type: uint32_t 
    max_vertex_buffers: Any  # type: uint32_t 
    max_buffer_size: Any  # type: uint64_t 
    max_vertex_attributes: Any  # type: uint32_t 
    max_vertex_buffer_array_stride: Any  # type: uint32_t 
    max_inter_stage_shader_variables: Any  # type: uint32_t 
    max_color_attachments: Any  # type: uint32_t 
    max_color_attachment_bytes_per_sample: Any  # type: uint32_t 
    max_compute_workgroup_storage_size: Any  # type: uint32_t 
    max_compute_invocations_per_workgroup: Any  # type: uint32_t 
    max_compute_workgroup_size_x: Any  # type: uint32_t 
    max_compute_workgroup_size_y: Any  # type: uint32_t 
    max_compute_workgroup_size_z: Any  # type: uint32_t 
    max_compute_workgroups_per_dimension: Any  # type: uint32_t 
    max_storage_buffers_in_vertex_stage: Any  # type: uint32_t 
    max_storage_textures_in_vertex_stage: Any  # type: uint32_t 
    max_storage_buffers_in_fragment_stage: Any  # type: uint32_t 
    max_storage_textures_in_fragment_stage: Any  # type: uint32_t 

@dataclass(frozen=True)
class SupportedFeatures:
    feature_count: Any  # type: size_t 
    features: Any  # type: FeatureName const * 

@dataclass(frozen=True)
class SupportedWGSLLanguageFeatures:
    feature_count: Any  # type: size_t 
    features: Any  # type: WGSLLanguageFeatureName const * 

@dataclass(frozen=True)
class Extent2D:
    width: Any  # type: uint32_t 
    height: Any  # type: uint32_t 

@dataclass(frozen=True)
class Extent3D:
    width: Any  # type: uint32_t 
    height: Any  # type: uint32_t 
    depth_or_array_layers: Any  # type: uint32_t 

@dataclass(frozen=True)
class ExternalTextureDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    label: Any  # type: StringView 
    plane_0: Any  # type: TextureView 
    plane_1: Any  # type: TextureView 
    crop_origin: Any  # type: Origin2D 
    crop_size: Any  # type: Extent2D 
    apparent_size: Any  # type: Extent2D 
    do_yuv_to_rgb_conversion_only: Any  # type: Bool 
    yuv_to_rgb_conversion_matrix: Any  # type: float const * 
    src_transfer_function_parameters: Any  # type: float const * 
    dst_transfer_function_parameters: Any  # type: float const * 
    gamut_conversion_matrix: Any  # type: float const * 
    mirrored: Any  # type: Bool 
    rotation: Any  # type: ExternalTextureRotation 

@dataclass(frozen=True)
class SharedBufferMemoryDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    label: Any  # type: StringView 

@dataclass(frozen=True)
class SharedTextureMemoryDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    label: Any  # type: StringView 

@dataclass(frozen=True)
class SharedBufferMemoryBeginAccessDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    initialized: Any  # type: Bool 
    fence_count: Any  # type: size_t 
    fences: Any  # type: SharedFence const * 
    signaled_values: Any  # type: uint64_t const * 

@dataclass(frozen=True)
class SharedTextureMemoryVkDedicatedAllocationDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    dedicated_allocation: Any  # type: Bool 

@dataclass(frozen=True)
class SharedTextureMemoryAHardwareBufferDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    handle: Any  # type: void * 
    use_external_format: Any  # type: Bool 

@dataclass(frozen=True)
class SharedTextureMemoryDmaBufPlane:
    fd: Any  # type: int 
    offset: Any  # type: uint64_t 
    stride: Any  # type: uint32_t 

@dataclass(frozen=True)
class SharedTextureMemoryDmaBufDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    size: Any  # type: Extent3D 
    drm_format: Any  # type: uint32_t 
    drm_modifier: Any  # type: uint64_t 
    plane_count: Any  # type: size_t 
    planes: Any  # type: SharedTextureMemoryDmaBufPlane const * 

@dataclass(frozen=True)
class SharedTextureMemoryOpaqueFDDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    vk_image_create_info: Any  # type: void const * 
    memory_FD: Any  # type: int 
    memory_type_index: Any  # type: uint32_t 
    allocation_size: Any  # type: uint64_t 
    dedicated_allocation: Any  # type: Bool 

@dataclass(frozen=True)
class SharedTextureMemoryZirconHandleDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    memory_FD: Any  # type: uint32_t 
    allocation_size: Any  # type: uint64_t 

@dataclass(frozen=True)
class SharedTextureMemoryDXGISharedHandleDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    handle: Any  # type: void * 
    use_keyed_mutex: Any  # type: Bool 

@dataclass(frozen=True)
class SharedTextureMemoryIOSurfaceDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    io_surface: Any  # type: void * 
    allow_storage_binding: Any  # type: Bool 

@dataclass(frozen=True)
class SharedTextureMemoryEGLImageDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    image: Any  # type: void * 

@dataclass(frozen=True)
class SharedTextureMemoryBeginAccessDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    concurrent_read: Any  # type: Bool 
    initialized: Any  # type: Bool 
    fence_count: Any  # type: size_t 
    fences: Any  # type: SharedFence const * 
    signaled_values: Any  # type: uint64_t const * 

@dataclass(frozen=True)
class SharedTextureMemoryVkImageLayoutBeginState:
    next_in_chain: Any  # type: ChainedStruct const * 
    old_layout: Any  # type: int32_t 
    new_layout: Any  # type: int32_t 

@dataclass(frozen=True)
class SharedTextureMemoryD3DSwapchainBeginState:
    next_in_chain: Any  # type: ChainedStruct const * 
    is_swapchain: Any  # type: Bool 

@dataclass(frozen=True)
class SharedFenceDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    label: Any  # type: StringView 

@dataclass(frozen=True)
class SharedFenceVkSemaphoreOpaqueFDDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    handle: Any  # type: int 

@dataclass(frozen=True)
class SharedFenceSyncFDDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    handle: Any  # type: int 

@dataclass(frozen=True)
class SharedFenceVkSemaphoreZirconHandleDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    handle: Any  # type: uint32_t 

@dataclass(frozen=True)
class SharedFenceDXGISharedHandleDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    handle: Any  # type: void * 

@dataclass(frozen=True)
class SharedFenceMTLSharedEventDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    shared_event: Any  # type: void * 

@dataclass(frozen=True)
class SharedFenceEGLSyncDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    sync: Any  # type: void * 

@dataclass(frozen=True)
class DawnFakeBufferOOMForTesting:
    next_in_chain: Any  # type: ChainedStruct const * 
    fake_OOM_at_wire_client_map: Any  # type: Bool 
    fake_OOM_at_native_map: Any  # type: Bool 
    fake_OOM_at_device: Any  # type: Bool 

@dataclass(frozen=True)
class DawnDrmFormatProperties:
    modifier: Any  # type: uint64_t 
    modifier_plane_count: Any  # type: uint32_t 

@dataclass(frozen=True)
class TexelCopyBufferInfo:
    layout: Any  # type: TexelCopyBufferLayout 
    buffer: Any  # type: Buffer 

@dataclass(frozen=True)
class TexelCopyBufferLayout:
    offset: Any  # type: uint64_t 
    bytes_per_row: Any  # type: uint32_t 
    rows_per_image: Any  # type: uint32_t 

@dataclass(frozen=True)
class TexelCopyTextureInfo:
    texture: Any  # type: Texture 
    mip_level: Any  # type: uint32_t 
    origin: Any  # type: Origin3D 
    aspect: Any  # type: TextureAspect 

@dataclass(frozen=True)
class ImageCopyExternalTexture:
    next_in_chain: Any  # type: ChainedStruct const * 
    external_texture: Any  # type: ExternalTexture 
    origin: Any  # type: Origin3D 
    natural_size: Any  # type: Extent2D 

@dataclass(frozen=True)
class Future:
    id: Any  # type: uint64_t 

@dataclass(frozen=True)
class FutureWaitInfo:
    future: Any  # type: Future 
    completed: Any  # type: Bool 

@dataclass(frozen=True)
class InstanceCapabilities:
    next_in_chain: Any  # type: ChainedStructOut * 
    timed_wait_any_enable: Any  # type: Bool 
    timed_wait_any_max_count: Any  # type: size_t 

@dataclass(frozen=True)
class InstanceDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    capabilities: Any  # type: InstanceCapabilities 

@dataclass(frozen=True)
class DawnWireWGSLControl:
    next_in_chain: Any  # type: ChainedStruct const * 
    enable_experimental: Any  # type: Bool 
    enable_unsafe: Any  # type: Bool 
    enable_testing: Any  # type: Bool 

@dataclass(frozen=True)
class DawnInjectedInvalidSType:
    next_in_chain: Any  # type: ChainedStruct const * 
    invalid_s_type: Any  # type: SType 

@dataclass(frozen=True)
class VertexAttribute:
    next_in_chain: Any  # type: ChainedStruct const * 
    format: Any  # type: VertexFormat 
    offset: Any  # type: uint64_t 
    shader_location: Any  # type: uint32_t 

@dataclass(frozen=True)
class VertexBufferLayout:
    next_in_chain: Any  # type: ChainedStruct const * 
    step_mode: Any  # type: VertexStepMode 
    array_stride: Any  # type: uint64_t 
    attribute_count: Any  # type: size_t 
    attributes: Any  # type: VertexAttribute const * 

@dataclass(frozen=True)
class Origin3D:
    x: Any  # type: uint32_t 
    y: Any  # type: uint32_t 
    z: Any  # type: uint32_t 

@dataclass(frozen=True)
class Origin2D:
    x: Any  # type: uint32_t 
    y: Any  # type: uint32_t 

@dataclass(frozen=True)
class PassTimestampWrites:
    next_in_chain: Any  # type: ChainedStruct const * 
    query_set: Any  # type: QuerySet 
    beginning_of_pass_write_index: Any  # type: uint32_t 
    end_of_pass_write_index: Any  # type: uint32_t 

@dataclass(frozen=True)
class PipelineLayoutDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    label: Any  # type: StringView 
    bind_group_layout_count: Any  # type: size_t 
    bind_group_layouts: Any  # type: BindGroupLayout const * 
    immediate_data_range_byte_size: Any  # type: uint32_t 

@dataclass(frozen=True)
class PipelineLayoutPixelLocalStorage:
    next_in_chain: Any  # type: ChainedStruct const * 
    total_pixel_local_storage_size: Any  # type: uint64_t 
    storage_attachment_count: Any  # type: size_t 
    storage_attachments: Any  # type: PipelineLayoutStorageAttachment const * 

@dataclass(frozen=True)
class PipelineLayoutStorageAttachment:
    next_in_chain: Any  # type: ChainedStruct const * 
    offset: Any  # type: uint64_t 
    format: Any  # type: TextureFormat 

@dataclass(frozen=True)
class ComputeState:
    next_in_chain: Any  # type: ChainedStruct const * 
    module: Any  # type: ShaderModule 
    entry_point: Any  # type: StringView 
    constant_count: Any  # type: size_t 
    constants: Any  # type: ConstantEntry const * 

@dataclass(frozen=True)
class QuerySetDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    label: Any  # type: StringView 
    type: Any  # type: QueryType 
    count: Any  # type: uint32_t 

@dataclass(frozen=True)
class QueueDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    label: Any  # type: StringView 

@dataclass(frozen=True)
class RenderBundleDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    label: Any  # type: StringView 

@dataclass(frozen=True)
class RenderBundleEncoderDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    label: Any  # type: StringView 
    color_format_count: Any  # type: size_t 
    color_formats: Any  # type: TextureFormat const * 
    depth_stencil_format: Any  # type: TextureFormat 
    sample_count: Any  # type: uint32_t 
    depth_read_only: Any  # type: Bool 
    stencil_read_only: Any  # type: Bool 

@dataclass(frozen=True)
class RenderPassColorAttachment:
    next_in_chain: Any  # type: ChainedStruct const * 
    view: Any  # type: TextureView 
    depth_slice: Any  # type: uint32_t 
    resolve_target: Any  # type: TextureView 
    load_op: Any  # type: LoadOp 
    store_op: Any  # type: StoreOp 
    clear_value: Any  # type: Color 

@dataclass(frozen=True)
class DawnRenderPassColorAttachmentRenderToSingleSampled:
    next_in_chain: Any  # type: ChainedStruct const * 
    implicit_sample_count: Any  # type: uint32_t 

@dataclass(frozen=True)
class RenderPassDepthStencilAttachment:
    next_in_chain: Any  # type: ChainedStruct const * 
    view: Any  # type: TextureView 
    depth_load_op: Any  # type: LoadOp 
    depth_store_op: Any  # type: StoreOp 
    depth_clear_value: Any  # type: float 
    depth_read_only: Any  # type: Bool 
    stencil_load_op: Any  # type: LoadOp 
    stencil_store_op: Any  # type: StoreOp 
    stencil_clear_value: Any  # type: uint32_t 
    stencil_read_only: Any  # type: Bool 

@dataclass(frozen=True)
class RenderPassDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    label: Any  # type: StringView 
    color_attachment_count: Any  # type: size_t 
    color_attachments: Any  # type: RenderPassColorAttachment const * 
    depth_stencil_attachment: Any  # type: RenderPassDepthStencilAttachment const * 
    occlusion_query_set: Any  # type: QuerySet 
    timestamp_writes: Any  # type: PassTimestampWrites const * 

@dataclass(frozen=True)
class RenderPassMaxDrawCount:
    next_in_chain: Any  # type: ChainedStruct const * 
    max_draw_count: Any  # type: uint64_t 

@dataclass(frozen=True)
class RenderPassDescriptorExpandResolveRect:
    next_in_chain: Any  # type: ChainedStruct const * 
    x: Any  # type: uint32_t 
    y: Any  # type: uint32_t 
    width: Any  # type: uint32_t 
    height: Any  # type: uint32_t 

@dataclass(frozen=True)
class RenderPassPixelLocalStorage:
    next_in_chain: Any  # type: ChainedStruct const * 
    total_pixel_local_storage_size: Any  # type: uint64_t 
    storage_attachment_count: Any  # type: size_t 
    storage_attachments: Any  # type: RenderPassStorageAttachment const * 

@dataclass(frozen=True)
class RenderPassStorageAttachment:
    next_in_chain: Any  # type: ChainedStruct const * 
    offset: Any  # type: uint64_t 
    storage: Any  # type: TextureView 
    load_op: Any  # type: LoadOp 
    store_op: Any  # type: StoreOp 
    clear_value: Any  # type: Color 

@dataclass(frozen=True)
class VertexState:
    next_in_chain: Any  # type: ChainedStruct const * 
    module: Any  # type: ShaderModule 
    entry_point: Any  # type: StringView 
    constant_count: Any  # type: size_t 
    constants: Any  # type: ConstantEntry const * 
    buffer_count: Any  # type: size_t 
    buffers: Any  # type: VertexBufferLayout const * 

@dataclass(frozen=True)
class PrimitiveState:
    next_in_chain: Any  # type: ChainedStruct const * 
    topology: Any  # type: PrimitiveTopology 
    strip_index_format: Any  # type: IndexFormat 
    front_face: Any  # type: FrontFace 
    cull_mode: Any  # type: CullMode 
    unclipped_depth: Any  # type: Bool 

@dataclass(frozen=True)
class DepthStencilState:
    next_in_chain: Any  # type: ChainedStruct const * 
    format: Any  # type: TextureFormat 
    depth_write_enabled: Any  # type: OptionalBool 
    depth_compare: Any  # type: CompareFunction 
    stencil_front: Any  # type: StencilFaceState 
    stencil_back: Any  # type: StencilFaceState 
    stencil_read_mask: Any  # type: uint32_t 
    stencil_write_mask: Any  # type: uint32_t 
    depth_bias: Any  # type: int32_t 
    depth_bias_slope_scale: Any  # type: float 
    depth_bias_clamp: Any  # type: float 

@dataclass(frozen=True)
class MultisampleState:
    next_in_chain: Any  # type: ChainedStruct const * 
    count: Any  # type: uint32_t 
    mask: Any  # type: uint32_t 
    alpha_to_coverage_enabled: Any  # type: Bool 

@dataclass(frozen=True)
class FragmentState:
    next_in_chain: Any  # type: ChainedStruct const * 
    module: Any  # type: ShaderModule 
    entry_point: Any  # type: StringView 
    constant_count: Any  # type: size_t 
    constants: Any  # type: ConstantEntry const * 
    target_count: Any  # type: size_t 
    targets: Any  # type: ColorTargetState const * 

@dataclass(frozen=True)
class ColorTargetState:
    next_in_chain: Any  # type: ChainedStruct const * 
    format: Any  # type: TextureFormat 
    blend: Any  # type: BlendState const * 
    write_mask: Any  # type: ColorWriteMask 

@dataclass(frozen=True)
class ColorTargetStateExpandResolveTextureDawn:
    next_in_chain: Any  # type: ChainedStruct const * 
    enabled: Any  # type: Bool 

@dataclass(frozen=True)
class BlendState:
    color: Any  # type: BlendComponent 
    alpha: Any  # type: BlendComponent 

@dataclass(frozen=True)
class RenderPipelineDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    label: Any  # type: StringView 
    layout: Any  # type: PipelineLayout 
    vertex: Any  # type: VertexState 
    primitive: Any  # type: PrimitiveState 
    depth_stencil: Any  # type: DepthStencilState const * 
    multisample: Any  # type: MultisampleState 
    fragment: Any  # type: FragmentState const * 

@dataclass(frozen=True)
class SamplerDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    label: Any  # type: StringView 
    address_mode_u: Any  # type: AddressMode 
    address_mode_v: Any  # type: AddressMode 
    address_mode_w: Any  # type: AddressMode 
    mag_filter: Any  # type: FilterMode 
    min_filter: Any  # type: FilterMode 
    mipmap_filter: Any  # type: MipmapFilterMode 
    lod_min_clamp: Any  # type: float 
    lod_max_clamp: Any  # type: float 
    compare: Any  # type: CompareFunction 
    max_anisotropy: Any  # type: uint16_t 

@dataclass(frozen=True)
class ShaderModuleDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    label: Any  # type: StringView 

@dataclass(frozen=True)
class ShaderSourceSPIRV:
    next_in_chain: Any  # type: ChainedStruct const * 
    code_size: Any  # type: uint32_t 
    code: Any  # type: uint32_t const * 

@dataclass(frozen=True)
class ShaderSourceWGSL:
    next_in_chain: Any  # type: ChainedStruct const * 
    code: Any  # type: StringView 

@dataclass(frozen=True)
class DawnShaderModuleSPIRVOptionsDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    allow_non_uniform_derivatives: Any  # type: Bool 

@dataclass(frozen=True)
class ShaderModuleCompilationOptions:
    next_in_chain: Any  # type: ChainedStruct const * 
    strict_math: Any  # type: Bool 

@dataclass(frozen=True)
class StencilFaceState:
    compare: Any  # type: CompareFunction 
    fail_op: Any  # type: StencilOperation 
    depth_fail_op: Any  # type: StencilOperation 
    pass_op: Any  # type: StencilOperation 

@dataclass(frozen=True)
class SurfaceDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    label: Any  # type: StringView 

@dataclass(frozen=True)
class SurfaceSourceAndroidNativeWindow:
    next_in_chain: Any  # type: ChainedStruct const * 
    window: Any  # type: void * 

@dataclass(frozen=True)
class EmscriptenSurfaceSourceCanvasHTMLSelector:
    next_in_chain: Any  # type: ChainedStruct const * 
    selector: Any  # type: StringView 

@dataclass(frozen=True)
class SurfaceSourceMetalLayer:
    next_in_chain: Any  # type: ChainedStruct const * 
    layer: Any  # type: void * 

@dataclass(frozen=True)
class SurfaceSourceWindowsHWND:
    next_in_chain: Any  # type: ChainedStruct const * 
    hinstance: Any  # type: void * 
    hwnd: Any  # type: void * 

@dataclass(frozen=True)
class SurfaceSourceXCBWindow:
    next_in_chain: Any  # type: ChainedStruct const * 
    connection: Any  # type: void * 
    window: Any  # type: uint32_t 

@dataclass(frozen=True)
class SurfaceSourceXlibWindow:
    next_in_chain: Any  # type: ChainedStruct const * 
    display: Any  # type: void * 
    window: Any  # type: uint64_t 

@dataclass(frozen=True)
class SurfaceSourceWaylandSurface:
    next_in_chain: Any  # type: ChainedStruct const * 
    display: Any  # type: void * 
    surface: Any  # type: void * 

@dataclass(frozen=True)
class SurfaceDescriptorFromWindowsCoreWindow:
    next_in_chain: Any  # type: ChainedStruct const * 
    core_window: Any  # type: void * 

@dataclass(frozen=True)
class SurfaceDescriptorFromWindowsUWPSwapChainPanel:
    next_in_chain: Any  # type: ChainedStruct const * 
    swap_chain_panel: Any  # type: void * 

@dataclass(frozen=True)
class SurfaceDescriptorFromWindowsWinUISwapChainPanel:
    next_in_chain: Any  # type: ChainedStruct const * 
    swap_chain_panel: Any  # type: void * 

@dataclass(frozen=True)
class TextureDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    label: Any  # type: StringView 
    usage: Any  # type: TextureUsage 
    dimension: Any  # type: TextureDimension 
    size: Any  # type: Extent3D 
    format: Any  # type: TextureFormat 
    mip_level_count: Any  # type: uint32_t 
    sample_count: Any  # type: uint32_t 
    view_format_count: Any  # type: size_t 
    view_formats: Any  # type: TextureFormat const * 

@dataclass(frozen=True)
class TextureBindingViewDimensionDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    texture_binding_view_dimension: Any  # type: TextureViewDimension 

@dataclass(frozen=True)
class TextureViewDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    label: Any  # type: StringView 
    format: Any  # type: TextureFormat 
    dimension: Any  # type: TextureViewDimension 
    base_mip_level: Any  # type: uint32_t 
    mip_level_count: Any  # type: uint32_t 
    base_array_layer: Any  # type: uint32_t 
    array_layer_count: Any  # type: uint32_t 
    aspect: Any  # type: TextureAspect 
    usage: Any  # type: TextureUsage 

@dataclass(frozen=True)
class YCbCrVkDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    vk_format: Any  # type: uint32_t 
    vk_y_cb_cr_model: Any  # type: uint32_t 
    vk_y_cb_cr_range: Any  # type: uint32_t 
    vk_component_swizzle_red: Any  # type: uint32_t 
    vk_component_swizzle_green: Any  # type: uint32_t 
    vk_component_swizzle_blue: Any  # type: uint32_t 
    vk_component_swizzle_alpha: Any  # type: uint32_t 
    vk_x_chroma_offset: Any  # type: uint32_t 
    vk_y_chroma_offset: Any  # type: uint32_t 
    vk_chroma_filter: Any  # type: FilterMode 
    force_explicit_reconstruction: Any  # type: Bool 
    external_format: Any  # type: uint64_t 

@dataclass(frozen=True)
class DawnTextureInternalUsageDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    internal_usage: Any  # type: TextureUsage 

@dataclass(frozen=True)
class DawnEncoderInternalUsageDescriptor:
    next_in_chain: Any  # type: ChainedStruct const * 
    use_internal_usages: Any  # type: Bool 

@dataclass(frozen=True)
class MemoryHeapInfo:
    properties: Any  # type: HeapProperty 
    size: Any  # type: uint64_t 

@dataclass(frozen=True)
class DawnBufferDescriptorErrorInfoFromWireClient:
    next_in_chain: Any  # type: ChainedStruct const * 
    out_of_memory: Any  # type: Bool 

@dataclass(frozen=True)
class SubgroupMatrixConfig:
    component_type: Any  # type: SubgroupMatrixComponentType 
    result_component_type: Any  # type: SubgroupMatrixComponentType 
    M: Any  # type: uint32_t 
    N: Any  # type: uint32_t 
    K: Any  # type: uint32_t 

