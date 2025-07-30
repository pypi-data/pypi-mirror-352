from PIL import Image, ImageSequence
import matplotlib.pyplot as plt
from tqdm.notebook import tqdm
import numpy as np
import shutil
import pickle
import json
import cv2
import os

def read_json(filename):
    """
    Read data from a JSON file and return it as a Python object.

    Args:
        filename (str): The name of the JSON file to read from.

    Returns:
        Any: The data read from the JSON file, as a Python object.
    """
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Invalid JSON format in file '{filename}'.")
        return None

def write_json(data, filename):
    """
    Write data to a JSON file.

    Args:
        data (Any): The data to write to the JSON file.
        filename (str): The name of the JSON file to write to.

    Returns:
        None
    """
    try:
        with open(filename, 'w') as f:
            json.dump(data, f)
    except IOError:
        print(f"Error writing to file '{filename}'.")


def split_video_to_mp4(video_path, output_dir, window_size=4):
    """
    Splits the given video (at video_path) into clips of size window_size and stores the output in output_dir

    Parameters:
        video_path (string): The path to the MP4 video.
        output_dir (string): The output filder that will store the sliding window clips.
        window_size (int)  : The # of frames in each video.
    """

    if output_dir in os.listdir('.'):
        shutil.rmtree(output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    cap = cv2.VideoCapture(video_path)

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frames = []
    ret, frame = cap.read()
    while ret:
        frames.append(frame)
        ret, frame = cap.read()

    cap.release()

    for i in range(len(frames) - window_size + 1):
        output_path = os.path.join(output_dir, f"{i+1}.mp4")
        out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

        for j in range(i, i + window_size):
            out.write(frames[j])

        out.release()

def get_output_dir(directory):
    """
    Takes the output directory created by split_video_to_mp4 and returns the sorted list of files.

    Parameters:
        directory (string): The path to the directory containing the split clips.

    Returns:
        list: the sorted files in the directory.
    """
    files = os.listdir(directory)
    files.sort(key = lambda x: int(x.split(".")[0]))
    return list(map(lambda x: os.path.join(directory, x), files))

def load_basketball(basketball_path, size):
    basketball = Image.open(basketball_path)
    basketball = basketball.resize((size, size), Image.LANCZOS)
    return basketball

def rotate_basketball(basketball):
    random_angle = np.random.randint(0, 360)
    return basketball.rotate(random_angle, expand=True)

def add_basketball_to_frame(frame, basketball):
    frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    basketball_rotated = rotate_basketball(basketball)

    frame_width, frame_height = frame_pil.size
    basketball_width, basketball_height = basketball_rotated.size

    max_x = frame_width - basketball_width
    max_y = frame_height - basketball_height
    rand_x = np.random.randint(0, max_x)
    rand_y = np.random.randint(0, max_y)

    frame_pil.paste(basketball_rotated, (rand_x, rand_y), basketball_rotated)
    return cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)

def add_noise(input_video_path, output_video_path, basketball_path, basketball_size):
    basketball = load_basketball(basketball_path, basketball_size)
    cap = cv2.VideoCapture(input_video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_with_basketball = add_basketball_to_frame(frame, basketball)

        out.write(frame_with_basketball)

    cap.release()
    out.release()
    #cv2.destroyAllWindows()

def pickle_read(file):
    """
    Reads the content from a pickle file.
    """
    with open(file, 'rb') as f:
        data = pickle.load(f)
    return data

def pickle_write(data, file_name):
    """
    Writes data (first argument) to a pickle file (second argument).
    """
    with open(file_name, 'wb') as file:
        pickle.dump(data, file)

pkl_read  = pickle_read
pkl_write = pickle_write

def json_read(file):
    """
    Reads the content from a JSON file.
    """
    with open(file, 'r') as f:
        data = json.load(f)
    return data

def json_write(data, file_name):
    """
    Writes data (first argument) to a JSON file (second argument).
    """
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)

def jsonl_read(file):
    """
    Reads the content from a JSONL file.
    """
    data = []
    with open(file, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    return data

def jsonl_write(data, file_name):
    """
    Writes data (first argument, a list of dictionaries/objects) to a JSONL file (second argument).
    """
    with open(file_name, 'w') as file:
        for item in data:
            json.dump(item, file)
            file.write('\n')
