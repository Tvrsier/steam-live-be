from __future__ import annotations

import logging
import threading
import time
from queue import Queue, Empty
from collections import deque
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Dict, Optional

import httpx

from src.lib.steam import SteamInterface, SteamEndpointName
from src.lib.steam import validate_interface_endpoint
from src.logger import appLogger
from src.lib.steam.client.utils import SteamRequestParams, SteamApiError
from src.lib.config import get_settings


@dataclass
class _RequestJob:
    """
    A dataclass representing a single request job to be processed by the Steam API.
    The caller shall be in idle state waiting for the `done_event` to be set.
    """
    url: str
    params: SteamRequestParams
    response: Optional[Dict[str, Any]] = None
    error: Optional[BaseException] = None
    done_event: threading.Event = threading.Event()


class Helper:
    """
    Sync motor that handles Steam API requests:
    - daily rate limit
    - burst limit (5 minute window)
    - FIFO queue of jobs
    - Single thread worker processing jobs in order
    """
    settings = get_settings()
    DEFAULT_RATE_LIMIT = settings.rate_limit
    DEFAULT_BURST_LIMIT = settings.burst_limit
    DEFAULT_BURST_WINDOW_SECONDS = settings.burst_window_seconds

    DEFAULT_RATE_WARN_THRESHOLD = settings.rate_warn_threshold
    DEFAULT_BURST_WARN_THRESHOLD = settings.burst_warn_threshold

    del settings

    def __init__(
            self,
            rate_limit: int = DEFAULT_RATE_LIMIT,
            burst_limit: int = DEFAULT_BURST_LIMIT,
            burst_window_seconds: int = DEFAULT_BURST_WINDOW_SECONDS,
            rate_warn_threshold: float = DEFAULT_RATE_WARN_THRESHOLD,
            burst_warn_threshold: float = DEFAULT_BURST_WARN_THRESHOLD,
            logger: Optional[logging.Logger] = None
    ):
        self._rate_limit = rate_limit
        self._burst_limit = burst_limit
        self._burst_window = timedelta(seconds=burst_window_seconds)
        self._rate_warn_threshold = rate_warn_threshold
        self._burst_warn_threshold = burst_warn_threshold

        self._rate_counter = 0
        self._rate_day: date = datetime.now().date()

        self._burst_timestamps: deque[datetime] = deque()

        self._lock = threading.Lock()
        self._queue: Queue[_RequestJob] = Queue()
        self._stop_event = threading.Event()

        self._logger = logger or appLogger

        self._worker_thread = threading.Thread(
            target=self._worker_loop,
            name="SteamClientHelperWorker",
            daemon=True
        )

        self._worker_thread.start()
        self._logger.debug("Steam Helper initialized: rate_limit=%d, burst_limit=%d, burst_window=%ss",
                           self._rate_limit, self._burst_limit, self._burst_window.total_seconds())

    def _request(
            self,
            url: str,
            params: Optional[SteamRequestParams] = None
    ) -> Dict[str, Any]:
        """
        Internal entry point. The request will be enqueued and wait for the result.
        Entrust this for:
        - No concurrency towards Steam API
        - Rate limit respect
        """
        params = params or SteamRequestParams()
        job = _RequestJob(url=url, params=params)

        self._logger.debug("Enqueuing request: url=%s, params=%s", url, params)
        self._queue.put(job)

        job.done_event.wait()

        if job.error is not None:
            err = SteamApiError("No response set for completed job.")
            self._logger.error("Request finished without response: url=%s, error=%s", url, job.error)
            raise err

        self._logger.debug("Request completed: url=%s", url)
        return job.response  # type: ignore[return-value]

    @staticmethod
    @validate_interface_endpoint
    def _build_url(interface: SteamInterface, endpoint: SteamEndpointName, version: int | None = None) -> str:
        settings = get_settings()
        base = settings.steam_api_base_url.rstrip("/")
        v = version or settings.steam_api_default_version

        return f"{base}/{interface.value}/{endpoint.value}/v{v}/"

    def _worker_loop(self) -> None:
        """
        Main worker loop
        Extracts jobs from the FIFO, calls Steam and apply rate limits
        :return:
        """
        self._logger.info("Steam Helper worker thread started.")

        while not self._stop_event.is_set():
            try:
                job = self._queue.get(timeout=0.5)
            except Empty:
                continue

            try:
                self._execute_job(job)
            finally:
                self._queue.task_done()

        self._logger.info("Steam Helper worker thread stopped.")

    def _execute_job(self, job: _RequestJob) -> None:
        """
        Execute a single job:
        - If rate limits are exceeded, wait accordingly
        - Calls Steam API
        - populates job response or error
        :return:
        """
        try:
            self._wait_rate_slots()

            start = time.monotonic()
            self._logger.debug("Performing HTTP call: url=%s", job.url)

            response = self._call_api(job.url, job.params)

            elapsed = time.monotonic() - start
            self._logger.debug("HTTP call completed in %.2fs: url=%s", elapsed, job.url)

            job.response = response
        except BaseException as e:
            job.error = e
        finally:
            job.done_event.set()

    @staticmethod
    def _call_api(url: str, params: SteamRequestParams) -> Dict[str, Any]:
        query = params.as_query()

        try:
            if params.call_method == "get":
                resp = httpx.get(url=url, params=query, timeout=10.0)
            else:
                resp = httpx.post(url=url, params=query, timeout=10.0)

            resp.raise_for_status()
            data = resp.json()

        except httpx.HTTPError as e:
            raise SteamApiError(f"HTTP error occurred: {e}") from e
        except Exception as e:
            raise SteamApiError(f"Unexpected error while calling Steam API: {e}") from e

        if not isinstance(data, dict):
            raise SteamApiError("Invalid response format from Steam API.")

        return data

    def _wait_rate_slots(self) -> None:
        """
        Apply rate limiting and burst limiting.
        When needed, it waits before allowing the request.
        :return:
        """
        while True:
            with self._lock:
                self._reset_daily_counter()
                self._clean_burst_window()

                if self._rate_counter >= self._rate_limit:
                    msg = f"Daily rate limit reached: {self._rate_counter} / {self._rate_limit}"
                    self._logger.error(msg)
                    raise SteamApiError(msg)

                if self._rate_counter >= self._rate_warn_threshold * self._rate_limit:
                    self._logger.warning("Daily rate limit threshold reached: %d / %d",
                                         self._rate_counter, self._rate_limit)

                burst_count = len(self._burst_timestamps)
                if burst_count >= self._burst_limit:
                    oldest = self._burst_timestamps[0]
                    now = datetime.now()
                    delta = (oldest + self._burst_window) - now

                    wait_seconds = max(delta.total_seconds(), 0.0)
                    self._logger.debug("Burst limit reached (%d / %d). Waiting %.2fs",
                                       burst_count, self._burst_limit, wait_seconds)
                else:
                    self._rate_counter += 1
                    self._burst_timestamps.append(datetime.now())

                    if burst_count >= self._burst_warn_threshold * self._burst_limit:
                        self._logger.warning("Burst limit threshold reached: %d / %d",
                                             burst_count, self._burst_limit)

                        return

                time.sleep(wait_seconds)

    def _reset_daily_counter(self) -> None:
        """
        Resets the daily rate counter every 24 hours
        :return:
        """
        today = datetime.now().date()
        if today != self._rate_counter:
            self._logger.info("Resetting daily counter")
            self._rate_day = today
            self._rate_counter = 0

    def _clean_burst_window(self) -> None:
        """
        Removes all timestamps outside the burst window
        :return:
        """
        now = datetime.now()
        window_start = now - self._burst_window

        while self._burst_timestamps and self._burst_timestamps[0] < window_start:
            self._burst_timestamps.popleft()

    def shutdown(self, wait: bool = True) -> None:
        """
        Stops the worker thread gracefully.
        :return:
        """
        self._logger.info("Shutting down Steam Helper...")
        self._stop_event.set()
        if wait:
            self._worker_thread.join(timeout=5.0)
            if self._worker_thread.is_alive():
                self._logger.warning("Steam Helper worker thread did not terminate in time.")

    def __del__(self) -> None:
        # noinspection PyBroadException
        try:
            self.shutdown(wait=False)
        except Exception:
            pass
