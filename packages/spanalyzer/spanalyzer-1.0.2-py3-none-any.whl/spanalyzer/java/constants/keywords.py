# Keywords for the Java Telemetry Detector

from enum import Enum

from typing import Dict
from typing import List


class JavaTelemetryKeywords(str, Enum):
    """
    Enum containing OpenTelemetry trace keywords used in Java.

    This includes keywords for the following:
    - Tracer Setup
    - Span Context
    - Attributes
    - Events
    - Instrumentation
    """

    # Tracer Setup
    GET_GLOBAL_TRACER = "getGlobalTracer"
    GET_TRACER = "getTracer"
    GET_TRACER_PROVIDER = "getTracerProvider"

    # Span Context
    SPAN_BUILDER = "spanBuilder"
    START_SPAN = "startSpan"
    MAKE_CURRENT = "makeCurrent"
    END = "end"
    CURRENT_SPAN = "currentSpan"

    # Attributes
    SET_ATTRIBUTE = "setAttribute"
    SET_ATTRIBUTES = "setAttributes"

    # Events
    ADD_EVENT = "addEvent"
    ADD_EVENTS = "addEvents"

    # Create Instrumentation
    COUNTER_ADD = "add"

    # Instrumentation
    INSTRUMENT = "instrument"

    @classmethod
    def values(cls) -> set[str]:
        """
        Get all keyword values as a set.
        """
        return {member.value for member in cls}

    @classmethod
    def get_attributes_structure(cls) -> Dict[str, List[str]]:
        """
        Get the attributes structure for categorized OpenTelemetry usage in Java.
        """
        return {
            "tracers": [],
            "spans": [],
            "attributes": [],
            "events": [],
            "counter": [],
        }
