import cv2
import time
import numpy as np
from optics_framework.common import utils
from optics_framework.common.image_interface import ImageInterface
from optics_framework.common.logging_config import internal_logger
from optics_framework.engines.vision_models.base_methods import load_template

class TemplateMatchingHelper(ImageInterface):
    """
    Template matching helper that detects a reference image inside an input image.

    This class uses OpenCV's :func:`cv2.matchTemplate` function to locate instances
    of a template (reference image) within a larger image.
    """

    def find_element(
        self,frame, reference_data, index=None, confidence_level=0.85, min_inliers=10
    ):
        """
        Match a template image within a single frame image using SIFT and FLANN-based matching.
        Returns the location of a specific match by index.

        Parameters:
        - frame (np.array): Image data of the frame.
        - reference_data (np.array): Image data of the template.
        - index (int): The index of the match to retrieve.
        - offset (list): Optional x and y offsets in pixels to adjust the center location.
        - confidence_level (float): Confidence level for the ratio test (default is 0.85).
        - min_inliers (int): Minimum number of inliers required to consider a match valid (default is 10).

        Returns:
        - Bool: True if the template is found in the frame, False otherwise.
        - tuple: (x, y) coordinates of the indexed match or (None, None) if out of bounds.
        - frame (np.array): The frame with all detected templates annotated.
        """
        reference_data = load_template(reference_data)
        sift = cv2.SIFT_create()
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)

        if reference_data is None or frame is None:
            return False,(None, None), None

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(reference_data, cv2.COLOR_BGR2GRAY)

        kp_frame, des_frame = sift.detectAndCompute(frame_gray, None)
        kp_template, des_template = sift.detectAndCompute(template_gray, None)

        if des_template is None or des_frame is None:
            return False,(None, None), frame

        try:
            matches = flann.knnMatch(des_template, des_frame, k=2)
        except cv2.error:
            return False, (None, None), frame

        good_matches = [m for m, n in matches if m.distance < confidence_level * n.distance]

        if len(good_matches) < min_inliers:
            return False, (None, None), frame

        src_pts = np.float32([kp_template[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp_frame[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        if M is None:
            return False, (None, None), frame

        matches_mask = mask.ravel().tolist()
        inliers = np.sum(matches_mask)
        if inliers < min_inliers:
            return False, (None, None), frame

        h, w = reference_data.shape[:2]
        centers = []
        for i in range(len(good_matches)):
            if matches_mask[i]:
                center_template = np.float32([[w / 2, h / 2]]).reshape(-1, 1, 2)
                center_frame = cv2.perspectiveTransform(center_template, M)
                center_x, center_y = int(center_frame[0][0][0]), int(center_frame[0][0][1])
                centers.append((center_x, center_y))

                # Draw bounding box around the matched template in the frame
                pts = np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)
                dst = cv2.perspectiveTransform(pts, M)
                frame = cv2.polylines(frame, [np.int32(dst)], True, (0, 255, 0), 3, cv2.LINE_AA)

                # Draw a small circle at the center
                cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)

        if not centers:
            return False, (None, None), frame

        if index is not None:
            if 0 <= index < len(centers):
                return True, centers[index], frame
            else:
                return False, (None, None), frame

        return True, centers[0], frame

    def assert_elements(self, frame, templates, timeout=30, rule="any"):
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
        end_time = time.time() + timeout
        annotated_frame = frame.copy()
        found_status = {template: False for template in templates}

        while time.time() < end_time:
            for template_path in templates:
                if found_status[template_path]:  # Skip if already found (for 'all' rule)
                    continue

                success, _ , annotated = self.find_element(
                    frame.copy(),  # use a copy of the frame to avoid overwriting annotations across templates
                    reference_data=template_path,
                )
                if success:
                    found_status[template_path] = True
                    annotated_frame = annotated  # use the latest annotated version

            # Rule evaluation
            if rule == "any" and any(found_status.values()):
                utils.save_screenshot(annotated_frame, "assert_elements_templatematching_result")
                return True
            if rule == "all" and all(found_status.values()):
                utils.save_screenshot(annotated_frame, "assert_elements_templatematching_result")
                return True

            time.sleep(0.5)  # Prevent busy looping

        internal_logger.warning("SIFT assert_elements failed within timeout.")
        utils.save_screenshot(annotated_frame, "assert_elements_templatematching_failed")
        return False


    def element_exist(self,frame, reference_data, offset=[0, 0], confidence_level=0.85, min_inliers=10):
        """
        Match a template image within a single frame image using SIFT and FLANN-based matching.
        Finds both the center of the template and its bounding box.

        Parameters:
        - frame (np.array): Image data of the frame.
        - reference_data (np.array): Image data of the template.
        - offset (list): Optional [x, y] offsets in pixels to adjust the center location.
        - confidence_level (float): Confidence level for the ratio test (default is 0.85).
        - min_inliers (int): Minimum number of inliers required to consider a match valid (default is 10).

        Returns:
        - bool: True if the template is found, False otherwise.
        - tuple: (x, y) coordinates of the center of the template in the frame or (None, None) if no match is found.
        - list: [(top-left), (bottom-right)] bounding box coordinates or None if no match is found.
        """

        # Create SIFT object
        sift = cv2.SIFT_create()

        # Create FLANN object with parameters
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)

        if reference_data is None or frame is None:
            # internal_logger.debug("Error: Cannot read the images.")
            return False, (None, None), None

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(reference_data, cv2.COLOR_BGR2GRAY)

        # Detect keypoints and descriptors for both images
        kp_frame, des_frame = sift.detectAndCompute(frame_gray, None)
        kp_template, des_template = sift.detectAndCompute(template_gray, None)

        if des_template is None or des_frame is None:
            # internal_logger.debug("Error: No descriptors found in template or frame.")
            return False, (None, None), None

        try:
            matches = flann.knnMatch(des_template, des_frame, k=2)
        except cv2.error as e:
            internal_logger.debug(f"Error in FLANN matching: {e}")
            return False, (None, None), None

        # Apply Lowe's ratio test to filter good matches
        good_matches = [m for m, n in matches if m.distance < confidence_level * n.distance]

        if len(good_matches) < min_inliers:
            # internal_logger.debug(f"Not enough good matches found: {len(good_matches)} (min required: {min_inliers})")
            return False, (None, None), None

        # Extract matched keypoints
        src_pts = np.float32([kp_template[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp_frame[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        # Compute homography matrix
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        if M is None:
            # internal_logger.debug("Homography matrix computation failed.")
            return False, (None, None), None

        matches_mask = mask.ravel().tolist()
        inliers = np.sum(matches_mask)

        if inliers < min_inliers:
            # internal_logger.debug(f"Not enough inliers: {inliers} (min required: {min_inliers})")
            return False, (None, None), None

        # Find center of the template in the frame
        h, w = reference_data.shape[:2]
        center_template = np.float32([[w / 2, h / 2]]).reshape(-1, 1, 2)
        center_frame = cv2.perspectiveTransform(center_template, M)
        center_x, center_y = int(center_frame[0][0][0]), int(center_frame[0][0][1])

        # Apply the offset to the center position
        center_x += offset[0]
        center_y -= offset[1]

        # Find bounding box corners
        bbox_pts = np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)
        try:
            bbox_transformed = cv2.perspectiveTransform(bbox_pts, M)
            bbox_corners = [(int(pt[0][0]), int(pt[0][1])) for pt in bbox_transformed]
            top_left = bbox_corners[0]
            bottom_right = bbox_corners[2]
        except cv2.error as e:
            internal_logger.debug(f"Error in perspective transformation: {e}")
            return False, (None, None), None

        # internal_logger.debug(f"Template found at center: ({center_x}, {center_y}) with bbox: {top_left} -> {bottom_right}")

        return True, (center_x, center_y), [top_left, bottom_right]
