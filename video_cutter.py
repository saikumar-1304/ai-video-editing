import time
import subprocess
import traceback
from logging_service import logger


TRANSITION_TIME = 5


class VideoCutter:
    def __init__(
        self,
        input_video_path: str,
        output_video_path: str,
        transition_video_path: str,
        speech_segments: list,
    ) -> None:
        self.__input_video_path = input_video_path
        self.__output_video_path = output_video_path
        self.__transition_video_path = transition_video_path
        self.__speech_segments = speech_segments

    def cut(self) -> None:
        self.__cut_ffmpeg()

    def __cut_ffmpeg(self):
        TRANSITION_EFFECT = 'fade'
        TRANSITION_DURATION = 2

        try:
            vw_start_time = time.time()
            logger.debug(f'START VIDEO WRITING: {vw_start_time} (timestamp)')

            # Initialize filter complex
            cmd = f'ffmpeg -i {self.__input_video_path} -filter_complex "'

            # First pass: normalize all segments to same fps
            k = 0
            for segment in self.__speech_segments:
                if not segment.is_relevant:
                    continue
                logger.debug(f'SEGMENT {k}: {segment.start_time_sec} - {segment.end_time_sec}')
                start = round(segment.start_time_sec, 1)
                end = round(segment.end_time_sec, 1)
                # Add fps filter before trim and ensure constant frame rate
                cmd += f'[0:v]fps=25,trim={start}:{end},setpts=PTS-STARTPTS[vtemp{k}];'
                cmd += f'[vtemp{k}]format=yuv420p[v{k}];'
                cmd += f'[0:a]atrim={start}:{end},asetpts=PTS-STARTPTS[a{k}];'
                k += 1

            # Second pass: apply transitions
            k = 0
            total_duration = 0
            last_video_slug = 'v0'
            last_audio_slug = 'a0'
            
            for segment in self.__speech_segments[:-1]:
                if not segment.is_relevant:
                    continue
                k += 1
                start = round(segment.start_time_sec, 1)
                end = round(segment.end_time_sec, 1)
                segment_duration = round(end - start - TRANSITION_DURATION, 1)
                total_duration = round(total_duration + segment_duration, 1)
                new_video_slug = f'vc{k}'
                new_audio_slug = f'ac{k}'
                
                # Ensure constant frame rate for xfade inputs
                cmd += f'[{last_video_slug}][v{k}]'
                cmd += f'xfade=transition={TRANSITION_EFFECT}:duration={TRANSITION_DURATION}:offset={total_duration}'
                cmd += f'[{new_video_slug}];'
                
                cmd += f'[{last_audio_slug}][a{k}]'
                cmd += f'acrossfade=d={TRANSITION_DURATION}:c1=tri:c2=tri'
                cmd += f'[{new_audio_slug}];'
                
                last_video_slug = new_video_slug
                last_audio_slug = new_audio_slug

            cmd = cmd[:-1] + '"'

            # Add output options
            cmd += f' -map "[{last_video_slug}]" -map "[{last_audio_slug}]"'
            cmd += f' -vcodec libx264 -acodec aac -preset ultrafast'
            cmd += f' -pix_fmt yuv420p'
            cmd += f' -r 25'  # Ensure output frame rate
            cmd += f' -f mp4 -y {self.__output_video_path}'

            logger.debug(f'RUNNING COMMAND: {cmd}')
            subprocess.run(cmd, shell=True, check=True)  # Added check=True to raise on error
            logger.debug(f'TIME TAKEN ON VIDEO WRITING: {time.time() - vw_start_time} (seconds)')

        except subprocess.CalledProcessError as e:
            logger.error(f'FFMPEG ERROR:\nCommand: {e.cmd}\nOutput: {e.output}\nError: {e.stderr}')
            raise
        except Exception as e:
            logger.error(f'PROBLEM WITH VIDEO WRITING:\n{traceback.format_exc()}')
            raise
        
    def __cut_moviepy(self):
        pass
        # OLD APPROACH

        # try:
        #     transition_clip = VideoFileClip(self.__transition_video_path)
        #     transition_clip = transition_clip.subclip(0, TRANSITION_TIME)
        # except Exception as e:
        #     logger.error(
        #         f'problem with loading transition video: {self.__transition_video_path}\nerror: {e}'
        #     )
        #     raise e

        # try:
        #     video_clip = VideoFileClip(self.__input_video_path)
        # except Exception as e:
        #     logger.error(
        #         f'problem with loading input video: {self.__input_video_path}\nerror: {e}'
        #     )
        #     raise e

        # arr = []
        # for i, segment in enumerate(self.__speech_segments):
        #     logger.debug(f'segment {i}: {segment}')
        #     if segment.is_relevant:
        #         arr.append(
        #             video_clip.subclip(segment.start_time_sec, segment.end_time_sec)
        #         )
        #     logger.debug(f'segment {i} is done')

        # logger.debug(f'start concatenating {len(arr)} clips')
        # final_clip = concatenate_videoclips(arr)
        # logger.debug('finish concatenating, start writing')
        # final_clip.write_videofile(
        #     self.__output_video_path,
        #     codec='libx264',
        #     audio_codec='aac',
        #     temp_audiofile='./media/temp-audio.m4a',
        #     remove_temp=True,
        #     preset='ultrafast',
        #     logger=None,
        #     threads=4
        # )
