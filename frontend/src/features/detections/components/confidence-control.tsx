interface ConfidenceControlProps {
  value: number;
  onChange: (value: number) => void;
  disabled?: boolean;
}

export function ConfidenceControl({ value, onChange, disabled = false }: ConfidenceControlProps) {
  const percentage = Math.round(value * 100);

  return (
    <div>
      <div className="flex items-center justify-between gap-4">
        <label htmlFor="confidence-threshold" className="text-sm font-semibold text-slate-900">
          Confidence threshold
        </label>

        <output
          htmlFor="confidence-threshold"
          className="rounded-md bg-blue-50 px-2.5 py-1 text-sm font-bold text-blue-700"
        >
          {percentage}%
        </output>
      </div>

      <input
        id="confidence-threshold"
        type="range"
        min="0.01"
        max="1"
        step="0.01"
        value={value}
        disabled={disabled}
        onChange={(event) => {
          onChange(Number(event.target.value));
        }}
        className="mt-4 h-2 w-full cursor-pointer appearance-none rounded-full bg-slate-200 accent-blue-600 disabled:cursor-not-allowed"
      />

      <div className="mt-2 flex justify-between text-xs text-slate-500">
        <span>More detections</span>
        <span>Higher precision</span>
      </div>

      <p className="mt-3 text-sm leading-6 text-slate-500">
        Lower values may detect more objects but can increase false positives.
      </p>
    </div>
  );
}
