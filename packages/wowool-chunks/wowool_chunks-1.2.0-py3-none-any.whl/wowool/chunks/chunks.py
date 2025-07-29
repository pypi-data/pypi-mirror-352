from wowool.diagnostic import Diagnostics, DiagnosticType, Diagnostic
from wowool.document.analysis.document import AnalysisDocument
from wowool.annotation.paragraph import Paragraph as WowoolParagraph
from wowool.annotation.sentence import Sentence
from wowool.string import canonicalize as canonicalize_sentence
import logging
from wowool.utility.apps.decorators import (
    exceptions_to_diagnostics,
    requires_analysis,
)
from wowool.chunks.app_id import APP_ID
from dataclasses import dataclass, field
from enum import Enum
from typing import overload
from re import compile as re_compile

logger = logging.getLogger(__name__)


class HeaderType(Enum):
    Absolute: int = 0
    Relative: int = 1


@dataclass
class Limits:
    max_chunk_size: int = 100
    soft_sentence_limit: int = 4
    header_level: int = -1


@dataclass
class Header:
    level: int = 0
    type: HeaderType = HeaderType.Absolute
    resolved: int = -1

    def __post_init__(self):
        if self.resolved == -1:
            self.resolved = self.level


def get_header_level(token):
    if token.literal[0] == "#":
        return Header(len(token.literal), HeaderType.Absolute)
    if token.literal.endswith("."):
        return Header(token.literal.count("."), HeaderType.Relative)


def get_header_info(sent):
    tokens = sent.tokens
    if len(tokens) > 0 and "hdr-prefix" in tokens[0].properties:
        return get_header_level(tokens[0])
    return None


class ChunkFlags(dict[str, bool]):

    @property
    def add_outline(self):
        return self["add_outline"] if "add_outline" in self else False

    @property
    def add_topics(self):
        return self["add_topics"] if "add_topics" in self else False

    @property
    def add_themes(self):
        return self["add_themes"] if "add_themes" in self else False

    @property
    def stems(self):
        return self["stems"] if "stems" in self else False

    @property
    def fix_spelling_mistakes(self):
        return self["fix_spelling_mistakes"] if "fix_spelling_mistakes" in self else False

    @property
    def canonicalize(self):
        return self["canonicalize"] if "canonicalize" in self else True

    @property
    def dates(self):
        return self["dates"] if "dates" in self else False

    @property
    def cleanup(self):
        return self["cleanup"] if "cleanup" in self else True

    @property
    def lowercase(self):
        return self["lowercase"] if "lowercase" in self else False


DEFAULT_MARKUP_CLEANUP_PATTERN = r"(:?^#+ |[*]{1,3}|[-]{2,3}|[-] | [-]|_{1,2}|^\s*[-+*>] |``)"
DEFAULT_MARKUP_CLEANUP = re_compile(DEFAULT_MARKUP_CLEANUP_PATTERN)


DEFAULT_MARKUP_CLEANUP_GROUPS_PATTERN = r"!?\[([^\]]+)\]\(([^)]+)\)"
DEFAULT_MARKUP_CLEANUP_GROUPS = re_compile(DEFAULT_MARKUP_CLEANUP_GROUPS_PATTERN)


def get_sentence_text(sent: Sentence, flags: ChunkFlags):
    text = canonicalize_sentence(sent, stem=flags.stems, dates=flags.dates, spelling=flags.fix_spelling_mistakes)

    if flags.cleanup:
        text = text.strip()
        text = DEFAULT_MARKUP_CLEANUP.sub("", text)
        text = DEFAULT_MARKUP_CLEANUP_GROUPS.sub(r"\1", text)

    if flags.lowercase:
        text = text.lower()
    return text


class ChunkSentence:
    def __init__(self, sentence: Sentence, paragraph_idx: int, flags: ChunkFlags, is_header: bool = False):
        self.sentence = sentence
        self.text = get_sentence_text(sentence, flags)
        self.nrof_tokens = len(sentence.tokens)
        self.paragraph_idx = paragraph_idx
        self.is_header = is_header

    def __repr__(self):
        return f"ChunkSent: {self.text} header={self.is_header}"

    def __str__(self):
        return f"ChunkSentence: {self.nrof_tokens} {self.text} header={self.is_header}"

    def to_json(self):
        return {"text": self.text, "nrof_tokens": self.nrof_tokens}


@dataclass
class Paragraph:
    sentences: list[ChunkSentence] = field(default_factory=list[ChunkSentence])
    paragraph_idx: int = 0
    parent: "Section" = None

    def add_sentence(self, sent: Sentence, flags: ChunkFlags):
        self.sentences.append(ChunkSentence(sent, self.paragraph_idx, flags))

    def has_sentences(self):
        return len(self.sentences) > 0

    def to_json(self):
        retval = {
            "type": "Paragraph",
        }

        if self.sentences:
            retval["sentences"] = [s.to_json() for s in self.sentences]

        return retval


@dataclass
class Section:
    header_data: Header | None = None
    sentence: ChunkSentence | None = None
    chunks: list["Section"] = field(default_factory=list["Section"])
    parent: "Section|None" = None
    paragraph_idx: int = 0

    @property
    def level(self):
        return self.header_data.level if self.header_data else 0

    @property
    def absolute_level(self):
        return self.header_data.resolved if self.header_data else 0

    @overload
    def push_section(self, header_level: int, paragraph_idx: int) -> "Section": ...

    @overload
    def push_section(self, header_info: Header, paragraph_idx: int) -> "Section": ...

    def push_section(self, header_info_or_level, paragraph_idx: int) -> "Section":
        if isinstance(header_info_or_level, int):
            header_info = Header(header_info_or_level, HeaderType.Absolute, resolved=header_info_or_level)
        elif isinstance(header_info_or_level, Header):
            header_info = header_info_or_level
        else:
            raise TypeError("Invalid type for header_info_or_level")

        new_chunk = Section(parent=self, header_data=header_info, paragraph_idx=paragraph_idx)
        self.chunks.append(new_chunk)
        return new_chunk

    def add_item(self, item):
        item.parent = self
        self.chunks.append(item)
        return item

    def set_header(self, sent: Sentence, flags: ChunkFlags):
        self.sentence = ChunkSentence(sent, self.paragraph_idx, flags, is_header=True)

    def to_json(self):
        retval = {
            "type": "Section",
        }

        if self.header_data:
            retval["header"] = {
                "level": self.header_data.level,
                "type": f"{self.header_data.type}",
                "resolved": self.header_data.resolved,
            }
        if self.sentence:
            retval["sentence"] = self.sentence.to_json()
        if self.chunks:
            retval["chunks"] = [c.to_json() for c in self.chunks]
        return retval


def is_section(item):
    return isinstance(item, Section)


def is_paragraph(item):
    return isinstance(item, Paragraph)


def find_absolute_header(chunk: Section) -> Section:
    chunk_ = chunk
    while chunk_ and chunk_.header_data and (chunk_.header_data.type == HeaderType.Relative or chunk_.header_data is None):
        chunk_ = chunk_.parent
    return chunk_


def find_absolute_header_level(chunk: Section) -> int:
    chunk = find_absolute_header(chunk)
    if chunk:
        return chunk.header_data.level
    return 0


@dataclass
class ChunkContext:
    current_size: int = 0


def print_chunk(chunk, level=0):

    print("  " * (level), "+", chunk)
    # titles = chunk.get_outline_titles()
    # if titles:
    #     for t in titles:
    #         print(" " * (level + 1), t)

    if chunk.header_data:
        print("  " * (level + 1), "header:", "TBI chunk.header_data.text")

    for s in chunk.sentences:
        print("  " * level, end="  - ")
        print(s.text)
    for c in chunk.chunks:
        print_chunk(c, level + 1)


def foreach_sentence(chunks: list[Section], cidx: int, cc: ChunkContext, callback, level=0):
    chunk = chunks[cidx]

    if is_section(chunk):
        if chunk.sentence:
            callback(cc, chunks, cidx, [chunk.sentence], 0)
        for sub_cidx, c in enumerate(chunk.chunks):
            foreach_sentence(chunk.chunks, sub_cidx, cc, callback, level + 1)
    elif is_paragraph(chunk):
        for sidx, sent in enumerate(chunk.sentences):
            callback(cc, chunks, cidx, chunk.sentences, sidx)


def find_chunk_in_parent(current: Section):
    if current.parent:
        for idx, ch in enumerate(current.parent.chunks):
            if id(ch) == id(current):
                return idx
    return None


@dataclass
class FlatSentence:
    sentence: ChunkSentence
    chunk: Section

    def __repr__(self):
        return f"FlatSentence: c={self.sentence.nrof_tokens:02} p={self.sentence.paragraph_idx:02} {self.sentence.text}"

    def __str__(self):
        return f"FlatSentence: c={self.sentence.nrof_tokens:02} p={self.sentence.paragraph_idx:02} {self.sentence.text}"

    def get_outline_titles(self):
        titles = []
        current = self.chunk

        include_lowest_level = True
        while current:
            if is_section(current) and current.header_data and current.sentence:
                if include_lowest_level:
                    idx_in_parent = find_chunk_in_parent(current)
                    add_title = True
                    if idx_in_parent is not None:
                        for ch in current.parent.chunks[idx_in_parent + 1 :]:
                            if is_section(ch) and ch.header_data and ch.header_data.resolved == current.header_data.resolved:
                                add_title = False
                                break
                    if add_title and current.sentence.is_header:
                        titles.append(current.sentence)
                    include_lowest_level = False
                elif current.sentence:
                    titles.append(current.sentence)
                # titles.append(current.sentences[0].text)
            current = current.parent
        return titles


@dataclass
class Chunk:
    sentences: list[ChunkSentence]
    outline: list[str] | None = None


# @dataclass
# class FlatResult:
#     sentences: list[FlatSentence]

#     def to_json(self):
#         return {
#             "sentences": [fs.sentence.to_json() for fs in self.sentences],
#         }

INVALID_BOUNDARY = -1


def find_block_limit(lines: list[FlatSentence], lidx: int, limits_boundaries, limits: Limits) -> int:

    if is_section(lines[lidx].chunk):
        return lidx
    up_idx = lidx - 1
    up_token_distance = 0
    paragraph_idx = lines[lidx].sentence.paragraph_idx
    nrof_sentences = 0
    while up_idx >= 0:
        if is_section(lines[up_idx].chunk):
            up_token_distance += lines[up_idx].sentence.nrof_tokens
            break
        elif lines[up_idx].sentence.paragraph_idx != paragraph_idx:
            up_idx += 1
            break
        if nrof_sentences >= limits.soft_sentence_limit:
            up_idx = INVALID_BOUNDARY
            break
        up_token_distance += lines[up_idx].sentence.nrof_tokens
        up_idx -= 1
        nrof_sentences += 1

    down_idx = lidx
    down_token_distance = 0
    nrof_sentences = 0
    while down_idx < len(lines):
        if is_section(lines[down_idx].chunk):
            break
        elif lines[down_idx].sentence.paragraph_idx != paragraph_idx:
            break
        elif nrof_sentences >= limits.soft_sentence_limit:
            down_idx = INVALID_BOUNDARY
            break
        down_token_distance += lines[down_idx].sentence.nrof_tokens
        down_idx += 1
        nrof_sentences += 1

    if up_idx == INVALID_BOUNDARY:
        if down_idx == INVALID_BOUNDARY:
            return lidx
        else:
            return down_idx
    elif down_idx == INVALID_BOUNDARY:
        return up_idx

    # print("up_token_distance:", up_token_distance, "down_token_distance:", down_token_distance)
    if up_token_distance > down_token_distance:
        # print("going down:", down_idx)
        if down_idx not in limits_boundaries:
            return down_idx
        else:
            return up_idx
    # print("going up:", up_idx)
    if up_idx not in limits_boundaries:
        return up_idx
    else:
        return down_idx


def create_chunks_base_on_limits(input_chunk: Section, limits: Limits, flags: ChunkFlags):
    if limits.header_level == -1:
        return create_chunks_base_on_limits_max_size(input_chunk, limits, flags)
    else:
        return create_chunks_base_on_limits_header_level(input_chunk, limits, flags)


def _debug_print_lines(lines):
    print("\nlines:")
    for idx, line in enumerate(lines):
        print(idx, line)
    print("$" * 80)


def create_chunks_from_blocks(blocks, flags: ChunkFlags):
    results = []
    for block in blocks:
        outline = None
        if len(block) > 0:
            outline_sentences = block[0].get_outline_titles()
            if flags.add_outline and len(outline_sentences) > 0 and outline_sentences[0] == block[0].sentence:
                block.pop(0)
            outline = [fs.sentence.text for fs in outline_sentences[::-1]]
        result_block = Chunk([fs.sentence for fs in block], outline=outline)
        results.append(result_block)
    return results


def create_chunks_base_on_limits_header_level(input_chunk: Section, limits: Limits, flags: ChunkFlags):
    cc = ChunkContext()
    lines = create_flatline(input_chunk)
    limits_boundaries = set()
    len_lines = len(lines)
    lidx = 0
    while lidx < len_lines:
        line = lines[lidx]
        # print(f"{cc.current_size:03}/{limits.max_chunk_size:03}, {line}")
        cc.current_size += line.sentence.nrof_tokens

        if is_section(line.chunk) and line.chunk.header_data and lidx != 0 and line.chunk.header_data.resolved <= limits.header_level:
            cc.current_size = 0
            limits_boundaries.add(lidx)
        else:
            if cc.current_size > limits.max_chunk_size:
                cl_idx = find_block_limit(lines, lidx, limits_boundaries, limits)
                cc.current_size = 0
                if cl_idx not in limits_boundaries:
                    limits_boundaries.add(cl_idx)
                    lidx = cl_idx
                    continue
                else:
                    limits_boundaries.add(lidx)
        lidx += 1

    limits_boundaries = list(limits_boundaries)
    limits_boundaries.sort()
    blocks = []
    blidx = 0
    for elidx in limits_boundaries:
        blocks.append(lines[blidx:elidx])
        blidx = elidx
    if blidx < len_lines:
        blocks.append(lines[blidx:])

    results = create_chunks_from_blocks(blocks, flags)
    return results


def create_chunks_base_on_limits_max_size(input_chunk: Section, limits: Limits, flags: ChunkFlags):
    cc = ChunkContext()
    lines = create_flatline(input_chunk)
    limits_boundaries = set()
    len_lines = len(lines)
    lidx = 0
    while lidx < len_lines:
        line = lines[lidx]
        # print(f"{cc.current_size:03}/{limits.max_chunk_size:03}, {line}")
        cc.current_size += line.sentence.nrof_tokens
        if cc.current_size > limits.max_chunk_size:
            cl_idx = find_block_limit(lines, lidx, limits_boundaries, limits)
            cc.current_size = 0
            if cl_idx not in limits_boundaries:
                limits_boundaries.add(cl_idx)
                lidx = cl_idx
                continue
            else:
                limits_boundaries.add(lidx)
        lidx += 1

    limits_boundaries = list(limits_boundaries)
    limits_boundaries.sort()
    blocks = []
    blidx = 0
    for elidx in limits_boundaries:
        blocks.append(lines[blidx:elidx])
        blidx = elidx
    if blidx < len_lines:
        blocks.append(lines[blidx:])

    results = create_chunks_from_blocks(blocks, flags)
    return results


def format_results(results, flags: ChunkFlags, language: str | None = None):
    topics = None
    themes = None

    try:
        if language is not None:
            from wowool.topic_identifier import TopicIdentifier
            from wowool.semantic_themes import Themes

            topics = TopicIdentifier(language=language) if flags.add_topics else None
            themes = Themes() if flags.add_themes else None
    except ImportError:
        pass

    retval = []
    for cidx, result in enumerate(results):
        if result.sentences:
            chunk = {}

            if flags.add_outline and result.outline:
                chunk["outline"] = result.outline

            chunk["sentences"] = [s.text for s in result.sentences]
            chunk["begin_offset"] = result.sentences[0].sentence.begin_offset
            chunk["end_offset"] = result.sentences[-1].sentence.end_offset

            sentence_collection = [s.sentence for s in result.sentences]
            if themes:
                themes_results = themes.process(sentence_collection)
                if themes_results:
                    chunk["themes"] = themes_results
            if topics:
                topics_results = topics.get_topics(f"chunk_{cidx}", sentence_collection)
                if topics_results:
                    chunk["topics"] = topics_results

            retval.append(chunk)
        # print("themes_results:", themes_results)
        # chunk_id = f"chunk_{cidx}"
        # print("=======>>>>>>>", tp.get_topics(chunk_id, sentence_collection))

    return retval


def create_flatline(input_chunk: Section) -> list[FlatSentence]:

    output_chunk = []
    context = ChunkContext()

    def check_chunk_size(cc: ChunkContext, chunks: list[Section], cidx: int, sentences: list[ChunkSentence], sidx: int):
        output_chunk.append(FlatSentence(sentences[sidx], chunks[cidx]))

    foreach_sentence([input_chunk], 0, context, check_chunk_size)
    return output_chunk


def print_paragraphs(document: AnalysisDocument):

    for pidx, paragraph in enumerate(WowoolParagraph.iter(document)):
        print("paragraph:", pidx)
        for sent in Sentence.iter(paragraph):
            print("  sent:", sent.text)


def invalid_sentence(sent):
    if len(sent.tokens) == 0:
        return True
    if sent.tokens[0].literal == ".":
        return True
    return False


def create_document_outline(document: AnalysisDocument, flags: ChunkFlags):

    top_node = Section()
    current_chunk = top_node
    prev_paragraph_idx = 0
    top_chunk = current_chunk
    for pidx, paragraph in enumerate(WowoolParagraph.iter(document)):
        for sent in Sentence.iter(paragraph):
            if invalid_sentence(sent):
                continue
            header_info = get_header_info(sent)
            if header_info:

                while current_chunk and is_paragraph(current_chunk):
                    current_chunk = current_chunk.parent

                header_level = 0
                if header_info.type == HeaderType.Absolute:
                    header_level = header_info.level
                else:
                    absolute_parent_chunk = find_absolute_header(current_chunk)
                    if absolute_parent_chunk:
                        header_level = absolute_parent_chunk.header_data.level + header_info.level
                        header_info = Header(header_info.level, HeaderType.Relative, header_level)

                if header_level > current_chunk.level:
                    current_chunk = current_chunk.push_section(header_info, paragraph_idx=pidx)
                elif header_level < current_chunk.level:
                    while current_chunk and (header_level < current_chunk.level or isinstance(current_chunk, Paragraph)):
                        current_chunk = current_chunk.parent
                    if current_chunk.parent:
                        current_chunk = current_chunk.parent.push_section(header_info, paragraph_idx=pidx)
                elif current_chunk.parent:
                    current_chunk = current_chunk.parent.push_section(header_info, paragraph_idx=pidx)
                current_chunk.set_header(sent, flags)

            else:
                if is_section(current_chunk):
                    paragraph = Paragraph(paragraph_idx=pidx)
                    current_chunk = current_chunk.add_item(paragraph)
                elif is_paragraph(current_chunk) and prev_paragraph_idx != pidx:
                    paragraph = Paragraph(paragraph_idx=pidx)
                    current_chunk = current_chunk.parent.add_item(paragraph)

                assert is_paragraph(current_chunk)
                current_chunk.add_sentence(sent, flags)
            prev_paragraph_idx = pidx
        prev_paragraph_idx = pidx
    return top_chunk


required_canonicals = {"Person", "Company", "Country"}


class Chunks:
    ID = APP_ID

    def __init__(
        self,
        max_chunk_size: int = 100,
        soft_sentence_limit: int = 4,
        header_level: int = 1,
        canonicalize: bool = True,
        fix_spelling_mistakes: bool = True,
        lowercase: bool = False,
        cleanup: bool = False,
        stems: bool = False,
        dates: bool = True,
        add_themes: bool = False,
        add_topics: bool = False,
        add_outline: bool = False,
    ):
        self.max_chunk_size = max_chunk_size
        self.flags = ChunkFlags(
            {
                "canonicalize": canonicalize,
                "stems": stems,
                "dates": dates,
                "cleanup": cleanup,
                "lowercase": lowercase,
                "fix_spelling_mistakes": fix_spelling_mistakes,
                "add_themes": add_themes,
                "add_topics": add_topics,
                "add_outline": add_outline,
            }
        )
        self.limits = Limits(
            max_chunk_size=max_chunk_size,
            soft_sentence_limit=soft_sentence_limit,
            header_level=header_level,
        )

    def check_settings(self, document: AnalysisDocument, diagnostics: Diagnostics):
        if self.flags.canonicalize:
            concepts = set(document.metadata.get("concepts", []))
            if not any(item in concepts for item in required_canonicals):
                diagnostics.add(
                    Diagnostic(
                        document.id,
                        "The canonicalize flag is set but could not have entities, add the entity domain when using canonicalize options.",
                        DiagnosticType.Warning,
                    ),
                )
        if self.flags.add_topics:
            concepts = set(document.metadata.get("concepts", []))
            diagnostics.add(
                Diagnostic(
                    document.id,
                    "The topics flag is set but could not find TopicCandidates add the topics domain when using the topics option.",
                    DiagnosticType.Warning,
                )
            )

    @exceptions_to_diagnostics
    @requires_analysis
    def __call__(self, document: AnalysisDocument, diagnostics: Diagnostics) -> AnalysisDocument:
        """
        :param document:  The document we want to create chunks.
        :type document: AnalysisDocument

        :returns: The given document with the result data. See the :ref:`json format <json_apps_chunk>`
        """

        self.check_settings(document, diagnostics)

        top_chunk = create_document_outline(document, self.flags)
        output_chunks = create_chunks_base_on_limits(top_chunk, self.limits, self.flags)
        output_chunks = format_results(output_chunks, self.flags, document.language)

        if top_chunk:
            document.add_results(APP_ID, {"chunks": output_chunks})
        if diagnostics:
            document.add_diagnostics(APP_ID, diagnostics)
        return document
