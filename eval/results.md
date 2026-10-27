# Redproof eval

| case | expected | Redproof verdict | correct? | changed-line coverage | coverage approves? | seconds |
| --- | --- | --- | --- | --- | --- | --- |
| boundary_real | REAL | REAL | yes | 100.0% | yes | 4.62 |
| boundary_fake | FAKE | FAKE | yes | 100.0% | yes | 4.85 |
| mock_fake | FAKE | FAKE | yes | 0.0% | no | 5.23 |
| recompute_fake | FAKE | FAKE | yes | 100.0% | yes | 4.50 |
| raises_real | REAL | REAL | yes | 66.7% | no | 6.77 |
| new_function_inconclusive | INCONCLUSIVE | INCONCLUSIVE | yes | 33.3% | no | 4.76 |

Fake tests: coverage approved 2 of 3. Redproof flagged 3 of 3. Redproof correct on 6 of 6 cases. Median time per case: 4.80 s.
