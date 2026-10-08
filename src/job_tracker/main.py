import argparse
import json
from pathlib import Path

from .extractor import extract_requirements


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract requirements from a job description."
    )
    parser.add_argument(
        "file",
        type=Path,
        help="Path to a text file containing the job description.",
    )

    args = parser.parse_args()

    if not args.file.exists():
        raise FileNotFoundError(f"File not found: {args.file}")

    job_description = args.file.read_text(encoding="utf-8")
    requirements = extract_requirements(job_description)

    print(json.dumps(requirements, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()