#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path
from typing import List, Optional
from .scrubber import Scrubber


def scrub_file(file_path: Path, scrubber: Scrubber, output_path: Optional[Path] = None) -> bool:
    try:
        content = file_path.read_text()
        matches = scrubber.scan(content)
        
        if matches:
            print(f"Found {len(matches)} potential secrets in {file_path}:")
            for match in matches:
                print(f"  - {match.pattern_name}: {match.value[:20]}... (line {content[:match.start].count(chr(10)) + 1})")
            
            scrubbed_content = scrubber.scrub_response(content)
            
            if output_path:
                output_path.write_text(scrubbed_content)
                print(f"Scrubbed content written to {output_path}")
            else:
                print("\nScrubbed content:")
                print(scrubbed_content)
            
            return True
        else:
            print(f"No secrets found in {file_path}")
            return False
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        return False


def scrub_stdin(scrubber: Scrubber) -> bool:
    content = sys.stdin.read()
    matches = scrubber.scan(content)
    
    if matches:
        print(f"Found {len(matches)} potential secrets in stdin:", file=sys.stderr)
        for match in matches:
            print(f"  - {match.pattern_name}: {match.value[:20]}...", file=sys.stderr)
        
        scrubbed_content = scrubber.scrub_response(content)
        print(scrubbed_content)
        return True
    else:
        print(content)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Scrub secrets from files or stdin",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  scrub-llm file.log                    # Check file for secrets
  scrub-llm file.log -o cleaned.log     # Write scrubbed output
  cat file.log | scrub-llm              # Process stdin
  scrub-llm *.log                       # Process multiple files
"""
    )
    
    parser.add_argument(
        'files',
        nargs='*',
        type=Path,
        help='Files to scrub (if none provided, reads from stdin)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output file for scrubbed content (only valid with single input file)'
    )
    
    parser.add_argument(
        '--no-regex',
        action='store_true',
        help='Disable regex-based detection'
    )
    
    parser.add_argument(
        '--no-entropy',
        action='store_true',
        help='Disable entropy-based detection'
    )
    
    parser.add_argument(
        '--min-entropy',
        type=float,
        default=3.5,
        help='Minimum Shannon entropy for detection (default: 3.5)'
    )
    
    parser.add_argument(
        '--min-length',
        type=int,
        default=20,
        help='Minimum string length for entropy detection (default: 20)'
    )
    
    args = parser.parse_args()
    
    if args.output and len(args.files) != 1:
        parser.error("--output can only be used with a single input file")
    
    scrubber = Scrubber(
        enable_regex=not args.no_regex,
        enable_entropy=not args.no_entropy,
        min_entropy=args.min_entropy,
        min_entropy_length=args.min_length
    )
    
    found_secrets = False
    
    if not args.files:
        found_secrets = scrub_stdin(scrubber)
    else:
        for file_path in args.files:
            if not file_path.exists():
                print(f"Error: {file_path} does not exist", file=sys.stderr)
                continue
            
            output_path = args.output if len(args.files) == 1 else None
            if scrub_file(file_path, scrubber, output_path):
                found_secrets = True
    
    sys.exit(1 if found_secrets else 0)


if __name__ == '__main__':
    main()