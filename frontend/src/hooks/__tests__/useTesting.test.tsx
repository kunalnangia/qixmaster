import { renderHook, act } from '@testing-library/react';
import { useTesting } from '../useTesting';
import { useToast } from '@/hooks/use-toast';

// Mock the useToast hook
jest.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: jest.fn(),
  }),
}));

// Mock fetch
global.fetch = jest.fn();

describe('useTesting', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('executePerformanceTest', () => {
    it('should execute performance test successfully', async () => {
      // Mock successful API responses
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({
            run_id: 'test-run-id',
            summary_metrics: {
              avg_response_time: 250,
              p95_response_time: 400,
              error_rate: 0.5,
              throughput: 50
            },
            detailed_reports: {
              executive_html: '/reports/test-run-id/report/index.html'
            }
          })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({
            run_id: 'test-run-id',
            bottlenecks: ['High response time on login endpoint'],
            recommendations: ['Optimize database queries'],
            next_tests: ['Run stress test with 100 concurrent users']
          })
        });

      const { result } = renderHook(() => {
        const testing = useTesting();
        const toast = useToast();
        return { ...testing, toast };
      });

      let testResult;
      await act(async () => {
        testResult = await result.current.executePerformanceTest('test-case-1', 'https://example.com', {
          test_type: 'load',
          concurrent_users: 10,
          duration: 60,
          ramp_up_time: 10,
          thresholds: {
            response_time: 1000,
            error_rate: 1,
            throughput: 10
          }
        });
      });

      expect(testResult).toBeDefined();
      expect(testResult.metrics.page_load_time).toBe(250);
      expect(testResult.metrics.first_contentful_paint).toBe(250);
      expect(testResult.metrics.largest_contentful_paint).toBe(400);
      expect(testResult.metrics.network_requests).toBe(50);
      expect(testResult.run_id).toBe('test-run-id');
      expect(testResult.ai_analysis).toBeDefined();
    });

    it('should handle performance test errors', async () => {
      // Mock failed API response
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({
          detail: 'Performance test failed'
        })
      });

      const { result } = renderHook(() => {
        const testing = useTesting();
        const toast = useToast();
        return { ...testing, toast };
      });

      await expect(
        act(() => result.current.executePerformanceTest('test-case-1', 'https://example.com'))
      ).rejects.toThrow('Performance test failed');
    });
  });
});