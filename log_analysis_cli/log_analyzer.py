import logging
import argparse
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()


class LogAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.ip_counter = {}
        self.errors = {}
        self.total_size = 0
        self.total_requests = 0

    def analyze_logs(self):
        with open(self.file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.replace('"', "")
                parts = line.split()

                if len(parts) >= 9:
                    ip = parts[0]
                    status_code = parts[-2]
                    size = parts[-1] if parts[-1] != "-" else "0"

                    self.ip_counter[ip] = self.ip_counter.get(ip, 0) + 1
                    if 400 <= int(status_code) < 600:
                        self.errors[status_code] = (
                            self.errors.get(status_code, 0) + 1
                        )
                    self.total_size += int(size)
                    self.total_requests += 1

    def get_top_ips(self):
        top_ips = sorted(
            self.ip_counter.items(), key=lambda x: x[1], reverse=True
        )[:5]
        return top_ips

    def get_top_errors(self):
        top_errors = sorted(
            self.errors.items(), key=lambda x: x[1], reverse=True
        )[:5]
        return top_errors

    def get_average_size(self):
        if self.total_requests == 0:
            return 0
        return self.total_size / self.total_requests

    def print_report(self):
        logger.info("Top 5 ip addresses:")
        top_ips = self.get_top_ips()
        for ip, count in top_ips:
            logger.info(f"{ip}: {count} requests")

        logger.info("Top 5 Errors:")
        top_errors = self.get_top_errors()
        for error, count in top_errors:
            logger.info(f"Error {error}: {count} occurrences")

        avg_size = self.get_average_size()
        logger.info(f"Average response size: {avg_size:.2f} bytes")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("log_file", nargs="?")
    args = parser.parse_args()

    if not args.log_file:
        logger.error("No log file provided. Please specify a log file.")
    else:
        file_path = Path(args.log_file)
        if not file_path.is_file():
            logger.error(f"The file {args.log_file} does not exist.")
        else:
            analyzer = LogAnalyzer(file_path)
            analyzer.analyze_logs()
            analyzer.print_report()
