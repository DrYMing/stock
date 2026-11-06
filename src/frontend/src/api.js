/**
 * API 客户端
 */

const API_HOST = window.location.hostname;
const API_BASE_URL = `http://${API_HOST}:8007/api`;

export const api = {
  /**
   * 健康检查
   */
  health: async () => {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.json();
  },

  /**
   * 获取所有数据源
   */
  getDataSources: async () => {
    const response = await fetch(`${API_BASE_URL}/sources`);
    return response.json();
  },

  /**
   * 切换数据源
   */
  switchSource: async (sourceName) => {
    const response = await fetch(`${API_BASE_URL}/switch-source`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ source_name: sourceName })
    });
    return response.json();
  },

  /**
   * 获取统计数据
   */
  getStats: async (params = {}) => {
    const queryParams = new URLSearchParams(params);
    const response = await fetch(`${API_BASE_URL}/stats?${queryParams}`);
    return response.json();
  },

  /**
   * 获取股票列表
   */
  getStocks: async (params = {}) => {
    const queryParams = new URLSearchParams(params);
    const response = await fetch(`${API_BASE_URL}/stocks?${queryParams}`);
    return response.json();
  },

  /**
   * 获取股票详情
   */
  getStockDetail: async (code) => {
    const response = await fetch(`${API_BASE_URL}/stocks/${code}`);
    if (!response.ok) {
      throw new Error('Stock not found');
    }
    return response.json();
  },

  /**
   * 获取股票收益率曲线
   */
  getStockReturns: async (code) => {
    const response = await fetch(`${API_BASE_URL}/stocks/${code}/returns`);
    if (!response.ok) {
      throw new Error('Stock not found');
    }
    return response.json();
  },

  /**
   * 获取表现最好/最差的股票
   */
  getTopStocks: async (params = {}) => {
    const queryParams = new URLSearchParams(params);
    const response = await fetch(`${API_BASE_URL}/top?${queryParams}`);
    return response.json();
  },
};
