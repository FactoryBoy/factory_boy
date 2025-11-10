#!/bin/sh

cd $(dirname $0)

echo "Running async basic example..."
python3 async_basic.py || exit 1

echo ""
echo "Running async ORM example..."
python3 async_orm.py || exit 1

echo ""
echo "All async examples passed!"

