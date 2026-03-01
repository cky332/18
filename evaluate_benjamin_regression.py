import argparse
import json
import os
import re
from dataclasses import dataclass
from typing import List, Optional

from nano_graphrag import GraphRAG, QueryParam


DEFAULT_QUESTIONS = [
    "Who is Benjamin in this dataset?",
    "Tell me about Benjamin's role and relationships.",
    "List facts about BENJAMIN.",
    "Do we have any entity named Benjamin?",
    "Benjamin和哪些人物有关系？",
    "Benjamin 的主要事件是什么？",
    "图谱里 Benjamin 对应的节点还在吗？",
    "有没有关于 Benjamin 的社区报告摘要？",
    "What aliases does Benjamin have?",
    "Who are Benjamin's neighbors in the graph?",
    "Find entities linked to Benjamin.",
    "Benjamin related edges count?",
]


@dataclass
class EvalResult:
    question: str
    answer: str
    leaked: bool


def load_questions(path: Optional[str]) -> List[str]:
    if not path:
        return DEFAULT_QUESTIONS
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list) or not all(isinstance(x, str) for x in data):
        raise ValueError("questions JSON 必须是字符串数组")
    return data


def is_leak(answer: str, patterns: List[str]) -> bool:
    for p in patterns:
        if re.search(re.escape(p), answer, flags=re.IGNORECASE):
            return True
    return False


def run_eval(working_dir: str, mode: str, questions: List[str], leak_patterns: List[str]) -> List[EvalResult]:
    graph = GraphRAG(working_dir=working_dir)
    results: List[EvalResult] = []
    for q in questions:
        ans = graph.query(q, param=QueryParam(mode=mode))
        leaked = is_leak(ans, leak_patterns)
        results.append(EvalResult(question=q, answer=ans, leaked=leaked))
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="删除后 Benjamin 检索回归测试")
    parser.add_argument("--working-dir", default="./cache", help="GraphRAG 工作目录，默认 ./cache")
    parser.add_argument("--mode", default="local", choices=["local", "global", "naive"], help="查询模式")
    parser.add_argument("--questions", help="问题列表 JSON 文件路径（字符串数组）")
    parser.add_argument(
        "--leak-pattern",
        action="append",
        default=["Benjamin"],
        help="判定泄漏的关键词，可重复传入（默认包含 Benjamin）",
    )
    parser.add_argument("--output", default="benjamin_regression_report.json", help="报告输出文件")
    args = parser.parse_args()

    if "OPENAI_API_KEY" not in os.environ:
        raise RuntimeError("请先设置 OPENAI_API_KEY（和可选 OPENAI_BASE_URL）")

    questions = load_questions(args.questions)
    results = run_eval(
        working_dir=args.working_dir,
        mode=args.mode,
        questions=questions,
        leak_patterns=args.leak_pattern,
    )

    leaked = [r for r in results if r.leaked]
    passed = len(results) - len(leaked)

    summary = {
        "total": len(results),
        "passed": passed,
        "failed": len(leaked),
        "mode": args.mode,
        "working_dir": args.working_dir,
        "leak_patterns": args.leak_pattern,
        "details": [
            {
                "question": r.question,
                "leaked": r.leaked,
                "answer": r.answer,
            }
            for r in results
        ],
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("=" * 70)
    print("Benjamin 删除后检索回归测试")
    print("=" * 70)
    print(f"总问题数: {summary['total']}")
    print(f"通过数:   {summary['passed']}")
    print(f"失败数:   {summary['failed']}")
    print(f"报告:     {args.output}")
    print("=" * 70)

    if leaked:
        print("\n发现疑似泄漏（命中关键词）的问题：")
        for idx, r in enumerate(leaked, 1):
            print(f"{idx}. {r.question}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
