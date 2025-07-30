"""Cross-platform monitor for browser performance metrics."""

import logging
import time
from typing import Any, Dict, List

from selenium import webdriver

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Cross-platform monitor for browser performance."""

    def __init__(self, driver: webdriver.Chrome) -> None:
        """
        Initialize PerformanceMonitor.

        Args:
            driver: WebDriver instance
        """
        self.driver = driver

    def get_page_load_time(self) -> float:
        """
        Get page loading time.

        Returns:
            Load time in seconds
        """
        try:
            navigation_start = self.driver.execute_script(
                "return window.performance.timing.navigationStart"
            )
            dom_complete = self.driver.execute_script(
                "return window.performance.timing.domComplete"
            )
            load_time = (dom_complete - navigation_start) / 1000.0
            logger.debug(f"Page load time: {load_time:.2f}s")
            return load_time
        except Exception as e:
            logger.warning(f"Could not get page load time: {e}")
            return 0.0

    def get_memory_usage(self) -> Dict[str, Any]:
        """
        Get memory usage (cross-platform).

        Returns:
            Dictionary with memory information
        """
        try:
            memory_info = self.driver.execute_script(
                """
                if ('memory' in performance) {
                    return {
                        usedJSHeapSize: performance.memory.usedJSHeapSize,
                        totalJSHeapSize: performance.memory.totalJSHeapSize,
                        jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
                    };
                }
                return null;
                """
            )

            if memory_info:
                result = {
                    "used_heap": memory_info.get("usedJSHeapSize", 0),
                    "total_heap": memory_info.get("totalJSHeapSize", 0),
                    "heap_limit": memory_info.get("jsHeapSizeLimit", 0),
                }
                logger.debug(f"Memory usage: {result['used_heap'] / 1024 / 1024:.1f}MB used")
                return result
            else:
                # Fallback for browsers without Memory API
                logger.debug("Memory API not available")
                return {
                    "used_heap": 0,
                    "total_heap": 0,
                    "heap_limit": 0,
                }
        except Exception as e:
            logger.warning(f"Could not get memory usage: {e}")
            return {}

    def get_network_timing(self) -> Dict[str, Any]:
        """
        Get network timing information.

        Returns:
            Dictionary with timing information
        """
        try:
            timing = self.driver.execute_script(
                """
                var timing = performance.getEntriesByType('navigation')[0];
                if (timing) {
                    return {
                        dnsLookup: timing.domainLookupEnd - timing.domainLookupStart,
                        tcpConnect: timing.connectEnd - timing.connectStart,
                        request: timing.responseStart - timing.requestStart,
                        response: timing.responseEnd - timing.responseStart,
                        domParsing: timing.domContentLoadedEventStart - timing.responseEnd,
                        resourceLoad: timing.loadEventStart - timing.domContentLoadedEventEnd
                    };
                }
                return null;
                """
            )

            if timing:
                logger.debug(f"Network timing - DNS: {timing.get('dnsLookup', 0):.0f}ms, "
                           f"Connect: {timing.get('tcpConnect', 0):.0f}ms")

            return timing or {}
        except Exception as e:
            logger.warning(f"Could not get network timing: {e}")
            return {}

    def get_resource_timing(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get resource timing for slowest resources.

        Args:
            limit: Number of resources to return

        Returns:
            List of slowest resources
        """
        try:
            resources = self.driver.execute_script(
                f"""
                var resources = performance.getEntriesByType('resource');
                return resources
                    .map(function(resource) {{
                        return {{
                            name: resource.name,
                            duration: resource.duration,
                            size: resource.transferSize || 0,
                            type: resource.initiatorType
                        }};
                    }})
                    .sort(function(a, b) {{ return b.duration - a.duration; }})
                    .slice(0, {limit});
                """
            )

            if resources:
                logger.debug(f"Found {len(resources)} resources, slowest: "
                           f"{resources[0]['duration']:.0f}ms" if resources else "none")

            return resources or []
        except Exception as e:
            logger.warning(f"Could not get resource timing: {e}")
            return []

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive performance metrics.

        Returns:
            Dictionary with all performance data
        """
        metrics = {
            "timestamp": time.time(),
            "url": self.driver.current_url,
            "load_time": self.get_page_load_time(),
            "memory": self.get_memory_usage(),
            "network": self.get_network_timing(),
            "slow_resources": self.get_resource_timing(5),
        }

        logger.debug("Collected comprehensive performance metrics")
        return metrics

    def log_performance_metrics(self) -> None:
        """Log comprehensive performance metrics."""
        try:
            load_time = self.get_page_load_time()
            memory = self.get_memory_usage()
            network = self.get_network_timing()

            logger.info("📊 Performance Metrics:")
            logger.info(f"   Page load time: {load_time:.2f}s")

            if memory:
                memory_mb = memory['used_heap'] / 1024 / 1024
                total_mb = memory['total_heap'] / 1024 / 1024
                logger.info(f"   Memory usage: {memory_mb:.1f}MB / {total_mb:.1f}MB")

            if network:
                logger.info(f"   DNS lookup: {network.get('dnsLookup', 0):.0f}ms")
                logger.info(f"   TCP connect: {network.get('tcpConnect', 0):.0f}ms")
                logger.info(f"   Request: {network.get('request', 0):.0f}ms")
                logger.info(f"   Response: {network.get('response', 0):.0f}ms")

        except Exception as e:
            logger.warning(f"Failed to log performance metrics: {e}")

    def create_performance_report(self) -> Dict[str, Any]:
        """
        Create detailed performance report.

        Returns:
            Dictionary with performance data
        """
        report = self.get_performance_metrics()

        # Add computed metrics
        if report["memory"]:
            memory_usage_percent = 0
            if report["memory"]["heap_limit"] > 0:
                memory_usage_percent = (report["memory"]["used_heap"] /
                                      report["memory"]["heap_limit"]) * 100
            report["memory_usage_percent"] = memory_usage_percent

        # Add performance score (simple heuristic)
        load_time = report["load_time"]
        if load_time < 1.0:
            performance_score = "excellent"
        elif load_time < 3.0:
            performance_score = "good"
        elif load_time < 5.0:
            performance_score = "fair"
        else:
            performance_score = "poor"

        report["performance_score"] = performance_score

        logger.info(f"Performance report created - Score: {performance_score}")
        return report
