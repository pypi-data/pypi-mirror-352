"""Vector store registry and configuration management."""

import logging
from typing import Dict, Any, Optional

from pyhub import load_toml
from pyhub.config import DEFAULT_TOML_PATH
from .backends import get_backend_class, list_backends
from .backends.base import BaseVectorStore

logger = logging.getLogger(__name__)


class VectorStoreRegistry:
    """벡터 스토어 레지스트리 및 설정 관리자."""
    
    def __init__(self, toml_path: Optional[str] = None):
        """
        레지스트리를 초기화합니다.
        
        Args:
            toml_path: TOML 설정 파일 경로
        """
        self.toml_path = toml_path or DEFAULT_TOML_PATH
        self._config = None
        self._instances: Dict[str, BaseVectorStore] = {}
    
    @property
    def config(self) -> Dict[str, Any]:
        """RAG 설정을 반환합니다."""
        if self._config is None:
            self._load_config()
        return self._config
    
    def _load_config(self) -> None:
        """TOML 파일에서 설정을 로드합니다."""
        try:
            # TOML 파일 직접 파싱
            import toml
            if self.toml_path.exists():
                with open(self.toml_path, "r", encoding="utf-8") as f:
                    toml_data = toml.load(f)
                    self._config = toml_data.get("rag", {})
            else:
                self._config = {}
        except Exception as e:
            logger.warning(f"Failed to load TOML config: {e}")
            self._config = {}
        
        # 기본값 설정
        if "default_backend" not in self._config:
            self._config["default_backend"] = "sqlite-vec"
        
        if "backends" not in self._config:
            self._config["backends"] = {}
    
    def get_default_backend(self) -> str:
        """기본 백엔드 이름을 반환합니다."""
        return self.config.get("default_backend", "sqlite-vec")
    
    def get_backend_config(self, backend_name: str) -> Dict[str, Any]:
        """특정 백엔드의 설정을 반환합니다."""
        backends_config = self.config.get("backends", {})
        backend_config = backends_config.get(backend_name, {})
        
        # 백엔드가 활성화되어 있는지 확인
        if not backend_config.get("enabled", True):
            raise ValueError(f"Backend '{backend_name}' is disabled in configuration")
        
        return backend_config
    
    def create_backend(
        self, 
        backend_name: Optional[str] = None,
        **override_config
    ) -> BaseVectorStore:
        """
        백엔드 인스턴스를 생성합니다.
        
        Args:
            backend_name: 백엔드 이름 (None이면 기본 백엔드 사용)
            **override_config: 설정 오버라이드
            
        Returns:
            백엔드 인스턴스
        """
        if backend_name is None:
            backend_name = self.get_default_backend()
        
        # 캐시 확인
        cache_key = f"{backend_name}:{hash(frozenset(override_config.items()))}"
        if cache_key in self._instances:
            return self._instances[cache_key]
        
        # 백엔드 클래스 로드
        backend_class = get_backend_class(backend_name)
        
        # 설정 병합
        config = self.get_backend_config(backend_name).copy()
        config.update(override_config)
        
        # 인스턴스 생성
        instance = backend_class(config)
        
        # 캐시 저장
        self._instances[cache_key] = instance
        
        return instance
    
    def list_available_backends(self) -> list[str]:
        """사용 가능한 백엔드 목록을 반환합니다."""
        available = []
        
        for backend_name in list_backends():
            try:
                instance = self.create_backend(backend_name)
                if instance.is_available():
                    available.append(backend_name)
            except Exception as e:
                logger.debug(f"Backend {backend_name} not available: {e}")
        
        return available


# 전역 레지스트리 인스턴스
_registry = None


def get_registry() -> VectorStoreRegistry:
    """전역 레지스트리 인스턴스를 반환합니다."""
    global _registry
    if _registry is None:
        _registry = VectorStoreRegistry()
    return _registry


def get_vector_store(
    backend_name: Optional[str] = None,
    **config
) -> BaseVectorStore:
    """
    벡터 스토어 인스턴스를 반환합니다.
    
    Args:
        backend_name: 백엔드 이름 (None이면 기본 백엔드 사용)
        **config: 설정 오버라이드
        
    Returns:
        벡터 스토어 인스턴스
    """
    return get_registry().create_backend(backend_name, **config)


def list_available_backends() -> list[str]:
    """사용 가능한 백엔드 목록을 반환합니다."""
    return get_registry().list_available_backends()


__all__ = [
    "VectorStoreRegistry",
    "get_registry",
    "get_vector_store",
    "list_available_backends",
]