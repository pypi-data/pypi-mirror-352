from abc import ABC
from typing import Optional, Tuple, Any


class ImageInterface(ABC):
    """
    Abstract base class for image processing engines.

    This interface defines methods for detecting and locating images or objects
    within input data (e.g., images or video frames), implementing the
    :class:`ImageInterface`.

    Implementers should handle specific input types (e.g., image bytes, file paths)
    and reference data as needed.
    """


    def element_exist(self, input_data: Any, reference_data: Any) -> Optional[Tuple[int, int]]:
        """
        Find the location of a reference image within the input data.

        :param input_data: The input source (e.g., image, video frame) for detection.
        :type input_data: Any
        :param reference_data: The reference data used for matching or comparison.
        :type reference_data: Any
        :return: A tuple (x, y) representing the top-left corner of the reference image,
                 or None if not found.
        :rtype: Optional[Tuple[int, int]]
        """
        pass


    def find_element(self, input_data, image, index=None) -> Optional[Tuple[bool, Tuple[int, int], Tuple[Tuple[int, int], Tuple[int, int]]]]:
        """
        Locate a specific image in the input data and return detailed detection info.

        :param input_data: The input source (e.g., image, video frame) for detection.
        :type input_data: Any
        :param image: The reference image to locate.
        :type image: Any
        :return: A tuple (found, center, bounds) where:
                 - found: bool indicating if the image was found
                 - center: (x, y) coordinates of the image center
                 - bounds: ((x1, y1), (x2, y2)) bounding box (top-left, bottom-right)
                 Returns None if not found.
        :rtype: Optional[Tuple[bool, Tuple[int, int], Tuple[Tuple[int, int], Tuple[int, int]]]]
        """
        pass

    def assert_elements(self, input_data, elements, timeout=30, rule="any"):
        """
        Assert that elements are present in the input data based on the specified rule.

        :param input_data: The input source (e.g., image, video frame) for detection.
        :type input_data: Any
        :param elements: List of elements to locate.
        :type elements: list
        :param timeout: Maximum time to wait for elements.
        :type timeout: int
        :param rule: Rule to apply ("any" or "all").
        :type rule: str
        :return: True if the assertion passes.
        :rtype: bool
        """
        pass
