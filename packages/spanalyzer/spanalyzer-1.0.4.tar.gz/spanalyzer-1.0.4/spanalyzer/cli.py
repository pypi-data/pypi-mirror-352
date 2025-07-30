# CLI for the spanalyzer

import argparse

from spanalyzer.engine import Engine


def main():
    """
    Main function for the spanalyzer CLI.
    """

    description = """
    Spanalyzer - OpenTelemetry Code Analysis Tool

    A static code analysis tool that detects and reports OpenTelemetry instrumentation
    in your codebase. It analyzes Python and Java source files to identify:
    - Tracer definitions
    - Span operations
    - Attribute settings
    - Event recordings
    - Counter metrics

    The tool provides two report types:
    - basic: A terminal-based overview of telemetry coverage
    - detailed: A comprehensive JSON report of all telemetry operations
    """

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "report_type",
        type=str,
        help="Type of report to generate",
        choices=["basic", "detailed"],
    )
    parser.add_argument(
        "-p",
        "--path",
        type=str,
        help="Path to the folder containing the scripts to be analyzed",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to the output file",
        default="spanalyzer_report.json",
    )
    parser.add_argument(
        "-l",
        "--language",
        type=str,
        help="Language of the scripts to be analyzed",
        choices=["python", "java"],
        default="python",
    )

    args = parser.parse_args()

    engine = Engine(
        args.path, args.report_type, language=args.language, output_path=args.output
    )

    engine.run()
