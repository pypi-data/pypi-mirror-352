import re
from typing import List, Generator, Dict, Set, Tuple, Callable, NewType

from scrapy.http import TextResponse
from scrapy import Selector

NUMBER_RE = re.compile(r"\d+$")
MAX_HEADERS = 20

Columns = NewType("Columns", Tuple[str, ...])
Result = NewType("Result", Dict[str, str])
Uid = NewType("Uid", Tuple[Tuple[str, str], ...])


def extract_row_text(row: Selector) -> List[str]:
    text = []
    for td in row.xpath(".//th") or row.xpath(".//td"):
        text.append(" ".join(td.xpath(".//text()").extract()).strip())
    return text


def iterate_rows(table: Selector) -> Generator[Tuple[List[str], str | None], None, None]:
    for row in table.xpath(".//tr"):
        url = None
        for _url in row.xpath(".//a/@href").extract():
            if not _url.startswith("mailto:"):
                url = _url
                break
        yield extract_row_text(row), url


def find_table_headers(table: Selector, candidate_fields: Tuple[str, ...]) -> List[str]:
    max_score_row = []
    max_score = 0
    for rowtexts, _ in iterate_rows(table):
        row_score = 0
        lower_rowtexts = [t.lower() for t in rowtexts]
        for kw in candidate_fields:
            if kw in lower_rowtexts:
                row_score += 1
        if len(list(filter(None, rowtexts))) <= MAX_HEADERS and row_score > max_score:
            max_score = row_score
            max_score_row = rowtexts
    return max_score_row


def findstocktable(tables: List[Selector], candidate_fields: Tuple[str, ...]) -> Selector | None:
    max_score_table = None
    max_score1 = 0
    max_score2 = 0
    for table in tables[::-1]:
        # score = len(list(filter(None, find_table_headers(table))))
        score1 = len(
            list(
                filter(
                    None,
                    set(candidate_fields).intersection(
                        [f.lower() for f in find_table_headers(table, candidate_fields)]
                    ),
                )
            )
        )
        score2 = len(list(filter(None, find_table_headers(table, candidate_fields))))
        if score1 <= MAX_HEADERS and score1 > max_score1 or (score1 == max_score1 and score2 > max_score2):
            max_score1 = score1
            max_score2 = score2
            max_score_table = table
    return max_score_table


def parse_stock_table(stocktable: Selector, headers: List[str]):
    header_find_status = False
    headers_lower = [h.lower() for h in headers]
    for row, url in iterate_rows(stocktable):
        if not header_find_status and row != headers:
            continue
        header_find_status = True
        if row == headers:
            continue
        if len(row) != len(headers):
            continue
        data = dict(zip(headers_lower, row))
        if url:
            data["url"] = url
        yield data


def parse_stock_table_ii(stocktable: Selector, headers: List[str]):
    headers = list(filter(None, headers))
    header_find_status = False
    headers_lower = [h.lower() for h in headers]
    for row, url in iterate_rows(stocktable):
        row = list(filter(None, row))
        if not header_find_status and row != headers:
            continue
        header_find_status = True
        if row == headers:
            continue
        data = dict(zip(headers_lower, row))
        if url:
            data["url"] = url
        yield data


def default_validate_result(result: Dict[str, str], columns: Columns) -> bool:
    return True


def score_results(results: List[Result]) -> int:
    score = 0
    for result in results:
        score += len([i for i in result.keys() if i])
    return score


def unique_id(result: Dict[str, str], dedupe_keywords: Columns) -> Uid:
    uid = []
    for key in dedupe_keywords:
        value = result.get(key)
        if value:
            uid.append((key, value))
    return Uid(tuple(uid))


def remove_all_empty_fields(results: List[Result]):
    fields: Set[str] = set()
    for result in results:
        fields.update(result.keys())
    all_empty_fields = []
    for field in fields:
        if all(not r[field] for r in results):
            all_empty_fields.append(field)
    for field in all_empty_fields:
        for result in results:
            result.pop(field)


def parse_stock_tables_from_response(
    response: TextResponse,
    columns: Columns,
    validate_result: Callable[[Result, Columns], bool] = default_validate_result,
    dedupe_keywords: Columns = Columns(()),
) -> List[Result]:
    """
    Identifies and extracts data from an html table, based on the column names provided.
    response - The target response where to search for the table
    columns - the name of the columns to extract
    validate_result - a callable which validates and eventually filters out each result generated
                      by the algorithm
    dedupe_keywords - which columns use to deduplicate results (results with all same values in the same fields are
                      mutual dupes)
    """
    all_results: List[Result] = []
    fields: Set[str] = set()
    all_tables = response.xpath("//table")
    if all_tables:
        stocktable = findstocktable(all_tables, columns)
        if stocktable is not None:
            headers = find_table_headers(stocktable, columns)
            for parse_method in parse_stock_table, parse_stock_table_ii:
                all_results_method = []
                seen: Set[Uid] = set()
                for table in all_tables:
                    for result in parse_method(table, headers):
                        if validate_result(result, columns) and (uid := unique_id(result, dedupe_keywords)) not in seen:
                            if uid:
                                seen.add(uid)
                            all_results_method.append(result)
                            fields.update(result.keys())
                if score_results(all_results_method) > score_results(all_results):
                    all_results = all_results_method
    for result in all_results:
        for field in fields:
            result.setdefault(field, "")
    remove_all_empty_fields(all_results)
    return all_results
