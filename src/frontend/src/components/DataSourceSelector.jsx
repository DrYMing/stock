/**
 * 数据源选择器组件
 */

import { useState, useEffect } from 'react';
import { api } from '../api';

function DataSourceSelector({ currentSource, onSourceChange }) {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const loadSources = async () => {
      try {
        const data = await api.getDataSources();
        setSources(data.sources);
        // 同步当前数据源状态
        if (data.current_source && data.current_source !== currentSource) {
          onSourceChange(data.current_source);
        }
      } catch (err) {
        console.error('Failed to load data sources:', err);
      } finally {
        setLoading(false);
      }
    };
    loadSources();
  }, []);

  const handleSwitchSource = async (sourceName) => {
    try {
      await api.switchSource(sourceName);
      onSourceChange(sourceName);
      setIsOpen(false);
    } catch (err) {
      console.error('Failed to switch source:', err);
      alert('切换数据源失败: ' + err.message);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow px-4 py-2">
        <span className="text-gray-500 text-sm">加载数据源...</span>
      </div>
    );
  }

  const currentSourceData = sources.find(s => s.name === currentSource) || sources[0];

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="bg-white rounded-lg shadow px-4 py-2 flex items-center gap-2 hover:bg-gray-50 transition-colors"
      >
        <span className="text-gray-700 text-sm">数据源:</span>
        <span className="text-blue-600 font-medium text-sm">
          {currentSourceData?.display_name || currentSourceData?.name || '未知'}
        </span>
        <svg
          className={`w-4 h-4 text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-xl z-20 border border-gray-200">
            <div className="py-2">
              <div className="px-4 py-2 border-b border-gray-100">
                <h3 className="text-sm font-semibold text-gray-700">选择数据源</h3>
              </div>
              {sources.map((source) => (
                <button
                  key={source.name}
                  onClick={() => handleSwitchSource(source.name)}
                  className={`w-full text-left px-4 py-3 hover:bg-blue-50 transition-colors ${
                    source.name === currentSource ? 'bg-blue-50' : ''
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className={`font-medium text-sm ${
                        source.name === currentSource ? 'text-blue-600' : 'text-gray-800'
                      }`}>
                        {source.display_name}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {source.stats?.total_stocks || 0} 只股票
                      </div>
                    </div>
                    {source.name === currentSource && (
                      <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                        <path
                          fillRule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clipRule="evenodd"
                        />
                      </svg>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default DataSourceSelector;
