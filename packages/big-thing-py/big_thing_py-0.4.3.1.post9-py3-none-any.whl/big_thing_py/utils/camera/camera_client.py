__all__ = ['CameraType', 'CameraClient', 'IPCameraSource', 'PiCameraSource']

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
import os
import subprocess
import cv2
import numpy as np
import platform
from typing import List, Union
from typing_extensions import override
from onvif import ONVIFCamera
import asyncio, time

from termcolor import colored, cprint


def is_raspberry_pi() -> bool:
    return (
        platform.uname().system == 'Linux'
        and os.path.isfile('/sys/firmware/devicetree/base/model')
        and 'Raspberry Pi' in open('/sys/firmware/devicetree/base/model').read()
    )


if is_raspberry_pi():
    try:
        from picamera2 import Picamera2
        from picamera2.encoders import H264Encoder
    except ImportError:
        cprint('Picamera2 모듈을 import할 수 없습니다. 라즈베리파이에 올바르게 설치되어 있는지 확인하세요.', 'yellow')
else:
    cprint('이 시스템은 라즈베리파이가 아닙니다. Picamera2를 사용할 수 없습니다.', 'yellow')


def get_os_bit() -> str:
    return platform.architecture()[0]


class CameraClient:
    # DEFAULT_IMAGE_FOLDER = 'capture_images'
    # DEFAULT_VIDEO_FOLDER = 'video_out'
    # DEFAULT_CONFIG_PATH = 'config.json'

    def __init__(
        self,
        camera_source: Union['USBCameraSource', 'IPCameraSource', 'PiCameraSource'],
        resolution: tuple[int, int] = (1280, 960),
        fps: int = 60,
    ) -> None:
        self._camera_source = camera_source
        self._resoultion = resolution
        self._fps = fps

        if not isinstance(camera_source, (USBCameraSource, IPCameraSource, PiCameraSource)):
            raise ValueError('Invalid camera source type')

    async def init(self):
        await self.camera_source.init()

    async def teardown(self):
        await self.camera_source.teardown()

    def save_current_frame(self, filename: str) -> None:
        while self.camera_source.current_frame is None:
            time.sleep(0.1)
        cv2.imwrite(filename, self.camera_source.current_frame)
        cprint(f'Image saved: {filename}', 'green')

    @property
    def camera_source(self) -> Union['USBCameraSource', 'IPCameraSource', 'PiCameraSource']:
        return self._camera_source

    @property
    def resolution(self) -> tuple[int, int]:
        self._resoultion = self._camera_source.resolution
        return self._resolution

    @property
    def fps(self) -> int:
        self._fps = self._camera_source.fps
        return self._fps

    @property
    def is_cam_on(self) -> bool:
        return self._camera_source.is_cam_on

    @camera_source.setter
    def camera_source(self, camera_source: Union['USBCameraSource', 'IPCameraSource', 'PiCameraSource']) -> None:
        self._camera_source = camera_source

    @resolution.setter
    def resolution(self, resolution: tuple[int, int]) -> None:
        self.camera_source.resolution = resolution
        self._resolution = resolution

    @fps.setter
    def fps(self, fps: int) -> None:
        self.camera_source.fps = fps
        self._fps = fps

    # def make_video(self, src_path=DEFAULT_IMAGE_FOLDER, dst_path=DEFAULT_VIDEO_FOLDER, speed=1.0) -> bool:
    #     try:
    #         cprint(f'Make video start. [video path : {dst_path}]')
    #         self._run_capture = False

    #         image_list = glob(f'{src_path}/*.jpg')
    #         image_list.sort()

    #         fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    #         fps = 30.0 * speed
    #         self._vout = cv2.VideoWriter(dst_path, fourcc, fps, (self._width, self._height))

    #         for image in tqdm(image_list, desc='image read'):
    #             frame = cv2.imread(image)
    #             self._vout.write(frame)
    #         self._vout.release()
    #         cprint(f'Make video finish. [video path : {dst_path}]')

    #         return True
    #     except Exception as e:
    #         cprint(e)
    #         return False

    # def start_capture(self) -> None:
    #     if not self._run_capture:
    #         self._run_capture = True
    #     else:
    #         cprint('thread already run now')

    # def stop_capture(self) -> None:
    #     if self._run_capture:
    #         self._run_capture = False
    #     else:
    #         cprint('thread already stop now')

    # def take_timelapse(self, duration: float, speed: float, folder=DEFAULT_IMAGE_FOLDER, video_path=DEFAULT_VIDEO_FOLDER) -> None:
    #     # Calculate the number of frames to capture based on duration and cycle
    #     total_frames = int(duration * 1000 / self._cycle)
    #     self.start_capture()

    #     cprint(f'Starting timelapse for {duration} seconds, capturing {total_frames} frames.')

    #     # Start the timelapse thread
    #     self.run_thread()

    #     # Wait for the timelapse to complete
    #     time.sleep(duration)
    #     self.stop_capture()

    #     cprint('Timelapse capture completed. Creating video...')

    #     # Create the video from captured images
    #     video_filename = os.path.join(video_path, f'timelapse_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4')
    #     success = self.make_video(src_path=folder, dst_path=video_filename, speed=speed)

    #     if success:
    #         cprint(f'Video created successfully: {video_filename}')
    #     else:
    #         cprint('Failed to create video.')

    # def cap_destroy(self) -> None:
    #     os_bit = platform.architecture()[0]
    #     if self._camera_type in [CameraType.USB, CameraType.IP]:
    #         self._cap.release()
    #     elif self._camera_type == CameraType.PICAMERA and os_bit == '64bit':
    #         self._cap.close()

    # def run(self, user_stop_event: Event, folder=DEFAULT_IMAGE_FOLDER) -> None:
    #     cprint(f'Capture start. [image path : ./{folder}/]')

    #     prev_millis = 0
    #     try:
    #         while not user_stop_event.wait(timeout=0.1):
    #             if (int(round(time.time() * 1000)) - prev_millis) > self._cycle and self._run_capture:
    #                 prev_millis = int(round(time.time() * 1000))
    #                 ret, frame = self._cap.read()
    #                 if ret:
    #                     os.makedirs(folder, exist_ok=True)
    #                     image_name = self.generate_image_name(folder)
    #                     now_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    #                     cv2.imwrite(f'{folder}/{image_name}.jpg', frame)
    #                     cprint(f'[{now_datetime}] Capture success! [press "v" to make video]\r')
    #                     self._capture_num += 1
    #                 else:
    #                     cprint('Camera capture failed!')
    #     except KeyboardInterrupt:
    #         cprint('KeyboardInterrupt... end timelapse')
    #         return False
    #     except Exception as e:
    #         cprint(e)
    #         cprint('while loop end')

    # def run_thread(self) -> None:
    #     self._timelapse_thread.start()

    # def generate_image_name(self, folder: str) -> str:
    #     now = datetime.datetime.now()
    #     capture_date = now.strftime('%Y%m%d')
    #     capture_time = now.strftime('%H%M%S')

    #     image_name = '_'.join([capture_date, capture_time])
    #     image_name_duplicate = glob(f'{folder}/*{image_name}*.jpg')

    #     if len(image_name_duplicate) > 1:
    #         tmp_list = []
    #         for image in image_name_duplicate:
    #             name_split = image.split('_')
    #             if len(name_split) > 2:
    #                 index = image.split('_')[-1][:-4]
    #                 tmp_list.append(int(index))
    #         latest_index = max(tmp_list)

    #         image_name = '_'.join([image_name, str(latest_index + 1)])
    #     elif len(image_name_duplicate) == 1:
    #         image_name += '_1'

    #     return image_name

    # def get_supported_resolutions(self) -> List[str]:
    #     command = f'v4l2-ctl -d {self._cap_num} --list-formats-ext'
    #     result = subprocess.run(command.split(), stdout=subprocess.PIPE, text=True)
    #     output = result.stdout
    #     resolutions = re.findall(r'(\d+)x(\d+)', output)
    #     return list(set(resolutions))

    # def camera_capture(self, image_name: str, cam_num: int = 0) -> bool:
    #     ret = False
    #     try:
    #         if is_raspberry_pi():
    #             if self._camera_type == CameraType.PICAMERA:
    #                 ret = self.save_image_from_picamera(filename=image_name)
    #             else:
    #                 ret = self.save_image_from_usb_camera(filename=image_name)
    #         elif platform.uname().system == 'Darwin':
    #             curr_time = time.time()
    #             while time.time() - curr_time < 0.1:
    #                 ret, frame = self._cap.read()
    #                 cv2.waitKey(30)
    #                 cv2.imwrite(image_name, frame)
    #         elif platform.uname().system == 'Windows':
    #             self._cap.release()
    #             self._cap = cv2.VideoCapture(cam_num, cv2.CAP_DSHOW)
    #             ret, frame = self._cap.read()
    #             cv2.imwrite(image_name, frame)
    #         else:
    #             ret = self.save_image_from_usb_camera(filename=image_name)
    #     except:
    #         return False
    #     finally:
    #         if 'cap' in locals() and not is_raspberry_pi():
    #             cap.release()

    #     return ret

    # def save_image_from_picamera(self, filename: str) -> bool:
    #     try:
    #         camera = Picamera2()
    #         camera_config = camera.create_still_configuration(main={'size': (1920, 1080)})
    #         camera.configure(camera_config)
    #         camera.start()
    #         camera.capture_file(filename)
    #         camera.close()
    #         return True
    #     except Exception as e:
    #         cprint(e)
    #         return False

    # def save_image_from_usb_camera(self, filename: str) -> bool:
    #     try:
    #         self._cap.open(self._cap_num)
    #         self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 99999)
    #         self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 99999)
    #         ret, frame = self._cap.read()
    #         cv2.imwrite(filename, frame)
    #         self._cap.release()
    #         return True
    #     except:
    #         return False

    # def get_cap(self) -> cv2.VideoCapture:
    #     return self._cap


class CameraSource(metaclass=ABCMeta):
    def __init__(
        self,
        resolution: tuple[int, int] = (1280, 960),
        fps: int = 60,
    ):
        self._resolution = resolution
        self._fps = fps
        self._cap: cv2.VideoCapture = None
        self._is_cam_on = False
        self._current_frame: Union[None, np.ndarray] = None
        # self._capture_frame_task: asyncio.Task = None

    async def init(self) -> None:
        self.cam_on()
        self.cam_off()

        # self._capture_frame_task = asyncio.create_task(self.capture_frame_task())
        await asyncio.sleep(0)
        cprint('Camera source initialized.', 'green')

    async def teardown(self) -> None:
        self.cam_off()

        # if self._capture_frame_task:
        #     self._capture_frame_task.cancel()
        #     try:
        #         await self._capture_frame_task
        #     except asyncio.CancelledError:
        #         pass

        cprint('Camera source teardown.', 'yellow')

    # async def capture_frame_task(self) -> None:
    #     while True:
    #         if self._cam_on and self._cap:
    #             ret, frame = self._cap.read()
    #             if ret:
    #                 self._current_frame = frame
    #         await asyncio.sleep(1 / self._fps)

    @abstractmethod
    def cam_on(self) -> None: ...

    @abstractmethod
    def cam_off(self) -> None: ...

    @property
    def resolution(self) -> tuple[int, int]:
        return self._resolution

    @property
    def fps(self) -> int:
        return self._fps

    @property
    def is_cam_on(self) -> bool:
        return self._is_cam_on

    @resolution.setter
    def resolution(self, resolution: tuple[int, int]) -> None:
        self._resolution = resolution
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

    @fps.setter
    def fps(self, fps: int) -> None:
        self._fps = fps
        self._cap.set(cv2.CAP_PROP_FPS, fps)

    @property
    def current_frame(self) -> Union[None, np.ndarray]:
        ret, frame = self._cap.read()
        if ret:
            self._current_frame = frame
        else:
            cprint('Cannot read frame from camera.', 'red')
        return self._current_frame


class USBCameraSource(CameraSource):

    def __init__(
        self,
        device_num: int = 0,
        resolution: tuple[int, int] = (640, 480),
        fps: int = 60,
        auto_detect: bool = False,
    ) -> None:
        super().__init__(resolution=resolution, fps=fps)

        self._device_num = device_num
        self._resoultion = resolution
        self._fps = fps

        self._auto_detect = auto_detect
        self._last_camera_index: int = None

    @override
    def cam_on(self) -> None:
        if self._cap is None:
            if self._last_camera_index:
                self._cap = cv2.VideoCapture(self._last_camera_index)
            elif self._auto_detect:
                index = self._get_usb_camera()
                self._cap = cv2.VideoCapture(index)
                self._last_camera_index = index
            else:
                self._cap = cv2.VideoCapture(self._device_num)
                self._last_camera_index = self._device_num

            if not self._cap.isOpened():
                raise ValueError(f'Cannot open camera at index {self._last_camera_index}')

            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._resoultion[0])
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._resoultion[1])
        else:
            cprint('Camera is already on.', 'yellow')

        self._cam_on = True

    @override
    def cam_off(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None
        else:
            cprint('Camera is already off.', 'yellow')

        self._cam_on = False

    def _get_usb_camera(self) -> int:
        camera_indices = []
        try:
            result = subprocess.run(['v4l2-ctl', '--list-devices'], capture_output=True, text=True, check=True)
            devices = result.stdout.split('\n')

            for i, line in enumerate(devices):
                if 'usb' in line.lower():
                    if i + 1 < len(devices):
                        device_path = devices[i + 1].strip()
                        if '/dev/video' in device_path:
                            index = int(device_path.replace('/dev/video', ''))
                            camera_indices.append(index)
        except FileNotFoundError:
            cprint('v4l2-ctl not found. Run ./samples/utils/camera/setup.sh script first. Falling back to default index search.', 'yellow')
        except subprocess.CalledProcessError as e:
            cprint(f'Error listing video devices: {e}. Falling back to default index search.')

        if not camera_indices:
            max_tested_cameras = 10
            camera_indices = list(range(max_tested_cameras))

        for index in camera_indices:
            return index
        else:
            raise ValueError('No USB camera found.', 'red')


@dataclass
class RTSPStream:
    host: str
    port: int
    user: str
    password: str
    stream_path: str

    def uri(self) -> str:
        return f'rtsp://{self.user}:{self.password}@{self.host}:{self.port}/{self.stream_path}'


class ONVIFSource:
    def __init__(self, host: str, port: int, user: str, password: str) -> None:
        self._host: str = host
        self._port: int = port
        self._user: str = user
        self._password: str = password
        self._rtsp_stream_list: List[RTSPStream] = []

    def load_onvif(self) -> cv2.VideoCapture:
        my_onvif_source = ONVIFCamera(self._host, self._port, self._user, self._password)
        media = my_onvif_source.create_media_service()
        profiles = media.GetProfiles()
        profile = profiles[0]
        request = media.create_type('GetStreamUri')
        request.ProfileToken = profile.token
        request.StreamSetup = {'Stream': 'RTP-Unicast', 'Transport': {'Protocol': 'RTSP'}}
        response = media.GetStreamUri(request)
        rtsp_stream = RTSPStream(host=self._host, port=self._port, user=self._user, password=self._password, stream_path=response.Uri)
        self._rtsp_stream_list.append(rtsp_stream)

    def print_stream_list(self) -> None:
        for rtsp_stream in self._rtsp_stream_list:
            cprint(rtsp_stream.uri())

    def get_rtsp_stream(self, stream_path: str = '') -> RTSPStream:
        if stream_path:
            for rtsp_stream in self._rtsp_stream_list:
                if rtsp_stream.stream_path == stream_path:
                    return rtsp_stream
        else:
            return self._rtsp_stream_list[0]


class IPCameraSource(CameraSource):
    def __init__(
        self,
        source: Union[RTSPStream, ONVIFSource],
        resolution: tuple[int, int] = (1280, 960),
        fps: int = 60,
    ) -> None:
        '''
        Support below devices

            - C200 Tapo Camera

        '''
        super().__init__(resolution=resolution, fps=fps)

        self._source = source
        self._resoultion = resolution
        self._fps = fps

        self._onvif_source: ONVIFSource = None

    @override
    def cam_on(self) -> None:
        if self._cap is None:
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"
            if isinstance(self._source, RTSPStream):
                uri = self._source.uri()
                self._cap = cv2.VideoCapture(uri, cv2.CAP_FFMPEG)
            elif isinstance(self._source, ONVIFSource):
                self._onvif_source = self._source
                self._onvif_source.load_onvif()
                uri = self._source.get_rtsp_stream('stream2').uri()
                self._cap = cv2.VideoCapture(uri, cv2.CAP_FFMPEG)

            if not self._cap.isOpened():
                raise ValueError(f'Cannot open camera at uri {uri}')

            self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            # self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 99999)
            # self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 99999)
        else:
            cprint('Camera is already on.', 'yellow')

        self._cam_on = True

    @override
    def cam_off(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None
        else:
            cprint('Camera is already off.', 'yellow')

        self._cam_on = False

    def show_stream(self) -> None:
        while True:
            cv2.imshow('Camera Stream', self.current_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()


# TODO (thsvkd): Implement PiCamera class
class PiCameraSource(CameraSource):

    def __init__(
        self,
        resolution: tuple[int, int] = (1280, 960),
        fps: int = 60,
    ):
        super().__init__(resolution=resolution, fps=fps)

        self._resolution = resolution
        self._fps = fps
        self.picam2 = Picamera2()
        self.config = self.picam2.create_still_configuration(main={'size': self.resolution})
        self.picam2.configure(self.config)

    @override
    def cam_on(self) -> None:
        self.picam2.start()
        # time.sleep(0.5)  # Wait for camera initialization

        self._cam_on = True

    @override
    def cam_off(self) -> None:
        self.picam2.stop()

        self._cam_on = False

    # def capture_image(self, filename='image.jpg'):
    #     self.picam2.capture_file(filename)
    #     cprint(f'Image captured: {filename}')

    # def start_preview(self):
    #     self.picam2.start_preview()

    # def stop_preview(self):
    #     self.picam2.stop_preview()

    # def record_video(self, filename='video.h264', duration=10, bitrate=10000000):
    #     video_config = self.picam2.create_video_configuration()
    #     self.picam2.configure(video_config)
    #     encoder = H264Encoder(bitrate=bitrate)
    #     self.picam2.start_recording(encoder, filename)
    #     cprint(f'Recording video for {duration} seconds...')
    #     time.sleep(duration)
    #     self.picam2.stop_recording()
    #     cprint(f'Video recorded: {filename}')

    # def change_resolution(self, resolution):
    #     self.resolution = resolution
    #     self.config = self.picam2.create_still_configuration(main={'size': self.resolution})
    #     self.picam2.configure(self.config)

    # def set_controls(self, controls):
    #     self.picam2.set_controls(controls)


if __name__ == '__main__':

    async def rtsp_test(file_mode: bool = False):
        try:
            camera_source = IPCameraSource(
                source=RTSPStream(
                    host='localhost',
                    port=554,
                    user='USER',
                    password='PASSWORD',
                    stream_path='stream2',
                )
            )
            camera_client = CameraClient(camera_source=camera_source)
            await camera_client.init()
            camera_client.camera_source.cam_off()
            camera_client.camera_source.cam_on()
            if file_mode:
                camera_client.save_current_frame('test.jpg')
            else:
                camera_source.show_stream()
        except KeyboardInterrupt:
            await camera_client.teardown()

    # async def onvif_test():
    #     try:
    #         camera_source = IPCameraSource(source=ONVIFSource(host='', port=2020, user='', password=''))
    #         camera_client = CameraClient(camera_source=camera_source)
    #         await camera_client.init()
    #         camera_client.save_current_frame('test.jpg')
    #     except KeyboardInterrupt:
    #         await camera_client.teardown()

    async def usb_cam_test():
        try:
            camera_source = USBCameraSource(auto_detect=True)
            camera_client = CameraClient(camera_source=camera_source)
            await camera_client.init()
            camera_client.save_current_frame('test.jpg')
        except KeyboardInterrupt:
            await camera_client.teardown()

    # asyncio.run(onvif_test())
    asyncio.run(rtsp_test(file_mode=False))
    # asyncio.run(usb_cam_test())
