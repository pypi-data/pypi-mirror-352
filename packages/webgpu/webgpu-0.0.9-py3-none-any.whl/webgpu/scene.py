import math
import time
from threading import Timer

from . import platform
from .canvas import Canvas
from .renderer import BaseRenderer, RenderOptions
from .utils import is_pyodide, max_bounding_box
from .webgpu_api import *

_TARGET_FPS = 60


def debounce(render_function):
    if platform.is_pyodide:
        return render_function

    # Render only once every 1/_TARGET_FPS seconds
    def debounced(*args, **kwargs):
        if debounced.timer is not None:
            # we already have a render scheduled, so do nothing
            return

        def f():
            # clear the timer, so we can schedule a new one with the next function call
            t = time.time()
            render_function(*args, **kwargs)
            debounced.timer = None
            debounced.t_last = t

        t_wait = max(1 / _TARGET_FPS - (time.time() - debounced.t_last), 0)
        debounced.timer = Timer(t_wait, f)
        debounced.timer.start()

    debounced.timer = None
    debounced.t_last = time.time()
    return debounced


class Scene:
    canvas: Canvas = None
    render_objects: list[BaseRenderer]
    options: RenderOptions
    gui: object = None

    def __init__(
        self,
        render_objects: list[BaseRenderer],
        id: str | None = None,
        canvas: Canvas | None = None,
    ):
        if id is None:
            import uuid

            id = str(uuid.uuid4())
        import threading
        self.redraw_mutex = threading.Lock()

        self._id = id
        self.render_objects = render_objects

        if is_pyodide:
            _scenes_by_id[id] = self
            if canvas is not None:
                self.init(canvas)

        self.t_last = 0

    def __repr__(self):
        return ""

    @property
    def id(self) -> str:
        return self._id

    @property
    def device(self) -> Device:
        return self.canvas.device

    def init(self, canvas):
        self.canvas = canvas
        self.options = RenderOptions(self.canvas)

        self.options.timestamp = time.time()
        for obj in self.render_objects:
            obj._update_and_create_render_pipeline(self.options)

        pmin, pmax = max_bounding_box([o.get_bounding_box() for o in self.render_objects])
        camera = self.options.camera
        camera.transform._center = 0.5 * (pmin + pmax)

        def norm(v):
            return max(math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2), 1e-6)

        camera.transform._scale = 2 / norm(pmax - pmin)
        if not (pmin[2] == 0 and pmax[2] == 0):
            camera.transform.rotate(270, 0)
            camera.transform.rotate(0, -20)
            camera.transform.rotate(20, 0)

        self._js_render = platform.create_proxy(self._render_direct)
        camera.register_callbacks(canvas.input_handler, self.render)
        self.options.update_buffers()
        if is_pyodide:
            _scenes_by_id[self.id] = self

        canvas.on_resize(self.render)

    def _render_objects(self, to_canvas=True):
        options = self.options
        for obj in self.render_objects:
            if obj.active:
                obj._update_and_create_render_pipeline(options)

        options.command_encoder = self.device.createCommandEncoder()
        for obj in self.render_objects:
            if obj.active:
                obj.render(options)

        if to_canvas:
            options.command_encoder.copyTextureToTexture(
                TexelCopyTextureInfo(self.canvas.target_texture),
                TexelCopyTextureInfo(self.canvas.context.getCurrentTexture()),
                [self.canvas.width, self.canvas.height, 1],
            )
        self.device.queue.submit([options.command_encoder.finish()])
        options.command_encoder = None

    def _redraw_blocking(self):
        with self.redraw_mutex:
            import time

            self.options.timestamp = time.time()
            for obj in self.render_objects:
                obj._update_and_create_render_pipeline(self.options)

            self.render()

    @debounce
    def _redraw_debounced(self):
        self._redraw_blocking()

    def redraw(self, blocking=False):
        if blocking:
            self._redraw_blocking()
        else:
            self._redraw_debounced()

    def _render(self):
        platform.js.requestAnimationFrame(self._js_render)

    def _render_direct(self, t=0):
        self._render_objects(to_canvas=True)

    @debounce
    def render(self, t=0):
        # self.canvas.resize()

        if is_pyodide:
            self._render()
            return
        # print("render")
        # print("canvas", self.canvas.canvas)
        # from . import proxy
        # proxy.js.console.log("canvas", self.canvas.canvas)
        # print("canvas size ", self.canvas.canvas.width, self.canvas.canvas.height)
        # print(
        #     "texture size",
        #     self.canvas.target_texture.width,
        #     self.canvas.target_texture.height,
        # )
        with self.redraw_mutex:
            self._render_objects(to_canvas=False)

            if not is_pyodide:
                platform.js.patchedRequestAnimationFrame(
                    self.canvas.device.handle,
                    self.canvas.context,
                    self.canvas.target_texture,
                )

    def cleanup(self):
        with self.redraw_mutex:
            if self.canvas is not None:
                self.options.camera.unregister_callbacks(self.canvas.input_handler)
                self.options.camera._render_function = None
                self.canvas.input_handler.unregister_callbacks()
                platform.destroy_proxy(self._js_render)
                del self._js_render
                self.canvas._on_resize_callbacks.remove(self.render)
                self.canvas = None

                if is_pyodide:
                    del _scenes_by_id[self.id]


if is_pyodide:
    _scenes_by_id: dict[str, Scene] = {}

    def get_scene(id: str) -> Scene:
        return _scenes_by_id[id]

    def redraw_scene(id: str):
        get_scene(id).redraw()
