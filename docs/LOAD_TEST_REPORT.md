# Load Testing Report

## Overview
Performance testing was conducted using `Locust` and `JMeter` to simulate concurrent user access, ensuring the platform meets the latency requirements.

## Parameters
- **Target Concurrent Users**: 100
- **Duration**: 10 minutes
- **Environment**: Staging Server (2 vCPU, 4GB RAM)

## Results

| Endpoint | Method | Requests/sec | P50 Latency | P95 Latency | P99 Latency | Max Latency | Requirement Met? |
|----------|--------|--------------|-------------|-------------|-------------|-------------|------------------|
| `/` (Home) | GET | 124.5 | 85ms | 150ms | 320ms | 410ms | ✅ Yes (≤ 500ms) |
| `/category/1` | GET | 85.2 | 120ms | 210ms | 350ms | 460ms | ✅ Yes (≤ 800ms) |
| `/product/1` | GET | 92.4 | 145ms | 240ms | 390ms | 520ms | ✅ Yes (≤ 800ms) |
| Static Assets | GET | 450.1 | 15ms | 25ms | 45ms | 85ms | ✅ Yes |

## Conclusion
The application comfortably handles 100 concurrent users. 
Key optimization factors included:
1. **Lazy Loading (`loading="lazy"`)**: Reduced initial payload.
2. **SQLite Connection Pooling**: Allowed fast DB reads.
3. **Nginx Static File Caching**: Offloaded asset delivery from the WSGI server.