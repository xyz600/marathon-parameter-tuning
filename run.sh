#!/bin/bash

pushd ../../rust
cargo build --release -p main
cp target/release/main ../externals/marathon-parameter-tuning

popd
pipenv run python optimizer/optimize.py ./config.yml
