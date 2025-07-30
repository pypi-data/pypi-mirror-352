from __future__ import annotations
from collections.abc import Iterable
from typing import List, Optional, Tuple, Union
import warnings

import numpy as np
import larp.fn as lpf
from larp.types import Scaler, RGJDict, FieldSize, Point, RGeoJSONCollection, RGeoJSONObject, RepulsionVectorsAndRef

"""
Author: Josue N Rivera

x are assumed to be a list of point coordinates in euclidean space

"""

class RGJGeometry():

    RGJType = None

    def __init__(self, coordinates:Union[np.ndarray, List[Point], List[List[Point]], Point], repulsion:Optional[np.ndarray] = None, properties:Optional[dict] = None, optional_dim = 2, **kwargs) -> None:
        self.coordinates = np.array(coordinates)
        self.repulsion = np.eye(optional_dim) if repulsion is None else np.array(repulsion)
        self.inv_repulsion = np.linalg.inv(self.repulsion)
        self.eye_repulsion = np.eye(len(self.repulsion))
        self.properties = {} if properties is None else properties
        self.grad_matrix = self.inv_repulsion + self.inv_repulsion.T
        
        bbox = self.coordinates.reshape(-1, 2)
        self.bbox = np.array([bbox.min(0), bbox.max(0)])

    def set_coordinates(self, new_coords):
        self.coordinates = np.array(new_coords)
        bbox = self.coordinates.reshape(-1, 2)
        self.bbox = np.array([bbox.min(0), bbox.max(0)])

    def set_repulsion(self, new_repulsion):
        self.repulsion = np.array(new_repulsion)
        self.inv_repulsion = np.linalg.inv(self.repulsion)
        self.eye_repulsion = np.eye(len(self.repulsion))
        self.grad_matrix = self.inv_repulsion + self.inv_repulsion.T

    def get_dist_matrix(self, scaled=True, inverted=True):

        if inverted and scaled:
            return self.inv_repulsion
        if not scaled:
            return self.eye_repulsion
        
        return self.repulsion

    def get_center_point(self) -> np.ndarray:
        if len(self.coordinates.shape) <= 1:
            return self.coordinates
        
        coords = np.reshape(self.coordinates, (-1, 2))

        return (coords.min(0) + coords.max(0))/2.0
    
    def in_bbox(self, x:Point) -> bool:

        bboxes = self.bbox.reshape((-1, 2))
        for i in range(0, len(bboxes), 2):
            if all(x >= bboxes[i]) and all(x <= bboxes[i+1]):
                return True

        return False

    def squared_dist(self, x: np.ndarray, scaled=True, inverted=True, **kwargs) -> np.ndarray:
        nvector = self.repulsion_vector(x, min_dist_select = True)
        matrix = self.get_dist_matrix(scaled=scaled, inverted=inverted)

        return ((nvector@matrix)*nvector).sum(axis=1)
    
    def repulsion_vector(self, x:np.ndarray, **kwargs) -> np.ndarray:
        raise NotImplementedError
    
    def gradient(self, x:np.ndarray, **kwargs):
        repulsion_vector = self.repulsion_vector(x, **kwargs)
        return - self.eval(x=x).reshape(-1, 1) * (repulsion_vector@self.grad_matrix.T)

    def eval(self, x:np.ndarray):
        return np.exp(-self.squared_dist(x))
    
    def toRGeoJSON(self) -> RGeoJSONObject:
        if self.RGJType is None: 
            return UserWarning(f"Object doesn't have a RGJType")
        
        return {
            "type": "Feature",
            "properties": self.properties,
            "geometry": {
                "type": self.RGJType,
                "coordinates": self.coordinates.tolist() if isinstance(self.coordinates, np.ndarray) else self.coordinates,
                "repulsion": self.repulsion.tolist()
            }
        }
    
    def __repr__(self):
        """
        Returns a more concise and unambiguous string representation of the object,
        typically used in debugging.
        """
        return str(self.toRGeoJSON())

    def __str__(self):
        """
        Returns a user-friendly string representation of the object,
        using its RGeoJSON representation.
        """

        def ndnumpy_to_str(array):
            string = f"{array.tolist()}"

            if len(string) > 50:
                string = string[:25] + "..." + string[-25:]

            return string

        return f"{self.__class__.__name__}(coordinates={ndnumpy_to_str(self.coordinates)} repulsion={ndnumpy_to_str(self.repulsion)})"


class PointRGJ(RGJGeometry):
    RGJType = "Point"

    def __init__(self, coordinates: Union[np.ndarray, Point], repulsion:Optional[np.ndarray] = None, **kwargs) -> None:
        super().__init__(coordinates=coordinates, repulsion=repulsion, **kwargs)

    def repulsion_vector(self, x: np.ndarray, **kwargs) -> np.ndarray:
        return x - self.coordinates

class LineStringRGJ(RGJGeometry):
    RGJType = "LineString"

    def __init__(self, coordinates: np.ndarray, repulsion:Optional[np.ndarray] = None, **kwargs) -> None:
        super().__init__(coordinates=coordinates, repulsion=repulsion, **kwargs)
        self.lines_n = len(self.coordinates) - 1
        self.points_in_line_pair = np.stack([self.coordinates[:-1], self.coordinates[1:]], axis=1)

    def set_coordinates(self, new_coords):
        super().set_coordinates(new_coords)
        self.lines_n = len(self.coordinates) - 1
        self.points_in_line_pair = np.stack([self.coordinates[:-1], self.coordinates[1:]], axis=1)
    
    def __repulsion_vector_one_line__(self, args) -> np.ndarray:
        x, line = args
        x2_d_x1 = line[1:2] - line[0:1]
        x_d_x1 = x - line[0:1]

        x12dotxx1 = (x2_d_x1*x_d_x1).sum(1, keepdims=True)
        x12dotx12 = (x2_d_x1*x2_d_x1).sum(1, keepdims=True)

        g = line[0] + np.clip(x12dotxx1/x12dotx12, 0.0, 1.0)*(x2_d_x1)
        return x - g
    
    def repulsion_vector(self, x: np.ndarray, min_dist_select:bool = True, **kwargs) -> np.ndarray:
        vectors:np.ndarray = [self.__repulsion_vector_one_line__((x, line)) for line in self.points_in_line_pair]

        vectors = np.stack(vectors, axis=0)
        if min_dist_select:
            vectors = vectors.swapaxes(0, 1)
            matrix = self.get_dist_matrix(scaled=True, inverted=True)
            nvectors = np.matmul(vectors, matrix)
            dist = (vectors*nvectors).sum(-1)
            select = dist.argmin(1)
            vectors = vectors[np.arange(len(select)), select]
        
        return vectors
    
class RectangleRGJ(RGJGeometry):
    RGJType = "Rectangle"

    def __init__(self, coordinates: np.ndarray, repulsion:Optional[np.ndarray] = None, **kwargs) -> None:
        super().__init__(coordinates=coordinates, repulsion=repulsion, **kwargs)
        self.x1_abs_x2 = np.abs(self.coordinates[0] - self.coordinates[1])

    def set_coordinates(self, new_coords):
        super().set_coordinates(new_coords)
        self.x1_abs_x2 = np.abs(self.coordinates[0] - self.coordinates[1])

    def repulsion_vector(self, x: np.ndarray, **kwargs) -> np.ndarray:
        
        return 0.5*np.sign(x-self.coordinates[0])*(np.abs(x-self.coordinates[0]) + np.abs(x-self.coordinates[1]) - self.x1_abs_x2)
    
class EllipseRGJ(RGJGeometry):
    RGJType = "Ellipse"
    DEN_ERROR_BUFFER = 1e-6

    def __init__(self, coordinates: np.ndarray, shape: np.ndarray, repulsion:Optional[np.ndarray] = None, **kwargs) -> None:

        super().__init__(coordinates=coordinates, repulsion=repulsion, **kwargs)
        self.shape = shape
        self.inv_shape = np.linalg.inv(self.shape)

        eval, evec  = np.linalg.eig(self.shape)
        vectors = evec * np.sqrt(eval) @ np.linalg.inv(evec)
        bounds = np.concatenate([self.coordinates + vectors, self.coordinates - vectors])
        self.bbox = np.array([bounds.min(0), bounds.max(0)])

    def set_coordinates(self, new_coords):
        super().set_coordinates(new_coords)

        eval, evec  = np.linalg.eig(self.shape)
        vectors = evec * np.sqrt(eval) @ np.linalg.inv(evec)
        bounds = np.concatenate([self.coordinates + vectors, self.coordinates - vectors])
        self.bbox = np.array([bounds.min(0), bounds.max(0)])

    def set_shape(self, new_shape):
        self.shape = new_shape
        self.inv_shape = np.linalg.inv(self.shape)

    def repulsion_vector(self, x: np.ndarray, **kwargs) -> np.ndarray:

        x_d_xh = x - self.coordinates
        Binvx = x_d_xh@self.inv_shape.T

        den = np.sqrt((Binvx*Binvx).sum(1, keepdims=True))
        den = np.maximum(den, self.DEN_ERROR_BUFFER)

        return np.maximum(1 - 1/den, 0)*x_d_xh
    
    def toRGeoJSON(self) -> RGeoJSONObject:
        out = super().toRGeoJSON()
        out["geometry"]['shape'] = self.shape.tolist() # type: ignore
        return out

class MultiPointRGJ(RGJGeometry):
    RGJType = "MultiPoint"

    def __init__(self, coordinates: np.ndarray, repulsion:Optional[np.ndarray] = None, **kwargs) -> None:
        super().__init__(coordinates=coordinates, repulsion=repulsion)
        self.bbox = self.coordinates.copy()

    def in_bbox(self, x:Point) -> bool:
        return any(self.bbox == x)

    def repulsion_vector(self, x: np.ndarray, min_dist_select:bool = True, **kwargs) -> np.ndarray:
        x = np.array(x)

        n = x.shape[0]
        m = self.coordinates.shape[0]

        x = np.tile(x, (m, 1, 1)).transpose(1, 0, 2)
        y = np.tile(self.coordinates, (n, 1, 1))
        diff = y - x

        if min_dist_select:
            matrix = self.get_dist_matrix(scaled=True, inverted=True)
            Adiff = np.matmul(diff, matrix)
            dist = (Adiff*diff).sum(-1)
            select = dist.argmin(1)
            diff = diff[np.arange(len(select)), select]
        else:
            diff = diff.swapaxes(0, 1)

        return diff
    
class MultiLineStringRGJ(LineStringRGJ):
    RGJType = "MultiLineString"

    def __init__(self, coordinates: np.ndarray, repulsion:Optional[np.ndarray] = None, properties:Optional[dict] = None, optional_dim = 2, **kwargs) -> None:

        self.coordinates = [np.array(coords) for coords in coordinates]
        self.repulsion = np.eye(optional_dim) if repulsion is None else np.array(repulsion)
        self.inv_repulsion = np.linalg.inv(self.repulsion)
        self.eye_repulsion = np.eye(len(self.repulsion))
        self.properties = {} if properties is None else properties
        self.grad_matrix = self.inv_repulsion + self.inv_repulsion.T
        
        self.lines_n = sum([len(coords)-1 for coords in self.coordinates])
        self.points_in_line_pair = np.concatenate([[coords[:-1], coords[1:]] for coords in self.coordinates], axis=1).swapaxes(0, 1)

        self.bbox = np.concatenate([np.array([coords.min(0), coords.max(0)]) for coords in self.coordinates])

    def set_coordinates(self, new_coords):
        self.coordinates = [np.array(coords) for coords in new_coords]
        self.lines_n = sum([len(coords)-1 for coords in self.coordinates])
        self.points_in_line_pair = np.concatenate([[coords[:-1], coords[1:]] for coords in self.coordinates], axis=1).swapaxes(0, 1)
        self.bbox = np.concatenate([np.array([coords.min(0), coords.max(0)]) for coords in self.coordinates])

    def get_center_point(self) -> np.ndarray:

        coords = np.concatenate([coords.reshape((-1, 2)) for coords in self.coordinates], axis=0)
        return (coords.min(0) + coords.max(0))/2.0

class MultiRectangleRGJ(RGJGeometry):

    RGJType = "MultiRectangle"

    def __init__(self, coordinates: np.ndarray, repulsion:Optional[np.ndarray] = None, **kwargs) -> None:
        super().__init__(coordinates=coordinates, repulsion=repulsion, **kwargs)
        self.rect_n = len(self.coordinates)
        self.bbox = np.array([np.array([coords.min(0), coords.max(0)]) for coords in self.coordinates])
        
    def set_coordinates(self, new_coords):
        super().set_coordinates(new_coords)
        self.rect_n = len(self.coordinates)
    
    def __repulsion_vector_one_rect__(self, args) -> np.ndarray:
        x, rect = args
        return 0.5*np.sign(x-rect[0])*(np.abs(x-rect[0]) + np.abs(x-rect[1]) - np.abs(rect[0] - rect[1]))
    
    def repulsion_vector(self, x: np.ndarray, min_dist_select:bool = True, **kwargs) -> np.ndarray:
        vectors:np.ndarray = [self.__repulsion_vector_one_rect__((x, rect)) for rect in self.coordinates]

        vectors = np.stack(vectors, axis=0)
        if min_dist_select:
            vectors = vectors.swapaxes(0, 1)
            matrix = self.get_dist_matrix(scaled=True, inverted=True)
            nvectors = np.matmul(vectors, matrix)
            dist = (vectors*nvectors).sum(-1)
            select = dist.argmin(1)
            vectors = vectors[np.arange(len(select)), select]
        
        return vectors

class MultiEllipseRGJ(RGJGeometry):
    RGJType = "MultiEllipse"
    DEN_ERROR_BUFFER = 1e-6

    def __init__(self, coordinates: np.ndarray, shape: np.ndarray, repulsion:Optional[np.ndarray] = None, **kwargs) -> None:
        super().__init__(coordinates=coordinates, repulsion=repulsion, **kwargs)
        self.shape = shape
        self.inv_shape = np.linalg.inv(self.shape)
        self.parameters = list(zip(self.coordinates, self.inv_shape))
        self.ellipse_n = len(self.coordinates)

        self.bbox = []

        for sp in self.shape:
            eval, evec  = np.linalg.eig(sp)
            vectors = evec * np.sqrt(eval) @ np.linalg.inv(evec)
            bounds = np.concatenate([self.coordinates + vectors, self.coordinates - vectors])
            self.bbox.append(np.array([bounds.min(0), bounds.max(0)]))

        self.bbox = np.array(self.bbox)

    def set_coordinates(self, new_coords):
        super().set_coordinates(new_coords)
        self.parameters = list(zip(self.coordinates, self.inv_shape))
        self.ellipse_n = len(self.coordinates)

        self.bbox = []
        for sp in self.shape:
            eval, evec  = np.linalg.eig(sp)
            vectors = evec * np.sqrt(eval) @ np.linalg.inv(evec)
            bounds = np.concatenate([self.coordinates + vectors, self.coordinates - vectors])
            self.bbox.append(np.array([bounds.min(0), bounds.max(0)]))

        self.bbox = np.array(self.bbox)

    def set_shape(self, new_shape):
        self.shape = new_shape
        self.inv_shape = np.linalg.inv(self.shape)
        self.parameters = list(zip(self.coordinates, self.inv_shape))
    
    def __repulsion_vector_one_ellipse__(self, args) -> np.ndarray:
        x, coordinate, inv_shape = args
        x_d_xh = x - coordinate
        Binvx = x_d_xh@inv_shape.T

        den = np.sqrt((Binvx*Binvx).sum(1, keepdims=True))
        den = np.maximum(den, self.DEN_ERROR_BUFFER)
        return np.maximum(1 - 1/den, 0)*x_d_xh
    
    def repulsion_vector(self, x: np.ndarray, min_dist_select:bool = True, **kwargs) -> np.ndarray:
        vectors:np.ndarray = [self.__repulsion_vector_one_ellipse__((x, parameters[0], parameters[1])) for parameters in self.parameters]

        vectors = np.stack(vectors, axis=0)
        if min_dist_select:
            vectors = vectors.swapaxes(0, 1)
            matrix = self.get_dist_matrix(scaled=True, inverted=True)
            nvectors = np.matmul(vectors, matrix) # Check: np.einsum('jk,ik->ij', matrix, vectors)
            dist = (vectors*nvectors).sum(-1)
            select = dist.argmin(1)
            vectors = vectors[np.arange(len(select)), select]
        
        return vectors
    
class GeometryCollectionRGJ(RGJGeometry):
    RGJType = "GeometryCollection"

    def __init__(self, geometries: List[RGJDict], properties:Optional[dict] = None, **kwargs) -> None:
        
        self.properties = {} if properties is None else properties
        self.rgjs:List[RGJGeometry] = [globals()[rgj_dict["type"]+"RGJ"](**rgj_dict) for rgj_dict in geometries]
        self.rgjs_n = len(self.rgjs)

        self.inv_repulsions = self.get_dist_matrix(scaled=True, inverted=True)
        self.grad_matrixes = np.array([rgj.grad_matrix for rgj in self.rgjs])

        bbox = np.concatenate([rgj.bbox for rgj in self.rgjs], 0).reshape(-1, 2)
        self.bbox = np.array([bbox.min(0), bbox.max(0)])

    def set_coordinates(self, new_coords):
        raise NotImplementedError

    def set_repulsion(self, new_repulsion):
        for rgj in self.rgjs:
            rgj.set_repulsion(new_repulsion)

    def in_bbox(self, x:Point) -> bool:
        return any([rgj.in_bbox(x) for rgj in self.rgjs])

    def get_dist_matrix(self, scaled=True, inverted=True) -> List[np.ndarray]:

        """
        Returns all distance matrix for all sub units
        """

        return np.array([rgj.get_dist_matrix(scaled=scaled, inverted=inverted) for rgj in self.rgjs])

    def get_center_point(self) -> np.ndarray:
        coords = np.reshape(np.array([rgj.get_center_point() for rgj in self.rgjs]), (-1, 2))
        return (coords.min(0) + coords.max(0))/2.0
    
    def squared_dist(self, x: np.ndarray, scaled=True, inverted=True, return_reference=False, **kwargs) -> np.ndarray:

        dists = np.stack([rgj.squared_dist(x, scaled=scaled, inverted=inverted) for rgj in self.rgjs], axis=1)

        if return_reference:
            min_idxs = np.argmin(dists, axis=1)
            return dists[np.arange(len(dists)), min_idxs], min_idxs

        return np.min(dists, axis=1)
    
    def repulsion_vector(self, x:np.ndarray, min_dist_select:bool = True, **kwargs) -> np.ndarray:

        vectors:np.ndarray = [rgj.repulsion_vector(x, min_dist_select=min_dist_select, **kwargs).reshape(-1, 2) for rgj in self.rgjs]

        vectors = np.stack(vectors, axis=0)

        if min_dist_select:
            vectors = vectors.swapaxes(0, 1)
            nvectors = np.einsum('ijk,lik->lij', self.inv_repulsions, vectors)
            dist = (vectors*nvectors).sum(-1)
            select = dist.argmin(1)
            vectors = vectors[np.arange(len(select)), select]

        return vectors
    
    def gradient(self, x: np.ndarray, **kwargs):

        _, dist_idxs = self.squared_dist(x, return_reference=True, **kwargs)

        repulsion_vector = self.repulsion_vector(x, min_dist_select = True, **kwargs)
        return - self.eval(x=x).reshape(-1, 1) * (np.einsum('ijk,ik->ij', self.grad_matrixes[dist_idxs], repulsion_vector))
    
    def toRGeoJSON(self) -> RGeoJSONObject:
        if self.RGJType is None: 
            return UserWarning(f"Object doesn't have a RGJType")
        
        return {
            "type": "Feature",
            "properties": self.properties,
            "geometry": {
                "type": self.RGJType,
                "geometries": [rgj.toRGeoJSON()["geometry"] for rgj in self.rgjs]
            }
        }
    
class PotentialField():
    
    """
    Represents a potential field composed of a subset of RGJ objects.

    This class allows the storage and spatial organization of RGJ geometries, and provides tools
    for bounding box management and automatic sizing/centering of the potential field based on input RGJs.

    Attributes:
        rgjs (List[RGJGeometry]): List of RGJ geometries in the field.
        center_point (Point or None): Central reference point of the potential field. Can be auto-calculated.
        size (np.ndarray or None): Spatial extent of the field (width, height). Can be inferred.
        extra_info (dict): Optional metadata or user-defined information.
        bbox (np.ndarray): Bounding box of all RGJs in the field. Shape (2, 2) -> [[xmin, ymin], [xmax, ymax]].

    Args:
        rgjs (Optional[List[RGJDict] or RGJGeometry]): List of RGJ objects or single RGJ geometry. Can be None.
        center_point (Optional[Point]): Optional center point for the field. If not provided, auto-calculated.
        size (Optional[FieldSize or float]): Width/height or 2D size of the field. If None, inferred from RGJs.
        properties (Optional[List[dict]]): List of metadata dictionaries for each RGJ (used when RGJs are dicts).
        extra_info (dict): Arbitrary extra user-defined metadata associated with the field.

    """

    def __init__(self, rgjs:Optional[Union[List[RGJDict], RGJGeometry]] = None, center_point: Optional[Point] = None, size:Optional[Union[FieldSize, float]] = None, properties:Optional[List[dict]] = None, extra_info={}):
        self.rgjs:List[RGJGeometry] = []
        self.__reload_center = None
        self.center_point = center_point
        self.extra_info = extra_info
        self.bbox = np.array([[None, None], [None, None]])

        if size is None:
            self.size = size
        elif np.isscalar(size):
            self.size = np.array([size, size])
        else:
            self.size = np.atleast_1d(size)

        if properties is None or isinstance(rgjs[0], RGJGeometry):
            for rgj in rgjs:
                self.addRGJ(rgj=rgj, reload_bbox=False)
        else:
            for rgj, proper in zip(rgjs, properties):
                self.addRGJ(rgj=rgj, properties=proper, reload_bbox=False)
        
        self.reload_bbox()

        if self.center_point is None:
            self.__reload_center = True # whether to recalculate center point if new RGJ are added
            if len(rgjs) > 0:
                self.center_point, suggest_size = self.__calculate_center_point__(suggest_size=True)
                self.size = np.array([max(suggest_size)]*2, dtype=float) if self.size is None else self.size
        else:
            self.__reload_center = False
            if len(rgjs) > 0:
                suggest_size = np.array([max(np.abs(self.bbox - self.center_point).reshape(-1))*2]*2)

                self.size = suggest_size if self.size is None else self.size

    def __getitem__(self, idxs: Union[int, np.integer, Iterable[int]]):
        """
        Access RGJ(s) in the field by index or list of indices.

        Args:
            idxs (int, np.integer, or Iterable[int]): Index or iterable of indices into the RGJ list.

        Returns:
            RGJGeometry or List[RGJGeometry] or None: The selected RGJ(s), or None if invalid input.
        """

        if isinstance(idxs, (int, np.integer)):
            return self.rgjs[int(idxs)]

        elif isinstance(idxs, Iterable) and not isinstance(idxs, (str, bytes)):
            return [self.rgjs[int(i)] for i in idxs]

        warnings.warn(f"Object of type {type(idxs)} not supported")
        return None

    def __iter__(self):
        self.rgj_idx = 0
        return self
    
    def __next__(self):
        if self.rgj_idx >= len(self):
            raise StopIteration
        out = self.rgjs[self.rgj_idx]
        self.rgj_idx += 1
        return out

    def __len__(self)->int:
        return len(self.rgjs)

    def __calculate_center_point__(self, suggest_size = False) -> Union[Point, Tuple[Point, float]]:
        center = np.sum(self.bbox, 0)/2.0

        if suggest_size:
            suggest_size = self.bbox[1] - self.bbox[0]
            return center, suggest_size
        
        return center
    
    def set_bbox(self, x_min:float, y_min:float, x_max:float, y_max:float):
        
        self.bbox = np.array([[x_min, y_min], [x_max, y_max]])
        self.center_point = np.sum(self.bbox, 0)/2.0
        self.size = self.bbox[1] - self.bbox[0]

    def set_all_repulsion(self, new_repulsion):
        new_repulsion = np.array(new_repulsion)
        for rgj in self.rgjs:
            rgj.set_repulsion(new_repulsion)

    def reload_bbox(self):
        if len(self):
            bbox = np.concatenate([rgj.bbox.reshape(-1, 2) for rgj in self.rgjs], 0)
            self.bbox = np.array([bbox.min(0), bbox.max(0)])
        else:
            self.bbox = np.array([[None, None], [None, None]])

        return self.bbox
    
    def reload_center_point(self, toggle=True, recal_size=False) -> Point:
        self.__reload_center = toggle
        if toggle and len(self.rgjs) > 0:
            if recal_size:
                self.center_point, suggest_size = self.__calculate_center_point__(True)
                self.size = np.array([max(suggest_size)]*2, dtype=float)
            else:
                self.center_point = self.__calculate_center_point__(False)

        return self.center_point

    def addRGJ(self, rgj:Union[RGJDict, RGJGeometry], properties:Optional[dict] = None, reload_bbox = True, **kward) -> None:

        if not isinstance(rgj, RGJGeometry):
            if not isinstance(rgj, dict) or "type" not in rgj:
                raise ValueError("RGJ must be an RGJGeometry.")
            
            cls = globals().get(rgj["type"] + "RGJ")
            if cls is None:
                raise ValueError(f"No RGJ class found for type {rgj['type']}")
            
            rgj = cls(properties=properties, **rgj, **kward)
        
        self.rgjs.append(rgj)

        if reload_bbox:
            self.reload_bbox()

        if self.__reload_center:
            self.center_point = self.__calculate_center_point__()

    def addField(self, new_field:PotentialField, reload_bbox = True):

        """
        Adds all RGJs from another potential field to this field.

        Args:
            new_field (PotentialField): A potential field containing RGJs to add.
            reload_bbox (bool, optional): Whether to recompute the bounding box after addition.
                                        Defaults to True.
        """
        og_reload_center = self.__reload_center
        self.__reload_center = False
        
        # Add rgj to field
        try:
            for rgj in new_field:
                self.addRGJ(rgj=rgj, reload_bbox=False)
        finally:
            self.__reload_center = og_reload_center

        if reload_bbox:
            self.reload_bbox()

        if self.__reload_center:
            self.center_point = self.__calculate_center_point__()

    def delRGJ(self, idxs: Union[int, List[int], np.ndarray], reload_bbox: bool = True) -> None:
        """
        Removes one or more RGJs from the field by their indices.

        Args:
            idxs (Union[int, List[int], np.ndarray]): A single index, list of indices, or 1D numpy array of indices to remove.
            reload_bbox (bool, optional): Whether to recompute the bounding box after deletion. Defaults to True.
        """
        # Normalize input and wrap indices within range
        idxs = np.atleast_1d(idxs).astype(int)
        idxs = np.unique(idxs % len(self))[::-1]  # Wrap, deduplicate, and reverse sort

        # Delete RGJs from highest to lowest index to avoid reindexing errors
        for idx in idxs:
            del self.rgjs[idx]

        # Optionally recalculate the center point if enabled
        if self.__reload_center:
            self.center_point = self.__calculate_center_point__()

        # Optionally recompute the bounding box
        if reload_bbox:
            self.reload_bbox()
   
    def in_bbox(self, point: Point, filted_idx: Optional[List[int]] = None) -> bool:
        """
        Check if the point lies within the bounding box of any RGJ.

        Args:
            point (Point): The 2D point to check.
            filted_idx (Optional[List[int]]): Optional subset of RGJ indices to filter.

        Returns:
            bool: True if the point is in any RGJ's bounding box.
        """
        point = np.array(point)
        rgjs = [self.rgjs[idx] for idx in filted_idx] if filted_idx is not None else self.rgjs

        return any(rgj.in_bbox(point) for rgj in rgjs)
    
    def find_bbox(self, point: Point, filted_idx: Optional[List[int]] = None) -> np.ndarray:
        """
        Return indices of RGJs whose bounding boxes contain the given point.

        Args:
            point (Point): The 2D point to check.
            filted_idx (Optional[List[int]]): Optional subset of RGJ indices to filter.

        Returns:
            np.ndarray: Indices of RGJs (in global index space) containing the point.
        """
        point = np.array(point)

        if filted_idx is not None:
            return np.array([idx for idx in filted_idx if self.rgjs[idx].in_bbox(point)])
        else:
            return np.nonzero([rgj.in_bbox(point) for rgj in self.rgjs])[0]
    
    def repulsion_vectors(self, points: Union[np.ndarray, List[Point]], filted_idx:Optional[List[int]] = None, min_dist_select:bool = True, return_reference = False) -> Union[np.ndarray, RepulsionVectorsAndRef]:
        points = np.atleast_2d(points).astype(float)
        if not len(self):
            return points*np.inf
        filted_idx = filted_idx if not filted_idx is None else list(range(len(self)))

        if return_reference:
            idxs = []
            repulsion_vectors = []

            for idx in filted_idx:
                vectors = self.rgjs[idx].repulsion_vector(points, min_dist_select=min_dist_select).reshape(-1, 2)

                idxs.extend([idx]*len(vectors))
                repulsion_vectors.append(vectors)

            repulsion_vectors = np.concatenate(repulsion_vectors, axis=0)
            return repulsion_vectors, np.array(idxs, dtype=int)
   
        else:
            rgjs = [self.rgjs[idx] for idx in filted_idx]
            return np.concatenate([rgj.repulsion_vector(points, min_dist_select=min_dist_select).reshape(-1, 2) for rgj in rgjs], axis=0)
    
    def gradient(self, points: Union[np.ndarray, List[Point]], min_dist_select=True) -> np.ndarray:

        points = np.atleast_2d(points).astype(float)
        if not len(self):
            return points * 0.0
        
        grad = np.zeros((len(points), 2), dtype=float)

        # Use closest RGJ per point to compute gradient
        _, grad_idxs = self.squared_dist(points=points, return_reference=True)
        unique_idxs = set(grad_idxs)
        
        for idx in unique_idxs:
            select = (grad_idxs == idx)
            grad[select] = self.rgjs[idx].gradient(points[select], min_dist_select=min_dist_select)
        
        return grad

    def eval(self, points: Union[np.ndarray, List[Point]], filted_idx:Optional[List[int]] = None) -> np.ndarray:
        points = np.atleast_2d(points).astype(float)
        rgjs = [self.rgjs[idx] for idx in filted_idx] if not filted_idx is None else self.rgjs

        if not len(rgjs):
            return points.sum(1)*0.0
        
        return np.max(np.stack([rgj.eval(points) for rgj in rgjs], axis=1), axis=1)
    
    def eval_per(self, points: Union[np.ndarray, List[Point]], idxs:Optional[List[int]] = None) -> np.ndarray:
        if len(points) != len(idxs):
            raise RuntimeError("The number of points doesn't match the number of indexes")
        
        points = np.atleast_2d(points).astype(float)
        n = len(points)
        idxs = np.array(idxs, dtype=int)
        
        evals = np.ones(n, dtype=points[0].dtype)
        for idx in set(idxs):
            select = idx == idxs
            evals[select] = self.rgjs[idx].eval(points[select])

        return evals
    
    def squared_dist(self, points:Union[np.ndarray, List[Point]], filted_idx:Optional[List[int]] = None, scaled=True, inverted=True, return_reference = False) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        points = np.atleast_2d(points).astype(float)
        if not len(self):
            warnings.warn("There are not any RGJs elements in the field")
            if return_reference:
                return points.sum(1)*np.inf, -np.ones_like(points.sum(1))
            return points.sum(1)*np.inf

        dists = self.squared_dist_list(points=points, filted_idx=filted_idx, scaled=scaled, inverted=inverted)

        if return_reference:
            min_idxs = np.argmin(dists, axis=1)

            filted_idx = filted_idx if filted_idx is not None else np.arange(len(self))
            return dists[np.arange(len(dists)), min_idxs], filted_idx[min_idxs]

        return np.min(dists, axis=1)
    
    def squared_dist_per(self, points: Union[np.ndarray, List[Point]], idxs:Optional[List[int]] = None, scaled=True, inverted=True) -> np.ndarray:

        idxs = [] if idxs is None else idxs
        n = len(points)

        if n != len(idxs):
            if not len(idxs):
                raise RuntimeError("The number of points doesn't match the number of indexes")
            else:
                warnings.warn("The number of points doesn't match the number of indexes. Each point matched with each rgj")
                idxs = np.arange(n)
        
        points = np.array(points)
        idxs = np.array(idxs, dtype=int)
        
        dists = np.ones(n, dtype=points[0].dtype)
        for idx in set(idxs):
            select = idx == idxs
            dists[select] = self.rgjs[idx].squared_dist(points[select], scaled=scaled, inverted=inverted)

        return dists
    
    def squared_dist_list(self, points:Union[np.ndarray, List[Point]], filted_idx:Optional[List[int]] = None, scaled=True, inverted=True) -> np.ndarray:
        points = np.atleast_2d(points).astype(float)
        rgjs = [self.rgjs[idx] for idx in filted_idx] if not filted_idx is None else self.rgjs

        if not len(rgjs):
            warnings.warn("There are not any RGJs elements in the field")
            return np.ones((len(points), len(rgjs)))*np.inf

        return np.stack([rgj.squared_dist(points, scaled=scaled, inverted=inverted) for rgj in rgjs], axis=1)
    
    def estimate_route_area(self, route:Union[List[Point], np.ndarray], step=1e-3, n=0, scale_transform:Scaler = lambda x: x) -> float:
        route = np.array(route)

        points, step, _ = lpf.interpolate_along_route(route=route, step=step, n=n, return_step_n=True)
        points = points if n <= 0 else points[:-1]

        f_eval = scale_transform(self.eval(points=points))

        return f_eval.sum()*step
    
    def estimate_route_highest_potential(self, route:Union[List[Point], np.ndarray], step=1e-2, n=0, scale_transform:Scaler = lambda x: x) -> float:
        route = np.array(route)

        points, step, _ = lpf.interpolate_along_route(route=route, step=step, n=n, return_step_n=True)
        points = points if n <= 0 else points[:-1]

        f_eval:np.ndarray = scale_transform(self.eval(points=points))

        return f_eval.max()

    def to_image(self, resolution:int = 200, margin:float = 0.0, center_point:Optional[Point] = None, size:Optional[FieldSize] = None, filted_idx:Optional[List[int]] = None, return_extent=True) -> Union[np.ndarray, Tuple[np.ndarray, List[float]]]:

        if center_point is None:
            if self.center_point is None:
                raise RuntimeError('Center point for field has not been defined')
            
            center_point = self.center_point

        if size is None:
            if self.size is None:
                raise RuntimeError('Size of field has not been defined')

            size = self.size
        else:
            size = np.array(size)

        n2 = size/2.0

        loc_tl = np.array(center_point) + np.array([-n2[0]-margin, n2[1]+margin])
        loc_br = np.array(center_point) + np.array([n2[0]+margin, -n2[1]-margin])

        y_resolution = int(resolution*abs(loc_tl[1] - loc_br[1])/abs(loc_br[0] - loc_tl[0]))
        xaxis = np.linspace(loc_tl[0], loc_br[0], resolution)
        yaxis = np.linspace(loc_tl[1], loc_br[1], y_resolution)

        xgrid, ygrid = np.meshgrid(xaxis, yaxis)
        points = np.vstack([xgrid.ravel(), ygrid.ravel()]).T

        image = self.eval(points, filted_idx=filted_idx).reshape((y_resolution, resolution))

        if return_extent:
            extent = np.reshape([loc_tl[0], loc_br[0], loc_br[1], loc_tl[1]], -1).tolist()
            return image, extent

        return image
    
    def toRGeoJSON(self, return_bbox=False) -> RGeoJSONCollection:\
    
        rgeojson = {
            'type': 'FeatureCollection',
            '_version_': "2D",
            'features': [rgj.toRGeoJSON() for rgj in self.rgjs],
            **self.extra_info
        }
        if return_bbox:
            extent = self.get_extent()
            rgeojson["bbox"] = extent[::2] + extent[1::2]

        return rgeojson
 