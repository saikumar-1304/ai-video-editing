import os
import shutil
import random
import traceback
import logging
from uuid import uuid4
from datetime import datetime
from process_video_service import ProcessVideoService
# from logging_service import logger
# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

MEDIA_FOLDER = "media"

def process_video_background(session_id: str, data):
    # Creating session folder locally
    session_folder_path = f"{MEDIA_FOLDER}/{session_id}"
    os.makedirs(session_folder_path, exist_ok=True)

    # Creating session sub folders locally
    input_video_path = f"{session_folder_path}/input.mp4"
    output_path = f"{session_folder_path}/output"
    os.makedirs(output_path, exist_ok=True)

    session_folder_url = None
    session_folder_id = None
    
    log_file_name = "log.txt"
    log_file_path = f"{output_path}/{log_file_name}"


    try:
        input_video_url = data["file_path"]
        class_n = data["class_n"]
        subject = data["subject"]
        use_gpt = data["use_gpt"]
        render_final_video = data["render_final_video"]

        logger.info(
            f"start processing: input_video_url: {input_video_url}, class_n: {class_n}, subject: {subject}, use_gpt: {use_gpt}, render_final_video: {render_final_video}"
        )
        input_video_path = f"{session_folder_path}/input.mp4"
        output_path = f"{session_folder_path}/output"
        os.makedirs(output_path, exist_ok=True)
        logger.info("download completed ...")
        logger.info("starting processing video")
        pvs = ProcessVideoService(
            input_video_path,
            class_n,
            subject,
            use_gpt=use_gpt,
            regenerate_audio=False,
            regenerate_transcription=False,
            write_final_video=render_final_video,
        )
        pvs.process()
        logger.info("processing completed")

        output_filenames = os.listdir(output_path)
        for output_filename in output_filenames:
            if output_filename == log_file_name:
                continue
            local_path = f"{output_path}/{output_filename}"


    except Exception:
        logger.error(f"error during video processing: {traceback.format_exc()}")


if __name__ == "__main__":
    process_video_background("123", {
        "file_path": "input.mp4",
        "class_n": "Math",
        "subject": "Algebra",
        "use_gpt": True,
        "render_final_video": True
    })