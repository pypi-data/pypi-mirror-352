import logging
import os
import re
from pathlib import Path
from shutil import rmtree
from typing import Optional, Union, cast

import typer
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.validators import URLValidator
from rich.console import Console
from rich.table import Table

from pyhub import init
from pyhub.caches import cache_clear_all
from pyhub.config import DEFAULT_TOML_PATH, DEFAULT_ENV_PATH
from pyhub.llm.json import json_dumps
from pyhub.llm.types import (
    LanguageEnum,
    LLMChatModelEnum,
    LLMChatModelType,
    LLMVendorEnum,
    LLMVendorType,
)
from pyhub.parser.upstage import UpstageDocumentParseParser
from pyhub.parser.upstage.parser import ImageDescriptor
from pyhub.parser.upstage.settings import (
    DEFAULT_BATCH_PAGE_SIZE,
    MAX_BATCH_PAGE_SIZE,
    SUPPORTED_FILE_EXTENSIONS,
)
from pyhub.parser.upstage.types import (
    CategoryEnum,
    DocumentFormatEnum,
    DocumentFormatType,
    DocumentSplitStrategyEnum,
    DocumentSplitStrategyType,
    Element,
    ElementCategoryType,
    OCRModeEnum,
    OCRModeType,
)
from pyhub.rag.utils import get_literal_values

console = Console()


def upstage(
    ctx: typer.Context,
    input_path: Optional[Path] = typer.Argument(
        None,
        help=f"입력 파일 경로 (지원 포맷: {', '.join(SUPPORTED_FILE_EXTENSIONS)})",
    ),
    output_dir_path: Optional[Path] = typer.Option(
        "output",
        "--output-dir-path",
        "-o",
        writable=True,
        help="Document jsonl 파일을 생성할 폴더 경로",
    ),
    document_format: DocumentFormatEnum = typer.Option(
        DocumentFormatEnum.MARKDOWN,
        "--document-format",
        "-d",
        help="생성할 문서 포맷",
    ),
    # is_create_unified_output: bool = typer.Option(
    #     False,
    #     "--create-unified-file",
    #     "-c",
    #     help="통합 파일 생성 여부",
    # ),
    document_split_strategy: DocumentSplitStrategyEnum = typer.Option(
        DocumentSplitStrategyEnum.PAGE,
        "--document-split-strategy",
        "-s",
        help=(
            "문서 분할 전략 | (1) page: 페이지 단위로 Document 생성, (2) element: Element 단위로 Document 생성, "
            "(3) none: 파일 전체를 하나의 Document로 생성"
        ),
    ),
    batch_page_size: int = typer.Option(
        DEFAULT_BATCH_PAGE_SIZE,
        "--batch-page-size",
        "-b",
        min=1,
        max=MAX_BATCH_PAGE_SIZE,
        help=(
            f"한 번의 API 호출에서 처리할 PDF 페이지 수입니다. Upstage Document Parse API는 "
            f"하나의 API 호출당 최대 {MAX_BATCH_PAGE_SIZE} 페이지까지 지원합니다. "
            f"{MAX_BATCH_PAGE_SIZE}페이지를 초과하는 PDF 파일에는 이 설정이 꼭 필요합니다."
        ),
    ),
    pages: Optional[str] = typer.Option(
        None,
        "--pages",
        help="처리할 특정 페이지 번호들 (쉼표나 공백으로 구분). 예: '1,2,3' 또는 '1 2 3' (PDF 변환에서만 적용)",
        callback=lambda x: validate_pages(x),
    ),
    start_page: int = typer.Option(
        1,
        min=1,
        help="시작 페이지 번호 (PDF 변환에서만 적용)",
    ),
    max_page: Optional[int] = typer.Option(
        None,
        min=1,
        help="처리할 최대 페이지 수",
    ),
    ocr_mode: OCRModeEnum = typer.Option(OCRModeEnum.FORCE, help="OCR 모드"),
    extract_element_types: str = typer.Option(
        "figure,chart,table",
        "--extract-element-types",
        "-t",
        help=f"이미지로서 추출할 Element (쉼표로 구분) : {', '.join([e.value for e in CategoryEnum])}",
        callback=lambda x: validate_categories(x),
    ),
    ignore_element_category: str = typer.Option(
        "footer",
        "--ignore",
        help=f"파싱 결과에서 제외할 Element 카테고리 목록 (쉼표로 구분) (디폴트: footer) : {', '.join(get_literal_values(ElementCategoryType))}",
        callback=lambda x: validate_categories(x),
    ),
    is_enable_image_descriptor: bool = typer.Option(
        False,
        "--enable-image-descriptor",
        "-i",
        help=(
            "이미지 Element에 대한 자동 설명 생성 여부. 활성화하면 --extract-element-types 옵션으로 지정한 Element들에 대한 텍스트 설명을 "
            "LLM을 통해 자동으로 생성하고, Document metadata의 image_descriptions 필드에 저장합니다."
        ),
    ),
    image_descriptor_llm_model: LLMChatModelEnum = typer.Option(
        LLMChatModelEnum.GPT_4O_MINI,
        "--image-descriptor-llm-model",
        "-m",
        help="이미지 설명 생성에 사용할 LLM 모델. gpt-4o-mini 처럼 멀티모달을 지원하는 모델을 지정하셔야 합니다.",
    ),
    image_descriptor_api_key: Optional[str] = typer.Option(
        None,
        "--image-descriptor-api-key",
        "-k",
        help=(
            "이미지 설명 생성에 사용할 LLM API 키. LLM 벤더에 맞게 지정해야 합니다. 미지정 시 각 벤더별 기본 "
            "환경변수(OPENAI_API_KEY, ANTHROPIC_API_KEY, UPSTAGE_API_KEY, GEMINI_API_KEY 등)에서 로딩됩니다."
        ),
    ),
    image_descriptor_base_url: Optional[str] = typer.Option(
        None,
        "--image-descriptor-base-url",
        "-r",
        help=(
            "이미지 설명 생성에 사용할 LLM API의 기본 URL. 기본 API 엔드포인트가 아닌 다른 엔드포인트를 사용하려는 경우 지정합니다. "
            "예: OpenAI 호환 API 서버, Ollama"
        ),
        callback=lambda x: validate_url(x),
    ),
    image_descriptor_temperature: Optional[float] = typer.Option(
        None,
        "--image-descriptor-temperature",
        "-p",
        help="이미지 설명 생성에 사용할 온도 값 (높을수록 다양한 응답)",
    ),
    image_descriptor_max_tokens: Optional[int] = typer.Option(
        None,
        "--image-descriptor-max-tokens",
        "-n",
        help="이미지 설명 생성의 최대 토큰 수",
    ),
    image_descriptor_language: str = typer.Option(
        LanguageEnum.KOREAN.value,
        "--image-descriptor-language",
        "-l",
        help="이미지 설명 생성에 사용할 언어",
        callback=lambda x: validate_language(x),
    ),
    is_verbose: bool = typer.Option(False, "--verbose"),
    is_force: bool = typer.Option(False, "--force", "-f", help="확인 없이 출력 폴더 삭제 후 재생성"),
    is_enable_cache: bool = typer.Option(
        False, "--enable-cache", help="API 응답 캐시를 활성화합니다. 활성화하면 이전 API 응답을 재사용하여 빠른 처리와 비용 절약이 가능합니다."
    ),
    is_cache_clear_all: bool = typer.Option(
        False,
        "--cache-clear-all",
        help="모든 캐시를 초기화합니다.",
    ),
    upstage_api_key: Optional[str] = typer.Option(
        None, help="Upstage API Key. 지정하지 않으면 UPSTAGE_API_KEY 환경 변수 사용"
    ),
    toml_path: Optional[Path] = typer.Option(
        DEFAULT_TOML_PATH,
        "--toml-file",
        help="toml 설정 파일 경로",
    ),
    env_path: Optional[Path] = typer.Option(
        DEFAULT_ENV_PATH,
        "--env-file",
        help="환경 변수 파일(.env) 경로",
    ),
    is_debug: bool = typer.Option(False, "--debug"),
):
    # input_path가 없으면 help를 출력하고 종료 (Django 초기화 전에 처리)
    if input_path is None:
        console.print(ctx.get_help())
        raise typer.Exit()

    log_level = logging.DEBUG if is_verbose else logging.INFO
    init(debug=True, log_level=log_level, toml_path=toml_path, env_path=env_path)

    if upstage_api_key is None:
        upstage_api_key = os.environ.get("UPSTAGE_API_KEY")

    if not upstage_api_key:
        raise typer.BadParameter(
            "--upstage-api-key 옵션이나 UPSTAGE_API_KEY 환경 변수를 통해 Upstage API Key를 설정해주세요."
        )
    else:
        # Validate Upstage API key format
        if not upstage_api_key.startswith("up_"):
            console.print(
                "[bold red]오류: Upstage API Key 형식이 올바르지 않습니다. Upstage API Key는 'up_'로 시작합니다.[/bold red]"
            )
            raise typer.Exit(code=1)

    is_pdf = input_path.suffix.lower() == ".pdf"

    extract_element_category_list = cast(list[ElementCategoryType], extract_element_types)
    ignore_element_category_list = cast(list[ElementCategoryType], ignore_element_category)

    # Check if output file exists and confirm overwrite if force option is not set
    if output_dir_path.exists():
        if is_force:
            if is_verbose:
                console.print(f"[yellow]출력 폴더 삭제 : {output_dir_path}[/yellow]")
            rmtree(output_dir_path, ignore_errors=True)
        else:
            overwrite = typer.confirm(
                f"출력 폴더 {output_dir_path}이(가) 이미 존재합니다. 삭제 후에 재생성하시겠습니까?"
            )
            if overwrite:
                if is_verbose:
                    console.print(f"[yellow]출력 폴더 {output_dir_path}을(를) 삭제합니다.[/yellow]")
                rmtree(output_dir_path, ignore_errors=True)
            else:
                console.print("[yellow]작업이 취소되었습니다.[/yellow]")
                raise typer.Exit(code=0)

    output_dir_path.mkdir(parents=True, exist_ok=True)

    # create one based on input_path with .jsonl extension
    jsonl_output_path = output_dir_path / input_path.with_suffix(".jsonl").name

    unified_document_paths = []
    for format_enum in (DocumentFormatEnum.MARKDOWN, DocumentFormatEnum.HTML, DocumentFormatEnum.TEXT):
        ext = DocumentFormatEnum.to_ext(format_enum)
        unified_output_path = output_dir_path / input_path.with_suffix(ext).name
        unified_output_path.unlink(missing_ok=True)
        unified_document_paths.append((format_enum, unified_output_path))

    # Debug: Print all arguments except api_key
    if is_verbose:
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("설정", style="cyan")
        table.add_column("값", style="green")

        # Add rows to the table
        table.add_row("입력 문서 파일 경로", str(input_path.absolute()))
        table.add_row("파일 생성 폴더", str(output_dir_path.absolute()))
        table.add_row("이미지로서 추출할 Element", ", ".join(extract_element_category_list))
        table.add_row("제외할 Element", ", ".join(ignore_element_category_list))
        table.add_row("OCR 모드", ocr_mode.value)
        table.add_row("Elements to Document 분할 전략", document_split_strategy.value)
        table.add_row("생성할 Document 포맷", document_format.value)
        # table.add_row("통합 문서 생성 여부", "예" if is_create_unified_output else "아니오")

        # Add batch size with warning if needed
        batch_size_str = str(batch_page_size)
        if not is_pdf and batch_page_size == DEFAULT_BATCH_PAGE_SIZE:
            batch_size_str += " [yellow](경고: PDF 파일에서만 사용됩니다.)[/yellow]"
        table.add_row("배치 크기", batch_size_str)

        end_page_label = "끝" if max_page is None else f"{start_page - 1 + max_page}"
        table.add_row("페이지 범위", f"{start_page} ~ {end_page_label}")

        # Add image descriptor information if enabled
        if is_enable_image_descriptor:
            table.add_row("이미지 설명 활성화", "예")
            if image_descriptor_base_url:
                table.add_row("이미지 설명 LLM 기본 URL", image_descriptor_base_url)
            table.add_row("이미지 설명 언어", image_descriptor_language)
            if image_descriptor_temperature is not None:
                table.add_row("이미지 설명 온도", str(image_descriptor_temperature))
            if image_descriptor_max_tokens is not None:
                table.add_row("이미지 설명 최대 토큰", str(image_descriptor_max_tokens))
        else:
            table.add_row("이미지 설명 활성화", "아니오")

        # table.add_row("터미널에 상세 정보 출력하기", "예" if is_verbose else "아니오")
        # table.add_row("생성 폴더 강제 재생성", "예" if is_force else "아니오")
        table.add_row("toml 파일 경로", str(toml_path))
        table.add_row("환경변수 파일 경로", str(env_path))
        # Print the table
        console.print(table)

    # Check if input file is a PDF. Warn if batch_size is specified but file is not a PDF
    if not is_pdf and batch_page_size != DEFAULT_BATCH_PAGE_SIZE and not is_verbose:
        console.print(f"[yellow]경고: 배치 크기 매개변수({batch_page_size})는 PDF가 아닌 파일에는 무시됩니다.[/yellow]")

    if is_enable_image_descriptor:
        image_descriptor = ImageDescriptor(
            llm_model=cast(LLMChatModelType, image_descriptor_llm_model.value),
            llm_api_key=image_descriptor_api_key,
            llm_base_url=image_descriptor_base_url,
            prompt_context={"language": image_descriptor_language},
            temperature=image_descriptor_temperature,
            max_tokens=image_descriptor_max_tokens,
            enable_cache=is_enable_cache,
        )
    else:
        image_descriptor = None

    parser = UpstageDocumentParseParser(
        upstage_api_key=upstage_api_key,
        split=cast(DocumentSplitStrategyType, document_split_strategy.value),
        pages=pages,
        start_page=start_page,
        max_page=max_page,
        image_descriptor=image_descriptor,
        ocr_mode=cast(OCRModeType, ocr_mode.value),
        document_format=cast(DocumentFormatType, document_format.value),
        base64_encoding_category_list=extract_element_category_list,
        ignore_element_category_list=ignore_element_category_list,
        enable_cache=is_enable_cache,
        verbose=is_verbose,
    )

    try:
        if is_cache_clear_all:
            cache_clear_all()

        with input_path.open("rb") as file:
            django_file = File(file)
            parser.is_valid(django_file, raise_exception=True)

            with jsonl_output_path.open("wt", encoding="utf-8") as f:
                document_count = 0
                for document in parser.lazy_parse(
                    django_file,
                    batch_page_size=batch_page_size,
                    ignore_validation=True,
                ):
                    document.metadata.setdefault("source", input_path.name)
                    f.write(json_dumps(document) + "\n")

                    if len(unified_document_paths) > 0:
                        for format_enum, output_path in unified_document_paths:
                            variant_page_content = document.variants.get(format_enum.value)

                            with output_path.open("at", encoding="utf-8") as uf:
                                if document_count > 0:
                                    uf.write("\n\n")
                                uf.write(variant_page_content)

                    el: Element
                    for el in document.elements:
                        if el.files:
                            html: str = el.image_descriptions

                            matches = re.findall(r"(<image\s+name=[\'\"](.*?)[\'\"]>.*?</image>)", html, re.DOTALL)
                            image_dict = {name: full_tag.strip() for full_tag, name in matches}

                            for name, _file in el.files.items():
                                output_path = output_dir_path / name
                                output_path.parent.mkdir(parents=True, exist_ok=True)
                                if output_path.exists():
                                    console.print(f"[red]경고: {output_path} 경로 파일을 덮어쓰기 합니다.[/red]")
                                output_path.open("wb").write(_file.read())

                                if name in image_dict:
                                    desc = image_dict[name]
                                    output_path.with_suffix(".txt").write_text(desc)

                    # for name, _file in document.files.items():
                    #     print("name :", repr(name))
                    #     output_path = output_dir_path / name
                    #     output_path.parent.mkdir(parents=True, exist_ok=True)
                    #     output_path.open("wb").write(_file.read())

                    document_count += 1

                if document_count > 0:
                    console.print(
                        f"[green]성공:[/green] {jsonl_output_path} 경로에 {document_count}개의 Document를 jsonl 포맷으로 생성했습니다."
                    )

                    if unified_document_paths:
                        for _, output_path in unified_document_paths:
                            console.print(f"[green]성공:[/green] {output_path} 경로에 통합 문서를 생성했습니다.")
                else:
                    console.print("[red]경고: 생성된 Document가 없습니다.[/red]")

    except Exception as e:
        console.print(f"[red]{e}[/red]")

        if is_debug:
            console.print_exception()

        raise typer.Exit(code=1)


def validate_categories(categories_str: str) -> list[str]:
    """Raises BadParameter exception if values not in CategoryEnum are entered."""
    if not categories_str:
        return []

    invalid_categories = []
    valid_categories = []

    for item in categories_str.split(","):
        category = item.strip()
        if category in CategoryEnum:
            valid_categories.append(category)
        else:
            invalid_categories.append(category)

    if invalid_categories:
        valid_values = [e.value for e in CategoryEnum]
        raise typer.BadParameter(
            f"유효하지 않은 값: {', '.join(invalid_categories)}. 유효한 값: {', '.join(valid_values)}"
        )

    return valid_categories


def validate_language(value: str) -> Union[LanguageEnum, str]:
    """Validates language input and returns either LanguageEnum or custom string value."""
    try:
        return LanguageEnum(value.upper())
    except ValueError:
        return value


def validate_output_formats(formats_str: str) -> list[DocumentFormatEnum]:
    """Validates and converts comma-separated format strings to DocumentFormatEnum list."""
    if not formats_str:
        return []

    valid_values: str = ", ".join(e.value for e in DocumentFormatEnum)

    # 인자값이 "-"로 시작하면 인자가 주어지지 않은 것으로 처리
    if formats_str.startswith("-"):
        raise typer.BadParameter(f"--unified-output-format (-u) 옵션 값이 누락되었습니다. 유효한 포맷 : {valid_values}")

    formats = []
    invalid_formats = []

    for fmt in formats_str.split(","):
        fmt = fmt.strip().lower()
        try:
            formats.append(DocumentFormatEnum(fmt))
        except ValueError:
            invalid_formats.append(fmt)

    if invalid_formats:
        raise typer.BadParameter(f"유효하지 않은 포맷: {', '.join(invalid_formats)}. 유효한 포맷: {valid_values}")

    return formats


def validate_url(url: Optional[str]) -> Optional[str]:
    """URL 형식의 유효성을 검사합니다."""
    if url is None:
        return None

    validator = URLValidator(schemes=("http", "https"))

    try:
        validator(url)
    except ValidationError:
        raise typer.BadParameter(f"Invalid URL Pattern : {url}")


def validate_pages(pages_str: Optional[str]) -> Optional[list[int]]:
    """페이지 번호 문자열을 파싱하여 유효한 페이지 번호 리스트를 반환합니다."""
    if not pages_str:
        return None

    # 숫자만 추출 (쉼표나 공백으로 구분된 숫자들)
    numbers = re.findall(r"\d+", pages_str)

    if not numbers:
        raise typer.BadParameter("유효한 페이지 번호가 없습니다. 예시: '1,2,3' 또는 '1 2 3'")

    # 문자열을 정수로 변환하고 중복 제거
    pages = sorted(set(int(num) for num in numbers))

    # 페이지 번호가 1 이상인지 확인
    if any(page < 1 for page in pages):
        raise typer.BadParameter("페이지 번호는 1 이상이어야 합니다.")

    return pages
