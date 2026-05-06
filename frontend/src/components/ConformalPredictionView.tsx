/**
 * Equine Oracle v3.1 - Conformal Prediction View
 * Frontend component for displaying prediction sets and uncertainty
 */

import React, { useState, useEffect } from 'react';
import { Card, Badge, Toggle, Tooltip, ProgressBar, Alert } from '../ui/components';
import { usePrediction } from '../hooks/usePrediction';

interface ConformalPredictionViewProps {
  raceId: string;
  betType: 'exacta' | 'trifecta' | 'quartet';
  onCombinationSelect?: (combination: number[]) => void;
}

interface PredictionSet {
  horses: number[];
  scores: number[];
  set_size: number;
  quantile_threshold: number;
}

interface ConformalData {
  prediction_sets: Record<string, PredictionSet>;
  uncertainty_coefficient: Record<string, number>;
  valid_combinations: number[][];
  coverage_guarantee: number;
  total_combinations: number;
  high_uncertainty_warning: boolean;
  calibrated: boolean;
}

export const ConformalPredictionView: React.FC<ConformalPredictionViewProps> = ({
  raceId,
  betType,
  onCombinationSelect
}) => {
  const [data, setData] = useState<ConformalData | null>(null);
  const [loading, setLoading] = useState(false);
  const [showSets, setShowSets] = useState(true);
  const [selectedCombo, setSelectedCombo] = useState<number[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { fetchExoticPrediction } = usePrediction();

  useEffect(() => {
    loadPrediction();
  }, [raceId, betType]);

  const loadPrediction = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await fetchExoticPrediction(raceId, betType);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load prediction');
    } finally {
      setLoading(false);
    }
  };

  // Uncertainty color coding
  const getUncertaintyColor = (coefficient: number): string => {
    if (coefficient < 0.25) return 'green';    // Low uncertainty
    if (coefficient < 0.40) return 'yellow';   // Medium uncertainty
    return 'red';                               // High uncertainty
  };

  // Horse confidence color
  const getHorseColor = (score: number): string => {
    if (score > 0.30) return 'green';
    if (score > 0.15) return 'yellow';
    return 'gray';
  };

  if (loading) {
    return (
      <Card className="conformal-loading">
        <div className="flex items-center justify-center p-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Loading conformal predictions...</span>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert type="error" className="m-4">
        {error}
      </Alert>
    );
  }

  if (!data) return null;

  const positions = betType === 'exacta' ? ['1st', '2nd'] 
                  : betType === 'trifecta' ? ['1st', '2nd', '3rd']
                  : ['1st', '2nd', '3rd', '4th'];

  return (
    <Card className="conformal-prediction-view max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-6 border-b pb-4">
        <div>
          <h3 className="text-xl font-bold text-gray-900">
            Conformal Prediction Sets
          </h3>
          <p className="text-sm text-gray-500 mt-1">
            {betType.toUpperCase()} • {data.total_combinations} valid combinations
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <Toggle 
            checked={showSets}
            onChange={setShowSets}
            label="Show Sets"
          />
          <Badge 
            color={data.calibrated ? 'green' : 'yellow'}
            className="text-sm"
          >
            {data.calibrated ? 'Calibrated' : 'Uncalibrated'}
          </Badge>
          <Tooltip content="90% coverage guarantee: true outcome in set 9/10 times">
            <Badge color="blue" className="cursor-help">
              {(data.coverage_guarantee * 100).toFixed(0)}% Coverage
            </Badge>
          </Tooltip>
        </div>
      </div>

      {/* High Uncertainty Warning */}
      {data.high_uncertainty_warning && (
        <Alert type="warning" className="mb-4">
          <div className="flex items-start">
            <span className="text-2xl mr-2">⚠️</span>
            <div>
              <p className="font-semibold">Wide Prediction Sets Detected</p>
              <p className="text-sm">
                High uncertainty race—model is less certain about outcomes. 
                Consider reducing stake size or waiting for more information.
              </p>
            </div>
          </div>
        </Alert>
      )}

      {/* Prediction Sets */}
      {showSets && (
        <div className="prediction-sets space-y-4 mb-6">
          {positions.map((position) => {
            const setData = data.prediction_sets[position];
            const uncertainty = data.uncertainty_coefficient[position];
            const color = getUncertaintyColor(uncertainty);

            return (
              <div 
                key={position}
                className="position-set p-4 rounded-lg border border-gray-200"
              >
                {/* Position Header */}
                <div className="flex justify-between items-center mb-3">
                  <div className="flex items-center gap-3">
                    <span className="text-lg font-bold text-gray-800">
                      {position === '1st' ? '🥇' : position === '2nd' ? '🥈' : position === '3rd' ? '🥉' : '4️⃣'} 
                      {position}
                    </span>
                    <Badge color={color}>
                      u = {uncertainty.toFixed(3)}
                    </Badge>
                  </div>
                  
                  <Tooltip content={`Set size: ${setData.set_size} horses`}>
                    <span className="text-sm text-gray-500">
                      {setData.set_size} horses in set
                    </span>
                  </Tooltip>
                </div>

                {/* Uncertainty Bar */}
                <div className="mb-3">
                  <ProgressBar 
                    value={uncertainty * 100}
                    max={100}
                    color={color}
                    label={`Uncertainty: ${(uncertainty * 100).toFixed(1)}%`}
                  />
                </div>

                {/* Horse Chips */}
                <div className="horse-chips flex flex-wrap gap-2">
                  {setData.horses.map((horseIdx, i) => (
                    <Tooltip 
                      key={horseIdx}
                      content={`Calibrated probability: ${(setData.scores[i] * 100).toFixed(1)}%`}
                    >
                      <Badge 
                        color={getHorseColor(setData.scores[i])}
                        className="text-sm px-3 py-1 cursor-pointer hover:opacity-80"
                      >
                        Horse {horseIdx + 1}
                        <span className="ml-2 text-xs opacity-75">
                          {(setData.scores[i] * 100).toFixed(0)}%
                        </span>
                      </Badge>
                    </Tooltip>
                  ))}
                </div>

                {/* Technical detail (collapsible) */}
                <details className="mt-2 text-xs text-gray-500">
                  <summary>Technical details</summary>
                  <p>Quantile threshold: {setData.quantile_threshold.toFixed(4)}</p>
                  <p>Non-conformity scores used for set construction</p>
                </details>
              </div>
            );
          })}
        </div>
      )}

      {/* Valid Combinations */}
      <div className="valid-combinations">
        <h4 className="text-lg font-semibold mb-3">
          Top {Math.min(10, data.valid_combinations.length)} Valid Combinations
        </h4>
        
        <div className="combo-grid grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
          {data.valid_combinations.slice(0, 10).map((combo, idx) => (
            <button
              key={idx}
              onClick={() => {
                setSelectedCombo(combo);
                onCombinationSelect?.(combo);
              }}
              className={`
                combo-item p-3 rounded-lg border text-left transition-all
                ${selectedCombo?.join(',') === combo.join(',') 
                  ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200' 
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'}
              `}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-gray-600">
                  Combo #{idx + 1}
                </span>
                {selectedCombo?.join(',') === combo.join(',') && (
                  <Badge color="blue" size="sm">Selected</Badge>
                )}
              </div>
              <div className="text-lg font-mono">
                {combo.map((horse, i) => (
                  <span key={i}>
                    <span className="font-bold text-gray-900">H{horse + 1}</span>
                    {i < combo.length - 1 && (
                      <span className="text-gray-400 mx-1">→</span>
                    )}
                  </span>
                ))}
              </div>
            </button>
          ))}
        </div>

        {data.valid_combinations.length > 10 && (
          <p className="text-sm text-gray-500 mt-3 text-center">
            +{data.valid_combinations.length - 10} more combinations available
          </p>
        )}
      </div>

      {/* Calibration Notice */}
      {!data.calibrated && (
        <Alert type="info" className="mt-4">
          Running in fallback mode (uncalibrated). For production use, 
          ensure calibration engine is fitted on validation data.
        </Alert>
      )}
    </Card>
  );
};

// Hook for fetching predictions
export const useConformalPrediction = () => {
  const fetchExoticPrediction = async (
    raceId: string, 
    betType: string
  ): Promise<ConformalData> => {
    const response = await fetch('/api/v1/predict/exotic', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        race_id: raceId,
        bet_type: betType,
        jurisdiction: localStorage.getItem('jurisdiction') || 'NZ'
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  };

  return { fetchExoticPrediction };
};
