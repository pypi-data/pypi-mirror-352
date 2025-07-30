"""
Health and Status logic
"""

from collections import defaultdict, deque
from dataclasses import dataclass
import traceback
import time
import statistics
from typing import Callable
import avesterra as av
from . import sysmon


@dataclass
class CallStat:
    restime: float
    """Response time of the call in seconds"""
    timestamp: float
    """Timestamp at which the call was made"""
    success: bool
    """Whether the call was successful or not"""


g_routes: dict[str, deque[CallStat]] = defaultdict(lambda: deque[CallStat](maxlen=100))


class MonitorStats:
    def __init__(self, name: str):
        self.name = name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        del exc_value, traceback
        end_time = time.time()
        assert self.start_time is not None

        g_routes[self.name].append(
            CallStat(
                restime=end_time - self.start_time,
                timestamp=self.start_time,
                success=exc_type is None,
            )
        )


def health_n_status_thread(
    component: av.AvEntity,
    authorization: av.AvAuthorization,
    statusfn: Callable[[], str],
):
    """
    Regularly publishes health and status, using the measurements done by the
    `measure` decorator function
    """
    while True:
        try:
            status = statusfn()
        except Exception as e:
            av.av_log.error(
                f"Exception raised in the health status function: {e}, default to RED"
            )
            status = "RED"
        try:
            _refresh_hns(component, authorization, status)
            time.sleep(10)
        except Exception:
            av.av_log.error(
                f"/!\\ bug in orchestra-toolkit library: Uncaught exception while reporting health status: {traceback.format_exc()}"
            )


def _refresh_hns(
    component: av.AvEntity, authorization: av.AvAuthorization, status: str
):
    try:
        sysmon.refresh_status(component, status, "GREEN", authorization)
    except Exception as e:
        av.av_log.warn(f"Invoke to sysmon failed: {e}")

    model = av.AvialModel()
    for name, metrics in g_routes.items():
        if not metrics:
            continue

        restime_ordered = sorted(s.restime for s in metrics)
        avg_response_time = sum(restime_ordered) / len(restime_ordered)
        timespan = time.time() - metrics[0].timestamp

        d = {
            "sample size": av.AvValue.encode_integer(len(metrics)),
            "avg response time": av.AvValue.encode_float(round(avg_response_time, 4)),
            "avg call per minute": av.AvValue.encode_float(
                round(len(metrics) / (timespan / 60.0), 1)
            ),
            "success rate %": av.AvValue.encode_float(
                round(sum(100 for s in metrics if s.success) / len(metrics), 1)
            ),
        }
        if len(metrics) > 1:

            d |= {
                "response time stddev": av.AvValue.encode_float(
                    round(statistics.stdev(restime_ordered), 4)
                ),
                "response time p01": av.AvValue.encode_float(
                    round(restime_ordered[int(len(metrics) * 0.01)], 4)
                ),
                "response time p10": av.AvValue.encode_float(
                    round(restime_ordered[int(len(metrics) * 0.1)], 4)
                ),
                "response time p50": av.AvValue.encode_float(
                    round(restime_ordered[len(metrics) // 2], 4)
                ),
                "response time p90": av.AvValue.encode_float(
                    round(restime_ordered[int(len(metrics) * 0.9)], 4)
                ),
                "response time p99": av.AvValue.encode_float(
                    round(restime_ordered[int(len(metrics) * 0.99)], 4)
                ),
            }
        model.attributes[av.AvAttribute.PERFORMANCE].traits[name].value = (
            av.AvValue.encode_aggregate(d)
        )

    try:
        av.store_entity(
            component,
            value=model.to_interchange(),
            authorization=authorization,
        )
        av.publish_event(
            component,
            event=av.AvEvent.UPDATE,
            attribute=av.AvAttribute.HEALTH,
            authorization=authorization,
        )
    except Exception as e:
        av.av_log.warn(f"Failed to store health and status in outlet: {e}")
