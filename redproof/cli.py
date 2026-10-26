"""Command-line entry point for Redproof."""

from redproof import __version__


def main() -> int:
    print(f"redproof {__version__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())