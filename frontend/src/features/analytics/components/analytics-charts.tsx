import type { EChartsCoreOption } from "echarts/core";

import { useMemo } from "react";

import type { DashboardStatistics } from "../statistics-schema";

import { EChart } from "./e-chart";

interface AnalyticsChartsProps {
  statistics: DashboardStatistics;
}

export function ClassDistributionChart({ statistics }: AnalyticsChartsProps) {
  const option = useMemo<EChartsCoreOption>(() => {
    const items = [...statistics.classes].reverse();

    return {
      aria: {
        enabled: true,
        description: "Bar chart showing detected object counts by class.",
      },

      tooltip: {
        trigger: "axis",
        axisPointer: {
          type: "shadow",
        },
      },

      grid: {
        left: 100,
        right: 24,
        top: 20,
        bottom: 40,
      },

      xAxis: {
        type: "value",
        minInterval: 1,
      },

      yAxis: {
        type: "category",
        data: items.map((item) => item.class_name),
      },

      series: [
        {
          name: "Objects",
          type: "bar",
          data: items.map((item) => item.object_count),
        },
      ],
    };
  }, [statistics]);

  return <EChart option={option} />;
}

const MAX_VISIBLE_AXIS_LABELS = 10;
const DEFAULT_VISIBLE_DAYS = 30;

function getAxisLabelInterval(pointCount: number): number {
  if (pointCount <= MAX_VISIBLE_AXIS_LABELS) {
    return 0;
  }

  return Math.max(
    0,
    Math.ceil(pointCount / MAX_VISIBLE_AXIS_LABELS) - 1,
  );
}

function getInitialZoomStart(pointCount: number): number {
  if (pointCount <= DEFAULT_VISIBLE_DAYS) {
    return 0;
  }

  return Math.max(
    0,
    ((pointCount - DEFAULT_VISIBLE_DAYS) / pointCount) * 100,
  );
}

function formatAxisDate(value: string): string {
  const dateParts = value.split("-");

  if (dateParts.length !== 3) {
    return value;
  }

  const [, month, day] = dateParts;

  return `${day}/${month}`;
}

export function DailyTrendChart({
  statistics,
}: AnalyticsChartsProps) {
  const option = useMemo<EChartsCoreOption>(() => {
    const pointCount = statistics.daily.length;
    const hasLongRange = pointCount > 14;
    const showSymbols = pointCount <= 14;
    const zoomStart = getInitialZoomStart(pointCount);

    return {
      aria: {
        show: true,
        description:
          "Line chart showing daily detection jobs and detected objects.",
      },

      animationDuration: 350,

      tooltip: {
        trigger: "axis",
        confine: true,
        axisPointer: {
          type: "line",
        },
      },

      legend: {
        top: 0,
        left: "center",
        data: ["Jobs", "Objects"],
      },

      grid: {
        left: 52,
        right: 24,
        top: 58,
        bottom: hasLongRange ? 92 : 50,
        containLabel: true,
      },

      xAxis: {
        type: "category",
        boundaryGap: false,

        data: statistics.daily.map(
          (item) => item.date,
        ),

        axisTick: {
          alignWithLabel: true,
        },

        axisLabel: {
          interval: getAxisLabelInterval(
            pointCount,
          ),
          hideOverlap: true,
          rotate: 0,
          margin: 14,
          formatter: formatAxisDate,
        },
      },

      yAxis: {
        type: "value",
        min: 0,
        minInterval: 1,
      },

      dataZoom: hasLongRange
        ? [
            {
              type: "inside",
              xAxisIndex: 0,
              start: zoomStart,
              end: 100,
            },
            {
              type: "slider",
              xAxisIndex: 0,
              start: zoomStart,
              end: 100,
              bottom: 10,
              height: 20,
              showDetail: false,
            },
          ]
        : [],

      series: [
        {
          name: "Jobs",
          type: "line",
          smooth: 0.25,
          showSymbol: showSymbols,
          symbolSize: 7,
          sampling: "lttb",

          data: statistics.daily.map(
            (item) => item.total_jobs,
          ),

          emphasis: {
            focus: "series",
          },
        },
        {
          name: "Objects",
          type: "line",
          smooth: 0.25,
          showSymbol: showSymbols,
          symbolSize: 7,
          sampling: "lttb",

          data: statistics.daily.map(
            (item) => item.detected_objects,
          ),

          emphasis: {
            focus: "series",
          },
        },
      ],
    };
  }, [statistics]);

  return (
    <EChart
      option={option}
      className="h-95 sm:h-105"
    />
  );
}

export function SourceDistributionChart({ statistics }: AnalyticsChartsProps) {
  const option = useMemo<EChartsCoreOption>(
    () => ({
      aria: {
        enabled: true,
        description: "Pie chart showing detection jobs by source type.",
      },

      tooltip: {
        trigger: "item",
      },

      legend: {
        bottom: 0,
      },

      series: [
        {
          name: "Sources",
          type: "pie",
          radius: ["45%", "70%"],

          data: statistics.sources.map((item) => ({
            name: item.source_type,
            value: item.job_count,
          })),
        },
      ],
    }),
    [statistics],
  );

  return <EChart option={option} />;
}
