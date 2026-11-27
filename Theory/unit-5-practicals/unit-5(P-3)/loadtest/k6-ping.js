// k6 script (runs in k6's own JS runtime, not Node). NOT RUN here: k6 was not installed in my environment.
//   k6 run loadtest/k6-ping.js
// k6 exits non-zero when a threshold fails, so this is usable as a CI gate.
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  vus: 50,
  duration: '30s',
  thresholds: {
    http_req_duration: ['p(99)<500'],     // slide threshold
    http_req_failed: ['rate<0.01'],       // error rate under 1 %
  },
};

export default function () {
  const res = http.get('http://localhost:3000/api/ping');
  check(res, { 'status is 200': (r) => r.status === 200 });
}
