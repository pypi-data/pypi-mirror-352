from collections.abc import Iterable, Iterator
import enum
from typing import Annotated, overload

from numpy.typing import ArrayLike

import lagrange


class Animation:
    def __init__(self) -> None: ...

    def __repr__(self) -> str: ...

    @property
    def name(self) -> str: ...

    @name.setter
    def name(self, arg: str, /) -> None: ...

    @property
    def extensions(self) -> Extensions: ...

    @extensions.setter
    def extensions(self, arg: Extensions, /) -> None: ...

class AnimationList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: AnimationList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Animation], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Animation]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Animation: ...

    @overload
    def __getitem__(self, arg: slice, /) -> AnimationList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Animation, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Animation, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Animation:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: AnimationList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Animation, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: AnimationList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

class BufferList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: BufferList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[int], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[int]: ...

    @overload
    def __getitem__(self, arg: int, /) -> int: ...

    @overload
    def __getitem__(self, arg: slice, /) -> BufferList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: int, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: int, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> int:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: BufferList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: int, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: BufferList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: int, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: int, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: int, /) -> None:
        """Remove first occurrence of `arg`."""

class Camera:
    """Camera"""

    def __init__(self) -> None: ...

    def __repr__(self) -> str: ...

    @property
    def name(self) -> str: ...

    @name.setter
    def name(self, arg: str, /) -> None: ...

    @property
    def position(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')]: ...

    @position.setter
    def position(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')], /) -> None: ...

    @property
    def up(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')]: ...

    @up.setter
    def up(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')], /) -> None: ...

    @property
    def look_at(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')]: ...

    @look_at.setter
    def look_at(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')], /) -> None: ...

    @property
    def near_plane(self) -> float: ...

    @near_plane.setter
    def near_plane(self, arg: float, /) -> None: ...

    @property
    def far_plane(self) -> float: ...

    @far_plane.setter
    def far_plane(self, arg: float, /) -> None: ...

    @property
    def type(self) -> Camera.Type: ...

    @type.setter
    def type(self, arg: Camera.Type, /) -> None: ...

    @property
    def aspect_ratio(self) -> float: ...

    @aspect_ratio.setter
    def aspect_ratio(self, arg: float, /) -> None: ...

    @property
    def horizontal_fov(self) -> float: ...

    @horizontal_fov.setter
    def horizontal_fov(self, arg: float, /) -> None: ...

    @property
    def orthographic_width(self) -> float: ...

    @orthographic_width.setter
    def orthographic_width(self, arg: float, /) -> None: ...

    @property
    def get_vertical_fov(self) -> float: ...

    @property
    def set_horizontal_fov_from_vertical_fov(self, arg: float, /) -> None: ...

    @property
    def extensions(self) -> Extensions: ...

    @extensions.setter
    def extensions(self, arg: Extensions, /) -> None: ...

    class Type(enum.Enum):
        """Camera type"""

        Perspective = 0

        Orthographic = 1

class CameraList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: CameraList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Camera], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Camera]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Camera: ...

    @overload
    def __getitem__(self, arg: slice, /) -> CameraList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Camera, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Camera, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Camera:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: CameraList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Camera, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: CameraList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

class ElementIdList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: ElementIdList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[int], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[int]: ...

    @overload
    def __getitem__(self, arg: int, /) -> int: ...

    @overload
    def __getitem__(self, arg: slice, /) -> ElementIdList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: int, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: int, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> int:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: ElementIdList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: int, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: ElementIdList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: int, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: int, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: int, /) -> None:
        """Remove first occurrence of `arg`."""

class Extensions:
    def __repr__(self) -> str: ...

    @property
    def size(self) -> int: ...

    @property
    def empty(self) -> bool: ...

    @property
    def data(self) -> ValueUnorderedMap: ...

    @data.setter
    def data(self, arg: ValueUnorderedMap, /) -> None: ...

class FacetAllocationStrategy(enum.Enum):
    EvenSplit = 0

    RelativeToMeshArea = 1

    RelativeToNumFacets = 2

    Synchronized = 3

class Image:
    def __init__(self) -> None: ...

    def __repr__(self) -> str: ...

    @property
    def name(self) -> str:
        """Name of the image object"""

    @name.setter
    def name(self, arg: str, /) -> None: ...

    @property
    def image(self) -> ImageBuffer:
        """Image buffer"""

    @image.setter
    def image(self, arg: ImageBuffer, /) -> None: ...

    @property
    def uri(self) -> str | None:
        """URI of the image file"""

    @uri.setter
    def uri(self, arg: str, /) -> None: ...

    @property
    def extensions(self) -> Extensions:
        """Additional data associated with the image"""

    @extensions.setter
    def extensions(self, arg: Extensions, /) -> None: ...

class ImageBuffer:
    def __init__(self) -> None: ...

    def __repr__(self) -> str: ...

    @property
    def width(self) -> int:
        """Image width"""

    @property
    def height(self) -> int:
        """Image height"""

    @property
    def num_channels(self) -> int:
        """Number of channels in each pixel"""

    @property
    def data(self) -> object:
        """Raw image data."""

    @data.setter
    def data(self, arg: Annotated[ArrayLike, dict(order='C', device='cpu')], /) -> None: ...

    @property
    def dtype(self) -> type | None:
        """The element data type of the image buffer."""

class ImageList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: ImageList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Image], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Image]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Image: ...

    @overload
    def __getitem__(self, arg: slice, /) -> ImageList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Image, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Image, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Image:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: ImageList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Image, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: ImageList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

class Light:
    """Light"""

    def __init__(self) -> None: ...

    def __repr__(self) -> str: ...

    @property
    def name(self) -> str: ...

    @name.setter
    def name(self, arg: str, /) -> None: ...

    @property
    def type(self) -> Light.Type: ...

    @type.setter
    def type(self, arg: Light.Type, /) -> None: ...

    @property
    def position(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')]: ...

    @position.setter
    def position(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')], /) -> None: ...

    @property
    def direction(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')]: ...

    @direction.setter
    def direction(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')], /) -> None: ...

    @property
    def up(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')]: ...

    @up.setter
    def up(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')], /) -> None: ...

    @property
    def intensity(self) -> float: ...

    @intensity.setter
    def intensity(self, arg: float, /) -> None: ...

    @property
    def attenuation_constant(self) -> float: ...

    @attenuation_constant.setter
    def attenuation_constant(self, arg: float, /) -> None: ...

    @property
    def attenuation_linear(self) -> float: ...

    @attenuation_linear.setter
    def attenuation_linear(self, arg: float, /) -> None: ...

    @property
    def attenuation_quadratic(self) -> float: ...

    @attenuation_quadratic.setter
    def attenuation_quadratic(self, arg: float, /) -> None: ...

    @property
    def attenuation_cubic(self) -> float: ...

    @attenuation_cubic.setter
    def attenuation_cubic(self, arg: float, /) -> None: ...

    @property
    def range(self) -> float: ...

    @range.setter
    def range(self, arg: float, /) -> None: ...

    @property
    def color_diffuse(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')]: ...

    @color_diffuse.setter
    def color_diffuse(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')], /) -> None: ...

    @property
    def color_specular(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')]: ...

    @color_specular.setter
    def color_specular(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')], /) -> None: ...

    @property
    def color_ambient(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')]: ...

    @color_ambient.setter
    def color_ambient(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')], /) -> None: ...

    @property
    def angle_inner_cone(self) -> float: ...

    @angle_inner_cone.setter
    def angle_inner_cone(self, arg: float, /) -> None: ...

    @property
    def angle_outer_cone(self) -> float: ...

    @angle_outer_cone.setter
    def angle_outer_cone(self, arg: float, /) -> None: ...

    @property
    def size(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(2), order='C')]: ...

    @size.setter
    def size(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(2), order='C')], /) -> None: ...

    @property
    def extensions(self) -> Extensions: ...

    @extensions.setter
    def extensions(self, arg: Extensions, /) -> None: ...

    class Type(enum.Enum):
        """Light type"""

        Undefined = 0

        Directional = 1

        Point = 2

        Spot = 3

        Ambient = 4

        Area = 5

class LightList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: LightList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Light], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Light]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Light: ...

    @overload
    def __getitem__(self, arg: slice, /) -> LightList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Light, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Light, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Light:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: LightList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Light, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: LightList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

class Material:
    def __init__(self) -> None: ...

    def __repr__(self) -> str: ...

    @property
    def name(self) -> str: ...

    @name.setter
    def name(self, arg: str, /) -> None: ...

    @property
    def base_color_value(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(4), order='C')]: ...

    @base_color_value.setter
    def base_color_value(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(4), order='C')], /) -> None: ...

    @property
    def base_color_texture(self) -> TextureInfo: ...

    @base_color_texture.setter
    def base_color_texture(self, arg: TextureInfo, /) -> None: ...

    @property
    def alpha_mode(self) -> Material.AlphaMode: ...

    @alpha_mode.setter
    def alpha_mode(self, arg: Material.AlphaMode, /) -> None: ...

    @property
    def alpha_cutoff(self) -> float: ...

    @alpha_cutoff.setter
    def alpha_cutoff(self, arg: float, /) -> None: ...

    @property
    def emissive_value(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')]: ...

    @emissive_value.setter
    def emissive_value(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')], /) -> None: ...

    @property
    def emissive_texture(self) -> TextureInfo: ...

    @emissive_texture.setter
    def emissive_texture(self, arg: TextureInfo, /) -> None: ...

    @property
    def metallic_value(self) -> float: ...

    @metallic_value.setter
    def metallic_value(self, arg: float, /) -> None: ...

    @property
    def roughness_value(self) -> float: ...

    @roughness_value.setter
    def roughness_value(self, arg: float, /) -> None: ...

    @property
    def metallic_roughness_texture(self) -> TextureInfo: ...

    @metallic_roughness_texture.setter
    def metallic_roughness_texture(self, arg: TextureInfo, /) -> None: ...

    @property
    def normal_texture(self) -> TextureInfo: ...

    @normal_texture.setter
    def normal_texture(self, arg: TextureInfo, /) -> None: ...

    @property
    def normal_scale(self) -> float: ...

    @normal_scale.setter
    def normal_scale(self, arg: float, /) -> None: ...

    @property
    def occlusion_texture(self) -> TextureInfo: ...

    @occlusion_texture.setter
    def occlusion_texture(self, arg: TextureInfo, /) -> None: ...

    @property
    def occlusion_strength(self) -> float: ...

    @occlusion_strength.setter
    def occlusion_strength(self, arg: float, /) -> None: ...

    @property
    def double_sided(self) -> bool: ...

    @double_sided.setter
    def double_sided(self, arg: bool, /) -> None: ...

    @property
    def extensions(self) -> Extensions: ...

    @extensions.setter
    def extensions(self, arg: Extensions, /) -> None: ...

    class AlphaMode(enum.Enum):
        """Alpha mode"""

        Opaque = 0

        Mask = 1

        Blend = 2

class MaterialList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: MaterialList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Material], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Material]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Material: ...

    @overload
    def __getitem__(self, arg: slice, /) -> MaterialList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Material, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Material, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Material:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: MaterialList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Material, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: MaterialList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

class MeshInstance3D:
    """A single mesh instance in a scene"""

    def __init__(self) -> None: ...

    @property
    def mesh_index(self) -> int: ...

    @mesh_index.setter
    def mesh_index(self, arg: int, /) -> None: ...

    @property
    def transform(self) -> Annotated[ArrayLike, dict(dtype='float64', order='C', device='cpu')]: ...

    @transform.setter
    def transform(self, arg: Annotated[ArrayLike, dict(dtype='float64', order='C', device='cpu')], /) -> None: ...

class Node:
    def __init__(self) -> None: ...

    def __repr__(self) -> str: ...

    @property
    def name(self) -> str: ...

    @name.setter
    def name(self, arg: str, /) -> None: ...

    @property
    def transform(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(4, 4), order='F')]:
        """The affine transform associated with this node"""

    @transform.setter
    def transform(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(4, 4), writable=False)], /) -> None: ...

    @property
    def parent(self) -> int | None:
        """Parent node index (None if no parent)"""

    @parent.setter
    def parent(self, arg: int, /) -> None: ...

    @property
    def children(self) -> ElementIdList: ...

    @children.setter
    def children(self, arg: ElementIdList, /) -> None: ...

    @property
    def meshes(self) -> SceneMeshInstanceList: ...

    @meshes.setter
    def meshes(self, arg: SceneMeshInstanceList, /) -> None: ...

    @property
    def cameras(self) -> ElementIdList: ...

    @cameras.setter
    def cameras(self, arg: ElementIdList, /) -> None: ...

    @property
    def lights(self) -> ElementIdList: ...

    @lights.setter
    def lights(self, arg: ElementIdList, /) -> None: ...

    @property
    def extensions(self) -> Extensions: ...

    @extensions.setter
    def extensions(self, arg: Extensions, /) -> None: ...

class NodeList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: NodeList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Node], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Node]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Node: ...

    @overload
    def __getitem__(self, arg: slice, /) -> NodeList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Node, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Node, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Node:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: NodeList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Node, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: NodeList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

class RemeshingOptions:
    def __init__(self) -> None: ...

    @property
    def facet_allocation_strategy(self) -> FacetAllocationStrategy: ...

    @facet_allocation_strategy.setter
    def facet_allocation_strategy(self, arg: FacetAllocationStrategy, /) -> None: ...

    @property
    def min_facets(self) -> int: ...

    @min_facets.setter
    def min_facets(self, arg: int, /) -> None: ...

class Scene:
    """A 3D scene"""

    def __init__(self) -> None: ...

    def __repr__(self) -> str: ...

    @property
    def name(self) -> str: ...

    @name.setter
    def name(self, arg: str, /) -> None: ...

    @property
    def nodes(self) -> NodeList: ...

    @nodes.setter
    def nodes(self, arg: NodeList, /) -> None: ...

    @property
    def root_nodes(self) -> ElementIdList: ...

    @root_nodes.setter
    def root_nodes(self, arg: ElementIdList, /) -> None: ...

    @property
    def meshes(self) -> SurfaceMeshList: ...

    @meshes.setter
    def meshes(self, arg: SurfaceMeshList, /) -> None: ...

    @property
    def images(self) -> ImageList: ...

    @images.setter
    def images(self, arg: ImageList, /) -> None: ...

    @property
    def textures(self) -> TextureList: ...

    @textures.setter
    def textures(self, arg: TextureList, /) -> None: ...

    @property
    def materials(self) -> MaterialList: ...

    @materials.setter
    def materials(self, arg: MaterialList, /) -> None: ...

    @property
    def lights(self) -> LightList: ...

    @lights.setter
    def lights(self, arg: LightList, /) -> None: ...

    @property
    def cameras(self) -> CameraList: ...

    @cameras.setter
    def cameras(self, arg: CameraList, /) -> None: ...

    @property
    def skeletons(self) -> SkeletonList: ...

    @skeletons.setter
    def skeletons(self, arg: SkeletonList, /) -> None: ...

    @property
    def animations(self) -> AnimationList: ...

    @animations.setter
    def animations(self, arg: AnimationList, /) -> None: ...

    @property
    def extensions(self) -> Extensions: ...

    @extensions.setter
    def extensions(self, arg: Extensions, /) -> None: ...

    def add(self, element: Node | lagrange.core.SurfaceMesh | Image | Texture | Material | Light | Camera | Skeleton | Animation) -> int:
        """
        Add an element to the scene.

        :param element: The element to add to the scene. E.g. node, mesh, image, texture, material, light, camera, skeleton, or animation.

        :returns: The id of the added element.
        """

    def add_child(self, parent_id: int, child_id: int) -> None:
        """
        Add a child node to a parent node.

        :param parent_id: The parent node id.
        :param child_id: The child node id.

        :returns: The id of the added child node.
        """

class SceneMeshInstance:
    """Mesh and material index of a node"""

    def __init__(self) -> None: ...

    def __repr__(self) -> str: ...

    @property
    def mesh(self) -> int | None:
        """Mesh index in the scene.meshes vector (None if invalid)"""

    @mesh.setter
    def mesh(self, arg: int, /) -> None: ...

    @property
    def materials(self) -> ElementIdList: ...

    @materials.setter
    def materials(self, arg: ElementIdList, /) -> None: ...

class SceneMeshInstanceList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: SceneMeshInstanceList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[SceneMeshInstance], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[SceneMeshInstance]: ...

    @overload
    def __getitem__(self, arg: int, /) -> SceneMeshInstance: ...

    @overload
    def __getitem__(self, arg: slice, /) -> SceneMeshInstanceList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: SceneMeshInstance, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: SceneMeshInstance, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> SceneMeshInstance:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: SceneMeshInstanceList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: SceneMeshInstance, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: SceneMeshInstanceList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

class SimpleScene3D:
    """Simple scene container for instanced meshes"""

    def __init__(self) -> None: ...

    @property
    def num_meshes(self) -> int:
        """Number of meshes in the scene"""

    def num_instances(self, mesh_index: int) -> int: ...

    @property
    def total_num_instances(self) -> int:
        """Total number of instances for all meshes in the scene"""

    def get_mesh(self, mesh_index: int) -> lagrange.core.SurfaceMesh: ...

    def ref_mesh(self, mesh_index: int) -> lagrange.core.SurfaceMesh: ...

    def get_instance(self, mesh_index: int, instance_index: int) -> MeshInstance3D: ...

    def reserve_meshes(self, num_meshes: int) -> None: ...

    def add_mesh(self, mesh: lagrange.core.SurfaceMesh) -> int: ...

    def reserve_instances(self, mesh_index: int, num_instances: int) -> None: ...

    def add_instance(self, instance: MeshInstance3D) -> int: ...

class Skeleton:
    def __init__(self) -> None: ...

    def __repr__(self) -> str: ...

    @property
    def meshes(self) -> ElementIdList: ...

    @meshes.setter
    def meshes(self, arg: ElementIdList, /) -> None: ...

    @property
    def extensions(self) -> Extensions: ...

    @extensions.setter
    def extensions(self, arg: Extensions, /) -> None: ...

class SkeletonList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: SkeletonList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Skeleton], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Skeleton]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Skeleton: ...

    @overload
    def __getitem__(self, arg: slice, /) -> SkeletonList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Skeleton, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Skeleton, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Skeleton:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: SkeletonList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Skeleton, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: SkeletonList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

class SurfaceMeshList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: SurfaceMeshList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[lagrange.core.SurfaceMesh], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[lagrange.core.SurfaceMesh]: ...

    @overload
    def __getitem__(self, arg: int, /) -> lagrange.core.SurfaceMesh: ...

    @overload
    def __getitem__(self, arg: slice, /) -> SurfaceMeshList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: lagrange.core.SurfaceMesh, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: lagrange.core.SurfaceMesh, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> lagrange.core.SurfaceMesh:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: SurfaceMeshList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: lagrange.core.SurfaceMesh, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: SurfaceMeshList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

class Texture:
    """Texture"""

    def __init__(self) -> None: ...

    def __repr__(self) -> str: ...

    @property
    def name(self) -> str: ...

    @name.setter
    def name(self, arg: str, /) -> None: ...

    @property
    def image(self) -> int | None:
        """Texture image index in scene.images vector (None if invalid)"""

    @image.setter
    def image(self, arg: int, /) -> None: ...

    @property
    def mag_filter(self) -> Texture.TextureFilter: ...

    @mag_filter.setter
    def mag_filter(self, arg: Texture.TextureFilter, /) -> None: ...

    @property
    def min_filter(self) -> Texture.TextureFilter: ...

    @min_filter.setter
    def min_filter(self, arg: Texture.TextureFilter, /) -> None: ...

    @property
    def wrap_u(self) -> Texture.WrapMode: ...

    @wrap_u.setter
    def wrap_u(self, arg: Texture.WrapMode, /) -> None: ...

    @property
    def wrap_v(self) -> Texture.WrapMode: ...

    @wrap_v.setter
    def wrap_v(self, arg: Texture.WrapMode, /) -> None: ...

    @property
    def scale(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(2), order='C')]: ...

    @scale.setter
    def scale(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(2), order='C')], /) -> None: ...

    @property
    def offset(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(2), order='C')]: ...

    @offset.setter
    def offset(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(2), order='C')], /) -> None: ...

    @property
    def rotation(self) -> float: ...

    @rotation.setter
    def rotation(self, arg: float, /) -> None: ...

    @property
    def extensions(self) -> Extensions: ...

    @extensions.setter
    def extensions(self, arg: Extensions, /) -> None: ...

    class WrapMode(enum.Enum):
        """Texture wrap mode"""

        Wrap = 0

        Clamp = 1

        Decal = 2

        Mirror = 3

    class TextureFilter(enum.Enum):
        """Texture filter mode"""

        Undefined = 0

        Nearest = 9728

        Linear = 9729

        NearestMipmapNearest = 9984

        LinearMipmapNearest = 9985

        NearestMipmapLinear = 9986

        LinearMipmapLinear = 9987

class TextureInfo:
    def __init__(self) -> None: ...

    def __repr__(self) -> str: ...

    @property
    def index(self) -> int | None:
        """Texture index in scene.textures vector. `None` if not set."""

    @index.setter
    def index(self, arg: int, /) -> None: ...

    @property
    def texcoord(self) -> int: ...

    @texcoord.setter
    def texcoord(self, arg: int, /) -> None: ...

class TextureList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: TextureList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Texture], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Texture]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Texture: ...

    @overload
    def __getitem__(self, arg: slice, /) -> TextureList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Texture, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Texture, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Texture:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: TextureList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Texture, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: TextureList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

class ValueList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: ValueList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Value], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Value]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Value: ...

    @overload
    def __getitem__(self, arg: slice, /) -> ValueList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Value, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Value, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Value:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: ValueList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Value, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: ValueList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

class ValueMap:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: ValueMap) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: dict[str, Value], /) -> None:
        """Construct from a dictionary"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the map is nonempty"""

    def __repr__(self) -> str: ...

    @overload
    def __contains__(self, arg: str, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def __iter__(self) -> Iterator[str]: ...

    def __getitem__(self, arg: str, /) -> Value: ...

    def __delitem__(self, arg: str, /) -> None: ...

    def clear(self) -> None:
        """Remove all items"""

    def __setitem__(self, arg0: str, arg1: Value, /) -> None: ...

    def update(self, arg: ValueMap, /) -> None:
        """Update the map with element from `arg`"""

    class ItemView:
        def __len__(self) -> int: ...

        def __iter__(self) -> Iterator[tuple[str, Value]]: ...

    class KeyView:
        @overload
        def __contains__(self, arg: str, /) -> bool: ...

        @overload
        def __contains__(self, arg: object, /) -> bool: ...

        def __len__(self) -> int: ...

        def __iter__(self) -> Iterator[str]: ...

    class ValueView:
        def __len__(self) -> int: ...

        def __iter__(self) -> Iterator[Value]: ...

    def keys(self) -> ValueMap.KeyView:
        """Returns an iterable view of the map's keys."""

    def values(self) -> ValueMap.ValueView:
        """Returns an iterable view of the map's values."""

    def items(self) -> ValueMap.ItemView:
        """Returns an iterable view of the map's items."""

class ValueUnorderedMap:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: ValueUnorderedMap) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: dict[str, Value], /) -> None:
        """Construct from a dictionary"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the map is nonempty"""

    def __repr__(self) -> str: ...

    @overload
    def __contains__(self, arg: str, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def __iter__(self) -> Iterator[str]: ...

    def __getitem__(self, arg: str, /) -> Value: ...

    def __delitem__(self, arg: str, /) -> None: ...

    def clear(self) -> None:
        """Remove all items"""

    def __setitem__(self, arg0: str, arg1: Value, /) -> None: ...

    def update(self, arg: ValueUnorderedMap, /) -> None:
        """Update the map with element from `arg`"""

    class ItemView:
        def __len__(self) -> int: ...

        def __iter__(self) -> Iterator[tuple[str, Value]]: ...

    class KeyView:
        @overload
        def __contains__(self, arg: str, /) -> bool: ...

        @overload
        def __contains__(self, arg: object, /) -> bool: ...

        def __len__(self) -> int: ...

        def __iter__(self) -> Iterator[str]: ...

    class ValueView:
        def __len__(self) -> int: ...

        def __iter__(self) -> Iterator[Value]: ...

    def keys(self) -> ValueUnorderedMap.KeyView:
        """Returns an iterable view of the map's keys."""

    def values(self) -> ValueUnorderedMap.ValueView:
        """Returns an iterable view of the map's values."""

    def items(self) -> ValueUnorderedMap.ItemView:
        """Returns an iterable view of the map's items."""

def compute_global_node_transform(scene: Scene, node_idx: int) -> Annotated[ArrayLike, dict(dtype='float32', shape=(4, 4), order='F')]:
    """
    Compute the global transform associated with a node.

    :param scene: The input node.
    :param node_idx: The index of the target node.

    :returns: The global transform of the target node, which is the combination of transforms from this node all the way to the root.
    """

def mesh_to_simple_scene(mesh: lagrange.core.SurfaceMesh) -> SimpleScene3D:
    """
    Converts a single mesh into a simple scene with a single identity instance of the input mesh.

    :param mesh: Input mesh to convert.

    :return: Simple scene containing the input mesh.
    """

def meshes_to_simple_scene(meshes: SurfaceMeshList) -> SimpleScene3D:
    """
    Converts a list of meshes into a simple scene with a single identity instance of each input mesh.

    :param meshes: Input meshes to convert.

    :return: Simple scene containing the input meshes.
    """

def simple_scene_to_mesh(scene: SimpleScene3D, normalize_normals: bool = True, normalize_tangents_bitangents: bool = True, preserve_attributes: bool = True) -> lagrange.core.SurfaceMesh:
    """
    Converts a scene into a concatenated mesh with all the transforms applied.

    :param scene: Scene to convert.
    :param normalize_normals: If enabled, normals are normalized after transformation.
    :param normalize_tangents_bitangents: If enabled, tangents and bitangents are normalized after transformation.
    :param preserve_attributes: Preserve shared attributes and map them to the output mesh.

    :return: Concatenated mesh.
    """
