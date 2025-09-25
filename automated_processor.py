#!/usr/bin/env python3
"""Simple automation runner to schedule periodic Reddit data processing."""

import time
import argparse
from pathlib import Path

from reddit_data_processor import RedditDataProcessor


def run_automation(subreddit, posts, data_dir, save_format, interval_minutes, iterations, client_id, client_secret, user_agent):
    for run in range(1, iterations + 1):
        print(f"\n=== Automation Run {run}/{iterations} ===")
        processor = RedditDataProcessor(client_id, client_secret, user_agent, data_dir)
        try:
            result = processor.process_data(subreddit, posts, save_format)
            if result:
                print(f"Run {run} complete: session {result['session_id']} processed {len(result['data'])} posts")
            else:
                print(f"Run {run} failed: see logs for details")
        finally:
            processor.close()

        if run < iterations:
            print(f"Sleeping for {interval_minutes} minute(s) before next run...")
            time.sleep(interval_minutes * 60)


def main():
    parser = argparse.ArgumentParser(description="Automate Reddit data collection at fixed intervals")
    parser.add_argument('--subreddit', default='iphone', help='Subreddit to scrape each run')
    parser.add_argument('--posts', type=int, default=200, help='Number of posts per run')
    parser.add_argument('--data-dir', default='reddit_data', help='Data storage directory')
    parser.add_argument('--format', choices=['json', 'pickle', 'clustering', 'all'], default='all', help='Output format')
    parser.add_argument('--interval', type=int, default=60, help='Interval between runs in minutes')
    parser.add_argument('--runs', type=int, default=3, help='How many runs to execute')
    parser.add_argument('--client-id', default='R4r2pV4_CLRBpr_Csx_F_A')
    parser.add_argument('--client-secret', default='ZHMtPtLx-PSYMAriIOXG4hD6XgkqlA')
    parser.add_argument('--user-agent', default='Beginning-Split862')

    args = parser.parse_args()

    run_automation(
        args.subreddit,
        args.posts,
        Path(args.data_dir),
        args.format,
        args.interval,
        args.runs,
        args.client_id,
        args.client_secret,
        args.user_agent
    )


if __name__ == '__main__':
    main()
