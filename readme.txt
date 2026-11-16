全球南方公共算力援助分配治理台

运行验收：
python3 -m compute_allocation run --fixture fixtures/acceptance.json --database /tmp/compute_allocation.sqlite3 --output /tmp/compute_allocation-output

核验：
python3 -m compute_allocation verify --database /tmp/compute_allocation.sqlite3 --output /tmp/compute_allocation-output

全量测试：
python3 -m unittest discover -s tests -v

按模块测试：
python3 -m unittest tests.allocation_signal.test_allocation_pressure -v

构建检查：
python3 -m compileall -q compute_allocation tests
