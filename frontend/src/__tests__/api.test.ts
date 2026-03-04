import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { apiClient, ApiError } from '@/lib/api';

describe('apiClient', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('makes GET request and returns JSON', async () => {
    const mockData = { id: 1, title: 'Test' };
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => mockData,
    } as Response);

    const result = await apiClient<{ id: number; title: string }>('/test');
    expect(result).toEqual(mockData);
    expect(fetch).toHaveBeenCalledWith('/test', expect.objectContaining({
      headers: expect.objectContaining({
        'Content-Type': 'application/json',
      }),
    }));
  });

  it('throws ApiError with status code on failure', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: async () => ({ detail: 'Not found' }),
    } as Response);

    try {
      await apiClient('/test');
      expect.fail('Expected ApiError to be thrown');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      expect((error as ApiError).status).toBe(404);
      expect((error as ApiError).message).toBe('Not found');
    }
  });

  it('handles 204 No Content responses', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      status: 204,
    } as Response);

    const result = await apiClient<void>('/test');
    expect(result).toBeUndefined();
  });

  it('sends Content-Type header', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({}),
    } as Response);

    await apiClient('/test');
    expect(fetch).toHaveBeenCalledWith('/test', expect.objectContaining({
      headers: expect.objectContaining({
        'Content-Type': 'application/json',
      }),
    }));
  });
});
