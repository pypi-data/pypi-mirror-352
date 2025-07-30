import argparse
from deplacecli.commands import Command

def main():

    parser = argparse.ArgumentParser(description="Deplace CLI - A tool to access Deplace AI datasets.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # List available commands when no commands / a wrong command is provided
    parser.set_defaults(func=lambda: parser.print_help())

    # Common arguments for all commands
    common = argparse.ArgumentParser(add_help=False)
    # No common arguments for all commands at the moment
    
    # Download
    download_parser = subparsers.add_parser("download", parents=[common])
    download_parser.add_argument("--token", required=True, help="Key for Storage Authentication")
    download_parser.add_argument("--path", default="deplace/", help="Path to download the dataset to (default: deplace/)")
    download_parser.add_argument("--dataset", default="sample", help="Dataset version to download (default: sample)")
    download_parser.add_argument("--limit", type=int, default=0, help="Limit the number of files to download (default: 0 means no limit)")
    download_parser.add_argument("--demo", action="store_true", default=False, help="Demo mode.")

    # Annotate
    annotate_parser = subparsers.add_parser("annotate", parents=[common])
    annotate_parser.add_argument("--episode", required=True, help="Episode in the format Vxx_Eyy")
    annotate_parser.add_argument("--output_folder", default="annotated/", help="Output folder for annotated video")
    annotate_parser.add_argument("--bbox", action="store_true", help="Enable bounding box annotation")
    annotate_parser.add_argument("--mask", action="store_true", help="Enable mask annotation")
    annotate_parser.add_argument("--label", action="store_true", help="Enable label annotation")
    annotate_parser.add_argument("--compression", choices=["avc1", "mp4v", "h264"], default="mp4v", help="Compression format for the annotated video")

    args = parser.parse_args()

    # Execute the command based on the subcommand
    if args.command == "download":
        Command.download(
            token=args.token, 
            source_folder=args.dataset,
            target_folder=args.path,
            limit_mp4=args.limit,
            demo=args.demo
        )

    elif args.command == "annotate":
        Command.annotate(
            episode=args.episode,
            output_folder=args.output_folder,
            bbox=args.bbox,
            mask=args.mask,
            label=args.label,
            compression=args.compression
        )

    elif args.command is None:
        parser.print_help()




    



