
import logging
import os, json, gzip, bz2, cv2
from typing import Dict, List, Literal, Optional

from deplacecli.draw import Landmarks, Mask, BBox, Text
from deplacecli.storage import AzureBlobStorage

class Command:

    @staticmethod
    def download(
        token: str,
        source_folder: str, 
        target_folder: str,
        limit_mp4: int,
        demo: False
    ):
        
        # Data container
        container_name = "demo" if demo else "datasets"
        
        dataset_storage = AzureBlobStorage(
            account_name="deplacestorage",
            account_sas_token=token,
            container_name=container_name
        )

        dataset_storage.import_remote_directory(
            remote_directory_path=source_folder,
            target_directory_path=target_folder,
            limit_mp4=limit_mp4
        )

    @staticmethod
    def annotate(
        episode: str,
        output_folder: str = "data/Folding/annotated/",
        bbox: bool = False,
        mask: bool = False,
        label: bool = False,
        compression: Optional[Literal["avc1", "mp4v", "h264"]] = "mp4v"
    ):
        
        # Check episode format
        if not episode or not isinstance(episode, str) or not episode.startswith("V") or "_" not in episode:
            raise ValueError("Invalid episode format. Expected format: Vxx_Eyy")

        # Walk path to find dataset.json file in the current directory
        current_directory = os.getcwd()
        dataset_json_path = None
        for root, dirs, files in os.walk(current_directory):
            if "dataset.json" in files:
                dataset_json_path = os.path.join(root, "dataset.json")
                break
            elif "dataset.json.gz" in files:
                dataset_json_path = os.path.join(root, "dataset.json.gz")
                break
            elif "dataset.json.bz2" in files:
                dataset_json_path = os.path.join(root, "dataset.json.bz2")
                break

        # If dataset.json is not found, raise an error
        if not dataset_json_path:
            raise FileNotFoundError("dataset.json not found in the current directory or its subdirectories.")
        
        # Walk path to find the video file in the current directory
        video_file = episode + ".mp4" if not episode.endswith(".mp4") else episode
        video_file_found = False
        for root, dirs, files in os.walk(current_directory):
            if video_file in files:
                video_file_found = True
                video_file_path = os.path.join(root, video_file)
                break

        # If video file is not found, raise an error
        if not video_file_found:
            raise FileNotFoundError(f"Video file {video_file} not found in the current directory or its subdirectories.")

        # Import the dataset
        if dataset_json_path.endswith(".gz"):
            with gzip.open(dataset_json_path, "rt", encoding="utf-8") as f:
                dataset: List[Dict] = json.load(f)
        elif dataset_json_path.endswith(".bz2"):
            with bz2.open(dataset_json_path, "rt", encoding="utf-8") as f:
                dataset: List[Dict] = json.load(f)
        else:
            with open(dataset_json_path, "r", encoding="utf-8") as f:
                dataset: List[Dict] = json.load(f)
                
        # Extract all the frames for the specified episode
        episode_frames = [frame for frame in dataset if frame.get('episode_id') == episode]
        episode_frames.sort(key=lambda frame: frame.get('frame_index', 0))

        # Check existence in dataset.json
        if not episode_frames:
            raise ValueError(f"No frames found for episode {episode} in dataset.json.")
        
        # Open the video file
        cap = cv2.VideoCapture(video_file_path)
        if not cap.isOpened():
            raise IOError("Cannot open video file")
        
        # Coherence check
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if not len(episode_frames) == frame_count:
            logging.warning(f"Number of frames in dataset.json ({len(episode_frames)}) does not match the video file ({frame_count}).")

        # Ensure output folder exists
        os.makedirs(output_folder, exist_ok=True)

        # Video Writer setup with compression
        annotated_episode_fp = os.path.join(output_folder, f"{episode}_VIZ.mp4")
        fourcc = cv2.VideoWriter.fourcc(*compression)  
        writer = cv2.VideoWriter(
            filename=annotated_episode_fp,
            fourcc=fourcc,
            fps=cap.get(cv2.CAP_PROP_FPS),
            frameSize=(
                int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            )
        )

        # Process each frame
        while cap.isOpened():

            ret, frame = cap.read()
            if not ret:
                break

            frame_index = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1
            frame_data = next(
                (f for f in episode_frames if f.get('frame_index') == frame_index), 
                None
            )

            # If frame data is not found, skip to the next frame
            if not frame_data: 
                logging.warning(f"Frame data not found for frame index {frame_index}. Skipping frame.")
                continue

            # Draw mask
            if frame_data.get("object_mask_rle") and mask:
                frame = Mask.draw(
                    frame, 
                    frame_data.get("object_mask_rle", None),
                )

            # Draw Object BBox
            if frame_data.get("object_bbox") and bbox:
                frame = BBox.draw_with_label(
                    frame, 
                    int(frame_data["object_bbox"][0] * frame_data["frame_width"]),
                    int(frame_data["object_bbox"][1] * frame_data["frame_height"]),
                    int(frame_data["object_bbox"][2] * frame_data["frame_width"]),
                    int(frame_data["object_bbox"][3] * frame_data["frame_height"]),
                    label=frame_data.get("action_label", ""),
                )

            # Draw Left Hand BBox
            if frame_data.get("hand_left_bbox") and bbox:
                frame = BBox.draw_with_label(
                    frame, 
                    int(frame_data["hand_left_bbox"][0] * frame_data["frame_width"]),
                    int(frame_data["hand_left_bbox"][1] * frame_data["frame_height"]),
                    int(frame_data["hand_left_bbox"][2] * frame_data["frame_width"]),
                    int(frame_data["hand_left_bbox"][3] * frame_data["frame_height"]),
                    label="Left Hand",
                )

            # Draw Right Hand Landmarks
            if frame_data.get("hand_left_mp_landmarks") and bbox:
                frame = Landmarks.draw(
                    frame, 
                    frame_data["hand_left_mp_landmarks"],
                )

            # Draw Right Hand BBox
            if frame_data.get("hand_right_bbox") and bbox:
                frame = BBox.draw_with_label(
                    frame, 
                    int(frame_data["hand_right_bbox"][0] * frame_data["frame_width"]),
                    int(frame_data["hand_right_bbox"][1] * frame_data["frame_height"]),
                    int(frame_data["hand_right_bbox"][2] * frame_data["frame_width"]),
                    int(frame_data["hand_right_bbox"][3] * frame_data["frame_height"]),
                    label="Right Hand",
                )

            # Draw Right Hand Landmarks
            if frame_data.get("hand_right_mp_landmarks") and bbox:
                frame = Landmarks.draw(
                    frame, 
                    frame_data["hand_right_mp_landmarks"],
                )

            # Draw Label
            if frame_data.get("action_label") and label:
                frame = Text.draw(frame, frame_data["action_label"])

            # Write the annotated frame to the video file
            writer.write(frame)

        # Release resources
        cap.release()
        writer.release()



            