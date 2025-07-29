import datetime
import re
import subprocess

from tensorflow.python.ops.ragged.ragged_math_ops import segment_prod


def convert_audio(audio_path, output_audio_path, codec="libopus", bitrate="32k", sample_rate=16000, vbr=True):
    stdout = ""

    try:
        start_time = datetime.datetime.now()

        # The ffmpeg command with the vorbis codec can reduce the conversion time by half
        stdout = subprocess.check_output([
            'ffmpeg',
            '-i', audio_path,
            '-c:a', codec,
            '-b:a', bitrate,
            '-ar', sample_rate.__str__(),
            '-vbr', 'on' if vbr else 'off',
            output_audio_path
        ], stderr=subprocess.STDOUT)

        end_time = datetime.datetime.now()
        print(f"Conversion time: {end_time - start_time}")

        return stdout.decode('utf-8')
    except Exception as e:
        print(f"Exception while converting audio: {e}")
        print(stdout)
        return False


def redact_audio(audio_path, output_audio_path, segments):
    stdout = ""

    try:
        start_time = datetime.datetime.now()
        segment_params = []

        for segment in segments:
            segment_params.append(f"between(t,{segment[0]},{segment[1]})")

        stdout = subprocess.check_output([
            'ffmpeg',
            '-i', audio_path,
            '-af', f"volume=0:enable='{'+'.join(segment_params)}'",
            '-y',
            output_audio_path
        ], stderr=subprocess.STDOUT)

        end_time = datetime.datetime.now()
        print(f"Redaction time: {end_time - start_time}")

        return stdout.decode('utf-8')
    except Exception as e:
        print(f"Exception while redacting audio: {e}")
        print(stdout)
        return False


def get_audio_duration(audio_path):
    try:
        stdout = subprocess.check_output([
            'ffprobe',
            '-i', audio_path,
        ], stderr=subprocess.STDOUT)

        return grab_audio_duration_from_ffmpeg_output(stdout.decode('utf-8'))
    except Exception as e:
        print(f"Exception while getting audio duration: {e}")
        return None


def grab_audio_duration_from_ffmpeg_output(stdout):
    duration_seconds = None

    try:
        duration_match = re.search(r' Duration: (\d+:\d+:\d+\.\d+)', stdout)

        if duration_match:
            duration = duration_match.group(1)
            duration_parts = duration.split(',' if "," in duration else '.')
            vals = duration_parts[0].split(':')
            duration_seconds = round(
                int(vals[0]) * 3600 + int(vals[1]) * 60 + int(vals[2]) + (
                    float(f"0.{duration_parts[1]}") if len(duration_parts) > 1 else 0),
                2)
            print(f"Audio duration: {duration_seconds}")
    except Exception as e:
        print(f"Exception while grabbing duration: {e}")
        return None

    return duration_seconds


def get_audio_info(audio_path):
    try:
        stdout = subprocess.check_output([
            'ffprobe',
            '-i', audio_path,
            '-show_entries',
            'stream=sample_rate,channels,duration,bit_rate',
            '-select_streams', 'a:0',
            '-of', 'compact=p=0:nk=1',
            '-v', '0'
        ], stderr=subprocess.STDOUT)

        parts = stdout.decode('utf-8').split("|")

        try:
            return {
                "sample_rate": int(parts[0]),
                "channels": int(parts[1]),
                "duration": float(parts[2]),
                "bit_rate": int(parts[3]),
            }
        except Exception as e:
            print(f"Exception while getting audio duration: {e}. File: {audio_path}. Data: {stdout}")
            return None
    except Exception as e:
        print(f"Exception while getting audio duration: {e}. File: {audio_path}")
        return None
