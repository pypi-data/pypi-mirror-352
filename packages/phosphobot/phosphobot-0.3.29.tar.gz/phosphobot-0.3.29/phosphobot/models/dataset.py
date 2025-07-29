import asyncio
import datetime
import json
import os
import shutil
import time
from pathlib import Path
from typing import Dict, List, Literal, Optional, Tuple, cast
import tempfile

import numpy as np
import pandas as pd
from huggingface_hub import (
    HfApi,
    create_branch,
    create_repo,
    delete_file,
    delete_folder,
    delete_repo,
    upload_folder,
)
from loguru import logger
from pydantic import (
    AliasChoices,
    BaseModel,
    Field,
    field_validator,
    model_validator,
)

from phosphobot.types import VideoCodecs
from phosphobot.utils import (
    NdArrayAsList,
    NumpyEncoder,
    compute_sum_squaresum_framecount_from_video,
    create_video_file,
    decode_numpy,
    get_field_min_max,
    get_hf_token,
    get_hf_username_or_orgid,
    get_home_app_path,
    parse_hf_username_or_orgid,
)
from phosphobot.models.robot import BaseRobot

DEFAULT_FILE_ENCODING = "utf-8"


class Observation(BaseModel):
    # Main image (reference for OpenVLA actions)
    # TODO PLB: what size?
    # OpenVLA size: 224 × 224px
    main_image: np.ndarray = Field(default_factory=lambda: np.array([]))
    # We store any other images from other cameras here
    secondary_images: List[np.ndarray] = Field(default_factory=list)
    # Size 7 array with the robot end effector (absolute, in the robot referencial)
    # Warning: this is not the same 'state' used in lerobot examples
    state: np.ndarray = Field(default_factory=lambda: np.array([]))
    # Current joints positions of the robot
    joints_position: np.ndarray
    # Instruction given to the robot, can be null when recording the dataset
    language_instruction: str | None = None
    # Timestamp in seconds since episode start (usefull for frequency)
    timestamp: float | None = None

    # To be able to use np.array in pydantic, we need to use arbitrary_types_allowed = True
    class Config:
        arbitrary_types_allowed = True

    def dict(self, *args, **kwargs):
        # Override dict method to handle numpy arrays
        d = super().dict(*args, **kwargs)
        return d


class Step(BaseModel):
    observation: Observation  # Current observation, most informations are stored here
    # Robot action as outputed by OpenVLA (size 7 array) based on the CURRENT observation
    action: Optional[np.ndarray] = None
    # if this is the first step of an episode that contains the initial state.
    is_first: bool | None = None
    # True if this is a terminal step, meaning the episode isn' over after this step but the robot is in a terminal state
    is_terminal: bool | None = None
    # if this is the last step of an episode, that contains the last observation. When true,
    is_last: bool | None = None
    reward: float = 0.0  # Reward given by the environment
    # Discount factor for the reward, not used for now
    discount: float = 1.0
    # Any other metadata we want to store, for instance the created_at timestamp in ms
    metadata: dict = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True
        extra = "ignore"


class Episode(BaseModel):
    """
    # Save an episode
    episode.save("robot_episode.json")

    # Load episode
    loaded_episode = Episode.load("robot_episode.json")

    """

    steps: List[Step] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)

    class Config:
        extra = "ignore"

    @property
    def dataset_path(self) -> Path:
        """
        Return the file path of the episode
        """
        format = self.metadata.get("format")
        dataset_name = self.metadata.get("dataset_name")
        if not format:
            raise ValueError("Episode metadata format not set")
        if not dataset_name:
            raise ValueError("Episode metadata dataset_name not set")

        path = get_home_app_path() / "recordings" / format / dataset_name
        os.makedirs(path, exist_ok=True)
        return path

    @property
    def episodes_path(self) -> Path:
        """
        Return the file path of the episode
        """
        path = self.dataset_path / "data" / "chunk-000"
        os.makedirs(path, exist_ok=True)
        return path

    @property
    def parquet_path(self) -> Path:
        """
        Return the file path of the episode .
        """
        return self.episodes_path / f"episode_{self.index:06d}.parquet"

    @property
    def json_path(self) -> Path:
        """
        Return the file path of the episode
        """
        return self.dataset_path / f"episode_{self.metadata['timestamp']}.json"

    @property
    def cameras_folder_path(self) -> Path:
        """
        Return the cameras folder path
        """
        return self.dataset_path / "videos" / "chunk-000"

    def get_video_path(self, camera_key: str) -> Path:
        """
        Return the file path of the episode
        """
        path = self.dataset_path / "videos" / "chunk-000" / camera_key
        os.makedirs(path, exist_ok=True)
        return path / f"episode_{self.index:06d}.mp4"

    def save(
        self,
        folder_name: str,
        dataset_name: str,
        fps: int,
        format_to_save: Literal["json", "lerobot_v2", "lerobot_v2.1"] = "lerobot_v2.1",
        last_frame_index: int | None = 0,
        info_model: Optional["InfoModel"] = None,
    ):
        """
        Save the episode to a JSON file with numpy array handling for phospho recording to RLDS format
        Save the episode to a parquet file with an mp4 video for LeRobot recording

        Episode are saved in a folder with the following structure:

        ---- <folder_name> : phosphobot
        |   ---- json
        |   |   ---- <dataset_name>
        |   |   |   ---- episode_xxxx-xx-xx_xx-xx-xx.json
        |   ---- lerobot_v2 or lerobot_v2.1
        |   |   ---- <dataset_name>
        |   |   |   ---- data
        |   |   |   |   ---- chunk-000
        |   |   |   |   |   ---- episode_xxxxxx.parquet
        |   |   |   ---- videos
        |   |   |   |   ---- chunk-000
        |   |   |   |   |   ---- observation.images.main.right (if stereo else only main)
        |   |   |   |   |   |   ---- episode_xxxxxx.mp4
        |   |   |   |   |   ---- observation.images.main.left (if stereo)
        |   |   |   |   |   |   ---- episode_xxxxxx.mp4
        |   |   |   |   |   ---- observation.images.secondary_0 (Optional)
        |   |   |   |   |   |   ---- episode_xxxxxx.mp4
        |   |   |   |   |   ---- observation.images.secondary_1 (Optional)
        |   |   |   |   |   |   ---- episode_xxxxxx.mp4
        |   |   |   ---- meta
        |   |   |   |   ---- stats.json or episodes_stats.jsonl (depending on format version)
        |   |   |   |   ---- episodes.jsonl
        |   |   |   |   ---- tasks.jsonl
        |   |   |   |   ---- info.json

        """

        # Update the metadata with the format used to save the episode
        self.metadata["format"] = format_to_save
        logger.info(f"Saving episode to {folder_name} with format {format_to_save}")
        self.metadata["dataset_name"] = os.path.join(
            folder_name, format_to_save, dataset_name
        )

        if format_to_save.startswith("lerobot"):
            if not info_model:
                raise ValueError("InfoModel is required to save in LeRobot format")

            if last_frame_index is None:
                raise ValueError(
                    "last_frame_index is required to save in LeRobot format"
                )

            # Check the elements in the folder folder_name/lerobot_v2-format/dataset_name/data/chunk-000/
            # the episode index is the max index + 1
            # We create the list of index from filenames and take the max + 1
            li_data_filename = os.listdir(self.episodes_path)
            episode_index = (
                max(
                    [
                        int(data_filename.split("_")[-1].split(".")[0])
                        for data_filename in li_data_filename
                    ]
                )
                + 1
                if li_data_filename
                else 0
            )

            lerobot_episode_parquet: LeRobotEpisodeModel = (
                self.convert_episode_data_to_LeRobot(
                    fps=fps,
                    episodes_path=str(self.episodes_path),
                    episode_index=episode_index,
                    last_frame_index=last_frame_index,
                    task_index=self.metadata.get("task_index", 0),
                )
            )
            lerobot_episode_parquet.to_parquet(str(self.parquet_path))

            # Create the main video file and path
            # Get the video_path from the InfoModel
            secondary_camera_frames = self.get_episode_frames_secondary_cameras()
            for i, (key, feature) in enumerate(
                info_model.features.observation_images.items()
            ):
                if i == 0:
                    # First video is the main camera
                    frames = np.array(self.get_episode_frames_main_camera())
                elif i > len(secondary_camera_frames):
                    # There are secondary cameras in the info model, but not in the episode
                    # Skip video creation.
                    logger.warning(
                        f"Secondary camera {key} not found in the episode. Skipping video creation."
                    )
                    break
                else:
                    # Following videos are the secondary cameras
                    frames = np.array(secondary_camera_frames[i - 1])
                video_path = self.get_video_path(camera_key=key)
                saved_path = create_video_file(
                    frames=frames,
                    output_path=str(video_path),
                    target_size=(feature.shape[1], feature.shape[0]),
                    fps=feature.info.video_fps,
                    codec=feature.info.video_codec,
                )
                # Check if the video was saved
                if (isinstance(saved_path, str) and os.path.exists(saved_path)) or (
                    isinstance(saved_path, tuple)
                    and all(os.path.exists(path) for path in saved_path)
                ):
                    logger.info(f"Video {key} {i} saved to {video_path}")
                else:
                    logger.error(f"Video {key} {i} not saved to {video_path}")

        # Case where we save the episode in JSON format
        # Save the episode to a JSON file
        else:
            self.metadata["timestamp"] = datetime.datetime.now().strftime(
                "%Y-%m-%d_%H-%M-%S"
            )
            episode_index = (
                max(
                    [
                        int(data_filename.split("_")[-1].split(".")[0])
                        for data_filename in os.listdir(self.episodes_path)
                    ]
                )
                + 1
                if os.listdir(self.episodes_path)
                else 0
            )
            # Convert the episode to a dictionary
            data_dict = self.model_dump()

            # Save to JSON using the custom encoder
            with open(self.json_path, "w", encoding=DEFAULT_FILE_ENCODING) as f:
                json.dump(data_dict, f, cls=NumpyEncoder)

    @classmethod
    def from_json(cls, episode_data_path: str) -> "Episode":
        """Load an episode data file. There is numpy array handling for json format."""
        # Check that the file exists
        if not os.path.exists(episode_data_path):
            raise FileNotFoundError(f"Episode file {episode_data_path} not found.")

        with open(episode_data_path, "r", encoding=DEFAULT_FILE_ENCODING) as f:
            data_dict = json.load(f, object_hook=decode_numpy)
            logger.debug(f"Data dict keys: {data_dict.keys()}")

        return cls(**data_dict)

    @classmethod
    def from_parquet(
        cls, episode_data_path: str, format: Literal["lerobot_v2", "lerobot_v2.1"]
    ) -> "Episode":
        """
        Load an episode data file. We only extract the information from the parquet data file.
        TODO(adle): Add more information in the Episode when loading from parquet data file from metafiles and videos
        """
        # Check that the file exists
        if not os.path.exists(episode_data_path):
            raise FileNotFoundError(f"Episode file {episode_data_path} not found.")

        episode_df = pd.read_parquet(episode_data_path)
        # Try to load the tasks.jsonl
        dataset_path = str(Path(episode_data_path).parent.parent.parent)

        tasks_path = os.path.join(dataset_path, "meta", "tasks.jsonl")
        if os.path.exists(tasks_path):
            # Load the tasks.jsonl file
            tasks_df = pd.read_json(tasks_path, lines=True)
            # Get the task index from the task index column
            episode_df["task_index"] = tasks_df["task_index"].iloc[0]
            # Merge the task index with the episode_df
            episode_df = pd.merge(
                episode_df,
                tasks_df[["task_index", "task"]],
                on="task_index",
                how="left",
            )

        # Rename the columns to match the expected names in the instance
        episode_df.rename(
            columns={
                "observation.state": "joints_position",
                "task": "language_instruction",
            },
            inplace=True,
        )
        # agregate the columns in joints_position, timestamp, main_image, state to a column observation.
        cols = ["joints_position", "timestamp"]
        if "language_instruction" in episode_df.columns:
            cols.append("language_instruction")
        # Create a new column "observation" that is a dict of the selected columns for each row
        episode_df["observation"] = episode_df[cols].to_dict(orient="records")

        # Add metadata to the episode
        # the path is like this : dataset_name/data/chunk-000/episode_xxxxxx.parquet
        # get the path : dataset_name
        normalized = os.path.normpath(episode_data_path)
        parts = normalized.split(os.sep)
        if len(parts) >= 4:
            dataset_path = parts[-4]
        else:
            logger.warning(
                f"Episode {episode_data_path} does not contain the dataset name in the path. Path should be: dataset_name/data/chunk-000/episode_xxxxxx.parquet"
                + "Using parent folder name as dataset name."
            )
            dataset_path = os.path.basename(os.path.dirname(episode_data_path))

        metadata = {
            "dataset_name": dataset_path,
            "format": format,
            "index": episode_df["episode_index"].iloc[0],
        }

        episode_model = cls(
            steps=cast(List[Step], episode_df.to_dict(orient="records")),
            metadata=metadata,
        )
        return episode_model

    @classmethod
    def load(
        cls,
        episode_data_path: str,
        format: Literal["json", "lerobot_v2", "lerobot_v2.1"],
    ) -> "Episode":
        """Load an episode data file. There is numpy array handling for json format.""
        If we load the parquet file we don't have informations about the images
        """
        episode_data_extension = episode_data_path.split(".")[-1]

        if episode_data_extension == "json":
            return cls.from_json(episode_data_path)
        elif episode_data_extension == "parquet":
            return cls.from_parquet(
                episode_data_path,
                format=cast(Literal["lerobot_v2", "lerobot_v2.1"], format),
            )
        else:
            raise ValueError(
                f"Unsupported episode data format: {episode_data_extension}"
            )

    def add_step(self, step: Step):
        """
        Add a step to the episode
        Handles the is_first, is_terminal and is_last flags to set the correct values when appending a step
        """
        # When a step is aded, it is the last of the episode by default until we add another step
        step.is_terminal = True
        step.is_last = True

        # Check if the observation are all NAN values (this is the case when there is a read error on motors)
        # If so, replace them with the previous step values
        if len(self.steps) > 0 and np.isnan(step.observation.joints_position).all():
            # Replace the joints_position with the previous step
            step.observation.joints_position = self.steps[
                -1
            ].observation.joints_position.copy()

        # If current step is the first step of the episode
        if not self.steps:
            step.is_first = True
        else:
            step.is_first = False
            # Change the previous step to not be terminal and last
            self.steps[-1].is_terminal = False
            self.steps[-1].is_last = False
        # Append the step to the episode
        self.steps.append(step)

    def update_previous_step(self, step: Step):
        """
        Update the previous step with the given step.
        """
        # The action is an order in absolute on the postion of the robots joints (radians angles)
        if len(self.steps) > 0:
            self.steps[-1].action = step.observation.joints_position.copy()

    async def play(
        self,
        robots: List[BaseRobot],
        playback_speed: float = 1.0,
        interpolation_factor: int = 4,
        replicate: bool = False,
    ):
        """
        Play the episode on the robot with on-the-fly interpolation.
        """

        def move_robots(joints: np.ndarray) -> None:
            """
            Solve which robot should move depending on the number of joints and
            the number of robots.
            - If nb robots == nb joints, move each robot with its respective joints
            - If nb joints > nb robots, move each robot with its respective joints until
                the last robot. Extra joints are ignored.
            - If nb joints < nb robots, move each robot with its respective joints until
                the last joint. Extra robots are ignored
            """

            nonlocal robots

            nb_joints = 1 + len(joints) % 6  # 6 joints per robot
            for i, robot in enumerate(robots):  # extra joints are ignored
                # If there are more robots than joints, ignore the extra robots
                if i >= nb_joints:
                    if replicate is False:
                        break
                    else:
                        # Go back to the first robot
                        i = i % nb_joints

                # Get the joints for the current robot
                robot_joints = joints[i * 6 : (i + 1) * 6]
                # Move the robot with its respective joints
                robot.set_motors_positions(robot_joints, enable_gripper=True)

        for index, step in enumerate(self.steps):
            # Get current and next step
            curr_step = step
            next_step = self.steps[index + 1] if index + 1 < len(self.steps) else None

            if (
                next_step is not None
                and curr_step.observation.timestamp is not None
                and next_step.observation.timestamp is not None
                and curr_step.observation.joints_position is not None
                and next_step.observation.joints_position is not None
            ):
                # if the current step is all NAN, skip
                if np.isnan(curr_step.observation.joints_position).all():
                    logger.warning(
                        f"Skipping step {index} because all joints positions are NaN"
                    )
                    continue
                # Calculate base delta timestamp
                delta_timestamp = (
                    next_step.observation.timestamp - curr_step.observation.timestamp
                )
                # Higher playback speed = less time per segment
                # Higher interpolation factor = less time per segment + more segments
                time_per_segment = (
                    delta_timestamp / interpolation_factor / playback_speed
                )

                # Fill empty values from the next step joints with the current step
                next_step.observation.joints_position = np.where(
                    np.isnan(next_step.observation.joints_position),
                    curr_step.observation.joints_position,
                    next_step.observation.joints_position,
                )

                # Perform interpolation steps
                for i in range(interpolation_factor):
                    start_time = time.perf_counter()

                    # Calculate interpolation ratio (0 to 1 across all segments)
                    t = i / interpolation_factor

                    # Interpolate between the current and next step
                    interp_value = t * (next_step.observation.joints_position) + (
                        1 - t
                    ) * (curr_step.observation.joints_position)

                    if index % 20 == 0 and i == 0:
                        logger.info(f"Playing step {index}")

                    move_robots(interp_value)
                    # Timing control
                    elapsed = time.perf_counter() - start_time
                    time_to_wait = max(time_per_segment - elapsed, 0)
                    await asyncio.sleep(time_to_wait)

            else:
                # Handle last step or cases where timestamp is None
                start_time = time.perf_counter()
                move_robots(curr_step.observation.joints_position)

    @property
    def index(self) -> int:
        """
        Return the episode index
        """
        return self.metadata.get("index", 0)

    # Setter
    @index.setter
    def index(self, value: int):
        """
        Set the episode index
        """
        self.metadata["index"] = value

    def convert_episode_data_to_LeRobot(
        self,
        fps: int,
        episodes_path: str,  # We need the episodes path to load the value of the last frame index
        episode_index: int = 0,
        last_frame_index: int = 0,
        task_index: int = 0,
    ):
        """
        Convert a dataset to the LeRobot format
        """
        logger.info("Converting dataset to LeRobot format...")

        # Prepare the data for the Parquet file
        episode_data: Dict[str, List] = {
            "action": [],
            "observation.state": [],  # with a dot, not an underscore
            "timestamp": [],
            "task_index": [],
            "episode_index": [],
            "frame_index": [],
            "index": [],
        }

        if self.steps[0].observation.timestamp is None:
            raise ValueError(
                "The first step of the episode must have a timestamp to calculate the other timestamps during reedition of timestamps."
            )

        logger.info(f"Number of steps during conversion: {len(self.steps)}")

        # episode_data["timestamp"] = [step.observation.timestamp for step in self.steps]
        episode_data["timestamp"] = (np.arange(len(self.steps)) / fps).tolist()

        for frame_index, step in enumerate(self.steps):
            # Fill in the data for each step
            episode_data["episode_index"].append(episode_index)
            episode_data["frame_index"].append(frame_index)
            episode_data["observation.state"].append(
                step.observation.joints_position.astype(np.float32)
            )
            episode_data["index"].append(frame_index + last_frame_index)
            # TODO: Implement multiple tasks in dataset
            episode_data["task_index"].append(task_index)
            assert step.action is not None, (
                "The action must be set for each step before saving"
            )
            episode_data["action"].append(step.action.tolist())

        # Validate frame dimensions and data type
        height, width = self.steps[0].observation.main_image.shape[:2]
        if any(
            frame.shape[:2] != (height, width) or frame.ndim != 3
            for frame in self.get_episode_frames_main_camera()
        ):
            raise ValueError(
                "All frames must have the same dimensions and be 3-channel RGB images."
            )

        return LeRobotEpisodeModel(
            action=episode_data["action"],
            observation_state=episode_data["observation.state"],
            timestamp=episode_data["timestamp"],
            task_index=episode_data["task_index"],
            episode_index=episode_data["episode_index"],
            frame_index=episode_data["frame_index"],
            index=episode_data["index"],
        )

    def get_episode_frames_main_camera(self) -> List[np.ndarray]:
        """
        Return the frames of the main camera
        """
        return [step.observation.main_image for step in self.steps]

    def get_episode_frames_secondary_cameras(self) -> List[np.ndarray]:
        """
        Returns a list, where each np.array is a series of frames for a secondary camera.
        """
        # Handle the case where there are no secondary images
        if len(self.steps) == 0 or not self.steps[0].observation.secondary_images:
            return []

        # Convert the nested structure to a numpy array first
        all_images = [
            np.array([step.observation.secondary_images[i] for step in self.steps])
            for i in range(len(self.steps[0].observation.secondary_images))
        ]

        return all_images

    def delete(self, update_hub: bool = True, repo_id: str | None = None) -> None:
        """
        Remove files related to the episode. Note: this doesn't update the meta files from the dataset.
        Call Data.delete_episode to update the meta files.

        If update_hub is True, the files will be removed from the Hugging Face repository.
        There is no verification that the files are actually in the repository or that the repository exists.
        You need to do that beforehand.
        """
        if (
            self.metadata.get("format") == "lerobot_v2"
            or self.metadata.get("format") == "lerobot_v2.1"
        ):
            # Delete the parquet file
            try:
                os.remove(self.parquet_path)
            except FileNotFoundError:
                logger.warning(
                    f"Parquet file {self.parquet_path} not found. Skipping deletion."
                )

            if update_hub and repo_id is not None:
                # In the huggingface dataset, we need to pass the relative path.
                relative_episode_path = (
                    f"data/chunk-000/episode_{self.index:06d}.parquet"
                )
                delete_file(
                    repo_id=repo_id,
                    path_in_repo=relative_episode_path,
                    repo_type="dataset",
                )

            # Remove the video files from the HF repository
            all_camera_folders = os.listdir(self.cameras_folder_path)
            for camera_key in all_camera_folders:
                if "image" not in camera_key:
                    continue
                try:
                    os.remove(self.get_video_path(camera_key))
                except FileNotFoundError:
                    logger.warning(
                        f"Video file {self.get_video_path(camera_key)} not found. Skipping deletion."
                    )
                if update_hub and repo_id is not None:
                    delete_file(
                        repo_id=repo_id,
                        path_in_repo=f"videos/chunk-000/{camera_key}/episode_{self.index:06d}.mp4",
                        repo_type="dataset",
                    )

        elif self.metadata.get("format") == "json":
            os.remove(self.json_path)

    def parquet(self) -> pd.DataFrame:
        """
        Load the .parquet file of the episode. Only works for LeRobot format.
        """
        if not (
            self.metadata.get("format") == "lerobot_v2"
            or self.metadata.get("format") == "lerobot_v2.1"
        ):
            raise ValueError(
                "The episode must be in LeRobot format to convert it to a DataFrame"
            )

        return pd.read_parquet(self.parquet_path)


class LeRobotEpisodeModel(BaseModel):
    """
    Data model for LeRobot episode in Parquet format
    Stored in a parquet in dataset_name/data/chunk-000/episode_xxxxxx.parquet
    """

    action: List[List[float]]
    observation_state: List[List[float]]
    timestamp: List[float]
    task_index: List[int]
    episode_index: List[int]
    frame_index: List[int]
    index: List[int]

    @model_validator(mode="before")
    def validate_lengths(cls, values):
        """
        Ensure all lists have the same length.
        """
        lengths = [
            len(values.get(field, []))
            for field in [
                "action",
                "observation_state",
                "timestamp",
                "task_index",
                "episode_index",
                "frame_index",
                "index",
            ]
        ]
        if len(set(lengths)) != 1:
            raise ValueError(
                "All items in LeRobotEpisodeParquet must have the same length."
            )
        return values

    def to_parquet(self, filename: str):
        """
        Save the episode to a Parquet file
        """
        df = pd.DataFrame(self.model_dump())
        # Rename the columns to match the expected names in the Parquet file
        df.rename(columns={"observation_state": "observation.state"}, inplace=True)
        df.to_parquet(filename, index=False)
        logger.debug(f"Wrote {df.shape[0]} rows dataset to {filename}")


class Dataset:
    """
    Handle common dataset operations. Useful to manage the dataset.
    """

    episodes: List[Episode]
    metadata: dict = Field(default_factory=dict)
    path: str
    dataset_name: str
    episode_format: Literal["json", "lerobot_v2", "lerobot_v2.1"]
    data_file_extension: str
    # Full path to the dataset folder
    folder_full_path: Path

    def __init__(self, path: str, enforce_path: bool = True) -> None:
        """
        Load an existing dataset.
        """
        # Check path format
        path_obj = Path(path)
        path_parts = path_obj.parts
        if enforce_path:
            if len(path_parts) < 2 or path_parts[-2] not in [
                "json",
                "lerobot_v2",
                "lerobot_v2.1",
            ]:
                raise ValueError("Wrong dataset path provided.")

        self.path = str(path_obj)
        self.episodes = []
        self.dataset_name = path_parts[-1]
        self.episode_format = cast(
            Literal["json", "lerobot_v2", "lerobot_v2.1"], path_parts[-2]
        )
        self.folder_full_path = path_obj
        self.data_file_extension = "json" if path_parts[-2] == "json" else "parquet"
        self.HF_API = HfApi(token=get_hf_token())

        # Validate dataset name
        if not Dataset.check_dataset_name(self.dataset_name):
            raise ValueError(
                "Dataset name contains invalid characters. Should not contain spaces or /"
            )

        # Check that the dataset folder exists
        if not os.path.exists(self.folder_full_path):
            raise ValueError(f"Dataset folder {self.folder_full_path} does not exist")

    @classmethod
    def check_dataset_name(cls, name: str) -> bool:
        """Validate dataset name format"""
        return " " not in name and "/" not in name

    @classmethod
    def consolidate_dataset_name(cls, name: str) -> str:
        """
        Check if the dataset name is valid.
        To be valid, the dataset name must be a string without spaces, /, or -.

        If not we replace them with underscores.
        """
        if not cls.check_dataset_name(name):
            logger.warning(
                "Dataset name contains invalid characters. Replacing them with underscores."
            )
            name.replace(" ", "_").replace("/", "_").replace("-", "_")

        return name

    @classmethod
    def remove_ds_store_files(cls, folder_path: str):
        try:
            # Iterate through all items in the folder
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)

                # If item is a .DS_Store file, remove it
                if item == ".DS_Store":
                    os.remove(item_path)
                    continue

                # If item is a directory, recurse into it
                if os.path.isdir(item_path):
                    cls.remove_ds_store_files(item_path)

        except (PermissionError, OSError):
            pass

    def get_episode_data_path(self, episode_id: int) -> str:
        """Get the full path to the data with episode id"""
        if self.episode_format == "json":
            return str(
                os.path.join(
                    os.path.dirname(self.folder_full_path),
                    f"episode_{episode_id:06d}.{self.data_file_extension}",
                )
            )
        else:
            return os.path.join(
                self.folder_full_path,
                "data",
                "chunk-000",
                f"episode_{episode_id:06d}.{self.data_file_extension}",
            )

    @property
    def meta_folder_full_path(self) -> str:
        """Get the folder path of the dataset"""
        return str(self.folder_full_path / "meta")

    @property
    def data_folder_full_path(self) -> str:
        """Get the full path to the data folder"""
        return str(self.folder_full_path / "data" / "chunk-000")

    @property
    def videos_folder_full_path(self) -> str:
        """Get the full path to the videos folder"""
        return str(self.folder_full_path / "videos" / "chunk-000")

    def get_df_episode(self, episode_id: int) -> pd.DataFrame:
        """Get the episode data as a pandas DataFrame"""
        if self.episode_format.startswith("lerobot"):
            logger.debug(f"Loading episode {episode_id} from parquet file")
            logger.debug(f"Episode data path: {self.get_episode_data_path(episode_id)}")
            return pd.read_parquet(self.get_episode_data_path(episode_id))
        elif self.episode_format == "json":
            return pd.read_json(self.get_episode_data_path(episode_id))
        else:
            raise NotImplementedError(
                f"Episode format {self.episode_format} not supported"
            )

    @property
    def repo_id(self) -> str:
        """
        Return the huggingface repository id
        """
        repo_id = f"{get_hf_username_or_orgid()}/{self.dataset_name}"
        return repo_id

    def check_repo_exists(self, repo_id: str | None) -> bool:
        """Check if a repository exists on Hugging Face"""
        repo_id = repo_id or self.repo_id
        return self.HF_API.repo_exists(repo_id=repo_id, repo_type="dataset")

    def get_episode_data_path_in_repo(self, episode_id: int) -> str:
        """Get the full path to the data with episode id in the repository"""
        return (
            f"data/chunk-000/episode_{episode_id:06d}.{self.data_file_extension}"
            if self.episode_format.startswith("lerobot")
            else f"episode_{episode_id:06d}.{self.data_file_extension}"
        )

    def sync_local_to_hub(self):
        """Reupload the dataset folder to Hugging Face"""
        username_or_orgid = get_hf_username_or_orgid()
        if username_or_orgid is None:
            logger.warning(
                "No Hugging Face token found. Please add a token in the Admin page.",
            )
            return

        repository_exists = self.HF_API.repo_exists(
            repo_id=self.repo_id, repo_type="dataset"
        )

        # If the repository does not exist, push the dataset to Hugging Face
        if not repository_exists:
            self.push_dataset_to_hub()

        # else, Delete the folders and reupload the dataset.
        else:
            # Delete the dataset folders from Hugging Face
            try:
                delete_folder(
                    repo_id=self.repo_id, path_in_repo="./data", repo_type="dataset"
                )
            except Exception:
                logger.debug("No data folder to delete")
            try:
                delete_folder(
                    repo_id=self.repo_id, path_in_repo="./videos", repo_type="dataset"
                )
            except Exception:
                logger.debug("No videos folder to delete")
            try:
                delete_folder(
                    repo_id=self.repo_id, path_in_repo="./meta", repo_type="dataset"
                )
            except Exception:
                logger.debug("No meta folder to delete")
            # Reupload the dataset folder to Hugging Face
            self.HF_API.upload_folder(
                folder_path=self.folder_full_path,
                repo_id=self.repo_id,
                repo_type="dataset",
            )

    def delete(self) -> None:
        """Delete the dataset from the local folder and Hugging Face"""
        # Delete locally
        if not os.path.exists(self.folder_full_path):
            logger.error(f"Dataset not found in {self.folder_full_path}")
            return

        # Remove the data file if confirmation is correct
        if os.path.isdir(self.folder_full_path):
            shutil.rmtree(self.folder_full_path)
            logger.success(f"Dataset deleted: {self.folder_full_path}")
        else:
            logger.error(f"The Dataset is a file: {self.folder_full_path}")

        # Remove the dataset from Hugging Face
        if self.check_repo_exists(self.repo_id):
            delete_repo(repo_id=self.repo_id, repo_type="dataset")

    def reindex_episodes(
        self,
        folder_path: str,
        nb_steps_deleted_episode: int = 0,
        old_index_to_new_index: Optional[Dict[int, int]] = None,
    ) -> Dict[int, int]:
        """
        Reindex the episode after removing one.
        This is used for videos or for parquet file

        Parameters:
        -----------
        folder_path: str
            The path to the folder where the episodes data or videos are stored. May be users/Downloads/dataset_name/data/chunk-000/
            or  users/Downloads/dataset_name/videos/chunk-000/observation.main_image.right
        nb_steps_deleted_episode: int
            The number of steps deleted in the episode
        old_index_to_new_index: Optional[Dict[int, int]]
            A dictionary mapping old indices to new indices. If None, the function will create a new mapping.

        Returns:
        --------
        Dict[int, int]
            A dictionary mapping old indices to new indices.

        Example:
        --------
        episodes in data are [episode_000000.parquet, episode_000001.parquet, episode_000003.parquet] after we removed episode_000002.parquet
        the result will be [episode_000000.parquet, episode_000001.parquet, episode_000002.parquet]
        """

        # Create a mapping of old index to new index
        if old_index_to_new_index is None:
            old_index_to_new_index = {}
            current_new_index_max = 0

            for filename in sorted(os.listdir(folder_path)):
                if filename.startswith("episode_"):
                    # Check the episode files and extract the index
                    # Also extract the file extension
                    file_extension = filename.split(".")[-1]
                    old_index = int(filename.split("_")[-1].split(".")[0])
                    old_index_to_new_index[old_index] = current_new_index_max
                    current_new_index_max += 1
            current_new_index_max = max(old_index_to_new_index.values()) + 1
        else:
            current_new_index_max = 0

        logger.debug(f"old_index_to_new_index: {old_index_to_new_index}")

        # Reindex the files in the folder
        total_nb_steps = 0
        for filename in sorted(os.listdir(folder_path)):
            if filename.startswith("episode_"):
                file_extension = filename.split(".")[-1]

                old_index = int(filename.split("_")[-1].split(".")[0])
                if old_index in old_index_to_new_index.keys():
                    new_index = old_index_to_new_index[old_index]
                else:
                    # If the file is not in the mapping, we need to create a new index
                    new_index = current_new_index_max
                    current_new_index_max += 1

                new_filename = f"episode_{new_index:06d}.{file_extension}"
                os.rename(
                    os.path.join(folder_path, filename),
                    os.path.join(folder_path, new_filename),
                )

                # Update the episode index inside the parquet file
                if file_extension == "parquet":
                    assert nb_steps_deleted_episode > 0, "Received 0 step deleted"
                    # Read the parquet file
                    df = pd.read_parquet(os.path.join(folder_path, new_filename))
                    # Use the mapping to update the episode index
                    df["episode_index"] = df["episode_index"].replace(
                        old_index_to_new_index
                    )
                    logger.debug(
                        f"Updating episode index in {new_filename}: {df['episode_index']}"
                    )
                    # Replace the global index (total number of steps in the dataset)
                    # First, make it from zero to the total number of rows
                    df["index"] = np.arange(len(df))
                    # Then, add the total number of steps in the dataset to the index
                    df["index"] = df["index"] + total_nb_steps
                    # Update the total number of steps
                    total_nb_steps += len(df)
                    # Save the updated parquet file
                    df.to_parquet(os.path.join(folder_path, new_filename))

                if file_extension == "json":
                    # Update the episode index inside the json file with pandas
                    df = pd.read_json(os.path.join(folder_path, new_filename))
                    df["episode_index"] = df["episode_index"].replace(
                        old_index_to_new_index
                    )
                    df.to_json(os.path.join(folder_path, new_filename))

        return old_index_to_new_index

    def delete_episode(self, episode_id: int, update_hub: bool = True) -> None:
        """
        Delete the episode data from the dataset.
        If format is lerobot, also delete the episode videos from the dataset
        and updates the meta data.
        JSON format not supported

        If update_hub is True, also delete the episode data from the Hugging Face repository
        """

        episode_to_delete = Episode.load(
            self.get_episode_data_path(episode_id), format=self.episode_format
        )
        # Get the full path to the data with episode id

        if self.episode_format == "lerobot_v2.0":
            raise NotImplementedError(
                "Episode deletion is not implemented for LeRobot v2.0 format. Please use v2.1 format."
            )

        if self.check_repo_exists(self.repo_id) is False:
            logger.warning(
                f"Repository {self.repo_id} does not exist on Hugging Face. Skipping deletion on Hugging Face"
            )
            update_hub = False

        logger.info(
            f"Deleting episode {episode_id} from dataset {self.dataset_name} with episode format {self.episode_format}"
        )

        if self.episode_format.startswith("lerobot"):
            # Start loading current meta data
            info_model = InfoModel.from_json(
                meta_folder_path=self.meta_folder_full_path
            )
            tasks_model = TasksModel.from_jsonl(
                meta_folder_path=self.meta_folder_full_path
            )
            episodes_model = EpisodesModel.from_jsonl(
                meta_folder_path=self.meta_folder_full_path,
                format=cast(Literal["lerobot_v2", "lerobot_v2.1"], self.episode_format),
            )
            if info_model.codebase_version == "v2.1":
                episodes_stats_model = EpisodesStatsModel.from_jsonl(
                    meta_folder_path=self.meta_folder_full_path
                )
            elif info_model.codebase_version == "v2.0":
                stats_model = StatsModel.from_json(
                    meta_folder_path=self.meta_folder_full_path
                )
            else:
                raise NotImplementedError(
                    f"Codebase version {info_model.codebase_version} not supported, should be v2.1 or v2.0"
                )

            # Update meta data before episode removal
            try:
                episode_parquet = episode_to_delete.parquet()
            except FileNotFoundError as e:
                logger.warning(f"Episode {episode_id} not found: {e}")
                episode_parquet = pd.DataFrame()
            tasks_model.update_for_episode_removal(
                df_episode_to_delete=episode_parquet,
                data_folder_full_path=self.data_folder_full_path,
            )
            tasks_model.save(meta_folder_path=self.meta_folder_full_path)
            logger.info("Tasks model updated")

            info_model.update_for_episode_removal(
                df_episode_to_delete=episode_parquet,
            )
            info_model.save(meta_folder_path=self.meta_folder_full_path)
            logger.info("Info model updated")

            # Delete the actual episode files (parquet and mp4 video)
            episode_to_delete.delete(update_hub=update_hub)

            # Rename the remaining episodes to keep the numbering consistent
            # be sure to reindex AFTER deleting the episode data
            old_index_to_new_index = self.reindex_episodes(
                nb_steps_deleted_episode=len(episode_to_delete.steps),
                folder_path=self.data_folder_full_path,
            )
            # Reindex the episode videos
            for camera_folder_full_path in self.get_camera_folders_full_paths():
                self.reindex_episodes(
                    folder_path=camera_folder_full_path,
                    old_index_to_new_index=old_index_to_new_index,  # type: ignore
                )

            episodes_model.update_for_episode_removal(
                episode_to_delete_index=episode_id,
                old_index_to_new_index=old_index_to_new_index,
            )
            episodes_model.save(
                meta_folder_path=self.meta_folder_full_path, save_mode="overwrite"
            )
            logger.info("Episodes model updated")

            if info_model.codebase_version == "v2.1":
                episodes_stats_model.update_for_episode_removal(
                    episode_to_delete_index=episode_id,
                    old_index_to_new_index=old_index_to_new_index,
                )
                episodes_stats_model.save(meta_folder_path=self.meta_folder_full_path)
                logger.info("Episodes stats model updated")
            elif info_model.codebase_version == "v2.0":
                # Update for episode removal is not implemented
                stats_model.update_for_episode_removal(
                    data_folder_path=self.data_folder_full_path,
                )
                stats_model.save(meta_folder_path=self.meta_folder_full_path)
                logger.info("Stats model updated")

            if update_hub:
                upload_folder(
                    folder_path=self.meta_folder_full_path,
                    repo_id=self.repo_id,
                    repo_type="dataset",
                    path_in_repo="meta",
                )

    def get_camera_folders_full_paths(self) -> List[str]:
        """
        Return the full path to the camera folders.
        This contains episode_000000.mp4, episode_000001.mp4, etc.
        """
        if self.episode_format == "json":
            raise ValueError("This method is only available for LeRobot datasets")
        return [
            os.path.join(self.videos_folder_full_path, camera_name)
            for camera_name in os.listdir(self.videos_folder_full_path)
        ]

    def get_camera_folders_repo_paths(self) -> List[str]:
        """
        Return the path to the camera folder in the repository
        """
        return [
            f"videos/chunk-000/{camera_name}"
            for camera_name in os.listdir(self.videos_folder_full_path)
        ]

    def get_total_frames(self) -> int:
        """
        Return the total number of frames in the dataset
        """
        return sum(len(episode.steps) for episode in self.episodes)

    def get_robot_types(self) -> str:
        """
        Return in one string the robot types used in the dataset
        """
        unique_robot_types = set(
            episode.metadata.get("robot_type") for episode in self.episodes
        )
        # Concatenate all the robot types in a string
        return ", ".join(
            str(robot) for robot in unique_robot_types if robot is not None
        )

    def get_observation_state_shape(self) -> tuple:
        """
        Check that the dataset has the same observation shape for all states and return it
        """
        unique_shapes = set(
            episode.steps[0].observation.state.shape for episode in self.episodes
        )
        if len(unique_shapes) > 1:
            raise ValueError(
                f"Dataset has multiple observation shapes: {unique_shapes}"
            )
        return unique_shapes.pop()

    def get_images_shape(self) -> tuple:
        """
        Check that all the images have the same shape and return it
        """
        unique_shapes = set(
            step.observation.main_image.shape
            for episode in self.episodes
            for step in episode.steps
        )
        if len(unique_shapes) > 1:
            raise ValueError(f"Dataset has multiple image shapes: {unique_shapes}")
        return unique_shapes.pop()

    def get_joints_position_shape(self) -> tuple:
        """
        Check that the dataset has the same observation.joint_positions shape for all episodes
        Return the shape of the observation main image
        """
        unique_shapes = set(
            step.observation.joints_position.shape
            for episode in self.episodes
            for step in episode.steps
        )

        if len(unique_shapes) > 1:
            raise ValueError(
                f"Dataset has multiple observation.joint_positions shapes: {unique_shapes}"
            )
        return unique_shapes.pop()

    def get_average_fps(self) -> float:
        """
        Return the average FPS of the dataset
        """
        # Calculate FPS for each episode
        episode_fps = []
        for episode in self.episodes:
            timestamps = np.array(
                [step.observation.timestamp for step in episode.steps]
            )
            if (
                len(timestamps) > 1
            ):  # Ensure we have at least 2 timestamps to calculate diff
                fps = 1 / np.mean(np.diff(timestamps))
                episode_fps.append(fps)

        return np.mean(episode_fps)

    def generate_read_me_string(self, dataset_name: str) -> str:
        """
        Generate a README string for the dataset.
        This is used to create the README file in the dataset folder.
        """
        return f"""
---
tags:
- phosphobot
- so100
- phospho-dk
task_categories:
- robotics                                                   
---

# {dataset_name}

**This dataset was generated using a [phospho starter pack](https://robots.phospho.ai).**

This dataset contains a series of episodes recorded with a robot and multiple cameras. \
It can be directly used to train a policy using imitation learning. \
It's compatible with LeRobot and RLDS.
"""

    def push_dataset_to_hub(self, branch_path: str | None = None):
        """
        Push the dataset to the Hugging Face Hub.

        Args:
            branch_path (str, optional): Additional branch to push to besides main
        """
        try:
            # Initialize HF API with token

            # Try to get username/org ID from token
            username_or_org_id = None
            try:
                # Get user info from token
                user_info = self.HF_API.whoami()
                username_or_org_id = parse_hf_username_or_orgid(user_info)

                if not username_or_org_id:
                    logger.error("Could not get username or org ID from token")
                    return

            except Exception as e:
                logger.warning(
                    "No user or org with write access found. Won't be able to push to Hugging Face."
                )
                return

            # Create README if it doesn't exist
            readme_path = os.path.join(self.folder_full_path, "README.md")
            if not os.path.exists(readme_path):
                with open(
                    readme_path, "w", encoding=DEFAULT_FILE_ENCODING
                ) as readme_file:
                    readme_file.write(self.generate_read_me_string(self.dataset_name))

            # Construct full repo name
            dataset_repo_name = f"{username_or_org_id}/{self.dataset_name}"
            create_2_1_branch = False

            # Check if repo exists, create if it doesn't
            try:
                self.HF_API.repo_info(repo_id=dataset_repo_name, repo_type="dataset")
                logger.info(f"Repository {dataset_repo_name} already exists.")
            except Exception:
                logger.info(
                    f"Repository {dataset_repo_name} does not exist. Creating it..."
                )
                create_repo(
                    repo_id=dataset_repo_name,
                    repo_type="dataset",
                    exist_ok=True,
                    token=True,
                )
                logger.info(f"Repository {dataset_repo_name} created.")
                create_2_1_branch = True

            # Push to main branch
            logger.info(
                f"Pushing the dataset to the main branch in repository {dataset_repo_name}"
            )
            self.HF_API.upload_folder(
                folder_path=self.folder_full_path,
                repo_id=dataset_repo_name,
                repo_type="dataset",
            )

            repo_refs = self.HF_API.list_repo_refs(
                repo_id=dataset_repo_name, repo_type="dataset"
            )
            existing_branch_names = [ref.name for ref in repo_refs.branches]

            # Create and push to v2.1 branch if needed
            if create_2_1_branch:
                try:
                    if "v2.1" not in existing_branch_names:
                        logger.info(
                            f"Creating branch v2.1 for dataset {dataset_repo_name}"
                        )
                        create_branch(
                            dataset_repo_name,
                            repo_type="dataset",
                            branch="v2.1",
                            token=True,
                        )
                        logger.info(
                            f"Branch v2.1 created for dataset {dataset_repo_name}"
                        )

                    # Push to v2.1 branch
                    logger.info(
                        f"Pushing the dataset to the branch v2.1 in repository {dataset_repo_name}"
                    )
                    self.HF_API.upload_folder(
                        folder_path=self.folder_full_path,
                        repo_id=dataset_repo_name,
                        repo_type="dataset",
                        revision="v2.1",
                    )
                except Exception as e:
                    logger.error(f"Error handling v2.1 branch: {e}")

            # Push to additional branch if specified
            if branch_path:
                try:
                    if branch_path not in existing_branch_names:
                        logger.info(
                            f"Creating branch {branch_path} for dataset {dataset_repo_name}"
                        )
                        create_branch(
                            dataset_repo_name,
                            repo_type="dataset",
                            branch=branch_path,
                            token=True,
                        )
                        logger.info(
                            f"Branch {branch_path} created for dataset {dataset_repo_name}"
                        )

                    # Push to specified branch
                    logger.info(f"Pushing the dataset to branch {branch_path}")
                    self.HF_API.upload_folder(
                        folder_path=self.folder_full_path,
                        repo_id=dataset_repo_name,
                        repo_type="dataset",
                        revision=branch_path,
                    )
                    logger.info(f"Dataset pushed to branch {branch_path}")
                except Exception as e:
                    logger.error(f"Error handling custom branch: {e}")

        except Exception as e:
            logger.warning(f"An error occurred: {e}")

    def merge_datasets(
        self,
        second_dataset: "Dataset",
        new_dataset_name: str,
        video_transform: dict[str, str],
        check_format: bool = True,
    ) -> None:
        """
        Merge multiple datasets into one.
        This will create a new dataset with the merged data.

        Merge `self` with `second_dataset` and create a new dataset.

        Dataset Structure

        Args:
            second_dataset (Dataset): Dataset to merge with `self`.
            new_dataset_name (str): Name of the folder where the merged dataset
                will be created.
            video_transform (dict[str, str]): Mapping of camera folder names
                from this dataset to the corresponding folders in
                ``second_dataset``. It ensures videos are copied to the correct
                location.

        The resulting dataset will follow this structure:

        / videos
            ├── chunk-000
            │   ├── observation.images.main
            │   |   ├── episode_000000.mp4
            │   ├── observation.images.secondary_0
            │   |   ├── episode_000000.mp4
        / data
            ├── chunk-000
            │   ├── episode_000000.parquet
        / meta
            ├── info.json
            ├── tasks.jsonl
            ├── episodes.jsonl
            ├── episodes_stats.jsonl
        / README.md
        """
        # Check that all datasets have the same format
        if check_format:
            if second_dataset.episode_format != self.episode_format:
                raise ValueError(
                    f"Dataset {second_dataset.dataset_name} has a different format: {second_dataset.episode_format}"
                )

        path_result_dataset = os.path.join(
            os.path.dirname(self.folder_full_path),
            new_dataset_name,
        )
        # If the dataset already exists, raise an error
        if os.path.exists(path_result_dataset):
            raise ValueError(
                f"Dataset {new_dataset_name} already exists in {path_result_dataset}"
            )
        os.makedirs(path_result_dataset, exist_ok=True)

        path_to_videos = os.path.join(
            path_result_dataset,
            "videos",
            "chunk-000",
        )
        os.makedirs(path_to_videos, exist_ok=True)

        ### VIDEOS
        logger.debug("Moving videos to the new dataset")

        # Start by moving videos to the new dataset
        for video_key in video_transform.keys():
            video_folder = video_key
            src_folder = os.path.join(self.videos_folder_full_path, video_folder)
            if os.path.exists(src_folder):
                # Move the video folder to the new dataset
                shutil.copytree(
                    src_folder,
                    os.path.join(path_to_videos, video_folder),
                )

                video_files = [f for f in os.listdir(src_folder) if f.endswith(".mp4")]
                nb_videos = len(video_files)

                # Move the videos from the second dataset to the new dataset and increment the index
                second_video_folder = video_transform[video_key]
                video_folder_full_path = os.path.join(
                    second_dataset.videos_folder_full_path,
                    second_video_folder,
                )
                for video_file in os.listdir(video_folder_full_path):
                    if video_file.endswith(".mp4"):
                        # Get the index of the video
                        video_index = int(video_file.split("_")[-1].split(".")[0])
                        # Rename the video file
                        new_video_file = f"episode_{video_index + nb_videos:06d}.mp4"
                        # Move the video file to the new dataset
                        shutil.copy(
                            os.path.join(video_folder_full_path, video_file),
                            os.path.join(path_to_videos, video_folder, new_video_file),
                        )

        ### META DATA
        logger.debug("Recreating meta files")
        meta_folder_path = os.path.join(path_result_dataset, "meta")
        os.makedirs(meta_folder_path, exist_ok=True)

        #### Tasks Model
        logger.debug("Creating tasks.jsonl")
        initial_tasks = TasksModel.from_jsonl(
            meta_folder_path=self.meta_folder_full_path
        )
        second_tasks = TasksModel.from_jsonl(
            meta_folder_path=second_dataset.meta_folder_full_path
        )
        tasks_mapping_second_to_first, new_number_of_tasks = initial_tasks.merge_with(
            second_task_model=second_tasks,
            meta_folder_to_save_to=meta_folder_path,
        )

        #### Episodes Model
        logger.debug("Creating episodes.jsonl")
        initial_episodes = EpisodesModel.from_jsonl(
            meta_folder_path=self.meta_folder_full_path,
            format="lerobot_v2.1",
        )
        second_episodes = EpisodesModel.from_jsonl(
            meta_folder_path=second_dataset.meta_folder_full_path,
            format="lerobot_v2.1",
        )
        initial_episodes.merge_with(
            second_episodes_model=second_episodes,
            meta_folder_to_save_to=meta_folder_path,
        )

        #### Info Model
        logger.debug("Creating info.json")

        first_info = InfoModel.from_json(
            meta_folder_path=self.meta_folder_full_path,
            format="lerobot_v2.1",
        )
        second_info = InfoModel.from_json(
            meta_folder_path=second_dataset.meta_folder_full_path,
            format="lerobot_v2.1",
        )

        first_info.merge_with(
            second_info_model=second_info,
            meta_folder_to_save_to=meta_folder_path,
            new_nb_tasks=new_number_of_tasks,
        )

        #### Stats model
        logger.debug("Creating episodes_stats.jsonl")

        first_stats = EpisodesStatsModel.from_jsonl(
            meta_folder_path=self.meta_folder_full_path
        )
        second_stats = EpisodesStatsModel.from_jsonl(
            meta_folder_path=second_dataset.meta_folder_full_path
        )
        first_stats.merge_with(
            second_stats_model=second_stats,
            meta_folder_path=meta_folder_path,
        )

        ### PARQUET FILES
        logger.debug("Moving parquet files to the new dataset")

        # Move the parquet files to the new dataset
        path_to_data = os.path.join(
            path_result_dataset,
            "data",
            "chunk-000",
        )
        os.makedirs(path_to_data, exist_ok=True)
        for parquet_file in os.listdir(self.data_folder_full_path):
            if parquet_file.endswith(".parquet"):
                # Move the parquet file to the new dataset
                shutil.copy(
                    os.path.join(self.data_folder_full_path, parquet_file),
                    os.path.join(path_to_data, parquet_file),
                )

        # Reload the first dataset info model
        first_info = InfoModel.from_json(
            meta_folder_path=self.meta_folder_full_path,
            format="lerobot_v2.1",
        )

        # Move the parquet files from the second dataset to the new dataset and edit them
        # - Rename the parquet file
        # - Update the episode index in the parquet file
        # - Update the index in the parquet file
        # - Update the task index in the parquet file

        for parquet_file in os.listdir(second_dataset.data_folder_full_path):
            if parquet_file.endswith(".parquet"):
                # Get the index of the parquet file
                parquet_index = int(parquet_file.split("_")[-1].split(".")[0])
                # Rename the parquet file
                new_parquet_file = (
                    f"episode_{parquet_index + first_info.total_episodes:06d}.parquet"
                )
                # Move the parquet file to the new dataset
                shutil.copy(
                    os.path.join(second_dataset.data_folder_full_path, parquet_file),
                    os.path.join(path_to_data, new_parquet_file),
                )

                # Load the parquet file
                df = pd.read_parquet(
                    os.path.join(path_to_data, new_parquet_file),
                )

                df["episode_index"] = df["episode_index"] + first_info.total_episodes
                df["task_index"] = df["task_index"].replace(
                    tasks_mapping_second_to_first,
                )
                df["index"] = df["index"] + first_info.total_frames

                # Save the parquet file
                df.to_parquet(
                    os.path.join(path_to_data, new_parquet_file),
                )

        # Create README file
        logger.debug("Creating README file")
        readme_path = os.path.join(path_result_dataset, "README.md")
        if not os.path.exists(readme_path):
            with open(readme_path, "w", encoding=DEFAULT_FILE_ENCODING) as readme_file:
                readme_file.write(self.generate_read_me_string(new_dataset_name))

        logger.info(f"Dataset {new_dataset_name} created successfully")

    def split_dataset(
        self, split_ratio: float, first_split_name: str, second_split_name: str
    ) -> None:
        """
        Split the dataset into two parts based on a given ratio.
        This will create two new datasets with the split data.
        The first dataset will contain split ratio of the original dataset,
        split_ratio should be between 0 and 1

        Note: This method is intended to work for v2.1 format only.

        Dataset Structure

        / videos
            ├── chunk-000
            │   ├── observation.images.main
            │   |   ├── episode_000000.mp4
            │   ├── observation.images.secondary_0
            │   |   ├── episode_000000.mp4
        / data
            ├── chunk-000
            │   ├── episode_000000.parquet
        / meta
            ├── info.json
            ├── tasks.jsonl
            ├── episodes.jsonl
            ├── episodes_stats.jsonl
        / README.md
        """
        if split_ratio <= 0 or split_ratio >= 1:
            raise ValueError(f"Split ratio {split_ratio} should be between 0 and 1")

        first_dataset_path = os.path.join(
            os.path.dirname(self.folder_full_path),
            first_split_name,
        )
        second_split_name_path = os.path.join(
            os.path.dirname(self.folder_full_path),
            second_split_name,
        )
        # If the dataset already exists, raise an error
        if os.path.exists(first_dataset_path):
            raise ValueError(
                f"Dataset {first_split_name} already exists in {first_dataset_path}"
            )
        if os.path.exists(second_split_name_path):
            raise ValueError(
                f"Dataset {second_split_name} already exists in {second_split_name_path}"
            )
        os.makedirs(first_dataset_path, exist_ok=True)
        os.makedirs(second_split_name_path, exist_ok=True)

        ### Find number of episodes

        path_to_data = os.path.join(
            self.folder_full_path,
            "data",
            "chunk-000",
        )
        nbr_of_episodes = len(
            [
                f
                for f in os.listdir(path_to_data)
                if f.endswith(".parquet") and f.startswith("episode_")
            ]
        )

        first_dataset_number_of_episodes = int(nbr_of_episodes * split_ratio)
        second_dataset_number_of_episodes = (
            nbr_of_episodes - first_dataset_number_of_episodes
        )
        logger.debug(
            f"Splitting dataset {self.dataset_name} into {first_split_name}: {first_dataset_number_of_episodes} and {second_split_name}: {second_dataset_number_of_episodes}"
        )

        ### VIDEOS
        logger.debug("Spliting videos")
        first_dataset_videos_path = os.path.join(
            first_dataset_path,
            "videos",
            "chunk-000",
        )
        os.makedirs(first_dataset_videos_path, exist_ok=True)
        second_dataset_videos_path = os.path.join(
            second_split_name_path,
            "videos",
            "chunk-000",
        )
        os.makedirs(second_dataset_videos_path, exist_ok=True)

        # Grab videos and move them
        for video_folder in os.listdir(self.videos_folder_full_path):
            if "image" in video_folder:
                # find all videos and sort them by name
                video_folder_full_path = os.path.join(
                    self.videos_folder_full_path, video_folder
                )
                video_files = [
                    f for f in os.listdir(video_folder_full_path) if f.endswith(".mp4")
                ]
                video_files.sort()
                # Split the videos into two parts
                first_dataset_video_files = video_files[
                    :first_dataset_number_of_episodes
                ]
                second_dataset_video_files = video_files[
                    first_dataset_number_of_episodes : first_dataset_number_of_episodes
                    + second_dataset_number_of_episodes
                ]
                # Move the video filed to the new dataset and rename the second ones
                os.makedirs(
                    os.path.join(first_dataset_videos_path, video_folder),
                    exist_ok=True,
                )
                for video_file in first_dataset_video_files:
                    # Move the video file to the new dataset
                    shutil.copy(
                        os.path.join(video_folder_full_path, video_file),
                        os.path.join(
                            first_dataset_videos_path,
                            video_folder,
                            video_file,
                        ),
                    )

                os.makedirs(
                    os.path.join(second_dataset_videos_path, video_folder),
                    exist_ok=True,
                )
                for video_file in second_dataset_video_files:
                    # Get the index of the video
                    video_index = (
                        int(video_file.split("_")[-1].split(".")[0])
                        - first_dataset_number_of_episodes
                    )
                    # Rename the video file
                    new_video_file = f"episode_{video_index:06d}.mp4"
                    # Move the video file to the new dataset
                    shutil.copy(
                        os.path.join(video_folder_full_path, video_file),
                        os.path.join(
                            second_dataset_videos_path,
                            video_folder,
                            new_video_file,
                        ),
                    )

        ### META FILES
        logger.debug("Creating meta files")
        first_meta_folder_path = os.path.join(first_dataset_path, "meta")
        second_meta_folder_path = os.path.join(second_split_name_path, "meta")
        os.makedirs(first_meta_folder_path, exist_ok=True)
        os.makedirs(second_meta_folder_path, exist_ok=True)

        #### episodes.jsonl
        logger.debug("Creating episodes.jsonl")

        initial_episodes = EpisodesModel.from_jsonl(
            meta_folder_path=self.meta_folder_full_path,
            format="lerobot_v2.1",
        )
        first_episodes_model, second_episodes_model = initial_episodes.split(
            split_ratio=split_ratio
        )
        first_episodes_model.save(
            meta_folder_path=first_meta_folder_path,
            save_mode="overwrite",
        )
        second_episodes_model.save(
            meta_folder_path=second_meta_folder_path,
            save_mode="overwrite",
        )

        #### episodes_stats.jsonl
        logger.debug("Creating episodes_stats.jsonl")

        initial_stats = EpisodesStatsModel.from_jsonl(
            meta_folder_path=self.meta_folder_full_path
        )
        first_episodes_stats_model, second_episodes_stats_model = initial_stats.split(
            split_ratio=split_ratio,
        )
        first_episodes_stats_model.save(
            meta_folder_path=first_meta_folder_path,
        )
        second_episodes_stats_model.save(
            meta_folder_path=second_meta_folder_path,
        )

        #### tasks.jsonl
        logger.debug("Creating tasks.jsonl")

        initial_tasks = TasksModel.from_jsonl(
            meta_folder_path=self.meta_folder_full_path
        )
        # Reload episodes to make sure we haven't modified them
        initial_episodes = EpisodesModel.from_jsonl(
            meta_folder_path=self.meta_folder_full_path,
            format="lerobot_v2.1",
        )
        (
            first_tasks,
            second_tasks,
            first_dataset_number_of_tasks,
            second_dataset_number_of_tasks,
            old_task_mapping_to_new,
        ) = initial_tasks.split(
            split_ratio=split_ratio, initial_episodes_model=initial_episodes
        )
        first_tasks.save(
            meta_folder_path=first_meta_folder_path,
        )
        second_tasks.save(
            meta_folder_path=second_meta_folder_path,
        )

        ### PARQUET FILES
        logger.debug("Spliting parquet files")

        first_dataset_data_path = os.path.join(
            first_dataset_path,
            "data",
            "chunk-000",
        )
        os.makedirs(first_dataset_data_path, exist_ok=True)
        second_dataset_data_path = os.path.join(
            second_split_name_path,
            "data",
            "chunk-000",
        )
        os.makedirs(second_dataset_data_path, exist_ok=True)

        # Move the parquet files to the new dataset and rename them
        # List and sort all parquets

        parquet_files = [
            f
            for f in os.listdir(self.data_folder_full_path)
            if f.endswith(".parquet") and f.startswith("episode_")
        ]
        parquet_files.sort()

        index_in_second_dataset = 0
        for parquet_file in parquet_files:
            # Get the index of the parquet file
            parquet_index = int(parquet_file.split("_")[-1].split(".")[0])
            # Rename the parquet file
            new_parquet_file = f"episode_{parquet_index:06d}.parquet"
            # Move the parquet file to the new dataset
            if parquet_index < first_dataset_number_of_episodes:
                shutil.copy(
                    os.path.join(path_to_data, parquet_file),
                    os.path.join(first_dataset_data_path, new_parquet_file),
                )
            else:
                # Rename the parquet file
                new_parquet_file = f"episode_{parquet_index - first_dataset_number_of_episodes:06d}.parquet"
                shutil.copy(
                    os.path.join(path_to_data, parquet_file),
                    os.path.join(second_dataset_data_path, new_parquet_file),
                )
                # Load parquet file
                df = pd.read_parquet(
                    os.path.join(second_dataset_data_path, new_parquet_file),
                )
                # Update the episode index in the parquet file
                df["episode_index"] = (
                    df["episode_index"] - first_dataset_number_of_episodes
                )
                # Update the index in the parquet file
                df["index"] = np.arange(len(df)) + index_in_second_dataset
                # Update the task index in the parquet file
                df["task_index"] = df["task_index"].replace(
                    old_task_mapping_to_new,
                )
                index_in_second_dataset += len(df)
                # Save the parquet file
                df.to_parquet(
                    os.path.join(second_dataset_data_path, new_parquet_file),
                )

        #### info.json
        # We create the info files last, because we need info from the other files
        logger.debug("Creating info.json")

        initial_info = InfoModel.from_json(
            meta_folder_path=self.meta_folder_full_path,
            format="lerobot_v2.1",
        )
        number_of_cameras = initial_info.total_videos // initial_info.total_episodes

        first_info = InfoModel.from_json(
            meta_folder_path=self.meta_folder_full_path,
            format="lerobot_v2.1",
        )
        first_info.total_episodes = first_dataset_number_of_episodes
        first_info.total_frames = initial_info.total_frames - index_in_second_dataset
        first_info.total_tasks = first_dataset_number_of_tasks
        first_info.splits = {
            "train": f"0:{first_dataset_number_of_episodes}",
        }
        first_info.total_videos = first_dataset_number_of_episodes * number_of_cameras

        second_info = InfoModel.from_json(
            meta_folder_path=self.meta_folder_full_path,
            format="lerobot_v2.1",
        )
        second_info.total_episodes = second_dataset_number_of_episodes
        second_info.total_frames = index_in_second_dataset
        second_info.total_tasks = second_dataset_number_of_tasks
        second_info.splits = {
            "train": f"{0}:{second_dataset_number_of_episodes}",
        }
        second_info.total_videos = second_dataset_number_of_episodes * number_of_cameras
        first_info.save(
            meta_folder_path=first_meta_folder_path,
        )
        second_info.save(
            meta_folder_path=second_meta_folder_path,
        )

        #### Create README.md files
        logger.debug("Creating README.md files")

        first_readme_path = os.path.join(first_dataset_path, "README.md")
        if not os.path.exists(first_readme_path):
            with open(
                first_readme_path,
                "w",
                encoding=DEFAULT_FILE_ENCODING,
            ) as readme_file:
                readme_file.write(self.generate_read_me_string(first_split_name))
        second_readme_path = os.path.join(second_split_name_path, "README.md")
        if not os.path.exists(second_readme_path):
            with open(
                second_readme_path,
                "w",
                encoding=DEFAULT_FILE_ENCODING,
            ) as readme_file:
                readme_file.write(self.generate_read_me_string(second_split_name))

        logger.info(
            f"Dataset {self.dataset_name} split into {first_split_name} and {second_split_name} successfully"
        )

    def delete_video_keys(self, video_keys_to_delete: List[str]) -> None:
        """
        Delete the video keys from the dataset.
        Will update the info.json file and delete the videos from the data folder.

        video_keys_to_delete are of the form "observation.images.{video_key}"
        """
        # Step 1: update the info.json file
        info = InfoModel.from_json(
            meta_folder_path=self.meta_folder_full_path,
            format="lerobot_v2.1",
        )
        # This method save also the info.json file
        info.update_for_video_removal(video_keys_to_delete, self.meta_folder_full_path)

        # Step 2: delete the videos from the data folder
        for video_key in video_keys_to_delete:
            video_folder = os.path.join(self.videos_folder_full_path, video_key)
            if os.path.exists(video_folder):
                shutil.rmtree(video_folder)

        # Step 3: update the stats.jsonl file
        stats = StatsModel.from_json(self.meta_folder_full_path)
        stats.update_for_video_key_removal(
            video_keys_to_delete, self.meta_folder_full_path
        )

    def shuffle_dataset(self, new_dataset_name) -> None:
        """
        Shuffle the episodes in the dataset.
        Expects a dataset in v2.1 format.
        This will pick a random shuffle of the episodes and apply it to the videos, data and meta files.
        """
        if self.episode_format != "lerobot_v2.1":
            raise ValueError(
                f"Dataset {self.dataset_name} is not in v2.1 format, cannot shuffle"
            )

        # Create a new dataset folder in the parent folder of the current dataset
        new_dataset_path = os.path.join(
            os.path.dirname(os.path.dirname(self.folder_full_path)),
            new_dataset_name,
        )

        # If the dataset already exists, raise an error
        if os.path.exists(new_dataset_path):
            raise ValueError(
                f"Dataset {new_dataset_name} already exists in {new_dataset_path}"
            )

        # Find the number of episodes in the dataset
        logger.info("Shuffling the dataset episodes")
        path_to_data = self.data_folder_full_path
        parquet_files = [
            f
            for f in os.listdir(path_to_data)
            if f.endswith(".parquet") and f.startswith("episode_")
        ]
        if not parquet_files:
            raise ValueError(
                f"No parquet files found in {path_to_data}. Is this a valid dataset?"
            )
        number_of_episodes = len(parquet_files)
        shuffle = np.random.permutation(number_of_episodes)

        ### Data
        logger.debug("Shuffling data files")
        os.makedirs(os.path.join(new_dataset_path, "data", "chunk-000"), exist_ok=True)

        for parquet_file in parquet_files:
            # Get the index of the parquet file
            parquet_index = int(parquet_file.split("_")[-1].split(".")[0])
            # Rename the parquet file
            new_parquet_file = f"episode_{shuffle[parquet_index]:06d}.parquet"
            # Move the parquet file to the new dataset
            shutil.copy(
                os.path.join(path_to_data, parquet_file),
                os.path.join(new_dataset_path, "data", "chunk-000", new_parquet_file),
            )

        # Repair datasets
        old_to_new = {k: int(v) for k, v in enumerate(shuffle)}
        self.reindex_episodes(
            folder_path=new_dataset_path, old_index_to_new_index=old_to_new
        )

        ### Videos

        logger.debug("Shuffling video files")
        path_to_videos = os.path.join(new_dataset_path, "videos", "chunk-000")
        os.makedirs(path_to_videos, exist_ok=True)

        for video_folder in os.listdir(self.videos_folder_full_path):
            if "image" in video_folder:
                os.makedirs(os.path.join(path_to_videos, video_folder), exist_ok=True)
                # Move the video folder to the new dataset
                video_folder_full_path = os.path.join(
                    self.videos_folder_full_path, video_folder
                )
                video_files = [
                    f for f in os.listdir(video_folder_full_path) if f.endswith(".mp4")
                ]
                # Sort the videos by name
                video_files.sort()

                # Move the videos from the second dataset to the new dataset and increment the index
                for video_file in video_files:
                    # Get the index of the video
                    video_index = int(video_file.split("_")[-1].split(".")[0])
                    # Rename the video file
                    new_video_file = f"episode_{shuffle[video_index]:06d}.mp4"
                    # Move the video file to the new dataset
                    shutil.copy(
                        os.path.join(video_folder_full_path, video_file),
                        os.path.join(path_to_videos, video_folder, new_video_file),
                    )

        ### Meta files
        logger.debug("Creating meta files")
        os.makedirs(os.path.join(new_dataset_path, "meta"), exist_ok=True)

        #### TASKS
        logger.debug("Copying tasks.json file")
        tasks_model = TasksModel.from_jsonl(
            meta_folder_path=self.meta_folder_full_path,
        )
        # No need to shuffle, just copy
        tasks_model.save(
            meta_folder_path=os.path.join(new_dataset_path, "meta"),
        )

        #### INFO
        logger.debug("Copying info.json file")
        info_model = InfoModel.from_json(
            meta_folder_path=self.meta_folder_full_path,
            format="lerobot_v2.1",
        )
        # No need to shuffle, just copy
        info_model.save(
            meta_folder_path=os.path.join(new_dataset_path, "meta"),
        )

        #### EPISODES
        logger.debug("Shuffling episodes.jsonl file")
        episodes_model = EpisodesModel.from_jsonl(
            meta_folder_path=self.meta_folder_full_path,
            format="lerobot_v2.1",
        )
        episodes_model.shuffle(
            permutation=shuffle,
        )
        episodes_model.save(
            meta_folder_path=os.path.join(new_dataset_path, "meta"),
            save_mode="overwrite",
        )

        #### EPISODES STATS
        logger.debug("Shuffling episodes_stats.jsonl file")
        episodes_stats_model = EpisodesStatsModel.from_jsonl(
            meta_folder_path=self.meta_folder_full_path,
        )
        episodes_stats_model.shuffle(
            permutation=shuffle,
        )
        episodes_stats_model.save(
            meta_folder_path=os.path.join(new_dataset_path, "meta"),
        )

        # Create README file
        logger.debug("Creating README file")
        readme_path = os.path.join(new_dataset_path, "README.md")
        if not os.path.exists(readme_path):
            with open(
                readme_path,
                "w",
                encoding=DEFAULT_FILE_ENCODING,
            ) as readme_file:
                readme_file.write(self.generate_read_me_string(new_dataset_name))


class Stats(BaseModel):
    """
    Statistics for a given feature.
    """

    max: NdArrayAsList | None = None
    min: NdArrayAsList | None = None
    mean: NdArrayAsList | None = None
    std: NdArrayAsList | None = None

    # These values are used for rolling computation of mean and std
    sum: NdArrayAsList | None = None
    square_sum: NdArrayAsList | None = None
    count: int = 0

    @field_validator("count", mode="before")
    @classmethod
    def validate_count(cls, value) -> int:
        if isinstance(value, int):
            return value
        elif isinstance(value, list) and len(value) == 1:
            return value[0]

        raise ValueError(
            f"Count must be an int or a list of length 1, got {type(value)} with length {len(value)}"
        )

    # To be able to use np.array in pydantic, we need to use arbitrary_types_allowed = True
    class Config:
        arbitrary_types_allowed = True
        extra = "allow"

    def update(self, value: np.ndarray | None) -> None:
        """
        Every recording step, update the stats with the new value.
        Note: These are not the final values for mean and std.
        You still neeed to call compute_from_rolling() to get the final values.
        """

        if value is None:
            return None

        # If square_sum is None, use the std to compute the square sum
        if self.square_sum is None and self.std is not None and self.mean is not None:
            self.square_sum = self.std**2 + self.mean**2

        # Update the max and min
        if self.max is None:
            self.max = value
        else:
            self.max = np.maximum(self.max, value)

        if self.min is None:
            self.min = value
        else:
            self.min = np.minimum(self.min, value)

        # Update the rolling sum and square sum
        if self.sum is None or self.square_sum is None:
            # We need to copy the value to avoid modifying the original value
            self.sum = value.copy()
            self.square_sum = value.copy() ** 2
            self.count = 1
        else:
            self.sum = self.sum + value
            self.square_sum = self.square_sum + value**2
            self.count += 1

    def compute_from_rolling(self):
        """
        Compute the mean and std from the rolling sum and square sum.
        """
        if self.count == 0:
            logger.error("Count is 0. Cannot compute mean and std.")
            return

        if self.sum is None or self.square_sum is None:
            # We have already computed the mean and std
            return

        self.mean = self.sum / self.count
        compute_diff = self.square_sum / self.count - self.mean**2
        if (compute_diff < 0).any():
            if (compute_diff < -2).any():
                logger.warning(
                    f"Negative value in the square sum. Replacing the negative values of std with 0.\nsquare_sum={self.square_sum}\ncount={self.count}\nmean={self.mean**2}"
                )
            variance = self.square_sum / self.count - self.mean**2
            variance[variance <= 0] = 0
            self.std = np.sqrt(variance)
        else:
            self.std = np.sqrt(self.square_sum / self.count - self.mean**2)

    def update_image(self, image_value: np.ndarray) -> None:
        """
        Update the stats with the new image.
        The stats are in dim 3 for RGB.
        We normalize with the number of pixels.
        """

        assert image_value.ndim == 3, "Image value must be 3D"

        if image_value is None:
            return None

        # Compute the square sum if not available
        if self.square_sum is None and self.std is not None and self.mean is not None:
            self.square_sum = self.std**2 + self.mean**2

        image_norm_32 = image_value.astype(dtype=np.float32) / 255.0

        # Update the max and min
        if self.max is None:
            self.max = np.max(image_norm_32, axis=(0, 1)).reshape(3, 1, 1)
        else:
            image_max_pixel = np.max(image_norm_32, axis=(0, 1)).reshape(3, 1, 1)
            # maximum is the max in each channel
            self.max = np.maximum(self.max, image_max_pixel)

        if self.min is None:
            self.min = np.min(image_norm_32, axis=(0, 1)).reshape(3, 1, 1)
            # Reshape to have the same shape as the mean and std
            self.min = self.min.reshape(3, 1, 1)
        else:
            image_min_pixel = np.min(image_norm_32, axis=(0, 1)).reshape(3, 1, 1)
            # Set the min to the min in each channel
            self.min = np.minimum(self.min, image_min_pixel)
            # Reshape to have the same shape as the mean and std
            self.min = self.min.reshape(3, 1, 1) if self.min is not None else self.min

        # Update the rolling sum and square sum
        nb_pixels = image_norm_32.shape[0] * image_norm_32.shape[1]
        # Convert to int32 to avoid overflow when computing the square sum
        if self.sum is None or self.square_sum is None:
            self.sum = np.sum(image_norm_32, axis=(0, 1))
            self.square_sum = np.sum(image_norm_32**2, axis=(0, 1))
            self.count = nb_pixels
        else:
            self.sum = self.sum + np.sum(image_norm_32, axis=(0, 1))
            self.square_sum = self.square_sum + np.sum(image_norm_32**2, axis=(0, 1))
            self.count += nb_pixels

    def compute_from_rolling_images(self):
        """
        Compute the mean and std from the rolling sum and square sum for images.
        """
        self.mean = self.sum / self.count
        self.std = np.sqrt(self.square_sum / self.count - self.mean**2)
        # We want .tolist() to yield [[[mean_r, mean_g, mean_b]]] and not [mean_r, mean_g, mean_b]
        # Reshape to have the same shape as the mean and std
        # This makes it easier to normalize the imags
        if self.mean.shape == (3,):
            self.mean = self.mean.reshape(3, 1, 1)
            self.std = self.std.reshape(3, 1, 1)
            # For the first episode the shape is (3,)
            # For the next ones the shape is (3,1,3)
            # We keep min and max of the first episode only
            self.min = self.min.reshape(3, 1, 1)
            self.max = self.max.reshape(3, 1, 1)


class StatsModel(BaseModel):
    """
    Data model utils to create stats.json file.

    Stats for  observation_state and actions are dim the number of joints
    Stats for images are dim 1, 3, 1
    The other stats are dim 1
    """

    observation_state: Stats = Field(
        default_factory=Stats,
        serialization_alias="observation.state",
        validation_alias=AliasChoices("observation.state", "observation_state"),
    )
    action: Stats = Field(default_factory=Stats)
    timestamp: Stats = Field(default_factory=Stats)
    frame_index: Stats = Field(default_factory=Stats)
    episode_index: Stats = Field(default_factory=Stats)
    index: Stats = Field(default_factory=Stats)
    task_index: Stats = Field(default_factory=Stats)

    # key is like: observation.images.main
    # value is Stats of the object: average pixel value, std, min, max ; and shape (height, width, channel)
    observation_images: Dict[str, Stats] = Field(
        default_factory=dict,
        serialization_alias="observation.images",
        validation_alias=AliasChoices(
            "observation.images",
            "observation.image",
            "observation_images",
            "observation_image",
        ),
    )

    @classmethod
    def from_json(cls, meta_folder_path: str) -> "StatsModel":
        """
        Read the stats.json file in the meta folder path.
        If the file does not exist, return an empty StatsModel.
        """
        if (
            not os.path.exists(f"{meta_folder_path}/stats.json")
            or os.stat(f"{meta_folder_path}/stats.json").st_size == 0
        ):
            return cls()

        with open(
            f"{meta_folder_path}/stats.json", "r", encoding=DEFAULT_FILE_ENCODING
        ) as f:
            stats_dict: Dict[str, Stats] = json.load(f)

        # Create a temporary dictionary for observation_images
        observation_images = {}
        # We need to create a list of keys in order not to modify
        # the dictionary while iterating over it
        for key in list(stats_dict.keys()):
            if "image" in key:
                observation_images[key] = stats_dict.pop(key)

        # Pass observation_images into the model constructor
        return cls(**stats_dict, observation_images=observation_images)

    def to_json(self, meta_folder_path: str) -> None:
        """
        Write the stats.json file in the meta folder path.
        """
        model_dict = self.model_dump(by_alias=True)

        # We flatten the fields in the dict observations images
        for key, value in model_dict["observation.images"].items():
            model_dict[key] = value
        model_dict.pop("observation.images")

        with open(
            f"{meta_folder_path}/stats.json", "w", encoding=DEFAULT_FILE_ENCODING
        ) as f:
            # Write the pydantic Basemodel as a str
            f.write(json.dumps(model_dict, indent=4))

    def update(
        self,
        step: Step,
        episode_index: int,
        current_step_index: int,
    ) -> None:
        """
        Updates the stats with the given step.
        """

        self.action.update(
            step.observation.joints_position
        )  # Because action lags behind by one step, we approximate it with the current observation
        self.observation_state.update(step.observation.joints_position)
        self.timestamp.update(np.array([step.observation.timestamp]))
        self.index.update(np.array([self.index.count]))
        self.episode_index.update(np.array([episode_index]))
        self.frame_index.update(np.array([current_step_index]))

        # TODO: Implement multiple language instructions
        # This should be the index of the instruction as it's in tasks.jsonl (TasksModel)
        self.task_index.update(np.array([0]))

        main_image = step.observation.main_image
        if main_image is not None:
            if "observation.images.main" not in self.observation_images.keys():
                # Initialize
                self.observation_images["observation.images.main"] = Stats()
            self.observation_images["observation.images.main"].update_image(main_image)

        for image_index, image in enumerate(step.observation.secondary_images):
            if (
                f"observation.images.secondary_{image_index}"
                not in self.observation_images.keys()
            ):
                # Initialize
                self.observation_images[
                    f"observation.images.secondary_{image_index}"
                ] = Stats()

            self.observation_images[
                f"observation.images.secondary_{image_index}"
            ].update_image(image)

    def save(self, meta_folder_path: str) -> None:
        """
        Save the stats to the meta folder path.
        Also computes the final mean and std for the Stats objects.
        """
        for field_key, field_value in self.__dict__.items():
            # if field is a Stats object, call .compute_from_rolling() to get the final mean and std
            if isinstance(field_value, Stats):
                field_value.compute_from_rolling()

            # Special case for images
            if isinstance(field_value, dict) and field_key == "observation_images":
                for key, value in field_value.items():
                    try:
                        if isinstance(value, Stats):
                            value.compute_from_rolling_images()
                    except ValueError as e:
                        logger.error(f"Error computing mean and std for {key}: {e}")

        self.to_json(meta_folder_path)

    def _update_for_episode_removal_mean_std_count(
        self, df_episode_to_delete: pd.DataFrame
    ) -> None:
        """
        Update the stats before removing an episode from the dataset.
        We do not compute the new min and max.
        We prefer to do it after the episode removal to directly access new indexes and episodes indexes.
        This only updates mean, std, sum, square_sum, and count.
        """
        if df_episode_to_delete.empty:
            return

        # Load the parquet file
        nb_steps_deleted_episode = len(df_episode_to_delete)

        # Remove [nan, nan, ...] arrays from actions and observation.state columns
        df_episode_to_delete = df_episode_to_delete[
            df_episode_to_delete["observation.state"].apply(
                lambda x: not np.all(np.isnan(x))
            )
        ]
        df_episode_to_delete = df_episode_to_delete[
            df_episode_to_delete["action"].apply(lambda x: not np.all(np.isnan(x)))
        ]

        df_sums_squaresums = pd.concat(
            [
                df_episode_to_delete.sum(skipna=True),
                (df_episode_to_delete**2).sum(skipna=True),
            ],
            axis=1,
        )
        df_sums_squaresums = df_sums_squaresums.rename(
            columns={0: "sums", 1: "squaresums"}
        )

        # Update stats for each field in the StatsModel
        for field_name, field in StatsModel.model_fields.items():
            # TODO task_index is not updated since we do not support multiple tasks
            # observation_images has a special treatment
            if field_name in ["task_index", "observation_images"]:
                continue
            field_value = getattr(self, field_name)
            # The key in StatsModel is observation_state
            field_name = (
                "observation.state" if field_name == "observation_state" else field_name
            )
            # Update statistics
            if field_name in df_episode_to_delete.columns:
                # Subtract sums
                logger.debug(f"Field {field_name} sum before: {field_value.sum}")
                field_value.sum = (
                    field_value.sum - df_sums_squaresums["sums"][field_name]
                )
                field_value.square_sum = (
                    field_value.square_sum
                    - df_sums_squaresums["squaresums"][field_name]
                )
                logger.debug(f"Field {field_name} sum after: {field_value.sum}")

                # Update count
                field_value.count = field_value.count - nb_steps_deleted_episode

                # Recalculate mean and standard deviation
                if field_value.count > 0:
                    field_value.mean = field_value.sum / field_value.count
                    variance = (field_value.square_sum / field_value.count) - np.square(
                        field_value.mean
                    )
                    if (isinstance(variance, np.ndarray) and np.all(variance >= 0)) or (
                        isinstance(variance, float) and variance >= 0
                    ):
                        field_value.std = np.sqrt(variance)
                    else:
                        logger.error(
                            f"Field {field_name} variance is negative: {variance}"
                            + f" for episode {df_episode_to_delete['episode_index'].iloc[0]}"
                        )
                else:
                    logger.error(
                        f"Field {field_name} count is 0. Cannot compute mean and std for episode {df_episode_to_delete['episode_index'].iloc[0]}"
                    )

    def get_total_frames(self, meta_folder_path: str) -> int:
        """
        Return the total number of frames in the dataset
        """
        info_path = os.path.join(meta_folder_path, "info.json")
        with open(info_path, "r", encoding=DEFAULT_FILE_ENCODING) as f:
            info_dict = json.load(f)
        return info_dict.get("total_frames", 0)

    def get_images_shapes(self, meta_folder_path: str, camera_key: str) -> List[int]:
        """
        Return the tuple (height, width, channel) of the images for a given camera key
        """
        info_path = os.path.join(meta_folder_path, "info.json")
        with open(info_path, "r", encoding=DEFAULT_FILE_ENCODING) as f:
            info_dict = json.load(f)
        return info_dict["features"][camera_key]["shape"]

    def _compute_count_sum_square_sum_item_from_mean_std(
        self, stats_item: "Stats", stats_key: str, meta_folder_path: str
    ):
        """Helper function to compute sum and square_sum from mean, std, and count
        meta_folder_path is used to compute the count from info.json
        This is the number of frames or the number of frames times the dimension of images for videos
        """
        if stats_item.mean is None or stats_item.std is None:
            raise ValueError(f"Mean and std are not computed for {stats_item}")

        if (
            stats_item.sum is None
            or stats_item.square_sum is None
            or stats_item.count == 0
        ):
            is_video = "image" in stats_key or "video" in stats_key
            # Get the number of frames from info.json
            count = (
                self.get_total_frames(meta_folder_path)
                * self.get_images_shapes(
                    meta_folder_path=meta_folder_path, camera_key=stats_key
                )[0]
                * self.get_images_shapes(
                    meta_folder_path=meta_folder_path, camera_key=stats_key
                )[1]
                if is_video
                else self.get_total_frames(meta_folder_path),
            )[0]
            if is_video:
                logger.debug(f"Mean shape for {stats_key}: {stats_item.mean.shape}")
                logger.debug(f"Count for {stats_key}: {count}")

            mean = stats_item.mean
            std = stats_item.std

            stats_item.count = count
            logger.debug(f"Count for {stats_key}: {count}")
            sum_array = mean * count
            square_sum_array = (std**2 + mean**2) * count

            stats_item.sum = sum_array
            stats_item.square_sum = square_sum_array
            if is_video:
                logger.debug(
                    f"Mean shape for {stats_key} after: {stats_item.mean.shape}"
                )

    def compute_count_square_sum_framecount_from_mean_std(self, meta_folder_path: str):
        """
        Compute the sum and square sum from the mean and std.
        This is useful when we want to update the stats after repairing a dataset.
        """
        # Process all stats fields
        for stats_key, stats_item in self.__dict__.items():
            if stats_key != "observation_images":
                # Process regular stats items
                try:
                    self._compute_count_sum_square_sum_item_from_mean_std(
                        stats_item=stats_item,
                        stats_key=stats_key,
                        meta_folder_path=meta_folder_path,
                    )
                except ValueError as e:
                    raise ValueError(f"{e} for {stats_key}")
            else:
                # Process observation_images items
                for camera_key, video_stats_item in stats_item.items():
                    try:
                        self._compute_count_sum_square_sum_item_from_mean_std(
                            stats_item=video_stats_item,
                            stats_key=camera_key,
                            meta_folder_path=meta_folder_path,
                        )
                    except ValueError as e:
                        raise ValueError(f"{e} for {camera_key}")

    def _update_for_episode_removal_images_stats(
        self,
        folder_videos_path: str,
        episode_to_delete_index: int,
        meta_folder_path: str,
    ) -> None:
        """
        Update the stats for images.

        For every camera, we need to delete the episode_{episode_index:06d}.mp4 file.

        We update the sum, square_sum, and count for each camera.

        We do not update the min and the max here. It is always 0 and 1 by experience
        """

        self.compute_count_square_sum_framecount_from_mean_std(
            meta_folder_path=meta_folder_path
        )

        cameras_folders = os.listdir(folder_videos_path)
        # Only keep directories
        cameras_folders = [
            camera_name
            for camera_name in cameras_folders
            if os.path.isdir(os.path.join(folder_videos_path, camera_name))
        ]
        for camera_name in cameras_folders:
            if "image" not in camera_name:
                continue
            # Create the path of the video episode_{episode_index:06d}.mp4
            video_path = os.path.join(
                folder_videos_path,
                camera_name,  # eg: observation.images.main
                f"episode_{episode_to_delete_index:06d}.mp4",
            )
            sum_array, square_sum_array, nb_pixel = (
                compute_sum_squaresum_framecount_from_video(video_path)
            )

            sum_array = sum_array.astype(np.float32)
            square_sum_array = square_sum_array.astype(np.float32)

            # Update the stats_model for sum square_sum and count
            self.observation_images[camera_name].sum = (
                self.observation_images[camera_name].sum - sum_array
            )
            self.observation_images[camera_name].square_sum = (
                self.observation_images[camera_name].square_sum - square_sum_array
            )
            self.observation_images[camera_name].count = (
                self.observation_images[camera_name].count - nb_pixel
            )
            # Update the stats_model for mean and std
            if (
                self.observation_images[camera_name].sum is not None
                and self.observation_images[camera_name].count
            ):
                mean_val = (
                    np.array(self.observation_images[camera_name].sum)
                    / self.observation_images[camera_name].count
                )
                self.observation_images[camera_name].mean = mean_val
                self.observation_images[camera_name].square_sum = (
                    self.observation_images[camera_name].square_sum
                    - np.square(mean_val)
                )

    def _update_for_episode_removal_min_max(
        self,
        data_folder_path: str,
        meta_folder_path: str,
        episode_to_delete_index: int,
    ) -> None:
        """
        Update the min and max in stats after removing an episode from the dataset.
        Be sure to call this function after reindexing the data.
        """
        self.compute_count_square_sum_framecount_from_mean_std(
            meta_folder_path=meta_folder_path
        )

        # Load all the other parquet files in one dataFrame
        li_data_folder_filenames = [
            file
            for file in os.listdir(data_folder_path)
            if file.endswith(".parquet")
            and file != f"episode_{episode_to_delete_index:06d}.parquet"
        ]
        if len(li_data_folder_filenames) == 0:
            return

        # Load all episodes
        all_episodes = [
            pd.read_parquet(str(os.path.join(data_folder_path, file)))
            for file in li_data_folder_filenames
        ]

        # Combine all episodes
        all_episodes_df = pd.concat(all_episodes)

        for field_name, field in StatsModel.model_fields.items():
            # TODO task_index is not updated since we do not support multiple tasks
            if field_name in ["task_index", "observation_images"]:
                continue
            logger.info(f"Updating field {field_name}")
            # Get the field value from the instance
            field_value = getattr(self, field_name)
            # Convert observation_state to observation.state
            field_name = (
                "observation.state" if field_name == "observation_state" else field_name
            )
            # Update statistics
            if field_name in all_episodes_df.keys():
                (field_value.min, field_value.max) = get_field_min_max(
                    all_episodes_df, field_name
                )
                # The value should be a numpy ndarray, even if it's a int or float
                if not isinstance(field_value.min, np.ndarray):
                    field_value.min = np.array([field_value.min])
                if not isinstance(field_value.max, np.ndarray):
                    field_value.max = np.array([field_value.max])

    def update_for_episode_removal(self, data_folder_path: str) -> None:
        # TODO: Handle everything in one function
        pass

    def update_for_video_key_removal(
        self,
        video_keys_to_delete: List[str],
        meta_folder_path: str,
        stats_file_name: str = "episodes_stats.jsonl",
    ) -> None:
        """
        Update the stats for given video keys to delete.
        No need to recompute as we are just removing a column from the stats.jsonl file.
        """
        # For each line of the stats.jsonl file, we need to delete the columns corresponding to the video keys to delete
        with (
            open(
                f"{meta_folder_path}/{stats_file_name}",
                "r",
                encoding=DEFAULT_FILE_ENCODING,
            ) as f,
            tempfile.NamedTemporaryFile(
                "w", delete=False, encoding=DEFAULT_FILE_ENCODING
            ) as temp,
        ):
            # Process each line
            for line in f:
                # Parse the JSON object from the line
                stats_dict = json.loads(line)
                if "stats" in stats_dict:
                    for video_key in video_keys_to_delete:
                        stats_dict["stats"].pop(video_key, None)
                else:
                    raise ValueError(
                        f"stats_dict does not contain a stats key: {stats_dict}"
                    )
                temp.write(json.dumps(stats_dict) + "\n")

        # Replace the original file with the temporary file
        shutil.move(temp.name, f"{meta_folder_path}/{stats_file_name}")

        logger.debug(
            f"Stats.jsonl file updated for video keys to delete: {video_keys_to_delete}"
        )


class EpisodesStatsFeatutes(BaseModel):
    """
    Features for each line of the episodes_stats.jsonl file.
    """

    episode_index: int = 0
    stats: StatsModel = Field(default_factory=StatsModel)

    def to_json(self) -> str:
        """
        Save the features as a json string.
        """
        # Use the aliases in StatsModel
        model_dict: dict[str, dict] = self.stats.model_dump(
            by_alias=True, warnings=False
        )

        for key, value in model_dict["observation.images"].items():
            model_dict[key] = value
        model_dict.pop("observation.images")

        # Convert count to a list and remove sum and square_sum for compatibility
        for key, value in model_dict.items():
            if isinstance(value["count"], int):
                value["count"] = [value["count"]]
            if "sum" in value.keys():
                value.pop("sum")
            if "square_sum" in value.keys():
                value.pop("square_sum")

        # Add the episode index
        result_dict = {"episode_index": self.episode_index, "stats": model_dict}

        # Convert to JSON string
        return json.dumps(result_dict)


class EpisodesStatsModel(BaseModel):
    """
    Creates the structure of the episodes_stats.jsonl file.
    """

    episodes_stats: List[EpisodesStatsFeatutes] = Field(default_factory=list)

    def update(self, step: Step, episode_index: int, current_step_index: int) -> None:
        """
        Updates the episodes_stats with the given step.
        """
        # Check if the episode index already exists
        if (
            self.episodes_stats != []
            and self.episodes_stats[-1].episode_index == episode_index
        ):
            # Update the stats for the last episode
            self.episodes_stats[-1].stats.update(
                step=step,
                episode_index=episode_index,
                current_step_index=current_step_index,
            )
            return

        # If the episode index does not exist, create a new entry
        new_episode_stats = EpisodesStatsFeatutes(
            episode_index=episode_index,
            stats=StatsModel(),
        )
        new_episode_stats.stats.update(
            step=step,
            episode_index=episode_index,
            current_step_index=current_step_index,
        )
        self.episodes_stats.append(new_episode_stats)

    def to_jsonl(self, meta_folder_path: str) -> None:
        """
        Write the episodes_stats.jsonl file in the meta folder path.
        """
        with open(
            f"{meta_folder_path}/episodes_stats.jsonl",
            "w",
            encoding=DEFAULT_FILE_ENCODING,
        ) as f:
            for episode_stats in self.episodes_stats:
                f.write(episode_stats.to_json() + "\n")

    @classmethod
    def from_jsonl(cls, meta_folder_path: str) -> "EpisodesStatsModel":
        """
        Read the episodes_stats.jsonl file in the meta folder path.
        If the file does not exist, return an empty EpisodeStatsModel.
        """
        if (
            not os.path.exists(f"{meta_folder_path}/episodes_stats.jsonl")
            or os.stat(f"{meta_folder_path}/episodes_stats.jsonl").st_size == 0
        ):
            return EpisodesStatsModel()

        with open(
            f"{meta_folder_path}/episodes_stats.jsonl",
            "r",
            encoding=DEFAULT_FILE_ENCODING,
        ) as f:
            _episodes_stats_dict: dict[int, EpisodesStatsFeatutes] = {}
            for line in f:
                parsed_line: dict = json.loads(line)

                episodes_stats_feature = EpisodesStatsFeatutes.model_validate(
                    parsed_line
                )
                # We need to parse the observation_images properly when loading the jsonl file
                observation_images = {}

                for key in list(parsed_line["stats"].keys()):
                    if "image" in key:
                        observation_images[key] = parsed_line["stats"].pop(key)

                episodes_stats_feature.stats.observation_images = observation_images

                _episodes_stats_dict[episodes_stats_feature.episode_index] = (
                    episodes_stats_feature
                )

        _episodes_stats_dict = dict(
            sorted(_episodes_stats_dict.items(), key=lambda x: x[0])
        )

        episodes_stats_model = EpisodesStatsModel(
            episodes_stats=list(_episodes_stats_dict.values())
        )

        return episodes_stats_model

    def save(self, meta_folder_path: str) -> None:
        """
        Save the episodes_stats to the meta folder path.
        Also computes the final mean and std for the Stats objects.
        """
        for episode_stats in self.episodes_stats:
            for field_key, field_value in episode_stats.stats.__dict__.items():
                # if field is a Stats object, call .compute_from_rolling() to get the final mean and std
                if isinstance(field_value, Stats):
                    field_value.compute_from_rolling()

                # Special case for images
                if isinstance(field_value, dict) and field_key == "observation_images":
                    for key, value in field_value.items():
                        try:
                            if isinstance(value, Stats):
                                value.compute_from_rolling_images()
                        except ValueError as e:
                            logger.error(f"Error computing mean and std for {key}: {e}")

        self.to_jsonl(meta_folder_path)

    def update_for_episode_removal(
        self, episode_to_delete_index: int, old_index_to_new_index: Dict[int, int]
    ) -> None:
        """
        Update the episodes_stats model before removing an episode from the dataset.
        We remove the line corresponding to the episode index.
        """
        self.episodes_stats = [
            episode_stats
            for episode_stats in self.episodes_stats
            if episode_stats.episode_index != episode_to_delete_index
        ]

        # Reindex the episodes
        if not old_index_to_new_index:
            for episode_stats in self.episodes_stats:
                if episode_stats.episode_index > episode_to_delete_index:
                    episode_stats.episode_index -= 1

        else:
            current_max_index = max(old_index_to_new_index.keys()) + 1
            for episode_stats in self.episodes_stats:
                if episode_stats.episode_index == episode_to_delete_index:
                    pass
                if episode_stats.episode_index in old_index_to_new_index.keys():
                    episode_stats.episode_index = old_index_to_new_index[
                        episode_stats.episode_index
                    ]
                else:
                    episode_stats.episode_index = current_max_index
                    current_max_index += 1
                    old_index_to_new_index[episode_stats.episode_index] = (
                        current_max_index
                    )

    def merge_with(
        self, second_stats_model: "EpisodesStatsModel", meta_folder_path: str
    ) -> None:
        """
        Merges an existing episodes stats model with another one.
        This is intended to be used when merging files for two so-100 together.
        """
        number_of_episodes_in_first_model = len(self.episodes_stats)

        # Update the episode_index for the second stats model
        for episode_stats in second_stats_model.episodes_stats:
            episode_stats.episode_index += number_of_episodes_in_first_model

        # Add the second stats model to the first one
        self.episodes_stats += second_stats_model.episodes_stats

        # Sort the episodes by episode index
        self.episodes_stats = sorted(self.episodes_stats, key=lambda x: x.episode_index)

        # Save the merged model
        self.save(meta_folder_path)

    def split(self, split_ratio: float):
        """
        Splits the episodes stats model into two parts.
        The first part contains the first split_ratio * len(episodes_stats) episodes.
        The second part contains the rest of the episodes.
        """
        split_index = int(len(self.episodes_stats) * split_ratio)
        first_part = EpisodesStatsModel(
            episodes_stats=self.episodes_stats[:split_index]
        )
        second_part = EpisodesStatsModel(
            episodes_stats=self.episodes_stats[split_index:]
        )

        # Reindex the second part
        for episode_stats in second_part.episodes_stats:
            episode_stats.episode_index -= len(first_part.episodes_stats)

        return first_part, second_part

    def shuffle(self, permutation: List[int] | np.ndarray) -> None:
        """
        Shuffles the episodes stats model according to the given permutation.
        The permutation is a list of indices that specifies the new order of the episodes.
        """
        if len(permutation) != len(self.episodes_stats):
            raise ValueError("Permutation length must match the number of episodes.")

        self.episodes_stats = [self.episodes_stats[i] for i in permutation]
        # Update episode_index
        for new_index, episode_stats in enumerate(self.episodes_stats):
            episode_stats.episode_index = new_index


class FeatureDetails(BaseModel):
    dtype: Literal["video", "int64", "float32", "str", "bool"]
    shape: List[int]
    names: List[str] | None


class VideoInfo(BaseModel):
    """
    Information about the video
    """

    video_fps: int = Field(
        default=10,
        serialization_alias="video.fps",
        validation_alias=AliasChoices("video.fps", "video_fps"),
    )
    video_codec: VideoCodecs = Field(
        serialization_alias="video.codec",
        validation_alias=AliasChoices("video.codec", "video_codec"),
    )

    video_pix_fmt: str = Field(
        default="yuv420p",
        serialization_alias="video.pix_fmt",
        validation_alias=AliasChoices("video.pix_fmt", "video_pix_fmt"),
    )
    video_is_depth_map: bool = Field(
        default=False,
        serialization_alias="video.is_depth_map",
        validation_alias=AliasChoices("video.is_depth_map", "video_is_depth_map"),
    )
    has_audio: bool = False


class VideoFeatureDetails(FeatureDetails):
    dtype: Literal["video"] = "video"
    info: VideoInfo = Field(validation_alias=AliasChoices("video_info", "info"))


class InfoFeatures(BaseModel):
    action: FeatureDetails
    observation_state: FeatureDetails = Field(
        serialization_alias="observation.state",
        validation_alias=AliasChoices("observation.state", "observation_state"),
    )

    timestamp: FeatureDetails = Field(
        default_factory=lambda: FeatureDetails(dtype="float32", shape=[1], names=None)
    )
    episode_index: FeatureDetails = Field(
        default_factory=lambda: FeatureDetails(dtype="int64", shape=[1], names=None)
    )
    frame_index: FeatureDetails = Field(
        default_factory=lambda: FeatureDetails(dtype="int64", shape=[1], names=None)
    )
    task_index: FeatureDetails = Field(
        default_factory=lambda: FeatureDetails(dtype="int64", shape=[1], names=None)
    )
    index: FeatureDetails = Field(
        default_factory=lambda: FeatureDetails(dtype="int64", shape=[1], names=None)
    )
    # Camera images
    observation_images: Dict[str, VideoFeatureDetails] = Field(
        default_factory=dict,
        serialization_alias="observation.images",
        validation_alias=AliasChoices(
            "observation.image",
            "observation.images",
            "observation_image",
            "observation_images",
        ),
    )

    # Optional fields (RL)
    next_done: FeatureDetails | None = Field(
        default=None,
        serialization_alias="next.done",
        validation_alias=AliasChoices("next.done", "next_done"),
    )
    next_success: FeatureDetails | None = Field(
        default=None,
        serialization_alias="next.success",
        validation_alias=AliasChoices("next.success", "next_success"),
    )
    next_reward: FeatureDetails | None = Field(
        default=None,
        serialization_alias="next.reward",
        validation_alias=AliasChoices("next.reward", "next_reward"),
    )

    def to_dict(self) -> dict:
        """
        Convert the InfoFeatures to a dictionary.
        This transforms observation_images and observation_state to the correct format.
        """
        model_dict = self.model_dump(by_alias=True)

        if self.observation_images is not None:
            for key, value in self.observation_images.items():
                model_dict[key] = value.model_dump(by_alias=True)

        model_dict.pop("observation.images")

        # Filter all None values
        model_dict = {
            key: value
            for key, value in model_dict.items()
            if value is not None and value != {}
        }

        return model_dict


class BaseRobotInfo(BaseModel):
    robot_type: str
    action: FeatureDetails
    observation_state: FeatureDetails = Field(
        serialization_alias="observation.state",
        validation_alias=AliasChoices("observation.state", "observation_state"),
    )

    def merge_base_robot_info(
        self, base_robot_info: "BaseRobotInfo"
    ) -> "BaseRobotInfo":
        """
        Merges an existing base robot info with another one.
        This is intended to be used when merging files for two so-100 together.
        """
        if (
            self.action.names is None
            or self.observation_state.names is None
            or base_robot_info.action.names is None
            or base_robot_info.observation_state.names is None
        ):
            raise ValueError(
                "The names field in the action and observation_state must be set."
            )
        self.robot_type += f", {base_robot_info.robot_type}"

        self.action.shape[0] += base_robot_info.action.shape[0]
        self.action.names += [
            name + "_secondary" for name in base_robot_info.action.names
        ]

        self.observation_state.shape[0] += base_robot_info.observation_state.shape[0]
        self.observation_state.names = self.observation_state.names + [
            name + "_secondary" for name in base_robot_info.observation_state.names
        ]

        return self


class InfoModel(BaseModel):
    """
    Data model util to create meta/info.jsonl file.
    """

    robot_type: str

    codebase_version: str = "v2.1"
    total_episodes: int = 0
    total_frames: int = 0
    total_tasks: int = 1  # By default, there is 1 task: "None"
    total_videos: int = 0
    total_chunks: int = 1
    chunks_size: int = 1000
    fps: int = 10
    splits: Dict[str, str] = Field(default_factory=lambda: {"train": "0:0"})
    data_path: str = (
        "data/chunk-{episode_chunk:03d}/episode_{episode_index:06d}.parquet"
    )
    video_path: str = (
        "videos/chunk-{episode_chunk:03d}/{video_key}/episode_{episode_index:06d}.mp4"
    )
    features: InfoFeatures

    @classmethod
    def from_robots(cls, robots: List[BaseRobot], **data) -> "InfoModel":
        """
        From a robot configuration, create the appropriate InfoModel.
        This is because it depends on the number of joints etc.
        """
        robot_info = robots[0].get_info_for_dataset()
        if len(robots) > 1:
            for robot in robots[1:]:
                new_info = robot.get_info_for_dataset()
                robot_info = robot_info.merge_base_robot_info(new_info)

        features = InfoFeatures(
            action=robot_info.action,
            observation_state=robot_info.observation_state,
        )
        return cls(
            **data,
            features=features,
            robot_type=robot_info.robot_type,
        )

    def to_dict(self):
        """
        Convert the InfoModel to a dictionary. This is different from
        model_dump() as it transforms the features to the correct format.
        """
        model_dict = self.model_dump(by_alias=True)
        model_dict["features"] = self.features.to_dict()
        return model_dict

    @classmethod
    def from_json(
        cls,
        meta_folder_path: str,
        fps: int | None = None,
        codec: VideoCodecs | None = None,
        robots: List[BaseRobot] | None = None,
        target_size: tuple[int, int] | None = None,
        secondary_camera_key_names: List[str] | None = None,
        format: Literal["lerobot_v2", "lerobot_v2.1"] = "lerobot_v2.1",
    ) -> "InfoModel":
        """
        Read the info.json file in the meta folder path.
        If the file does not exist, try to create the InfoModel from the provided data.

        raise ValueError if the file does not exist and no data is provided to create the InfoModel.
        """
        # Check if the file existes.
        if (
            not os.path.exists(f"{meta_folder_path}/info.json")
            or os.stat(f"{meta_folder_path}/info.json").st_size == 0
        ):
            if robots is None:
                raise ValueError(
                    "No info.json file found and no robot provided to create the InfoModel"
                )
            if codec is None:
                raise ValueError("No codec provided to create the InfoModel")
            if fps is None:
                raise ValueError("No fps provided to create the InfoModel")
            if target_size is None:
                raise ValueError("No target_size provided to create the InfoModel")
            if secondary_camera_key_names is None:
                raise ValueError(
                    "No secondary_camera_ids provided to create the InfoModel"
                )

            info_model = cls.from_robots(robots)
            video_shape = [target_size[1], target_size[0], 3]
            video_info = VideoInfo(video_codec=codec, video_fps=fps)

            info_model.fps = fps

            info_model.features.observation_images["observation.images.main"] = (
                VideoFeatureDetails(
                    shape=video_shape,
                    names=["height", "width", "channel"],
                    info=video_info,
                )
            )

            # Add secondary cameras
            for secondary_camera_key_name in secondary_camera_key_names:
                info_model.features.observation_images[secondary_camera_key_name] = (
                    VideoFeatureDetails(
                        shape=video_shape,
                        names=["height", "width", "channel"],
                        info=video_info,
                    )
                )

            info_model.codebase_version = "v2.1" if format == "lerobot_v2.1" else "v2.0"

            return info_model

        with open(
            f"{meta_folder_path}/info.json", "r", encoding=DEFAULT_FILE_ENCODING
        ) as f:
            info_model_dict = json.load(f)

        info_model_dict["features"]["observation_state"] = info_model_dict[
            "features"
        ].pop("observation.state")
        observation_images = {}
        keys_to_remove = []
        for key, value in info_model_dict["features"].items():
            if "observation.image" in key:
                observation_images[key] = value
                keys_to_remove.append(key)
        for key in keys_to_remove:
            del info_model_dict["features"][key]
        info_model_dict["features"]["observation_images"] = observation_images
        infos = cls.model_validate(info_model_dict)
        return infos

    @classmethod
    def from_multidataset(
        cls,
        robot_type: str,
        nb_cameras: int,
        fps: int,
        nb_motors: int,
        chunks_size: int,
        resize_video: Tuple[int, int],
        # li_datasets is a list of LeRobotDatasets
        # We dont type it as List[LeRobotDataset] to avoid importing LeRobotDataset
        li_datasets: list,
    ) -> "InfoModel":
        """Create an InfoModel from multiple datasets information."""

        # Create the action and observation_state FeatureDetails
        action_details = FeatureDetails(
            dtype="float32",
            shape=[nb_motors],
            names=[f"motor_{i + 1}" for i in range(nb_motors)],
        )

        observation_state_details = FeatureDetails(
            dtype="float32",
            shape=[nb_motors],
            names=[f"motor_{i + 1}" for i in range(nb_motors)],
        )

        # Create the observation_images dictionary
        observation_images = {}
        for i in range(nb_cameras):
            camera_key = (
                f"observation.images.{'main' if i == 0 else f'secondary_{i - 1}'}"
            )
            observation_images[camera_key] = VideoFeatureDetails(
                shape=[resize_video[1], resize_video[0], 3],
                names=["height", "width", "channel"],
                info=VideoInfo(
                    video_fps=fps,
                    video_codec="mp4v",
                    video_pix_fmt="yuv420p",
                    video_is_depth_map=False,
                    has_audio=False,
                ),
            )

        # Create InfoFeatures object
        features = InfoFeatures(
            action=action_details,
            observation_state=observation_state_details,
            observation_images=observation_images,
        )

        # Create the base InfoModel
        info_model = cls(
            robot_type=robot_type,
            codebase_version="v2.0",
            total_episodes=0,
            total_frames=0,
            total_tasks=1,
            total_videos=0,
            total_chunks=1,
            chunks_size=chunks_size,
            fps=fps,
            features=features,
        )

        # Update with dataset information if provided
        if li_datasets:
            # Calculate totals from all datasets
            for dataset in li_datasets:
                info = dataset.meta.info
                info_model.total_frames += info.get("total_frames", 0)
                info_model.total_videos += info.get("total_videos", 0)
                info_model.total_episodes += info.get("total_episodes", 0)

            info_model.splits = {"train": f"0:{info_model.total_episodes}"}
            info_model.total_chunks = info_model.total_episodes // chunks_size

            # Count unique tasks
            unique_tasks = set()
            for dataset in li_datasets:
                unique_tasks.update(dataset.meta.task_to_task_index.keys())

            info_model.total_tasks = len(unique_tasks)

        return info_model

    def to_json(self, meta_folder_path: str) -> None:
        """
        Write the info.json file in the meta folder path.
        """
        with open(
            f"{meta_folder_path}/info.json", "w", encoding=DEFAULT_FILE_ENCODING
        ) as f:
            f.write(json.dumps(self.to_dict(), indent=4))

    def update(self, episode: Episode) -> None:
        """
        Update the info given a new recorded Episode.
        """
        # Read the number of total episodes and videos based on the number of files
        # in the data folder

        nb_episodes = len(
            [
                file
                for file in os.listdir(episode.episodes_path)
                if file.endswith(".parquet")
            ]
        )

        self.total_episodes = nb_episodes
        self.total_frames += len(episode.steps)
        # Count the number of videos in every subfolder
        video_path = os.path.join(episode.dataset_path, "videos", "chunk-000")
        total_videos = 0
        for camera_name in os.listdir(video_path):
            # Count the number of videos in the subfolder
            if "image" not in camera_name:
                continue
            total_videos += len(
                [
                    file
                    for file in os.listdir(os.path.join(video_path, camera_name))
                    if file.endswith(".mp4")
                ]
            )

        self.total_videos = total_videos
        self.splits = {"train": f"0:{self.total_episodes}"}

        # Handle task index
        task_index = episode.metadata.get("task_index", 0)
        if task_index >= self.total_tasks:
            self.total_tasks = task_index + 1

        # TODO: Implement support for multiple chunks

    def save(
        self,
        meta_folder_path: str,
    ) -> None:
        """
        Save the info to the meta folder path.
        """
        self.to_json(meta_folder_path)

    def update_for_episode_removal(self, df_episode_to_delete: pd.DataFrame) -> None:
        """
        Update the info before removing an episode from the dataset.
        """
        if df_episode_to_delete.empty:
            return

        # Read from the data folder
        self.total_episodes -= 1
        self.total_frames -= len(df_episode_to_delete)
        self.total_videos -= len(self.features.observation_images.keys())
        self.splits = {"train": f"0:{self.total_episodes}"}
        # TODO(adle): Implement support for multi tasks in dataset
        # self.total_tasks -= ...

    def merge_with(
        self,
        second_info_model: "InfoModel",
        meta_folder_to_save_to: str,
        new_nb_tasks: int,
    ) -> None:
        """
        Will merge the info.json file with another one and save it to the new meta folder.
        """
        # Merge the info model
        self.total_episodes += second_info_model.total_episodes
        self.total_frames += second_info_model.total_frames
        self.total_videos += second_info_model.total_videos
        self.total_tasks = new_nb_tasks
        self.splits = {"train": f"0:{self.total_episodes}"}

        # Save the info.json file
        self.to_json(meta_folder_path=meta_folder_to_save_to)

    def update_for_video_removal(
        self, video_keys_to_delete: List[str], meta_folder_to_save_to: str
    ) -> None:
        """
        Update the info when removing a video from the dataset.

        full_video_keys are of the form "observation.images.{video_key}"

        Need to update:
        - total_frames
        - total_videos

        Need to delete:
        - features.{video_key}

        Will save the info.json file to the meta_folder_to_save_to folder.
        """

        # Get the current number of video keys before deleting
        nb_video_keys_before_deletion = len(self.features.observation_images.keys())

        # We keep the number of total frames constant

        self.total_videos -= self.total_episodes * len(video_keys_to_delete)

        print(
            f"self.features.observation_images: {self.features.observation_images.keys()}"
        )

        # Remove the video from the folder
        for video_key in video_keys_to_delete:
            # Check if it starts with observation.images.
            if video_key.startswith("observation.images."):
                del self.features.observation_images[video_key]
            else:
                del self.features.observation_images[f"observation.images.{video_key}"]

        # Save the info.json file
        self.to_json(meta_folder_path=meta_folder_to_save_to)


class TasksFeatures(BaseModel):
    """
    Features of the lines in tasks.jsonl.
    """

    task_index: int
    task: str = "None"


class TasksModel(BaseModel):
    """
    Data model util to create meta/tasks.jsonl file.
    """

    tasks: List[TasksFeatures]
    _initial_nb_total_tasks: int = 0

    @classmethod
    def from_jsonl(cls, meta_folder_path: str) -> "TasksModel":
        """
        Read the tasks.jsonl file in the meta folder path.
        """
        if not os.path.exists(f"{meta_folder_path}/tasks.jsonl"):
            return cls(tasks=[])

        with open(
            f"{meta_folder_path}/tasks.jsonl", "r", encoding=DEFAULT_FILE_ENCODING
        ) as f:
            tasks = []
            for line in f:
                tasks.append(TasksFeatures(**json.loads(line)))

        tasks_model = cls(tasks=tasks)
        # Do it after model init, otherwise pydantic ignores the value of _original_nb_total_tasks
        tasks_model._initial_nb_total_tasks = len(tasks)
        return tasks_model

    @classmethod
    def from_li_tasks(cls, li_tasks: List[str]) -> "TasksModel":
        """Create a TasksModel from a list of tasks."""
        # Ensure that the tasks are unique
        li_tasks = list(set(li_tasks))
        tasks = [
            TasksFeatures(task_index=i, task=task) for i, task in enumerate(li_tasks)
        ]
        return cls(tasks=tasks, _initial_nb_total_tasks=len(tasks))

    def to_jsonl(
        self,
        meta_folder_path: str,
        save_mode: Literal["append", "overwrite"] = "overwrite",
    ) -> None:
        """
        Write the tasks.jsonl file in the meta folder path.
        """

        if save_mode == "overwrite":
            with open(f"{meta_folder_path}/tasks.jsonl", "w") as f:
                for task in self.tasks:
                    f.write(task.model_dump_json() + "\n")
        elif save_mode == "append":
            with open(
                f"{meta_folder_path}/tasks.jsonl", "a", encoding=DEFAULT_FILE_ENCODING
            ) as f:
                # Only append the new tasks to the file
                for task in self.tasks[self._initial_nb_total_tasks :]:
                    f.write(task.model_dump_json() + "\n")

    def update(self, step: Step) -> None:
        """
        Updates the tasks with the given step.
        """
        # Add the task only if it is not in the tasks already
        if str(step.observation.language_instruction) not in [
            task.task for task in self.tasks
        ]:
            logger.info(
                f"Adding task: {step.observation.language_instruction} to {[task.task for task in self.tasks]}"
            )
            self.tasks.append(
                TasksFeatures(
                    task_index=len(self.tasks),
                    task=str(step.observation.language_instruction),
                )
            )

    def update_for_episode_removal(
        self, df_episode_to_delete: pd.DataFrame, data_folder_full_path=str
    ) -> None:
        """
        Update the tasks when removing an episode from the dataset.
        We count the number of occurences of task_index in the dataset.
        If the episode is the only one with this task_index, we remove it from the tasks.jsonl file.
        """
        if df_episode_to_delete.empty:
            return

        # For each file in the data folder get the task indexes (unique)
        task_indexes: List[int] = []
        for file in os.listdir(data_folder_full_path):
            if file.endswith(".parquet"):
                df = pd.read_parquet(f"{data_folder_full_path}/{file}")
                task_indexes.extend(df["task_index"].unique())

        for task_index in df_episode_to_delete["task_index"].unique():
            task_index = int(task_index)
            # delete the line in tasks.jsonl if and only if the task index in this episode is the only one in the dataset
            if task_indexes.count(task_index) == 1:
                self.tasks = [
                    task for task in self.tasks if task.task_index != task_index
                ]

    def save(self, meta_folder_path: str) -> None:
        """
        Save the episodes to the meta folder path.
        """
        self.to_jsonl(meta_folder_path)

    def merge_with(
        self, second_task_model: "TasksModel", meta_folder_to_save_to: str
    ) -> tuple[dict[int, int], int]:
        """
        Will merge the tasks.jsonl file with another one and save it to the new meta folder.
        Returns a task mapping of the old task index to the new one.
        """
        # Create a mapping of the old task index to the new one
        old_index_to_new_index: Dict[int, int] = {}

        for i, task_model in enumerate(second_task_model.tasks):
            # Check if the task is already in the first task model
            if task_model.task not in [t.task for t in self.tasks]:
                # If not, add it to the first task model
                old_index_to_new_index[task_model.task_index] = len(self.tasks)
                self.tasks.append(
                    TasksFeatures(task_index=len(self.tasks), task=task_model.task)
                )
            else:
                # If it is, update the mapping
                old_index_to_new_index[task_model.task_index] = [
                    t.task for t in self.tasks
                ].index(task_model.task)

        new_number_of_tasks = len(self.tasks)

        # Save the tasks.jsonl file
        self.to_jsonl(meta_folder_path=meta_folder_to_save_to, save_mode="overwrite")

        return old_index_to_new_index, new_number_of_tasks

    def split(self, split_ratio: float, initial_episodes_model: "EpisodesModel"):
        """
        Splits the tasks model into two parts.
        The first part contains the first split_ratio * len(tasks) tasks.
        The second part contains the rest of the tasks.
        """
        split_index = int(len(initial_episodes_model.episodes) * split_ratio)

        first_tasks = TasksModel(tasks=[])
        second_tasks = TasksModel(tasks=[])
        mapping_old_to_new_index: dict[int, int] = {}

        for episode in initial_episodes_model.episodes:
            if episode.episode_index < split_index:
                if episode.tasks[0] not in [
                    first_tasks.tasks[i].task for i in range(len(first_tasks.tasks))
                ]:
                    first_tasks.tasks.append(
                        TasksFeatures(
                            task_index=len(first_tasks.tasks), task=episode.tasks[0]
                        )
                    )
            else:
                if episode.tasks[0] not in [
                    second_tasks.tasks[i].task for i in range(len(second_tasks.tasks))
                ]:
                    second_tasks.tasks.append(
                        TasksFeatures(
                            task_index=len(second_tasks.tasks), task=episode.tasks[0]
                        )
                    )
                    # Find the previous task index in the initial tasks model
                    task_index = [
                        task.task_index
                        for task in self.tasks
                        if task.task == episode.tasks[0]
                    ]
                    if task_index:
                        mapping_old_to_new_index[task_index[0]] = len(
                            mapping_old_to_new_index
                        )
                    else:
                        raise ValueError(
                            f"Task {episode.tasks[0]} not found in the initial tasks model"
                        )

        # Count the number of different tasks in the first part
        nbr_tasks_first_part = len(first_tasks.tasks)
        nbr_tasks_second_part = len(second_tasks.tasks)

        return (
            first_tasks,
            second_tasks,
            nbr_tasks_first_part,
            nbr_tasks_second_part,
            mapping_old_to_new_index,
        )


class EpisodesFeatures(BaseModel):
    """
    Features for each line of the episodes.jsonl file.
    """

    episode_index: int = 0
    tasks: List[str] = []
    length: int = 0

    # Import tasks as a list of str if it is a str
    @field_validator("tasks", mode="before")
    def validate_tasks(cls, v):
        if isinstance(v, str):
            return [v]
        elif isinstance(v, list):
            return v
        else:
            raise ValueError("tasks must be a list of strings or a single string")


class EpisodesModel(BaseModel):
    """
    Follow the structure of the episodes.jsonl file.
    """

    episodes: List[EpisodesFeatures] = Field(default_factory=list)
    _episodes_features: Dict[int, EpisodesFeatures] | None = None
    _original_nb_total_episodes: int = 0

    def update(self, step: Step, episode_index: int) -> None:
        """
        Updates the episodes with the given episode.
        episode_index is the index of the episode of the current step.
        """
        # If episode_index is not in the episodes, add it

        if self._episodes_features is None:
            self._episodes_features = {
                episode.episode_index: episode for episode in self.episodes
            }

        episode = self._episodes_features.get(episode_index)

        if episode is not None:
            # Increase the nb frames counter
            episode.length += 1
            # Add the language instruction if it's a new one
            if str(step.observation.language_instruction) not in episode.tasks:
                episode.tasks.append(str(step.observation.language_instruction))
        else:
            # Create a new episode
            new_episode = EpisodesFeatures(
                episode_index=episode_index,
                tasks=[str(step.observation.language_instruction)],
                length=1,
            )
            self.episodes.append(new_episode)
            self._episodes_features[episode_index] = new_episode

    def to_jsonl(
        self, meta_folder_path: str, save_mode: Literal["append", "overwrite"]
    ) -> None:
        """
        Write the episodes.jsonl file in the meta folder path.
        """
        if save_mode == "append":
            with open(f"{meta_folder_path}/episodes.jsonl", "a") as f:
                for episode in self.episodes[self._original_nb_total_episodes :]:
                    f.write(episode.model_dump_json() + "\n")
        elif save_mode == "overwrite":
            if self._episodes_features is None:
                self._episodes_features = {
                    episode.episode_index: episode for episode in self.episodes
                }

            with open(f"{meta_folder_path}/episodes.jsonl", "w") as f:
                for episode in self._episodes_features.values():
                    f.write(episode.model_dump_json() + "\n")
        else:
            raise ValueError("save_mode must be 'append' or 'overwrite'")

    @classmethod
    def from_jsonl(
        cls, meta_folder_path: str, format: Literal["lerobot_v2", "lerobot_v2.1"]
    ) -> "EpisodesModel":
        """
        Read the episodes.jsonl file in the meta folder path.
        """
        if not os.path.exists(f"{meta_folder_path}/episodes.jsonl"):
            return EpisodesModel()

        with open(
            f"{meta_folder_path}/episodes.jsonl", "r", encoding=DEFAULT_FILE_ENCODING
        ) as f:
            _episodes_features: dict[int, EpisodesFeatures] = {}
            last_index = 0
            missing_episodes = []
            for line in f:
                episodes_feature = EpisodesFeatures.model_validate_json(line)
                _episodes_features[episodes_feature.episode_index] = episodes_feature
                # If we skipped an index, check if the parquet file exists and if so recreate the episode
                if episodes_feature.episode_index != last_index + 1:
                    missing_indexes = [
                        i
                        for i in range(last_index + 1, episodes_feature.episode_index)
                        if i not in _episodes_features
                    ]
                    logger.debug(f"Missing indexes: {missing_indexes}")
                    # Dataset path is the parent folder of the meta folder
                    data_folder_path = os.path.dirname(meta_folder_path)
                    for i in missing_indexes:
                        episode_path = os.path.join(
                            data_folder_path,
                            "data",
                            "chunk-000",
                            f"episode_{i:06d}.parquet",
                        )
                        if os.path.exists(episode_path):
                            episode = Episode.from_parquet(episode_path, format=format)
                            _episodes_features[i] = EpisodesFeatures(
                                episode_index=i,
                                tasks=[
                                    str(
                                        episode.steps[
                                            0
                                        ].observation.language_instruction
                                    )
                                ],
                                length=len(episode.steps),
                            )
                            missing_episodes.append(i)
                last_index = episodes_feature.episode_index

        # Sort the _episodes_features by increasing episode_index
        _episodes_features = dict(
            sorted(_episodes_features.items(), key=lambda x: x[0])
        )

        # If we found missing episodes and added them to the list, we need to update the file
        if missing_episodes:
            with open(
                f"{meta_folder_path}/episodes.jsonl",
                "w",
                encoding=DEFAULT_FILE_ENCODING,
            ) as f:
                for episode_feature in _episodes_features.values():
                    f.write(episode_feature.model_dump_json() + "\n")

        episodes_model = EpisodesModel(
            episodes=list(_episodes_features.values()),
        )
        # Do it after model init, otherwise pydantic ignores the value of _original_nb_total_episodes
        episodes_model._original_nb_total_episodes = len(_episodes_features.keys())
        episodes_model._episodes_features = _episodes_features
        return episodes_model

    def save(
        self,
        meta_folder_path: str,
        save_mode: Literal["append", "overwrite"] = "overwrite",
    ) -> None:
        """
        Save the episodes to the meta folder path.
        """
        self.to_jsonl(meta_folder_path=meta_folder_path, save_mode=save_mode)

    def update_for_episode_removal(
        self, episode_to_delete_index: int, old_index_to_new_index: Dict[int, int]
    ) -> None:
        """
        Update the episodes model before removing an episode from the dataset.
        We just remove the line corresponding to the episode_index of the parquet file.
        """
        # Remove the episode from the list
        self.episodes = [
            episode
            for episode in self.episodes
            if episode.episode_index != episode_to_delete_index
        ]

        # Reindex the episodes
        if not old_index_to_new_index:
            # Reindex the episodes
            for episode in self.episodes:
                if episode.episode_index > episode_to_delete_index:
                    episode.episode_index -= 1

        else:
            # Use the old_index_to_new_index to update the episode index
            current_max_index = max(old_index_to_new_index.keys()) + 1
            for episode in self.episodes:
                if episode.episode_index == episode_to_delete_index:
                    pass
                if episode.episode_index in old_index_to_new_index.keys():
                    # Update the episode index
                    episode.episode_index = old_index_to_new_index[
                        episode.episode_index
                    ]
                else:
                    # Update the episode index to the new one
                    episode.episode_index = current_max_index
                    current_max_index += 1
                    # Update mapping
                    old_index_to_new_index[episode.episode_index] = current_max_index

        # Recreate the _episodes_features dict
        self._episodes_features = {
            episode.episode_index: episode for episode in self.episodes
        }

    def merge_with(
        self, second_episodes_model: "EpisodesModel", meta_folder_to_save_to
    ) -> None:
        """
        Merge the episodes with another episodes model and save it to the new meta folder.
        """
        # Update the episode_index for the second episodes model
        for episode in second_episodes_model.episodes:
            episode.episode_index += len(self.episodes)

        # Merge the episodes
        self.episodes.extend(second_episodes_model.episodes)

        # Remove duplicates
        self.episodes = list(
            {episode.episode_index: episode for episode in self.episodes}.values()
        )
        self._episodes_features = {
            episode.episode_index: episode for episode in self.episodes
        }

        # Save the episodes.jsonl file
        self.to_jsonl(meta_folder_path=meta_folder_to_save_to, save_mode="overwrite")

    @classmethod
    def repair_parquets(self, parquets_path: str) -> bool:
        """
        This function will attempt to correct the parquet files in the dataset.
        It will:
        - Check if the parquets are correctly indexed
        - Rewrite all episode_index, frame index and index
        """
        # Check if the parquets exist
        if not os.path.exists(parquets_path):
            logger.warning(f"Parquet path {parquets_path} does not exist.")
            return False
        # Fetch all the parquet files
        parquet_files = os.listdir(parquets_path)
        parquet_files = [file for file in parquet_files if file.endswith(".parquet")]
        parquet_files.sort()
        # Check if the files are correctly indexed
        for i, file in enumerate(parquet_files):
            # Check if the file is correctly indexed
            if f"episode_{i:06d}.parquet" not in file:
                logger.warning(
                    f"Parquet file {file} is not correctly indexed. Expected episode_{i:06d}.parquet"
                )
                return False

        logger.info("Parquet files are correctly indexed. Will attempt to repair them.")
        cumulative_index = 0
        for i, file in enumerate(parquet_files):
            # Read the parquet file
            df = pd.read_parquet(os.path.join(parquets_path, file))
            # Check if the episode_index is correct
            df["episode_index"] = i
            df["frame_index"] = np.arange(len(df))
            df["index"] = np.arange(len(df)) + cumulative_index
            cumulative_index += len(df)
            # Save the parquet file
            df.to_parquet(os.path.join(parquets_path, file), index=False)
            logger.info(f"Parquet file {file} repaired.")

        return True

    def split(self, split_ratio: float):
        """
        Split the episodes model into two parts.
        """
        # Calculate the split index
        split_index = int(len(self.episodes) * split_ratio)
        # Split the episodes
        first_part = self.episodes[:split_index]
        second_part = self.episodes[split_index:]
        # Reindex second part
        for i, episode in enumerate(second_part):
            episode.episode_index = episode.episode_index - len(first_part)
        # Create new episodes models
        first_part_model = EpisodesModel(episodes=first_part)
        second_part_model = EpisodesModel(episodes=second_part)
        return first_part_model, second_part_model

    def shuffle(self, permutation: List[int] | np.ndarray) -> None:
        """
        Shuffle the episodes in the model.
        """
        # Edit the episode indexes based on the permutation
        for i, episode in enumerate(self.episodes):
            episode.episode_index = permutation[i]
        self.episodes.sort(key=lambda x: x.episode_index)
        # Recreate the _episodes_features dict
        self._episodes_features = {
            episode.episode_index: episode for episode in self.episodes
        }
