import { BarChart, LineChart, PieChart } from "echarts/charts";

import {
  AriaComponent,
  DataZoomComponent,
  GridComponent,
  LegendComponent,
  TooltipComponent,
} from "echarts/components";

import * as echarts from "echarts/core";

import type { EChartsCoreOption, EChartsType } from "echarts/core";

import { CanvasRenderer } from "echarts/renderers";

import { useEffect, useRef } from "react";

import { cn } from "../../../lib/cn";

echarts.use([
  BarChart,
  LineChart,
  PieChart,

  AriaComponent,
  DataZoomComponent,
  GridComponent,
  LegendComponent,
  TooltipComponent,

  CanvasRenderer,
]);

interface EChartProps {
  option: EChartsCoreOption;
  className?: string;
}

export function EChart({ option, className }: EChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  const chartRef = useRef<EChartsType | null>(null);

  useEffect(() => {
    const container = containerRef.current;

    if (!container) {
      return;
    }

    const chart = echarts.init(container);

    chartRef.current = chart;

    const resizeObserver = new ResizeObserver(() => {
      chart.resize();
    });

    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();
      chart.dispose();
      chartRef.current = null;
    };
  }, []);

  useEffect(() => {
    chartRef.current?.setOption(option, true);
  }, [option]);

  return <div ref={containerRef} className={cn("h-80 w-full", className)} />;
}
