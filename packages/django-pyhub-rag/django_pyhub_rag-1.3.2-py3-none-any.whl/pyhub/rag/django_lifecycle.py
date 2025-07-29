from typing import Any

from django.core.exceptions import ImproperlyConfigured

try:
    import numpy as np
except ImportError:
    np = None

from django_lifecycle import model_state as orig_model_state


class NewModelState(orig_model_state.ModelState):

    def __init__(self, initial_state: dict[str, Any]):
        super().__init__(initial_state)

        # ndarray 값은 bool 판단을 지원하지 않습니다.
        # 그래서 bool 판단을 지원하는 tuple로 변환을 합니다.
        for k in self.initial_state:
            v = self.initial_state[k]

            if np is None:
                raise ImproperlyConfigured("Please install the numpy package")

            if isinstance(v, np.ndarray):
                self.initial_state[k] = tuple(v)


setattr(orig_model_state, "ModelState", NewModelState)
