import argparse
import logging
import os

from prophecy_lineage_extractor.reader import get_reader




def main():
    parser = argparse.ArgumentParser(description="Prophecy Lineage Extractor")
    parser.add_argument("--project-id", type=str, required=True, help="Prophecy Project ID")
    parser.add_argument("--pipeline-id", type=str, required=True, nargs='+', help="Prophecy Pipeline ID(s)")
    parser.add_argument("--send-email", action="store_true", help="Enable verbose output")
    parser.add_argument("--branch", type=str, default="default", help="Branch to run lineage extractor on")
    parser.add_argument("--reader", type=str, default="lineage", help="Read Via 'lineage' backend or 'knowledge-graph' backend to run lineage extractor on")
    parser.add_argument("--recursive_extract", type=str, default="true", help="Whether to Recursively include Upstream Source Transformations")
    parser.add_argument("--run_for_all", type=str, default="false", help="Whether to Create Project Level Sheet")
    parser.add_argument("--output-dir", type=str, required=True, help="Output directory inside the project")
    parser.add_argument("--fmt", type=str, required=False, help="What format to write to")
    parser.add_argument("--log-level", type=str, default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Set the logging level")

    args = parser.parse_args()

    # Configure logging with the specified log level
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logging.info(f"Logging level set to {args.log_level}")
    pipeline_id_str = args.pipeline_id[0]
    reader_str = args.reader
    pipeline_output_dir = os.path.join(args.output_dir)
    os.makedirs(pipeline_output_dir, exist_ok=True)
    logging.info(f"pipeline_id={pipeline_id_str}")
    reader = get_reader(reader_str)(
        project_id=args.project_id,
        branch=args.branch,
        output_dir=pipeline_output_dir,
        send_email=args.send_email,
        recursive_extract=args.recursive_extract,
        run_for_all = args.run_for_all,
        fmt=args.fmt if args.fmt else 'excel',
        pipeline_id_str=pipeline_id_str,
    )
    reader.process()
    # reader.writer.write()

if __name__ == "__main__":
    main()