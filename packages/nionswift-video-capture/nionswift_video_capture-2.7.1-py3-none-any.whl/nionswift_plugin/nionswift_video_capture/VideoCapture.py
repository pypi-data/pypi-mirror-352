# standard libraries
import gettext
import logging
import threading
import time
import typing

# third party libraries
import numpy

# local libraries
from nion.ui import Declarative
from nion.utils import Model
from nion.utils import Registry
from nion.utils import StructuredModel

VideoFrameType = numpy.typing.NDArray[typing.Any]

_ = gettext.gettext

# informal measurements show read() takes approx 70ms (14fps)
# on Macbook Pro. CEM 2013-July.
# after further investigation, read() can take about 6ms on same
# computer. to do this, need to read out less frequently (by
# limiting frame rate to 15fps). this means that the next frame
# is constantly ready, so doesn't have to wait for it.
# the hardware manager will happily eat up 100% of python-cpu time.
MAX_FRAME_RATE = 20  # frames per second
MINIMUM_DUTY = 0.05  # seconds
TIMEOUT = 5.0  # seconds

def video_capture_thread(source_url: str, buffer_ref: typing.List[typing.Optional[VideoFrameType]], cancel_event: threading.Event, ready_event: threading.Event, done_event: threading.Event) -> None:
    try:
        video_capture = cv2.VideoCapture(source_url)
        try:
            while not cancel_event.is_set():
                start = time.time()
                retval, image = video_capture.read()
                if retval:
                    buffer_ref[0] = numpy.copy(image)
                    ready_event.set()
                    done_event.wait()
                    done_event.clear()
                    elapsed = time.time() - start
                    delay = max(1.0/MAX_FRAME_RATE - elapsed, MINIMUM_DUTY)
                    cancel_event.wait(delay)
                else:
                    buffer_ref[0] = None
                    ready_event.set()
        finally:
            video_capture.release()
    except Exception as e:
        logging.exception(f"video capture thread exception {e}")


class VideoCamera:

    def __init__(self, camera_id: str, camera_name: str, source: str) -> None:
        self.camera_id = camera_id
        self.camera_name = camera_name
        self.__source = source

    def update_settings(self, settings: typing.Mapping[str, typing.Any]) -> None:
        self.__source = settings.get("camera_index", settings.get("url"))

    def start_acquisition(self) -> None:
        self.buffer_ref: typing.List[typing.Optional[VideoFrameType]] = [None]
        self.cancel_event = threading.Event()
        self.ready_event = threading.Event()
        self.done_event = threading.Event()
        self.thread = threading.Thread(target=video_capture_thread, args=(self.__source, self.buffer_ref, self.cancel_event, self.ready_event, self.done_event))
        self.thread.start()

    def acquire_data(self) -> VideoFrameType:
        if self.ready_event.wait(5.0):
            self.ready_event.clear()
            raw_data = self.buffer_ref[0]
            data = numpy.copy(raw_data) if raw_data is not None else None
            self.done_event.set()
            assert data is not None
            return data
        else:
            raise RuntimeError(f"No frame received {self.__source}")

    def stop_acquisition(self) -> None:
        self.cancel_event.set()
        self.done_event.set()
        self.thread.join()


class VideoDeviceFactory:

    display_name = _("Video Capture")
    factory_id = "nionswift.video_capture"

    def make_video_device(self, settings: typing.Mapping[str, typing.Any]) -> typing.Optional[VideoCamera]:
        if settings.get("driver") == self.factory_id:
            source = settings.get("camera_index", settings.get("url"))
            camera_id = settings["device_id"]
            camera_name = settings["name"]
            video_device = VideoCamera(camera_id, camera_name, source)
            return video_device
        return None

    def describe_settings(self) -> typing.Sequence[typing.Mapping[str, typing.Any]]:
        return [
            {'name': 'camera_index', 'type': 'int'},
            {'name': 'url', 'type': 'string'},
        ]

    def get_editor_description(self) -> typing.Any:
        u = Declarative.DeclarativeUI()

        url_field = u.create_line_edit(text="@binding(settings.url)", width=360)
        camera_index_combo = u.create_combo_box(items=["None", "0", "1", "2", "3"], current_index="@binding(camera_index_model.value)")

        label_column = u.create_column(u.create_label(text=_("URL:")), u.create_label(text=_("Camera Index (0 for none):")), spacing=4)
        field_column = u.create_column(url_field, camera_index_combo, spacing=4)

        return u.create_row(label_column, field_column, u.create_stretch(), spacing=12)

    def create_editor_handler(self, settings: typing.Optional[StructuredModel.ModelLike]) -> typing.Any:

        class EditorHandler(Declarative.Handler):

            def __init__(self, settings: typing.Optional[StructuredModel.ModelLike]) -> None:
                super().__init__()

                self.settings = settings

                self.camera_index_model = Model.PropertyModel[int]()

                def camera_index_changed(index: typing.Optional[int]) -> None:
                    formats = [None, 0, 1, 2, 3]
                    setattr(self.settings, "camera_index", formats[index or 0])

                self.camera_index_model.on_value_changed = camera_index_changed

                camera_index = getattr(self.settings, "camera_index", None)
                self.camera_index_model.value = camera_index + 1 if camera_index is not None else 0

        return EditorHandler(settings)




# see http://docs.opencv.org/index.html
# fail cleanly if not able to import
import_error = False
try:
    import cv2
except ImportError:
    import_error = True


class VideoCaptureExtension:

    # required for Swift to recognize this as an extension class.
    extension_id = "nion.swift.extensions.video_capture"

    def __init__(self, api_broker: typing.Any) -> None:
        # grab the api object.
        api = api_broker.get_api(version="1", ui_version="1")

        global import_error
        if import_error:
            api.raise_requirements_exception(_("Could not import cv2."))

    Registry.register_component(VideoDeviceFactory(), {"video_device_factory"})

    def close(self) -> None:
        pass
