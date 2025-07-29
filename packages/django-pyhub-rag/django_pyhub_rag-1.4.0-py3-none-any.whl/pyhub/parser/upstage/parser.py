import asyncio
import io
import json
import logging
from dataclasses import dataclass
from functools import reduce
from os import environ
from typing import Any, AsyncGenerator, Generator, Optional, cast

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.errors import PdfReadError

from pyhub import PromptTemplates
from pyhub.http import cached_http_async
from pyhub.llm import LLM, AnthropicLLM, GoogleLLM, OllamaLLM, OpenAILLM
from pyhub.llm.base import BaseLLM, DescribeImageRequest
from pyhub.llm.types import (
    GoogleChatModelType,
    LLMChatModelType,
    OpenAIChatModelType,
    Reply,
)
from pyhub.parser.documents import Document

from .settings import (
    DEFAULT_TIMEOUT,
    DOCUMENT_PARSE_API_URL,
    DOCUMENT_PARSE_DEFAULT_MODEL,
    MAX_BATCH_PAGE_SIZE,
)
from .types import (
    DocumentFormatType,
    DocumentSplitStrategyType,
    Element,
    ElementCategoryType,
    ElementContent,
    OCRModeType,
)
from .validators import validate_upstage_document

logger = logging.getLogger(__name__)


@dataclass
class ImageDescriptor:
    llm_model: LLMChatModelType = "gpt-4o-mini"
    llm_api_key: Optional[str] = None
    llm_base_url: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    system_prompts: Optional[dict[str, str]] = None
    user_prompts: Optional[dict[str, str]] = None
    enable_cache: bool = False

    DEFAULT_SYSTEM_PROMPTS = {
        "image": "prompts/describe/image/system.md",
        "table": "prompts/describe/table/system.md",
    }
    DEFAULT_USER_PROMPTS = {
        "image": "prompts/describe/image/user.md",
        "table": "prompts/describe/table/user.md",
    }
    prompt_context: Optional[dict[str, Any]] = None

    def __post_init__(self):
        image_prompt_templates = self.get_prompts("describe_image")
        table_prompt_templates = self.get_prompts("describe_table")

        if self.system_prompts is None or len(self.system_prompts) == 0:
            self.system_prompts = {
                "image": image_prompt_templates["system"],
                "table": table_prompt_templates["system"],
            }

        if self.user_prompts is None or len(self.user_prompts) == 0:
            self.user_prompts = {
                "image": image_prompt_templates["user"],
                "table": table_prompt_templates["user"],
            }

    @classmethod
    def get_prompts(cls, prompt_type: str, use_default_prompts: bool = True) -> PromptTemplates:
        try:
            return PromptTemplates(
                system=settings.PROMPT_TEMPLATES[prompt_type]["system"],
                user=settings.PROMPT_TEMPLATES[prompt_type]["user"],
            )
        except KeyError as e:
            if use_default_prompts:
                return PromptTemplates(
                    system=cls.DEFAULT_SYSTEM_PROMPTS["image"],
                    user=cls.DEFAULT_USER_PROMPTS["image"],
                )
            else:
                raise e

    def __str__(self) -> str:
        """인스턴스 정보를 문자열로 반환합니다. API 키는 제외됩니다."""
        return (
            f"ImageDescriptor(model={self.llm_model}, "
            f"temperature={self.temperature}, max_tokens={self.max_tokens}, "
            f"system_prompts={list(self.system_prompts.keys())}, "
            f"user_prompts={list(self.user_prompts.keys())})"
        )

    def get_llm(self) -> BaseLLM:
        match LLM.get_vendor_from_model(self.llm_model):
            case "openai":
                llm = OpenAILLM(
                    model=cast(OpenAIChatModelType, self.llm_model),
                    api_key=self.llm_api_key,
                    base_url=self.llm_base_url,
                )
            case "anthropic":
                llm = AnthropicLLM(model=self.llm_model, api_key=self.llm_api_key)
            case "google":
                llm = GoogleLLM(model=cast(GoogleChatModelType, self.llm_model), api_key=self.llm_api_key)
            case "ollama":
                llm = OllamaLLM(model=self.llm_model, base_url=self.llm_base_url)
            case _:
                raise ValueError(f"Not Implemented llm vendor for {self.llm_model}")

        return llm

    def get_system_prompt(self, category: ElementCategoryType) -> Optional[str]:
        try:
            return self.system_prompts[category]
        except KeyError:
            return self.system_prompts["image"]

    def get_user_prompt(self, category: ElementCategoryType) -> Optional[str]:
        try:
            return self.user_prompts[category]
        except KeyError:
            return self.user_prompts["image"]


class UpstageDocumentParseParser:
    def __init__(
        self,
        upstage_api_key: Optional[str] = None,
        api_url: str = DOCUMENT_PARSE_API_URL,
        model: str = DOCUMENT_PARSE_DEFAULT_MODEL,
        split: DocumentSplitStrategyType = "page",
        pages: Optional[list[int]] = None,
        start_page: int = 1,
        max_page: Optional[int] = None,
        image_descriptor: ImageDescriptor = None,
        ocr_mode: OCRModeType = "auto",
        document_format: DocumentFormatType = "markdown",
        coordinates: bool = False,
        base64_encoding_category_list: Optional[list[ElementCategoryType]] = None,
        ignore_element_category_list: Optional[list[ElementCategoryType]] = None,
        enable_cache: bool = False,
        verbose: bool = False,
    ):
        """
        UpstageDocumentParseParser 클래스의 인스턴스를 초기화합니다.

        Args:
            upstage_api_key (str, optional): Upstage API 접근을 위한 API 키.
                                     기본값은 None이며, 이 경우 환경 변수
                                     `UPSTAGE_API_KEY`에서 가져옵니다.
            api_url (str, optional): Upstage API 접근을 위한 API URL.
                                     기본값은 DOCUMENT_PARSE_API_URL입니다.
            model (str, optional): 문서 파싱에 사용할 모델.
                                  기본값은 DOCUMENT_PARSE_DEFAULT_MODEL입니다.
            split (SplitType, optional): 적용할 분할 유형.
                                         기본값은 "page"입니다.
                                         옵션:
                                         - "none": 분할 없음, 전체 문서를 단일 청크로 반환합니다.
                                         - "page": 문서를 페이지별로 분할합니다.
                                         - "element": 문서를 개별 요소(단락, 표 등)로 분할합니다.
            pages (list[int], optional): 처리할 페이지 번호 리스트
            start_page (int, optional): 시작 페이지 번호
            max_page (int, optional): 처리할 최대 페이지 수.
                                      None은 모든 페이지를 처리함을 의미합니다. 기본값은 None입니다.
            ocr_mode (OCRMode, optional): OCR을 사용하여 문서의 이미지에서 텍스트를 추출합니다.
                                     기본값은 "auto"입니다.
                                     옵션:
                                     - "force": 이미지에서 텍스트를 추출하기 위해 OCR이 사용됩니다.
                                     - "auto": PDF에서 텍스트가 추출됩니다. (입력이 PDF 형식이 아닌 경우 오류가 발생합니다)
            document_format (DocumentFormat, optional): 추론 결과의 형식.
                                                   기본값은 "html"입니다.
                                                   옵션: "text", "html", "markdown"
            coordinates (bool, optional): 출력에 OCR 좌표를 포함할지 여부.
                                          기본값은 False 입니다.
            base64_encoding_category_list (list[CategoryType], optional): base64로 인코딩할 요소의 카테고리.
                                                        기본값은 빈 리스트입니다.
            ignore_element_category_list (list[CategoryType], optional): 제외할 요소의 카테고리.
                                                        기본값은 빈 리스트입니다.
            enable_cache (bool, optional): API 응답 캐시를 활성화할지 여부.
                                         기본값은 False입니다.
            verbose (bool, optional): 상세한 처리 정보를 표시할지 여부.
                                     기본값은 False입니다.
        """
        self.upstage_api_key = upstage_api_key or environ.get("UPSTAGE_API_KEY")
        self.api_url = api_url
        self.model = model
        self.split = split
        self.pages = pages
        self.start_page = start_page
        self.max_page = max_page
        self.image_descriptor = image_descriptor
        self.ocr_mode = ocr_mode
        self.document_format = document_format
        self.coordinates = coordinates
        self.base64_encoding_category_list = base64_encoding_category_list or []
        self.ignore_element_category_list = ignore_element_category_list or []
        self.validators = [validate_upstage_document]
        self.errors: Optional[list[ValidationError]] = None
        self.enable_cache = enable_cache
        self.verbose = verbose

    def is_valid(self, file: File, raise_exception: bool = False) -> bool:
        """
        파일이 Upstage Document Parse API 제약 조건을 충족하는지 검증합니다.
        검증이 실패하면 self.errors에 검증 오류를 수집합니다.

        Args:
            file (File): 검증할 파일 객체
            raise_exception (bool): True인 경우, 검증 실패 시 ValidationError를 발생시킵니다.
                             기본값은 False입니다.

        Returns:
            bool: 파일이 모든 검증 검사를 통과하면 True, 그렇지 않으면 False.
                  False인 경우, 검증 오류는 self.errors를 통해 접근할 수 있습니다.

        Raises:
            ValidationError: 검증이 실패하고 raise_exception이 True인 경우 발생합니다.
        """

        self.errors = []

        for validator in self.validators:
            try:
                validator(file)
            except ValidationError as e:
                self.errors.append(e)

        valid = len(self.errors) == 0

        if raise_exception and valid is False:
            raise ValidationError(self.errors)

        return valid

    def lazy_parse(
        self,
        file: File,
        batch_page_size: int,
        ignore_validation: bool = False,
    ) -> Generator[Document, None, None]:
        """
        문서를 동기적으로 파싱하고 지정된 분할 유형에 따라 Document 객체를 생성합니다.
        내부적으로는 비동기 lazy_parse 메서드를 실행하고 결과를 동기적으로 반환합니다.
        """

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        async_iter = self.lazy_parse_async(file, batch_page_size, ignore_validation=ignore_validation)

        try:
            while True:
                try:
                    document = loop.run_until_complete(async_iter.__anext__())
                    yield document
                except StopAsyncIteration:
                    break
        except Exception as e:
            raise ValueError(str(e)) from e

    async def lazy_parse_async(
        self,
        file: File,
        batch_page_size: int,
        ignore_validation: bool = False,
    ) -> AsyncGenerator[Document, None]:
        """
        문서를 비동기적으로 파싱하고 지정된 분할 유형에 따라 Document 객체를 생성합니다.

        Args:
            file (File): 파싱할 입력 파일 객체.
            batch_page_size (int): 한 번에 처리할 페이지 수.
            ignore_validation (bool): 파일 검증을 건너뛸지 여부.
                                      기본값은 False입니다.

        Returns:
            AsyncGenerator[Document, None]: 파싱된 문서 객체들의 비동기 반복자.

        Raises:
            ValueError: 유효하지 않은 분할 유형이 제공되거나 파일 검증이 실패한 경우 발생합니다.
        """

        if ignore_validation is False:
            if not self.is_valid(file):
                logger.debug("파일 검증 실패: %s", self.errors)
                raise ValueError(f"파일 검증 실패: {self.errors}")
            logger.debug("파일 검증 성공")

        if self.split == "none":
            element_list = []
            async for element in self._generate_elements(file, batch_page_size):
                element_list.append(element)
            merged_element = reduce(lambda x, y: x + y, element_list)
            merged_element.coordinates = []
            document = merged_element.to_document(self.document_format)

            logger.debug(
                "문서를 %d 글자와 %d 메타데이터 항목으로 생성했습니다",
                len(document.page_content),
                len(document.metadata),
            )

            yield document

        elif self.split == "element":
            async for element in self._generate_elements(file, batch_page_size):
                yield element.to_document(self.document_format)

        elif self.split == "page":
            page_group_dict = {}
            async for element in self._generate_elements(file, batch_page_size):
                if element.page not in page_group_dict:
                    page_group_dict[element.page] = []
                page_group_dict[element.page].append(element)

            page_set: list[int] = sorted(page_group_dict.keys())

            for page in page_set:
                group: list[Element] = page_group_dict[page]
                page_element = reduce(lambda x, y: x + y, group)
                page_element.coordinates = []
                yield page_element.to_document(self.document_format)

        else:
            logger.debug("유효하지 않은 분할 유형이 제공되었습니다: %s", self.split)

            raise ValueError(f"유효하지 않은 분할 유형: {self.split}")

    async def _generate_elements(self, file: File, batch_page_size: int) -> AsyncGenerator[Element, None]:
        """
        파일을 처리하여 Element 객체들을 생성하는 비동기 제너레이터입니다.

        Args:
            file (File): 처리할 파일 객체
            batch_page_size (int): 한 번에 처리할 페이지 수

        Returns:
            AsyncGenerator[Element, None]: Element 객체들의 비동기 제너레이터

        Raises:
            ValueError: PDF 파일 읽기 실패 또는 batch_page_size가 최대 허용 페이지 수를 초과할 경우 발생합니다.
        """
        try:
            full_docs = PdfReader(file)
            total_pages = len(full_docs.pages)
            is_pdf = True
            logger.info("PDF 파일 : 총 %d 페이지", total_pages)
        except PdfReadError:
            logger.debug("파일이 PDF가 아닙니다. 단일 페이지 문서로 처리합니다")
            full_docs = None
            total_pages = 1
            is_pdf = False
        except Exception as e:
            raise ValueError(f"PDF 파일 읽기 실패: {e}") from e

        # max_page 제한 적용 (설정된 경우)
        if (self.max_page or 0) > 0 and is_pdf:
            total_pages = min(total_pages, self.start_page - 1 + self.max_page)
            logger.debug("max_page=%d 설정 : %d 페이지까지만 변환", self.max_page, total_pages)

        # batch_page_size가 최대 허용 페이지 수를 초과하지 않는지 검증
        if batch_page_size > MAX_BATCH_PAGE_SIZE:
            raise ValueError(
                f"batch_page_size ({batch_page_size})가 최대 허용 페이지 수 ({MAX_BATCH_PAGE_SIZE})를 초과합니다"
            )

        if is_pdf:
            # pages 인자가 있는 경우 해당 페이지들만 처리
            if self.pages:
                # 유효한 페이지 번호만 필터링 (1-based 페이지 번호를 0-based 인덱스로 변환)
                valid_pages = [p - 1 for p in self.pages if 0 <= p - 1 < total_pages]
                logger.info("변환할 페이지 : %s", ", ".join(map(str, self.pages)))

                for page_index in valid_pages:
                    logger.info("%d 페이지 변환", page_index + 1)

                    merger = PdfWriter()
                    merger.append(full_docs, pages=(page_index, page_index + 1))
                    with io.BytesIO() as buffer:
                        merger.write(buffer)
                        buffer.seek(0)
                        response_obj = await self._call_document_parse_api({"document": buffer})
                        async for element in self._response_to_elements(response_obj, total_pages, page_index):
                            if element.category in self.ignore_element_category_list:
                                content_s = getattr(element.content, self.document_format)
                                content_preview = content_s[:100] + ("..." if len(content_s) > 100 else "")
                                logger.debug(
                                    "Ignore element category : %s, content: %s", element.category, repr(content_preview)
                                )
                            else:
                                yield element

            else:  # pages 인자가 없는 경우 기존 로직 수행
                start_page_index = max(0, self.start_page - 1)
                while start_page_index < total_pages:
                    # 실제로 처리할 페이지 수 계산 (남은 페이지와 batch_page_size 중 작은 값)
                    pages_to_process = min(batch_page_size, total_pages - start_page_index)
                    end_page_index = start_page_index + pages_to_process - 1

                    if start_page_index == end_page_index:
                        logger.debug("%d / %d 페이지", start_page_index + 1, total_pages)
                    else:
                        logger.debug(
                            "%d~%d / %d 페이지",
                            start_page_index + 1,
                            end_page_index + 1,
                            total_pages,
                        )

                    merger = PdfWriter()
                    merger.append(
                        full_docs,
                        pages=(start_page_index, min(start_page_index + pages_to_process, len(full_docs.pages))),
                    )
                    with io.BytesIO() as buffer:
                        merger.write(buffer)
                        buffer.seek(0)
                        response_obj = await self._call_document_parse_api({"document": buffer})
                        async for element in self._response_to_elements(response_obj, total_pages, start_page_index):
                            if element.category in self.ignore_element_category_list:
                                content_s = getattr(element.content, self.document_format)
                                content_preview = content_s[:100] + ("..." if len(content_s) > 100 else "")
                                logger.debug(
                                    "Ignore element category : %s, content: %s", element.category, repr(content_preview)
                                )
                            else:
                                element.page += start_page_index
                                yield element

                    start_page_index += pages_to_process

        else:
            response_obj = await self._call_document_parse_api({"document": file})
            async for element in self._response_to_elements(response_obj, total_pages, 0):
                if element.category in self.ignore_element_category_list:
                    content_s = getattr(element.content, self.document_format)
                    content_preview = content_s[:100] + ("..." if len(content_s) > 100 else "")
                    logger.debug("Ignore element category : %s, content: %s", element.category, content_preview)
                else:
                    yield element

    async def _call_document_parse_api(
        self,
        files: dict,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> dict:
        """
        제공된 파일로 API 엔드포인트에 POST 요청을 비동기적으로 보내고 응답을 반환합니다.

        Args:
            files (dict): 요청에 보낼 파일을 포함하는 사전.
            timeout (int, optional): 요청 타임아웃(초). 기본값은 DEFAULT_TIMEOUT입니다.

        Returns:
            dict: API 응답 데이터를 포함하는 사전

        Raises:
            ValueError: API 호출에 오류가 있는 경우 발생합니다.
        """
        headers = {
            "Authorization": f"Bearer {self.upstage_api_key}",
        }
        data = {
            "ocr": self.ocr_mode,
            "model": self.model,
            "output_formats": "['html', 'text', 'markdown']",
            "coordinates": self.coordinates,
            "base64_encoding": "[" + ",".join(f"'{el}'" for el in self.base64_encoding_category_list) + "]",
        }

        try:
            response_data: bytes = await cached_http_async(
                self.api_url,
                method="POST",
                headers=headers,
                data=data,
                files=files,
                timeout=timeout,
                ignore_cache=not self.enable_cache,
                cache_alias="upstage",
            )
            return json.loads(response_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed json decode : {e}") from e
        except Exception as e:
            raise ValueError(str(e)) from e

    async def _response_to_elements(
        self,
        response_obj: dict,
        total_pages: int,
        start_page_index: int = 0,
    ) -> AsyncGenerator[Element, None]:
        """
        API 응답 객체를 파싱하여 Element 객체들을 생성하는 비동기 제너레이터입니다.

        Args:
            response_obj (dict): API 응답 데이터를 포함하는 사전
            total_pages (int): 문서의 총 페이지 수

        Returns:
            AsyncGenerator[Element, None]: Element 객체들의 비동기 제너레이터
        """
        api: str = response_obj.get("api")
        model: str = response_obj.get("model")
        # usage: dict = response_obj.get("usage")  # ex: { "pages": 10 }
        bare_element_list = response_obj.get("elements") or []

        logger.info("Upstage %s (%s) API 요청에서 %d개의 요소를 찾았습니다.", model, api, len(bare_element_list))

        if self.image_descriptor is not None:
            image_descriptor_llm = self.image_descriptor.get_llm()
            prompt_context = (self.image_descriptor.prompt_context or {}).copy()
        else:
            image_descriptor_llm = None
            prompt_context = {}

        element_list: list[Element] = []
        request_list: list[DescribeImageRequest] = []
        for bare_element in bare_element_list:
            element = Element(
                id=bare_element["id"],
                page=bare_element["page"] + start_page_index,
                total_pages=total_pages,
                category=bare_element["category"],
                content=ElementContent(
                    markdown=bare_element["content"]["markdown"],
                    text=bare_element["content"]["text"],
                    html=bare_element["content"]["html"],
                ),
                b64_str=bare_element.get("base64_encoding", ""),
                coordinates=bare_element.get("coordinates") or [],
                api=api,
                model=model,
            )

            element_list.append(element)

            if image_descriptor_llm is not None and len(element.files) > 0:
                system_prompt = self.image_descriptor.get_system_prompt(element.category)
                user_prompt = self.image_descriptor.get_user_prompt(element.category)

                for file_path, file in element.files.items():
                    logger.debug("file path : %s", file_path)
                    context = prompt_context.copy()
                    context["context"] = None  # 맥락이 있다면 추가

                    request_list.append(
                        DescribeImageRequest(
                            image=file,
                            image_path=file_path,
                            system_prompt=system_prompt,
                            user_prompt=user_prompt,
                            temperature=self.image_descriptor.temperature,
                            max_tokens=self.image_descriptor.max_tokens,
                            prompt_context=context,
                        )
                    )

        if image_descriptor_llm is not None and len(request_list) > 0:
            logger.info(
                "%d개의 요소에서 %d개의 이미지를 찾았습니다.",
                len(element_list),
                len(request_list),
            )
            logger.info(
                "%s 모델을 통해 이미지 설명을 생성합니다.",
                self.image_descriptor.llm_model,
            )

            llm_reply_list: list[Reply] = await image_descriptor_llm.describe_images_async(
                request_list, enable_cache=self.image_descriptor.enable_cache
            )
            if not isinstance(llm_reply_list, list):
                llm_reply_list = [llm_reply_list]  # noqa

            assert len(request_list) == len(llm_reply_list)

            # 이미지 설명을 각 element에 매핑
            current_idx = 0
            for element in element_list:
                if element.files:
                    num_files = len(element.files)

                    for file_path, reply in zip(
                        element.files.keys(),
                        llm_reply_list[current_idx : current_idx + num_files],
                    ):
                        element.image_descriptions += f"<image name='{file_path}'>" + reply.text + "</image>" + "\n"
                        if reply.usage:
                            logger.debug("Image description token : %s", reply.usage)

                    element.image_descriptions = element.image_descriptions.strip()

                    current_idx += num_files

        for element in element_list:
            yield element
