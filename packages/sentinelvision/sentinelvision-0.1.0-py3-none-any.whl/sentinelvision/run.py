import argparse
from core.pipeline import run_pipeline

def main():
    parser = argparse.ArgumentParser(description="SentinelVision: Real-time visual tracking and reasoning")
    parser.add_argument('--config', type=str, default=None, help='Path to custom config YAML (optional)')
    args = parser.parse_args()

    run_pipeline(args.config)

if __name__ == "__main__":
    main()
